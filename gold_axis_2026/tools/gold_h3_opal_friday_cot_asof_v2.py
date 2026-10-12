#!/usr/bin/env python3
"""Nonbinding H3 OPAL Friday-release COT research challenger. Does not overwrite frozen H3.

Uses issued-at assumption D1 15:00 Turkey; true actual issued_at is NOT archived.
COT official special overrides from the existing PIT authority take precedence.
Default Tuesday->Friday 15:30 New York is provisional in holiday weeks.
Recomputes OPAL only; does not claim HELIOS, SAGE, or DPTC full rerun.
"""
from __future__ import annotations

from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import json

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

AX = Path(__file__).resolve().parents[1]
PANEL = AX / "GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_OPAL_PANEL.csv"
RAW_COT = AX / "GOLD_COT_GOLD_PIT_STATE_RAW_REBUILT_2026-10-06.csv"
BASE = AX / "GOLD_H3_CLEAN_OPAL_PREDICTIONS_2026-10-03.csv"
OUT = AX / "GOLD_H3_OPAL_FRIDAY_COT_ASOF_V2_RESEARCH.csv"
SUMMARY = AX / "GOLD_H3_OPAL_FRIDAY_COT_ASOF_V2_RESEARCH.json"

TZ_NY = ZoneInfo("America/New_York")
TZ_TR = ZoneInfo("Europe/Istanbul")
COT_BASIC = ["opt_mm_net", "opt_prod_net", "opt_swap_net", "opt_other_net",
             "d_opt_mm_net", "d_opt_prod_net", "opt_mm_z52", "opt_prod_z52",
             "opt_swap_z52", "opt_other_z52", "spec_hedger_gap",
             "spec_swap_gap", "fut_mm_net", "fut_prod_net"]
FEATURES = COT_BASIC + ["trend_x_opt_mm", "trend_x_opt_prod",
                        "trend_x_spec_hedger_gap", "trend_strength"]
THRESHOLD = 0.70


def model() -> Pipeline:
    return Pipeline([
        ("scale", StandardScaler()),
        ("logreg", LogisticRegression(C=1.0, solver="lbfgs", max_iter=3000,
                                      class_weight="balanced", random_state=20261003)),
    ])


def timestamp_issue(day: pd.Timestamp) -> pd.Timestamp:
    dt = datetime.combine(day.date(), time(15, 0), tzinfo=TZ_TR)
    return pd.Timestamp(dt).tz_convert("UTC")


def timestamp_friday(report: pd.Timestamp) -> pd.Timestamp:
    # Tuesday report under ordinary CFTC weekly publication; holidays need exceptions.
    dt = datetime.combine((report + pd.Timedelta(days=3)).date(),
                          time(15, 30), tzinfo=TZ_NY)
    return pd.Timestamp(dt).tz_convert("UTC")


def main() -> None:
    p = pd.read_csv(PANEL)
    cot = pd.read_csv(RAW_COT)
    old = pd.read_csv(BASE)
    for col in ("feature_cutoff_date", "forecast_issue_date", "target_end_date_h3"):
        p[col] = pd.to_datetime(p[col], errors="raise")
    p = p.sort_values("forecast_issue_date").reset_index(drop=True)
    cot["report_date"] = pd.to_datetime(cot["report_date"], errors="raise")
    cot["released_utc"] = cot.report_date.map(timestamp_friday)
    overrides = cot.cot_official_special_release_at_utc.astype("string")
    special = overrides.notna() & overrides.str.strip().fillna("").ne("")
    if special.any():
        cot.loc[special, "released_utc"] = pd.to_datetime(
            cot.loc[special, "cot_official_special_release_at_utc"], utc=True)
    cot = cot.sort_values("released_utc").reset_index(drop=True)
    for f in COT_BASIC:
        cot[f] = pd.to_numeric(cot[f], errors="raise")
    if cot[COT_BASIC].isna().any().any():
        cot = cot.dropna(subset=COT_BASIC)
    p["assumed_issued_at_utc"] = p.forecast_issue_date.map(timestamp_issue)

    z = pd.merge_asof(
        p.sort_values("assumed_issued_at_utc"),
        cot[["released_utc", "report_date"] + COT_BASIC].sort_values("released_utc"),
        left_on="assumed_issued_at_utc", right_on="released_utc",
        direction="backward", suffixes=("", "_new"))
    z = z.dropna(subset=["report_date"] + [f + "_new" for f in COT_BASIC])
    for f in COT_BASIC:
        z[f] = z.pop(f + "_new").astype(float)
    sign = np.where(z.momentum_up.astype(int).eq(1), 1.0, -1.0)
    z["trend_x_opt_mm"] = sign * z.opt_mm_net
    z["trend_x_opt_prod"] = sign * z.opt_prod_net
    z["trend_x_spec_hedger_gap"] = sign * z.spec_hedger_gap
    z = z.sort_values("forecast_issue_date").reset_index(drop=True)
    p["month_key"] = p.forecast_issue_date.dt.strftime("%Y-%m")
    z["month_key"] = z.forecast_issue_date.dt.strftime("%Y-%m")

    b = old[["forecast_issue_date", "p_reversal", "override", "p_opal"]].copy()
    b["forecast_issue_date"] = pd.to_datetime(b.forecast_issue_date)
    results = []
    validation = []
    for month in sorted(z.loc[z.forecast_issue_date >= "2025-01-01", "month_key"].unique()):
        te = z[z.month_key.eq(month)].copy()
        cutoff = te.feature_cutoff_date.min()
        first_issue = te.forecast_issue_date.min()
        train = z[(z.target_end_date_h3 <= cutoff) &
                  (z.forecast_issue_date < first_issue)]
        train_original = p[(p.target_end_date_h3 <= cutoff) &
                           (p.forecast_issue_date < first_issue)]
        if len(train) < 80 or train.reversal_target.nunique() < 2:
            continue
        # Exact sklearn original-model parity check, against frozen clean OPAL outputs
        base_model = model().fit(train_original[FEATURES].to_numpy(float),
                                 train_original.reversal_target.astype(int))
        test_original = p[p.month_key.eq(month)]
        orig_pred = pd.DataFrame({
            "forecast_issue_date": test_original.forecast_issue_date.to_numpy(),
            "recomputed": base_model.predict_proba(test_original[FEATURES].to_numpy(float))[:, 1]
        })
        check = orig_pred.merge(b, on="forecast_issue_date", how="inner")
        if not check.empty:
            validation.append(float((check.recomputed - check.p_reversal).abs().max()))

        challenger = model().fit(train[FEATURES].to_numpy(float),
                                 train.reversal_target.astype(int))
        probs = challenger.predict_proba(te[FEATURES].to_numpy(float))[:, 1]
        for row, prob in zip(te.itertuples(index=False), probs):
            follows = bool(row.aurora_follows_momentum)
            flip = bool(follows and prob >= THRESHOLD)
            p_opal = ((1.0 - prob) if int(row.momentum_up) == 1 else prob) if flip else float(row.p_aurora)
            results.append({
                "forecast_issue_date": row.forecast_issue_date.date().isoformat(),
                "feature_cutoff_date": row.feature_cutoff_date.date().isoformat(),
                "target_end_date_h3": row.target_end_date_h3.date().isoformat(),
                "cot_report_date_friday_asof": row.report_date.date().isoformat(),
                "cot_released_at_utc": row.released_utc.isoformat(),
                "assumed_issue_at_utc": row.assumed_issued_at_utc.isoformat(),
                "train_n": len(train), "p_reversal_friday": prob,
                "friday_override": flip, "p_opal_friday": p_opal,
                "friday_pred_up": int(p_opal >= 0.5), "y_up": int(row.y_up),
                "label_status": "RETROSPECTIVE_POSTHOC"
            })
    out = pd.DataFrame(results)
    if out.empty:
        raise RuntimeError("NO_RESULT")
    out["correct_friday"] = out.friday_pred_up.eq(out.y_up.astype(int))
    parity_max = max(validation) if validation else None
    # Require historical model replication close enough to assess near-threshold changes.
    if parity_max is None or parity_max > 0.008:
        raise RuntimeError(f"FROZEN_SKLEARN_BASELINE_PARITY_FAIL max_abs={parity_max}")
    out.to_csv(OUT, index=False)
    s = {"status": "NONBINDING_OPAL_RETRAIN_RESEARCH_ONLY",
         "baseline_probability_reproduction_max_abs": parity_max,
         "friday_available_clock": "15:30 New York (special delays override), 15:00 Turkey assumed issue",
         "model": "OPAL-only. Full HELIOS/SAGE/RuleFlow/DPTC must be sequentially re-run.",
         "monthly": {}}
    out["month"] = out.forecast_issue_date.str.slice(0, 7)
    for month, g in out.groupby("month"):
        s["monthly"][month] = {"n": len(g), "correct": int(g.correct_friday.sum()),
                               "overrides": int(g.friday_override.sum())}
    SUMMARY.write_text(json.dumps(s, indent=2) + "\n")
    print(json.dumps(s, indent=2))


if __name__ == "__main__":
    main()
