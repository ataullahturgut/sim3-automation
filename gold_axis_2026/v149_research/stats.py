from __future__ import annotations

import math
import numpy as np


def normal_pvalue(z: float) -> float:
    return float(math.erfc(abs(float(z)) / math.sqrt(2.0)))


def hac_mean_test(diff, lag: int = 1) -> dict:
    """Two-sided equal-predictive-accuracy test with Newey-West variance."""
    x = np.asarray(diff, float)
    n = len(x)
    if n < max(12, 4 * (lag + 1)):
        return {"status": "BLOCKED_INSUFFICIENT_SAMPLE", "n": n}
    u = x - x.mean()
    long_var = float(u @ u / n)
    for k in range(1, lag + 1):
        gamma = float(u[k:] @ u[:-k] / n)
        long_var += 2.0 * (1.0 - k / (lag + 1.0)) * gamma
    if long_var <= 1e-15:
        return {"status": "NOT_PROVEN_ZERO_VARIANCE", "n": n, "mean_diff": float(x.mean())}
    stat = float(x.mean() / math.sqrt(long_var / n))
    return {
        "status": "COMPUTED",
        "n": n,
        "lag": lag,
        "mean_diff": float(x.mean()),
        "statistic": stat,
        "p_value_two_sided": normal_pvalue(stat),
    }


def conditional_predictive_ability(diff, state, lag: int = 1) -> dict:
    """HAC Wald test of E[h_t*d_t]=0 using pre-origin state instruments."""
    d = np.asarray(diff, float)
    z = np.asarray(state, float)
    n = len(d)
    if n < 24 or z.ndim != 2 or len(z) != n:
        return {"status": "BLOCKED_INSUFFICIENT_SAMPLE", "n": n}
    g = z * d[:, None]
    mean = g.mean(axis=0)
    centered = g - mean
    omega = centered.T @ centered / n
    for k in range(1, lag + 1):
        gamma = centered[k:].T @ centered[:-k] / n
        omega += (1.0 - k / (lag + 1.0)) * (gamma + gamma.T)
    try:
        wald = float(n * mean @ np.linalg.pinv(omega) @ mean)
    except np.linalg.LinAlgError:
        return {"status": "NOT_PROVEN_SINGULAR", "n": n}
    # Conservative chi-square tail upper bound; exact scipy use is optional.
    try:
        from scipy.stats import chi2
        p = float(chi2.sf(wald, z.shape[1]))
    except Exception:
        p = None
    return {"status": "COMPUTED", "n": n, "lag": lag, "df": int(z.shape[1]), "wald": wald, "p_value": p}


def circular_block_superior_set(losses: dict[str, np.ndarray], block: int, seed: int, reps: int = 2000) -> dict:
    names = sorted(losses)
    n = len(next(iter(losses.values())))
    if n < 40:
        return {"status": "BLOCKED_INSUFFICIENT_SAMPLE", "n": n, "formal_hansen_mcs": "NOT_PROVEN"}
    means = {k: float(np.mean(losses[k])) for k in names}
    best = min(names, key=lambda k: (means[k], k))
    rng = np.random.default_rng(seed)
    models = {}
    for name in names:
        x = np.asarray(losses[name]) - np.asarray(losses[best])
        observed = float(x.mean())
        centered = x - observed
        draws = np.empty(reps)
        for b in range(reps):
            out = []
            while len(out) < n:
                start = int(rng.integers(0, n))
                out.extend(centered[(np.arange(start, start + block) % n)].tolist())
            draws[b] = np.mean(out[:n])
        p = 1.0 if name == best else float((1 + np.sum(draws >= observed)) / (reps + 1))
        models[name] = {"mean_loss": means[name], "difference_vs_best": observed, "p_one_sided": p, "in_5pct_set": p >= 0.05}
    return {
        "status": "MCS_STYLE_DIAGNOSTIC",
        "formal_hansen_mcs": "NOT_PROVEN",
        "n": n,
        "block": block,
        "repetitions": reps,
        "best_point_estimate": best,
        "models": models,
    }
