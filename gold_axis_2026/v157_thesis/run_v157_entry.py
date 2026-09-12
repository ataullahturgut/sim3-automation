from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy.stats import norm

from gold_axis_2026.v157_thesis import run_v157_breakaware_realized_moments as core


def hac_dm_hln(base: pd.DataFrame, challenger: pd.DataFrame, h: int) -> dict:
    """Aligned pinball-loss DM diagnostic with Bartlett HAC and HLN correction."""
    a = base[["origin_index", "target_return", "q25", "q50", "q75"]].copy()
    a = a.rename(columns={"q25": "bq25", "q50": "bq50", "q75": "bq75"})
    b = challenger[["origin_index", "q25", "q50", "q75"]].copy()
    b = b.rename(columns={"q25": "cq25", "q50": "cq50", "q75": "cq75"})
    m = a.merge(b, on="origin_index", how="inner")
    if len(m) < max(20, h + 5):
        return {"n": int(len(m)), "status": "INSUFFICIENT_ALIGNED"}
    lb = core.pinball_row(pd.DataFrame({
        "target_return": m["target_return"], "q25": m["bq25"], "q50": m["bq50"], "q75": m["bq75"]
    }))
    lc = core.pinball_row(pd.DataFrame({
        "target_return": m["target_return"], "q25": m["cq25"], "q50": m["cq50"], "q75": m["cq75"]
    }))
    d = lb - lc  # positive => challenger lower pinball loss
    n = len(d)
    mu = float(np.mean(d))
    u = d - mu
    lag = min(h - 1, n - 2)
    lrv = float(np.mean(u * u))
    for k in range(1, lag + 1):
        gamma = float(np.mean(u[k:] * u[:-k]))
        weight = 1.0 - k / (lag + 1.0)
        lrv += 2.0 * weight * gamma
    if not math.isfinite(lrv) or lrv <= 0:
        return {
            "n": int(n), "mean_loss_gain": mu,
            "base_mean_pinball_aligned": float(np.mean(lb)),
            "challenger_mean_pinball_aligned": float(np.mean(lc)),
            "status": "NONPOSITIVE_HAC_VARIANCE",
        }
    dm = mu / math.sqrt(lrv / n)
    factor2 = (n + 1.0 - 2.0 * h + h * (h - 1.0) / n) / n
    hln = dm * math.sqrt(max(factor2, 0.0))
    return {
        "n": int(n),
        "mean_loss_gain": mu,
        "base_mean_pinball_aligned": float(np.mean(lb)),
        "challenger_mean_pinball_aligned": float(np.mean(lc)),
        "hac_lag": int(lag),
        "dm_stat": float(dm),
        "hln_dm_stat": float(hln),
        "pvalue_one_sided_challenger_better": float(norm.sf(hln)),
        "status": "OK",
    }


# Patch before core.main executes. The frozen scientific specification is unchanged;
# this entrypoint only corrects the implementation of the pre-specified comparison statistic.
core.hac_dm_hln = hac_dm_hln


def main() -> None:
    core.main()


if __name__ == "__main__":
    main()
