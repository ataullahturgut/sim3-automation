from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from sklearn.ensemble import BaggingClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    log_loss,
    matthews_corrcoef,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v154_thesis/contracts/v154_settlement_horizon_tree_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v154_thesis"
SEED = 20260912


def q(conn, sql: str, params=None) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn, params=params)


def load_endpoint(conn, start: str, end: str) -> pd.DataFrame:
    d = q(
        conn,
        """
        SELECT observation_ts,
               (observation_ts AT TIME ZONE 'America/New_York')::date AS date,
               close::double precision AS close
        FROM xau_intraday_research_cache_1m
        WHERE observation_ts >= %s::timestamptz
          AND observation_ts < (%s::date + interval '1 day')
          AND (observation_ts AT TIME ZONE 'America/New_York')::time = time '13:29:00'
          AND close > 0
        ORDER BY observation_ts
        """,
        (start, end),
    )
    if d.empty:
        raise RuntimeError("BLOCKED_1329_ENDPOINT_EMPTY")
    d["observation_ts"] = pd.to_datetime(d["observation_ts"], utc=True)
    d["date"] = pd.to_datetime(d["date"])
    d["close"] = pd.to_numeric(d["close"], errors="coerce")
    d = d.dropna(subset=["date", "close"]).sort_values(["date", "observation_ts"])
    d = d.drop_duplicates("date", keep="last").reset_index(drop=True)
    if d["date"].duplicated().any():
        raise RuntimeError("DUPLICATE_1329_DATE")
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


def add_features(d: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
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

    d["fast_role"] = _fast_role(c)
    d["slow_role"] = [_slow_role_at(d, i) for i in range(len(d))]
    d["monthly_direction_3m"] = [_monthly_direction_at(d, i) for i in range(len(d))]
    cols.extend(["fast_role", "slow_role", "monthly_direction_3m"])
    return d, cols


def add_target(d: pd.DataFrame, h: int) -> pd.DataFrame:
    z = d.copy()
    z["target_close"] = z["close"].shift(-h)
    z["target_date"] = z["date"].shift(-h)
    z["target_return"] = np.log(z["target_close"] / z["close"])
    z["y"] = np.where(z["target_return"].notna(), (z["target_return"] > 0).astype(int), np.nan)
    z["elapsed_calendar_days"] = (z["target_date"] - z["date"]).dt.days
    return z


def estimator(model_id: str, cfg: dict):
    if model_id == "RF500":
        return make_pipeline(
            SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
            RandomForestClassifier(
                n_estimators=int(cfg["n_estimators"]),
                max_features=cfg["max_features"],
                min_samples_leaf=int(cfg["min_samples_leaf"]),
                class_weight=cfg["class_weight"],
                random_state=int(cfg["random_state"]),
                n_jobs=-1,
            ),
        )
    if model_id == "BAG300":
        tree = DecisionTreeClassifier(min_samples_leaf=int(cfg["tree_min_samples_leaf"]), random_state=int(cfg["random_state"]))
        return make_pipeline(
            SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
            BaggingClassifier(
                estimator=tree,
                n_estimators=int(cfg["n_estimators"]),
                random_state=int(cfg["random_state"]),
                n_jobs=-1,
            ),
        )
    if model_id == "SGB300":
        return make_pipeline(
            SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
            GradientBoostingClassifier(
                n_estimators=int(cfg["n_estimators"]),
                learning_rate=float(cfg["learning_rate"]),
                max_depth=int(cfg["max_depth"]),
                subsample=float(cfg["subsample"]),
                random_state=int(cfg["random_state"]),
            ),
        )
    if model_id == "LOGIT":
        return make_pipeline(
            SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
            StandardScaler(),
            LogisticRegression(C=float(cfg["C"]), max_iter=int(cfg["max_iter"]), random_state=int(cfg["random_state"])),
        )
    raise KeyError(model_id)


def _fit_and_predict(z: pd.DataFrame, features: list[str], model_id: str, model_cfg: dict, train_target_cutoff: str, origin_start: str, origin_end: str) -> tuple[pd.DataFrame, dict]:
    cutoff = pd.Timestamp(train_target_cutoff)
    start = pd.Timestamp(origin_start)
    end = pd.Timestamp(origin_end)
    train = z[z["target_date"].notna() & z["y"].notna() & (z["target_date"] <= cutoff)].copy()
    score = z[z["target_date"].notna() & z["y"].notna() & (z["date"] >= start) & (z["date"] <= end) & (z["target_date"] <= end)].copy()
    if len(train) < 150:
        raise RuntimeError(f"BLOCKED_MIN_TRAIN:{model_id}:{len(train)}")
    if train["y"].nunique() < 2:
        raise RuntimeError(f"BLOCKED_ONE_CLASS_TRAIN:{model_id}")
    if score.empty:
        raise RuntimeError(f"BLOCKED_EMPTY_SCORE:{model_id}:{origin_start}:{origin_end}")
    m = estimator(model_id, model_cfg)
    m.fit(train[features], train["y"].astype(int))
    p = m.predict_proba(score[features])[:, 1]
    score = score[["date", "target_date", "target_return", "elapsed_calendar_days", "y"]].copy()
    score["p"] = np.clip(p.astype(float), 1e-6, 1 - 1e-6)
    score["pred"] = (score["p"] >= 0.5).astype(int)
    freq = float(train["y"].mean())
    majority = int(freq >= 0.5)
    info = {
        "train_n": int(len(train)),
        "train_up_rate": freq,
        "training_majority_class": majority,
        "training_majority_probability": max(freq, 1.0 - freq),
        "train_last_target_date": train["target_date"].max().date().isoformat(),
    }
    return score, info


def _metrics(score: pd.DataFrame, info: dict, h: int) -> dict:
    y = score["y"].astype(int).to_numpy()
    pred = score["pred"].astype(int).to_numpy()
    p = score["p"].to_numpy(float)
    majority_pred = np.full(len(y), int(info["training_majority_class"]), dtype=int)
    grid = score.iloc[::h].copy()
    gy = grid["y"].astype(int).to_numpy()
    gp = grid["pred"].astype(int).to_numpy()
    elapsed = score["elapsed_calendar_days"].dropna().astype(float)
    return {
        **info,
        "n": int(len(score)),
        "accuracy": float(accuracy_score(y, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "brier": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, p, labels=[0, 1])),
        "mcc": float(matthews_corrcoef(y, pred)),
        "actual_up_rate": float(np.mean(y)),
        "predicted_up_rate": float(np.mean(pred)),
        "training_majority_accuracy": float(accuracy_score(y, majority_pred)),
        "training_majority_balanced_accuracy": float(balanced_accuracy_score(y, majority_pred)),
        "balanced_accuracy_gain_vs_training_majority": float(balanced_accuracy_score(y, pred) - balanced_accuracy_score(y, majority_pred)),
        "p50_accuracy": float(max(np.mean(y), 1.0 - np.mean(y))),
        "fixed_grid_nonoverlap_n": int(len(grid)),
        "fixed_grid_nonoverlap_accuracy": float(accuracy_score(gy, gp)) if len(grid) else None,
        "elapsed_calendar_days_median": None if elapsed.empty else float(elapsed.median()),
        "elapsed_calendar_days_p10": None if elapsed.empty else float(elapsed.quantile(0.10)),
        "elapsed_calendar_days_p90": None if elapsed.empty else float(elapsed.quantile(0.90)),
    }


def gate_pass(v: dict, t: dict, contract: dict) -> dict:
    g = contract["evaluation"]["research_interest_gate"]
    checks = {
        "validation_balanced_accuracy": v["balanced_accuracy"] >= float(g["balanced_accuracy_each_of_2025_and_2026_min"]),
        "test_balanced_accuracy": t["balanced_accuracy"] >= float(g["balanced_accuracy_each_of_2025_and_2026_min"]),
        "validation_accuracy": v["accuracy"] >= float(g["accuracy_each_of_2025_and_2026_min"]),
        "test_accuracy": t["accuracy"] >= float(g["accuracy_each_of_2025_and_2026_min"]),
        "validation_balanced_gain": v["balanced_accuracy_gain_vs_training_majority"] >= float(g["balanced_accuracy_gain_vs_training_majority_each_period_min"]),
        "test_balanced_gain": t["balanced_accuracy_gain_vs_training_majority"] >= float(g["balanced_accuracy_gain_vs_training_majority_each_period_min"]),
    }
    return {"pass": bool(all(checks.values())), "checks": checks}


def run(contract: dict, d: pd.DataFrame, features: list[str]) -> tuple[dict, pd.DataFrame]:
    w = contract["windows"]
    rows = []
    out: dict[str, dict] = {}
    for h in contract["horizons_settlement_sessions"]:
        z = add_target(d, int(h))
        out[str(h)] = {}
        for model_id, cfg in contract["models"].items():
            val, vinfo = _fit_and_predict(
                z, features, model_id, cfg,
                w["formation_end"], w["validation_start"], w["validation_end"],
            )
            test, tinfo = _fit_and_predict(
                z, features, model_id, cfg,
                w["validation_end"], w["test_start"], w["test_end"],
            )
            vm = _metrics(val, vinfo, int(h))
            tm = _metrics(test, tinfo, int(h))
            out[str(h)][model_id] = {
                "validation_2025": vm,
                "test_2026_available_cache": tm,
                "research_interest_gate": gate_pass(vm, tm, contract),
            }
            for period, frame in [("VALIDATION_2025", val), ("TEST_2026", test)]:
                f = frame.copy()
                f["period"] = period
                f["horizon"] = int(h)
                f["model_id"] = model_id
                rows.append(f)
    return out, pd.concat(rows, ignore_index=True)


def main() -> None:
    contract = json.loads(CONTRACT.read_text())
    if contract["status"] != "FROZEN_BEFORE_V154_2025_2026_SCORING":
        raise RuntimeError("CONTRACT_NOT_FROZEN")
    if contract["governance"]["production_authority"]:
        raise RuntimeError("PRODUCTION_AUTHORITY_MUST_BE_FALSE")
    db = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not db:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    with psycopg.connect(db) as conn:
        raw = load_endpoint(conn, contract["windows"]["formation_start"], contract["windows"]["test_end"])
    d, features = add_features(raw)
    results, preds = run(contract, d, features)
    report = {
        "contract_id": contract["contract_id"],
        "evidence_class": contract["evidence_class"],
        "endpoint_label": contract["source"]["endpoint_label"],
        "endpoint_rows": int(len(d)),
        "endpoint_first": d["date"].min().date().isoformat(),
        "endpoint_last": d["date"].max().date().isoformat(),
        "endpoint_year_counts": {str(k): int(v) for k, v in d["date"].dt.year.value_counts().sort_index().items()},
        "feature_count": int(len(features)),
        "features": features,
        "results": results,
        "primary_specification": {"model": contract["primary_model"], "horizon": contract["primary_horizon"]},
        "governance": contract["governance"],
        "notes": [
            "13:29 ET is an XAU/USD spot research endpoint aligned to the start of CME GC's settlement window, not the GC settlement price.",
            "Targets are h subsequent observed exact 13:29 endpoints; calendar-day spacing is reported for audit.",
            "2025/2026 results are retrospective successor diagnostics, not fresh blind confirmation.",
            "No post-score feature, threshold, or model changes are permitted under this V1.54 contract."
        ],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    d.to_csv(OUT / "v154_settlement_endpoint_features.csv", index=False)
    preds.to_csv(OUT / "v154_settlement_horizon_predictions.csv", index=False)
    (OUT / "v154_settlement_horizon_tree_results.json").write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
