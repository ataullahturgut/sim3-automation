from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import logsumexp
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import gold_monthly_market_regime_discovery_v1 as base

EVAL_START = "2015-07"
CORE_START = "2022-01"
TRANSPORT_START = "2025-01"
END = "2026-08"
K = 3
CONFIDENCE = 0.60
OOD_Q = 0.05
MIN_TRAIN_MONTHS = 60
FEATURES = list(base.FEATURES)
R_STATES = ["R0", "R1", "R2"]


def load_json(path: str):
    return json.loads(Path(path).read_text())


def month_diff(a: str, b: str) -> int:
    return int(pd.Period(b, freq="M").ordinal - pd.Period(a, freq="M").ordinal)


def canonical_map_training(posts: np.ndarray, train: pd.DataFrame):
    hard = posts.argmax(axis=1)
    if len(set(int(x) for x in hard)) == K:
        return base.canonical_map(hard, train), False

    scores = []
    gold = train["Gold_r1"].to_numpy(float)
    vol = train["Gold_rv_ratio"].to_numpy(float)
    for s in range(K):
        w = posts[:, s].astype(float)
        den = float(w.sum())
        if den <= 1e-12:
            g = float("inf")
            v = float("inf")
        else:
            g = float(np.sum(w * gold) / den)
            v = float(np.sum(w * vol) / den)
        scores.append((g, v, int(s)))
    scores.sort()
    return {old: new for new, (_, _, old) in enumerate(scores)}, True


def fit_frozen(train: pd.DataFrame):
    if len(train) < MIN_TRAIN_MONTHS:
        raise RuntimeError(("INSUFFICIENT_TRAIN_HISTORY", len(train), str(train.index.min()), str(train.index.max())))

    scaler = StandardScaler().fit(train[FEATURES].to_numpy(float))
    z_train = scaler.transform(train[FEATURES].to_numpy(float))

    pca_full = PCA().fit(z_train)
    cum = np.cumsum(pca_full.explained_variance_ratio_)
    npc = int(np.searchsorted(cum, 0.85) + 1)
    npc = max(2, min(6, npc))

    pca = PCA(n_components=npc, random_state=0).fit(z_train)
    x_train = pca.transform(z_train)

    (ll, seed, model), failures = base.fit_best_hmm(x_train, K)
    train_posts, train_loge = base.forward_filter(model, x_train)
    mapping, fallback = canonical_map_training(train_posts, train)

    train_max_emission = train_loge.max(axis=1)
    ood_threshold = float(np.quantile(train_max_emission, OOD_Q))

    return {
        "scaler": scaler,
        "pca": pca,
        "model": model,
        "mapping": mapping,
        "mapping_fallback": fallback,
        "npc": npc,
        "pca_explained": float(pca.explained_variance_ratio_.sum()),
        "seed": int(seed),
        "train_ll": float(ll),
        "fit_failures": int(len(failures)),
        "ood_threshold": ood_threshold,
        "train_rows": int(len(train)),
        "train_start": str(train.index.min()),
        "train_end": str(train.index.max()),
        "x_train": x_train,
    }


def score_sequence(fit, train: pd.DataFrame, future: pd.DataFrame):
    scaler = fit["scaler"]
    pca = fit["pca"]
    model = fit["model"]
    mapping = fit["mapping"]

    z_future = scaler.transform(future[FEATURES].to_numpy(float))
    x_future = pca.transform(z_future)
    x_all = np.vstack([fit["x_train"], x_future])

    posts, loge = base.forward_filter(model, x_all)
    ntrain = len(train)
    out = []
    for j, month in enumerate(future.index):
        i = ntrain + j
        prev = posts[i - 1]
        prior = prev @ np.asarray(model.transmat_, float)
        logpred = float(logsumexp(np.log(np.maximum(prior, 1e-300)) + loge[i]))

        raw_state = int(np.argmax(posts[i]))
        state_id = int(mapping[raw_state])
        state = f"R{state_id}"
        prob = float(posts[i, raw_state])
        label = state if prob >= CONFIDENCE else "BELIRSIZ"
        max_em = float(loge[i].max())
        ood = bool(max_em < fit["ood_threshold"])

        out.append({
            "month": str(month),
            "state": state,
            "state_id": state_id,
            "probability": prob,
            "label": label,
            "ood": ood,
            "predictive_log_score": logpred,
            "max_emission_logdensity": max_em,
            "ood_threshold_train_p05": fit["ood_threshold"],
            "train_start": fit["train_start"],
            "train_end": fit["train_end"],
            "train_rows": fit["train_rows"],
            "pca_components": fit["npc"],
            "pca_explained_variance": fit["pca_explained"],
            "hmm_seed": fit["seed"],
            "hmm_train_loglik": fit["train_ll"],
            "hmm_fit_failure_count": fit["fit_failures"],
            "canonical_mapping": {str(k): int(v) for k, v in mapping.items()},
            "canonical_weighted_fallback": bool(fit["mapping_fallback"]),
        })
    return out


def expanding_rows(panel: pd.DataFrame, months: list[str]):
    rows = []
    for month in months:
        train = panel.loc[panel.index < month].copy()
        cur = panel.loc[[month]].copy()
        fit = fit_frozen(train)
        row = score_sequence(fit, train, cur)[0]
        row["detector"] = "EXPANDING_REFIT"
        rows.append(row)
    return rows


def annual_anchored_rows(panel: pd.DataFrame, months: list[str]):
    by_year = {}
    for m in months:
        by_year.setdefault(int(m[:4]), []).append(m)

    rows = []
    for year in sorted(by_year):
        anchor_end = f"{year-1}-12"
        train = panel.loc[panel.index <= anchor_end].copy()
        year_months = [m for m in panel.index if f"{year}-01" <= m <= min(f"{year}-12", END)]
        future = panel.loc[year_months].copy()
        fit = fit_frozen(train)
        scored = score_sequence(fit, train, future)
        wanted = set(by_year[year])
        for row in scored:
            if row["month"] in wanted:
                row["detector"] = "ANNUAL_ANCHORED"
                row["anchor_end"] = anchor_end
                rows.append(row)
    rows.sort(key=lambda r: r["month"])
    return rows


def strict_2024_anchor_rows(panel: pd.DataFrame):
    train = panel.loc[panel.index <= "2024-12"].copy()
    future = panel.loc[(panel.index >= "2025-01") & (panel.index <= END)].copy()
    fit = fit_frozen(train)
    rows = score_sequence(fit, train, future)
    for row in rows:
        row["detector"] = "STRICT_2024_ANCHOR"
        row["anchor_end"] = "2024-12"
    return rows


def attach_reference(rows, ref):
    out = []
    for r in rows:
        rr = ref.loc[r["month"]]
        ref_label = str(rr["state"]) if float(rr["state_probability"]) >= CONFIDENCE else "BELIRSIZ"
        z = dict(r)
        z.update({
            "reference_state": str(rr["state"]),
            "reference_probability": float(rr["state_probability"]),
            "reference_label": ref_label,
            "reference_ood": bool(rr["ood_below_train_p05"]),
        })
        out.append(z)
    return out


def period_metrics(rows):
    if not rows:
        return {}

    n = len(rows)
    ref_conf = [r for r in rows if r["reference_label"] in R_STATES]
    decided = [r for r in ref_conf if r["label"] in R_STATES]

    confusion = {
        ref: {pred: 0 for pred in R_STATES + ["BELIRSIZ"]}
        for ref in R_STATES
    }
    for r in ref_conf:
        confusion[r["reference_label"]][r["label"]] += 1

    recalls = {}
    for ref_state in R_STATES:
        denom = sum(confusion[ref_state].values())
        recalls[ref_state] = None if denom == 0 else float(confusion[ref_state][ref_state] / denom)

    present = [x for x in recalls.values() if x is not None]
    pls = np.asarray([r["predictive_log_score"] for r in rows], float)

    return {
        "n_months": n,
        "mean_predictive_log_score": float(pls.mean()),
        "median_predictive_log_score": float(np.median(pls)),
        "total_predictive_log_score": float(pls.sum()),
        "belirsiz_rate": float(sum(r["label"] == "BELIRSIZ" for r in rows) / n),
        "ood_rate": float(sum(bool(r["ood"]) for r in rows) / n),
        "exact_reference_label_agreement": float(sum(r["label"] == r["reference_label"] for r in rows) / n),
        "reference_confident_months": int(len(ref_conf)),
        "strict_r_state_accuracy": None if not ref_conf else float(sum(r["label"] == r["reference_label"] for r in ref_conf) / len(ref_conf)),
        "decided_months": int(len(decided)),
        "decided_only_accuracy": None if not decided else float(sum(r["label"] == r["reference_label"] for r in decided) / len(decided)),
        "per_regime_recall": recalls,
        "balanced_accuracy_strict": None if not present else float(np.mean(present)),
        "confusion_matrix_ref_rows_detector_cols": confusion,
    }


def slice_rows(rows, start, end=END):
    return [r for r in rows if start <= r["month"] <= end]


def paired_score_summary(expanding, anchored, start, end=END):
    e = {r["month"]: r for r in expanding if start <= r["month"] <= end}
    a = {r["month"]: r for r in anchored if start <= r["month"] <= end}
    months = sorted(set(e) & set(a))
    diffs = np.asarray([a[m]["predictive_log_score"] - e[m]["predictive_log_score"] for m in months], float)
    return {
        "n_months": len(months),
        "mean_anchored_minus_expanding": float(diffs.mean()),
        "median_anchored_minus_expanding": float(np.median(diffs)),
        "total_anchored_minus_expanding": float(diffs.sum()),
        "anchored_better_months": int(np.sum(diffs > 0)),
        "expanding_better_months": int(np.sum(diffs < 0)),
        "ties": int(np.sum(diffs == 0)),
        "anchored_better_share": float(np.mean(diffs > 0)),
        "monthly_differences": [{"month": m, "anchored_minus_expanding": float(a[m]["predictive_log_score"] - e[m]["predictive_log_score"])} for m in months],
    }


def transition_delays(rows):
    out = []
    last_state = None
    last_conf_month = None
    for i, r in enumerate(rows):
        state = r["reference_label"]
        if state not in R_STATES:
            continue
        if last_state is None:
            last_state = state
            last_conf_month = r["month"]
            continue
        if state != last_state:
            tmonth = r["month"]
            found = None
            for cand in rows[i:]:
                if month_diff(tmonth, cand["month"]) > 6:
                    break
                if cand["label"] == state:
                    found = cand["month"]
                    break
            out.append({
                "reference_transition_month": tmonth,
                "previous_reference_state": last_state,
                "new_reference_state": state,
                "previous_confident_reference_month": last_conf_month,
                "detector_first_new_state_month": found,
                "delay_months": None if found is None else month_diff(tmonth, found),
                "censored_after_6m": bool(found is None),
            })
            last_state = state
        last_conf_month = r["month"]
    return out


def checkpoint_table(detectors):
    months = ["2024-03", "2024-04", "2024-05", "2024-06",
              "2026-04", "2026-05", "2026-06", "2026-07", "2026-08"]
    out = []
    for month in months:
        row = {"month": month}
        for name, rows in detectors.items():
            r = next((x for x in rows if x["month"] == month), None)
            if r is None:
                continue
            row[name] = {
                "label": r["label"],
                "state": r["state"],
                "probability": r["probability"],
                "ood": r["ood"],
                "predictive_log_score": r["predictive_log_score"],
                "train_end": r["train_end"],
            }
            row["reference"] = {
                "label": r["reference_label"],
                "state": r["reference_state"],
                "probability": r["reference_probability"],
                "ood": r["reference_ood"],
            }
        out.append(row)
    return out


def verify_expanding_against_prior(expanding, prior):
    prior_map = {r["month"]: r for r in prior["walkforward_months"]}
    mismatches = []
    max_prob_diff = 0.0
    for r in expanding:
        p = prior_map.get(r["month"])
        if p is None:
            mismatches.append({"month": r["month"], "issue": "missing_prior"})
            continue
        d = abs(float(r["probability"]) - float(p["live_probability"]))
        max_prob_diff = max(max_prob_diff, d)
        if r["label"] != p["live_label"] or r["state"] != p["live_state"] or d > 1e-6:
            mismatches.append({
                "month": r["month"],
                "new_state": r["state"], "prior_state": p["live_state"],
                "new_label": r["label"], "prior_label": p["live_label"],
                "probability_abs_diff": d,
            })
    return {
        "matched_months": len(expanding) - len(mismatches),
        "n_months": len(expanding),
        "max_probability_abs_diff": max_prob_diff,
        "mismatches": mismatches,
        "pass": len(mismatches) == 0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--regime-discovery-json", required=True)
    ap.add_argument("--prior-walkforward-json", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    src = load_json(args.regime_discovery_json)
    prior = load_json(args.prior_walkforward_json)

    if src.get("status") != "COMPLETE" or src.get("evidence", {}).get("selected_hmm_k") != 3:
        raise RuntimeError("INVALID_DISCOVERY_REFERENCE")
    if prior.get("status") != "COMPLETE":
        raise RuntimeError("INVALID_PRIOR_WALKFORWARD_REFERENCE")

    raw = pd.DataFrame(src["monthly_regimes"]).sort_values("month").reset_index(drop=True)
    missing = [c for c in FEATURES if c not in raw.columns]
    if missing:
        raise RuntimeError(("MISSING_FEATURES", missing))

    panel = raw[["month"] + FEATURES].copy().set_index("month")
    ref = raw[["month", "state", "state_probability", "ood_below_train_p05"]].copy().set_index("month")

    eval_months = [m for m in panel.index if EVAL_START <= m <= END]
    expanding = attach_reference(expanding_rows(panel, eval_months), ref)
    annual = attach_reference(annual_anchored_rows(panel, eval_months), ref)
    strict = attach_reference(strict_2024_anchor_rows(panel), ref)

    verify = verify_expanding_against_prior(expanding, prior)
    if not verify["pass"]:
        raise RuntimeError(("EXPANDING_REPRODUCTION_MISMATCH", verify))

    periods = {
        "full_replay_2015_07_2026_08": EVAL_START,
        "core_2022_01_2026_08": CORE_START,
        "transport_2025_01_2026_08": TRANSPORT_START,
    }

    metrics = {}
    paired = {}
    for pname, start in periods.items():
        metrics[pname] = {
            "EXPANDING_REFIT": period_metrics(slice_rows(expanding, start)),
            "ANNUAL_ANCHORED": period_metrics(slice_rows(annual, start)),
        }
        paired[pname] = paired_score_summary(expanding, annual, start)

    metrics["transport_2025_01_2026_08"]["STRICT_2024_ANCHOR"] = period_metrics(strict)

    strict_vs_exp = []
    e_transport = {r["month"]: r for r in slice_rows(expanding, TRANSPORT_START)}
    for r in strict:
        e = e_transport[r["month"]]
        strict_vs_exp.append(r["predictive_log_score"] - e["predictive_log_score"])
    strict_vs_exp = np.asarray(strict_vs_exp, float)
    paired["transport_strict2024_minus_expanding"] = {
        "n_months": int(len(strict_vs_exp)),
        "mean_strict_minus_expanding": float(strict_vs_exp.mean()),
        "median_strict_minus_expanding": float(np.median(strict_vs_exp)),
        "total_strict_minus_expanding": float(strict_vs_exp.sum()),
        "strict_better_months": int(np.sum(strict_vs_exp > 0)),
        "strict_better_share": float(np.mean(strict_vs_exp > 0)),
    }

    detectors = {
        "EXPANDING_REFIT": expanding,
        "ANNUAL_ANCHORED": annual,
    }
    key = checkpoint_table(detectors)

    transitions = {
        "EXPANDING_REFIT": transition_delays(expanding),
        "ANNUAL_ANCHORED": transition_delays(annual),
    }

    # Pre-registered interpretation checks. These are descriptive gates, not alarm authorization.
    core_pair = paired["core_2022_01_2026_08"]
    anchor_2024 = next((x for x in transitions["ANNUAL_ANCHORED"] if x["reference_transition_month"] == "2024-04"), None)
    exp_2026 = {r["month"]: r for r in expanding if "2026-05" <= r["month"] <= "2026-08"}
    ann_2026 = {r["month"]: r for r in annual if "2026-05" <= r["month"] <= "2026-08"}

    anchored_transition_improvement = bool(
        (ann_2026["2026-05"]["label"] == "BELIRSIZ" or ann_2026["2026-06"]["label"] == "BELIRSIZ" or
         (ann_2026["2026-07"]["label"] == "R1" and exp_2026["2026-07"]["label"] != "R1"))
    )
    preserves_2024 = bool(anchor_2024 is not None and anchor_2024["delay_months"] is not None and anchor_2024["delay_months"] <= 1)
    core_logscore_not_worse = bool(core_pair["mean_anchored_minus_expanding"] >= 0.0)

    candidate_supported = bool(core_logscore_not_worse and preserves_2024 and anchored_transition_improvement)

    result = {
        "schema": "GOLD_MONTHLY_MARKET_REGIME_ANCHORED_COMPARISON_V1_2026-09-30",
        "status": "COMPLETE",
        "scientific_gate": "PASS",
        "purpose": "regime-only anchored-vs-expanding detector comparison",
        "expanding_reproduction_check": verify,
        "metrics": metrics,
        "paired_predictive_log_score": paired,
        "transitions": transitions,
        "key_checkpoints": key,
        "decision_checks": {
            "core_mean_predictive_log_score_anchored_minus_expanding": core_pair["mean_anchored_minus_expanding"],
            "core_logscore_not_worse": core_logscore_not_worse,
            "annual_anchor_2024_R2_transition_delay_months": None if anchor_2024 is None else anchor_2024["delay_months"],
            "preserves_2024_transition_with_delay_le_1m": preserves_2024,
            "improves_2026_transition_behavior": anchored_transition_improvement,
            "annual_anchored_supported_as_next_candidate": candidate_supported,
        },
        "walkforward_rows": {
            "EXPANDING_REFIT": expanding,
            "ANNUAL_ANCHORED": annual,
            "STRICT_2024_ANCHOR_2025_2026": strict,
        },
        "governance": {
            "forecast_error_used": False,
            "alarm_labels_used": False,
            "model_forecasts_used": False,
            "router_outputs_used": False,
            "future_market_state_used_in_parameter_fit": False,
            "reference_labels_used_in_parameter_fit": False,
            "alarm_selection_tested": False,
            "alarm_weighting_tested": False,
            "forecast_correction_tested": False,
            "2025_2026_claimed_untouched": False,
        },
        "interpretation_guardrail": (
            "Reference-label agreement is secondary because reference labels are HMM-derived. "
            "Predictive log score is the primary non-circular comparison."
        ),
    }

    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")

    print("SCIENTIFIC_GATE=PASS")
    print(json.dumps({
        "expanding_reproduction_check": verify,
        "decision_checks": result["decision_checks"],
        "metrics": metrics,
        "paired_predictive_log_score": {k: {kk: vv for kk, vv in v.items() if kk != "monthly_differences"} for k, v in paired.items()},
        "key_checkpoints": key,
        "transitions_recent": {
            name: [x for x in vals if x["reference_transition_month"] >= "2022-01"]
            for name, vals in transitions.items()
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
