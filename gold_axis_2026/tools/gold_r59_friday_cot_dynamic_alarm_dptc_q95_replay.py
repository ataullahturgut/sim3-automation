#!/usr/bin/env python3
"""R59: independent H3 Friday-COT dynamic Handoff -> DPTC-Q95 replay.

Nonbinding controlled counterfactual. Preserve frozen source features, frozen
2025 SELLR threshold, label-free dependence phase, and R57 external SAGE /
RuleFlow recombination. Rebuild *all* alarm eligibility and trust chronologically.
DO NOT substitute the old alarm cohort. OPAL numerical challenger in R56 is
approximate and upstream external experts are not retrained here.

Run from repository root:
  python gold_axis_2026/tools/gold_r59_friday_cot_dynamic_alarm_dptc_q95_replay.py
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import pandas as pd

AX = Path(__file__).resolve().parents[1]
R57 = AX / "GOLD_R57_20261012_FRIDAY_COT_V5_FROZEN_SAGE_RF_ALARM_COHORT_Q95_191_SENSITIVITY.csv"
R56 = AX / "GOLD_R56_20261012_H3_FRIDAY_COT_DYNAMIC_HELIOS_V1_V5_931ROW_REPLAY.csv"
TL = AX / "GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V1_TIMELINE_2026-10-04.csv"
PH = AX / "GOLD_H3_DEPENDENCE_PHASE_SHIFT_V1_PANEL_2026-10-05.csv"
SELLR = AX / "GOLD_H3_COMPETENCE_TRANSITION_V1_SELLR_SCORES_SOURCE_2026-10-05.csv"
OLD_ACT = AX / "GOLD_H3_DPTC_V1_ACTIONS_2026-10-05.csv"
OUT_CSV = AX / "GOLD_R59_20261012_FRIDAY_COT_DYNAMIC_ALARM_DPTC_Q95_191_REPLAY.csv"
OUT_JSON = AX / "GOLD_R59_20261012_FRIDAY_COT_DYNAMIC_ALARM_DPTC_Q95_SUMMARY.json"
THR = 2.3677413378977423


def truth(x: object) -> bool:
    return str(x).strip().lower() in ("true", "1", "yes")


def build_scores() -> pd.DataFrame:
    source = AX / "tools/gold_h3_remaining53_signal_audit.py"
    spec = importlib.util.spec_from_file_location("r59_audit_scores", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load canonical Handoff score code")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    scores, _ = mod.build_scores()
    scores = scores.sort_values("feature_cutoff_date").reset_index(drop=True)
    # Pandas max(skipna=True) returns NaN if both lag features are absent.
    # This is critical: treating missing lag as -Infinity creates four false
    # positive 2026 alarm candidates (02-17, 03-11, 04-24, 07-06).
    scores["internal_now"] = scores[["fragility_score", "flow_score"]].max(axis=1)
    scores["internal_lag1"] = scores[["fragility_score_lag1", "flow_score_lag1"]].max(axis=1)
    scores["internal_d1"] = scores.internal_now - scores.internal_lag1
    return scores[["feature_cutoff_date", "leadlag_score_premax", "internal_now", "internal_d1"]]


def decision_simulation(rows: pd.DataFrame, prefix: str) -> tuple[pd.DataFrame, list[dict]]:
    trust = False
    consecutive_broken = 0
    pending: list[dict] = []
    decisions: list[dict] = []
    for r in rows.loc[rows[f"{prefix}_alarm"]].sort_values("day").itertuples(index=False):
        now = r.day
        # Use complete original and new target maturities from R57; the old
        # DPTC action export had a known NaT target-date serialization bug.
        matured = sorted((x for x in pending if x["target"] <= now),
                         key=lambda x: (x["target"], x["day"]))
        pending = [x for x in pending if x["target"] > now]
        for x in matured:
            if x["acted"] and trust:
                if x["competence_y"]:
                    consecutive_broken = 0
                else:
                    consecutive_broken += 1
                    if consecutive_broken >= 2:
                        trust = False
                        consecutive_broken = 0
        base = int(getattr(r, f"{prefix}Base"))
        actual = int(r.y)
        phase = truth(r.dependence_phase)
        fire = bool(pd.notna(r.sellr_score) and
                    float(r.sellr_score) >= THR and base == int(r.mom))
        if not trust and fire:
            trust = True
            consecutive_broken = 0
        mode = "TRUST" if trust else ("PHASE" if phase else "KEEP")
        acted = mode != "KEEP"
        record = {
            "day": now, "issue": r.issue, "target": r.target,
            "mode": mode, "acted": acted, "phase": phase, "sellr_fire": fire,
            "baseline_correct": base == actual,
            "competence_y": int(base != actual),
        }
        decisions.append(record)
        pending.append({
            "day": now, "target": r.target, "acted": acted,
            "competence_y": int(base != actual),
        })
    return pd.DataFrame(decisions), [x for x in decisions if x["acted"]]


def main() -> None:
    a = pd.read_csv(R57)
    assert len(a) == 191 and not a.day.duplicated().any()
    for col in ("day", "issue", "target"):
        a[col] = pd.to_datetime(a[col], errors="raise")
    a = a.sort_values("day").reset_index(drop=True)

    r56 = pd.read_csv(R56)
    r56["issue_date"] = pd.to_datetime(r56.issue_date)
    r56 = r56[["issue_date", "original_COT_report", "friday_COT_report",
               "new_pred_up", "old_pred_up"]]
    a = a.merge(r56, left_on="issue", right_on="issue_date", how="left", validate="one_to_one")
    assert a.new_pred_up.notna().all()
    assert (a.new_pred_up.astype(int) == a.newV5.astype(int)).all()
    assert (a.old_pred_up.astype(int) == a.oldV5.astype(int)).all()

    score = build_scores().rename(columns={"feature_cutoff_date": "day"})
    phase = pd.read_csv(PH)[["feature_cutoff_date", "dependence_phase"]]
    sellr = pd.read_csv(SELLR)[["feature_cutoff_date", "sellr_score"]]
    for f in (phase, sellr):
        f["feature_cutoff_date"] = pd.to_datetime(f.feature_cutoff_date)
    a = a.merge(score, on="day", how="left", validate="one_to_one")
    a = a.merge(phase, left_on="day", right_on="feature_cutoff_date",
                how="left", validate="one_to_one").drop(columns="feature_cutoff_date")
    a = a.merge(sellr, left_on="day", right_on="feature_cutoff_date",
                how="left", validate="one_to_one").drop(columns="feature_cutoff_date")

    gate = ((a.leadlag_score_premax >= 0.60)
            & (a.internal_now >= 0.60)
            & (a.internal_d1 >= 0))
    a["old_alarm"] = gate & (a.oldBase.astype(int) == a.mom.astype(int))
    a["new_alarm"] = gate & (a.newBase.astype(int) == a.mom.astype(int))

    original_tl = pd.read_csv(TL)
    original_tl = original_tl[original_tl.period == "2026_STRESS"]
    original_dates = set(pd.to_datetime(original_tl.feature_cutoff_date))
    old_dates = set(a.loc[a.old_alarm, "day"])
    assert len(original_dates) == len(old_dates) == 28 and old_dates == original_dates, (
        "FROZEN_HANDOFF_28_ALARM_PARITY_FAIL")
    assert int(a.new_alarm.sum()) == 22

    old_tl, old_act = decision_simulation(a, "old")
    new_tl, new_act = decision_simulation(a, "new")
    expected = pd.read_csv(OLD_ACT)
    expected = set(pd.to_datetime(expected.loc[expected.variant == "Q95", "feature_cutoff_date"]))
    assert len(old_act) == len(expected) == 13
    assert set(x["day"] for x in old_act) == expected, "DPTC_13_ACTION_PARITY_FAIL"

    for prefix, timeline in (("old", old_tl), ("new", new_tl)):
        modes = timeline.set_index("day")["mode"]
        a[f"{prefix}_mode"] = a.day.map(modes).fillna("NO_ALARM")
        a[f"{prefix}_act"] = a[f"{prefix}_mode"].isin(("TRUST", "PHASE"))
        a[f"{prefix}_final"] = (
            a[f"{prefix}Base"].astype(int) ^ a[f"{prefix}_act"].astype(int))
        a[f"{prefix}_correct"] = a[f"{prefix}_final"] == a.y.astype(int)

    old_base = int((a.oldBase == a.y).sum())
    new_base = int((a.newBase == a.y).sum())
    old_final = int(a.old_correct.sum())
    new_final = int(a.new_correct.sum())
    assert (old_base, new_base, old_final, new_final) == (126, 124, 135, 129)
    assert int((a.originalQ95 == a.y).sum()) == old_final
    assert (a.old_final == a.originalQ95).all(), "FROZEN_Q95_191_ROW_PARITY_FAIL"

    monthly = {}
    for month, g in a.groupby(a.issue.dt.strftime("%Y-%m")):
        monthly[month] = {
            "n": len(g), "old_correct": int(g.old_correct.sum()),
            "new_correct": int(g.new_correct.sum()),
            "old_acts": int(g.old_act.sum()), "new_acts": int(g.new_act.sum())
        }
    assert monthly["2026-05"]["old_correct"] == 17
    assert monthly["2026-05"]["new_correct"] == 17

    summary = {
        "status": "CONTROLLED_DYNAMIC_HANDOFF_DPTC_Q95_REPLAY_NONBINDING",
        "parity": {
            "old_handoff_alarms": 28, "old_dptc_actions": 13,
            "frozen_old_191_predictions": "EXACT_191_OF_191",
            "old_baseline_correct": old_base, "old_dptc_correct": old_final
        },
        "friday_cot": {
            "new_handoff_alarms": int(a.new_alarm.sum()),
            "new_dptc_actions": len(new_act),
            "new_baseline_correct": new_base, "new_dptc_correct": new_final,
            "new_correct_rate": new_final / len(a),
        },
        "reproduction_contract": {
            "month_issue_window": "2026 Jan-Sep 191 issues",
            "target": "unchanged H3 D0 to third retained source-day D3",
            "release": "Friday 15:30 America/New_York incl CFTC specials",
            "issue_time_assumption": "15:00 Europe/Istanbul",
            "frozen_external": "IFBC LLRS RuleFlow, dependence phase, SELLR score and threshold",
            "dynamic": "old and new candidate alarm eligibility, sellr-fire, phase entry, pending target maturity, trust hysteresis",
            "limitation": "R56 OPAL IRLS approximation, not exact sklearn refit; original external expert source freezes and SELLR raw score not re-trained; posthoc target and PIT caveats",
        },
        "old_action_dates": [x["day"].strftime("%Y-%m-%d") for x in old_act],
        "new_action_dates": [x["day"].strftime("%Y-%m-%d") for x in new_act],
        "monthly": monthly,
    }
    cols = ["day", "issue", "target", "original_COT_report", "friday_COT_report",
            "y", "mom", "oldV5", "newV5", "oldBase", "newBase",
            "leadlag_score_premax", "internal_now", "internal_d1",
            "dependence_phase", "sellr_score",
            "old_alarm", "new_alarm", "old_mode", "new_mode",
            "old_act", "new_act", "old_final", "new_final",
            "old_correct", "new_correct", "originalQ95"]
    a[cols].to_csv(OUT_CSV, index=False)
    OUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
