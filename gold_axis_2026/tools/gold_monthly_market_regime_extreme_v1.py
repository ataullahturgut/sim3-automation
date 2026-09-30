from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import logsumexp

import gold_monthly_market_regime_discovery_v1 as base
import gold_monthly_market_regime_prototype_alignment_v1 as palign

START = "2015-07"
HIST_END = "2021-12"
VAL_START = "2022-01"
VAL_END = "2024-12"
TRANSPORT_START = "2025-01"
END = "2026-08"
CONFIDENCE = 0.60
FEATURES = list(base.FEATURES)


def load_json(path: str):
    return json.loads(Path(path).read_text())


def training_predictive_scores(model, posts: np.ndarray, loge: np.ndarray) -> np.ndarray:
    vals = []
    trans = np.asarray(model.transmat_, float)
    for i in range(1, len(posts)):
        prior = posts[i - 1] @ trans
        vals.append(float(logsumexp(np.log(np.maximum(prior, 1e-300)) + loge[i])))
    return np.asarray(vals, float)


def fit_extreme_stats(fit, train: pd.DataFrame):
    scaler = fit["scaler"]
    model = fit["model"]
    z_train = scaler.transform(train[FEATURES].to_numpy(float))
    x_train = fit["x_train"]
    posts, loge = base.forward_filter(model, x_train)
    hard = posts.argmax(axis=1)

    centers = {}
    state_distance_pools = {}
    emission_pools = {}

    for s in range(model.n_components):
        w = posts[:, s].astype(float)
        den = float(w.sum())
        if den <= 1e-12:
            raise RuntimeError(("ZERO_STATE_MASS", s, len(train)))
        center = np.sum(w[:, None] * z_train, axis=0) / den
        centers[s] = center

        mask = hard == s
        state_distance_pools[s] = np.sqrt(np.sum((z_train[mask] - center) ** 2, axis=1))
        emission_pools[s] = loge[mask, s]

    pred_scores = training_predictive_scores(model, posts, loge)
    jumps = np.sqrt(np.sum(np.diff(z_train, axis=0) ** 2, axis=1))

    return {
        "z_train": z_train,
        "posts_train": posts,
        "loge_train": loge,
        "hard_train": hard,
        "centers": centers,
        "distance_pools": state_distance_pools,
        "emission_pools": emission_pools,
        "predictive_scores": pred_scores,
        "predictive_q10": float(np.quantile(pred_scores, 0.10)),
        "jump_pool": jumps,
        "jump_q90": float(np.quantile(jumps, 0.90)),
    }


def score_sequence(fit, train: pd.DataFrame, future: pd.DataFrame):
    stats = fit_extreme_stats(fit, train)
    scaler = fit["scaler"]
    pca = fit["pca"]
    model = fit["model"]

    raw_future = future[FEATURES].to_numpy(float)
    z_future = scaler.transform(raw_future)
    x_future = pca.transform(z_future)

    x_all = np.vstack([fit["x_train"], x_future])
    z_all = np.vstack([stats["z_train"], z_future])

    posts, loge = base.forward_filter(model, x_all)
    ntrain = len(train)
    trans = np.asarray(model.transmat_, float)

    out = []
    for j, month in enumerate(future.index):
        i = ntrain + j
        prev_i = i - 1

        prev_best = int(np.argmax(posts[prev_i]))
        cur_best = int(np.argmax(posts[i]))
        prev_prob = float(posts[prev_i, prev_best])
        cur_prob = float(posts[i, cur_best])

        eligible = bool(prev_best == cur_best and prev_prob >= CONFIDENCE and cur_prob >= CONFIDENCE)
        persistent_state = cur_best if eligible else None

        # One-step predictive score and jump are always available.
        prior = posts[prev_i] @ trans
        pred_score = float(logsumexp(np.log(np.maximum(prior, 1e-300)) + loge[i]))
        e2 = bool(pred_score <= stats["predictive_q10"])
        pred_pct = float(np.mean(stats["predictive_scores"] <= pred_score))

        jump = float(np.sqrt(np.sum((z_all[i] - z_all[prev_i]) ** 2)))
        e4 = bool(jump >= stats["jump_q90"])
        jump_pct = float(np.mean(stats["jump_pool"] <= jump))

        e1 = False
        e3 = False
        emission_pct = None
        emission_q10 = None
        state_dist = None
        state_dist_q90 = None
        state_dist_pct = None
        pool_size = 0

        if eligible:
            s = persistent_state
            epool = stats["emission_pools"][s]
            dpool = stats["distance_pools"][s]
            pool_size = int(min(len(epool), len(dpool)))

            if pool_size >= 8:
                emission_q10 = float(np.quantile(epool, 0.10))
                cur_emission = float(loge[i, s])
                emission_pct = float(np.mean(epool <= cur_emission))
                e1 = bool(cur_emission <= emission_q10)

                center = stats["centers"][s]
                state_dist = float(np.sqrt(np.sum((z_all[i] - center) ** 2)))
                state_dist_q90 = float(np.quantile(dpool, 0.90))
                state_dist_pct = float(np.mean(dpool <= state_dist))
                e3 = bool(state_dist >= state_dist_q90)

        active = []
        for name, flag in [
            ("E1_STATE_EMISSION_TAIL", e1),
            ("E2_PREDICTIVE_SURPRISE", e2),
            ("E3_WITHIN_STATE_13D_DISTANCE", e3),
            ("E4_MARKET_STATE_JUMP", e4),
        ]:
            if flag:
                active.append(name)

        anomaly_count = int(e1) + int(e2) + int(e3) + int(e4)

        if not eligible:
            status = "DEFER"
            extreme = False
        else:
            extreme = bool(anomaly_count >= 2)
            status = "EXTREME" if extreme else "NORMAL"

        sem_id = int(fit["prototype_mapping"][cur_best])
        sem_state = f"R{sem_id}"
        sem_label = sem_state if cur_prob >= CONFIDENCE else "BELIRSIZ"

        out.append({
            "month": str(month),
            "extreme_status": status,
            "extreme_flag": extreme,
            "eligible_within_regime": eligible,
            "anomaly_count": anomaly_count,
            "active_signals": active,
            "E1_state_emission_tail": e1,
            "E2_predictive_surprise": e2,
            "E3_within_state_13D_distance": e3,
            "E4_market_state_jump": e4,
            "previous_raw_state": prev_best,
            "current_raw_state": cur_best,
            "previous_raw_state_probability": prev_prob,
            "current_raw_state_probability": cur_prob,
            "same_raw_state": bool(prev_best == cur_best),
            "semantic_state": sem_state,
            "semantic_label": sem_label,
            "semantic_probability": cur_prob,
            "state_pool_size": pool_size,
            "emission_empirical_percentile": emission_pct,
            "emission_train_q10": emission_q10,
            "predictive_log_score": pred_score,
            "predictive_score_empirical_percentile": pred_pct,
            "predictive_score_train_q10": stats["predictive_q10"],
            "within_state_distance": state_dist,
            "within_state_distance_train_q90": state_dist_q90,
            "within_state_distance_empirical_percentile": state_dist_pct,
            "market_state_jump_norm": jump,
            "market_state_jump_train_q90": stats["jump_q90"],
            "market_state_jump_empirical_percentile": jump_pct,
            "train_start": fit["train_start"],
            "train_end": fit["train_end"],
            "train_rows": fit["train_rows"],
            "hmm_seed": fit["seed"],
            "prototype_assignment_reporting_only": fit["prototype_detail"]["assignment"],
        })

    return out


def expanding_rows(panel: pd.DataFrame, months: list[str], proto):
    rows = []
    for month in months:
        train = panel.loc[panel.index < month].copy()
        cur = panel.loc[[month]].copy()
        fit = palign.fit_frozen(train, proto)
        row = score_sequence(fit, train, cur)[0]
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
        scored = score_sequence(fit, train, future)
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


def attach_transition(rows, v2_rows):
    vm = {r["month"]: r for r in v2_rows}
    out = []
    for r in rows:
        v = vm.get(r["month"])
        if v is None:
            raise RuntimeError(("MISSING_V2_MONTH", r["detector"], r["month"]))
        z = dict(r)
        z["transition_v2_flag"] = bool(v["transition_flag"])
        z["transition_v2_status"] = str(v["transition_status"])
        out.append(z)
    return out


def run_lengths(rows):
    months = [r["month"] for r in rows if r["extreme_status"] == "EXTREME"]
    if not months:
        return {"max_run_length": 0, "runs": []}

    periods = [pd.Period(m, freq="M") for m in months]
    runs = []
    start = periods[0]
    prev = periods[0]

    for p in periods[1:]:
        if p.ordinal == prev.ordinal + 1:
            prev = p
        else:
            runs.append((start, prev))
            start = prev = p
    runs.append((start, prev))

    data = [
        {
            "start": str(a),
            "end": str(b),
            "length": int(b.ordinal - a.ordinal + 1),
        }
        for a, b in runs
    ]
    return {"max_run_length": max(x["length"] for x in data), "runs": data}


def period_metrics(rows, start, end):
    rr = [r for r in rows if start <= r["month"] <= end]
    eligible = [r for r in rr if r["eligible_within_regime"]]
    extreme = [r for r in eligible if r["extreme_flag"]]
    normal = [r for r in eligible if not r["extreme_flag"]]
    deferred = [r for r in rr if not r["eligible_within_regime"]]

    anomaly_dist = Counter(str(r["anomaly_count"]) for r in eligible)
    sem_dist = Counter(r["semantic_state"] for r in extreme)

    both = sum(r["extreme_flag"] and r["transition_v2_flag"] for r in rr)
    extreme_only = sum(r["extreme_flag"] and not r["transition_v2_flag"] for r in rr)
    transition_only = sum((not r["extreme_flag"]) and r["transition_v2_flag"] for r in rr)
    neither = len(rr) - both - extreme_only - transition_only

    return {
        "n_months": len(rr),
        "eligible_months": len(eligible),
        "defer_count": len(deferred),
        "defer_rate": None if not rr else float(len(deferred) / len(rr)),
        "extreme_count": len(extreme),
        "extreme_rate_among_eligible": None if not eligible else float(len(extreme) / len(eligible)),
        "normal_count": len(normal),
        "anomaly_count_distribution_eligible": dict(anomaly_dist),
        "extreme_semantic_regime_distribution_reporting_only": dict(sem_dist),
        "extreme_runs": run_lengths(rr),
        "transition_v2_overlap": {
            "extreme_only": int(extreme_only),
            "transition_only": int(transition_only),
            "both": int(both),
            "neither": int(neither),
            "share_of_extreme_also_transition": None if not extreme else float(both / len(extreme)),
        },
        "extreme_months": [
            {
                "month": r["month"],
                "semantic_state": r["semantic_state"],
                "anomaly_count": r["anomaly_count"],
                "active_signals": r["active_signals"],
                "transition_v2": r["transition_v2_status"],
            }
            for r in extreme
        ],
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


def checkpoint_table(expanding, annual):
    months = [
        "2024-03", "2024-04", "2024-05", "2024-06",
        "2026-01", "2026-02", "2026-03", "2026-04",
        "2026-05", "2026-06", "2026-07", "2026-08",
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
                "extreme_status": r["extreme_status"],
                "anomaly_count": r["anomaly_count"],
                "active_signals": r["active_signals"],
                "transition_v2_status": r["transition_v2_status"],
                "same_raw_state": r["same_raw_state"],
                "previous_raw_state_probability": r["previous_raw_state_probability"],
                "current_raw_state_probability": r["current_raw_state_probability"],
                "emission_percentile": r["emission_empirical_percentile"],
                "predictive_score_percentile": r["predictive_score_empirical_percentile"],
                "within_state_distance_percentile": r["within_state_distance_empirical_percentile"],
                "jump_percentile": r["market_state_jump_empirical_percentile"],
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
    months = [m for m in panel.index if START <= m <= END]

    expanding = attach_reference(expanding_rows(panel, months, proto), ref)
    annual = attach_reference(annual_rows(panel, months, proto), ref)

    expanding = attach_transition(expanding, v2["rows"]["EXPANDING_REFIT"])
    annual = attach_transition(annual, v2["rows"]["ANNUAL_ANCHORED"])

    verify_exp = verify_against_prior(expanding, prior["rows"]["EXPANDING_REFIT"], "EXPANDING_REFIT")
    verify_ann = verify_against_prior(annual, prior["rows"]["ANNUAL_ANCHORED"], "ANNUAL_ANCHORED")
    if not verify_exp["pass"] or not verify_ann["pass"]:
        raise RuntimeError(("UNDERLYING_REGIME_REPRODUCTION_FAILED", verify_exp, verify_ann))

    periods = {
        "historical_2015_07_2021_12": (START, HIST_END),
        "validation_2022_01_2024_12": (VAL_START, VAL_END),
        "transport_2025_01_2026_08": (TRANSPORT_START, END),
        "full_replay_2015_07_2026_08": (START, END),
    }

    metrics = {}
    for pname, (a, b) in periods.items():
        metrics[pname] = {
            "EXPANDING_REFIT": period_metrics(expanding, a, b),
            "ANNUAL_ANCHORED": period_metrics(annual, a, b),
        }

    hist_rate = metrics["historical_2015_07_2021_12"]["EXPANDING_REFIT"]["extreme_rate_among_eligible"]
    val_rate = metrics["validation_2022_01_2024_12"]["EXPANDING_REFIT"]["extreme_rate_among_eligible"]
    val_overlap = metrics["validation_2022_01_2024_12"]["EXPANDING_REFIT"]["transition_v2_overlap"]["share_of_extreme_also_transition"]

    selectivity_hist = hist_rate is not None and 0.05 <= hist_rate <= 0.30
    selectivity_val = val_rate is not None and 0.05 <= val_rate <= 0.30
    distinctness = val_overlap is not None and val_overlap < 0.50
    descriptive_candidate = bool(selectivity_hist and selectivity_val and distinctness)

    result = {
        "schema": "GOLD_MONTHLY_MARKET_REGIME_EXTREME_V1_2026-09-30",
        "status": "COMPLETE",
        "scientific_gate": "PASS",
        "rule": {
            "eligibility": "same raw latent state at t-1 and t; both posteriors >=0.60",
            "E1": "persistent-state emission logdensity <= training same-state q10",
            "E2": "one-step predictive log score <= training q10",
            "E3": "distance to posterior-weighted same-state 13D standardized center >= training same-state q90",
            "E4": "13D standardized month-to-month jump >= training q90",
            "EXTREME": "eligible AND at least 2 of E1..E4",
            "NORMAL": "eligible AND fewer than 2 signals",
            "DEFER": "not eligible",
            "threshold_search": False,
        },
        "underlying_regime_reproduction": {
            "EXPANDING_REFIT": verify_exp,
            "ANNUAL_ANCHORED": verify_ann,
        },
        "diagnostic_gate": {
            "historical_extreme_rate": hist_rate,
            "validation_extreme_rate": val_rate,
            "validation_share_of_extreme_also_transition_v2": val_overlap,
            "historical_selectivity_5_to_30pct_pass": selectivity_hist,
            "validation_selectivity_5_to_30pct_pass": selectivity_val,
            "distinctness_less_than_50pct_overlap_pass": distinctness,
            "descriptive_candidate_pass": descriptive_candidate,
        },
        "metrics": metrics,
        "key_checkpoints": checkpoint_table(expanding, annual),
        "rows": {
            "EXPANDING_REFIT": expanding,
            "ANNUAL_ANCHORED": annual,
        },
        "governance": {
            "market_state_features_only": True,
            "semantic_prototypes_used_in_extreme_decision": False,
            "semantic_labels_reporting_only": True,
            "transition_v2_used_in_extreme_decision": False,
            "transition_v2_overlap_reporting_only": True,
            "forecast_error_used": False,
            "forecast_used": False,
            "alarm_labels_used": False,
            "high_medium_normal_used": False,
            "future_target_information_used": False,
            "thresholds_tuned": False,
            "alarm_selection_tested": False,
            "alarm_weighting_tested": False,
            "forecast_correction_tested": False,
            "routing_tested": False,
            "2025_2026_claimed_untouched": False,
        },
    }

    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")

    def compact(x):
        y = dict(x)
        y.pop("extreme_months", None)
        y.pop("extreme_runs", None)
        return y

    print("SCIENTIFIC_GATE=PASS")
    print(json.dumps({
        "diagnostic_gate": result["diagnostic_gate"],
        "historical": {k: compact(v) for k, v in metrics["historical_2015_07_2021_12"].items()},
        "validation": {k: compact(v) for k, v in metrics["validation_2022_01_2024_12"].items()},
        "transport": {k: compact(v) for k, v in metrics["transport_2025_01_2026_08"].items()},
        "transport_extreme_months": {
            k: v["extreme_months"] for k, v in metrics["transport_2025_01_2026_08"].items()
        },
        "key_checkpoints": result["key_checkpoints"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
