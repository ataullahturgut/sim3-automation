from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
R4_SRC = ROOT / "r4_1" / "src"
sys.path.insert(0, str(R4_SRC))

from gold_r4.tactical import completed_weekly_closes, fast_state, slow_state  # noqa: E402

SERIES_ID = "XAU_EOD_TWELVE_NY17"
QUALITY_INPUT = "APPROVED_CANONICAL_TWELVE_NY17"
EVIDENCE_CLASS = "LATE_BOOTSTRAP_SHADOW_CONTEXT"
TARGET_CONTEXT = "2026-09"
CONTRACT = ROOT / "GOLD_CONTROL_STAGE4A_TACTICAL_CONTEXT_DISPLAY_CONTRACT_2026-09-02.md"
CUTOFF_TS = "2026-09-02 00:00:00+00"
FEATURES = {
    "FAST_STATE": "R4_1_SMA20_2_MARKET_DAY_PERSISTENCE_V1",
    "SLOW_STATE": "R4_1_COMPLETED_WEEKLY_SMA4_2_WEEK_PERSISTENCE_V1",
}


def git_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def load_inputs(cur, calc_ts: datetime) -> list[dict]:
    cur.execute(
        """
        SELECT id, observation_ts, value, source, available_as_of, retrieved_at, lineage_id
        FROM observations_as_of(%s)
        WHERE series_id=%s AND quality_status=%s
          AND observation_ts >= timestamptz '2026-07-01 00:00:00+00'
          AND observation_ts < %s::timestamptz
        ORDER BY observation_ts, retrieved_at, id
        """,
        (calc_ts, SERIES_ID, QUALITY_INPUT, CUTOFF_TS),
    )
    rows = [dict(r) for r in cur.fetchall()]
    if len(rows) < 35:
        raise RuntimeError(f"TACTICAL_CONTEXT_INSUFFICIENT_ROWS:{len(rows)}")
    lineages = sorted({r["lineage_id"] for r in rows})
    if len(lineages) != 1:
        raise RuntimeError(f"TACTICAL_CONTEXT_LINEAGE_COUNT:{len(lineages)}")
    if sorted({r["source"] for r in rows}) != ["Twelve Data"]:
        raise RuntimeError("TACTICAL_CONTEXT_SOURCE_MISMATCH")
    if any(r["available_as_of"] > calc_ts or r["retrieved_at"] > calc_ts for r in rows):
        raise RuntimeError("TACTICAL_CONTEXT_PIT_VIOLATION")
    return sorted(rows, key=lambda r: r["observation_ts"])


def calculate(rows: list[dict]) -> tuple[str, str, str, str, datetime]:
    closes = [float(r["value"]) for r in rows]
    if any(not (x > 0) for x in closes):
        raise RuntimeError("TACTICAL_CONTEXT_INVALID_LEVEL")
    fast = fast_state(closes).value
    daily = pd.DataFrame({
        "date": [pd.Timestamp(r["observation_ts"]).tz_convert("UTC").tz_localize(None) for r in rows],
        "close": closes,
    })
    asof = daily["date"].max()
    weekly = completed_weekly_closes(daily, asof)
    slow = slow_state(weekly).value
    lineage_id = str(rows[0]["lineage_id"])
    fingerprint_payload = {
        "contract": CONTRACT.name,
        "series_id": SERIES_ID,
        "target_context": TARGET_CONTEXT,
        "cutoff_ts": CUTOFF_TS,
        "input_ids": [int(r["id"]) for r in rows],
        "input_observation_ts": [r["observation_ts"].isoformat() for r in rows],
        "input_available_as_of": [r["available_as_of"].isoformat() for r in rows],
        "lineage_id": lineage_id,
        "fast_contract": "SMA20_2_MARKET_DAY_PERSISTENCE",
        "slow_contract": "COMPLETED_WEEKLY_SMA4_2_WEEK_PERSISTENCE",
    }
    fingerprint = hashlib.sha256(
        json.dumps(fingerprint_payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    input_cutoff = max(r["available_as_of"] for r in rows)
    return fast, slow, fingerprint, lineage_id, input_cutoff


def existing_context(cur, feature_name: str, feature_version: str):
    cur.execute(
        """
        select id, value_text, metadata
        from derived_feature_snapshots
        where feature_name=%s and feature_version=%s
          and metadata->>'target_context'=%s
          and metadata->>'evidence_class'=%s
        order by calculation_ts desc, id desc
        """,
        (feature_name, feature_version, TARGET_CONTEXT, EVIDENCE_CLASS),
    )
    return [dict(r) for r in cur.fetchall()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--persist", action="store_true")
    args = parser.parse_args()

    if "FROZEN_BEFORE_TACTICAL_CONTEXT_ISSUANCE" not in CONTRACT.read_text(encoding="utf-8"):
        raise RuntimeError("TACTICAL_CONTEXT_CONTRACT_NOT_FROZEN")
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")

    calc_ts = datetime.now(timezone.utc)
    sha = git_commit()
    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select count(distinct trigger_name) as n
                from information_schema.triggers
                where event_object_schema='public'
                  and event_object_table='derived_feature_snapshots'
                  and trigger_name='trg_derived_feature_snapshots_immutable'
                """
            )
            if int(cur.fetchone()["n"]) != 1:
                raise RuntimeError("DERIVED_FEATURE_IMMUTABILITY_GUARD_NOT_ACTIVE")

            input_rows = load_inputs(cur, calc_ts)
            input_count = len(input_rows)
            fast, slow, fingerprint, lineage_id, input_cutoff = calculate(input_rows)
            values = {"FAST_STATE": fast, "SLOW_STATE": slow}

            for feature_name, feature_version in FEATURES.items():
                existing = existing_context(cur, feature_name, feature_version)
                if existing:
                    row = existing[0]
                    metadata = row.get("metadata") or {}
                    if row.get("value_text") == values[feature_name] and metadata.get("input_fingerprint") == fingerprint:
                        continue
                    raise RuntimeError(f"TACTICAL_CONTEXT_CONFLICT_EXISTING:{feature_name}")

            summary = {
                "status": "DRY_RUN_PASS" if not args.persist else "READY_TO_PERSIST",
                "target_context": TARGET_CONTEXT,
                "fast_state": fast,
                "slow_state": slow,
                "input_count": input_count,
                "input_fingerprint": fingerprint,
                "raw_market_values_logged": False,
                "prospective_h1_claim": False,
            }
            if not args.persist:
                conn.rollback()
                summary["database_writes"] = "NONE"
                print(json.dumps(summary, indent=2, sort_keys=True))
                print("STAGE4_TACTICAL_CONTEXT_DRY_RUN_PASS")
                return 0

            inserted: dict[str, int] = {}
            common_lineage = {
                "series_id": SERIES_ID,
                "source": "Twelve Data",
                "lineage_id": lineage_id,
                "selected_input_ids": [int(r["id"]) for r in input_rows],
                "selected_observation_ts": [r["observation_ts"].isoformat() for r in input_rows],
                "selected_available_as_of": [r["available_as_of"].isoformat() for r in input_rows],
                "input_fingerprint": fingerprint,
            }
            for feature_name, feature_version in FEATURES.items():
                if existing_context(cur, feature_name, feature_version):
                    continue
                metadata = {
                    "target_context": TARGET_CONTEXT,
                    "evidence_class": EVIDENCE_CLASS,
                    "display_scope": "COMPONENT_CONTEXT_ONLY",
                    "prospective_h1_claim": False,
                    "decision_store_write": "NONE",
                    "canonical_forecast_write": "NONE",
                    "position_mapping": "NOT_PROVEN_POSITION_MAPPING",
                    "input_fingerprint": fingerprint,
                    "contract": CONTRACT.name,
                    "raw_market_values_logged": False,
                }
                cur.execute(
                    """
                    insert into derived_feature_snapshots
                      (feature_name, feature_version, calculation_ts, input_cutoff,
                       value_text, git_commit, input_lineage, quality_status, metadata)
                    values (%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s::jsonb)
                    returning id
                    """,
                    (
                        feature_name, feature_version, calc_ts, input_cutoff,
                        values[feature_name], sha, json.dumps(common_lineage), EVIDENCE_CLASS,
                        json.dumps(metadata),
                    ),
                )
                inserted[feature_name] = int(cur.fetchone()["id"])
        conn.commit()

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            for feature_name, feature_version in FEATURES.items():
                verified_rows = existing_context(cur, feature_name, feature_version)
                if not verified_rows:
                    raise RuntimeError(f"TACTICAL_CONTEXT_POST_COMMIT_MISSING:{feature_name}")
                verified = verified_rows[0]
                if verified.get("value_text") != values[feature_name]:
                    raise RuntimeError(f"TACTICAL_CONTEXT_POST_COMMIT_VALUE_MISMATCH:{feature_name}")
                if (verified.get("metadata") or {}).get("input_fingerprint") != fingerprint:
                    raise RuntimeError(f"TACTICAL_CONTEXT_POST_COMMIT_FINGERPRINT_MISMATCH:{feature_name}")
        conn.rollback()

    print(json.dumps({
        "status": "INSERTED_VERIFIED",
        "target_context": TARGET_CONTEXT,
        "fast_state": fast,
        "slow_state": slow,
        "inserted_ids": inserted,
        "input_count": input_count,
        "input_fingerprint": fingerprint,
        "raw_market_values_logged": False,
        "prospective_h1_claim": False,
        "decision_store_write": "NONE",
        "canonical_forecast_write": "NONE",
    }, indent=2, sort_keys=True))
    print("STAGE4_TACTICAL_CONTEXT_ISSUE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
