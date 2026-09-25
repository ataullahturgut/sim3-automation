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
        math.gamma(1 + beta) * math.sin(math.pi * beta / 2)
        / (math.gamma((1 + beta) / 2) * beta * 2 ** ((beta - 1) / 2))
    ) ** (1 / beta)
    u = rng.normal(0, sigma, size=shape)
    v = rng.normal(0, 1, size=shape)
    return u / (np.abs(v) ** (1 / beta) + 1e-12)


def woa_phase(X, Y, seed, generations, center, Xv=None, Yv=None, refit=False):
    rng = np.random.default_rng(seed)
    whales = common.init_population(rng, center, refit=refit)
    fit = common.population_fit(whales, X, Y)
    bi = int(np.argmin(fit))
    best, best_fit = whales[bi].copy(), float(fit[bi])
    vbest, vfit = None, math.inf
    if Xv is not None:
        vbest, vfit = common.validation_pick(whales, fit, X, Y, Xv, Yv, vbest, vfit)

    for t in range(generations):
        a = 2.0 - 2.0 * (t / max(1, generations - 1))
        a2 = -1.0 - (t / max(1, generations - 1))
        new = np.empty_like(whales)
        for i in range(len(whales)):
            r1, r2 = float(rng.random()), float(rng.random())
            A = 2 * a * r1 - a
            C = 2 * r2
            p = float(rng.random())
            l = (a2 - 1.0) * float(rng.random()) + 1.0
            if p < 0.5:
                if abs(A) < 1.0:
                    D = np.abs(C * best - whales[i])
                    x = best - A * D
                else:
                    rand_whale = whales[int(rng.integers(0, len(whales)))]
                    D = np.abs(C * rand_whale - whales[i])
                    x = rand_whale - A * D
            else:
                D = np.abs(best - whales[i])
                x = D * np.exp(l) * np.cos(2 * np.pi * l) + best
            new[i] = np.clip(x, LOWER, UPPER)
        whales = new
        fit = common.population_fit(whales, X, Y)
        bi = int(np.argmin(fit))
        if float(fit[bi]) < best_fit:
            best, best_fit = whales[bi].copy(), float(fit[bi])
        if Xv is not None:
            vbest, vfit = common.validation_pick(whales, fit, X, Y, Xv, Yv, vbest, vfit)
    return (vbest if Xv is not None else best), (vfit if Xv is not None else best_fit)


def hho_phase(X, Y, seed, generations, center, Xv=None, Yv=None, refit=False):
    rng = np.random.default_rng(seed)
    hawks = common.init_population(rng, center, refit=refit)
    fit = common.population_fit(hawks, X, Y)
    bi = int(np.argmin(fit))
    rabbit, rabbit_fit = hawks[bi].copy(), float(fit[bi])
    vbest, vfit = None, math.inf
    if Xv is not None:
        vbest, vfit = common.validation_pick(hawks, fit, X, Y, Xv, Yv, vbest, vfit)

    for t in range(generations):
        E1 = 2 * (1 - t / max(1, generations - 1))
        mean_h = np.mean(hawks, axis=0)
        new = np.empty_like(hawks)
        for i in range(len(hawks)):
            E0 = 2 * float(rng.random()) - 1
            escaping = E1 * E0
            q, r = float(rng.random()), float(rng.random())

            if abs(escaping) >= 1:
                if q < 0.5:
                    rand_h = hawks[int(rng.integers(0, len(hawks)))]
                    xn = rand_h - rng.random(PARAM_DIM) * np.abs(
                        rand_h - 2 * rng.random(PARAM_DIM) * hawks[i]
                    )
                else:
                    xn = (rabbit - mean_h) - rng.random(PARAM_DIM) * (
                        LOWER + rng.random(PARAM_DIM) * SPAN
                    )
            else:
                J = 2 * (1 - float(rng.random()))
                if r >= 0.5 and abs(escaping) >= 0.5:
                    xn = (rabbit - hawks[i]) - escaping * np.abs(J * rabbit - hawks[i])
                elif r >= 0.5 and abs(escaping) < 0.5:
                    xn = rabbit - escaping * np.abs(rabbit - hawks[i])
                elif r < 0.5 and abs(escaping) >= 0.5:
                    ypos = rabbit - escaping * np.abs(J * rabbit - hawks[i])
                    zpos = ypos + rng.random(PARAM_DIM) * levy(rng, (PARAM_DIM,)) * (0.05 * SPAN)
                    ypos, zpos = np.clip(ypos, LOWER, UPPER), np.clip(zpos, LOWER, UPPER)
                    fy = common.training_loss(ypos, X, Y)
                    fz = common.training_loss(zpos, X, Y)
                    fi = fit[i]
                    xn = ypos if fy < min(fi, fz) else (zpos if fz < fi else hawks[i])
                else:
                    ypos = rabbit - escaping * np.abs(J * rabbit - mean_h)
                    zpos = ypos + rng.random(PARAM_DIM) * levy(rng, (PARAM_DIM,)) * (0.05 * SPAN)
                    ypos, zpos = np.clip(ypos, LOWER, UPPER), np.clip(zpos, LOWER, UPPER)
                    fy = common.training_loss(ypos, X, Y)
                    fz = common.training_loss(zpos, X, Y)
                    fi = fit[i]
                    xn = ypos if fy < min(fi, fz) else (zpos if fz < fi else hawks[i])

            new[i] = np.clip(xn, LOWER, UPPER)

        hawks = new
        fit = common.population_fit(hawks, X, Y)
        bi = int(np.argmin(fit))
        if float(fit[bi]) < rabbit_fit:
            rabbit, rabbit_fit = hawks[bi].copy(), float(fit[bi])
        if Xv is not None:
            vbest, vfit = common.validation_pick(hawks, fit, X, Y, Xv, Yv, vbest, vfit)

    return (vbest if Xv is not None else rabbit), (vfit if Xv is not None else rabbit_fit)


def aco_phase(X, Y, seed, generations, center, Xv=None, Yv=None, refit=False):
    rng = np.random.default_rng(seed)
    archive = common.init_population(rng, center, refit=refit)
    fit = common.population_fit(archive, X, Y)
    elite_n, q, xi = 8, 0.35, 0.85
    vbest, vfit = None, math.inf
    if Xv is not None:
        vbest, vfit = common.validation_pick(archive, fit, X, Y, Xv, Yv, vbest, vfit)

    for _ in range(generations):
        order = np.argsort(fit)
        elite, efit = archive[order[:elite_n]], fit[order[:elite_n]]
        ranks = np.arange(elite_n)
        w = np.exp(-(ranks ** 2) / (2 * (q * elite_n) ** 2))
        w /= w.sum()

        samples = []
        for _j in range(POP_SIZE):
            k = int(rng.choice(elite_n, p=w))
            sigma = xi * np.mean(np.abs(elite[k] - elite), axis=0) + 1e-3 * SPAN
            samples.append(
                np.clip(elite[k] + rng.normal(0, 1, PARAM_DIM) * sigma, LOWER, UPPER)
            )

        cand = np.stack(samples)
        cfit = common.population_fit(cand, X, Y)
        archive = np.vstack([elite, cand])
        fit = np.concatenate([efit, cfit])
        keep = np.argsort(fit)[:POP_SIZE]
        archive, fit = archive[keep], fit[keep]

        if Xv is not None:
            vbest, vfit = common.validation_pick(archive, fit, X, Y, Xv, Yv, vbest, vfit)

    bi = int(np.argmin(fit))
    return (vbest if Xv is not None else archive[bi].copy()), (
        vfit if Xv is not None else float(fit[bi])
    )


def bat_phase(X, Y, seed, generations, center, Xv=None, Yv=None, refit=False):
    rng = np.random.default_rng(seed)
    x = common.init_population(rng, center, refit=refit)
    v = np.zeros_like(x)
    fit = common.population_fit(x, X, Y)
    bi = int(np.argmin(fit))
    best, best_fit = x[bi].copy(), float(fit[bi])
    A = np.full(len(x), 0.9)
    pulse = np.full(len(x), 0.5)
    vbest, vfit = None, math.inf

    if Xv is not None:
        vbest, vfit = common.validation_pick(x, fit, X, Y, Xv, Yv, vbest, vfit)

    for _ in range(generations):
        for i in range(len(x)):
            freq = 2 * rng.random()
            v[i] = v[i] + (x[i] - best) * freq
            cand = x[i] + v[i]
            if rng.random() > pulse[i]:
                local_sigma = common.REFIT_SIGMA if refit else (0.05 * SPAN)
                cand = best + rng.normal(0, 1, PARAM_DIM) * local_sigma
            cand = np.clip(cand, LOWER, UPPER)
            cf = common.training_loss(cand, X, Y)
            if cf < fit[i] and rng.random() < A[i]:
                x[i], fit[i] = cand, cf
                A[i] *= 0.97
                pulse[i] = min(0.95, pulse[i] + 0.01)
            if cf < best_fit:
                best, best_fit = cand.copy(), float(cf)

        if Xv is not None:
            vbest, vfit = common.validation_pick(x, fit, X, Y, Xv, Yv, vbest, vfit)

    return (vbest if Xv is not None else best), (vfit if Xv is not None else best_fit)


PHASE = {"WOA": woa_phase, "HHO": hho_phase, "ACO": aco_phase, "BAT": bat_phase}
SEED_BASE = {"WOA": 98110, "HHO": 108110, "ACO": 118110, "BAT": 128110}


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
        "WOA": {"population": POP_SIZE, "a_schedule": "2_to_0", "a2_schedule": "-1_to_-2"},
        "HHO": {"population": POP_SIZE, "energy_schedule": "2_to_0", "rapid_dives": "Levy_scaled_to_parameter_span"},
        "ACO": {"population": POP_SIZE, "elite_archive": 8, "q": 0.35, "xi": 0.85},
        "BAT": {"population": POP_SIZE, "A0": 0.9, "pulse0": 0.5, "freq_range": [0.0, 2.0]},
    }[method]

    out = {
        "batch_id": "VW_MIDAS_ELMFIS_META_BATCH_3_V1",
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

    path = Path(f"vw_midas_elmfis_meta_batch_3_v1_{method.lower()}_result.json")
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
