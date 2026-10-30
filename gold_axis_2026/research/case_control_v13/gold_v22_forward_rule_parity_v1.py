#!/usr/bin/env python3
"""As-of-only seven-rule V22 scorer; strict parity with original 647 research days.

Consumes original same-date BASE14/V18/V19/CFTC features and V21 WATCH inputs.
Does not train the BASE14 upstream model, assert firstprint market provenance,
inspect target outcome labels, issue alarms, or write a production database.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

from risk_v22_slope_decision import read_original

OUT = Path(__file__).resolve().parent / "outputs"


def check(condition, msg):
    if not bool(condition):
        raise AssertionError("V22_FORWARD_RULE_GUARD_" + msg)


def source_rows():
    s = pd.read_csv(OUT / "v19_asof_21_variable_panel.csv")
    baseline = read_original()
    watch = pd.read_csv(OUT / "v21_daily_shadow.csv")[
        ["origin", "BI_v21_fragility_watch"]]
    data = (s.merge(baseline, on="origin", validate="one_to_one")
              .merge(watch, on="origin", validate="one_to_one")
              .sort_values("origin").reset_index(drop=True))
    check(len(data) == 647 and data.origin.is_unique, "SOURCE_647_ORIGINS")
    return data


def score_one(now, yesterday, prior_five, prior_decision):
    """Only as-of feature rows and previous day's computed state.
    No y1/y5/next10 fields may influence an actionable status.
    """
    current = str(now.origin)
    prev_ok = (yesterday is not None
               and 0 < (pd.Timestamp(current) -
                         pd.Timestamp(str(yesterday.origin))).days <= 4)
    accelerate = (100 * (now.AU_ret5 - prior_five.AU_ret5)
                  if prior_five is not None else float("nan"))
    one_day = (100 * (now.price / yesterday.price - 1)
               if prev_ok else float("nan"))
    red = now.alert_level == "RED"
    yellow = now.alert_level == "YELLOW"
    strong = bool(now.strong)
    why = str(now.why)
    p1 = bool(red and strong and np.isfinite(accelerate) and accelerate > 1)
    p2 = bool(red and strong and
              ("CFTC_CONFIRMED_RISK_ACCELERATION" in why or
               "CFTC_RISK_ACCEL" in why))
    p3 = bool(red and strong and np.isfinite(one_day)
              and one_day <= -1.5 and "GVZ" in why)
    p4 = bool(red and strong and now.gvz_level >= 35 and now.rsi14 >= .55)
    core = p1 or p2 or p3 or p4
    # V22 allows one day of memory, but cannot recursively extend P5.
    previous_core = (bool(prior_decision["original_RED_core"])
                     if prev_ok and prior_decision else False)
    previous_up = (bool(prior_decision["five_day_gold_pct"] > 0)
                   if prev_ok and prior_decision else False)
    p5 = bool(red and strong and now.AU_ret5 > 0 and previous_core and previous_up)
    p6 = bool(yellow and strong)
    p7 = bool(now.BI_v21_fragility_watch)
    check(not p7 or now.alert_level == "NORMAL", "V21_WATCH_NOT_NORMAL")
    selected = core or p5 or p6 or p7
    if core or p5:
        status = "ACTIVE_REVIEW"
    elif p6:
        status = "CONTINUATION_REVIEW"
    elif p7:
        status = "FRAGILITY_WATCH"
    elif red:
        status = "ORIGINAL_RED_REVIEW_ONLY"
    else:
        status = "NO_ACTIONABLE_REVIEW"
    reasons = "|".join(name for yes, name in [
        (p1, "MOMENTUM_ACCELERATES"),
        (p2, "CFTC_CONFIRM"),
        (p3, "GVZ_SHOCK"),
        (p4, "EXTREME_GVZ"),
        (p5, "ONE_DAY_RED_MEMORY"),
        (p6, "V18_ONE_DAY_YELLOW"),
        (p7, "V21_NORMAL_FRAGILITY"),
    ] if yes)
    if now.AU_ret5 < 0:
        slope = "DOWN_5DAY"
    elif not np.isfinite(accelerate):
        slope = "UNKNOWN"
    elif accelerate > 1:
        slope = "UP_ACCELERATING"
    elif accelerate < -1:
        slope = "UP_DECELERATING"
    else:
        slope = "UP_STABLE"
    return {
        "origin": current, "original_RED_core": core,
        "five_day_gold_pct": float(100 * now.AU_ret5),
        "five_day_acceleration_pp": float(accelerate),
        "one_day_gold_pct": float(one_day),
        "slope": slope,
        "effective_review": bool(selected),
        "effective_level": status, "effective_reasons": reasons,
        "active_RED_phase": bool(core or p5),
        "yellow_carry": bool(p6), "watch": bool(p7),
        "original_alert_changed": False, "live_enabled": False,
    }


def score_history(data):
    all_decisions = []
    for _, group in data.groupby(data.origin.str[:4], sort=True):
        group = group.reset_index(drop=True)
        previous_decision = None
        for i, row in group.iterrows():
            previous = group.iloc[i - 1] if i else None
            fifth = group.iloc[i - 5] if i >= 5 else None
            calculated = score_one(row, previous, fifth, previous_decision)
            all_decisions.append(calculated)
            previous_decision = calculated
    return pd.DataFrame(all_decisions)


def parity():
    data = source_rows()
    got = score_history(data)
    original = (pd.read_csv(OUT / "v22_daily_decisions.csv")
                .sort_values("origin").reset_index(drop=True))
    check(len(got) == 647 and len(original) == 647, "ROWS_ORIGINAL")
    check(got.origin.tolist() == original.origin.tolist(), "DATES_PARITY")
    strings = ["slope", "effective_level", "effective_reasons"]
    bools = ["original_RED_core", "effective_review", "active_RED_phase",
             "yellow_carry", "watch", "original_alert_changed", "live_enabled"]
    floats = ["five_day_gold_pct", "five_day_acceleration_pp", "one_day_gold_pct"]
    for key in strings:
        a = got[key].fillna("").astype(str).tolist()
        b = original[key].fillna("").astype(str).tolist()
        check(a == b, "STRING_" + key)
    for key in bools:
        check(got[key].tolist() == original[key].tolist(), "BOOL_" + key)
    for key in floats:
        check(np.allclose(got[key], original[key], rtol=0, atol=1e-10,
                          equal_nan=True), "NUMERIC_" + key)
    # A target outcome column must not alter any output, even if poisoned.
    poisoned = data.copy()
    poisoned["y5_AUDIT_ONLY"] = False
    poisoned["y1_AUDIT_ONLY"] = True
    again = score_history(poisoned)
    check(again.equals(got), "FUTURE_LABEL_POISON_INFLUENCED_SIGNAL")
    result = {
        "status": "V22_SEVEN_RULE_FORWARD_PARITY_PASS_RESEARCH_ONLY",
        "dates": len(got), "original_rules_unchanged": True,
        "labels_used": False, "upstream_BASE14_CFTC21_live_ready": False,
        "data_firstprint_certified": False,
        "live_signals_issued": 0, "neon_writes": False,
    }
    print(json.dumps(result, sort_keys=True, indent=2), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["historical-parity"], required=True)
    parser.add_argument("--out", default="")
    args = parser.parse_args()
    result = parity()
    if args.out:
        Path(args.out).write_text(json.dumps(result, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
