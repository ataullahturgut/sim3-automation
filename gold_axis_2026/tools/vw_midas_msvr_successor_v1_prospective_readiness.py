from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import date, datetime, timezone
from pathlib import Path

import psycopg
import requests

MODEL_ID = "VW_MIDAS_MSVR_SUCCESSOR_V1"
ORIGIN_CUTOFF = datetime(2026, 9, 30, 21, 0, 0, tzinfo=timezone.utc)
ORIGIN_DATE = date(2026, 9, 30)
TARGET_MONTH = "2026-10"

STAK_REPO = "lbruton/StakTrakr"
STAK_PATH = "data/spot-history-2026.json"
STAK_COMMITS_URL = f"https://api.github.com/repos/{STAK_REPO}/commits"
STAK_RAW = f"https://raw.githubusercontent.com/{STAK_REPO}"
METALS = ("Gold", "Silver", "Platinum", "Palladium")
HISTORICAL_SERIES = {
    "Gold": "XAU_STAKTRAKR_RESEARCH_DAILY_R1",
    "Silver": "XAG_STAKTRAKR_RESEARCH_DAILY_R1",
    "Platinum": "XPT_STAKTRAKR_RESEARCH_DAILY_R1",
    "Palladium": "XPD_STAKTRAKR_RESEARCH_DAILY_R1",
}
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
FOUR_METAL_REFRESH_CONTRACT = Path(
    "gold_axis_2026/GOLD_CONTROL_VW_MIDAS_MSVR_SUCCESSOR_V1_FOUR_METAL_PROSPECTIVE_SOURCE_REFRESH_CONTRACT.md"
)
ANCHOR_BRIDGE_CONTRACT = Path(
    "gold_axis_2026/GOLD_CONTROL_VW_MIDAS_MSVR_SUCCESSOR_V1_XAU_TARGET_ANCHOR_BRIDGE_CONTRACT.md"
)


def authority_counts(cur):
    names = (
        "monthly_forecast_contracts",
        "decision_signal_snapshots",
        "decision_runs",
        "decision_events",
    )
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


def fetch_historical_july(cur):
    out = {m: {} for m in METALS}
    for metal, sid in HISTORICAL_SERIES.items():
        cur.execute(
            "SELECT observation_ts::date,value FROM observations "
            "WHERE series_id=%s AND observation_ts >= '2026-07-01' "
            "AND observation_ts < '2026-08-01' ORDER BY observation_ts",
            (sid,),
        )
        out[metal] = {d: float(v) for d, v in cur.fetchall()}
    return out


def fetch_stak_snapshot():
    s = requests.Session()
    s.headers.update({"User-Agent": "gold-control-prospective-readiness/1.0"})
    r = s.get(STAK_COMMITS_URL, params={"path": STAK_PATH, "per_page": 1}, timeout=30)
    r.raise_for_status()
    commits = r.json()
    if not isinstance(commits, list) or not commits:
        raise RuntimeError("STAKTRAKR_FILE_COMMIT_NOT_FOUND")
    commit = commits[0]
    sha = str(commit["sha"])
    commit_time = (
        commit.get("commit", {}).get("committer", {}).get("date")
        or commit.get("commit", {}).get("author", {}).get("date")
    )
    raw_url = f"{STAK_RAW}/{sha}/{STAK_PATH}"
    rr = s.get(raw_url, timeout=60)
    rr.raise_for_status()
    raw = rr.content
    payload = rr.json()
    if not isinstance(payload, list):
        raise RuntimeError("STAKTRAKR_SCHEMA_NOT_LIST")

    rows = {m: {} for m in METALS}
    conflicts = []
    for row in payload:
        if not isinstance(row, dict):
            continue
        metal = str(row.get("metal") or "")
        if metal not in rows:
            continue
        try:
            d = datetime.fromisoformat(str(row.get("timestamp")).replace("Z", "+00:00")).date()
            value = float(row.get("spot"))
        except (TypeError, ValueError):
            continue
        if d > ORIGIN_DATE:
            continue
        if d in rows[metal] and abs(rows[metal][d] - value) > 1e-12:
            conflicts.append({"metal": metal, "date": d.isoformat()})
            continue
        rows[metal][d] = value

    common = sorted(set.intersection(*(set(rows[m]) for m in METALS)))
    by_month = {}
    for month in ("2026-07", "2026-08", "2026-09"):
        ds = [d for d in common if d.isoformat().startswith(month)]
        by_month[month] = {
            "common_days": len(ds),
            "first": ds[0].isoformat() if ds else None,
            "last": ds[-1].isoformat() if ds else None,
        }
    return {
        "commit_sha": sha,
        "commit_time": commit_time,
        "payload_sha256": hashlib.sha256(raw).hexdigest(),
        "rows": rows,
        "common_dates": common,
        "months": by_month,
        "conflicting_duplicates": conflicts,
    }


def continuity_check(historical, snapshot):
    hist_common = sorted(set.intersection(*(set(historical[m]) for m in METALS)))
    snap_rows = snapshot["rows"]
    snap_common = set.intersection(*(set(snap_rows[m]) for m in METALS))
    compared = 0
    mismatches = []
    for d in hist_common:
        if d not in snap_common:
            mismatches.append({"date": d.isoformat(), "reason": "MISSING_IN_PROSPECTIVE_SNAPSHOT"})
            continue
        for metal in METALS:
            compared += 1
            old = historical[metal][d]
            new = snap_rows[metal][d]
            if abs(old - new) > 1e-9:
                mismatches.append(
                    {
                        "date": d.isoformat(),
                        "metal": metal,
                        "old": old,
                        "new": new,
                    }
                )
    gate = bool(hist_common) and not mismatches and not snapshot["conflicting_duplicates"]
    return {
        "historical_july_common_days": len(hist_common),
        "compared_values": compared,
        "mismatch_count": len(mismatches),
        "mismatches_preview": mismatches[:10],
        "gate": gate,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--output",
        default="vw_midas_msvr_successor_v1_prospective_readiness.json",
    )
    args = ap.parse_args()
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL is required")

    now = datetime.now(timezone.utc)
    source_error = None
    try:
        snapshot = fetch_stak_snapshot()
    except Exception as exc:
        snapshot = None
        source_error = f"{type(exc).__name__}:{exc}"

    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            before = authority_counts(cur)
            runtime = runtime_counts(cur)
            historical_july = fetch_historical_july(cur)

            cur.execute(
                "SELECT count(*)::int, min(available_as_of), max(observation_ts)::date "
                "FROM observations WHERE series_id=%s "
                "AND metadata->>'origin_month'='2026-09'",
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
            cur.execute(
                "SELECT max(metadata->>'origin_month') FROM observations WHERE series_id=%s",
                (GPR_PIT,),
            )
            gpr_latest_origin = cur.fetchone()[0]
            cur.execute(
                "SELECT max(observation_ts)::date FROM observations WHERE series_id=%s",
                (CORE_GOLD,),
            )
            core_gold_last = cur.fetchone()[0]
            after = authority_counts(cur)

    continuity = continuity_check(historical_july, snapshot) if snapshot else {
        "historical_july_common_days": 0,
        "compared_values": 0,
        "mismatch_count": 0,
        "mismatches_preview": [],
        "gate": False,
    }

    four_metal_contract = FOUR_METAL_REFRESH_CONTRACT.exists()
    anchor_contract = ANCHOR_BRIDGE_CONTRACT.exists()
    origin_reached = now >= ORIGIN_CUTOFF
    august = snapshot["months"]["2026-08"] if snapshot else {"common_days": 0, "first": None, "last": None}
    september = snapshot["months"]["2026-09"] if snapshot else {"common_days": 0, "first": None, "last": None}
    four_metal_complete = (
        snapshot is not None
        and continuity["gate"]
        and august["common_days"] >= 20
        and september["common_days"] >= 20
        and september["last"] is not None
        and september["last"] >= "2026-09-27"
    )
    gpr_ready = int(gpr_rows or 0) > 0 and gpr_aug_rows > 0 and gpr_available is not None

    blockers = []
    if not four_metal_contract:
        blockers.append("BLOCKED_FOUR_METAL_SOURCE_REFRESH_CONTRACT_NOT_FROZEN")
    if snapshot is None:
        blockers.append("WAITING_FOUR_METAL_SOURCE_DATA")
    elif not continuity["gate"]:
        blockers.append("BLOCKED_STAKTRAKR_PROSPECTIVE_HISTORY_REVISION_OR_SEMANTIC_DRIFT")
    elif not four_metal_complete:
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
        "forecast_origin": "2026-09-30T21:00:00Z",
        "target_month": TARGET_MONTH,
        "status": status,
        "origin_reached": origin_reached,
        "blockers": blockers,
        "four_metal": {
            "source_contract_frozen": four_metal_contract,
            "source_error": source_error,
            "snapshot_commit_sha": snapshot["commit_sha"] if snapshot else None,
            "snapshot_commit_time": snapshot["commit_time"] if snapshot else None,
            "payload_sha256": snapshot["payload_sha256"] if snapshot else None,
            "august": august,
            "september": september,
            "continuity": continuity,
            "completeness_gate": four_metal_complete,
        },
        "gpr": {
            "latest_origin_vintage_present": gpr_latest_origin,
            "origin_vintage_rows": int(gpr_rows or 0),
            "origin_vintage_available_as_of": gpr_available.isoformat() if gpr_available else None,
            "origin_vintage_last_observation": gpr_last_obs.isoformat() if gpr_last_obs else None,
            "required_august_observation_rows": gpr_aug_rows,
            "gate": gpr_ready,
        },
        "target_anchor": {
            "historical_core5_last_observation": core_gold_last.isoformat() if core_gold_last else None,
            "anchor_bridge_contract_frozen": anchor_contract,
            "prospective_measurement": "STAKTRAKR_COMMON4_GOLD_MONTHLY_MEAN_PROSPECTIVE_V1",
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
