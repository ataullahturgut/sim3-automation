from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
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


def old_canonical_map(posts: np.ndarray, train: pd.DataFrame):
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


def build_frozen_prototypes(raw: pd.DataFrame):
    dev = raw.loc[raw["month"] <= "2024-12"].copy()
    x = dev[FEATURES].to_numpy(float)
    mu = x.mean(axis=0)
    sd = x.std(axis=0, ddof=0)
    sd = np.where(sd <= 1e-12, 1.0, sd)

    prototypes = {}
    raw_means = {}
    for i, label in enumerate(R_STATES):
        sub = dev.loc[dev["state"] == label, FEATURES]
        if sub.empty:
            raise RuntimeError(("EMPTY_REFERENCE_PROTOTYPE", label))
        m = sub.to_numpy(float).mean(axis=0)
        raw_means[label] = {f: float(v) for f, v in zip(FEATURES, m)}
        prototypes[label] = (m - mu) / sd

    return {
        "mu": mu,
        "sd": sd,
        "prototype_vectors": prototypes,
        "raw_means": raw_means,
        "n_dev": int(len(dev)),
        "period": [str(dev["month"].min()), str(dev["month"].max())],
    }


def prototype_map(posts: np.ndarray, train: pd.DataFrame, proto):
    x = train[FEATURES].to_numpy(float)
    state_profiles = []
    raw_profiles = []

    for s in range(K):
        w = posts[:, s].astype(float)
        den = float(w.sum())
        if den <= 1e-12:
            raise RuntimeError(("ZERO_POSTERIOR_MASS_STATE", s, len(train)))
        m = np.sum(w[:, None] * x, axis=0) / den
        raw_profiles.append(m)
        state_profiles.append((m - proto["mu"]) / proto["sd"])

    state_profiles = np.asarray(state_profiles, float)
    ref_profiles = np.asarray([proto["prototype_vectors"][r] for r in R_STATES], float)
    cost = np.sqrt(((state_profiles[:, None, :] - ref_profiles[None, :, :]) ** 2).sum(axis=2))

    rows, cols = linear_sum_assignment(cost)
    mapping = {int(r): int(c) for r, c in zip(rows, cols)}
    total_cost = float(sum(cost[r, c] for r, c in zip(rows, cols)))

    detail = {
        "distance_matrix": {
            str(s): {R_STATES[j]: float(cost[s, j]) for j in range(K)}
            for s in range(K)
        },
        "assignment": {str(s): R_STATES[mapping[s]] for s in range(K)},
        "total_assignment_cost": total_cost,
        "latent_raw_profiles": {
            str(s): {f: float(v) for f, v in zip(FEATURES, raw_profiles[s])}
            for s in range(K)
        },
    }
    return mapping, detail


def fit_frozen(train: pd.DataFrame, proto):
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

    old_map, old_fallback = old_canonical_map(train_posts, train)
    proto_map, proto_detail = prototype_map(train_posts, train, proto)

    train_max_emission = train_loge.max(axis=1)
    ood_threshold = float(np.quantile(train_max_emission, OOD_Q))

    return {
        "scaler": scaler,
        "pca": pca,
        "model": model,
        "old_mapping": old_map,
        "old_mapping_fallback": old_fallback,
        "prototype_mapping": proto_map,
        "prototype_detail": proto_detail,
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
    z_future = fit["scaler"].transform(future[FEATURES].to_numpy(float))
    x_future = fit["pca"].transform(z_future)
    x_all = np.vstack([fit["x_train"], x_future])

    posts, loge = base.forward_filter(fit["model"], x_all)
    ntrain = len(train)
    out = []

    for j, month in enumerate(future.index):
        i = ntrain + j
        prev = posts[i - 1]
        prior = prev @ np.asarray(fit["model"].transmat_, float)
        logpred = float(logsumexp(np.log(np.maximum(prior, 1e-300)) + loge[i]))

        raw_state = int(np.argmax(posts[i]))
        prob = float(posts[i, raw_state])

        old_id = int(fit["old_mapping"][raw_state])
        proto_id = int(fit["prototype_mapping"][raw_state])
        old_state = f"R{old_id}"
        proto_state = f"R{proto_id}"

        old_label = old_state if prob >= CONFIDENCE else "BELIRSIZ"
        proto_label = proto_state if prob >= CONFIDENCE else "BELIRSIZ"

        max_em = float(loge[i].max())
        ood = bool(max_em < fit["ood_threshold"])

        out.append({
            "month": str(month),
            "raw_state_id": raw_state,
            "probability": prob,
            "old_state": old_state,
            "old_label": old_label,
            "prototype_state": proto_state,
            "prototype_label": proto_label,
            "semantic_state_changed": bool(old_state != proto_state),
            "output_label_changed": bool(old_label != proto_label),
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
            "old_mapping": {str(k): int(v) for k, v in fit["old_mapping"].items()},
            "prototype_mapping": {str(k): int(v) for k, v in fit["prototype_mapping"].items()},
            "prototype_alignment": fit["prototype_detail"],
        })

    return out


def expanding_rows(panel: pd.DataFrame, months: list[str], proto):
    rows = []
    for month in months:
        train = panel.loc[panel.index < month].copy()
        cur = panel.loc[[month]].copy()
        fit = fit_frozen(train, proto)
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
        fit = fit_frozen(train, proto)
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


def metrics(rows, label_field):
    if not rows:
        return {}

    n = len(rows)
    ref_conf = [r for r in rows if r["reference_label"] in R_STATES]
    decided = [r for r in ref_conf if r[label_field] in R_STATES]

    confusion = {
        ref: {pred: 0 for pred in R_STATES + ["BELIRSIZ"]}
        for ref in R_STATES
    }
    for r in ref_conf:
        confusion[r["reference_label"]][r[label_field]] += 1

    recalls = {}
    for rs in R_STATES:
        den = sum(confusion[rs].values())
        recalls[rs] = None if den == 0 else float(confusion[rs][rs] / den)

    vals = [v for v in recalls.values() if v is not None]

    return {
        "n_months": n,
        "exact_reference_label_agreement": float(sum(r[label_field] == r["reference_label"] for r in rows) / n),
        "reference_confident_months": int(len(ref_conf)),
        "strict_r_state_accuracy": None if not ref_conf else float(sum(r[label_field] == r["reference_label"] for r in ref_conf) / len(ref_conf)),
        "decided_months": int(len(decided)),
        "decided_only_accuracy": None if not decided else float(sum(r[label_field] == r["reference_label"] for r in decided) / len(decided)),
        "per_regime_recall": recalls,
        "balanced_accuracy_strict": None if not vals else float(np.mean(vals)),
        "confusion_matrix_ref_rows_detector_cols": confusion,
    }


def semantic_change_summary(rows):
    n = len(rows)
    return {
        "n_months": n,
        "semantic_state_changed_months": int(sum(r["semantic_state_changed"] for r in rows)),
        "semantic_state_changed_share": float(sum(r["semantic_state_changed"] for r in rows) / n),
        "output_label_changed_months": int(sum(r["output_label_changed"] for r in rows)),
        "output_label_changed_share": float(sum(r["output_label_changed"] for r in rows) / n),
        "changed_months": [
            {
                "month": r["month"],
                "old_state": r["old_state"],
                "prototype_state": r["prototype_state"],
                "probability": r["probability"],
                "old_label": r["old_label"],
                "prototype_label": r["prototype_label"],
            }
            for r in rows if r["semantic_state_changed"]
        ],
    }


def slice_rows(rows, start, end=END):
    return [r for r in rows if start <= r["month"] <= end]


def transition_delays(rows, label_field):
    out = []
    last_state = None
    last_conf_month = None

    for i, r in enumerate(rows):
        ref_state = r["reference_label"]
        if ref_state not in R_STATES:
            continue
        if last_state is None:
            last_state = ref_state
            last_conf_month = r["month"]
            continue

        if ref_state != last_state:
            tmonth = r["month"]
            found = None
            for cand in rows[i:]:
                if month_diff(tmonth, cand["month"]) > 6:
                    break
                if cand[label_field] == ref_state:
                    found = cand["month"]
                    break
            out.append({
                "reference_transition_month": tmonth,
                "previous_reference_state": last_state,
                "new_reference_state": ref_state,
                "previous_confident_reference_month": last_conf_month,
                "detector_first_new_state_month": found,
                "delay_months": None if found is None else month_diff(tmonth, found),
                "censored_after_6m": bool(found is None),
            })
            last_state = ref_state

        last_conf_month = r["month"]

    return out


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
        dp = abs(float(r["probability"]) - float(p["probability"]))
        ds = abs(float(r["predictive_log_score"]) - float(p["predictive_log_score"]))
        max_prob = max(max_prob, dp)
        max_score = max(max_score, ds)
        if dp > 1e-6 or ds > 1e-6 or r["old_state"] != p["state"] or r["old_label"] != p["label"]:
            problems.append({
                "month": r["month"],
                "prob_diff": dp,
                "score_diff": ds,
                "old_state": r["old_state"],
                "prior_state": p["state"],
                "old_label": r["old_label"],
                "prior_label": p["label"],
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
                "old_state": r["old_state"],
                "old_label": r["old_label"],
                "prototype_state": r["prototype_state"],
                "prototype_label": r["prototype_label"],
                "probability": r["probability"],
                "semantic_state_changed": r["semantic_state_changed"],
                "predictive_log_score": r["predictive_log_score"],
                "ood": r["ood"],
                "train_end": r["train_end"],
                "prototype_assignment": r["prototype_alignment"]["assignment"],
                "prototype_distance_matrix": r["prototype_alignment"]["distance_matrix"],
            }
            row["reference"] = {
                "state": r["reference_state"],
                "label": r["reference_label"],
                "probability": r["reference_probability"],
                "ood": r["reference_ood"],
            }
        out.append(row)

    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--regime-discovery-json", required=True)
    ap.add_argument("--prior-comparison-json", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    src = load_json(args.regime_discovery_json)
    prior = load_json(args.prior_comparison_json)

    if src.get("status") != "COMPLETE" or src.get("evidence", {}).get("selected_hmm_k") != 3:
        raise RuntimeError("INVALID_DISCOVERY_REFERENCE")
    if prior.get("status") != "COMPLETE":
        raise RuntimeError("INVALID_PRIOR_COMPARISON")

    raw = pd.DataFrame(src["monthly_regimes"]).sort_values("month").reset_index(drop=True)
    missing = [c for c in FEATURES if c not in raw.columns]
    if missing:
        raise RuntimeError(("MISSING_FEATURES", missing))

    proto = build_frozen_prototypes(raw)

    panel = raw[["month"] + FEATURES].copy().set_index("month")
    ref = raw[["month", "state", "state_probability", "ood_below_train_p05"]].copy().set_index("month")
    eval_months = [m for m in panel.index if EVAL_START <= m <= END]

    expanding = attach_reference(expanding_rows(panel, eval_months, proto), ref)
    annual = attach_reference(annual_rows(panel, eval_months, proto), ref)

    prior_exp = prior["walkforward_rows"]["EXPANDING_REFIT"]
    prior_ann = prior["walkforward_rows"]["ANNUAL_ANCHORED"]
    verify_exp = verify_against_prior(expanding, prior_exp, "EXPANDING_REFIT")
    verify_ann = verify_against_prior(annual, prior_ann, "ANNUAL_ANCHORED")

    if not verify_exp["pass"] or not verify_ann["pass"]:
        raise RuntimeError(("UNDERLYING_FIT_REPRODUCTION_FAILED", verify_exp, verify_ann))

    periods = {
        "full_replay_2015_07_2026_08": EVAL_START,
        "core_2022_01_2026_08": CORE_START,
        "transport_2025_01_2026_08": TRANSPORT_START,
    }

    period_results = {}
    for pname, start in periods.items():
        er = slice_rows(expanding, start)
        ar = slice_rows(annual, start)
        period_results[pname] = {
            "EXPANDING_REFIT": {
                "old_gold_r1_mapping": metrics(er, "old_label"),
                "prototype_alignment": metrics(er, "prototype_label"),
                "semantic_changes": semantic_change_summary(er),
            },
            "ANNUAL_ANCHORED": {
                "old_gold_r1_mapping": metrics(ar, "old_label"),
                "prototype_alignment": metrics(ar, "prototype_label"),
                "semantic_changes": semantic_change_summary(ar),
            },
        }

    checkpoints = checkpoint_table(expanding, annual)

    transitions = {
        "EXPANDING_REFIT": {
            "old": transition_delays(expanding, "old_label"),
            "prototype": transition_delays(expanding, "prototype_label"),
        },
        "ANNUAL_ANCHORED": {
            "old": transition_delays(annual, "old_label"),
            "prototype": transition_delays(annual, "prototype_label"),
        },
    }

    result = {
        "schema": "GOLD_MONTHLY_MARKET_REGIME_PROTOTYPE_ALIGNMENT_V1_2026-09-30",
        "status": "COMPLETE",
        "scientific_gate": "PASS",
        "purpose": "semantic latent-state alignment only; underlying density models unchanged",
        "frozen_prototype_definition": {
            "period": proto["period"],
            "n_months": proto["n_dev"],
            "features": FEATURES,
            "reference_regime_raw_means": proto["raw_means"],
            "standardization_mean": {f: float(v) for f, v in zip(FEATURES, proto["mu"])},
            "standardization_sd": {f: float(v) for f, v in zip(FEATURES, proto["sd"])},
            "standardized_prototypes": {
                r: {f: float(v) for f, v in zip(FEATURES, proto["prototype_vectors"][r])}
                for r in R_STATES
            },
            "distance": "Euclidean across all 13 frozen-standardized features",
            "assignment": "Hungarian one-to-one minimum total distance",
            "latent_profile": "filtered-posterior-weighted mean over own training history",
        },
        "underlying_fit_reproduction": {
            "EXPANDING_REFIT": verify_exp,
            "ANNUAL_ANCHORED": verify_ann,
            "predictive_log_score_changed_by_alignment": False,
        },
        "period_results": period_results,
        "transitions": transitions,
        "key_checkpoints": checkpoints,
        "rows": {
            "EXPANDING_REFIT": expanding,
            "ANNUAL_ANCHORED": annual,
        },
        "governance": {
            "forecast_error_used": False,
            "alarm_labels_used": False,
            "model_forecasts_used": False,
            "router_outputs_used": False,
            "prototype_reference_period_ends_2024_12": True,
            "prototype_used_only_for_semantic_mapping": True,
            "hmm_parameters_changed_by_alignment": False,
            "posterior_probabilities_changed_by_alignment": False,
            "predictive_log_score_changed_by_alignment": False,
            "alarm_selection_tested": False,
            "alarm_weighting_tested": False,
            "forecast_correction_tested": False,
            "2015_2024_replay_is_retrospective_only": True,
            "2025_2026_claimed_untouched": False,
        },
    }

    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")

    def compact_period(pname):
        z = period_results[pname]
        return {
            det: {
                "old": z[det]["old_gold_r1_mapping"],
                "prototype": z[det]["prototype_alignment"],
                "semantic_changes": {k: v for k, v in z[det]["semantic_changes"].items() if k != "changed_months"},
            }
            for det in z
        }

    print("SCIENTIFIC_GATE=PASS")
    print(json.dumps({
        "underlying_fit_reproduction": result["underlying_fit_reproduction"],
        "core": compact_period("core_2022_01_2026_08"),
        "transport": compact_period("transport_2025_01_2026_08"),
        "key_checkpoints": checkpoints,
        "transitions_recent": {
            det: {
                k: [x for x in vals if x["reference_transition_month"] >= "2022-01"]
                for k, vals in maps.items()
            }
            for det, maps in transitions.items()
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
