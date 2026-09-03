from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
R4_SRC = ROOT / "r4_1" / "src"
sys.path.insert(0, str(R4_SRC))

from gold_r4.gvz import gvz_risk  # noqa: E402
from gold_r4.monthly import three_month_direction  # noqa: E402
from gold_r4.tactical import completed_weekly_closes, fast_state, slow_state  # noqa: E402

CONTRACT = ROOT / "GOLD_CONTROL_AUG31_EOD_STATE_REPLAY_CONTRACT_2026-09-03.md"
CONTRACT_MARKER = "FROZEN_AUG31_EOD_STATE_REPLAY_V1"
EVIDENCE_CLASS = "HISTORICAL_REPLAY"
TARGET_CONTEXT = "2026-09"
STATE_AS_OF = datetime(2026, 8, 31, 21, 0, tzinfo=timezone.utc)
XAU_SERIES = "XAU_EOD_TWELVE_NY17"
XAU_QUALITY = "APPROVED_CANONICAL_TWELVE_NY17"
GVZ_SERIES = "GVZ_CBOE"

FEATURES = {
    "AUG31_REPLAY_MONTHLY_DIRECTION_3M": (
        "MONTHLY_DIRECTION_3M",
        "R4_1_3M_SIMPLE_RETURN_V1",
        "strategic monthly direction / historical state replay",
    ),
    "AUG31_REPLAY_FAST_STATE": (
        "FAST",
        "R4_1_SMA20_2_MARKET_DAY_PERSISTENCE_V1",
        "short-horizon tactical state / historical state replay",
    ),
    "AUG31_REPLAY_SLOW_STATE": (
        "SLOW",
        "R4_1_COMPLETED_WEEKLY_SMA4_2_WEEK_PERSISTENCE_V1",
        "medium-horizon tactical state / historical state replay",
    ),
    "AUG31_REPLAY_GVZ_VALUE": (
        "GVZ_RISK",
        "R4_1_GVZ_RISK_CAP_CONTEXT_V1",
        "risk-cap context / historical state replay",
    ),
    "AUG31_REPLAY_GVZ_CAP": (
        "GVZ_RISK",
        "R4_1_GVZ_RISK_CAP_CONTEXT_V1",
        "risk-cap context / historical state replay",
    ),
    "AUG31_REPLAY_GVZ_PANIC": (
        "GVZ_RISK",
        "R4_1_GVZ_RISK_CAP_CONTEXT_V1",
        "risk-cap context / historical state replay",
    ),
    "AUG31_REPLAY_GVZ_REGIME": (
        "GVZ_RISK",
        "R4_1_GVZ_RISK_CAP_CONTEXT_V1",
        "risk-cap context / historical state replay",
    ),
}

BLOCKERS = {
    "CAUSAL_PATCH": "BLOCKED_REPLAY_INPUT_SET_NOT_REPRODUCIBLE_FOR_2026_08_31",
    "VW_MIDAS_MSVR": "BLOCKED_NOT_PROVEN_EXECUTABLE",
    "MACRO_EVENT": "BLOCKED_NOT_FULLY_RECOVERED",
    "EMERGENCY_LEVEL": "BLOCKED_NO_AUTHORIZED_REPLAY_MONTHLY_REFERENCE",
    "EMERGENCY_REVERSAL": "BLOCKED_NO_AUTHORIZED_REPLAY_MONTHLY_REFERENCE",
    "BOCPD": "BLOCKED_EXACT_FORWARD_BOCPD_RULE_NOT_RECOVERED",
}


def git_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _load_xau(cur) -> list[dict[str, Any]]:
    cur.execute(
        """
        SELECT DISTINCT ON (observation_ts)
               id, observation_ts, value, source, available_as_of, retrieved_at, lineage_id, quality_status
        FROM observations
        WHERE series_id=%s AND quality_status=%s
          AND observation_ts >= timestamptz '2026-05-01 00:00:00+00'
          AND observation_ts <= %s
        ORDER BY observation_ts, retrieved_at DESC, id DESC
        """,
        (XAU_SERIES, XAU_QUALITY, STATE_AS_OF),
    )
    rows = [dict(r) for r in cur.fetchall()]
    if len(rows) < 45:
        raise RuntimeError(f"AUG31_STATE_REPLAY_XAU_INSUFFICIENT:{len(rows)}")
    if {str(r["source"]) for r in rows} != {"Twelve Data"}:
        raise RuntimeError("AUG31_STATE_REPLAY_XAU_SOURCE_MISMATCH")
    if max(r["observation_ts"] for r in rows) != STATE_AS_OF:
        raise RuntimeError("AUG31_STATE_REPLAY_XAU_BOUNDARY_MISSING")
    return rows


def _month_end_rows(xau: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_month: dict[str, dict[str, Any]] = {}
    for row in xau:
        key = row["observation_ts"].strftime("%Y-%m")
        if key not in by_month or row["observation_ts"] > by_month[key]["observation_ts"]:
            by_month[key] = row
    required = ["2026-05", "2026-06", "2026-07", "2026-08"]
    missing = [m for m in required if m not in by_month]
    if missing:
        raise RuntimeError(f"AUG31_STATE_REPLAY_MONTH_END_MISSING:{missing}")
    return [by_month[m] for m in required]


def _load_gvz(cur) -> dict[str, Any]:
    cur.execute(
        """
        SELECT id, observation_ts, value, source, available_as_of, retrieved_at, lineage_id, quality_status
        FROM observations
        WHERE series_id=%s AND observation_ts <= timestamptz '2026-08-31 23:59:59+00'
          AND value > 0
        ORDER BY observation_ts DESC, retrieved_at DESC, id DESC
        LIMIT 1
        """,
        (GVZ_SERIES,),
    )
    row = cur.fetchone()
    if row is None:
        raise RuntimeError("AUG31_STATE_REPLAY_GVZ_MISSING")
    out = dict(row)
    if out["observation_ts"].date().isoformat() != "2026-08-31":
        raise RuntimeError(f"AUG31_STATE_REPLAY_GVZ_WRONG_DATE:{out['observation_ts']}")
    if str(out["source"]) != "Cboe":
        raise RuntimeError("AUG31_STATE_REPLAY_GVZ_SOURCE_MISMATCH")
    return out


def calculate_state(xau: list[dict[str, Any]], gvz_row: dict[str, Any]) -> dict[str, Any]:
    month_rows = _month_end_rows(xau)
    month_values = [float(r["value"]) for r in month_rows]
    returns = [(month_values[i] / month_values[i - 1]) - 1.0 for i in range(1, len(month_values))]
    monthly_direction = three_month_direction(returns).value

    closes = [float(r["value"]) for r in xau]
    fast = fast_state(closes).value
    daily = pd.DataFrame(
        {
            "date": [pd.Timestamp(r["observation_ts"]).tz_convert("UTC").tz_localize(None) for r in xau],
            "close": closes,
        }
    )
    weekly = completed_weekly_closes(daily, pd.Timestamp("2026-08-31"))
    slow = slow_state(weekly).value

    gvz_value = float(gvz_row["value"])
    risk = gvz_risk(gvz_value, full_cap_max=25.9795, half_cap_max=30.5238)
    regime = "PANIC" if risk.panic else ("NORMAL" if float(risk.cap) == 1.0 else "ELEVATED")

    return {
        "monthly_direction": monthly_direction,
        "fast_state": fast,
        "slow_state": slow,
        "gvz_value": gvz_value,
        "gvz_cap": float(risk.cap),
        "gvz_panic": bool(risk.panic),
        "gvz_regime": regime,
        "monthly_return_signs": ["POS" if x > 0 else "NEG" if x < 0 else "ZERO" for x in returns],
        "month_rows": month_rows,
    }


def _xau_lineage(xau: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [
        {
            "id": int(r["id"]),
            "observation_ts": r["observation_ts"].isoformat(),
            "available_as_of": r["available_as_of"].isoformat(),
            "retrieved_at": r["retrieved_at"].isoformat(),
            "lineage_id": str(r["lineage_id"]),
        }
        for r in xau
    ]
    return {
        "series_id": XAU_SERIES,
        "source": "Twelve Data",
        "state_boundary": STATE_AS_OF.isoformat(),
        "selected_rows": selected,
        "retrieved_post_origin": any(r["retrieved_at"] > STATE_AS_OF for r in xau),
        "input_fingerprint": _canonical_hash(selected),
    }


def _gvz_lineage(row: dict[str, Any]) -> dict[str, Any]:
    selected = {
        "id": int(row["id"]),
        "observation_ts": row["observation_ts"].isoformat(),
        "available_as_of": row["available_as_of"].isoformat(),
        "retrieved_at": row["retrieved_at"].isoformat(),
        "lineage_id": str(row["lineage_id"]),
    }
    return {
        "series_id": GVZ_SERIES,
        "source": "Cboe",
        "state_boundary": STATE_AS_OF.isoformat(),
        "selected_row": selected,
        "retrieved_post_origin": row["retrieved_at"] > STATE_AS_OF,
        "input_fingerprint": _canonical_hash(selected),
    }


def _expected_features(state: dict[str, Any], xau_lineage: dict[str, Any], gvz_lineage: dict[str, Any]) -> dict[str, dict[str, Any]]:
    common = {
        "target_context": TARGET_CONTEXT,
        "state_as_of": STATE_AS_OF.isoformat(),
        "evidence_class": EVIDENCE_CLASS,
        "historical_replay": True,
        "prospective_h1_claim": False,
        "current_runtime_authority": False,
        "canonical_authority": False,
        "decision_store_write": "NONE",
        "canonical_forecast_write": "NONE",
        "selector_rule": "NOT_PROVEN_EXPERT_SELECTION_RULE",
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
        "position_mapping": "NOT_PROVEN_POSITION_MAPPING",
        "contract": CONTRACT.name,
        "raw_market_values_logged": False,
    }
    return {
        "AUG31_REPLAY_MONTHLY_DIRECTION_3M": {
            "value_text": state["monthly_direction"],
            "lineage": xau_lineage,
            "metadata": {**common, "role": "STRATEGIC_DIRECTION_CONTEXT", "direction_vote_permitted": False, "replay_return_signs": state["monthly_return_signs"]},
        },
        "AUG31_REPLAY_FAST_STATE": {
            "value_text": state["fast_state"],
            "lineage": xau_lineage,
            "metadata": {**common, "role": "TACTICAL_CONTEXT", "direction_vote_permitted": False},
        },
        "AUG31_REPLAY_SLOW_STATE": {
            "value_text": state["slow_state"],
            "lineage": xau_lineage,
            "metadata": {**common, "role": "TACTICAL_CONTEXT", "direction_vote_permitted": False},
        },
        "AUG31_REPLAY_GVZ_VALUE": {
            "value_text": f"{state['gvz_value']:.2f}",
            "lineage": gvz_lineage,
            "metadata": {**common, "role": "RISK_ONLY", "direction_vote_permitted": False},
        },
        "AUG31_REPLAY_GVZ_CAP": {
            "value_text": f"{state['gvz_cap']:.1f}",
            "lineage": gvz_lineage,
            "metadata": {**common, "role": "RISK_ONLY", "direction_vote_permitted": False},
        },
        "AUG31_REPLAY_GVZ_PANIC": {
            "value_text": str(state["gvz_panic"]).lower(),
            "lineage": gvz_lineage,
            "metadata": {**common, "role": "RISK_ONLY", "direction_vote_permitted": False},
        },
        "AUG31_REPLAY_GVZ_REGIME": {
            "value_text": state["gvz_regime"],
            "lineage": gvz_lineage,
            "metadata": {**common, "role": "RISK_ONLY", "direction_vote_permitted": False},
        },
    }


def _existing(cur) -> dict[str, dict[str, Any]]:
    cur.execute(
        """
        SELECT id, feature_name, feature_version, value_text, input_lineage, metadata
        FROM derived_feature_snapshots
        WHERE feature_name = ANY(%s)
          AND metadata->>'evidence_class'=%s
          AND metadata->>'target_context'=%s
          AND metadata->>'state_as_of'=%s
        ORDER BY feature_name, calculation_ts DESC, id DESC
        """,
        (list(FEATURES), EVIDENCE_CLASS, TARGET_CONTEXT, STATE_AS_OF.isoformat()),
    )
    rows = [dict(r) for r in cur.fetchall()]
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        if row["feature_name"] in out:
            raise RuntimeError(f"AUG31_STATE_REPLAY_DUPLICATE_EXISTING:{row['feature_name']}")
        out[row["feature_name"]] = row
    return out


def _verify_existing_exact(existing: dict[str, dict[str, Any]], expected: dict[str, dict[str, Any]]) -> None:
    if not existing:
        return
    if set(existing) != set(expected):
        raise RuntimeError(f"AUG31_STATE_REPLAY_PARTIAL_EXISTING:{sorted(existing)}")
    for name, spec in expected.items():
        row = existing[name]
        if row["value_text"] != spec["value_text"]:
            raise RuntimeError(f"AUG31_STATE_REPLAY_EXISTING_VALUE_CONFLICT:{name}")
        if (row.get("metadata") or {}).get("contract") != CONTRACT.name:
            raise RuntimeError(f"AUG31_STATE_REPLAY_EXISTING_CONTRACT_CONFLICT:{name}")
        if (row.get("input_lineage") or {}).get("input_fingerprint") != spec["lineage"].get("input_fingerprint"):
            raise RuntimeError(f"AUG31_STATE_REPLAY_EXISTING_LINEAGE_CONFLICT:{name}")


def _insert_replay(cur, expected: dict[str, dict[str, Any]], sha: str, calc_ts: datetime) -> dict[str, int]:
    inserted: dict[str, int] = {}
    run_ids: dict[str, uuid.UUID] = {}
    engine_features: dict[str, list[int]] = {}

    for name, spec in expected.items():
        engine_id, version, role = FEATURES[name]
        cur.execute(
            """
            INSERT INTO derived_feature_snapshots
              (feature_name, feature_version, calculation_ts, input_cutoff, value_text,
               git_commit, input_lineage, quality_status, metadata)
            VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s::jsonb)
            RETURNING id
            """,
            (
                name,
                version,
                calc_ts,
                STATE_AS_OF,
                spec["value_text"],
                sha,
                json.dumps(spec["lineage"], sort_keys=True),
                EVIDENCE_CLASS,
                json.dumps(spec["metadata"], sort_keys=True),
            ),
        )
        feature_id = int(cur.fetchone()["id"])
        inserted[name] = feature_id
        engine_features.setdefault(engine_id, []).append(feature_id)

    for engine_id, feature_ids in engine_features.items():
        first_feature = next(name for name, (eid, _, _) in FEATURES.items() if eid == engine_id)
        _, version, role = FEATURES[first_feature]
        relevant_specs = [expected[name] for name, (eid, _, _) in FEATURES.items() if eid == engine_id]
        fingerprints = sorted({str(spec["lineage"]["input_fingerprint"]) for spec in relevant_specs})
        run_fingerprint = _canonical_hash({"engine_id": engine_id, "fingerprints": fingerprints, "state_as_of": STATE_AS_OF.isoformat()})
        run_id = uuid.uuid4()
        run_ids[engine_id] = run_id
        metadata = {
            "contract": CONTRACT.name,
            "historical_replay": True,
            "state_as_of": STATE_AS_OF.isoformat(),
            "prospective_h1_claim": False,
            "current_runtime_authority": False,
            "canonical_authority": False,
            "decision_store_write": "NONE",
            "canonical_forecast_write": "NONE",
            "direction_vote_permitted": False,
            "blocked_components": BLOCKERS,
        }
        cur.execute(
            """
            INSERT INTO engine_execution_runs
              (run_id, engine_id, engine_version, engine_role, as_of, target_context,
               evidence_class, runtime_status, status_code, direction_vote_permitted,
               git_commit, input_fingerprint, metadata)
            VALUES (%s,%s,%s,%s,%s,%s,%s,'ISSUED','HISTORICAL_REPLAY_STATE_AVAILABLE',false,%s,%s,%s::jsonb)
            """,
            (
                run_id,
                engine_id,
                version,
                role,
                calc_ts,
                TARGET_CONTEXT,
                EVIDENCE_CLASS,
                sha,
                run_fingerprint,
                json.dumps(metadata, sort_keys=True),
            ),
        )
        for feature_id in feature_ids:
            cur.execute(
                "INSERT INTO engine_execution_derived_outputs(run_id, derived_feature_snapshot_id) VALUES (%s,%s)",
                (run_id, feature_id),
            )
    return inserted


def build_summary(state: dict[str, Any], write_status: str) -> dict[str, Any]:
    return {
        "status": write_status,
        "target_context": TARGET_CONTEXT,
        "state_as_of": STATE_AS_OF.isoformat(),
        "evidence_class": EVIDENCE_CLASS,
        "monthly_direction": state["monthly_direction"],
        "fast_state": state["fast_state"],
        "slow_state": state["slow_state"],
        "gvz_value": round(float(state["gvz_value"]), 2),
        "gvz_cap": float(state["gvz_cap"]),
        "gvz_panic": bool(state["gvz_panic"]),
        "gvz_regime": state["gvz_regime"],
        "blocked_components": BLOCKERS,
        "prospective_h1_claim": False,
        "current_runtime_authority": False,
        "canonical_forecast_write": "NONE",
        "decision_store_write": "NONE",
        "raw_market_values_logged": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--persist", action="store_true")
    args = parser.parse_args()

    if not CONTRACT.is_file() or CONTRACT_MARKER not in CONTRACT.read_text(encoding="utf-8"):
        raise RuntimeError("AUG31_STATE_REPLAY_CONTRACT_NOT_FROZEN")
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")

    sha = git_commit()
    calc_ts = datetime.now(timezone.utc)
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
                raise RuntimeError("AUG31_STATE_REPLAY_IMMUTABILITY_GUARD_MISSING")

            xau = _load_xau(cur)
            gvz_row = _load_gvz(cur)
            state = calculate_state(xau, gvz_row)
            xau_lineage = _xau_lineage(xau)
            gvz_lineage = _gvz_lineage(gvz_row)
            expected = _expected_features(state, xau_lineage, gvz_lineage)
            existing = _existing(cur)
            _verify_existing_exact(existing, expected)

            if not args.persist:
                conn.rollback()
                print(json.dumps(build_summary(state, "DRY_RUN_PASS"), indent=2, sort_keys=True))
                print("AUG31_EOD_STATE_HISTORICAL_REPLAY_DRY_RUN_PASS")
                return 0

            if existing:
                conn.rollback()
                print(json.dumps(build_summary(state, "IDEMPOTENT_ALREADY_PRESENT"), indent=2, sort_keys=True))
                print("AUG31_EOD_STATE_HISTORICAL_REPLAY_ALREADY_PRESENT_PASS")
                return 0

            inserted = _insert_replay(cur, expected, sha, calc_ts)
            if len(inserted) != 7:
                raise RuntimeError(f"AUG31_STATE_REPLAY_INSERT_COUNT:{len(inserted)}")
        conn.commit()

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            existing = _existing(cur)
            _verify_existing_exact(existing, expected)
            cur.execute("SELECT count(*) AS n FROM latest_engine_runtime_state")
            if int(cur.fetchone()["n"]) != 12:
                raise RuntimeError("AUG31_STATE_REPLAY_OPERATIONAL_RUNTIME_COUNT_CHANGED")
            cur.execute(
                """
                SELECT runtime_status, count(*) AS n
                FROM latest_engine_runtime_state
                GROUP BY runtime_status
                """
            )
            status_counts = {r["runtime_status"]: int(r["n"]) for r in cur.fetchall()}
            if status_counts != {"ACTIVE": 4, "WAITING": 3, "BLOCKED": 5}:
                raise RuntimeError(f"AUG31_STATE_REPLAY_RUNTIME_DISTRIBUTION_CHANGED:{status_counts}")
            cur.execute("SELECT count(*) AS n FROM canonical_monthly_forecasts")
            canonical_count = int(cur.fetchone()["n"])
            cur.execute("SELECT count(*) AS n FROM decision_signal_snapshots")
            decision_count = int(cur.fetchone()["n"])
            if canonical_count != 0 or decision_count != 0:
                raise RuntimeError(f"AUG31_STATE_REPLAY_AUTHORITY_VIOLATION:{canonical_count}:{decision_count}")
        conn.rollback()

    summary = build_summary(state, "INSERTED_VERIFIED")
    summary["inserted_feature_count"] = 7
    print(json.dumps(summary, indent=2, sort_keys=True))
    print("AUG31_EOD_STATE_HISTORICAL_REPLAY_PERSIST_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
