from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
R4_SRC = ROOT / "r4_1" / "src"
sys.path.insert(0, str(R4_SRC))

from gold_r4.gvz import gvz_risk  # noqa: E402

SERIES_ID = "GVZ_CBOE"
SOURCE = "Cboe"
QUALITY_INPUT = "APPROVED_AUTHORITY_RETRIEVAL_FLOOR"
EVIDENCE_CLASS = "LATE_BOOTSTRAP_SHADOW_CONTEXT"
FEATURE_VERSION = "R4_1_GVZ_RISK_CAP_CONTEXT_V1"
CONTRACT = ROOT / "GOLD_CONTROL_STAGE4A_GVZ_RISK_CONTEXT_CONTRACT_2026-09-03.md"
CONFIG_PATH = ROOT / "r4_1" / "config" / "frozen_r4_1.json"
FEATURES = ("GVZ_VALUE", "GVZ_CAP", "GVZ_PANIC", "GVZ_REGIME")


def git_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def load_config() -> dict:
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    gvz = dict(cfg.get("gvz") or {})
    required = {
        "full_cap_max",
        "half_cap_max",
        "panic_above",
        "caps",
        "role",
    }
    if not required.issubset(gvz):
        raise RuntimeError(f"GVZ_FROZEN_CONFIG_MISSING:{sorted(required - set(gvz))}")
    caps = dict(gvz.get("caps") or {})
    required_caps = {"normal", "elevated", "panic"}
    if not required_caps.issubset(caps):
        raise RuntimeError(f"GVZ_FROZEN_CONFIG_CAPS_MISSING:{sorted(required_caps - set(caps))}")
    if float(gvz["panic_above"]) != float(gvz["half_cap_max"]):
        raise RuntimeError("GVZ_FROZEN_CONFIG_PANIC_BOUNDARY_MISMATCH")
    if str(gvz["role"]) != "RISK_ONLY":
        raise RuntimeError("GVZ_FROZEN_CONFIG_ROLE_MISMATCH")
    if (
        float(caps["normal"]) != 1.0
        or float(caps["elevated"]) != 0.5
        or float(caps["panic"]) != 0.25
    ):
        raise RuntimeError("GVZ_FROZEN_CONFIG_CAP_MISMATCH")
    return {
        **gvz,
        "normal_cap": float(caps["normal"]),
        "elevated_cap": float(caps["elevated"]),
        "panic_cap": float(caps["panic"]),
    }


def load_latest_input(cur, calc_ts: datetime) -> dict:
    cur.execute(
        """
        SELECT id, observation_ts, value, source, source_symbol,
               available_as_of, retrieved_at, lineage_id, quality_status
        FROM observations_as_of(%s)
        WHERE series_id=%s
          AND source=%s
          AND quality_status=%s
          AND available_as_of <= %s
          AND retrieved_at <= %s
        ORDER BY observation_ts DESC, available_as_of DESC, retrieved_at DESC, id DESC
        LIMIT 1
        """,
        (calc_ts, SERIES_ID, SOURCE, QUALITY_INPUT, calc_ts, calc_ts),
    )
    row = cur.fetchone()
    if row is None:
        raise RuntimeError("GVZ_CONTEXT_NO_PIT_ELIGIBLE_CBOE_OBSERVATION")
    out = dict(row)
    value = float(out["value"])
    if not math.isfinite(value) or value <= 0:
        raise RuntimeError("GVZ_CONTEXT_INVALID_VALUE")
    if out.get("source") != SOURCE:
        raise RuntimeError("GVZ_CONTEXT_SOURCE_MISMATCH")
    if out.get("quality_status") != QUALITY_INPUT:
        raise RuntimeError("GVZ_CONTEXT_QUALITY_MISMATCH")
    if out.get("available_as_of") > calc_ts or out.get("retrieved_at") > calc_ts:
        raise RuntimeError("GVZ_CONTEXT_PIT_VIOLATION")
    return out


def calculate(row: dict, cfg: dict, target_context: str) -> tuple[dict[str, str], str, datetime]:
    value = float(row["value"])
    risk = gvz_risk(
        value,
        full_cap_max=float(cfg["full_cap_max"]),
        half_cap_max=float(cfg["half_cap_max"]),
    )
    expected_cap = (
        float(cfg["panic_cap"])
        if risk.panic
        else float(cfg["elevated_cap"])
        if risk.cap == 0.5
        else float(cfg["normal_cap"])
    )
    if float(risk.cap) != expected_cap:
        raise RuntimeError("GVZ_CONTEXT_CALC_CAP_CONFIG_MISMATCH")
    regime = "PANIC" if risk.panic else "ELEVATED" if float(risk.cap) == 0.5 else "NORMAL"
    values = {
        "GVZ_VALUE": format(value, ".10g"),
        "GVZ_CAP": format(float(risk.cap), ".2g"),
        "GVZ_PANIC": "true" if bool(risk.panic) else "false",
        "GVZ_REGIME": regime,
    }
    fingerprint_payload = {
        "contract": CONTRACT.name,
        "series_id": SERIES_ID,
        "source": SOURCE,
        "quality_status": QUALITY_INPUT,
        "target_context": target_context,
        "observation_id": int(row["id"]),
        "observation_ts": row["observation_ts"].isoformat(),
        "available_as_of": row["available_as_of"].isoformat(),
        "retrieved_at": row["retrieved_at"].isoformat(),
        "lineage_id": str(row["lineage_id"]),
        "config": {
            "full_cap_max": float(cfg["full_cap_max"]),
            "half_cap_max": float(cfg["half_cap_max"]),
            "panic_above": float(cfg["panic_above"]),
            "normal_cap": float(cfg["normal_cap"]),
            "elevated_cap": float(cfg["elevated_cap"]),
            "panic_cap": float(cfg["panic_cap"]),
            "role": str(cfg["role"]),
        },
    }
    fingerprint = hashlib.sha256(
        json.dumps(fingerprint_payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return values, fingerprint, row["available_as_of"]


def rows_for_fingerprint(cur, feature_name: str, target_context: str, fingerprint: str) -> list[dict]:
    cur.execute(
        """
        SELECT id, value_text, metadata
        FROM derived_feature_snapshots
        WHERE feature_name=%s
          AND feature_version=%s
          AND metadata->>'target_context'=%s
          AND metadata->>'evidence_class'=%s
          AND metadata->>'input_fingerprint'=%s
        ORDER BY calculation_ts DESC, id DESC
        """,
        (feature_name, FEATURE_VERSION, target_context, EVIDENCE_CLASS, fingerprint),
    )
    return [dict(r) for r in cur.fetchall()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--persist", action="store_true")
    args = parser.parse_args()

    contract_text = CONTRACT.read_text(encoding="utf-8")
    if "FROZEN_BEFORE_GVZ_CONTEXT_ISSUANCE" not in contract_text:
        raise RuntimeError("GVZ_CONTEXT_CONTRACT_NOT_FROZEN")
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")

    calc_ts = datetime.now(timezone.utc)
    target_context = calc_ts.strftime("%Y-%m")
    cfg = load_config()
    sha = git_commit()

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT count(distinct trigger_name) AS n
                FROM information_schema.triggers
                WHERE event_object_schema='public'
                  AND event_object_table='derived_feature_snapshots'
                  AND trigger_name='trg_derived_feature_snapshots_immutable'
                """
            )
            if int(cur.fetchone()["n"]) != 1:
                raise RuntimeError("DERIVED_FEATURE_IMMUTABILITY_GUARD_NOT_ACTIVE")

            source_row = load_latest_input(cur, calc_ts)
            values, fingerprint, input_cutoff = calculate(source_row, cfg, target_context)
            for feature_name in FEATURES:
                existing = rows_for_fingerprint(cur, feature_name, target_context, fingerprint)
                if existing and any(r.get("value_text") != values[feature_name] for r in existing):
                    raise RuntimeError(f"GVZ_CONTEXT_CONFLICT_EXISTING:{feature_name}")

            if not args.persist:
                conn.rollback()
                print(json.dumps({
                    "status": "DRY_RUN_PASS",
                    "target_context": target_context,
                    "features": list(FEATURES),
                    "regime": values["GVZ_REGIME"],
                    "cap": values["GVZ_CAP"],
                    "input_fingerprint": fingerprint,
                    "raw_market_values_logged": False,
                    "prospective_h1_claim": False,
                    "database_writes": "NONE",
                }, indent=2, sort_keys=True))
                print("STAGE4_GVZ_RISK_CONTEXT_DRY_RUN_PASS")
                return 0

            common_lineage = {
                "series_id": SERIES_ID,
                "source": SOURCE,
                "source_symbol": source_row.get("source_symbol"),
                "observation_id": int(source_row["id"]),
                "observation_ts": source_row["observation_ts"].isoformat(),
                "available_as_of": source_row["available_as_of"].isoformat(),
                "retrieved_at": source_row["retrieved_at"].isoformat(),
                "lineage_id": str(source_row["lineage_id"]),
                "input_fingerprint": fingerprint,
            }
            inserted: dict[str, int] = {}
            for feature_name in FEATURES:
                existing = rows_for_fingerprint(cur, feature_name, target_context, fingerprint)
                if existing:
                    continue
                metadata = {
                    "target_context": target_context,
                    "evidence_class": EVIDENCE_CLASS,
                    "display_scope": "COMPONENT_CONTEXT_ONLY",
                    "prospective_h1_claim": False,
                    "decision_store_write": "NONE",
                    "canonical_forecast_write": "NONE",
                    "direction_vote": False,
                    "role": "RISK_ONLY",
                    "position_mapping": "NOT_PROVEN_POSITION_MAPPING",
                    "input_fingerprint": fingerprint,
                    "contract": CONTRACT.name,
                    "raw_market_values_logged": False,
                    "frozen_thresholds": {
                        "full_cap_max": float(cfg["full_cap_max"]),
                        "half_cap_max": float(cfg["half_cap_max"]),
                        "panic_above": float(cfg["panic_above"]),
                        "normal_cap": float(cfg["normal_cap"]),
                        "elevated_cap": float(cfg["elevated_cap"]),
                        "panic_cap": float(cfg["panic_cap"]),
                    },
                }
                cur.execute(
                    """
                    INSERT INTO derived_feature_snapshots
                      (feature_name, feature_version, calculation_ts, input_cutoff,
                       value_text, git_commit, input_lineage, quality_status, metadata)
                    VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s::jsonb)
                    RETURNING id
                    """,
                    (
                        feature_name,
                        FEATURE_VERSION,
                        calc_ts,
                        input_cutoff,
                        values[feature_name],
                        sha,
                        json.dumps(common_lineage),
                        EVIDENCE_CLASS,
                        json.dumps(metadata),
                    ),
                )
                inserted[feature_name] = int(cur.fetchone()["id"])
        conn.commit()

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            for feature_name in FEATURES:
                verified = rows_for_fingerprint(cur, feature_name, target_context, fingerprint)
                if not verified:
                    raise RuntimeError(f"GVZ_CONTEXT_POST_COMMIT_MISSING:{feature_name}")
                if verified[0].get("value_text") != values[feature_name]:
                    raise RuntimeError(f"GVZ_CONTEXT_POST_COMMIT_VALUE_MISMATCH:{feature_name}")
        conn.rollback()

    print(json.dumps({
        "status": "INSERTED_VERIFIED",
        "target_context": target_context,
        "features": list(FEATURES),
        "regime": values["GVZ_REGIME"],
        "cap": values["GVZ_CAP"],
        "inserted_ids": inserted,
        "input_fingerprint": fingerprint,
        "raw_market_values_logged": False,
        "prospective_h1_claim": False,
        "decision_store_write": "NONE",
        "canonical_forecast_write": "NONE",
    }, indent=2, sort_keys=True))
    print("STAGE4_GVZ_RISK_CONTEXT_ISSUE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
