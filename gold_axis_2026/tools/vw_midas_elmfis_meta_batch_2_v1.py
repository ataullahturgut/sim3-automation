from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

import numpy as np
import psycopg

import vw_midas_msvr_successor_v1 as base
import vw_midas_elmfis_baseline_v1 as elmfis
import vw_midas_elmfis_meta_batch_1_v1 as common

DEV_START, DEV_END = common.DEV_START, common.DEV_END
TR_START, TR_END = common.TR_START, common.TR_END
ST_START, ST_END = common.ST_START, common.ST_END

POP_SIZE = common.POP_SIZE
SELECT_GENS = common.SELECT_GENS
REFIT_GENS = common.REFIT_GENS
REPEATS = common.REPEATS
PARAM_DIM = common.PARAM_DIM
LOWER, UPPER = common.LOWER, common.UPPER
SPAN = UPPER - LOWER


def levy(rng, shape, beta=1.5):
    sigma = (
        math.gamma(1 + beta) * np.sin(np.pi * beta / 2)
        / (math.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))
    ) ** (1 / beta)
    u = rng.normal(0, sigma, size=shape)
    v = rng.normal(0, 1, size=shape)
    return u / (np.abs(v) ** (1 / beta) + 1e-12)


def mpa_phase(X, Y, seed, generations, center, Xv=None, Yv=None, refit=False):
    rng = np.random.default_rng(seed)
    pop = common.init_population(rng, center, refit=refit)
    fit = common.population_fit(pop, X, Y)
    bi = int(np.argmin(fit))
    elite, elite_fit = pop[bi].copy(), float(fit[bi])
    vbest, vfit = None, math.inf

    if Xv is not None:
        vbest, vfit = common.validation_pick(pop, fit, X, Y, Xv, Yv, vbest, vfit)

    FADs, P = 0.2, 0.5
    for t in range(1, generations + 1):
        cf = (1 - t / generations) ** (2 * t / generations)
        old, old_fit = pop.copy(), fit.copy()

        if t <= generations / 3:
            RB = rng.normal(0, 1, size=pop.shape)
            step = RB * (elite[None, :] - RB * pop)
            pop = pop + P * rng.random(pop.shape) * step
        elif t <= 2 * generations / 3:
            RL = 0.05 * levy(rng, pop.shape)
            RB = rng.normal(0, 1, size=pop.shape)
            half = len(pop) // 2
            for i in range(len(pop)):
                if i < half:
                    step = RL[i] * (elite - RL[i] * pop[i])
                    pop[i] = pop[i] + P * rng.random(PARAM_DIM) * step
                else:
                    step = RB[i] * (RB[i] * elite - pop[i])
                    pop[i] = elite + P * cf * step
        else:
            RL = 0.05 * levy(rng, pop.shape)
            step = RL * (RL * elite[None, :] - pop)
            pop = elite[None, :] + P * cf * step

        pop = np.clip(pop, LOWER, UPPER)

        if rng.random() < FADs:
            U = (rng.random(pop.shape) < FADs).astype(float)
            random_box = LOWER + rng.random(pop.shape) * SPAN
            pop = pop + cf * random_box * U
        else:
            r = rng.random()
            i1, i2 = rng.permutation(len(pop)), rng.permutation(len(pop))
            pop = pop + (FADs * (1 - r) + r) * (pop[i1] - pop[i2])
        pop = np.clip(pop, LOWER, UPPER)

        fit = common.population_fit(pop, X, Y)
        keep = old_fit < fit
        pop[keep], fit[keep] = old[keep], old_fit[keep]

        bi = int(np.argmin(fit))
        if float(fit[bi]) < elite_fit:
            elite, elite_fit = pop[bi].copy(), float(fit[bi])

        if Xv is not None:
            vbest, vfit = common.validation_pick(pop, fit, X, Y, Xv, Yv, vbest, vfit)

    return (vbest if Xv is not None else elite), (vfit if Xv is not None else elite_fit)


def abc_population(rng, center, refit=False, food_n=None):
    food_n = food_n or POP_SIZE // 2
    center = np.clip(np.asarray(center, float), LOWER, UPPER)
    food = np.empty((food_n, PARAM_DIM), float)
    food[0] = center
    sigma = common.REFIT_SIGMA if refit else common.LOCAL_SIGMA
    n_local = food_n - 1 if refit else max(1, (food_n - 1) // 2)
    if n_local:
        noise = rng.normal(0.0, 1.0, size=(n_local, PARAM_DIM)) * sigma
        food[1:1 + n_local] = np.clip(center[None, :] + noise, LOWER, UPPER)
    start = 1 + n_local
    if start < food_n:
        food[start:] = rng.uniform(LOWER, UPPER, size=(food_n - start, PARAM_DIM))
    return food


def abc_phase(X, Y, seed, generations, center, Xv=None, Yv=None, refit=False):
    rng = np.random.default_rng(seed)
    food_n = POP_SIZE // 2
    food = abc_population(rng, center, refit=refit, food_n=food_n)
    fit = common.population_fit(food, X, Y)
    trials = np.zeros(food_n, dtype=int)
    limit = 12
    vbest, vfit = None, math.inf

    if Xv is not None:
        vbest, vfit = common.validation_pick(food, fit, X, Y, Xv, Yv, vbest, vfit)

    def neighbor(i):
        k = i
        while k == i:
            k = int(rng.integers(0, food_n))
        j = int(rng.integers(0, PARAM_DIM))
        phi = float(rng.uniform(-1, 1))
        v = food[i].copy()
        proposed = food[i, j] + phi * (food[i, j] - food[k, j])
        v[j] = np.clip(proposed, LOWER[j], UPPER[j])
        return v

    for _ in range(generations):
        for i in range(food_n):
            v = neighbor(i)
            vf = common.training_loss(v, X, Y)
            if vf < fit[i]:
                food[i], fit[i], trials[i] = v, vf, 0
            else:
                trials[i] += 1

        quality = 1.0 / (1.0 + fit)
        probs = quality / quality.sum()
        for _ in range(food_n):
            i = int(rng.choice(food_n, p=probs))
            v = neighbor(i)
            vf = common.training_loss(v, X, Y)
            if vf < fit[i]:
                food[i], fit[i], trials[i] = v, vf, 0
            else:
                trials[i] += 1

        for i in range(food_n):
            if trials[i] >= limit:
                if refit:
                    food[i] = np.clip(
                        center + rng.normal(0.0, 1.0, size=PARAM_DIM) * common.REFIT_SIGMA,
                        LOWER, UPPER,
                    )
                else:
                    food[i] = rng.uniform(LOWER, UPPER, size=PARAM_DIM)
                fit[i] = common.training_loss(food[i], X, Y)
                trials[i] = 0

        if Xv is not None:
            vbest, vfit = common.validation_pick(food, fit, X, Y, Xv, Yv, vbest, vfit)

    bi = int(np.argmin(fit))
    return (vbest if Xv is not None else food[bi].copy()), (
        vfit if Xv is not None else float(fit[bi])
    )


def ssa_phase(X, Y, seed, generations, center, Xv=None, Yv=None, refit=False):
    rng = np.random.default_rng(seed)
    pop = common.init_population(rng, center, refit=refit)
    fit = common.population_fit(pop, X, Y)
    n_prod = max(1, int(round(len(pop) * 0.2)))
    n_aware = max(1, int(round(len(pop) * 0.15)))
    ST, eps = 0.8, 1e-12
    vbest, vfit = None, math.inf

    if Xv is not None:
        vbest, vfit = common.validation_pick(pop, fit, X, Y, Xv, Yv, vbest, vfit)

    for _t in range(1, generations + 1):
        order = np.argsort(fit)
        best, worst = pop[order[0]].copy(), pop[order[-1]].copy()
        R2 = float(rng.random())

        for rank_idx, idx in enumerate(order[:n_prod], start=1):
            if R2 < ST:
                decay = np.exp(-rank_idx / (rng.uniform(0.2, 1.0) * generations + eps))
                pop[idx] = pop[idx] * decay
            else:
                pop[idx] = pop[idx] + rng.normal(0, 1, size=PARAM_DIM) * (0.10 * SPAN)
            pop[idx] = np.clip(pop[idx], LOWER, UPPER)

        for rank_idx, idx in enumerate(order[n_prod:], start=n_prod + 1):
            if rank_idx > len(pop) / 2:
                q = float(rng.normal())
                raw = np.clip((worst - pop[idx]) / ((rank_idx ** 2) + eps), -10, 10)
                # Map the original SSA multiplicative move into the heterogeneous
                # ELMFIS bounds around the current best/anchor scale.
                pop[idx] = center + q * np.exp(raw) * (0.05 * SPAN)
            else:
                signs = np.where(rng.random(PARAM_DIM) < 0.5, -1.0, 1.0)
                pop[idx] = best + np.abs(pop[idx] - best) * signs * rng.random(PARAM_DIM)
            pop[idx] = np.clip(pop[idx], LOWER, UPPER)

        current_fit = common.population_fit(pop, X, Y)
        bi, wi = int(np.argmin(current_fit)), int(np.argmax(current_fit))
        best, worst = pop[bi].copy(), pop[wi].copy()
        best_fit, worst_fit = float(current_fit[bi]), float(current_fit[wi])

        for idx in rng.choice(len(pop), size=n_aware, replace=False):
            fi = float(current_fit[idx])
            if fi > best_fit:
                pop[idx] = best + rng.normal(0, 1, size=PARAM_DIM) * np.abs(pop[idx] - best)
            else:
                K = float(rng.uniform(-1, 1))
                pop[idx] = pop[idx] + K * np.abs(pop[idx] - worst) / (
                    abs(fi - worst_fit) + eps
                )
            pop[idx] = np.clip(pop[idx], LOWER, UPPER)

        fit = common.population_fit(pop, X, Y)
        if Xv is not None:
            vbest, vfit = common.validation_pick(pop, fit, X, Y, Xv, Yv, vbest, vfit)

    bi = int(np.argmin(fit))
    return (vbest if Xv is not None else pop[bi].copy()), (
        vfit if Xv is not None else float(fit[bi])
    )


def gwo_phase(X, Y, seed, generations, center, Xv=None, Yv=None, refit=False):
    rng = np.random.default_rng(seed)
    wolves = common.init_population(rng, center, refit=refit)
    fit = common.population_fit(wolves, X, Y)
    vbest, vfit = None, math.inf

    if Xv is not None:
        vbest, vfit = common.validation_pick(wolves, fit, X, Y, Xv, Yv, vbest, vfit)

    for t in range(generations):
        order = np.argsort(fit)
        alpha, beta, delta = (wolves[order[i]].copy() for i in range(3))
        a = 2.0 - 2.0 * (t / max(1, generations - 1))
        new = np.empty_like(wolves)

        for i in range(len(wolves)):
            candidates = []
            for leader in (alpha, beta, delta):
                r1, r2 = rng.random(PARAM_DIM), rng.random(PARAM_DIM)
                A, C = 2 * a * r1 - a, 2 * r2
                D = np.abs(C * leader - wolves[i])
                candidates.append(leader - A * D)
            new[i] = np.mean(candidates, axis=0)

        wolves = np.clip(new, LOWER, UPPER)
        fit = common.population_fit(wolves, X, Y)
        if Xv is not None:
            vbest, vfit = common.validation_pick(wolves, fit, X, Y, Xv, Yv, vbest, vfit)

    bi = int(np.argmin(fit))
    return (vbest if Xv is not None else wolves[bi].copy()), (
        vfit if Xv is not None else float(fit[bi])
    )


PHASE = {"MPA": mpa_phase, "ABC": abc_phase, "SSA": ssa_phase, "GWO": gwo_phase}
SEED_BASE = {"MPA": 48110, "ABC": 68110, "SSA": 78110, "GWO": 88110}


def select_and_refit(method, X, Y, split, target):
    fn = PHASE[method]
    Xtr, Ytr, Xv, Yv = X[:split], Y[:split], X[split:], Y[split:]
    base_theta = common.initial_theta(Xtr)

    repeat_rows = []
    best_theta, best_val, best_rep = None, math.inf, None
    target_seed = sum(map(ord, target))

    for rep in range(REPEATS):
        seed = SEED_BASE[method] + 1009 * rep + target_seed
        theta, vfit = fn(
            Xtr, Ytr, seed, SELECT_GENS, center=base_theta,
            Xv=Xv, Yv=Yv, refit=False
        )
        repeat_rows.append({
            "repeat": rep,
            "seed": seed,
            "inner_validation_fitness": float(vfit),
        })
        if vfit < best_val:
            best_theta, best_val, best_rep = theta.copy(), float(vfit), rep

    refit_seed = SEED_BASE[method] + 900001 + 1009 * int(best_rep) + target_seed
    final_theta, full_fit = fn(
        X, Y, refit_seed, REFIT_GENS, center=best_theta,
        Xv=None, Yv=None, refit=True
    )
    return final_theta, best_val, float(full_fit), int(best_rep), repeat_rows


def predict_target(samples, target, method):
    keys, X, Y, tx, ym, ys, split = common.arrays(samples, target)
    theta, valfit, fullfit, rep, repeats = select_and_refit(method, X, Y, split, target)

    pred_std = common.predict_with_fit(theta, X, Y, tx)[0]
    pred = pred_std * ys + ym
    centers, spreads = common.decode(theta)

    return (
        pred,
        len(keys),
        valfit,
        fullfit,
        rep,
        repeats,
        float(np.min(spreads)),
        float(np.max(spreads)),
        float(np.max(np.abs(centers))),
    )


def evaluate(bundle, cache, method, start, end):
    rows = []
    for target in base.month_range(start, end):
        (
            pred, n, valfit, fullfit, rep, repeats,
            min_spread, max_spread, max_abs_center,
        ) = predict_target(cache[target], target, method)
        origin = base.month_shift(target, -1)

        rows.append({
            "target": target,
            "origin": origin,
            "method": method,
            "train_rows": n,
            "selected_repeat": rep,
            "inner_validation_fitness": valfit,
            "full_history_refit_fitness": fullfit,
            "repeat_validation": repeats,
            "antecedent_min_spread": min_spread,
            "antecedent_max_spread": max_spread,
            "antecedent_max_abs_center": max_abs_center,
            "pred_log_return_gold": float(pred[0]),
            "forecast": float(bundle.core_gold[origin] * math.exp(float(pred[0]))),
            "actual": float(bundle.core_gold[target]),
            "rw": float(bundle.core_gold[origin]),
        })
    return rows


def read_authority_invariants(dsn):
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)


def run_method(method):
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    bundle = base.load_data(dsn)
    cache = {
        t: base.all_samples_at_origin(bundle, t, governed=True)
        for t in base.month_range(DEV_START, ST_END)
    }

    dev = evaluate(bundle, cache, method, DEV_START, DEV_END)
    tr = evaluate(bundle, cache, method, TR_START, TR_END)
    st = evaluate(bundle, cache, method, ST_START, ST_END)

    after = read_authority_invariants(dsn)
    if after != bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    params = {
        "MPA": {
            "population": POP_SIZE,
            "FADs": 0.2,
            "P": 0.5,
            "phases": "Brownian/transition/Levy with marine memory",
        },
        "ABC": {
            "colony": POP_SIZE,
            "food_sources": POP_SIZE // 2,
            "limit": 12,
        },
        "SSA": {
            "population": POP_SIZE,
            "producer_ratio": 0.2,
            "aware_ratio": 0.15,
            "safety_threshold": 0.8,
        },
        "GWO": {
            "population": POP_SIZE,
            "a_schedule": "2_to_0_linear",
        },
    }[method]

    out = {
        "batch_id": "VW_MIDAS_ELMFIS_META_BATCH_2_V1",
        "model_id": f"VW_MIDAS_{method}_ELMFIS_V1",
        "method": method,
        "canonical_elmfis": {
            "inputs": common.INPUTS,
            "outputs": common.OUTPUTS,
            "rules": common.RULES,
            "membership": "bell_gaussian_exp_minus_squared_distance",
            "and_operator": "product_logspace",
            "rule_normalization": True,
            "consequent": "first_order_TSK_linear",
            "consequent_fit": "analytic_ridge_per_candidate",
            "ridge_alpha": elmfis.RIDGE_ALPHA,
        },
        "optimization_contract": {
            "scope": "antecedent_centers_and_log_spreads_only",
            "optimized_parameters": PARAM_DIM,
            "center_bounds_standardized": [common.CENTER_LOW, common.CENTER_HIGH],
            "spread_bounds_standardized": [common.SPREAD_LOW, common.SPREAD_HIGH],
            "population_reference": POP_SIZE,
            "selection_generations": SELECT_GENS,
            "full_history_refit_generations": REFIT_GENS,
            "deterministic_repeats_per_target": REPEATS,
            "initialization": "training_only_kmeans_anchor_plus_local_and_uniform_exploration",
            "inner_split": "chronological_last_20pct_training_history_min_6",
            "population_evolution_objective": "0.7*Gold_standardized_MAE + 0.3*all_output_standardized_MAE on inner-training with analytic ridge consequent",
            "selection_fitness": "same weighted MAE on chronological validation tail; top-quartile train candidates only; consequents fit on inner-training",
            "refit": "warm-start antecedents from validation-selected theta; optimize on all pre-target history; consequents solved analytically",
            "target_month_in_fitness": False,
        },
        "method_parameters": params,
        "authority": {
            "database_access": "READ_ONLY",
            "feature_contract": "UNCHANGED_VW_MIDAS_8_FEATURE",
            "target": "NEXT_MONTH_AVERAGE_PRICE_VIA_4_RETURN_OUTPUTS",
            "random_validation": "NONE",
            "selection_period": f"{DEV_START}..{DEV_END}",
            "2025_role": "LOCKED_TRANSPORT_NOT_SELECTION",
            "2026_role": "RETROSPECTIVE_STRESS_NOT_SELECTION",
            "primary_metrics": ["sum_abs_error", "direction_accuracy_pct"],
            "source_checks": bundle.source_checks,
            "authority_invariants_before": bundle.invariants_before,
            "authority_invariants_after": after,
        },
        "dev": {
            "metrics": elmfis.active_metrics(dev),
            "yearly": elmfis.yearly(dev),
            "rows": dev,
        },
        "transport_2025": {
            "metrics": elmfis.active_metrics(tr),
            "rows": tr,
        },
        "stress_2026": {
            "metrics": elmfis.active_metrics(st),
            "rows": st,
        },
    }

    path = Path(f"vw_midas_elmfis_meta_batch_2_v1_{method.lower()}_result.json")
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "method": method,
        "dev": out["dev"]["metrics"],
        "transport_2025": out["transport_2025"]["metrics"],
        "stress_2026": out["stress_2026"]["metrics"],
    }, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--method", required=True, choices=sorted(PHASE))
    args = parser.parse_args()
    run_method(args.method)


if __name__ == "__main__":
    main()
