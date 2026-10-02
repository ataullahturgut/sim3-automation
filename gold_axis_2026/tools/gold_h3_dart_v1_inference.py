from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_dart_inference_out"))
OUT.mkdir(parents=True, exist_ok=True)

DART = ROOT / "gold_axis_2026" / "GOLD_H3_DART_V1_PREDICTIONS_2026-10-02.csv"
SENTRY = ROOT / "gold_axis_2026" / "GOLD_H3_SENTRY_V1_PREDICTIONS_2026-10-02.csv"

SEED = 20261002
REPS = 10000
BLOCKS = [5, 10]


def logloss_row(y, p):
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    y = np.asarray(y, int)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def metric_loss_arrays(y, cand, base):
    y = np.asarray(y, int)
    cand = np.asarray(cand, float)
    base = np.asarray(base, float)
    c_pred = (cand >= 0.5).astype(int)
    b_pred = (base >= 0.5).astype(int)

    # Differences are candidate - comparator.
    # For accuracy, positive is better.
    # For Brier/logloss, negative is better.
    return {
        "accuracy": (c_pred == y).astype(float) - (b_pred == y).astype(float),
        "brier": (cand - y) ** 2 - (base - y) ** 2,
        "logloss": logloss_row(y, cand) - logloss_row(y, base),
    }


def circular_block_bootstrap(diff, block_len, rng, reps=REPS):
    diff = np.asarray(diff, float)
    n = len(diff)
    if n == 0:
        raise ValueError("empty diff")
    nblocks = int(np.ceil(n / block_len))
    vals = np.empty(reps, float)

    batch = 500
    offsets = np.arange(block_len, dtype=int)
    for start_rep in range(0, reps, batch):
        m = min(batch, reps - start_rep)
        starts = rng.integers(0, n, size=(m, nblocks))
        idx = (starts[:, :, None] + offsets[None, None, :]) % n
        idx = idx.reshape(m, -1)[:, :n]
        vals[start_rep:start_rep + m] = diff[idx].mean(axis=1)
    return vals


def summarize(diff, metric, block_len, seed_offset):
    obs = float(np.mean(diff))
    rng = np.random.default_rng(SEED + seed_offset)
    boot = circular_block_bootstrap(diff, block_len, rng)
    lo, hi = np.quantile(boot, [0.025, 0.975])

    if metric == "accuracy":
        improve_share = float(np.mean(boot > 0))
    else:
        improve_share = float(np.mean(boot < 0))

    return {
        "metric": metric,
        "block_len": int(block_len),
        "observed_diff": obs,
        "ci95_low": float(lo),
        "ci95_high": float(hi),
        "bootstrap_improve_share": improve_share,
        "reps": REPS,
    }


def load():
    d = pd.read_csv(DART)
    s = pd.read_csv(SENTRY)
    for x in [d, s]:
        x["forecast_issue_date"] = pd.to_datetime(x["forecast_issue_date"])
    s2 = s[["forecast_issue_date", "p_sentry"]].copy()
    x = d.merge(s2, on="forecast_issue_date", how="left", validate="one_to_one")
    if x.p_sentry.isna().any():
        raise RuntimeError("MISSING_SENTRY_MATCH")
    return x.sort_values("forecast_issue_date").reset_index(drop=True)


def main():
    x = load()

    comparisons = {
        "DART_vs_STRUCTURAL": ("p_dart", "p_structural"),
        "DART_vs_SENTRY": ("p_dart", "p_sentry"),
        "PATH_vs_STRUCTURAL": ("p_path_global", "p_structural"),
    }
    periods = {
        "2025": x.year == 2025,
        "2026": x.year == 2026,
        "2025-2026": x.year.isin([2025, 2026]),
    }

    rows = []
    seed_i = 0
    for period, mask in periods.items():
        z = x[mask].copy()
        y = z.y_up.to_numpy(int)
        for comp, (cand_col, base_col) in comparisons.items():
            diffs = metric_loss_arrays(y, z[cand_col], z[base_col])
            for metric, diff in diffs.items():
                for block_len in BLOCKS:
                    seed_i += 1
                    rows.append({
                        "period": period,
                        "comparison": comp,
                        "n": int(len(z)),
                        **summarize(diff, metric, block_len, seed_i),
                    })

    tab = pd.DataFrame(rows)
    tab.to_csv(OUT / "dart_v1_inference_bootstrap.csv", index=False)

    # Compact headline table: block length 5 and 10 for accuracy and Brier.
    headline = tab[
        tab.metric.isin(["accuracy", "brier"])
    ].copy()

    summary = {
        "schema": "DART_H3_V1_INFERENCE_AUDIT",
        "bootstrap_reps": REPS,
        "block_lengths": BLOCKS,
        "results": tab.to_dict(orient="records"),
    }
    (OUT / "dart_v1_inference_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n"
    )

    lines = [
        "# DART-H3 V1 — DEPENDENCE-AWARE INFERENCE AUDIT", "",
        "Circular moving-block bootstrap; paired forecast-origin differences; 10,000 replicates.", "",
        "## Accuracy difference", "",
        "| Period | Comparison | Block | Observed | 95% interval | P(improvement) |",
        "|---|---|---:|---:|---:|---:|",
    ]
    acc = tab[tab.metric == "accuracy"]
    for r in acc.itertuples():
        lines.append(
            f"| {r.period} | {r.comparison} | {int(r.block_len)} | "
            f"{100*r.observed_diff:+.2f} pp | "
            f"[{100*r.ci95_low:+.2f}, {100*r.ci95_high:+.2f}] pp | "
            f"{100*r.bootstrap_improve_share:.1f}% |"
        )

    lines += ["", "## Brier difference", "",
              "Negative values favor the candidate.", "",
              "| Period | Comparison | Block | Observed | 95% interval | P(improvement) |",
              "|---|---|---:|---:|---:|---:|"]
    br = tab[tab.metric == "brier"]
    for r in br.itertuples():
        lines.append(
            f"| {r.period} | {r.comparison} | {int(r.block_len)} | "
            f"{r.observed_diff:+.4f} | "
            f"[{r.ci95_low:+.4f}, {r.ci95_high:+.4f}] | "
            f"{100*r.bootstrap_improve_share:.1f}% |"
        )

    lines += ["", "## Interpretation", "",
              "Intervals crossing zero imply the observed point-estimate advantage is not statistically decisive under that dependence sensitivity. "
              "This audit is descriptive robustness evidence and does not alter DART states or thresholds."]

    (OUT / "DART_V1_INFERENCE_RESULT.md").write_text("\n".join(lines) + "\n")
    print((OUT / "DART_V1_INFERENCE_RESULT.md").read_text())


if __name__ == "__main__":
    main()
