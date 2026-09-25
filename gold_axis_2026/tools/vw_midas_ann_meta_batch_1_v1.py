from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import psycopg

import vw_midas_msvr_successor_v1 as base

DEV_START, DEV_END = "2022-04", "2024-12"
TR_START, TR_END = "2025-01", "2025-12"
ST_START, ST_END = "2026-01", "2026-07"

INPUTS = 8
HIDDEN = 4
OUTPUTS = 4
ACTIVATION = "tanh"
PARAM_DIM = INPUTS * HIDDEN + HIDDEN + HIDDEN * OUTPUTS + OUTPUTS

LOWER, UPPER = -2.0, 2.0
POP_SIZE = 24
SELECT_GENS = 45
REFIT_GENS = 15
REPEATS = 3
VAL_FRAC = 0.20
MIN_VAL = 6


def decode(theta):
    theta = np.asarray(theta, float)
    i = 0
    W1 = theta[i:i + INPUTS * HIDDEN].reshape(INPUTS, HIDDEN)
    i += INPUTS * HIDDEN
    b1 = theta[i:i + HIDDEN]
    i += HIDDEN
    W2 = theta[i:i + HIDDEN * OUTPUTS].reshape(HIDDEN, OUTPUTS)
    i += HIDDEN * OUTPUTS
    b2 = theta[i:i + OUTPUTS]
    return W1, b1, W2, b2


def ann_predict(theta, X):
    W1, b1, W2, b2 = decode(theta)
    return np.tanh(X @ W1 + b1) @ W2 + b2


def weighted_mae(theta, X, Y):
    pred = ann_predict(theta, X)
    mae_gold = np.mean(np.abs(pred[:, 0] - Y[:, 0]))
    mae_all = np.mean(np.abs(pred - Y))
    return float(0.7 * mae_gold + 0.3 * mae_all)


def arrays(samples, target):
    keys = sorted(k for k in samples if k < target)
    if len(keys) < 30:
        raise RuntimeError(f"TRAIN_TOO_SMALL {target} n={len(keys)}")
    X = np.stack([samples[k][0] for k in keys])
    Y = np.stack([samples[k][1] for k in keys])
    tx = samples[target][0][None, :]
    xm, xs, ym, ys = X.mean(0), X.std(0), Y.mean(0), Y.std(0)
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


def init_population(rng, center=None):
    if center is None:
        pop = rng.uniform(LOWER, UPPER, size=(POP_SIZE, PARAM_DIM))
    else:
        pop = np.clip(
            np.asarray(center)[None, :] + rng.normal(0.0, 0.18, size=(POP_SIZE, PARAM_DIM)),
            LOWER, UPPER
        )
        pop[0] = np.asarray(center)
    return pop


def validation_pick(pop, train_fit, Xv, Yv, incumbent_theta=None, incumbent_val=math.inf):
    # Validation does not drive population evolution. It only selects among candidates
    # that are already in the top quartile by chronological inner-training loss.
    k = max(3, len(pop) // 4)
    idx = np.argsort(train_fit)[:k]
    best_theta = incumbent_theta
    best_val = incumbent_val
    for i in idx:
        v = weighted_mae(pop[i], Xv, Yv)
        if v < best_val:
            best_val = float(v)
            best_theta = pop[i].copy()
    return best_theta, best_val


def pso_phase(X, Y, seed, generations, center=None, Xv=None, Yv=None):
    rng = np.random.default_rng(seed)
    pop = init_population(rng, center)
    vel = rng.normal(0.0, 0.12, size=pop.shape)
    fit = np.array([weighted_mae(x, X, Y) for x in pop])
    pbest, pfit = pop.copy(), fit.copy()
    gi = int(np.argmin(pfit))
    gbest, gfit = pbest[gi].copy(), float(pfit[gi])
    vbest, vfit = None, math.inf
    if Xv is not None:
        vbest, vfit = validation_pick(pop, fit, Xv, Yv, vbest, vfit)
    w, c1, c2, vmax = 0.72, 1.45, 1.45, 0.6
    for _ in range(generations):
        r1 = rng.random(pop.shape)
        r2 = rng.random(pop.shape)
        vel = w * vel + c1 * r1 * (pbest - pop) + c2 * r2 * (gbest - pop)
        vel = np.clip(vel, -vmax, vmax)
        pop = np.clip(pop + vel, LOWER, UPPER)
        fit = np.array([weighted_mae(x, X, Y) for x in pop])
        imp = fit < pfit
        pbest[imp], pfit[imp] = pop[imp], fit[imp]
        gi = int(np.argmin(pfit))
        if float(pfit[gi]) < gfit:
            gbest, gfit = pbest[gi].copy(), float(pfit[gi])
        if Xv is not None:
            vbest, vfit = validation_pick(pop, fit, Xv, Yv, vbest, vfit)
    return (vbest if Xv is not None else gbest), (vfit if Xv is not None else gfit)


def tournament(rng, pop, fit, k=3):
    idx = rng.choice(len(pop), size=k, replace=False)
    return pop[idx[np.argmin(fit[idx])]].copy()


def ga_phase(X, Y, seed, generations, center=None, Xv=None, Yv=None):
    rng = np.random.default_rng(seed)
    pop = init_population(rng, center)
    fit = np.array([weighted_mae(x, X, Y) for x in pop])
    vbest, vfit = None, math.inf
    if Xv is not None:
        vbest, vfit = validation_pick(pop, fit, Xv, Yv, vbest, vfit)
    for g in range(generations):
        elite = np.argsort(fit)[:2]
        new = [pop[i].copy() for i in elite]
        sigma = max(0.04, 0.22 * (1.0 - g / max(1, generations - 1)))
        while len(new) < POP_SIZE:
            p1 = tournament(rng, pop, fit)
            p2 = tournament(rng, pop, fit)
            if rng.random() < 0.85:
                a = rng.random(PARAM_DIM)
                c1 = a * p1 + (1.0 - a) * p2
                c2 = a * p2 + (1.0 - a) * p1
            else:
                c1, c2 = p1.copy(), p2.copy()
            for c in (c1, c2):
                mask = rng.random(PARAM_DIM) < 0.08
                if np.any(mask):
                    c[mask] += rng.normal(0.0, sigma, size=int(mask.sum()))
                new.append(np.clip(c, LOWER, UPPER))
                if len(new) >= POP_SIZE:
                    break
        pop = np.stack(new)
        fit = np.array([weighted_mae(x, X, Y) for x in pop])
        if Xv is not None:
            vbest, vfit = validation_pick(pop, fit, Xv, Yv, vbest, vfit)
    bi = int(np.argmin(fit))
    return (vbest if Xv is not None else pop[bi].copy()), (vfit if Xv is not None else float(fit[bi]))


def de_phase(X, Y, seed, generations, center=None, Xv=None, Yv=None):
    rng = np.random.default_rng(seed)
    pop = init_population(rng, center)
    fit = np.array([weighted_mae(x, X, Y) for x in pop])
    vbest, vfit = None, math.inf
    if Xv is not None:
        vbest, vfit = validation_pick(pop, fit, Xv, Yv, vbest, vfit)
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
            tf = weighted_mae(trial, X, Y)
            if tf < fit[i]:
                nxt[i], nfit[i] = trial, tf
        pop, fit = nxt, nfit
        if Xv is not None:
            vbest, vfit = validation_pick(pop, fit, Xv, Yv, vbest, vfit)
    bi = int(np.argmin(fit))
    return (vbest if Xv is not None else pop[bi].copy()), (vfit if Xv is not None else float(fit[bi]))


PHASE = {"PSO": pso_phase, "GA": ga_phase, "DE": de_phase}
SEED_BASE = {"PSO": 27110, "GA": 37110, "DE": 57110}


def select_and_refit(method, X, Y, split, target):
    fn = PHASE[method]
    Xtr, Ytr, Xv, Yv = X[:split], Y[:split], X[split:], Y[split:]
    repeat_rows = []
    best_theta, best_val, best_rep = None, math.inf, None
    target_seed = sum(map(ord, target))
    for rep in range(REPEATS):
        seed = SEED_BASE[method] + 1009 * rep + target_seed
        theta, vfit = fn(Xtr, Ytr, seed, SELECT_GENS, center=None, Xv=Xv, Yv=Yv)
        repeat_rows.append({"repeat": rep, "seed": seed, "inner_validation_fitness": float(vfit)})
        if vfit < best_val:
            best_theta, best_val, best_rep = theta.copy(), float(vfit), rep
    refit_seed = SEED_BASE[method] + 900001 + 1009 * int(best_rep) + target_seed
    final_theta, full_fit = fn(X, Y, refit_seed, REFIT_GENS, center=best_theta, Xv=None, Yv=None)
    return final_theta, best_val, float(full_fit), int(best_rep), repeat_rows


def predict_target(samples, target, method):
    keys, X, Y, tx, ym, ys, split = arrays(samples, target)
    theta, valfit, fullfit, rep, repeats = select_and_refit(method, X, Y, split, target)
    pred = ann_predict(theta, tx)[0] * ys + ym
    return pred, len(keys), valfit, fullfit, rep, repeats


def evaluate(bundle, cache, method, start, end):
    rows = []
    for target in base.month_range(start, end):
        pred, n, valfit, fullfit, rep, repeats = predict_target(cache[target], target, method)
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
    for method in ("PSO", "GA", "DE"):
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
        "batch_id": "VW_MIDAS_ANN_META_BATCH_1_V1",
        "canonical_ann": {
            "input_units": INPUTS,
            "hidden_layers": [HIDDEN],
            "hidden_activation": ACTIVATION,
            "output_units": OUTPUTS,
            "output_activation": "linear",
            "optimized_parameters": PARAM_DIM,
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
            "PSO": {"w": 0.72, "c1": 1.45, "c2": 1.45, "vmax": 0.6},
            "GA": {"elite": 2, "tournament_k": 3, "crossover_prob": 0.85, "mutation_prob": 0.08, "mutation_sigma": "0.22_to_0.04"},
            "DE": {"F": 0.7, "CR": 0.9},
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

    Path("vw_midas_ann_meta_batch_1_v1_result.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    summary = {
        method: {
            "dev": results[method]["dev"]["metrics"],
            "transport_2025": results[method]["transport_2025"]["metrics"],
            "stress_2026": results[method]["stress_2026"]["metrics"],
        }
        for method in results
    }
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
