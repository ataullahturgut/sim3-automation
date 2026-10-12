#!/usr/bin/env python3
"""R64 offline exact-sklearn rerun of R61/R62/R63 with R60 COT release calendar.

Not executed in the connected GitHub-only analysis runtime; run in a checked-out
repo with pandas/numpy/scikit-learn. No frozen source file is overwritten.
Historical 2026 retrospective models are not prospective.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

AX = Path(__file__).resolve().parents[1]
ROOT = AX.parent
TOOLS = AX / "tools"
sys.path.insert(0, str(TOOLS))
import gold_h3_helios_v1 as h1
import gold_h3_helios_v2 as h2
import gold_h3_helios_v3_gt as h3
import gold_h3_helios_v4_rge as h4
import gold_h3_helios_v5_dce as h5
import gold_h3_remaining53_signal_audit as alarm_source

BASIC = ("opt_mm_net opt_prod_net opt_swap_net opt_other_net "
         "d_opt_mm_net d_opt_prod_net opt_mm_z52 opt_prod_z52 opt_swap_z52 "
         "opt_other_z52 spec_hedger_gap spec_swap_gap fut_mm_net fut_prod_net").split()
FEATS = BASIC + ["trend_x_opt_mm", "trend_x_opt_prod",
                 "trend_x_spec_hedger_gap", "trend_strength"]
SELLR_THR = 2.3677413378977423
OLD_V5 = AX / "GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
OLD_OPAL = AX / "GOLD_H3_CLEAN_OPAL_PREDICTIONS_2026-10-03.csv"
OUT = AX / "GOLD_R64_EXACT_SKLEARN_WEEKDAY_COT_HELIOS_DPTC_191.csv"
SUMMARY = AX / "GOLD_R64_EXACT_SKLEARN_WEEKDAY_COT_HELIOS_DPTC_SUMMARY.json"


def affirmative(x: object) -> bool:
    return str(x).strip().lower() in {"true", "yes", "1"}


def model() -> Pipeline:
    return Pipeline([
        ("scale", StandardScaler()),
        ("logreg", LogisticRegression(
            C=1.0, solver="lbfgs", max_iter=3000,
            class_weight="balanced", random_state=20261003
        )),
    ])


def retrain() -> tuple[pd.DataFrame, dict]:
    p = pd.read_csv(AX / "GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_OPAL_PANEL.csv")
    clk = pd.read_csv(AX / "GOLD_R60_20261012_H3_ALL_WEEKDAYS_SOURCE_COT_RELEASE_CLOCK_1029.csv")
    cot = pd.read_csv(AX / "GOLD_COT_GOLD_PIT_STATE_RAW_REBUILT_2026-10-06.csv")
    ref = pd.read_csv(OLD_OPAL)
    assert len(p) == len(clk) == 1029
    assert len(ref) == 931
    for col in ("feature_cutoff_date", "forecast_issue_date", "target_end_date_h3"):
        p[col] = pd.to_datetime(p[col], errors="raise")
    for col in BASIC:
        cot[col] = pd.to_numeric(cot[col], errors="coerce")
    cot = cot.dropna(subset=BASIC).set_index("report_date")
    assert not cot.index.duplicated().any()

    clk["forecast_issue_date"] = pd.to_datetime(clk.issue_date, errors="raise")
    joined = p.merge(
        clk[["forecast_issue_date", "corrected_release_COT_report",
             "COT_report_release_utc", "COT_report_release_TR"]],
        on="forecast_issue_date", how="inner", validate="one_to_one")
    assert len(joined) == 1029
    xnew = joined.copy()
    for col in BASIC:
        xnew[col] = xnew.corrected_release_COT_report.map(cot[col])
        assert xnew[col].notna().all(), col
    sign = np.where(xnew.momentum_up.astype(int) == 1, 1.0, -1.0)
    xnew["trend_x_opt_mm"] = sign * xnew.opt_mm_net
    xnew["trend_x_opt_prod"] = sign * xnew.opt_prod_net
    xnew["trend_x_spec_hedger_gap"] = sign * xnew.spec_hedger_gap
    assert all(pd.to_numeric(p[x], errors="coerce").notna().all() for x in FEATS)

    issued_utc = pd.to_datetime(xnew.forecast_issue_date.dt.strftime("%Y-%m-%d") +
                                " 12:00:00", utc=True)
    release_utc = pd.to_datetime(xnew.COT_report_release_utc, utc=True)
    assert (release_utc <= issued_utc).all()
    ref["forecast_issue_date"] = pd.to_datetime(ref.forecast_issue_date)
    ref = ref.set_index("forecast_issue_date")
    p["month_key"] = p.forecast_issue_date.dt.strftime("%Y-%m")
    xnew["month_key"] = xnew.forecast_issue_date.dt.strftime("%Y-%m")
    orig_probdiff = []
    rowout = []
    for mon in sorted(xnew.loc[xnew.forecast_issue_date >= "2022-11-01", "month_key"].unique()):
        te = xnew[xnew.month_key.eq(mon)].copy()
        first = te.feature_cutoff_date.min()
        first_issue = te.forecast_issue_date.min()
        eligible = (p.target_end_date_h3 <= first) & (p.forecast_issue_date < first_issue)
        eligible_new = (xnew.target_end_date_h3 <= first) & (xnew.forecast_issue_date < first_issue)
        orig_train = p.loc[eligible]
        new_train = xnew.loc[eligible_new]
        if len(orig_train) < 80:
            continue
        assert len(orig_train) == len(new_train)
        assert orig_train.reversal_target.nunique() == 2
        original = model().fit(orig_train[FEATS].to_numpy(float),
                               orig_train.reversal_target.to_numpy(int))
        original_te = p[p.month_key.eq(mon)]
        p0 = original.predict_proba(original_te[FEATS].to_numpy(float))[:, 1]
        orig_ref = ref.loc[original_te.forecast_issue_date, "p_reversal"].to_numpy(float)
        orig_probdiff.append(float(np.max(np.abs(p0 - orig_ref))))
        challenger = model().fit(new_train[FEATS].to_numpy(float),
                                 new_train.reversal_target.to_numpy(int))
        prob = challenger.predict_proba(te[FEATS].to_numpy(float))[:, 1]
        for r, value in zip(te.itertuples(index=False), prob):
            follow = affirmative(r.aurora_follows_momentum)
            flip = bool(follow and value >= .70)
            p_opal = (1 - value if int(r.momentum_up) == 1 else value) if flip else float(r.p_aurora)
            rowout.append({
                "forecast_issue_date": r.forecast_issue_date,
                "p_reversal": float(value), "override": flip,
                "p_opal": float(p_opal),
                "cot_report_date": r.corrected_release_COT_report,
                "cot_available_date": pd.Timestamp(r.COT_report_release_TR[:10]).strftime("%Y-%m-%d"),
                "train_n": int(len(new_train)),
            })

    result = pd.DataFrame(rowout).sort_values("forecast_issue_date")
    assert len(result) == 931
    reference = ref.loc[result.forecast_issue_date]
    p0err = max(orig_probdiff)
    # A strict, independent numerical gate; sklearn should reproduce the original
    # well below this bound on a compatible dependency version.
    if p0err > 0.008:
        raise RuntimeError(f"BASELINE_SKLEARN_REPRODUCTION_FAIL {p0err:.8g}")
    # Do not claim original frozen accuracy unless the actual scipy/sklearn
    # implementation matches all old ORIGINAL threshold choices.
    return result, {"n": 931, "original_sklearn_probability_max_abs_diff": p0err}


def simulate_helios(challenger: pd.DataFrame, tmp: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    paths = {
        "AURORA": AX / "GOLD_H3_CLEAN_AURORA_PREDICTIONS_2026-10-03.csv",
        "RIFT": AX / "GOLD_H3_CLEAN_RIFT_PREDICTIONS_2026-10-03.csv",
        "TURN": AX / "GOLD_H3_CLEAN_TURN_PREDICTIONS_2026-10-03.csv",
        "VEGA": AX / "GOLD_H3_CLEAN_VEGA_PREDICTIONS_2026-10-03.csv",
    }
    for k, v in paths.items():
        setattr(h1, k, v)

    def chain(opal_file: Path, stem: str) -> pd.DataFrame:
        h1.OPAL = opal_file
        g1, _ = h1.build_ledger()
        v1file = tmp / f"{stem}_v1.csv"
        g1.to_csv(v1file, index=False)
        h2.V1 = v1file
        g2 = h2.build_v2()
        v2file = tmp / f"{stem}_v2.csv"
        g2.to_csv(v2file, index=False)
        h3.H1, h3.H2, h3.OPAL = v1file, v2file, opal_file
        g3 = h3.simulate_market(h3.load_base())
        g4, _ = h4.simulate_rge(g3)
        return h5.apply_dce(g4)

    old = chain(OLD_OPAL, "frozen")
    original_stored = pd.read_csv(OLD_V5)
    assert len(old) == len(original_stored) == 931
    p_diff = float(np.max(np.abs(old.p_helios_v5_dce.to_numpy(float) -
                                 original_stored.p_helios_v5_dce.to_numpy(float))))
    if p_diff > 1e-10:
        raise RuntimeError(f"OLD_HELIOS_931_PARITY_FAIL {p_diff:.8g}")
    modified = pd.read_csv(OLD_OPAL)
    modified["forecast_issue_date"] = pd.to_datetime(modified.forecast_issue_date)
    q = challenger.set_index("forecast_issue_date")
    assert len(modified) == 931 and len(q) == 931
    for field in ("p_reversal", "override", "p_opal", "cot_report_date", "cot_available_date"):
        modified[field] = modified.forecast_issue_date.map(q[field])
    assert modified.p_reversal.notna().all()
    opalfile = tmp / "COT_OFFICIAL_RELEASE_OPAL_NEW.csv"
    modified.to_csv(opalfile, index=False)
    new = chain(opalfile, "challenger")
    return old, new


def replay_dptc(old: pd.DataFrame, new: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    r = pd.read_csv(AX / "GOLD_R57_20261012_FRIDAY_COT_V5_FROZEN_SAGE_RF_ALARM_COHORT_Q95_191_SENSITIVITY.csv")
    i = pd.read_csv(AX / "GOLD_H3_SAGE_V1_IFBC_SNAPSHOT_2026-10-04.csv").set_index("feature_cutoff_date")
    l = pd.read_csv(AX / "GOLD_H3_SAGE_V1_LLRS_SNAPSHOT_2026-10-04.csv").set_index("feature_cutoff_date")
    rf = pd.read_csv(AX / "GOLD_H3_RULEFLOW_V3_TOPOLOGY_DIAGNOSTIC_2026-10-04.csv")
    rf_dates = set(rf.loc[rf.v3_candidate.map(affirmative), "date"])
    s = pd.read_csv(AX / "GOLD_H3_COMPETENCE_TRANSITION_V1_SELLR_SCORES_SOURCE_2026-10-05.csv")
    score = s.set_index("feature_cutoff_date")
    ph = pd.read_csv(AX / "GOLD_H3_DEPENDENCE_PHASE_SHIFT_V1_PANEL_2026-10-05.csv").set_index("feature_cutoff_date")
    alarm, _ = alarm_source.build_scores()
    alarm["internal_now"] = alarm[["fragility_score", "flow_score"]].max(axis=1)
    alarm["internal_lag1"] = alarm[["fragility_score_lag1", "flow_score_lag1"]].max(axis=1)
    alarm["internal_d1"] = alarm.internal_now - alarm.internal_lag1
    signal = alarm.set_index(alarm.feature_cutoff_date.dt.strftime("%Y-%m-%d"))
    prior_h = old.set_index(old.forecast_issue_date.dt.strftime("%Y-%m-%d"))
    after_h = new.set_index(new.forecast_issue_date.dt.strftime("%Y-%m-%d"))
    def votes(h):
        return (pd.to_numeric(h.p_helios_v5_dce) >= .5).astype(int)
    data = []
    for row in r.itertuples(index=False):
        h0 = prior_h.loc[row.issue]
        h1new = after_h.loc[row.issue]
        v0, v1new, mom = int(votes(h0)), int(votes(h1new)), int(row.mom)
        f = i.loc[row.day] if row.day in i.index else None
        z = l.loc[row.day] if row.day in l.index else None
        ifbc = f is not None and float(f.ifbc_count60) >= 4 and float(f.ifbc_score) >= .70
        llrs = z is not None and affirmative(z.llrs_external_opposes) and float(z.llrs_incremental) > 0 and float(z.llrs_pressure) >= .10
        gate_sg = ifbc and llrs
        sg0, sg1 = gate_sg and v0 == mom, gate_sg and v1new == mom
        rf0, rf1 = (row.day in rf_dates and v0 == mom), (row.day in rf_dates and v1new == mom)
        b0, b1 = v0 ^ (sg0 or rf0), v1new ^ (sg1 or rf1)
        assert b0 == int(row.oldBase) and v0 == int(row.oldV5), row.day
        a = signal.loc[row.day]
        eligible = (pd.notna(a.leadlag_score_premax) and a.leadlag_score_premax >= .60
                    and pd.notna(a.internal_now) and a.internal_now >= .60
                    and pd.notna(a.internal_d1) and a.internal_d1 >= 0)
        data.append({
            "day": row.day, "issue": row.issue, "target": row.target,
            "y": int(row.y), "mom": mom, "oldBase": b0, "newBase": b1,
            "old_alarm": bool(eligible and b0 == mom),
            "new_alarm": bool(eligible and b1 == mom),
            "phase": affirmative(ph.loc[row.day, "dependence_phase"]),
            "sellr": float(score.loc[row.day, "sellr_score"]),
            "originalQ95": int(row.originalQ95),
        })
    a = pd.DataFrame(data).sort_values("day").reset_index(drop=True)
    def machine(prefix):
        trust = False
        broken = 0
        pending = []
        act = []
        final = []
        modes = []
        for row in a.itertuples(index=False):
            matured = sorted([p for p in pending if p["target"] <= row.day],
                             key=lambda p: (p["target"], p["day"]))
            pending = [p for p in pending if p["target"] > row.day]
            for p in matured:
                if p["acted"] and trust:
                    if p["competence"]: broken = 0
                    else:
                        broken += 1
                        if broken >= 2: trust, broken = False, 0
            base = int(getattr(row, prefix + "Base"))
            is_alarm = bool(getattr(row, prefix + "_alarm"))
            catalyst = is_alarm and np.isfinite(row.sellr) and row.sellr >= SELLR_THR
            if not trust and catalyst: trust, broken = True, 0
            mode = "NO_ALARM" if not is_alarm else "TRUST" if trust else "PHASE" if row.phase else "KEEP"
            acted = mode in ("TRUST", "PHASE")
            modes.append(mode)
            act.append(acted)
            final.append(base ^ acted)
            if is_alarm:
                pending.append({"day": row.day, "target": row.target,
                                "acted": acted, "competence": int(base != row.y)})
        a[prefix + "_mode"] = modes
        a[prefix + "_action"] = act
        a[prefix + "_final"] = final
    machine("old")
    machine("new")
    assert len(a) == 191
    assert int(a.old_alarm.sum()) == 28
    assert int(a.old_action.sum()) == 13
    assert (a.old_final.astype(int) == a.originalQ95.astype(int)).all()
    assert int((a.old_final == a.y).sum()) == 135
    return a, {
        "old_191_row_dptc_parity": True,
        "old_correct": 135,
        "new_correct": int((a.new_final == a.y).sum()),
        "new_alarms": int(a.new_alarm.sum()),
        "new_actions": int(a.new_action.sum()),
    }


def main() -> None:
    challenger, opal_gate = retrain()
    with tempfile.TemporaryDirectory(prefix="gold_h3_r64_") as td:
        old, new = simulate_helios(challenger, Path(td))
        a, res = replay_dptc(old, new)
    a.to_csv(OUT, index=False)
    out = {"status": "EXACT_PYTHON_SKLEARN_CONTROLLED_H3_REPLAY",
           "original_opal_gate": opal_gate,
           "old_helios_parity_931": True,
           "new_HELIOS_2025": int(((new.year == 2025) &
                 ((new.p_helios_v5_dce >= .5).astype(int) == new.y_up.astype(int))).sum()),
           "new_HELIOS_2026": int(((new.year == 2026) &
                 ((new.p_helios_v5_dce >= .5).astype(int) == new.y_up.astype(int))).sum()),
           "DPTC": res,
           "held_fixed": "External IFBC/LLRS RuleFlow regime inputs, DEPENDENCE_PHASE, SELLR raw score",
           "not_prospective": True}
    SUMMARY.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
