from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy.stats import norm

from gold_axis_2026.v157_thesis import run_v157_breakaware_realized_moments as core


def load_realized_moments(conn, contract: dict) -> pd.DataFrame:
    """Frozen realized moments with BPV pairs restricted to truly adjacent valid returns."""
    w = contract["windows"]
    s = contract["source"]["realized_moment_session"]
    d = core.q(
        conn,
        """
        WITH session_bars AS (
          SELECT observation_ts,
                 close::double precision AS close,
                 (observation_ts AT TIME ZONE 'America/New_York')::date AS date,
                 (observation_ts AT TIME ZONE 'America/New_York')::time AS ny_time
          FROM xau_intraday_research_cache_1m
          WHERE observation_ts >= %s::timestamptz
            AND observation_ts < (%s::date + interval '1 day')
            AND close > 0
            AND (observation_ts AT TIME ZONE 'America/New_York')::time >= %s::time
            AND (observation_ts AT TIME ZONE 'America/New_York')::time <= %s::time
        ), lagged AS (
          SELECT *,
                 lag(close) OVER (PARTITION BY date ORDER BY observation_ts) AS prev_close,
                 lag(observation_ts) OVER (PARTITION BY date ORDER BY observation_ts) AS prev_ts
          FROM session_bars
        ), returns AS (
          SELECT date, observation_ts,
                 CASE
                   WHEN prev_close > 0
                    AND extract(epoch FROM (observation_ts-prev_ts)) > 0
                    AND extract(epoch FROM (observation_ts-prev_ts)) <= %s
                   THEN ln(close/prev_close)
                 END AS r
          FROM lagged
        ), paired AS (
          SELECT date, observation_ts, r,
                 lag(r) OVER (PARTITION BY date ORDER BY observation_ts) AS prev_r
          FROM returns
        )
        SELECT date,
               count(r)::integer AS rm_n,
               sum(r*r) FILTER (WHERE r IS NOT NULL)::double precision AS rm_rv,
               sum(CASE WHEN r < 0 THEN r*r ELSE 0 END) FILTER (WHERE r IS NOT NULL)::double precision AS rm_rsv_neg,
               sum(CASE WHEN r >= 0 THEN r*r ELSE 0 END) FILTER (WHERE r IS NOT NULL)::double precision AS rm_rsv_pos,
               sum(r*r*r) FILTER (WHERE r IS NOT NULL)::double precision AS rm_m3,
               sum(r*r*r*r) FILTER (WHERE r IS NOT NULL)::double precision AS rm_m4,
               (pi()/2.0 * sum(abs(r)*abs(prev_r)) FILTER (WHERE r IS NOT NULL AND prev_r IS NOT NULL))::double precision AS rm_bpv,
               max(abs(r)) FILTER (WHERE r IS NOT NULL)::double precision AS rm_max_abs,
               max(observation_ts) FILTER (WHERE r IS NOT NULL) AS rm_last_ts
        FROM paired
        GROUP BY date
        ORDER BY date
        """,
        (w["data_start"], w["test_end"], s["start"], s["end"], int(s["maximum_gap_seconds"])),
    )
    if d.empty:
        raise RuntimeError("BLOCKED_REALIZED_MOMENTS_EMPTY")
    d["date"] = pd.to_datetime(d["date"])
    d["rm_last_ts"] = pd.to_datetime(d["rm_last_ts"], utc=True)
    for c in ["rm_n", "rm_rv", "rm_rsv_neg", "rm_rsv_pos", "rm_m3", "rm_m4", "rm_bpv", "rm_max_abs"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    n = d["rm_n"].astype(float)
    rv = d["rm_rv"].astype(float)
    d["rm_vol"] = np.sqrt(rv.clip(lower=0.0))
    d["rm_downside_share"] = d["rm_rsv_neg"] / rv.replace(0, np.nan)
    d["rm_skew"] = np.sqrt(n) * d["rm_m3"] / np.power(rv.replace(0, np.nan), 1.5)
    d["rm_kurt"] = n * d["rm_m4"] / np.power(rv.replace(0, np.nan), 2.0)
    d["rm_jump_fraction"] = np.maximum(0.0, 1.0 - d["rm_bpv"] / rv.replace(0, np.nan))
    min_n = int(s["minimum_valid_returns"])
    moment_cols = contract["realized_moment_features"]
    finite = np.isfinite(d[moment_cols].to_numpy(dtype=float)).all(axis=1)
    d["rm_valid"] = d["rm_n"].ge(min_n) & finite
    d.loc[~d["rm_valid"], moment_cols] = np.nan
    return d


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
    d = lb - lc
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


# Implementation corrections discovered before reading V1.57 scoring output.
# They do not change the frozen candidate family, thresholds, horizons or model parameters.
core.load_realized_moments = load_realized_moments
core.hac_dm_hln = hac_dm_hln


def main() -> None:
    core.main()


if __name__ == "__main__":
    main()
