from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import gold_monthly_market_regime_discovery_v1 as base

EVAL_START = "2015-07"
CORE_START = "2022-01"
TRANSPORT_START = "2025-01"
END = "2026-08"
MIN_TRAIN_MONTHS = 60
CONFIDENCE = 0.60
OOD_Q = 0.05
K = 3
FEATURES = list(base.FEATURES)
R_STATES = ["R0", "R1", "R2"]


def load_json(path: str):
    return json.loads(Path(path).read_text())


def month_diff(a: str, b: str) -> int:
    pa = pd.Period(a, freq="M")
    pb = pd.Period(b, freq="M")
    return int(pb.ordinal - pa.ordinal)


def month_add(a: str, n: int) -> str:
    return str(pd.Period(a, freq="M") + n)


def weighted_canonical_map(posts: np.ndarray, train: pd.DataFrame):
    scores = []
    gold = train["Gold_r1"].to_numpy(float)
    vol = train["Gold_rv_ratio"].to_numpy(float)
    for s in range(posts.shape[1]):
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
    return {old: new for new, (_, _, old) in enumerate(scores)}


def canonical_map_training(posts: np.ndarray, train: pd.DataFrame):
    hard = posts.argmax(axis=1)
    if len(set(int(x) for x in hard)) == K:
        return base.canonical_map(hard, train), False
    return weighted_canonical_map(posts, train), True


def fit_one_origin(panel: pd.DataFrame, month: str):
    train = panel.loc[panel.index < month].copy()
    current = panel.loc[[month]].copy()
    if len(train) < MIN_TRAIN_MONTHS:
        raise RuntimeError(("INSUFFICIENT_TRAIN_HISTORY", month, len(train)))

    scaler = StandardScaler().fit(train[FEATURES].to_numpy(float))
    z_train = scaler.transform(train[FEATURES].to_numpy(float))
    z_cur = scaler.transform(current[FEATURES].to_numpy(float))

    pca_full = PCA().fit(z_train)
    cum = np.cumsum(pca_full.explained_variance_ratio_)
    npc = int(np.searchsorted(cum, 0.85) + 1)
    npc = max(2, min(6, npc))

    pca = PCA(n_components=npc, random_state=0).fit(z_train)
    x_train = pca.transform(z_train)
    x_cur = pca.transform(z_cur)

    (ll, seed, model), failures = base.fit_best_hmm(x_train, K)

    x_seq = np.vstack([x_train, x_cur])
    posts, loge = base.forward_filter(model, x_seq)
    train_posts = posts[:-1]
    cur_post = posts[-1]

    mapping, fallback = canonical_map_training(train_posts, train)
    raw_state = int(np.argmax(cur_post))
    state_id = int(mapping[raw_state])
    state = f"R{state_id}"
    confidence = float(cur_post[raw_state])
    label = state if confidence >= CONFIDENCE else "BELIRSIZ"

    train_max_emission = loge[:-1].max(axis=1)
    cur_max_emission = float(loge[-1].max())
    ood_threshold = float(np.quantile(train_max_emission, OOD_Q))
    ood = bool(cur_max_emission < ood_threshold)

    display = label
    if ood:
        if label == "BELIRSIZ":
            display = "BELIRSIZ / AŞIRI-OOD"
        else:
            display = f"{label}-AŞIRI/OOD"

    return {
        "month": month,
        "train_end": str(train.index[-1]),
        "train_rows": int(len(train)),
        "pca_components": int(npc),
        "pca_explained_variance": float(pca.explained_variance_ratio_.sum()),
        "hmm_k": K,
        "hmm_seed": int(seed),
        "hmm_train_loglik": float(ll),
        "hmm_fit_failure_count": int(len(failures)),
        "canonical_mapping": {str(k): int(v) for k, v in mapping.items()},
        "canonical_weighted_fallback": bool(fallback),
        "state": state,
        "state_id": state_id,
        "state_probability": confidence,
        "label": label,
        "ood": ood,
        "display_label": display,
        "max_emission_logdensity": cur_max_emission,
        "ood_threshold_train_p05": ood_threshold,
    }


def ref_label(row):
    return row["state"] if float(row["state_probability"]) >= CONFIDENCE else "BELIRSIZ"


def period_metrics(rows):
    if not rows:
        return {}
    n = len(rows)
    exact = sum(r["live_label"] == r["reference_label"] for r in rows)

    ref_conf = [r for r in rows if r["reference_label"] in R_STATES]
    strict_correct = sum(r["live_label"] == r["reference_label"] for r in ref_conf)

    decided = [r for r in ref_conf if r["live_label"] in R_STATES]
    decided_correct = sum(r["live_label"] == r["reference_label"] for r in decided)

    confusion = {
        ref: {pred: 0 for pred in R_STATES + ["BELIRSIZ"]}
        for ref in R_STATES
    }
    recalls = {}
    for r in ref_conf:
        confusion[r["reference_label"]][r["live_label"]] += 1

    for ref in R_STATES:
        denom = sum(confusion[ref].values())
        recalls[ref] = None if denom == 0 else float(confusion[ref][ref] / denom)

    present = [v for v in recalls.values() if v is not None]
    bal = None if not present else float(np.mean(present))

    return {
        "n_months": n,
        "reference_uncertain_rate": float(sum(r["reference_label"] == "BELIRSIZ" for r in rows) / n),
        "walkforward_uncertain_rate": float(sum(r["live_label"] == "BELIRSIZ" for r in rows) / n),
        "walkforward_ood_rate": float(sum(bool(r["live_ood"]) for r in rows) / n),
        "exact_label_agreement": float(exact / n),
        "reference_confident_months": int(len(ref_conf)),
        "strict_r_state_accuracy": None if not ref_conf else float(strict_correct / len(ref_conf)),
        "decided_months": int(len(decided)),
        "decided_only_accuracy": None if not decided else float(decided_correct / len(decided)),
        "per_regime_recall": recalls,
        "balanced_accuracy_strict": bal,
        "confusion_matrix_ref_rows_live_cols": confusion,
    }


def confident_reference_transitions(rows):
    out = []
    last_state = None
    last_conf_month = None
    for r in rows:
        state = r["reference_label"]
        if state not in R_STATES:
            continue
        if last_state is None:
            last_state = state
            last_conf_month = r["month"]
            continue
        if state != last_state:
            tmonth = r["month"]
            new_state = state
            found = None
            for cand in rows:
                if cand["month"] < tmonth:
                    continue
                d = month_diff(tmonth, cand["month"])
                if d > 6:
                    break
                if cand["live_label"] == new_state:
                    found = cand["month"]
                    break
            out.append({
                "reference_transition_month": tmonth,
                "previous_reference_state": last_state,
                "new_reference_state": new_state,
                "previous_confident_reference_month": last_conf_month,
                "walkforward_first_new_state_month": found,
                "delay_months": None if found is None else month_diff(tmonth, found),
                "censored_after_6m": bool(found is None),
            })
            last_state = state
        last_conf_month = r["month"]
    return out


def slice_rows(rows, start, end=END):
    return [r for r in rows if start <= r["month"] <= end]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--regime-discovery-json", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    src = load_json(args.regime_discovery_json)
    if src.get("status") != "COMPLETE":
        raise RuntimeError("REFERENCE_DISCOVERY_NOT_COMPLETE")
    if src.get("evidence", {}).get("selected_hmm_k") != 3:
        raise RuntimeError(("REFERENCE_K_NOT_3", src.get("evidence", {}).get("selected_hmm_k")))

    monthly = src["monthly_regimes"]
    raw = pd.DataFrame(monthly).copy()
    if list(raw["month"]) != sorted(raw["month"].tolist()):
        raw = raw.sort_values("month").reset_index(drop=True)

    missing = [c for c in FEATURES if c not in raw.columns]
    if missing:
        raise RuntimeError(("MISSING_MARKET_STATE_FEATURES", missing))

    # Critical governance boundary: detector panel is rebuilt from month + market-state features only.
    # Reference state/probability/OOD columns are retained separately and are not present in fit_one_origin().
    panel = raw[["month"] + FEATURES].copy().set_index("month")
    ref = raw[["month", "state", "state_probability", "ood_below_train_p05"]].copy().set_index("month")

    if panel.index.min() > "2010-07" or panel.index.max() < END:
        raise RuntimeError(("REFERENCE_PANEL_COVERAGE", str(panel.index.min()), str(panel.index.max())))

    eval_months = [m for m in panel.index if EVAL_START <= m <= END]
    if not eval_months or eval_months[0] != EVAL_START or eval_months[-1] != END:
        raise RuntimeError(("EVAL_COVERAGE", eval_months[:1], eval_months[-1:]))

    live_rows = []
    for month in eval_months:
        live = fit_one_origin(panel, month)
        rr = ref.loc[month]
        reference_label = rr["state"] if float(rr["state_probability"]) >= CONFIDENCE else "BELIRSIZ"
        live_rows.append({
            "month": month,
            "reference_state": str(rr["state"]),
            "reference_probability": float(rr["state_probability"]),
            "reference_label": reference_label,
            "reference_ood": bool(rr["ood_below_train_p05"]),
            "live_state": live["state"],
            "live_probability": live["state_probability"],
            "live_label": live["label"],
            "live_ood": live["ood"],
            "live_display_label": live["display_label"],
            "train_end": live["train_end"],
            "train_rows": live["train_rows"],
            "pca_components": live["pca_components"],
            "pca_explained_variance": live["pca_explained_variance"],
            "hmm_seed": live["hmm_seed"],
            "hmm_train_loglik": live["hmm_train_loglik"],
            "hmm_fit_failure_count": live["hmm_fit_failure_count"],
            "canonical_mapping": live["canonical_mapping"],
            "canonical_weighted_fallback": live["canonical_weighted_fallback"],
            "max_emission_logdensity": live["max_emission_logdensity"],
            "ood_threshold_train_p05": live["ood_threshold_train_p05"],
        })

    full = slice_rows(live_rows, EVAL_START)
    core = slice_rows(live_rows, CORE_START)
    transport = slice_rows(live_rows, TRANSPORT_START)

    transitions = confident_reference_transitions(full)

    key_months = [
        "2024-03", "2024-04", "2024-05", "2024-06",
        "2026-04", "2026-05", "2026-06", "2026-07", "2026-08",
    ]
    key = [r for r in live_rows if r["month"] in key_months]

    t_202404 = next((x for x in transitions if x["reference_transition_month"] == "2024-04"), None)
    transition_zone = [r for r in live_rows if r["month"] in ("2026-05", "2026-06")]
    r1_stable = [r for r in live_rows if r["month"] in ("2026-07", "2026-08")]

    result = {
        "schema": "GOLD_MONTHLY_MARKET_REGIME_WALKFORWARD_V1_2026-09-30",
        "status": "COMPLETE",
        "scientific_gate": "PASS",
        "purpose": "current-regime real-time detection audit; not next-month regime forecasting",
        "authority": {
            "reference_run": 36716979693,
            "reference_artifact": 11097041821,
            "reference_schema": src.get("schema"),
            "reference_selected_hmm_k": src.get("evidence", {}).get("selected_hmm_k"),
        },
        "design": {
            "effective_panel_start": str(panel.index.min()),
            "eval_start": EVAL_START,
            "core_start": CORE_START,
            "transport_start": TRANSPORT_START,
            "end": END,
            "min_prior_train_months": MIN_TRAIN_MONTHS,
            "fit_window": "expanding; strictly through t-1",
            "current_month_used_in_parameter_fit": False,
            "hmm_k": K,
            "confidence_threshold": CONFIDENCE,
            "ood_training_quantile": OOD_Q,
            "pca_variance_target": 0.85,
            "pca_min_components": 2,
            "pca_max_components": 6,
            "features": FEATURES,
        },
        "metrics": {
            "full_replay_2015_07_2026_08": period_metrics(full),
            "core_2022_01_2026_08": period_metrics(core),
            "transport_2025_01_2026_08": period_metrics(transport),
        },
        "transitions": transitions,
        "key_checkpoints": key,
        "checkpoint_summary": {
            "2024_04_reference_transition": t_202404,
            "2026_05_06_any_live_uncertain": bool(any(r["live_label"] == "BELIRSIZ" for r in transition_zone)),
            "2026_05_06_live_labels": {r["month"]: r["live_display_label"] for r in transition_zone},
            "2026_07_08_live_labels": {r["month"]: r["live_display_label"] for r in r1_stable},
            "2026_07_08_both_live_r1": bool(len(r1_stable) == 2 and all(r["live_label"] == "R1" for r in r1_stable)),
        },
        "walkforward_months": live_rows,
        "governance": {
            "forecast_error_used": False,
            "alarm_labels_used": False,
            "model_forecasts_used": False,
            "router_outputs_used": False,
            "future_market_state_used_in_fit": False,
            "reference_labels_used_in_fit": False,
            "current_month_used_in_fit": False,
            "alarm_selection_tested": False,
            "alarm_weighting_tested": False,
            "forecast_correction_tested": False,
        },
        "interpretation_note": (
            "2015-07..2024-12 is retrospective replay of the K=3 architecture. "
            "2025-01..2026-08 is the cleanest frozen-architecture transport interval."
        ),
    }

    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")

    print("SCIENTIFIC_GATE=PASS")
    print(json.dumps({
        "metrics": result["metrics"],
        "checkpoint_summary": result["checkpoint_summary"],
        "key_checkpoints": result["key_checkpoints"],
        "transitions": result["transitions"],
        "weighted_mapping_fallback_months": [
            r["month"] for r in live_rows if r["canonical_weighted_fallback"]
        ],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
