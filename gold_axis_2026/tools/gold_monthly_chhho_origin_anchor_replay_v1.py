"""ChHHO monthly original-vs-prefix-price scientific comparison.

Re-runs the *unchanged* original 24x45x3 ChHHO optimizer and chronological
ANFIS local refinement on the frozen 2022-2024 DEV snapshot. Price-level
alternatives affect ONLY the final exp(return)*anchor multiplication, not
feature or model hyperparameters. Not a certified as-of initial publication.
"""
from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import math
from datetime import date, timedelta
from pathlib import Path

import numpy as np

import gold_monthly_dev_snapshot_v1 as snapshots
import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_stage3c_literature_v1 as chhho

EXPECTED_SHA = "2111e394f60d131995273789fc014dc339db4e1b7672095c89117c133879a3eb"
REFERENCE_DEV_SAE = 1413.0297794085
REFERENCE_DEV_DIRECTION = 23
FIRST, LAST = "2022-04", "2024-12"

def origin_cutoff(origin: str, strict: bool = True) -> str:
    year, month = map(int, origin.split("-"))
    last = date(year, month, calendar.monthrange(year, month)[1])
    # If observations are date-only, last-calendar-day prices cannot be proven
    # available before the close. Strict arm excludes the entire last day.
    return (last - timedelta(days=1) if strict else last).isoformat()

def prefix_origin_price(rows: list[dict], origin: str, strict: bool = True) -> dict:
    """Price average from origin-dated observed trading days only.

    The date cutoff prevents target-month price use. NO claim that these
    retrospectively archived observations have verified first-publication
    timestamps. We deliberately prohibit missing-date or weekend substitution.
    """
    cutoff = origin_cutoff(origin, strict=strict)
    selected = [r for r in rows if r["date"][:7] == origin and r["date"] <= cutoff]
    if len(selected) < 15:
        raise RuntimeError(f"ASOF_ORIGIN_PREFIX_COVERAGE_FAIL origin={origin} n={len(selected)}")
    days = [r["date"] for r in selected]
    if days != sorted(set(days)):
        raise RuntimeError(f"ASOF_ORIGIN_DATES_NOT_SORTED_OR_UNIQUE origin={origin}")
    if any(date.fromisoformat(day).isoweekday() > 5 for day in days):
        raise RuntimeError(f"ASOF_ORIGIN_NON_BUSINESS_DAY origin={origin}")
    values = [float(r["Gold"]) for r in selected]
    if not all(math.isfinite(p) and p > 0 for p in values):
        raise RuntimeError(f"ASOF_ORIGIN_BAD_PRICE origin={origin}")
    return {
        "anchor_usd_oz": float(np.mean(values)),
        "origin": origin,
        "cutoff_exclusive_of_month_end_date": strict,
        "cutoff_day_inclusive": cutoff,
        "first_observed_date": days[0],
        "last_observed_date": days[-1],
        "observed_business_day_count": len(days),
        "series_id": "XAU_STAKTRAKR_RESEARCH_DAILY_R1",
        "first_publication_time_verified": False,
        "evidence_class": "HISTORICAL_RECONSTRUCTION_NO_ORIGINAL_FIRSTPRINT",
    }

def metrics(rows, variant: str, target: str) -> dict:
    f = np.array([r["forecasts"][variant] for r in rows])
    a = np.array([r["targets"][target] for r in rows])
    ref = np.array([r["anchors"][variant] for r in rows])
    ae = abs(f-a)
    return {
        "n":len(rows), "sum_abs_error":float(ae.sum()), "MAE_usd":float(ae.mean()),
        "MAPE_pct":float(np.mean(ae/a)*100),
        "direction_correct":int(np.sum(np.sign(f-ref)==np.sign(a-ref))),
        "per_year_SAE":{yr:float(sum(e for e,r in zip(ae,rows) if r["target"].startswith(yr)))
                        for yr in ("2022","2023","2024")},
    }

def run(snapshot_file: str) -> dict:
    bundle, metadata = snapshots.load_snapshot(snapshot_file)
    if metadata["payload_sha256"] != EXPECTED_SHA:
        raise RuntimeError("NOT_AUTHORIZED_FROZEN_DEV_SNAPSHOT")
    document = json.loads(Path(snapshot_file).read_text(encoding="utf-8"))
    dated = document["payload"]["daily_common_rows"]
    if not dated or dated != sorted(dated, key=lambda r:r["date"]):
        raise RuntimeError("BAD_DAILY_SOURCE_SORT")
    if any(r["date"] >= "2025-01-01" for r in dated):
        raise RuntimeError("FUTURE_DATE_IN_FROZEN_DEV_SOURCE")

    rows = []
    for target in base.month_range(FIRST,LAST):
        origin = base.month_shift(target,-1)
        # Last month has no label; optimizer sees only preceding completed Y.
        samples = base.all_samples_at_origin(bundle,target,governed=True)
        if samples[target][1] is not None:
            raise RuntimeError("TARGET_LABEL_SHOULD_BE_ABSENT")
        prediction, training_rows, diag = chhho.select(samples,target,"CHHHO")
        pred_return = float(pred[0])
        original = float(bundle.core_gold[origin])
        provisional = prefix_origin_price(dated,origin,strict=True)
        full = prefix_origin_price(dated,origin,strict=False)
        anchors = {"CORE5_FINAL_HISTORICAL":original,
                   "STAK_PREFIX_STRICT_DATE":provisional["anchor_usd_oz"],
                   "STAK_FULL_ORIGIN_MONTH":full["anchor_usd_oz"]}
        forecasts = {k:float(v*math.exp(pred_return)) for k,v in anchors.items()}
        if origin not in bundle.monthly_metal["Gold"] or target not in bundle.monthly_metal["Gold"]:
            raise RuntimeError("TARGET_MATCHED_EVALUATION_LABEL_ABSENT")
        rows.append({
            "target":target, "origin":origin, "training_rows":training_rows,
            "optimizer_diagnostics":diag, "pred_log_return_gold":pred_return,
            "origin_date_cutoff":provisional["cutoff_day_inclusive"],
            "prefix":provisional, "full":full,
            "anchors":anchors,
            "forecasts":forecasts,
            "targets":{"CORE5_FINAL_HISTORICAL":float(bundle.core_gold[target]),
                       "STAK_MONTHLY_MATCHED":float(bundle.monthly_metal["Gold"][target])},
            "provenance_flags":{
                "future_target_label_used_in_fit":False,
                "origin_daily_firstprint_verified":False,
                "core5_origin_final_mean_asof_verified":False,
            }
        })
        print(f"ANCHOR_REPLAY_PROGRESS {target} {len(rows)}/33",flush=True)
    old=metrics(rows,"CORE5_FINAL_HISTORICAL","CORE5_FINAL_HISTORICAL")
    if abs(old["sum_abs_error"]-REFERENCE_DEV_SAE)>1e-3 or old["direction_correct"]!=REFERENCE_DEV_DIRECTION:
        raise RuntimeError(f"ORIGINAL_CHHHO_PARITY_FAIL {old}")
    score={}
    for variant in ("CORE5_FINAL_HISTORICAL","STAK_PREFIX_STRICT_DATE","STAK_FULL_ORIGIN_MONTH"):
        score[variant]={
            "vs_CORE5_FINAL_HISTORICAL":metrics(rows,variant,"CORE5_FINAL_HISTORICAL"),
            "vs_STAK_MONTHLY_MATCHED":metrics(rows,variant,"STAK_MONTHLY_MATCHED"),
        }
    source_sha=hashlib.sha256(snapshots.canonical_bytes(document["payload"])).hexdigest()
    return {
        "schema":"GOLD_MONTHLY_CHHHO_ORIGIN_ANCHOR_REPLAY_V1",
        "status":"SCIENTIFIC_HISTORICAL_REPLAY_NOT_ORIGINAL_LIVE_PIT",
        "model":"ORIGINAL_CHHHO_ANFIS_UNCHANGED_FULL_24x45x3",
        "snapshot_payload_sha256":source_sha,
        "selection_period":"DEV 2022-04..2024-12",
        "future_period_data_loaded":False,
        "model_retrained_each_outer_origin":True,
        "forecast_target_prices_read_only_for_scoring":True,
        "origin_price_firstprint_verified":False,
        "no_production_change":True,
        "methods":{
            "CORE5_FINAL_HISTORICAL":"retrospective final monthly origin price, not original as-of",
            "STAK_PREFIX_STRICT_DATE":"mean of origin-month spot prices dated no later than day BEFORE last calendar date, 15+ business days, reconstructed history",
            "STAK_FULL_ORIGIN_MONTH":"mean through last calendar date of origin month, reconstructed history",
        },
        "scores":score,"rows":rows,
        "baseline_parity":{
            "pass":True,"reference_DEV_SAE":REFERENCE_DEV_SAE,
            "recomputed_DEV_SAE":old["sum_abs_error"],
            "direction":old["direction_correct"],
        },
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    result=run(args.snapshot)
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf-8")
    print("MONTHLY_ANCHOR_REPLAY_GATE=PASS",flush=True)
    print(json.dumps({"baseline":result["baseline_parity"],"scores":result["scores"]},sort_keys=True),flush=True)

if __name__=="__main__":
    main()
