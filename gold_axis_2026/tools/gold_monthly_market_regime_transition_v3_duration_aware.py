from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

import gold_monthly_market_regime_discovery_v1 as base
import gold_monthly_market_regime_prototype_alignment_v1 as palign

CAL_START = "2015-07"
CAL_END = "2021-12"
VAL_START = "2022-01"
VAL_END = "2024-12"
TRANSPORT_START = "2025-01"
END = "2026-08"
CONFIDENCE = 0.60
FEATURES = list(base.FEATURES)
R_STATES = ["R0", "R1", "R2"]

GRID = {
    "age_pct_thr": [0.60, 0.75, 0.85, 0.95],
    "hazard_thr": [0.15, 0.25, 0.35, 0.45],
    "alt_prob_thr": [0.20, 0.30, 0.40],
    "alt_growth_thr": [0.05, 0.10, 0.15],
    "drop_thr": [0.10, 0.15, 0.20],
    "moderate_persistence": [1, 2],
    "strong_alt_prob_thr": [0.50, 0.60, 0.70],
    "strong_margin_thr": [0.00, 0.10],
    "strong_growth_thr": [0.15, 0.25],
    "strong_drop_thr": [0.20, 0.30],
}


def load_json(path: str):
    return json.loads(Path(path).read_text())


def next_month(month: str) -> str:
    return str(pd.Period(month, freq="M") + 1)


def month_diff(first: str, confirmation: str) -> int:
    return int(pd.Period(confirmation, freq="M").ordinal - pd.Period(first, freq="M").ordinal)


def semantic_posts(raw_posts: np.ndarray, mapping: dict[int, int]) -> np.ndarray:
    out = np.zeros_like(raw_posts)
    for raw_state, sem_state in mapping.items():
        out[:, sem_state] = raw_posts[:, raw_state]
    return out


def spell_decompose(states: np.ndarray):
    if len(states) == 0:
        return []
    spells = []
    start = 0
    cur = int(states[0])
    for i in range(1, len(states)):
        s = int(states[i])
        if s != cur:
            spells.append({"state": cur, "start": start, "end": i - 1, "length": i - start})
            start = i
            cur = s
    spells.append({"state": cur, "start": start, "end": len(states) - 1, "length": len(states) - start})
    return spells


def duration_stats(sem_hard_history: np.ndarray, incumbent: int):
    spells = spell_decompose(sem_hard_history)
    if not spells:
        return {
            "spell_age": None,
            "completed_spell_pool_size": 0,
            "completed_spell_lengths": [],
            "age_percentile": None,
            "smoothed_exit_hazard": None,
        }

    current = spells[-1]
    if int(current["state"]) != int(incumbent):
        raise RuntimeError(("INCUMBENT_SPELL_MISMATCH", incumbent, current))

    age = int(current["length"])
    completed = [int(s["length"]) for s in spells[:-1] if int(s["state"]) == int(incumbent)]
    n = len(completed)

    if n == 0:
        age_pct = None
        hazard = None
    else:
        arr = np.asarray(completed, int)
        age_pct = float(np.mean(arr <= age))
        risk = int(np.sum(arr >= age))
        exits = int(np.sum(arr == age))
        if risk == 0:
            hazard = 1.0
            age_pct = 1.0
        else:
            hazard = float((exits + 0.5) / (risk + 1.0))

    return {
        "spell_age": age,
        "completed_spell_pool_size": n,
        "completed_spell_lengths": completed,
        "age_percentile": age_pct,
        "smoothed_exit_hazard": hazard,
    }


def score_sequence_features(fit, train: pd.DataFrame, future: pd.DataFrame):
    z_future = fit["scaler"].transform(future[FEATURES].to_numpy(float))
    x_future = fit["pca"].transform(z_future)
    x_all = np.vstack([fit["x_train"], x_future])

    posts, _ = base.forward_filter(fit["model"], x_all)
    sem = semantic_posts(posts, fit["prototype_mapping"])
    sem_hard = sem.argmax(axis=1)
    ntrain = len(train)

    out = []
    for j, month in enumerate(future.index):
        i = ntrain + j
        prev_i = i - 1

        incumbent = int(sem_hard[prev_i])
        hist_states = sem_hard[: prev_i + 1]
        ds = duration_stats(hist_states, incumbent)

        alt_idx = [s for s in range(3) if s != incumbent]
        p_inc_prev = float(sem[prev_i, incumbent])
        p_inc_cur = float(sem[i, incumbent])
        alt_prev = float(np.max(sem[prev_i, alt_idx]))
        alt_cur = float(np.max(sem[i, alt_idx]))

        cur_best = int(np.argmax(sem[i]))
        cur_best_prob = float(sem[i, cur_best])
        sem_state = f"R{cur_best}"
        sem_label = sem_state if cur_best_prob >= CONFIDENCE else "BELIRSIZ"

        row = {
            "month": str(month),
            "semantic_state": sem_state,
            "semantic_label": sem_label,
            "semantic_probability": cur_best_prob,
            "incumbent_semantic_state": f"R{incumbent}",
            "incumbent_semantic_state_id": incumbent,
            "incumbent_posterior_prev": p_inc_prev,
            "incumbent_posterior_cur": p_inc_cur,
            "incumbent_drop": float(p_inc_prev - p_inc_cur),
            "alternative_posterior_prev": alt_prev,
            "alternative_posterior_cur": alt_cur,
            "alternative_growth": float(alt_cur - alt_prev),
            "incumbent_vs_alternative_margin_cur": float(p_inc_cur - alt_cur),
            **ds,
            "train_start": fit["train_start"],
            "train_end": fit["train_end"],
            "train_rows": fit["train_rows"],
            "hmm_seed": fit["seed"],
            "prototype_assignment": fit["prototype_detail"]["assignment"],
        }
        out.append(row)

    return out


def expanding_rows(panel: pd.DataFrame, months: list[str], proto):
    rows = []
    for month in months:
        train = panel.loc[panel.index < month].copy()
        cur = panel.loc[[month]].copy()
        fit = palign.fit_frozen(train, proto)
        row = score_sequence_features(fit, train, cur)[0]
        row["detector"] = "EXPANDING_REFIT"
        rows.append(row)
    return rows


def annual_rows(panel: pd.DataFrame, months: list[str], proto):
    by_year = {}
    for m in months:
        by_year.setdefault(int(m[:4]), []).append(m)

    rows = []
    for year in sorted(by_year):
        if year == 2015:
            anchor_end = "2015-06"
            future_start = "2015-07"
        else:
            anchor_end = f"{year-1}-12"
            future_start = f"{year}-01"

        train = panel.loc[panel.index <= anchor_end].copy()
        year_months = [m for m in panel.index if future_start <= m <= min(f"{year}-12", END)]
        future = panel.loc[year_months].copy()
        fit = palign.fit_frozen(train, proto)
        scored = score_sequence_features(fit, train, future)
        wanted = set(by_year[year])

        for row in scored:
            if row["month"] in wanted:
                row["detector"] = "ANNUAL_ANCHORED"
                row["anchor_end"] = anchor_end
                rows.append(row)

    rows.sort(key=lambda r: r["month"])
    return rows


def attach_reference(rows, ref):
    out = []
    for r in rows:
        rr = ref.loc[r["month"]]
        p = float(rr["state_probability"])
        s = str(rr["state"])
        z = dict(r)
        z.update({
            "reference_state": s,
            "reference_probability": p,
            "reference_label": s if p >= CONFIDENCE else "BELIRSIZ",
            "reference_ood": bool(rr["ood_below_train_p05"]),
        })
        out.append(z)
    return out


def build_reference_events(ref_monthly: pd.DataFrame):
    seq = []
    for _, rr in ref_monthly.iterrows():
        p = float(rr["state_probability"])
        seq.append({
            "month": str(rr["month"]),
            "label": str(rr["state"]) if p >= CONFIDENCE else "BELIRSIZ",
        })

    events = []
    last_state = None
    last_month = None

    for r in seq:
        if r["label"] not in R_STATES:
            continue
        if last_state is None:
            last_state = r["label"]
            last_month = r["month"]
            continue
        if r["label"] != last_state:
            zs = next_month(last_month)
            conf = r["month"]
            events.append({
                "old_state": last_state,
                "new_state": r["label"],
                "last_confident_old_month": last_month,
                "zone_start": zs,
                "confirmation_month": conf,
                "zone_months": [str(p) for p in pd.period_range(zs, conf, freq="M")],
            })
            last_state = r["label"]
        last_month = r["month"]

    return events


def moderate_condition(row, p):
    n = int(row["completed_spell_pool_size"])
    age_pct = row["age_percentile"]
    hazard = row["smoothed_exit_hazard"]
    if n < 3 or age_pct is None or hazard is None:
        return False

    directional = (
        float(row["alternative_growth"]) >= p["alt_growth_thr"]
        or float(row["incumbent_drop"]) >= p["drop_thr"]
    )
    return bool(
        age_pct >= p["age_pct_thr"]
        and hazard >= p["hazard_thr"]
        and float(row["alternative_posterior_cur"]) >= p["alt_prob_thr"]
        and directional
    )


def strong_condition(row, p):
    directional = (
        float(row["alternative_growth"]) >= p["strong_growth_thr"]
        or float(row["incumbent_drop"]) >= p["strong_drop_thr"]
    )
    return bool(
        float(row["alternative_posterior_cur"]) >= p["strong_alt_prob_thr"]
        and float(row["incumbent_vs_alternative_margin_cur"]) <= p["strong_margin_thr"]
        and directional
    )


def apply_rule(rows, p):
    out = []
    prev_mod = False
    prev_month = None

    for r in rows:
        moderate_raw = moderate_condition(r, p)
        strong = strong_condition(r, p)

        consecutive = (
            prev_month is not None
            and pd.Period(r["month"], freq="M").ordinal == pd.Period(prev_month, freq="M").ordinal + 1
        )

        if p["moderate_persistence"] == 1:
            moderate_persisted = moderate_raw
        else:
            moderate_persisted = bool(moderate_raw and consecutive and prev_mod)

        flag = bool(strong or moderate_persisted)

        z = dict(r)
        z.update({
            "moderate_condition_raw": moderate_raw,
            "moderate_persisted": moderate_persisted,
            "strong_break": strong,
            "transition_flag": flag,
            "transition_status": "TRANSITION" if flag else "STABLE",
            "branch": (
                "STRONG+MODERATE" if strong and moderate_persisted
                else "STRONG" if strong
                else "MODERATE" if moderate_persisted
                else "NONE"
            ),
        })
        out.append(z)

        prev_mod = moderate_raw
        prev_month = r["month"]

    return out


def slice_rows(rows, start, end):
    return [r for r in rows if start <= r["month"] <= end]


def period_metrics(rows, events, start, end):
    rr = slice_rows(rows, start, end)
    months = {r["month"] for r in rr}
    evs = [e for e in events if start <= e["confirmation_month"] <= end]

    zone = set()
    for e in evs:
        zone.update(m for m in e["zone_months"] if m in months)

    zone_rows = [r for r in rr if r["month"] in zone]
    nonzone = [r for r in rr if r["month"] not in zone]
    flags = [r for r in rr if r["transition_flag"]]

    tp = int(sum(r["transition_flag"] for r in zone_rows))
    fp = int(sum(r["transition_flag"] for r in nonzone))

    details = []
    leads = []
    hits = 0
    for e in evs:
        zset = set(e["zone_months"])
        flagged = [r for r in rr if r["month"] in zset and r["transition_flag"]]
        first = flagged[0]["month"] if flagged else None
        lead = None if first is None else month_diff(first, e["confirmation_month"])
        if first is not None:
            hits += 1
            leads.append(lead)
        details.append({
            **e,
            "first_detector_flag_in_zone": first,
            "lead_months_before_confirmation": lead,
            "hit": first is not None,
        })

    pool_available = [r for r in rr if int(r["completed_spell_pool_size"]) >= 3]
    flag_ages = [int(r["spell_age"]) for r in flags if r["spell_age"] is not None]
    branches = Counter(r["branch"] for r in flags)

    return {
        "n_months": len(rr),
        "transition_flags": len(flags),
        "flag_rate": None if not rr else float(len(flags) / len(rr)),
        "transition_zone_months": len(zone_rows),
        "transition_zone_hits": tp,
        "transition_zone_recall": None if not zone_rows else float(tp / len(zone_rows)),
        "non_zone_months": len(nonzone),
        "false_transition_count": fp,
        "false_transition_rate_non_zone": None if not nonzone else float(fp / len(nonzone)),
        "precision": None if not flags else float(tp / len(flags)),
        "reference_transition_events": len(evs),
        "event_hits": hits,
        "event_misses": len(evs) - hits,
        "event_hit_rate": None if not evs else float(hits / len(evs)),
        "mean_lead_months_before_confirmation": None if not leads else float(np.mean(leads)),
        "duration_pool_available_months": len(pool_available),
        "duration_pool_available_rate": None if not rr else float(len(pool_available) / len(rr)),
        "flag_spell_age_mean": None if not flag_ages else float(np.mean(flag_ages)),
        "flag_spell_age_median": None if not flag_ages else float(np.median(flag_ages)),
        "flag_branch_counts": dict(branches),
        "event_details": details,
    }


def parameter_tuples():
    keys = [
        "age_pct_thr", "hazard_thr", "alt_prob_thr", "alt_growth_thr", "drop_thr",
        "moderate_persistence", "strong_alt_prob_thr", "strong_margin_thr",
        "strong_growth_thr", "strong_drop_thr",
    ]
    for vals in itertools.product(*(GRID[k] for k in keys)):
        yield dict(zip(keys, vals))


def lex_tuple(p):
    return tuple(p[k] for k in [
        "age_pct_thr", "hazard_thr", "alt_prob_thr", "alt_growth_thr", "drop_thr",
        "moderate_persistence", "strong_alt_prob_thr", "strong_margin_thr",
        "strong_growth_thr", "strong_drop_thr",
    ])


def select_rule(cal_rows, events):
    scored = []
    for p in parameter_tuples():
        applied = apply_rule(cal_rows, p)
        m = period_metrics(applied, events, CAL_START, CAL_END)
        scored.append((p, m))

    eligible = [
        (p, m) for p, m in scored
        if m["false_transition_rate_non_zone"] is not None
        and m["false_transition_rate_non_zone"] <= 0.15
    ]

    fallback = False
    if eligible:
        def key(item):
            p, m = item
            hit = -1.0 if m["event_hit_rate"] is None else m["event_hit_rate"]
            precision = -1.0 if m["precision"] is None else m["precision"]
            zrec = -1.0 if m["transition_zone_recall"] is None else m["transition_zone_recall"]
            lead = -999.0 if m["mean_lead_months_before_confirmation"] is None else m["mean_lead_months_before_confirmation"]
            return (-hit, -precision, -zrec, -lead, m["flag_rate"], lex_tuple(p))
        best = min(eligible, key=key)
    else:
        fallback = True
        def key(item):
            p, m = item
            hit = -1.0 if m["event_hit_rate"] is None else m["event_hit_rate"]
            precision = -1.0 if m["precision"] is None else m["precision"]
            zrec = -1.0 if m["transition_zone_recall"] is None else m["transition_zone_recall"]
            return (
                m["false_transition_rate_non_zone"],
                -hit,
                -precision,
                -zrec,
                lex_tuple(p),
            )
        best = min(scored, key=key)

    pbest, mbest = best
    return {
        "selected_params": pbest,
        "calibration_metrics": mbest,
        "eligible_candidate_count": len(eligible),
        "total_candidate_count": len(scored),
        "fallback_used": fallback,
    }


def verify_against_prior(rows, prior_rows, detector):
    prior = {r["month"]: r for r in prior_rows}
    problems = []
    max_prob = 0.0

    for r in rows:
        p = prior.get(r["month"])
        if p is None:
            problems.append({"month": r["month"], "issue": "missing_prior"})
            continue
        dp = abs(float(r["semantic_probability"]) - float(p["probability"]))
        max_prob = max(max_prob, dp)
        if dp > 1e-6 or r["semantic_state"] != p["prototype_state"] or r["semantic_label"] != p["prototype_label"]:
            problems.append({
                "month": r["month"],
                "probability_abs_diff": dp,
                "state": r["semantic_state"],
                "prior_state": p["prototype_state"],
                "label": r["semantic_label"],
                "prior_label": p["prototype_label"],
            })

    return {
        "detector": detector,
        "pass": len(problems) == 0,
        "n_months": len(rows),
        "max_probability_abs_diff": max_prob,
        "problems": problems,
    }


def checkpoint_table(expanding, annual):
    months = [
        "2024-03", "2024-04", "2024-05", "2024-06",
        "2026-04", "2026-05", "2026-06", "2026-07", "2026-08",
    ]
    out = []
    for m in months:
        row = {"month": m}
        for name, rows in [("EXPANDING_REFIT", expanding), ("ANNUAL_ANCHORED", annual)]:
            r = next((x for x in rows if x["month"] == m), None)
            if r is None:
                continue
            row[name] = {
                "semantic_state": r["semantic_state"],
                "semantic_label": r["semantic_label"],
                "semantic_probability": r["semantic_probability"],
                "transition_status": r["transition_status"],
                "branch": r["branch"],
                "spell_age": r["spell_age"],
                "completed_spell_pool_size": r["completed_spell_pool_size"],
                "age_percentile": r["age_percentile"],
                "smoothed_exit_hazard": r["smoothed_exit_hazard"],
                "incumbent_posterior_prev": r["incumbent_posterior_prev"],
                "incumbent_posterior_cur": r["incumbent_posterior_cur"],
                "incumbent_drop": r["incumbent_drop"],
                "alternative_posterior_cur": r["alternative_posterior_cur"],
                "alternative_growth": r["alternative_growth"],
                "margin_cur": r["incumbent_vs_alternative_margin_cur"],
                "moderate_raw": r["moderate_condition_raw"],
                "moderate_persisted": r["moderate_persisted"],
                "strong_break": r["strong_break"],
            }
            row["reference"] = {
                "state": r["reference_state"],
                "label": r["reference_label"],
                "probability": r["reference_probability"],
            }
        out.append(row)
    return out


def v2_validation_metrics(v2_rows, events):
    rows = [
        {"month": r["month"], "transition_flag": bool(r["transition_flag"])}
        for r in v2_rows
    ]
    return period_metrics(rows, events, VAL_START, VAL_END)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--regime-discovery-json", required=True)
    ap.add_argument("--prototype-alignment-json", required=True)
    ap.add_argument("--transition-v2-json", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    src = load_json(args.regime_discovery_json)
    prior = load_json(args.prototype_alignment_json)
    v2 = load_json(args.transition_v2_json)

    if src.get("status") != "COMPLETE":
        raise RuntimeError("INVALID_DISCOVERY_REFERENCE")
    if prior.get("status") != "COMPLETE":
        raise RuntimeError("INVALID_PROTOTYPE_REFERENCE")
    if v2.get("status") != "COMPLETE":
        raise RuntimeError("INVALID_V2_REFERENCE")

    raw = pd.DataFrame(src["monthly_regimes"]).sort_values("month").reset_index(drop=True)
    proto = palign.build_frozen_prototypes(raw)
    panel = raw[["month"] + FEATURES].copy().set_index("month")
    ref = raw[["month", "state", "state_probability", "ood_below_train_p05"]].copy().set_index("month")
    events = build_reference_events(raw[["month", "state", "state_probability"]])

    # 1) Calibration rows only. No 2022+ V3 rows are computed before rule freeze.
    cal_months = [m for m in panel.index if CAL_START <= m <= CAL_END]
    cal_exp_base = attach_reference(expanding_rows(panel, cal_months, proto), ref)
    selection = select_rule(cal_exp_base, events)
    selected = selection["selected_params"]
    cal_exp = apply_rule(cal_exp_base, selected)

    # 2) Freeze, then later periods.
    later_months = [m for m in panel.index if VAL_START <= m <= END]
    later_exp_base = attach_reference(expanding_rows(panel, later_months, proto), ref)
    later_exp = apply_rule(later_exp_base, selected)
    expanding = cal_exp + later_exp

    all_months = [m for m in panel.index if CAL_START <= m <= END]
    annual_base = attach_reference(annual_rows(panel, all_months, proto), ref)
    annual = apply_rule(annual_base, selected)

    verify_exp = verify_against_prior(expanding, prior["rows"]["EXPANDING_REFIT"], "EXPANDING_REFIT")
    verify_ann = verify_against_prior(annual, prior["rows"]["ANNUAL_ANCHORED"], "ANNUAL_ANCHORED")
    if not verify_exp["pass"] or not verify_ann["pass"]:
        raise RuntimeError(("UNDERLYING_REGIME_REPRODUCTION_FAILED", verify_exp, verify_ann))

    metrics = {
        "calibration_2015_07_2021_12": {
            "EXPANDING_REFIT": period_metrics(expanding, events, CAL_START, CAL_END),
            "ANNUAL_ANCHORED": period_metrics(annual, events, CAL_START, CAL_END),
        },
        "validation_2022_01_2024_12": {
            "EXPANDING_REFIT": period_metrics(expanding, events, VAL_START, VAL_END),
            "ANNUAL_ANCHORED": period_metrics(annual, events, VAL_START, VAL_END),
        },
        "transport_2025_01_2026_08": {
            "EXPANDING_REFIT": period_metrics(expanding, events, TRANSPORT_START, END),
            "ANNUAL_ANCHORED": period_metrics(annual, events, TRANSPORT_START, END),
        },
        "full_replay_2015_07_2026_08": {
            "EXPANDING_REFIT": period_metrics(expanding, events, CAL_START, END),
            "ANNUAL_ANCHORED": period_metrics(annual, events, CAL_START, END),
        },
    }

    v2_val = v2_validation_metrics(v2["rows"]["EXPANDING_REFIT"], events)
    vm = metrics["validation_2022_01_2024_12"]["EXPANDING_REFIT"]

    precision_gate = (
        vm["precision"] is not None
        and v2_val["precision"] is not None
        and vm["precision"] >= v2_val["precision"] + 0.05
    )
    promotion = bool(
        (vm["event_hit_rate"] or 0.0) >= (2.0 / 3.0)
        and (vm["false_transition_rate_non_zone"] if vm["false_transition_rate_non_zone"] is not None else 1.0) <= 0.15
        and precision_gate
    )

    result = {
        "schema": "GOLD_MONTHLY_MARKET_REGIME_TRANSITION_V3_DURATION_AWARE_2026-09-30",
        "status": "COMPLETE",
        "scientific_gate": "PASS",
        "method": "explicit-duration semi-Markov hazard overlay on frozen HMM/prototype regime engine",
        "calibration_freeze": {
            "calibration_period": [CAL_START, CAL_END],
            "primary_schedule": "EXPANDING_REFIT",
            "grid": GRID,
            "selection": selection,
            "rule_frozen_before_2022_plus_rows": True,
        },
        "selected_rule": selected,
        "underlying_regime_reproduction": {
            "EXPANDING_REFIT": verify_exp,
            "ANNUAL_ANCHORED": verify_ann,
        },
        "metrics": metrics,
        "v2_validation_reference": v2_val,
        "promotion_gate": {
            "required_event_hit_rate": 2.0 / 3.0,
            "required_false_transition_rate_max": 0.15,
            "required_precision_vs_v2": "V2 + 0.05",
            "v3_event_hit_rate": vm["event_hit_rate"],
            "v3_false_transition_rate": vm["false_transition_rate_non_zone"],
            "v3_precision": vm["precision"],
            "v2_precision": v2_val["precision"],
            "precision_gate_pass": precision_gate,
            "promoted_candidate": promotion,
        },
        "reference_events": events,
        "key_checkpoints": checkpoint_table(expanding, annual),
        "rows": {
            "EXPANDING_REFIT": expanding,
            "ANNUAL_ANCHORED": annual,
        },
        "governance": {
            "market_state_only": True,
            "forecast_used": False,
            "forecast_error_used": False,
            "alarm_labels_used": False,
            "future_target_information_used": False,
            "v3_rule_tuned_on_2022_plus": False,
            "2025_2026_claimed_untouched": False,
            "alarm_selection_tested": False,
            "alarm_weighting_tested": False,
            "forecast_correction_tested": False,
            "routing_tested": False,
        },
    }

    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")

    def compact(m):
        return {k: v for k, v in m.items() if k != "event_details"}

    print("SCIENTIFIC_GATE=PASS")
    print(json.dumps({
        "selected_rule": selected,
        "selection": selection,
        "promotion_gate": result["promotion_gate"],
        "calibration": {k: compact(v) for k, v in metrics["calibration_2015_07_2021_12"].items()},
        "validation": {k: compact(v) for k, v in metrics["validation_2022_01_2024_12"].items()},
        "transport": {k: compact(v) for k, v in metrics["transport_2025_01_2026_08"].items()},
        "key_checkpoints": result["key_checkpoints"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
