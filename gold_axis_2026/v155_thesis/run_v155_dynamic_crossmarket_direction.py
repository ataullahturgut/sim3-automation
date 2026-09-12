from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, brier_score_loss, log_loss, matthews_corrcoef
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v155_thesis/contracts/v155_dynamic_crossmarket_direction_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v155_thesis"
SEED = 20260912

PIT_SERIES = {
    "dgs10": "DGS10_ALFRED_PIT_ME",
    "dff": "DFF_ALFRED_PIT_ME",
    "fx": "DEXCHUS_ALFRED_PIT_ME",
}
EQUITY_SERIES = {
    "nasdaq": "NASDAQ100_FRED",
    "sp500": "SP500_FRED",
    "djia": "DJIA_FRED",
}
PRECIOUS_SERIES = {
    "xag": "XAG_STAKTRAKR_RESEARCH_DAILY_R1",
    "xpt": "XPT_STAKTRAKR_RESEARCH_DAILY_R1",
    "xpd": "XPD_STAKTRAKR_RESEARCH_DAILY_R1",
}


def q(conn, sql: str, params=None) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn, params=params)


def load_gold_endpoint(conn, start: str, end: str) -> pd.DataFrame:
    d = q(
        conn,
        """
        WITH x AS (
          SELECT observation_ts,
                 close::double precision AS close,
                 (observation_ts AT TIME ZONE 'America/New_York')::date AS date,
                 (observation_ts AT TIME ZONE 'America/New_York')::time AS ny_time
          FROM xau_intraday_research_cache_1m
          WHERE observation_ts >= %s::timestamptz
            AND observation_ts < (%s::date + interval '1 day')
            AND close > 0
        )
        SELECT date,
               max(observation_ts) FILTER (WHERE ny_time=time '13:29:00') AS observation_ts,
               max(close) FILTER (WHERE ny_time=time '03:29:00') AS c0329,
               max(close) FILTER (WHERE ny_time=time '07:59:00') AS c0759,
               max(close) FILTER (WHERE ny_time=time '08:29:00') AS c0829,
               max(close) FILTER (WHERE ny_time=time '13:29:00') AS close
        FROM x
        GROUP BY date
        HAVING max(close) FILTER (WHERE ny_time=time '13:29:00') IS NOT NULL
        ORDER BY date
        """,
        (start, end),
    )
    if d.empty:
        raise RuntimeError("BLOCKED_GOLD_1329_EMPTY")
    d["date"] = pd.to_datetime(d["date"])
    d["observation_ts"] = pd.to_datetime(d["observation_ts"], utc=True)
    for c in ["c0329", "c0759", "c0829", "close"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d.sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)
    return d


def load_observations(conn, ids: list[str], end: str) -> pd.DataFrame:
    d = q(
        conn,
        """
        SELECT series_id,observation_ts,value,available_as_of,retrieved_at
        FROM observations
        WHERE series_id=ANY(%s)
          AND observation_ts < (%s::date + interval '2 day')
        ORDER BY series_id,observation_ts,retrieved_at
        """,
        (ids, end),
    )
    if d.empty:
        return d
    d["observation_ts"] = pd.to_datetime(d["observation_ts"], utc=True)
    d["available_as_of"] = pd.to_datetime(d["available_as_of"], utc=True)
    d["retrieved_at"] = pd.to_datetime(d["retrieved_at"], utc=True)
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    return d


def _rsi(s: pd.Series, window: int = 14) -> pd.Series:
    delta = s.diff()
    gain = delta.clip(lower=0).rolling(window, min_periods=window).mean()
    loss = (-delta.clip(upper=0)).rolling(window, min_periods=window).mean()
    rs = gain / loss.replace(0, np.nan)
    out = 100.0 - 100.0 / (1.0 + rs)
    out = out.where(loss.ne(0), 100.0)
    out = out.where(gain.ne(0), 0.0)
    return out


def _fast_role(close: pd.Series) -> pd.Series:
    ma = close.rolling(20, min_periods=20).mean()
    raw = np.sign(close - ma)
    out = pd.Series(np.nan, index=close.index, dtype=float)
    ready = ma.notna() & ma.shift(1).notna()
    out.loc[ready] = 0.0
    out.loc[ready & raw.eq(1) & raw.shift(1).eq(1)] = 1.0
    out.loc[ready & raw.eq(-1) & raw.shift(1).eq(-1)] = -1.0
    return out


def _slow_role_at(d: pd.DataFrame, i: int) -> float:
    asof = pd.Timestamp(d.loc[i, "date"])
    x = d.loc[: i - 1, ["date", "close"]].copy() if i > 0 else d.iloc[0:0][["date", "close"]].copy()
    if x.empty:
        return np.nan
    x = x.sort_values("date").set_index("date")
    current_week_end = asof.to_period("W-FRI").end_time.normalize()
    weekly = x["close"].resample("W-FRI").last().dropna()
    weekly = weekly.loc[weekly.index < current_week_end]
    if len(weekly) < 5:
        return np.nan
    ma = weekly.rolling(4, min_periods=4).mean()
    cur = np.sign(float(weekly.iloc[-1]) - float(ma.iloc[-1]))
    prev = np.sign(float(weekly.iloc[-2]) - float(ma.iloc[-2]))
    if cur == prev == 1:
        return 1.0
    if cur == prev == -1:
        return -1.0
    return 0.0


def _monthly_direction_at(d: pd.DataFrame, i: int) -> float:
    asof = pd.Timestamp(d.loc[i, "date"])
    x = d.loc[: i - 1, ["date", "close"]].copy() if i > 0 else d.iloc[0:0][["date", "close"]].copy()
    if x.empty:
        return np.nan
    x = x.sort_values("date").set_index("date")
    completed = x.loc[x.index.to_period("M") < asof.to_period("M"), "close"]
    monthly = completed.resample("ME").last().dropna()
    mr = np.log(monthly).diff().dropna()
    if len(mr) < 3:
        return np.nan
    return float(np.sign(float(mr.iloc[-3:].mean())))


def add_gold_features(d: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    d = d.copy().sort_values("date").reset_index(drop=True)
    c = d["close"].astype(float)
    lp = np.log(c)
    r = lp.diff()
    cols: list[str] = []
    for k in range(1, 6):
        name = f"ret_lag{k}"
        d[name] = r.shift(k - 1)
        cols.append(name)
    for k in [3, 5, 10, 20, 50]:
        name = f"mom{k}"
        d[name] = lp - lp.shift(k)
        cols.append(name)
    for k in [5, 10, 20]:
        name = f"vol{k}"
        d[name] = r.rolling(k, min_periods=k).std(ddof=0)
        cols.append(name)
    d["rsi14"] = _rsi(c, 14) / 100.0
    ema12 = c.ewm(span=12, adjust=False, min_periods=12).mean()
    ema26 = c.ewm(span=26, adjust=False, min_periods=26).mean()
    d["macd_12_26"] = (ema12 - ema26) / c
    sma5 = c.rolling(5, min_periods=5).mean()
    sma20 = c.rolling(20, min_periods=20).mean()
    sma50 = c.rolling(50, min_periods=50).mean()
    d["sma5_over_sma20"] = sma5 / sma20 - 1.0
    d["sma20_over_sma50"] = sma20 / sma50 - 1.0
    sd20 = c.rolling(20, min_periods=20).std(ddof=0)
    d["bollinger_z20"] = (c - sma20) / sd20.replace(0, np.nan)
    cols.extend(["rsi14", "macd_12_26", "sma5_over_sma20", "sma20_over_sma50", "bollinger_z20"])

    d["europe_session_ret"] = np.where(d["c0329"].gt(0) & d["c0759"].gt(0), np.log(d["c0759"] / d["c0329"]), np.nan)
    d["us_morning_ret"] = np.where(d["c0759"].gt(0), np.log(d["close"] / d["c0759"]), np.nan)
    d["post_0829_ret"] = np.where(d["c0829"].gt(0), np.log(d["close"] / d["c0829"]), np.nan)
    cols.extend(["europe_session_ret", "us_morning_ret", "post_0829_ret"])

    d["fast_role"] = _fast_role(c)
    d["slow_role"] = [_slow_role_at(d, i) for i in range(len(d))]
    d["monthly_direction_3m"] = [_monthly_direction_at(d, i) for i in range(len(d))]
    cols.extend(["fast_role", "slow_role", "monthly_direction_3m"])
    return d, cols


def merge_pit_rates_fx(d: pd.DataFrame, obs: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    d = d.copy().sort_values("observation_ts")
    cols: list[str] = []
    for name, sid in PIT_SERIES.items():
        z = obs[obs["series_id"] == sid].copy()
        level = f"{name}_level"
        change = f"{name}_logdiff" if name == "fx" else f"{name}_delta"
        cols.extend([level, change])
        if z.empty:
            d[level] = np.nan
            d[change] = np.nan
            continue
        z = z[z["available_as_of"].notna() & z["value"].notna()].sort_values(["available_as_of", "retrieved_at"])
        z = z.drop_duplicates("available_as_of", keep="last")[["available_as_of", "value"]]
        z = z.rename(columns={"available_as_of": "avail", "value": level})
        if name == "fx":
            z[change] = np.log(z[level].astype(float)).diff()
        else:
            z[change] = z[level].astype(float).diff()
        d = pd.merge_asof(d.sort_values("observation_ts"), z.sort_values("avail"), left_on="observation_ts", right_on="avail", direction="backward", allow_exact_matches=True)
        if (d["avail"].notna() & (d["avail"] > d["observation_ts"])).any():
            raise RuntimeError(f"PIT_FUTURE_JOIN:{name}")
        d = d.drop(columns=["avail"])
    return d.sort_values("date").reset_index(drop=True), cols


def merge_lagged_daily(d: pd.DataFrame, obs: pd.DataFrame, mapping: dict[str, str]) -> tuple[pd.DataFrame, list[str]]:
    d = d.copy().sort_values("date")
    cols: list[str] = []
    for name, sid in mapping.items():
        col = f"{name}_ret"
        cols.append(col)
        z = obs[obs["series_id"] == sid].copy()
        if z.empty:
            d[col] = np.nan
            continue
        z["source_date"] = z["observation_ts"].dt.tz_convert("UTC").dt.tz_localize(None).dt.normalize()
        z = z[z["value"].notna()].sort_values(["source_date", "retrieved_at"]).drop_duplicates("source_date", keep="last")
        z[col] = np.log(z["value"].astype(float)).diff()
        z = z[["source_date", col]].dropna(subset=["source_date"]).sort_values("source_date")
        d = pd.merge_asof(d.sort_values("date"), z, left_on="date", right_on="source_date", direction="backward", allow_exact_matches=False)
        if (d["source_date"].notna() & (d["source_date"] >= d["date"])).any():
            raise RuntimeError(f"DAILY_LAG_VIOLATION:{name}")
        d = d.drop(columns=["source_date"])
    return d, cols


def build_panel(conn, contract: dict) -> tuple[pd.DataFrame, list[str], list[str]]:
    w = contract["windows"]
    d, base = add_gold_features(load_gold_endpoint(conn, w["data_start"], w["test_end"]))
    pit = load_observations(conn, list(PIT_SERIES.values()), w["test_end"])
    d, pit_cols = merge_pit_rates_fx(d, pit)
    daily = load_observations(conn, list(EQUITY_SERIES.values()) + list(PRECIOUS_SERIES.values()), w["test_end"])
    d, eq_cols = merge_lagged_daily(d, daily, EQUITY_SERIES)
    d, pm_cols = merge_lagged_daily(d, daily, PRECIOUS_SERIES)
    full = base + pit_cols + eq_cols + pm_cols
    return d.sort_values("date").reset_index(drop=True), base, full


def add_target(d: pd.DataFrame, h: int) -> pd.DataFrame:
    z = d.copy()
    z["target_close"] = z["close"].shift(-h)
    z["target_date"] = z["date"].shift(-h)
    z["target_return"] = np.log(z["target_close"] / z["close"])
    z["y"] = np.where(z["target_return"].notna(), (z["target_return"] > 0).astype(int), np.nan)
    z["origin_index"] = np.arange(len(z), dtype=int)
    return z


def estimator(kind: str, params: dict):
    if kind == "LOGIT":
        return make_pipeline(
            SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
            StandardScaler(),
            LogisticRegression(C=float(params["C"]), max_iter=int(params["max_iter"]), random_state=int(params["random_state"])),
        )
    if kind == "HGB":
        return make_pipeline(
            SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
            HistGradientBoostingClassifier(
                max_depth=int(params["max_depth"]),
                max_iter=int(params["max_iter"]),
                learning_rate=float(params["learning_rate"]),
                l2_regularization=float(params["l2_regularization"]),
                random_state=int(params["random_state"]),
            ),
        )
    if kind == "MLP16":
        return make_pipeline(
            SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
            StandardScaler(),
            MLPClassifier(
                hidden_layer_sizes=tuple(params["hidden_layer_sizes"]),
                alpha=float(params["alpha"]),
                max_iter=int(params["max_iter"]),
                early_stopping=bool(params["early_stopping"]),
                random_state=int(params["random_state"]),
            ),
        )
    raise KeyError(kind)


def _fit_model(model, kind: str, x: pd.DataFrame, y: pd.Series, weights: np.ndarray | None):
    if weights is None:
        return model.fit(x, y)
    step = {"LOGIT": "logisticregression", "HGB": "histgradientboostingclassifier", "MLP16": "mlpclassifier"}[kind]
    return model.fit(x, y, **{f"{step}__sample_weight": weights})


def sequential_candidate(z: pd.DataFrame, features: list[str], candidate_id: str, cfg: dict, params: dict, h: int, contract: dict) -> pd.DataFrame:
    min_train = int(contract["sequential_training"]["minimum_mature_labels"])
    start = pd.Timestamp(contract["sequential_training"]["prediction_start"])
    rows = []
    for t in range(len(z) - h):
        if pd.Timestamp(z.loc[t, "date"]) < start:
            continue
        mature = [j for j in range(t) if j + h <= t and pd.notna(z.loc[j, "y"])]
        if len(mature) < min_train:
            continue
        mode = cfg["fit_mode"]
        weights = None
        if mode == "ROLLING":
            mature = mature[-int(cfg["window"]):]
        elif mode == "EXP_WEIGHTED":
            ages = np.arange(len(mature) - 1, -1, -1, dtype=float)
            hl = float(cfg["half_life"])
            weights = np.exp(-math.log(2.0) * ages / hl)
        else:
            raise KeyError(mode)
        yy = z.loc[mature, "y"].astype(int)
        if yy.nunique() < 2:
            continue
        model = estimator(cfg["model"], params[cfg["model"]])
        _fit_model(model, cfg["model"], z.loc[mature, features], yy, weights)
        p = float(model.predict_proba(z.loc[[t], features])[0, 1])
        all_mature = [j for j in range(t) if j + h <= t and pd.notna(z.loc[j, "y"])]
        histfreq = (float(z.loc[all_mature, "y"].sum()) + 0.5) / (len(all_mature) + 1.0)
        rows.append({
            "origin_index": int(t),
            "origin_date": z.loc[t, "date"],
            "target_date": z.loc[t, "target_date"],
            "target_return": float(z.loc[t, "target_return"]),
            "y": int(z.loc[t, "y"]),
            "candidate": candidate_id,
            "p": float(np.clip(p, 1e-6, 1 - 1e-6)),
            "p_histfreq": float(np.clip(histfreq, 1e-6, 1 - 1e-6)),
            "train_n": int(len(mature)),
        })
    return pd.DataFrame(rows)


def _mean_logloss(prior: pd.DataFrame) -> float:
    p = np.clip(prior["p"].to_numpy(float), 1e-6, 1 - 1e-6)
    y = prior["y"].to_numpy(int)
    return float(np.mean(-(y * np.log(p) + (1 - y) * np.log(1 - p))))


def dynamic_layer(frames: dict[str, pd.DataFrame], h: int, contract: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    ids = list(frames)
    common = None
    for cid in ids:
        cur = frames[cid][["origin_index", "origin_date", "target_date", "target_return", "y", "p", "p_histfreq"]].copy()
        cur = cur.rename(columns={"p": f"p__{cid}"})
        keep = ["origin_index", "origin_date", "target_date", "target_return", "y", "p_histfreq", f"p__{cid}"] if common is None else ["origin_index", f"p__{cid}"]
        common = cur[keep] if common is None else common.merge(cur[keep], on="origin_index", how="inner")
    if common is None or common.empty:
        return pd.DataFrame(), pd.DataFrame()

    dma_cfg = contract["dynamic_layer"]["DMA_LOGLOSS63"]
    look = int(dma_cfg["lookback_mature_predictions"])
    min_mature = int(dma_cfg["minimum_mature_per_member"])
    eta = float(dma_cfg["eta"])
    histories = {cid: frames[cid].set_index("origin_index") for cid in ids}
    dma_rows = []
    dms_rows = []
    for _, r in common.iterrows():
        t = int(r["origin_index"])
        losses: dict[str, float] = {}
        valid = True
        for cid in ids:
            hm = histories[cid]
            prior = hm[(hm.index + h <= t)].tail(look)
            if len(prior) < min_mature:
                valid = False
                break
            losses[cid] = _mean_logloss(prior)
        if not valid:
            continue
        raw_w = {cid: math.exp(-eta * losses[cid]) for cid in ids}
        den = sum(raw_w.values())
        probs = {cid: float(r[f"p__{cid}"]) for cid in ids}
        p_dma = sum(raw_w[cid] * probs[cid] for cid in ids) / den
        best = min(ids, key=lambda cid: (losses[cid], cid))
        base = {
            "origin_index": t,
            "origin_date": r["origin_date"],
            "target_date": r["target_date"],
            "target_return": float(r["target_return"]),
            "y": int(r["y"]),
            "p_histfreq": float(r["p_histfreq"]),
            "member_losses": json.dumps(losses, sort_keys=True),
        }
        dma_rows.append({**base, "candidate": "DMA_LOGLOSS63", "p": float(np.clip(p_dma, 1e-6, 1 - 1e-6)), "selected_member": None})
        dms_rows.append({**base, "candidate": "DMS_LOGLOSS63", "p": probs[best], "selected_member": best})
    return pd.DataFrame(dma_rows), pd.DataFrame(dms_rows)


def metrics(f: pd.DataFrame, pcol: str = "p") -> dict:
    if f.empty:
        return {"n": 0, "status": "BLOCKED_EMPTY"}
    y = f["y"].astype(int).to_numpy()
    p = np.clip(f[pcol].to_numpy(float), 1e-6, 1 - 1e-6)
    pred = (p >= 0.5).astype(int)
    histp = np.clip(f["p_histfreq"].to_numpy(float), 1e-6, 1 - 1e-6)
    histpred = (histp >= 0.5).astype(int)
    return {
        "n": int(len(f)),
        "accuracy": float(accuracy_score(y, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "brier": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, p, labels=[0, 1])),
        "mcc": float(matthews_corrcoef(y, pred)),
        "actual_up_rate": float(np.mean(y)),
        "predicted_up_rate": float(np.mean(pred)),
        "histfreq_accuracy": float(accuracy_score(y, histpred)),
        "histfreq_balanced_accuracy": float(balanced_accuracy_score(y, histpred)),
        "balanced_gain_vs_histfreq": float(balanced_accuracy_score(y, pred) - balanced_accuracy_score(y, histpred)),
    }


def selective_metrics(f: pd.DataFrame, threshold: float) -> dict:
    if f.empty:
        return {"n": 0, "coverage": 0.0, "status": "BLOCKED_EMPTY"}
    p = f["p"].to_numpy(float)
    mask = np.abs(p - 0.5) >= threshold
    z = f.loc[mask].copy()
    if z.empty:
        return {"n": 0, "coverage": 0.0, "status": "NO_SIGNAL"}
    y = z["y"].astype(int).to_numpy()
    pred = (z["p"].to_numpy(float) >= 0.5).astype(int)
    return {
        "n": int(len(z)),
        "coverage": float(len(z) / len(f)),
        "selective_accuracy": float(accuracy_score(y, pred)),
        "selective_balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "mcc": float(matthews_corrcoef(y, pred)),
    }


def period_slice(f: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    a = pd.Timestamp(start)
    b = pd.Timestamp(end)
    return f[(f["origin_date"] >= a) & (f["origin_date"] <= b) & (f["target_date"] <= b)].copy()


def lane_gate(v: dict, t: dict, lane: str, contract: dict) -> dict:
    g = contract["evaluation"]["research_interest_gates"][lane]
    checks = {
        "validation_accuracy": v.get("accuracy", 0.0) >= float(g["accuracy_each_period_min"]),
        "validation_balanced": v.get("balanced_accuracy", 0.0) >= float(g["balanced_accuracy_each_period_min"]),
        "test_accuracy": t.get("accuracy", 0.0) >= float(g["accuracy_each_period_min"]),
        "test_balanced": t.get("balanced_accuracy", 0.0) >= float(g["balanced_accuracy_each_period_min"]),
    }
    return {"pass": bool(all(checks.values())), "checks": checks}


def selective_gate(v: dict, t: dict, contract: dict) -> dict:
    g = contract["evaluation"]["research_interest_gates"]["SELECTIVE"]
    checks = {
        "validation_accuracy": v.get("selective_accuracy", 0.0) >= float(g["selective_accuracy_each_period_min"]),
        "validation_coverage": v.get("coverage", 0.0) >= float(g["coverage_each_period_min"]),
        "test_accuracy": t.get("selective_accuracy", 0.0) >= float(g["selective_accuracy_each_period_min"]),
        "test_coverage": t.get("coverage", 0.0) >= float(g["coverage_each_period_min"]),
    }
    return {"pass": bool(all(checks.values())), "checks": checks}


def run_horizon(panel: pd.DataFrame, base_cols: list[str], full_cols: list[str], h: int, contract: dict) -> tuple[dict, pd.DataFrame]:
    z = add_target(panel, h)
    feature_sets = {"BASE": base_cols, "FULL": full_cols}
    frames: dict[str, pd.DataFrame] = {}
    for cid, cfg in contract["base_candidates"].items():
        frames[cid] = sequential_candidate(z, feature_sets[cfg["feature_set"]], cid, cfg, contract["model_parameters"], h, contract)
    dma, dms = dynamic_layer(frames, h, contract)
    frames["DMA_LOGLOSS63"] = dma
    frames["DMS_LOGLOSS63"] = dms

    w = contract["windows"]
    periods = {
        "FORMATION_2024": (w["formation_score_start"], w["formation_score_end"]),
        "VALIDATION_2025": (w["validation_start"], w["validation_end"]),
        "TEST_2026_AVAILABLE": (w["test_start"], w["test_end"]),
    }
    out = {"candidates": {}, "dynamic": {}}
    pred_rows = []
    for cid, f in frames.items():
        if f.empty:
            out["candidates" if cid not in {"DMA_LOGLOSS63", "DMS_LOGLOSS63"} else "dynamic"][cid] = {k: {"n": 0} for k in periods}
            continue
        block = {}
        for plabel, (a, b) in periods.items():
            g = period_slice(f, a, b)
            block[plabel] = metrics(g)
            gg = g.copy()
            gg["period"] = plabel
            gg["horizon"] = h
            pred_rows.append(gg)
        if cid == "DMA_LOGLOSS63":
            th = float(contract["dynamic_layer"]["DMA_SELECT60"]["probability_distance_from_half_min"])
            block["SELECTIVE60_VALIDATION_2025"] = selective_metrics(period_slice(f, w["validation_start"], w["validation_end"]), th)
            block["SELECTIVE60_TEST_2026"] = selective_metrics(period_slice(f, w["test_start"], w["test_end"]), th)
        target = out["dynamic"] if cid in {"DMA_LOGLOSS63", "DMS_LOGLOSS63"} else out["candidates"]
        target[cid] = block

    dmab = out["dynamic"].get("DMA_LOGLOSS63", {})
    v = dmab.get("VALIDATION_2025", {"n": 0})
    t = dmab.get("TEST_2026_AVAILABLE", {"n": 0})
    lane = "TACTICAL_H1_DMA" if h == 1 else "STRATEGIC_H20_DMA"
    out["dma_research_interest_gate"] = lane_gate(v, t, lane, contract)
    sv = dmab.get("SELECTIVE60_VALIDATION_2025", {"n": 0})
    st = dmab.get("SELECTIVE60_TEST_2026", {"n": 0})
    out["selective60_research_interest_gate"] = selective_gate(sv, st, contract)
    return out, pd.concat(pred_rows, ignore_index=True) if pred_rows else pd.DataFrame()


def main() -> None:
    contract = json.loads(CONTRACT.read_text())
    if contract["status"] != "FROZEN_BEFORE_V155_2025_2026_SCORING":
        raise RuntimeError("CONTRACT_NOT_FROZEN")
    if contract["governance"]["production_authority"]:
        raise RuntimeError("PRODUCTION_AUTHORITY_MUST_BE_FALSE")
    db = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not db:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    with psycopg.connect(db) as conn:
        panel, base_cols, full_cols = build_panel(conn, contract)
    results = {}
    all_preds = []
    for lane, h in contract["horizons"].items():
        block, preds = run_horizon(panel, base_cols, full_cols, int(h), contract)
        results[lane] = block
        if not preds.empty:
            preds["lane"] = lane
            all_preds.append(preds)
    report = {
        "contract_id": contract["contract_id"],
        "evidence_class": contract["evidence_class"],
        "panel_n": int(len(panel)),
        "panel_first": panel["date"].min().date().isoformat(),
        "panel_last": panel["date"].max().date().isoformat(),
        "base_feature_count": int(len(base_cols)),
        "full_feature_count": int(len(full_cols)),
        "base_features": base_cols,
        "full_features": full_cols,
        "results": results,
        "governance": contract["governance"],
        "notes": [
            "All sequential model fits and DMA/DMS weights use only labels mature at the current origin.",
            "Daily equities and precious metals are strictly lagged historical reconstructions, not prospective archived PIT claims.",
            "2025/2026 are retrospective successor diagnostics because predecessor research already exposed those outcomes.",
            "No result-dependent candidate or selective-threshold change is allowed under V1.55."
        ],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    panel.to_csv(OUT / "v155_dynamic_crossmarket_panel.csv", index=False)
    if all_preds:
        pd.concat(all_preds, ignore_index=True).to_csv(OUT / "v155_dynamic_crossmarket_predictions.csv", index=False)
    (OUT / "v155_dynamic_crossmarket_results.json").write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
