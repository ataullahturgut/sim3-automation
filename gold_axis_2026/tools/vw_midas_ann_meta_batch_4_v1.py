from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import psycopg

import vw_midas_msvr_successor_v1 as base
import vw_midas_ann_meta_batch_1_v1 as common

DEV_START, DEV_END = common.DEV_START, common.DEV_END
TR_START, TR_END = common.TR_START, common.TR_END
ST_START, ST_END = common.ST_START, common.ST_END

POP_SIZE = common.POP_SIZE
SELECT_GENS = common.SELECT_GENS
REFIT_GENS = common.REFIT_GENS
REPEATS = common.REPEATS
LOWER, UPPER = common.LOWER, common.UPPER
PARAM_DIM = common.PARAM_DIM


def levy(rng, shape, beta=1.5):
    sigma = (
        math.gamma(1 + beta) * math.sin(math.pi * beta / 2)
        / (math.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))
    ) ** (1 / beta)
    u = rng.normal(0, sigma, size=shape)
    v = rng.normal(0, 1, size=shape)
    return u / (np.abs(v) ** (1 / beta) + 1e-12)


def fa_phase(X, Y, seed, generations, center=None, Xv=None, Yv=None):
    rng = np.random.default_rng(seed)
    x = common.init_population(rng, center)
    fit = np.array([common.weighted_mae(z, X, Y) for z in x])
    beta0 = 1.0
    gamma = 1.0 / PARAM_DIM
    alpha = 0.25
    vbest, vfit = None, math.inf
    if Xv is not None:
        vbest, vfit = common.validation_pick(x, fit, Xv, Yv, vbest, vfit)

    for _ in range(generations):
        order = np.argsort(fit)
        x, fit = x[order], fit[order]
        for i in range(1, POP_SIZE):
            for j in range(i):
                if fit[j] < fit[i]:
                    r2 = np.mean((x[i] - x[j]) ** 2)
                    beta = beta0 * np.exp(-gamma * r2)
                    cand = x[i] + beta * (x[j] - x[i]) + alpha * rng.normal(0, 1, PARAM_DIM)
                    cand = np.clip(cand, LOWER, UPPER)
                    cf = common.weighted_mae(cand, X, Y)
                    if cf < fit[i]:
                        x[i], fit[i] = cand, cf
        alpha *= 0.97
        if Xv is not None:
            vbest, vfit = common.validation_pick(x, fit, Xv, Yv, vbest, vfit)

    bi = int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()), (
        vfit if Xv is not None else float(fit[bi])
    )


def mfo_phase(X, Y, seed, generations, center=None, Xv=None, Yv=None):
    rng = np.random.default_rng(seed)
    moth = common.init_population(rng, center)
    fit = np.array([common.weighted_mae(z, X, Y) for z in moth])
    order = np.argsort(fit)
    flames, ffit = moth[order].copy(), fit[order].copy()
    b = 1.0
    vbest, vfit = None, math.inf
    if Xv is not None:
        vbest, vfit = common.validation_pick(moth, fit, Xv, Yv, vbest, vfit)

    for t in range(generations):
        flame_no = max(1, int(round(POP_SIZE - t * (POP_SIZE - 1) / max(1, generations - 1))))
        new = np.empty_like(moth)
        for i in range(POP_SIZE):
            fidx = min(i, flame_no - 1)
            flame = flames[fidx]
            dist = np.abs(flame - moth[i])
            l = rng.uniform(-1, 1, PARAM_DIM)
            new[i] = dist * np.exp(b * l) * np.cos(2 * np.pi * l) + flame
        moth = np.clip(new, LOWER, UPPER)
        fit = np.array([common.weighted_mae(z, X, Y) for z in moth])
        combined = np.vstack([flames, moth])
        cfit = np.concatenate([ffit, fit])
        keep = np.argsort(cfit)[:POP_SIZE]
        flames, ffit = combined[keep].copy(), cfit[keep].copy()
        if Xv is not None:
            vbest, vfit = common.validation_pick(moth, fit, Xv, Yv, vbest, vfit)

    return (vbest if Xv is not None else flames[0].copy()), (
        vfit if Xv is not None else float(ffit[0])
    )


def fpa_phase(X, Y, seed, generations, center=None, Xv=None, Yv=None):
    rng = np.random.default_rng(seed)
    x = common.init_population(rng, center)
    fit = np.array([common.weighted_mae(z, X, Y) for z in x])
    p = 0.8
    vbest, vfit = None, math.inf
    if Xv is not None:
        vbest, vfit = common.validation_pick(x, fit, Xv, Yv, vbest, vfit)

    for _ in range(generations):
        best = x[int(np.argmin(fit))].copy()
        for i in range(POP_SIZE):
            if rng.random() < p:
                step = 0.01 * levy(rng, (PARAM_DIM,))
                cand = x[i] + step * (best - x[i])
            else:
                j, k = rng.choice(POP_SIZE, 2, replace=False)
                cand = x[i] + rng.random() * (x[j] - x[k])
            cand = np.clip(cand, LOWER, UPPER)
            cf = common.weighted_mae(cand, X, Y)
            if cf < fit[i]:
                x[i], fit[i] = cand, cf
        if Xv is not None:
            vbest, vfit = common.validation_pick(x, fit, Xv, Yv, vbest, vfit)

    bi = int(np.argmin(fit))
    return (vbest if Xv is not None else x[bi].copy()), (
        vfit if Xv is not None else float(fit[bi])
    )


def cs_phase(X, Y, seed, generations, center=None, Xv=None, Yv=None):
    rng = np.random.default_rng(seed)
    nests = common.init_population(rng, center)
    fit = np.array([common.weighted_mae(z, X, Y) for z in nests])
    pa = 0.25
    vbest, vfit = None, math.inf
    if Xv is not None:
        vbest, vfit = common.validation_pick(nests, fit, Xv, Yv, vbest, vfit)

    for _ in range(generations):
        best = nests[int(np.argmin(fit))].copy()
        for i in range(POP_SIZE):
            cand = nests[i] + 0.01 * levy(rng, (PARAM_DIM,)) * (nests[i] - best)
            cand = np.clip(cand, LOWER, UPPER)
            cf = common.weighted_mae(cand, X, Y)
            j = int(rng.integers(0, POP_SIZE))
            if cf < fit[j]:
                nests[j], fit[j] = cand, cf

        abandon = rng.random(POP_SIZE) < pa
        for i in np.where(abandon)[0]:
            j, k = rng.choice(POP_SIZE, 2, replace=False)
            cand = nests[i] + rng.random(PARAM_DIM) * (nests[j] - nests[k])
            cand = np.clip(cand, LOWER, UPPER)
            cf = common.weighted_mae(cand, X, Y)
            if cf < fit[i]:
                nests[i], fit[i] = cand, cf

        if Xv is not None:
            vbest, vfit = common.validation_pick(nests, fit, Xv, Yv, vbest, vfit)

    bi = int(np.argmin(fit))
    return (vbest if Xv is not None else nests[bi].copy()), (
        vfit if Xv is not None else float(fit[bi])
    )


PHASE = {"FA": fa_phase, "MFO": mfo_phase, "FPA": fpa_phase, "CS": cs_phase}
SEED_BASE = {"FA": 137110, "MFO": 147110, "FPA": 157110, "CS": 177110}


def select_and_refit(method, X, Y, split, target):
    fn = PHASE[method]
    Xtr, Ytr, Xv, Yv = X[:split], Y[:split], X[split:], Y[split:]
    repeat_rows = []
    best_theta, best_val, best_rep = None, math.inf, None
    target_seed = sum(map(ord, target))

    for rep in range(REPEATS):
        seed = SEED_BASE[method] + 1009 * rep + target_seed
        theta, vfit = fn(Xtr, Ytr, seed, SELECT_GENS, center=None, Xv=Xv, Yv=Yv)
        repeat_rows.append(
            {"repeat": rep, "seed": seed, "inner_validation_fitness": float(vfit)}
        )
        if vfit < best_val:
            best_theta, best_val, best_rep = theta.copy(), float(vfit), rep

    refit_seed = SEED_BASE[method] + 900001 + 1009 * int(best_rep) + target_seed
    final_theta, full_fit = fn(
        X, Y, refit_seed, REFIT_GENS, center=best_theta, Xv=None, Yv=None
    )
    return final_theta, best_val, float(full_fit), int(best_rep), repeat_rows


def predict_target(samples, target, method):
    keys, X, Y, tx, ym, ys, split = common.arrays(samples, target)
    theta, valfit, fullfit, rep, repeats = select_and_refit(method, X, Y, split, target)
    pred = common.ann_predict(theta, tx)[0] * ys + ym
    return pred, len(keys), valfit, fullfit, rep, repeats


def evaluate(bundle, cache, method, start, end):
    rows = []
    for target in base.month_range(start, end):
        pred, n, valfit, fullfit, rep, repeats = predict_target(
            cache[target], target, method
        )
        origin = base.month_shift(target, -1)
        rows.append(
            {
                "target": target,
                "origin": origin,
                "method": method,
                "train_rows": n,
                "selected_repeat": rep,
                "inner_validation_fitness": valfit,
                "full_history_refit_fitness": fullfit,
                "repeat_validation": repeats,
                "pred_log_return_gold": float(pred[0]),
                "forecast": float(bundle.core_gold[origin] * math.exp(float(pred[0]))),
                "actual": float(bundle.core_gold[target]),
                "rw": float(bundle.core_gold[origin]),
            }
        )
    return rows


def read_authority_invariants(dsn):
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)


def main():
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    bundle = base.load_data(dsn)
    cache = {
        t: base.all_samples_at_origin(bundle, t, governed=True)
        for t in base.month_range(DEV_START, ST_END)
    }

    results = {}
    for method in ("FA", "MFO", "FPA", "CS"):
        dev = evaluate(bundle, cache, method, DEV_START, DEV_END)
        tr = evaluate(bundle, cache, method, TR_START, TR_END)
        st = evaluate(bundle, cache, method, ST_START, ST_END)
        results[method] = {
            "model_id": f"VW_MIDAS_{method}_ANN_V1",
            "dev": {"metrics": base.metrics(dev), "yearly": base.yearly(dev), "rows": dev},
            "transport_2025": {"metrics": base.metrics(tr), "rows": tr},
            "stress_2026": {"metrics": base.metrics(st), "rows": st},
        }

    after = read_authority_invariants(dsn)
    if after != bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    out = {
        "batch_id": "VW_MIDAS_ANN_META_BATCH_4_V1",
        "canonical_ann": {
            "input_units": common.INPUTS,
            "hidden_layers": [common.HIDDEN],
            "hidden_activation": common.ACTIVATION,
            "output_units": common.OUTPUTS,
            "output_activation": "linear",
            "optimized_parameters": common.PARAM_DIM,
        },
        "optimization_contract": {
            "scope": "all_ann_weights_and_biases",
            "bounds": [LOWER, UPPER],
            "population": POP_SIZE,
            "selection_generations": SELECT_GENS,
            "full_history_refit_generations": REFIT_GENS,
            "deterministic_repeats_per_target": REPEATS,
            "inner_split": "chronological_last_20pct_training_history_min_6",
            "population_evolution_objective": "0.7*Gold_standardized_MAE + 0.3*all_output_standardized_MAE on inner-training",
            "selection_fitness": "same weighted MAE on chronological validation tail; top-quartile train candidates only",
            "refit": "warm-start from validation-selected theta; optimize on all pre-target history",
            "target_month_in_fitness": False,
        },
        "method_parameters": {
            "FA": {"beta0": 1.0, "gamma": "1/PARAM_DIM", "alpha0": 0.25, "alpha_decay": 0.97},
            "MFO": {"b": 1.0, "flames": "linear POP_SIZE_to_1"},
            "FPA": {"global_pollination_probability": 0.8, "levy_scale": 0.01},
            "CS": {"abandon_probability": 0.25, "levy_scale": 0.01},
        },
        "authority": {
            "database_access": "READ_ONLY",
            "feature_contract": "UNCHANGED_VW_MIDAS_8_FEATURE",
            "random_validation": "NONE",
            "selection_period": f"{DEV_START}..{DEV_END}",
            "2025_role": "LOCKED_TRANSPORT_NOT_SELECTION",
            "2026_role": "RETROSPECTIVE_STRESS_NOT_SELECTION",
            "source_checks": bundle.source_checks,
            "authority_invariants_before": bundle.invariants_before,
            "authority_invariants_after": after,
        },
        "models": results,
    }

    Path("vw_midas_ann_meta_batch_4_v1_result.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(json.dumps({
        method: {
            "dev": results[method]["dev"]["metrics"],
            "transport_2025": results[method]["transport_2025"]["metrics"],
            "stress_2026": results[method]["stress_2026"]["metrics"],
        }
        for method in results
    }, sort_keys=True))


if __name__ == "__main__":
    main()
