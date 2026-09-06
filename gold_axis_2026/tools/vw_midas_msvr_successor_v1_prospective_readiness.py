from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import psycopg

MODEL_ID = "VW_MIDAS_MSVR_SUCCESSOR_V1"
ORIGIN_CUTOFF = datetime(2026, 9, 30, 23, 59, 59, tzinfo=timezone.utc)
TARGET_MONTH = "2026-10"
FOUR_METALS = (
    "XAU_STAKTRAKR_RESEARCH_DAILY_R1",
    "XAG_STAKTRAKR_RESEARCH_DAILY_R1",
    "XPT_STAKTRAKR_RESEARCH_DAILY_R1",
    "XPD_STAKTRAKR_RESEARCH_DAILY_R1",
)
RUNTIME_ENGINE_IDS = (
    "MONTHLY_DIRECTION_3M",
    "FAST",
    "SLOW",
    "GVZ_RISK",
    "BOCPD_RETURN_SUCCESSOR_V1",
    "MACRO_EVENT_SUCCESSOR_V2",
    "CAUSAL_PATCH",
    "MOMENTUM_3M",
    "RANDOM_WALK",
    "EMERGENCY_LEVEL",
    "EMERGENCY_REVERSAL",
    "VW_MIDAS_MSVR",
)
GPR_PIT = "GPR_OFFICIAL_GIT_PIT"
CORE_GOLD = "CORE5_GOLD_USD_OZ_RESEARCH_R1"
FOUR_METAL_REFRESH_CONTRACT = Path("gold_axis_2026/GOLD_CONTROL_VW_MIDAS_MSVR_SUCCESSOR_V1_FOUR_METAL_PROSPECTIVE_SOURCE_REFRESH_CONTRACT.md")
ANCHOR_BRIDGE_CONTRACT = Path("gold_axis_2026/GOLD_CONTROL_VW_MIDAS_MSVR_SUCCESSOR_V1_XAU_TARGET_ANCHOR_BRIDGE_CONTRACT.md")


def authority_counts(cur):
    names = ("monthly_forecast_contracts", "decision_signal_snapshots", "decision_runs", "decision_events")
    out = {}
    for name in names:
        cur.execute(f"SELECT count(*) FROM {name}")
        out[name] = int(cur.fetchone()[0])
    return out


def runtime_counts(cur):
    cur.execute(
        "SELECT runtime_status, count(*)::int FROM latest_engine_runtime_state "
        "WHERE engine_id = ANY(%s) GROUP BY runtime_status ORDER BY runtime_status",
        (list(RUNTIME_ENGINE_IDS),),
    )
    return {status: int(n) for status, n in cur.fetchall()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="vw_midas_msvr_successor_v1_prospective_readiness.json")
    args = ap.parse_args()
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL is required")

    now = datetime.now(timezone.utc)
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            before = authority_counts(cur)
            runtime = runtime_counts(cur)

            cur.execute(
                "SELECT series_id, count(*)::int, max(observation_ts)::date "
                "FROM observations WHERE series_id = ANY(%s) "
                "GROUP BY series_id ORDER BY series_id",
                (list(FOUR_METALS),),
            )
            metal_state = {sid: {"rows": n, "last_observation": last.isoformat() if last else None} for sid, n, last in cur.fetchall()}

            cur.execute(
                "WITH x AS ("
                " SELECT observation_ts::date d, count(DISTINCT series_id) k "
                " FROM observations "
                " WHERE series_id = ANY(%s) AND observation_ts >= '2026-09-01' AND observation_ts < '2026-10-01' "
                " GROUP BY observation_ts::date"
                ") SELECT count(*) FILTER (WHERE k=4)::int, min(d) FILTER (WHERE k=4), max(d) FILTER (WHERE k=4) FROM x",
                (list(FOUR_METALS),),
            )
            common_n, common_first, common_last = cur.fetchone()
            common_n = int(common_n or 0)

            cur.execute(
                "SELECT count(*)::int, min(available_as_of), max(observation_ts)::date "
                "FROM observations WHERE series_id=%s AND metadata->>'origin_month'='2026-09'",
                (GPR_PIT,),
            )
            gpr_rows, gpr_available, gpr_last_obs = cur.fetchone()
            cur.execute(
                "SELECT count(*)::int FROM observations WHERE series_id=%s "
                "AND metadata->>'origin_month'='2026-09' "
                "AND observation_ts >= '2026-08-01' AND observation_ts < '2026-09-01'",
                (GPR_PIT,),
            )
            gpr_aug_rows = int(cur.fetchone()[0])

            cur.execute("SELECT max(observation_ts)::date FROM observations WHERE series_id=%s", (CORE_GOLD,))
            core_gold_last = cur.fetchone()[0]

            after = authority_counts(cur)

    four_metal_contract = FOUR_METAL_REFRESH_CONTRACT.exists()
    anchor_contract = ANCHOR_BRIDGE_CONTRACT.exists()
    origin_reached = now > ORIGIN_CUTOFF
    four_metal_complete = common_n >= 20 and common_last is not None and common_last.isoformat() >= "2026-09-27"
    gpr_ready = int(gpr_rows or 0) > 0 and gpr_aug_rows > 0 and gpr_available is not None

    blockers = []
    if not four_metal_contract:
        blockers.append("BLOCKED_FOUR_METAL_SOURCE_REFRESH_CONTRACT_NOT_FROZEN")
    if not four_metal_complete:
        blockers.append("WAITING_FOUR_METAL_SOURCE_DATA")
    if not gpr_ready:
        blockers.append("WAITING_GPR_2026_09_ORIGIN_VINTAGE")
    if not anchor_contract:
        blockers.append("BLOCKED_TARGET_ANCHOR_REFRESH_CONTRACT_NOT_FROZEN")

    if not origin_reached:
        status = "WAITING_ORIGIN_NOT_REACHED"
    elif blockers:
        status = blockers[0]
    else:
        status = "READY_FOR_IMMUTABLE_PROSPECTIVE_SHADOW_ISSUANCE"

    out = {
        "model_id": MODEL_ID,
        "scope": "PROSPECTIVE_SHADOW_READINESS_ONLY",
        "checked_at_utc": now.isoformat(),
        "forecast_origin": "2026-09-30",
        "target_month": TARGET_MONTH,
        "status": status,
        "origin_reached": origin_reached,
        "blockers": blockers,
        "four_metal": {
            "existing_r1_series_state": metal_state,
            "september_common_complete_days": common_n,
            "september_first_common_day": common_first.isoformat() if common_first else None,
            "september_last_common_day": common_last.isoformat() if common_last else None,
            "completeness_gate": four_metal_complete,
            "prospective_source_refresh_contract_frozen": four_metal_contract,
        },
        "gpr": {
            "origin_vintage_rows": int(gpr_rows or 0),
            "origin_vintage_available_as_of": gpr_available.isoformat() if gpr_available else None,
            "origin_vintage_last_observation": gpr_last_obs.isoformat() if gpr_last_obs else None,
            "required_august_observation_rows": gpr_aug_rows,
            "gate": gpr_ready,
        },
        "target_anchor": {
            "historical_core5_last_observation": core_gold_last.isoformat() if core_gold_last else None,
            "current_anchor_bridge_contract_frozen": anchor_contract,
        },
        "authority_counts_before": before,
        "authority_counts_after": after,
        "authority_invariants_unchanged": before == after,
        "runtime_counts": runtime,
        "governance": {
            "database_writes": "NONE",
            "forecast_writes": "NONE",
            "decision_writes": "NONE",
            "runtime_mutation": "NONE",
            "auto_selector": "OFF",
            "auto_ensemble": "OFF",
            "backdated_prospective_issuance": "FORBIDDEN",
        },
    }
    if before != after:
        raise RuntimeError("AUTHORITY_INVARIANT_CHANGED_DURING_READINESS_CHECK")
    Path(args.output).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "blockers": blockers, "origin_reached": origin_reached}, sort_keys=True))


if __name__ == "__main__":
    main()
