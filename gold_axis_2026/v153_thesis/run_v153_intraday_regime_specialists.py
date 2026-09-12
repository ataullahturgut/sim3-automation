from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from scipy.stats import binomtest
from sklearn.metrics import balanced_accuracy_score

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v153_thesis/contracts/v153_intraday_regime_specialists_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v153_thesis"


def q(conn, sql: str, params=None) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn, params=params)


def load_daily_intraday_state(conn, start: str, end: str) -> pd.DataFrame:
    sql = r"""
    WITH raw AS (
      SELECT observation_ts,
             close::double precision AS close,
             ((observation_ts AT TIME ZONE 'America/New_York') + interval '7 hours')::date AS trade_date,
             (observation_ts AT TIME ZONE 'America/New_York')::time AS ny_time,
             date_bin(interval '5 minutes', observation_ts, timestamptz '2000-01-01 00:00:00+00') AS bucket5
      FROM xau_intraday_research_cache_1m
      WHERE observation_ts >= %s::timestamptz
        AND observation_ts < (%s::date + interval '2 day')
        AND close > 0
    ), five AS (
      SELECT DISTINCT ON (trade_date,bucket5)
             trade_date,bucket5,observation_ts,close
      FROM raw
      ORDER BY trade_date,bucket5,observation_ts DESC
    ), five_ret AS (
      SELECT trade_date,bucket5,close,
             ln(close / lag(close) OVER (PARTITION BY trade_date ORDER BY bucket5)) AS r5
      FROM five
    ), rv AS (
      SELECT trade_date,
             count(r5) AS n5,
             sum(r5*r5) FILTER (WHERE r5 > 0) AS rs_plus,
             sum(r5*r5) FILTER (WHERE r5 < 0) AS rs_minus,
             sum(r5*r5) AS rv
      FROM five_ret
      GROUP BY trade_date
    ), endpoints AS (
      SELECT trade_date,
             max(close) FILTER (WHERE ny_time='03:29:00') AS c0329,
             max(close) FILTER (WHERE ny_time='07:59:00') AS c0759,
             max(close) FILTER (WHERE ny_time='16:59:00') AS c1659
      FROM raw
      GROUP BY trade_date
    )
    SELECT r.trade_date,r.n5,r.rs_plus,r.rs_minus,r.rv,e.c0329,e.c0759,e.c1659
    FROM rv r
    LEFT JOIN endpoints e USING(trade_date)
    WHERE r.trade_date >= %s::date
      AND r.trade_date <= %s::date
    ORDER BY r.trade_date
    """
    d = q(conn, sql, (start, end, start, end))
    d["trade_date"] = pd.to_datetime(d["trade_date"])
    for c in ["n5","rs_plus","rs_minus","rv","c0329","c0759","c1659"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    return d


def add_semivariance_state(d: pd.DataFrame, contract: dict) -> pd.DataFrame:
    d = d.copy().sort_values("trade_date").reset_index(drop=True)
    cfg = contract["specialists"]["RSV_TTSM_S2_1D"]
    min_n = int(cfg["minimum_5min_returns_per_trade_day"])
    good = d["n5"].ge(min_n)
    rp = d["rs_plus"].where(good)
    rm = d["rs_minus"].where(good)
    win = int(cfg["semivariance_window_trade_days"])
    ref = int(cfg["semivariance_reference_window_trade_days"])
    pct = float(cfg["semivariance_percentile"])
    d["rs5_plus"] = rp.rolling(win, min_periods=win).sum()
    d["rs5_minus"] = rm.rolling(win, min_periods=win).sum()
    # Literature rule uses a rolling historical distribution including the current observable day.
    d["q80_plus"] = d["rs5_plus"].rolling(ref, min_periods=ref).quantile(pct)
    d["q80_minus"] = d["rs5_minus"].rolling(ref, min_periods=ref).quantile(pct)
    d["europe_ret"] = np.where(
        d["c0329"].gt(0) & d["c0759"].gt(0),
        np.log(d["c0759"] / d["c0329"]),
        np.nan,
    )
    return d


def exact_origin_frame(daily: pd.DataFrame, contract: dict) -> pd.DataFrame:
    x = daily[daily["c1659"].gt(0)].copy().sort_values("trade_date").reset_index(drop=True)
    x["prev_close"] = x["c1659"].shift(1)
    x["next_close"] = x["c1659"].shift(-1)
    x["ret_origin"] = np.log(x["c1659"] / x["prev_close"])
    x["ret_next"] = np.log(x["next_close"] / x["c1659"])
    x["target_sign"] = np.sign(x["ret_next"]).replace(0, np.nan)

    tcfg = contract["specialists"]["RSV_TTSM_S2_1D"]
    look = int(tcfg["momentum_lookback_exact_origins"])
    x["mom20"] = np.log(x["c1659"] / x["c1659"].shift(look))
    x["mom_sign"] = np.sign(x["mom20"])
    hp = x["rs5_plus"] > x["q80_plus"]
    hm = x["rs5_minus"] > x["q80_minus"]
    ready = x[["q80_plus","q80_minus","rs5_plus","rs5_minus","mom20"]].notna().all(axis=1) & x["mom_sign"].ne(0)
    sig = pd.Series(0, index=x.index, dtype="int64")
    both_low = ready & ~hp & ~hm
    both_high = ready & hp & hm
    minus_only = ready & ~hp & hm
    plus_only = ready & hp & ~hm
    sig.loc[both_low] = x.loc[both_low, "mom_sign"].astype(int)
    sig.loc[minus_only & x["mom_sign"].gt(0)] = -1
    sig.loc[plus_only & x["mom_sign"].lt(0)] = 1
    # both_high and asymmetric same-direction cases remain NO_SIGNAL under TTSM-S2.
    x["sig_ttsm_s2"] = sig
    x["tts_region"] = np.select(
        [both_high, minus_only, both_low, plus_only],
        ["R1_BOTH_HIGH", "R2_MINUS_HIGH", "R3_BOTH_LOW", "R4_PLUS_HIGH"],
        default="NOT_READY",
    )

    dcfg = contract["specialists"]["MODERATE_DOWNSHOCK_REVERSAL_1D"]
    lb = int(dcfg["lookback_exact_origin_returns"])
    mn = int(dcfg["minimum_history"])
    hist_abs = x["ret_origin"].abs().shift(1)
    x["down_q50"] = hist_abs.rolling(lb, min_periods=mn).quantile(float(dcfg["lower_quantile"]))
    x["down_q75"] = hist_abs.rolling(lb, min_periods=mn).quantile(float(dcfg["upper_quantile"]))
    down_ready = x[["ret_origin","down_q50","down_q75"]].notna().all(axis=1)
    down_gate = down_ready & x["ret_origin"].lt(0) & x["ret_origin"].abs().gt(x["down_q50"]) & x["ret_origin"].abs().le(x["down_q75"])
    x["sig_downshock"] = np.where(down_gate, 1, 0).astype(int)

    x["sig_europe"] = np.sign(x["europe_ret"]).fillna(0).astype(int)
    return x


def metric(x: pd.DataFrame, signal_col: str) -> dict:
    z = x[x[signal_col].isin([-1,1]) & x["target_sign"].isin([-1,1])].copy()
    if z.empty:
        return {"n": 0, "status": "NO_SIGNAL"}
    hit = (z[signal_col].astype(int) == z["target_sign"].astype(int))
    signed = z[signal_col].astype(float) * z["ret_next"].astype(float)
    y = (z["target_sign"] > 0).astype(int)
    yh = (z[signal_col] > 0).astype(int)
    return {
        "n": int(len(z)),
        "hits": int(hit.sum()),
        "selective_accuracy": float(hit.mean()),
        "balanced_accuracy": float(balanced_accuracy_score(y, yh)) if y.nunique() > 1 else None,
        "exact_binomial_one_sided_p": float(binomtest(int(hit.sum()), int(len(z)), p=0.5, alternative="greater").pvalue),
        "median_signed_next_log_return": float(np.median(signed)),
        "up_signal_rate": float((z[signal_col] > 0).mean()),
    }


def score_periods(x: pd.DataFrame, contract: dict) -> dict:
    w = contract["windows"]
    periods = {
        "FORMATION_PRE2025": (w["source_start"], w["formation_end"]),
        "VALIDATION_2025_RETROSPECTIVE": (w["validation_start"], w["validation_end"]),
        "TEST_2026_RETROSPECTIVE_AVAILABLE_CACHE": (w["test_start"], w["test_end"]),
    }
    signals = {
        "RSV_TTSM_S2_1D": "sig_ttsm_s2",
        "MODERATE_DOWNSHOCK_REVERSAL_1D": "sig_downshock",
        "EUROPE_SESSION_CONTINUATION_1D": "sig_europe",
    }
    out = {}
    for label, (a,b) in periods.items():
        g = x[(x["trade_date"] >= pd.Timestamp(a)) & (x["trade_date"] <= pd.Timestamp(b))].copy()
        valid_target_n = int(g["target_sign"].isin([-1,1]).sum())
        out[label] = {"valid_target_n": valid_target_n}
        for sid,col in signals.items():
            m = metric(g, col)
            m["coverage"] = 0.0 if valid_target_n == 0 else float(m.get("n",0) / valid_target_n)
            out[label][sid] = m
        # Raw 20-origin momentum benchmark for the semivariance specialist.
        g["sig_raw_mom20"] = np.sign(g["mom20"]).fillna(0).astype(int)
        m = metric(g, "sig_raw_mom20")
        m["coverage"] = 0.0 if valid_target_n == 0 else float(m.get("n",0) / valid_target_n)
        out[label]["RAW_MOM20_BENCHMARK"] = m
    return out


def main() -> None:
    contract = json.loads(CONTRACT.read_text())
    if contract["status"] != "FROZEN_BEFORE_V153_2025_2026_SUCCESSOR_SCORING":
        raise RuntimeError("CONTRACT_NOT_FROZEN")
    if contract["governance"]["production_authority"]:
        raise RuntimeError("PRODUCTION_AUTHORITY_MUST_BE_FALSE")
    db = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not db:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    with psycopg.connect(db) as conn:
        daily = load_daily_intraday_state(conn, contract["windows"]["source_start"], contract["windows"]["test_end"])
    daily = add_semivariance_state(daily, contract)
    exact = exact_origin_frame(daily, contract)
    results = score_periods(exact, contract)
    report = {
        "contract_id": contract["contract_id"],
        "evidence_class": contract["evidence_class"],
        "source_days": int(len(daily)),
        "exact_origin_rows": int(len(exact)),
        "first_trade_date": daily["trade_date"].min().date().isoformat(),
        "last_trade_date": daily["trade_date"].max().date().isoformat(),
        "results": results,
        "governance": contract["governance"],
        "notes": [
            "V1.53 scoring is retrospective because 2025-2026 outcomes were visible in predecessor research.",
            "The TTSM-S2 rule was frozen from published methodology before V1.53 successor scoring.",
            "Downshock and Europe-session specialists were frozen from pre-2025 formation diagnostics before V1.53 successor scoring.",
            "No production authority or production writes are created by this run."
        ],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    exact.to_csv(OUT / "v153_intraday_specialist_rows.csv", index=False)
    (OUT / "v153_intraday_regime_specialists_results.json").write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
