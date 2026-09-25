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

DEV_START, DEV_END = "2022-04", "2024-12"
TR_START, TR_END = "2025-01", "2025-12"
ST_START, ST_END = "2026-01", "2026-07"

INPUTS = 8
RULES = elmfis.N_RULES
OUTPUTS = 4
N_ANT = RULES * INPUTS
PARAM_DIM = 2 * N_ANT

CENTER_LOW, CENTER_HIGH = -4.0, 4.0
SPREAD_LOW, SPREAD_HIGH = elmfis.SPREAD_FLOOR, 4.0
LOWER = np.concatenate([
    np.full(N_ANT, CENTER_LOW),
    np.full(N_ANT, math.log(SPREAD_LOW)),
])
UPPER = np.concatenate([
    np.full(N_ANT, CENTER_HIGH),
    np.full(N_ANT, math.log(SPREAD_HIGH)),
])

POP_SIZE = 24
SELECT_GENS = 45
REFIT_GENS = 15
REPEATS = 3
VAL_FRAC = 0.20
MIN_VAL = 6

LOCAL_SIGMA = np.concatenate([
    np.full(N_ANT, 0.45),
    np.full(N_ANT, 0.30),
])
REFIT_SIGMA = np.concatenate([
    np.full(N_ANT, 0.16),
    np.full(N_ANT, 0.12),
])


def encode(centers, spreads):
    centers = np.asarray(centers, float).reshape(-1)
    spreads = np.asarray(spreads, float).reshape(-1)
    theta = np.concatenate([
        np.clip(centers, CENTER_LOW, CENTER_HIGH),
        np.log(np.clip(spreads, SPREAD_LOW, SPREAD_HIGH)),
    ])
    return np.clip(theta, LOWER, UPPER)


def decode(theta):
    theta = np.asarray(theta, float)
    if theta.shape != (PARAM_DIM,):
        raise ValueError(f"BAD_THETA_SHAPE {theta.shape}")
    centers = theta[:N_ANT].reshape(RULES, INPUTS)
    log_spreads = theta[N_ANT:].reshape(RULES, INPUTS)
    spreads = np.exp(log_spreads)
    spreads = np.clip(spreads, SPREAD_LOW, SPREAD_HIGH)
    return centers, spreads


def initial_theta(X):
    centers, spreads, _ = elmfis.fit_antecedents(X)
    return encode(centers, spreads)


def predict_with_fit(theta, Xfit, Yfit, Xeval):
    centers, spreads = decode(theta)
    beta = elmfis.fit_consequents(Xfit, Yfit, centers, spreads)
    return elmfis.tsk_design(Xeval, centers, spreads) @ beta


def weighted_mae_from_pred(pred, Y):
    mae_gold = np.mean(np.abs(pred[:, 0] - Y[:, 0]))
    mae_all = np.mean(np.abs(pred - Y))
    return float(0.7 * mae_gold + 0.3 * mae_all)


def training_loss(theta, X, Y):
    return weighted_mae_from_pred(predict_with_fit(theta, X, Y, X), Y)


def validation_loss(theta, Xtr, Ytr, Xv, Yv):
    return weighted_mae_from_pred(predict_with_fit(theta, Xtr, Ytr, Xv), Yv)


def arrays(samples, target):
    keys = sorted(k for k in samples if k < target)
    if len(keys) < 30:
        raise RuntimeError(f"TRAIN_TOO_SMALL {target} n={len(keys)}")
    X = np.stack([samples[k][0] for k in keys])
    Y = np.stack([samples[k][1] for k in keys])
    tx = samples[target][0][None, :]

    xm, xs = X.mean(0), X.std(0)
    ym, ys = Y.mean(0), Y.std(0)
    xs = np.where(xs < 1e-9, 1.0, xs)
    ys = np.where(ys < 1e-9, 1.0, ys)

    Xs = (X - xm) / xs
    Ys = (Y - ym) / ys
    txs = (tx - xm) / xs

    nval = max(MIN_VAL, int(round(VAL_FRAC * len(Xs))))
    split = len(Xs) - nval
    if split < 24:
        raise RuntimeError(f"INNER_TRAIN_TOO_SMALL {target} n={len(Xs)} split={split}")

    return keys, Xs, Ys, txs, ym, ys, split


def init_population(rng, center, refit=False):
    center = np.clip(np.asarray(center, float), LOWER, UPPER)
    pop = np.empty((POP_SIZE, PARAM_DIM), float)
    pop[0] = center

    if refit:
        noise = rng.normal(0.0, 1.0, size=(POP_SIZE - 1, PARAM_DIM)) * REFIT_SIGMA
        pop[1:] = np.clip(center[None, :] + noise, LOWER, UPPER)
        return pop

    n_local = (POP_SIZE - 1) // 2
    if n_local:
        noise = rng.normal(0.0, 1.0, size=(n_local, PARAM_DIM)) * LOCAL_SIGMA
        pop[1:1 + n_local] = np.clip(center[None, :] + noise, LOWER, UPPER)
    start = 1 + n_local
    if start < POP_SIZE:
        pop[start:] = rng.uniform(LOWER, UPPER, size=(POP_SIZE - start, PARAM_DIM))
    return pop


def population_fit(pop, X, Y):
    return np.array([training_loss(x, X, Y) for x in pop], float)


def validation_pick(pop, train_fit, Xtr, Ytr, Xv, Yv, incumbent_theta=None, incumbent_val=math.inf):
    # Validation never drives optimizer evolution. It selects only among the
    # top quartile by chronological inner-training loss.
    k = max(3, len(pop) // 4)
    idx = np.argsort(train_fit)[:k]
    best_theta = incumbent_theta
    best_val = incumbent_val
    for i in idx:
        v = validation_loss(pop[i], Xtr, Ytr, Xv, Yv)
        if v < best_val:
            best_val = float(v)
            best_theta = pop[i].copy()
    return best_theta, best_val


def pso_phase(X, Y, seed, generations, center, Xv=None, Yv=None, refit=False):
    rng = np.random.default_rng(seed)
    pop = init_population(rng, center, refit=refit)
    vel = rng.normal(0.0, 0.10, size=pop.shape) * (UPPER - LOWER)
    fit = population_fit(pop, X, Y)
    pbest, pfit = pop.copy(), fit.copy()
    gi = int(np.argmin(pfit))
    gbest, gfit = pbest[gi].copy(), float(pfit[gi])
    vbest, vfit = None, math.inf

    if Xv is not None:
        vbest, vfit = validation_pick(pop, fit, X, Y, Xv, Yv, vbest, vfit)

    w, c1, c2, vmax_frac = 0.72, 1.45, 1.45, 0.15
    vmax = vmax_frac * (UPPER - LOWER)

    for _ in range(generations):
        r1 = rng.random(pop.shape)
        r2 = rng.random(pop.shape)
        vel = w * vel + c1 * r1 * (pbest - pop) + c2 * r2 * (gbest - pop)
        vel = np.clip(vel, -vmax, vmax)
        pop = np.clip(pop + vel, LOWER, UPPER)
        fit = population_fit(pop, X, Y)

        imp = fit < pfit
        pbest[imp], pfit[imp] = pop[imp], fit[imp]
        gi = int(np.argmin(pfit))
        if float(pfit[gi]) < gfit:
            gbest, gfit = pbest[gi].copy(), float(pfit[gi])

        if Xv is not None:
            vbest, vfit = validation_pick(pop, fit, X, Y, Xv, Yv, vbest, vfit)

    return (vbest if Xv is not None else gbest), (vfit if Xv is not None else gfit)


def tournament(rng, pop, fit, k=3):
    idx = rng.choice(len(pop), size=k, replace=False)
    return pop[idx[np.argmin(fit[idx])]].copy()


def ga_phase(X, Y, seed, generations, center, Xv=None, Yv=None, refit=False):
    rng = np.random.default_rng(seed)
    pop = init_population(rng, center, refit=refit)
    fit = population_fit(pop, X, Y)
    vbest, vfit = None, math.inf

    if Xv is not None:
        vbest, vfit = validation_pick(pop, fit, X, Y, Xv, Yv, vbest, vfit)

    span = UPPER - LOWER
    for g in range(generations):
        elite = np.argsort(fit)[:2]
        new = [pop[i].copy() for i in elite]
        sigma_frac = max(0.015, 0.08 * (1.0 - g / max(1, generations - 1)))

        while len(new) < POP_SIZE:
            p1 = tournament(rng, pop, fit)
            p2 = tournament(rng, pop, fit)
            if rng.random() < 0.85:
                a = rng.random(PARAM_DIM)
                c1 = a * p1 + (1.0 - a) * p2
                c2 = a * p2 + (1.0 - a) * p1
            else:
                c1, c2 = p1.copy(), p2.copy()

            for child in (c1, c2):
                mask = rng.random(PARAM_DIM) < 0.08
                if np.any(mask):
                    child[mask] += rng.normal(
                        0.0,
                        sigma_frac * span[mask],
                        size=int(mask.sum()),
                    )
                new.append(np.clip(child, LOWER, UPPER))
                if len(new) >= POP_SIZE:
                    break

        pop = np.stack(new)
        fit = population_fit(pop, X, Y)

        if Xv is not None:
            vbest, vfit = validation_pick(pop, fit, X, Y, Xv, Yv, vbest, vfit)

    bi = int(np.argmin(fit))
    return (vbest if Xv is not None else pop[bi].copy()), (vfit if Xv is not None else float(fit[bi]))


def de_phase(X, Y, seed, generations, center, Xv=None, Yv=None, refit=False):
    rng = np.random.default_rng(seed)
    pop = init_population(rng, center, refit=refit)
    fit = population_fit(pop, X, Y)
    vbest, vfit = None, math.inf

    if Xv is not None:
        vbest, vfit = validation_pick(pop, fit, X, Y, Xv, Yv, vbest, vfit)

    F, CR = 0.7, 0.9
    for _ in range(generations):
        nxt, nfit = pop.copy(), fit.copy()
        for i in range(POP_SIZE):
            pool = [j for j in range(POP_SIZE) if j != i]
            a, b, c = rng.choice(pool, size=3, replace=False)
            mutant = np.clip(pop[a] + F * (pop[b] - pop[c]), LOWER, UPPER)
            mask = rng.random(PARAM_DIM) < CR
            mask[rng.integers(0, PARAM_DIM)] = True
            trial = np.where(mask, mutant, pop[i])
            tf = training_loss(trial, X, Y)
            if tf < fit[i]:
                nxt[i], nfit[i] = trial, tf
        pop, fit = nxt, nfit

        if Xv is not None:
            vbest, vfit = validation_pick(pop, fit, X, Y, Xv, Yv, vbest, vfit)

    bi = int(np.argmin(fit))
    return (vbest if Xv is not None else pop[bi].copy()), (vfit if Xv is not None else float(fit[bi]))


PHASE = {"PSO": pso_phase, "GA": ga_phase, "DE": de_phase}
SEED_BASE = {"PSO": 28110, "GA": 38110, "DE": 58110}


def select_and_refit(method, X, Y, split, target):
    fn = PHASE[method]
    Xtr, Ytr, Xv, Yv = X[:split], Y[:split], X[split:], Y[split:]
    base_theta = initial_theta(Xtr)

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
    keys, X, Y, tx, ym, ys, split = arrays(samples, target)
    theta, valfit, fullfit, rep, repeats = select_and_refit(method, X, Y, split, target)

    pred_std = predict_with_fit(theta, X, Y, tx)[0]
    pred = pred_std * ys + ym
    centers, spreads = decode(theta)

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

    out = {
        "batch_id": "VW_MIDAS_ELMFIS_META_BATCH_1_V1",
        "model_id": f"VW_MIDAS_{method}_ELMFIS_V1",
        "method": method,
        "canonical_elmfis": {
            "inputs": INPUTS,
            "outputs": OUTPUTS,
            "rules": RULES,
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
            "center_bounds_standardized": [CENTER_LOW, CENTER_HIGH],
            "spread_bounds_standardized": [SPREAD_LOW, SPREAD_HIGH],
            "population": POP_SIZE,
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
        "method_parameters": {
            "PSO": {"w": 0.72, "c1": 1.45, "c2": 1.45, "vmax_fraction_of_parameter_span": 0.15},
            "GA": {"elite": 2, "tournament_k": 3, "crossover_prob": 0.85, "mutation_prob": 0.08, "mutation_sigma_fraction": "0.08_to_0.015"},
            "DE": {"F": 0.7, "CR": 0.9},
        }[method],
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

    path = Path(f"vw_midas_elmfis_meta_batch_1_v1_{method.lower()}_result.json")
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
