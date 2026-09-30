from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import logsumexp

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
    "drop_thr": [0.10, 0.15, 0.20, 0.25],
    "margin_thr": [0.15, 0.25, 0.35, 0.45],
    "margin_drop_thr": [0.15, 0.25, 0.35, 0.45],
    "alt_growth_thr": [0.10, 0.15, 0.20, 0.25],
    "proto_drop_thr": [0.25, 0.50, 0.75, 1.00],
    "fast_votes": [2, 3],
    "persistent_votes": [1, 2],
    "persistent_margin_thr": [0.30, 0.45, 0.60],
}


def load_json(path: str):
    return json.loads(Path(path).read_text())


def next_month(month: str) -> str:
    return str(pd.Period(month, freq="M") + 1)


def month_diff(a: str, b: str) -> int:
    return int(pd.Period(b, freq="M").ordinal - pd.Period(a, freq="M").ordinal)


def semantic_posts(raw_posts: np.ndarray, mapping: dict[int, int]) -> np.ndarray:
    out = np.zeros_like(raw_posts)
    for raw_state, sem_state in mapping.items():
        out[:, sem_state] = raw_posts[:, raw_state]
    return out


def prototype_distances(raw_values: np.ndarray, proto) -> np.ndarray:
    z = (raw_values - proto["mu"]) / proto["sd"]
    p = np.asarray([proto["prototype_vectors"][r] for r in R_STATES], float)
    return np.sqrt(((z[:, None, :] - p[None, :, :]) ** 2).sum(axis=2))


def interval_features(sem_posts_arr: np.ndarray, proto_dist_arr: np.ndarray, i: int):
    if i <= 0:
        return None
    incumbent = int(np.argmax(sem_posts_arr[i - 1]))
    alt_idx = [s for s in range(3) if s != incumbent]

    p_inc_prev = float(sem_posts_arr[i - 1, incumbent])
    p_inc_cur = float(sem_posts_arr[i, incumbent])

    alt_prev = float(np.max(sem_posts_arr[i - 1, alt_idx]))
    alt_cur = float(np.max(sem_posts_arr[i, alt_idx]))

    margin_prev = float(p_inc_prev - alt_prev)
    margin_cur = float(p_inc_cur - alt_cur)

    d_inc_prev = float(proto_dist_arr[i - 1, incumbent])
    d_inc_cur = float(proto_dist_arr[i, incumbent])
    d_alt_prev = float(np.min(proto_dist_arr[i - 1, alt_idx]))
    d_alt_cur = float(np.min(proto_dist_arr[i, alt_idx]))

    proto_adv_prev = float(d_alt_prev - d_inc_prev)
    proto_adv_cur = float(d_alt_cur - d_inc_cur)

    return {
        "incumbent_semantic_state_id": incumbent,
        "incumbent_semantic_state": f"R{incumbent}",
        "incumbent_posterior_prev": p_inc_prev,
        "incumbent_posterior_cur": p_inc_cur,
        "incumbent_drop": float(p_inc_prev - p_inc_cur),
        "alternative_posterior_prev": alt_prev,
        "alternative_posterior_cur": alt_cur,
        "alternative_growth": float(alt_cur - alt_prev),
        "margin_prev": margin_prev,
        "margin_cur": margin_cur,
        "margin_drop": float(margin_prev - margin_cur),
        "prototype_advantage_prev": proto_adv_prev,
        "prototype_advantage_cur": proto_adv_cur,
        "prototype_advantage_drop": float(proto_adv_prev - proto_adv_cur),
    }


def score_sequence_features(fit, train: pd.DataFrame, future: pd.DataFrame, proto):
    raw_train = train[FEATURES].to_numpy(float)
    raw_future = future[FEATURES].to_numpy(float)
    raw_all = np.vstack([raw_train, raw_future])

    z_future = fit["scaler"].transform(raw_future)
    x_future = fit["pca"].transform(z_future)
    x_all = np.vstack([fit["x_train"], x_future])

    posts, loge = base.forward_filter(fit["model"], x_all)
    sem = semantic_posts(posts, fit["prototype_mapping"])
    pdist = prototype_distances(raw_all, proto)

    ntrain = len(train)
    transmat = np.asarray(fit["model"].transmat_, float)
    out = []

    for j, month in enumerate(future.index):
        i = ntrain + j
        cur = interval_features(sem, pdist, i)
        prev = interval_features(sem, pdist, i - 1)

        current_best_sem = int(np.argmax(sem[i]))
        current_best_prob = float(sem[i, current_best_sem])
        semantic_state = f"R{current_best_sem}"
        semantic_label = semantic_state if current_best_prob >= CONFIDENCE else "BELIRSIZ"

        prior = posts[i - 1] @ transmat
        pred_score = float(logsumexp(np.log(np.maximum(prior, 1e-300)) + loge[i]))

        row = {
            "month": str(month),
            "semantic_state": semantic_state,
            "semantic_label": semantic_label,
            "semantic_probability": current_best_prob,
            "predictive_log_score": pred_score,
            "train_start": fit["train_start"],
            "train_end": fit["train_end"],
            "train_rows": fit["train_rows"],
            "hmm_seed": fit["seed"],
            "prototype_assignment": fit["prototype_detail"]["assignment"],
        }
        for prefix, feat in [("current", cur), ("previous_interval", prev)]:
            if feat is None:
                continue
            for k, v in feat.items():
                row[f"{prefix}_{k}"] = v
        out.append(row)

    return out


def expanding_rows(panel: pd.DataFrame, months: list[str], proto):
    rows = []
    for month in months:
        train = panel.loc[panel.index < month].copy()
        cur = panel.loc[[month]].copy()
        fit = palign.fit_frozen(train, proto)
        row = score_sequence_features(fit, train, cur, proto)[0]
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
        scored = score_sequence_features(fit, train, future, proto)
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


def directional_votes(row, params, prefix="current"):
    vals = {
        "drop": float(row[f"{prefix}_incumbent_drop"]),
        "margin_drop": float(row[f"{prefix}_margin_drop"]),
        "alt_growth": float(row[f"{prefix}_alternative_growth"]),
        "proto_drop": float(row[f"{prefix}_prototype_advantage_drop"]),
    }
    flags = {
        "POSTERIOR_DROP": vals["drop"] >= params["drop_thr"],
        "MARGIN_COLLAPSE": vals["margin_drop"] >= params["margin_drop_thr"],
        "ALTERNATIVE_GROWTH": vals["alt_growth"] >= params["alt_growth_thr"],
        "PROTOTYPE_ADVANTAGE_DROP": vals["proto_drop"] >= params["proto_drop_thr"],
    }
    return int(sum(flags.values())), flags


def apply_rule_row(row, params):
    cur_votes, cur_flags = directional_votes(row, params, "current")
    prev_votes, prev_flags = directional_votes(row, params, "previous_interval")
    margin_cur = float(row["current_margin_cur"])

    fast = bool(margin_cur <= params["margin_thr"] and cur_votes >= params["fast_votes"])
    persistent = bool(
        margin_cur <= params["persistent_margin_thr"]
        and cur_votes >= params["persistent_votes"]
        and prev_votes >= params["persistent_votes"]
    )
    flag = bool(fast or persistent)

    return {
        "transition_flag": flag,
        "transition_status": "TRANSITION" if flag else "STABLE",
        "fast_branch": fast,
        "persistent_branch": persistent,
        "current_directional_votes": cur_votes,
        "previous_directional_votes": prev_votes,
        "current_directional_flags": [k for k, v in cur_flags.items() if v],
        "previous_directional_flags": [k for k, v in prev_flags.items() if v],
    }


def apply_rule(rows, params):
    out = []
    for r in rows:
        z = dict(r)
        z.update(apply_rule_row(r, params))
        out.append(z)
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
        "event_details": details,
    }


def parameter_tuples():
    keys = [
        "drop_thr", "margin_thr", "margin_drop_thr", "alt_growth_thr",
        "proto_drop_thr", "fast_votes", "persistent_votes", "persistent_margin_thr",
    ]
    for vals in itertools.product(*(GRID[k] for k in keys)):
        yield dict(zip(keys, vals))


def lex_tuple(p):
    return tuple(p[k] for k in [
        "drop_thr", "margin_thr", "margin_drop_thr", "alt_growth_thr",
        "proto_drop_thr", "fast_votes", "persistent_votes", "persistent_margin_thr",
    ])


def select_rule(cal_rows, events):
    scored = []
    for p in parameter_tuples():
        applied = apply_rule(cal_rows, p)
        m = period_metrics(applied, events, CAL_START, CAL_END)
        scored.append((p, m))

    eligible = [(p, m) for p, m in scored if (m["event_hit_rate"] or 0.0) >= (2.0 / 3.0)]
    used_fallback = False

    if eligible:
        def key(item):
            p, m = item
            precision = -1.0 if m["precision"] is None else m["precision"]
            zrec = -1.0 if m["transition_zone_recall"] is None else m["transition_zone_recall"]
            lead = -999.0 if m["mean_lead_months_before_confirmation"] is None else m["mean_lead_months_before_confirmation"]
            return (
                m["false_transition_rate_non_zone"],
                -precision,
                -zrec,
                -lead,
                lex_tuple(p),
            )
        best = min(eligible, key=key)
    else:
        used_fallback = True
        def key(item):
            p, m = item
            hit = -1.0 if m["event_hit_rate"] is None else m["event_hit_rate"]
            precision = -1.0 if m["precision"] is None else m["precision"]
            zrec = -1.0 if m["transition_zone_recall"] is None else m["transition_zone_recall"]
            return (
                -hit,
                m["false_transition_rate_non_zone"],
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
        "fallback_used": used_fallback,
    }


def verify_against_prior(rows, prior_rows, detector):
    prior = {r["month"]: r for r in prior_rows}
    problems = []
    max_prob = 0.0
    max_score = 0.0
    for r in rows:
        p = prior.get(r["month"])
        if p is None:
            problems.append({"month": r["month"], "issue": "missing_prior"})
            continue
        dp = abs(float(r["semantic_probability"]) - float(p["probability"]))
        ds = abs(float(r["predictive_log_score"]) - float(p["predictive_log_score"]))
        max_prob = max(max_prob, dp)
        max_score = max(max_score, ds)
        if dp > 1e-6 or ds > 1e-6 or r["semantic_state"] != p["prototype_state"] or r["semantic_label"] != p["prototype_label"]:
            problems.append({
                "month": r["month"],
                "probability_abs_diff": dp,
                "score_abs_diff": ds,
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
        "max_predictive_log_score_abs_diff": max_score,
        "problems": problems,
    }


def v1_period_metrics(v1_rows, events, start, end):
    rows = []
    for r in v1_rows:
        z = {
            "month": r["month"],
            "transition_flag": bool(r["transition_flag"]),
        }
        rows.append(z)
    return period_metrics(rows, events, start, end)


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
                "semantic_label": r["semantic_label"],
                "semantic_state": r["semantic_state"],
                "semantic_probability": r["semantic_probability"],
                "transition_status": r["transition_status"],
                "fast_branch": r["fast_branch"],
                "persistent_branch": r["persistent_branch"],
                "current_votes": r["current_directional_votes"],
                "previous_votes": r["previous_directional_votes"],
                "current_flags": r["current_directional_flags"],
                "previous_flags": r["previous_directional_flags"],
                "incumbent_drop": r["current_incumbent_drop"],
                "margin_cur": r["current_margin_cur"],
                "margin_drop": r["current_margin_drop"],
                "alternative_growth": r["current_alternative_growth"],
                "prototype_advantage_drop": r["current_prototype_advantage_drop"],
            }
            row["reference"] = {
                "state": r["reference_state"],
                "label": r["reference_label"],
                "probability": r["reference_probability"],
            }
        out.append(row)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--regime-discovery-json", required=True)
    ap.add_argument("--prototype-alignment-json", required=True)
    ap.add_argument("--v1-json", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    src = load_json(args.regime_discovery_json)
    prior = load_json(args.prototype_alignment_json)
    v1 = load_json(args.v1_json)

    if src.get("status") != "COMPLETE" or src.get("evidence", {}).get("selected_hmm_k") != 3:
        raise RuntimeError("INVALID_DISCOVERY_REFERENCE")
    if prior.get("status") != "COMPLETE":
        raise RuntimeError("INVALID_PROTOTYPE_ALIGNMENT_REFERENCE")
    if v1.get("status") != "COMPLETE":
        raise RuntimeError("INVALID_V1_REFERENCE")

    raw = pd.DataFrame(src["monthly_regimes"]).sort_values("month").reset_index(drop=True)
    proto = palign.build_frozen_prototypes(raw)
    panel = raw[["month"] + FEATURES].copy().set_index("month")
    ref = raw[["month", "state", "state_probability", "ood_below_train_p05"]].copy().set_index("month")
    events = build_reference_events(raw[["month", "state", "state_probability"]])

    # 1) Historical calibration only. No 2022+ detector rows are computed before rule freeze.
    cal_months = [m for m in panel.index if CAL_START <= m <= CAL_END]
    cal_exp_base = attach_reference(expanding_rows(panel, cal_months, proto), ref)
    selection = select_rule(cal_exp_base, events)
    selected = selection["selected_params"]

    # Rule is frozen here.
    cal_exp = apply_rule(cal_exp_base, selected)

    # 2) Only after freeze, compute later periods and the annual schedule.
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

    v1_validation = {
        "EXPANDING_REFIT": v1_period_metrics(v1["rows"]["EXPANDING_REFIT"], events, VAL_START, VAL_END),
        "ANNUAL_ANCHORED": v1_period_metrics(v1["rows"]["ANNUAL_ANCHORED"], events, VAL_START, VAL_END),
    }

    vm = metrics["validation_2022_01_2024_12"]["EXPANDING_REFIT"]
    v1m = v1_validation["EXPANDING_REFIT"]
    precision_gate = (
        vm["precision"] is not None and v1m["precision"] is not None
        and vm["precision"] >= v1m["precision"] + 0.05
    )
    promotion = bool(
        (vm["event_hit_rate"] or 0.0) >= (2.0 / 3.0)
        and (vm["false_transition_rate_non_zone"] or 1.0) <= 0.15
        and precision_gate
    )

    result = {
        "schema": "GOLD_MONTHLY_MARKET_REGIME_TRANSITION_DETECTOR_V2_2026-09-30",
        "status": "COMPLETE",
        "scientific_gate": "PASS",
        "calibration_freeze": {
            "calibration_period": [CAL_START, CAL_END],
            "primary_schedule": "EXPANDING_REFIT",
            "candidate_grid": GRID,
            "selection": selection,
            "rule_frozen_before_2022_plus_rows": True,
        },
        "selected_rule": selected,
        "underlying_regime_reproduction": {
            "EXPANDING_REFIT": verify_exp,
            "ANNUAL_ANCHORED": verify_ann,
        },
        "metrics": metrics,
        "v1_validation_2022_2024": v1_validation,
        "promotion_gate": {
            "validation_event_hit_rate_required": 2.0 / 3.0,
            "validation_false_transition_rate_max": 0.15,
            "validation_precision_required_vs_v1": "V1 + 0.05",
            "v2_event_hit_rate": vm["event_hit_rate"],
            "v2_false_transition_rate": vm["false_transition_rate_non_zone"],
            "v2_precision": vm["precision"],
            "v1_precision": v1m["precision"],
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
            "market_state_features_only": True,
            "forecast_error_used": False,
            "forecast_used": False,
            "alarm_labels_used": False,
            "high_medium_normal_used": False,
            "future_target_information_used": False,
            "reference_labels_used_for_calibration_only_2015_2021": True,
            "reference_labels_used_for_detection": False,
            "v2_rule_tuned_on_2022_plus": False,
            "2025_2026_claimed_untouched": False,
            "alarm_selection_tested": False,
            "alarm_weighting_tested": False,
            "forecast_correction_tested": False,
            "routing_tested": False,
        },
    }

    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")

    def compact(m):
        return {k: {kk: vv for kk, vv in v.items() if kk != "event_details"} for k, v in m.items()}

    print("SCIENTIFIC_GATE=PASS")
    print(json.dumps({
        "selected_rule": selected,
        "selection": selection,
        "promotion_gate": result["promotion_gate"],
        "calibration": compact(metrics["calibration_2015_07_2021_12"]),
        "validation": compact(metrics["validation_2022_01_2024_12"]),
        "transport": compact(metrics["transport_2025_01_2026_08"]),
        "full": compact(metrics["full_replay_2015_07_2026_08"]),
        "v1_validation": compact(v1_validation),
        "key_checkpoints": result["key_checkpoints"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
