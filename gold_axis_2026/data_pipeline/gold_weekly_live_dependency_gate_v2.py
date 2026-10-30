#!/usr/bin/env python3
"""Read-only, fail-closed production dependency check for original V34 ANN and V22/BASE14.

This does NOT fit, retrain, forecast, issue risk signals, write Neon, or trade.
A clean GitHub Actions outcome means the check executed, NOT LIVE_READY.
The original weekly model requires four SAME-SOURCE daily metals with a
historical availability contract; XAU NY17 is NOT its replacement.
"""
from __future__ import annotations
import argparse
import json
import os
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

METALS = ("AU", "AG", "PT", "PD")
RESEARCH_ONLY = "RESEARCH_GIT_SNAPSHOT_NOT_PIT"
FROZEN_MODEL = "WEEKLY_H1_ANN_MLP8_TANH_ALPHA1_V1"
EXPECTED_FEATURES = 16


def target_monday(now):
    """Next not-yet-started Monday; never backdate today's live forecast."""
    today = now.astimezone(timezone.utc).date()
    days = (7 - today.weekday()) % 7
    if days == 0:
        days = 7
    return today + timedelta(days=days)


def completed_origin(target):
    prev_friday = target - timedelta(days=3)
    # StakTrakr is a UTC-DAY reference, not the NY17 session close.
    # Friday's entire UTC day must end before a complete week is available.
    # The source may publish later; every input must be seen before issuance.
    return datetime(prev_friday.year, prev_friday.month, prev_friday.day,
                    tzinfo=timezone.utc) + timedelta(days=1)


def inspect_metals(rows, now, target=None):
    """Rows: price_date, metal, evidence_status, source_captured_at.
    No imputation of missing weekday prices; 3 full four-metal shared days
    required in the previous Mon-Fri origin week (the original research minimum).
    """
    target = target or target_monday(now)
    origin = completed_origin(target)
    start = target - timedelta(days=7)
    end = target - timedelta(days=3)
    per_day = defaultdict(dict)
    errors = []
    for row in rows:
        dt = row["price_date"]
        if isinstance(dt, str):
            dt = date.fromisoformat(dt)
        if isinstance(dt, datetime):
            dt = dt.date()
        metal = row["metal"]
        if not (start <= dt <= end) or metal not in METALS:
            errors.append("OUTSIDE_EXPECTED_ORIGIN_OR_UNKNOWN_METAL")
            continue
        if metal in per_day[dt]:
            errors.append("DUPLICATE_METAL_PER_DATE")
        per_day[dt][metal] = row
    aligned = sorted(d for d, metals in per_day.items()
                     if d.weekday() < 5 and all(m in metals for m in METALS))
    bad_evidence = []
    late_capture = []
    for d in aligned:
        for metal in METALS:
            row = per_day[d][metal]
            if row["evidence_status"] != "FIRSTPRINT_PROSPECTIVE":
                bad_evidence.append((str(d), metal, row["evidence_status"]))
            captured = row.get("source_captured_at")
            if captured is None:
                late_capture.append((str(d), metal, "CAPTURE_TIME_MISSING"))
            else:
                if isinstance(captured, str):
                    captured = datetime.fromisoformat(captured.replace("Z", "+00:00"))
                if captured.tzinfo is None or captured > now:
                    late_capture.append((str(d), metal, str(captured)))
    if now < origin:
        status = "BLOCKED_ORIGIN_NOT_CLOSED"
    elif errors:
        status = "BLOCKED_INVALID_FOUR_METAL_ROWS"
    elif len(aligned) < 3:
        status = "BLOCKED_FOUR_METAL_ORIGIN_WEEK_MISSING"
    elif bad_evidence:
        status = "BLOCKED_RESEARCH_SNAPSHOT_NOT_FIRSTPRINT"
    elif late_capture:
        status = "BLOCKED_SOURCE_NOT_AVAILABLE_AT_ORIGIN"
    else:
        status = "FOUR_METAL_INPUT_PIT_CANDIDATE_ONLY"
    return {
        "status": status,
        "targetWeekMonday": target.isoformat(),
        "originWeekMonday": start.isoformat(),
        "earliestCompleteUTCWeekCutoff": origin.isoformat(),
        "originComplete": now >= origin,
        "fourMetalAlignedDays": len(aligned),
        "alignedDates": [d.isoformat() for d in aligned],
        "dataContract": "FOUR_METAL_SAME_SOURCE_WEEKLY_16D_NOT_XAU_NY17_ONLY",
        "firstprintUnverified": bool(bad_evidence),
        "lateOrMissingCapture": bool(late_capture),
        "invalidRows": sorted(set(errors)),
        "minimumAlignedDays": 3,
    }


def compose(now, market, four, live_weekly_rows, live_risk_rows):
    market_ready = market["status"] == "READY"
    # Rows alone cannot prove frozen weights, 16D features, PIT preprocessing,
    # checksum and byte-for-byte reproduction of the original model.
    weekly_status = ("BLOCKED_ORIGINAL_CHECKPOINT_AND_EXECUTOR_UNVERIFIED"
                     if four["status"] == "FOUR_METAL_INPUT_PIT_CANDIDATE_ONLY"
                     else "BLOCKED_FOUR_METAL_PREREQUISITES")
    # V22 depends on original BASE14/CFTC21 features AND chronological
    # casebook state, not only the five current headline macro observations.
    risk_status = "BLOCKED_NO_VERIFIED_ASOF_BASE14_CFTC21_V22_EXECUTOR"
    return {
        "schema": "GOLD_WEEKLY_LIVE_DEPENDENCY_GATE_V2",
        "asOfUTC": now.isoformat(),
        "status": "BLOCKED_NOT_LIVE",
        "marketData": market,
        "fourMetalWeeklyOrigin": four,
        "weeklyANN": {
            "model": FROZEN_MODEL, "features": EXPECTED_FEATURES,
            "status": weekly_status,
            "prospectiveRows": live_weekly_rows,
            "required": ["verified_original_parameters_and_input_normalization",
                         "same_source_four_metals_asof_origin",
                         "frozen_model_sha256_and_reproducible_forward_runner",
                         "prospective_firstprint_record_with_preweek_origin"],
        },
        "downsideSignals": {
            "models": ["BASE14", "V22"], "status": risk_status,
            "prospectiveRows": live_risk_rows,
            "required": ["original_BASE14_and_CFTC21_features_asof",
                         "V22_seven_rules_and_prior_day_state",
                         "release_time_and_source_vintage_proof",
                         "timestamped_frozen_signals_and_replay_parity"],
        },
        "marketFiveSeriesReady": market_ready,
        "sourceIsResearchNotProspective": four["firstprintUnverified"],
        "liveForecastPublished": False,
        "liveRiskSignalPublished": False,
        "monthlyCalibrationPaused": True,
        "portfolioUnchanged": True,
        "databaseWrites": False,
    }


def from_neon(now):
    import psycopg
    from psycopg.rows import dict_row
    from gold_weekly_live_readiness_v1 import REQUIRED, evaluate_sources
    uri = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not uri:
        raise RuntimeError("MISSING_NEON_DATABASE_URL")
    target = target_monday(now)
    origin_monday = target - timedelta(days=7)
    origin_friday = target - timedelta(days=3)
    with psycopg.connect(uri, row_factory=dict_row, connect_timeout=12,
                         options="-c default_transaction_read_only=on") as db:
        with db.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT ON (series_id) series_id,
                     observation_ts AS last_observed, quality_status
                FROM public.canonical_latest
                WHERE series_id = ANY(%s)
                ORDER BY series_id, observation_ts DESC
            """, (list(REQUIRED),))
            market = evaluate_sources(cur.fetchall(), now)
            cur.execute("""
                SELECT DISTINCT ON (price_date,metal)
                    price_date,metal,evidence_class AS evidence_status,
                    first_observed_utc AS source_captured_at
                FROM gold_weekly_live.staktrakr_daily_utc_reference_v1
                WHERE price_date BETWEEN %s AND %s
                ORDER BY price_date,metal,first_observed_utc DESC
            """, (origin_monday, origin_friday))
            four = inspect_metals(cur.fetchall(), now, target)
            cur.execute("SELECT count(*) AS n FROM gold_weekly_live.weekly_forecast_records")
            weekly = int(cur.fetchone()["n"])
            cur.execute("SELECT count(*) AS n FROM gold_weekly_live.downside_signal_records")
            risk = int(cur.fetchone()["n"])
    return compose(now, market, four, weekly, risk)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out")
    parser.add_argument("--strict-live", action="store_true")
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    result = from_neon(now)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    print(payload, flush=True)
    if args.out:
        Path(args.out).write_text(payload + "\n", encoding="utf-8")
    return 3 if args.strict_live and result["status"] != "READY" else 0


if __name__ == "__main__":
    raise SystemExit(main())
