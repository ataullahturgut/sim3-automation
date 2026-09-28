#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np

import vw_midas_msvr_successor_v1 as base
import gold_monthly_boosting_ensemble_e1_baselines_v1 as e1
import gold_monthly_boosting_ensemble_e2_simplex_v1 as e2

DEV_START, DEV_END = "2022-04", "2024-12"
ALPHAS = [0.00, 0.10, 0.25, 0.50, 0.75, 1.00]

POOLS = {
    "FULL5": ["CATBOOST_PRICE", "CATBOOST_BALANCED", "GBRT", "LIGHTGBM", "XGB_DIRECTION"],
    "REDUCED4": ["CATBOOST_PRICE", "GBRT", "LIGHTGBM", "XGB_DIRECTION"],
}

REFS = {
    "CATBOOST_PRICE": {"sum_abs_error": 1460.433935309605, "direction_correct": 20},
    "FULL5": {
        "median_sum_abs_error": 1484.731330609916,
        "median_direction_correct": 23,
        "equal_sum_abs_error": 1503.458115374356,
        "equal_direction_correct": 21,
        "e2_raw_sum_abs_error": 1532.4585226357096,
        "e2_raw_direction_correct": 19,
    },
    "REDUCED4": {
        "median_sum_abs_error": 1490.6522619575326,
        "median_direction_correct": 22,
        "equal_sum_abs_error": 1512.863860829353,
        "equal_direction_correct": 20,
        "e2_raw_sum_abs_error": 1524.257954917245,
        "e2_raw_direction_correct": 18,
    },
}

TOL = 1e-8


def alpha_key(alpha: float) -> str:
    return f"{alpha:.2f}"


def rank_key(item: dict):
    m = item["metrics"]
    return (
        float(m["sum_abs_error"]),
        -int(m["direction_correct"]),
        float(m["rmse"]),
        float(item["alpha"]),
    )


def build_rows(targets, P, actual, rw, names, simplex_history, alpha):
    equal = e1.equal_weights(len(names))
    preds = []
    rows = []
    for i, target in enumerate(targets):
        ws = np.array([simplex_history[i]["weights"][n] for n in names], dtype=float)
        w = (1.0 - alpha) * equal + alpha * ws
        w = np.clip(w, 0.0, 1.0)
        w = w / float(w.sum())
        pred = float(P[i] @ w)
        preds.append(pred)
        rows.append(
            {
                "target": target,
                "forecast": pred,
                "actual": float(actual[i]),
                "rw": float(rw[i]),
                "absolute_error": float(abs(pred - actual[i])),
                "direction_correct": bool(
                    int(np.sign(pred - rw[i])) == int(np.sign(actual[i] - rw[i]))
                ),
                "trained_on_prior_dev_origins": int(
                    simplex_history[i]["trained_on_prior_dev_origins"]
                ),
                "simplex_fallback_equal": bool(simplex_history[i]["fallback_equal"]),
                "weights": {n: float(x) for n, x in zip(names, w)},
            }
        )
    return np.asarray(preds, dtype=float), rows


def evaluate_pool(components, pool, names):
    targets, P, actual, rw = e1.matrix(components, names)
    if targets[0] != DEV_START or targets[-1] != DEV_END or len(targets) != 33:
        raise RuntimeError(f"DEV_SCOPE_FAIL {pool}")

    equal_pred = P @ e1.equal_weights(len(names))
    equal_metrics = e1.metrics(equal_pred, actual, rw, targets)
    median_pred = np.median(P, axis=1)
    median_metrics = e1.metrics(median_pred, actual, rw, targets)

    ref = REFS[pool]
    if abs(equal_metrics["sum_abs_error"] - ref["equal_sum_abs_error"]) > TOL:
        raise RuntimeError(f"E1_EQUAL_AE_REPRO_FAIL {pool}")
    if equal_metrics["direction_correct"] != ref["equal_direction_correct"]:
        raise RuntimeError(f"E1_EQUAL_DIR_REPRO_FAIL {pool}")
    if abs(median_metrics["sum_abs_error"] - ref["median_sum_abs_error"]) > TOL:
        raise RuntimeError(f"E1_MEDIAN_AE_REPRO_FAIL {pool}")
    if median_metrics["direction_correct"] != ref["median_direction_correct"]:
        raise RuntimeError(f"E1_MEDIAN_DIR_REPRO_FAIL {pool}")

    raw_pred, simplex_history = e2.prequential_simplex(P, actual, names)
    raw_metrics = e1.metrics(raw_pred, actual, rw, targets)
    if abs(raw_metrics["sum_abs_error"] - ref["e2_raw_sum_abs_error"]) > TOL:
        raise RuntimeError(f"E2_RAW_AE_REPRO_FAIL {pool}")
    if raw_metrics["direction_correct"] != ref["e2_raw_direction_correct"]:
        raise RuntimeError(f"E2_RAW_DIR_REPRO_FAIL {pool}")

    variants = {}
    for alpha in ALPHAS:
        pred, variant_rows = build_rows(
            targets, P, actual, rw, names, simplex_history, alpha
        )
        m = e1.metrics(pred, actual, rw, targets)
        variants[alpha_key(alpha)] = {
            "alpha": float(alpha),
            "metrics": m,
            "rows": variant_rows,
            "delta_sigma_ae_vs_e1_median": float(
                m["sum_abs_error"] - ref["median_sum_abs_error"]
            ),
            "beats_e1_median": bool(
                m["sum_abs_error"] < ref["median_sum_abs_error"] - TOL
            ),
        }

    v0 = variants["0.00"]["metrics"]
    v1 = variants["1.00"]["metrics"]
    if abs(v0["sum_abs_error"] - ref["equal_sum_abs_error"]) > TOL:
        raise RuntimeError(f"ALPHA0_IDENTITY_FAIL {pool}")
    if abs(v1["sum_abs_error"] - ref["e2_raw_sum_abs_error"]) > TOL:
        raise RuntimeError(f"ALPHA1_IDENTITY_FAIL {pool}")

    ranking = sorted(variants.values(), key=rank_key)
    learned_ranking = sorted(
        [v for v in variants.values() if v["alpha"] > 0.0], key=rank_key
    )
    best_overall = ranking[0]
    best_learned = learned_ranking[0]
    promoted = bool(
        best_learned["metrics"]["sum_abs_error"]
        < ref["median_sum_abs_error"] - TOL
    )

    decision = (
        "PROMOTED_LEARNED_SHRINKAGE"
        if promoted
        else "LEARNED_WEIGHTS_CLOSED_NOT_PROMOTED"
    )

    return {
        "pool": pool,
        "components": names,
        "references": {
            "e1_equal": equal_metrics,
            "e1_median": median_metrics,
            "e2_raw_simplex": raw_metrics,
        },
        "variants": variants,
        "ranking": [
            {
                "alpha": v["alpha"],
                "sum_abs_error": v["metrics"]["sum_abs_error"],
                "direction_correct": v["metrics"]["direction_correct"],
                "rmse": v["metrics"]["rmse"],
                "delta_sigma_ae_vs_e1_median": v["delta_sigma_ae_vs_e1_median"],
                "beats_e1_median": v["beats_e1_median"],
            }
            for v in ranking
        ],
        "best_overall_alpha": best_overall["alpha"],
        "best_learned_alpha": best_learned["alpha"],
        "best_learned_metrics": best_learned["metrics"],
        "learned_shrinkage_promoted": promoted,
        "decision": decision,
    }


def render_report(payload):
    lines = [
        "# GOLD MONTHLY FORECAST — BOOSTING ENSEMBLE E3 CONTROLLED SHRINKAGE RESULT",
        "",
        "Date: 2026-09-28",
        "Status: COMPLETE / SCIENTIFIC GATE PASS",
        "",
        "## Frozen protocol",
        "- Pools: FULL5 and REDUCED4 only.",
        "- Shrinkage: w_alpha(t) = (1-alpha) * w_equal + alpha * w_simplex(t).",
        "- Alpha grid: 0.00, 0.10, 0.25, 0.50, 0.75, 1.00.",
        "- E2 simplex weights remain expanding-prequential and prior-only.",
        "- E1 MEDIAN remains a separate frozen comparator.",
        "- 2025 NOT OPENED.",
        "- 2026 QUARANTINED / NOT USED.",
        "- DB READ_ONLY.",
        "",
        "## Results",
        "",
    ]
    for pool in ("FULL5", "REDUCED4"):
        r = payload["results"][pool]
        lines += [
            f"### {pool}",
            "",
            "| Alpha | SigmaAE | Direction | Delta vs E1 Median | Beats Median |",
            "|---:|---:|---:|---:|---|",
        ]
        for z in r["ranking"]:
            lines.append(
                f"| {z['alpha']:.2f} | {z['sum_abs_error']:.6f} | "
                f"{z['direction_correct']}/33 | {z['delta_sigma_ae_vs_e1_median']:+.6f} | "
                f"{'YES' if z['beats_e1_median'] else 'NO'} |"
            )
        bm = r["best_learned_metrics"]
        lines += [
            "",
            f"- Best learned alpha: **{r['best_learned_alpha']:.2f}**",
            f"- Best learned SigmaAE: **{bm['sum_abs_error']:.6f}**",
            f"- Best learned direction: **{bm['direction_correct']}/33**",
            f"- Decision: **{r['decision']}**",
            "",
        ]

    lines += [
        "## Family status after E3",
        "",
        f"- CATBOOST_PRICE reference: {REFS['CATBOOST_PRICE']['sum_abs_error']:.6f} / {REFS['CATBOOST_PRICE']['direction_correct']}/33.",
        f"- FULL5 MEDIAN reference: {REFS['FULL5']['median_sum_abs_error']:.6f} / {REFS['FULL5']['median_direction_correct']}/33.",
        "",
    ]

    any_promoted = any(
        payload["results"][p]["learned_shrinkage_promoted"]
        for p in ("FULL5", "REDUCED4")
    )
    if any_promoted:
        lines += [
            "At least one learned shrinkage candidate beats its frozen E1 median comparator on the primary DEV SigmaAE metric. Carry the promoted candidate into final robustness together with the family reference models.",
            "",
        ]
    else:
        lines += [
            "No learned shrinkage candidate beats its frozen E1 median comparator on DEV SigmaAE. Learned-weight ensemble optimization is therefore closed. Proceed to final Boosting robustness with CATBOOST_PRICE and E1 FULL5 MEDIAN as the principal challengers.",
            "",
        ]

    lines += [
        "## Reproducibility",
        f"- Payload SHA256: {payload['payload_sha256']}",
        "",
        "## Kontrol ve Uyum Özeti",
        "- E3 freeze respected: PASS.",
        "- Frozen alpha grid unchanged: PASS.",
        "- Alpha=0 identity to E1 equal: PASS.",
        "- Alpha=1 identity to E2 raw simplex: PASS.",
        "- Component metrics exact reconciliation: PASS.",
        "- 2025 opened: NO.",
        "- 2026 used: NO.",
        "- Random split: NONE.",
        "- DB mutation: NONE / READ_ONLY.",
        "",
    ]
    return "\n".join(lines)


def main():
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    bundle = base.load_data(dsn)
    targets, components = e1.read_components(bundle)
    if targets[0] != DEV_START or targets[-1] != DEV_END or len(targets) != 33:
        raise RuntimeError("DEV_TARGET_SCOPE_FAIL")

    results = {
        pool: evaluate_pool(components, pool, names)
        for pool, names in POOLS.items()
    }

    after = e1.s5.read_invariants(dsn)
    if after != bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    compact = {
        pool: {
            "ranking": results[pool]["ranking"],
            "forecasts": {
                key: [row["forecast"] for row in v["rows"]]
                for key, v in results[pool]["variants"].items()
            },
        }
        for pool in results
    }
    digest = hashlib.sha256(
        json.dumps(compact, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    payload = {
        "scope": "BOOSTING_ENSEMBLE_E3_CONTROLLED_SHRINKAGE_V1",
        "freeze_file": "GOLD_MONTHLY_BOOSTING_ENSEMBLE_E3_SHRINKAGE_FREEZE_2026-09-28.md",
        "contract": {
            "dev": f"{DEV_START}..{DEV_END}",
            "dev_n": 33,
            "alpha_grid": ALPHAS,
            "shrinkage_target": "EQUAL_WEIGHTS",
            "median_role": "SEPARATE_FROZEN_COMPARATOR",
            "simplex_state": "E2_PRIOR_ONLY_EXPANDING_PREQUENTIAL_UNCHANGED",
            "minimum_prior_dev_origins": e2.MIN_META_HISTORY,
            "subset_search": "NONE",
            "stacking": "NONE",
            "random_split": "NONE",
            "database": "READ_ONLY",
            "2025_role": "NOT_OPENED_NOT_EVALUATED",
            "2026_role": "QUARANTINED_NOT_USED",
            "primary_metric": "DEV_PRICE_SUM_ABS_ERROR",
            "promotion_rule": "BEST_ALPHA_GT_0_MUST_BEAT_POOL_E1_MEDIAN_SIGMA_AE",
        },
        "results": results,
        "authority_invariants_before": bundle.invariants_before,
        "authority_invariants_after": after,
        "payload_sha256": digest,
    }

    Path("gold_monthly_boosting_ensemble_e3_shrinkage_v1_result.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    Path(
        "gold_axis_2026/GOLD_MONTHLY_BOOSTING_ENSEMBLE_E3_SHRINKAGE_RESULT_2026-09-28.md"
    ).write_text(render_report(payload), encoding="utf-8")

    print("OUTPUT_GATE=PASS", flush=True)
    print(
        json.dumps(
            {
                "decisions": {
                    pool: {
                        "best_overall_alpha": results[pool]["best_overall_alpha"],
                        "best_learned_alpha": results[pool]["best_learned_alpha"],
                        "best_learned_metrics": results[pool]["best_learned_metrics"],
                        "learned_shrinkage_promoted": results[pool][
                            "learned_shrinkage_promoted"
                        ],
                        "decision": results[pool]["decision"],
                    }
                    for pool in results
                },
                "payload_sha256": digest,
                "authority_invariants_unchanged": after == bundle.invariants_before,
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
