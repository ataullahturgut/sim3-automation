"""Independent audit 2026-10-12 — what accuracy do our LABEL CONSTRUCTIONS produce with ZERO predictability?

Pure simulation (no market data, no model, no Neon access). Prices follow a driftless Gaussian random walk,
so any directional accuracy above 50% comes only from information already contained in the label/feature
timing. Reproduces every simulated number quoted in
GOLD_AUDIT_20261012_INDEPENDENT_SCIENTIFIC_AUDIT_ROOT_CAUSE_AND_ROADMAP.md.

  python3 gold_axis_2026/tools/gold_audit_20261012_label_structure_null_sim.py
"""
import numpy as np

N = 200_000


def monthly(rng, n=21):
    # target: log(avg(M+1)/avg(M)) as in vw_midas_* `y = log(M[target]/M[p])`; origin = end of month M
    p = np.cumsum(rng.standard_normal((N, 2 * n)), 1)
    a0, a1, pend = p[:, :n].mean(1), p[:, n:].mean(1), p[:, n - 1]
    y = a1 - a0
    age = np.arange(n - 1, 0, -1)
    w = np.exp(-0.1 * age); w /= w.sum()  # VW weights as in weighted_daily_return() with lam=0.1 (z=0)
    vw = (np.diff(p[:, :n], axis=1) * w).sum(1)
    return {
        "dir_acc_sign(P_end-A_M)": np.mean(np.sign(pend - a0) == np.sign(y)),
        "dir_acc_sign(VW)": np.mean(np.sign(vw) == np.sign(y)),
        "corr(VW, P_end-A_M)": np.corrcoef(vw, pend - a0)[0, 1],
        "MAE_last_price / MAE_prev_average(RW used in repo)": np.mean(abs(a1 - pend)) / np.mean(abs(y)),
    }


def h3(rng, h=24):
    q = np.cumsum(rng.standard_normal((N, 5 * h)), 1)
    am_t, cut, am_t3 = q[:, 10], q[:, 20], q[:, 3 * h + 10]          # LBMA-AM-like P[t]; 16NY feature cutoff
    m_t, m_t3 = q[:, :h].mean(1), q[:, 3 * h:4 * h].mean(1)           # UTC daily-mean P[t] (2026 sqld)
    iss = q[:, h + 12]                                                 # 08:00 NY on issue date
    return {
        "AM label: dir_acc_sign(P_cutoff-P_t)": np.mean(np.sign(cut - am_t) == np.sign(am_t3 - am_t)),
        "daily-mean label: dir_acc_sign(P_cutoff-P_t)": np.mean(np.sign(cut - m_t) == np.sign(m_t3 - m_t)),
        "daily-mean label: dir_acc_sign(P_issue08NY-P_t)": np.mean(np.sign(iss - m_t) == np.sign(m_t3 - m_t)),
    }


def cig(rng, h=24):
    c = np.cumsum(rng.standard_normal((N, 2 * h)), 1)
    am0, am1, cut = c[:, 10], c[:, h + 10], c[:, 21]
    return {"AM(D-1)->AM(D) label: dir_acc_sign(P_cutoff(D-1)-AM(D-1))": np.mean(np.sign(cut - am0) == np.sign(am1 - am0))}


def null_max_envelope(rng):
    out = {}
    for n in (120, 200, 250):
        for k in (10, 50, 100, 375):
            m = (rng.binomial(n, 0.5, size=(20_000, k)) / n).max(1)
            out[f"N={n},K={k}"] = (round(m.mean(), 3), round(float(np.quantile(m, .95)), 3))
    return out


def break_even(mean_abs_pct, round_trip_cost_pct):
    # expected gross edge per trade (2p-1)*m must exceed cost c  ->  p* = 0.5 + c/(2m)
    return 0.5 + round_trip_cost_pct / (2 * mean_abs_pct)


if __name__ == "__main__":
    for name, fn, seed in (("MONTHLY", monthly, 1), ("H3", h3, 7), ("CIG-D1", cig, 7)):
        print(name, {k: round(float(v), 4) for k, v in fn(np.random.default_rng(seed)).items()})
    print("NULL max-accuracy envelope (mean, 95%):", null_max_envelope(np.random.default_rng(3)))
    for lab, m in (("OVN 2025 (R65 0.6541%)", 0.6541), ("DAY 2025 (R65 0.4842%)", 0.4842), ("OVN 2026 (R65 1.0598%)", 1.0598)):
        print("break-even accuracy", lab, {c: round(break_even(m, c), 3) for c in (0.05, 0.10, 0.20, 0.30, 0.50)})
