from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import psycopg
import requests
from psycopg.rows import dict_row
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

ROOT = Path(__file__).resolve().parents[1]
ENGINE_ID = "VW_MIDAS_SVR_XAU_SUCCESSOR_V2"
CONTRACT_VERSION = "V2_PRE_SCORE_ELIGIBILITY_CORRECTION_2026-09-05"
TWELVE_URL = "https://api.twelvedata.com/time_series"
GPR_SERIES = "GPR_OFFICIAL_GIT_PIT"
SOURCE_START = pd.Timestamp("2022-03-01")
SOURCE_END = pd.Timestamp("2026-08-01")
FIRST_FEATURE_ORIGIN = pd.Timestamp("2022-09-01")
VALIDATION_ORIGIN_START = pd.Timestamp("2024-10-01")
VALIDATION_ORIGIN_END = pd.Timestamp("2025-09-01")
LOCK_ORIGIN_START = pd.Timestamp("2025-10-01")
LOCK_ORIGIN_END = pd.Timestamp("2026-07-01")
CURRENT_ORIGIN = pd.Timestamp("2026-08-01")
CURRENT_TARGET = pd.Timestamp("2026-09-01")
MIN_DAILY = 15
MIN_FIT = 24
INNER_MAX = 12
C_GRID = (0.25, 1.0, 4.0)
GAMMA_GRID = (0.05, 0.20, 0.80)
EPSILON_GRID = (0.01, 0.05, 0.10)
FEATURES = (
    "MR_lag1",
    "MR_lag2",
    "MR_lag3",
    "MR_abs_lag1",
    "MR_MA_3",
    "MR_MA_6",
    "MR_sign_lag1",
    "VW_DAILY_RETURN",
    "GPR_norm_lagged",
    "month_sin",
    "month_cos",
)


class SourceGateError(RuntimeError):
    pass


def month_range(a: pd.Timestamp, b: pd.Timestamp) -> list[pd.Timestamp]:
    return list(pd.date_range(a, b, freq="MS"))


def _three_month_windows(start: pd.Timestamp, end: pd.Timestamp) -> Iterable[tuple[pd.Timestamp, pd.Timestamp]]:
    cur = start
    while cur <= end:
        wend = min(cur + pd.offsets.MonthBegin(2), end)
        yield cur, wend
        cur = wend + pd.offsets.MonthBegin(1)


def _request_json(session: requests.Session, params: dict, attempts: int = 5) -> dict:
    for attempt in range(attempts):
        try:
            r = session.get(TWELVE_URL, params=params, timeout=(20, 120))
            payload = r.json()
        except (requests.RequestException, ValueError) as exc:
            if attempt + 1 == attempts:
                raise SourceGateError(f"TWELVE_TRANSPORT_{type(exc).__name__}") from exc
            time.sleep(min(5 * (attempt + 1), 20))
            continue
        code = payload.get("code") if isinstance(payload, dict) else None
        if r.status_code == 429 or code == 429:
            if attempt + 1 == attempts:
                raise SourceGateError("TWELVE_RATE_LIMIT_EXHAUSTED")
            time.sleep(65)
            continue
        if r.status_code != 200 or not isinstance(payload, dict) or payload.get("status") == "error":
            message = payload.get("message") if isinstance(payload, dict) else None
            raise SourceGateError(f"TWELVE_HTTP_{r.status_code}_API_{code or 'NA'}:{message or 'NO_MESSAGE'}")
        return payload
    raise AssertionError("unreachable")


def fetch_twelve_ny17_hourly(api_key: str) -> pd.Series:
    if not api_key.strip():
        raise SourceGateError("TWELVE_DATA_API_KEY_MISSING")
    session = requests.Session()
    session.headers.update({"User-Agent": "Gold-Control-VW-Successor-V2/1.0"})
    rows: dict[pd.Timestamp, float] = {}
    for start, end in _three_month_windows(SOURCE_START, SOURCE_END):
        end_day = end + pd.offsets.MonthEnd(0)
        payload = _request_json(
            session,
            {
                "symbol": "XAU/USD",
                "interval": "1h",
                "start_date": start.strftime("%Y-%m-%d 00:00:00"),
                "end_date": end_day.strftime("%Y-%m-%d 23:59:59"),
                "timezone": "America/New_York",
                "order": "ASC",
                "outputsize": 5000,
                "apikey": api_key,
            },
        )
        for item in payload.get("values") or []:
            dt = str(item.get("datetime", ""))
            if not dt.endswith("16:00:00"):
                continue
            try:
                ts = pd.Timestamp(dt).normalize()
                val = float(item["close"])
            except Exception:
                continue
            month = ts.to_period("M").to_timestamp()
            if val > 0 and SOURCE_START <= month <= SOURCE_END:
                rows[ts] = val
        time.sleep(0.5)
    if not rows:
        raise SourceGateError("BLOCKED_TWELVE_HOURLY_NO_NY17_REFERENCES")
    s = pd.Series(rows, dtype=float).sort_index()
    s.name = "xau_ny17_hourly_research"
    return s


def audit_twelve_coverage(daily: pd.Series) -> tuple[pd.Series, dict[str, int]]:
    if daily.index.has_duplicates:
        raise SourceGateError("BLOCKED_TWELVE_DUPLICATE_DAILY_REFERENCE")
    values = daily.to_numpy(float)
    if not np.isfinite(values).all() or (values <= 0).any():
        raise SourceGateError("BLOCKED_TWELVE_INVALID_PRICE_REFERENCE")
    expected = month_range(SOURCE_START, SOURCE_END)
    counts = daily.groupby(daily.index.to_period("M")).size()
    out: dict[str, int] = {}
    for m in expected:
        n = int(counts.get(m.to_period("M"), 0))
        out[m.strftime("%Y-%m")] = n
        if n < MIN_DAILY:
            raise SourceGateError(f"BLOCKED_TWELVE_V2_MONTH_COVERAGE:{m.strftime('%Y-%m')}:{n}")
    monthly = daily.groupby(daily.index.to_period("M")).mean()
    monthly.index = monthly.index.to_timestamp()
    monthly = monthly.reindex(expected)
    if monthly.isna().any():
        raise SourceGateError("BLOCKED_TWELVE_V2_MONTHLY_AVERAGE_GAP")
    return monthly.astype(float), out


def load_gpr_norms(database_url: str, origins: Iterable[pd.Timestamp]) -> dict[pd.Timestamp, float]:
    if not database_url.strip():
        raise SourceGateError("NEON_DATABASE_URL_MISSING")
    requested = sorted({pd.Timestamp(x).to_period("M").to_timestamp() for x in origins})
    result: dict[pd.Timestamp, float] = {}
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            for origin in requested:
                origin_key = origin.strftime("%Y-%m")
                known_month = origin - pd.offsets.MonthBegin(1)
                cur.execute(
                    """
                    select observation_ts, value, lineage_id, payload_hash,
                           available_as_of, retrieved_at, first_seen_at,
                           metadata
                    from observations
                    where series_id=%s
                      and metadata->>'origin_month'=%s
                      and quality_status='APPROVED_HISTORICAL_PIT_RECONSTRUCTION_RESEARCH'
                    order by observation_ts
                    """,
                    (GPR_SERIES, origin_key),
                )
                rows = [dict(r) for r in cur.fetchall()]
                if not rows:
                    raise SourceGateError(f"BLOCKED_GPR_V2_ORIGIN_MISSING:{origin_key}")
                lineages = {str(r["lineage_id"]) for r in rows}
                payloads = {str(r["payload_hash"]) for r in rows}
                if len(lineages) != 1 or len(payloads) != 1:
                    raise SourceGateError(f"BLOCKED_GPR_V2_LINEAGE_MULTIPLICITY:{origin_key}")
                hist: dict[pd.Timestamp, float] = {}
                for r in rows:
                    meta = r.get("metadata") or {}
                    if meta.get("historical_reconstruction_not_original_retrieval") is not True:
                        raise SourceGateError(f"BLOCKED_GPR_V2_RECONSTRUCTION_FLAG:{origin_key}")
                    if r["retrieved_at"] != r["first_seen_at"]:
                        raise SourceGateError(f"BLOCKED_GPR_V2_RETRIEVAL_TRUTH:{origin_key}")
                    month = pd.Timestamp(r["observation_ts"]).tz_localize(None).to_period("M").to_timestamp()
                    if month <= known_month:
                        hist[month] = float(r["value"])
                if known_month not in hist:
                    raise SourceGateError(
                        f"BLOCKED_GPR_V2_REQUIRED_P_MINUS_1_MISSING:{origin_key}:{known_month.strftime('%Y-%m')}"
                    )
                vals = np.asarray(list(hist.values()), dtype=float)
                if not np.isfinite(vals).all() or (vals <= 0).any():
                    raise SourceGateError(f"BLOCKED_GPR_V2_INVALID_VALUES:{origin_key}")
                lo, hi = float(vals.min()), float(vals.max())
                norm = 0.5 if hi <= lo else (float(hist[known_month]) - lo) / (hi - lo)
                result[origin] = float(np.clip(norm, 0.0, 1.0))
    if len(result) != len(requested):
        raise SourceGateError(f"BLOCKED_GPR_V2_ORIGIN_COVERAGE:{len(result)}/{len(requested)}")
    return result


def variable_weighted_daily_return(daily: pd.Series, origin_month: pd.Timestamp, gpr_norm: float) -> float:
    origin_month = pd.Timestamp(origin_month).to_period("M").to_timestamp()
    mask = daily.index.to_period("M") == origin_month.to_period("M")
    current = daily.loc[mask].sort_index()
    before = daily.loc[daily.index < origin_month].sort_index()
    if current.empty or before.empty:
        raise SourceGateError(f"INSUFFICIENT_DAILY_RETURN_CONTEXT:{origin_month.strftime('%Y-%m')}")
    vals = np.r_[float(before.iloc[-1]), current.to_numpy(float)]
    returns = np.diff(np.log(vals))
    if len(returns) < MIN_DAILY:
        raise SourceGateError(f"INSUFFICIENT_DAILY_RETURNS:{origin_month.strftime('%Y-%m')}")
    lam = 0.1 * math.exp(-10.0 * float(np.clip(gpr_norm, 0.0, 1.0)))
    ages = np.arange(len(returns) - 1, -1, -1, dtype=float)
    weights = np.exp(-lam * ages)
    weights /= weights.sum()
    return float(weights @ returns)


def build_feature_frame(daily: pd.Series, monthly: pd.Series, gpr_norms: dict[pd.Timestamp, float]) -> pd.DataFrame:
    mr = np.log(monthly / monthly.shift(1))
    rows: list[dict] = []
    for origin in pd.date_range(FIRST_FEATURE_ORIGIN, CURRENT_ORIGIN, freq="MS"):
        target = origin + pd.offsets.MonthBegin(1)
        if origin not in monthly.index or origin not in gpr_norms:
            raise SourceGateError(f"V2_FEATURE_ORIGIN_INPUT_MISSING:{origin.strftime('%Y-%m')}")
        hist_r = mr.loc[:origin].dropna()
        if len(hist_r) < 6:
            raise SourceGateError(f"V2_FEATURE_RETURN_HISTORY_LT_6:{origin.strftime('%Y-%m')}")
        g = float(gpr_norms[origin])
        m = target.month
        origin_price = float(monthly.loc[origin])
        actual = float(monthly.loc[target]) if target in monthly.index and pd.notna(monthly.loc[target]) else np.nan
        rec = {
            "origin": origin,
            "target": target,
            "origin_price": origin_price,
            "actual": actual,
            "MR_lag1": float(hist_r.iloc[-1]),
            "MR_lag2": float(hist_r.iloc[-2]),
            "MR_lag3": float(hist_r.iloc[-3]),
            "MR_abs_lag1": abs(float(hist_r.iloc[-1])),
            "MR_MA_3": float(hist_r.iloc[-3:].mean()),
            "MR_MA_6": float(hist_r.iloc[-6:].mean()),
            "MR_sign_lag1": float(np.sign(hist_r.iloc[-1])),
            "VW_DAILY_RETURN": variable_weighted_daily_return(daily, origin, g),
            "GPR_norm_lagged": g,
            "month_sin": math.sin(2.0 * math.pi * m / 12.0),
            "month_cos": math.cos(2.0 * math.pi * m / 12.0),
        }
        rec["y"] = math.log(actual / origin_price) if np.isfinite(actual) else np.nan
        rows.append(rec)
    frame = pd.DataFrame(rows).set_index("origin").sort_index()
    if frame.empty:
        raise SourceGateError("V2_NO_FEATURE_ROWS")
    return frame


def fit_predict_return(train: pd.DataFrame, test: pd.DataFrame, params: tuple[float, float, float]) -> float:
    if len(train) < MIN_FIT:
        raise ValueError("MIN_FIT_NOT_MET")
    C, gamma, epsilon = params
    sx = StandardScaler().fit(train[list(FEATURES)])
    sy = StandardScaler().fit(train[["y"]])
    model = SVR(kernel="rbf", C=C, gamma=gamma, epsilon=epsilon)
    model.fit(sx.transform(train[list(FEATURES)]), sy.transform(train[["y"]]).ravel())
    pred_scaled = float(model.predict(sx.transform(test[list(FEATURES)]))[0])
    return float(sy.inverse_transform(np.array([[pred_scaled]], dtype=float))[0, 0])


def tune_for_outer(frame: pd.DataFrame, origin: pd.Timestamp) -> tuple[tuple[float, float, float], int, float]:
    origin = pd.Timestamp(origin).to_period("M").to_timestamp()
    train_all = frame[(frame.index < origin) & frame["y"].notna()].copy()
    if len(train_all) < MIN_FIT:
        raise ValueError("OUTER_MIN_FIT_NOT_MET")
    eligible_inner: list[pd.Timestamp] = []
    for inner_origin in train_all.index[-INNER_MAX:]:
        inner_train = frame[(frame.index < inner_origin) & frame["y"].notna()]
        if len(inner_train) >= MIN_FIT:
            eligible_inner.append(pd.Timestamp(inner_origin))
    if not eligible_inner:
        raise ValueError("NO_ELIGIBLE_INNER_ORIGINS")
    scored: list[tuple[float, float, float, float]] = []
    for C, gamma, epsilon in itertools.product(C_GRID, GAMMA_GRID, EPSILON_GRID):
        errors: list[float] = []
        for inner_origin in eligible_inner:
            tr = frame[(frame.index < inner_origin) & frame["y"].notna()]
            te = frame.loc[[inner_origin]]
            pred = fit_predict_return(tr, te, (C, gamma, epsilon))
            errors.append(abs(pred - float(te["y"].iloc[0])))
        scored.append((float(np.mean(errors)), C, gamma, epsilon))
    scored.sort(key=lambda z: (z[0], z[1], z[2], z[3]))
    best = scored[0]
    return (best[1], best[2], best[3]), len(eligible_inner), best[0]


def predict_origin(frame: pd.DataFrame, origin: pd.Timestamp) -> dict:
    origin = pd.Timestamp(origin).to_period("M").to_timestamp()
    if origin not in frame.index:
        raise KeyError(origin)
    params, inner_n, inner_mae = tune_for_outer(frame, origin)
    train = frame[(frame.index < origin) & frame["y"].notna()].copy()
    test = frame.loc[[origin]]
    pred_return = fit_predict_return(train, test, params)
    origin_price = float(test["origin_price"].iloc[0])
    actual = float(test["actual"].iloc[0]) if np.isfinite(test["actual"].iloc[0]) else np.nan
    return {
        "origin": origin,
        "target": pd.Timestamp(test["target"].iloc[0]),
        "forecast": float(origin_price * math.exp(pred_return)),
        "pred_return": pred_return,
        "rw": origin_price,
        "actual": actual,
        "C": params[0],
        "gamma": params[1],
        "epsilon": params[2],
        "inner_origins": inner_n,
        "inner_mae_log_return": inner_mae,
        "train_n": len(train),
    }


def replay_origins(frame: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    rows: list[dict] = []
    for origin in pd.date_range(start, end, freq="MS"):
        if origin not in frame.index or not np.isfinite(frame.loc[origin, "actual"]):
            raise SourceGateError(f"V2_REPLAY_TARGET_MISSING:{origin.strftime('%Y-%m')}")
        row = predict_origin(frame, origin)
        row["candidate_error"] = row["forecast"] - row["actual"]
        row["rw_error"] = row["rw"] - row["actual"]
        rows.append(row)
    return pd.DataFrame(rows)


def metrics(df: pd.DataFrame) -> dict:
    actual = df["actual"].to_numpy(float)
    fc = df["forecast"].to_numpy(float)
    rw = df["rw"].to_numpy(float)
    ae = np.abs(fc - actual)
    rw_ae = np.abs(rw - actual)
    direction_actual = np.sign(actual - rw)
    direction_pred = np.sign(fc - rw)
    return {
        "n": int(len(df)),
        "relative_mae_vs_rw": float(ae.sum() / rw_ae.sum()) if rw_ae.sum() > 0 else math.inf,
        "mae": float(ae.mean()),
        "rw_mae": float(rw_ae.mean()),
        "mape": float(np.mean(ae / actual) * 100.0),
        "rw_mape": float(np.mean(rw_ae / actual) * 100.0),
        "smape": float(np.mean(2.0 * ae / (np.abs(fc) + np.abs(actual))) * 100.0),
        "rmse": float(np.sqrt(np.mean((fc - actual) ** 2))),
        "median_ae": float(np.median(ae)),
        "rw_median_ae": float(np.median(rw_ae)),
        "monthly_win_rate_vs_rw": float(np.mean(ae < rw_ae)),
        "directional_accuracy": float(np.mean(direction_actual == direction_pred)),
    }


def origin_bucket_mae_ratios(df: pd.DataFrame) -> dict[str, float]:
    buckets = {
        "2024-10..2024-12": (pd.Timestamp("2024-10-01"), pd.Timestamp("2024-12-01")),
        "2025-01..2025-09": (pd.Timestamp("2025-01-01"), pd.Timestamp("2025-09-01")),
    }
    out: dict[str, float] = {}
    origins = pd.to_datetime(df["origin"])
    for label, (a, b) in buckets.items():
        g = df[(origins >= a) & (origins <= b)]
        if g.empty:
            out[label] = math.inf
            continue
        cand = float(np.mean(np.abs(g["forecast"] - g["actual"])))
        rw = float(np.mean(np.abs(g["rw"] - g["actual"])))
        out[label] = cand / rw if rw > 0 else math.inf
    return out


def validation_gate(vm: dict, bucket_ratios: dict[str, float]) -> tuple[bool, list[str]]:
    checks = {
        "relative_mae_vs_rw_lt_1": vm["relative_mae_vs_rw"] < 1.0,
        "mape_not_worse_than_rw": vm["mape"] <= vm["rw_mape"],
        "median_ae_not_worse_than_rw": vm["median_ae"] <= vm["rw_median_ae"],
        "monthly_win_rate_gte_0_5": vm["monthly_win_rate_vs_rw"] >= 0.5,
        "all_origin_bucket_mae_ratios_lte_1_5": all(v <= 1.5 for v in bucket_ratios.values()),
    }
    failed = [k for k, v in checks.items() if not v]
    return not failed, failed


def stable_input_fingerprint(daily: pd.Series, gpr_norms: dict[pd.Timestamp, float]) -> str:
    h = hashlib.sha256()
    for ts, val in daily.items():
        h.update(f"D|{pd.Timestamp(ts).isoformat()}|{float(val):.10f}\n".encode())
    for m, val in sorted(gpr_norms.items()):
        h.update(f"G|{pd.Timestamp(m).strftime('%Y-%m')}|{float(val):.12f}\n".encode())
    return h.hexdigest()


def prediction_fingerprint(df: pd.DataFrame) -> str:
    h = hashlib.sha256()
    for _, r in df.sort_values("origin").iterrows():
        h.update(
            f"{pd.Timestamp(r['origin']).strftime('%Y-%m')}|{float(r['forecast']):.10f}|{float(r['pred_return']):.12f}|{r['C']}|{r['gamma']}|{r['epsilon']}\n".encode()
        )
    return h.hexdigest()


def prefix_invariance_check(daily: pd.Series, monthly: pd.Series, gpr_norms: dict[pd.Timestamp, float], origin: pd.Timestamp = pd.Timestamp("2025-03-01")) -> bool:
    full = build_feature_frame(daily, monthly, gpr_norms)
    next_month = origin + pd.offsets.MonthBegin(1)
    daily_prefix = daily.loc[daily.index < next_month]
    monthly_prefix = monthly.loc[:origin]
    gpr_prefix = {m: v for m, v in gpr_norms.items() if m <= origin}
    # Build only the chosen origin directly from prefix inputs to avoid requiring later configured origins.
    mr = np.log(monthly_prefix / monthly_prefix.shift(1))
    hist_r = mr.loc[:origin].dropna()
    if len(hist_r) < 6 or origin not in gpr_prefix:
        return False
    g = float(gpr_prefix[origin])
    target = origin + pd.offsets.MonthBegin(1)
    m = target.month
    prefix_vec = np.array([
        float(hist_r.iloc[-1]),
        float(hist_r.iloc[-2]),
        float(hist_r.iloc[-3]),
        abs(float(hist_r.iloc[-1])),
        float(hist_r.iloc[-3:].mean()),
        float(hist_r.iloc[-6:].mean()),
        float(np.sign(hist_r.iloc[-1])),
        variable_weighted_daily_return(daily_prefix, origin, g),
        g,
        math.sin(2.0 * math.pi * m / 12.0),
        math.cos(2.0 * math.pi * m / 12.0),
    ], dtype=float)
    full_vec = full.loc[origin, list(FEATURES)].to_numpy(float)
    return bool(np.allclose(full_vec, prefix_vec, atol=1e-12, rtol=0.0))


def structural_self_audit() -> None:
    assert ENGINE_ID == "VW_MIDAS_SVR_XAU_SUCCESSOR_V2"
    assert SOURCE_START == pd.Timestamp("2022-03-01")
    assert SOURCE_END == pd.Timestamp("2026-08-01")
    assert FIRST_FEATURE_ORIGIN == pd.Timestamp("2022-09-01")
    assert VALIDATION_ORIGIN_START == pd.Timestamp("2024-10-01")
    assert VALIDATION_ORIGIN_END == pd.Timestamp("2025-09-01")
    assert len(pd.date_range(VALIDATION_ORIGIN_START, VALIDATION_ORIGIN_END, freq="MS")) == 12
    assert LOCK_ORIGIN_START == pd.Timestamp("2025-10-01")
    assert LOCK_ORIGIN_END == pd.Timestamp("2026-07-01")
    assert MIN_FIT == 24
    assert INNER_MAX == 12
    assert C_GRID == (0.25, 1.0, 4.0)
    assert GAMMA_GRID == (0.05, 0.20, 0.80)
    assert EPSILON_GRID == (0.01, 0.05, 0.10)
    assert FEATURES == (
        "MR_lag1", "MR_lag2", "MR_lag3", "MR_abs_lag1", "MR_MA_3", "MR_MA_6",
        "MR_sign_lag1", "VW_DAILY_RETURN", "GPR_norm_lagged", "month_sin", "month_cos"
    )


def execute(out_dir: Path) -> dict:
    structural_self_audit()
    api_key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    database_url = os.environ.get("NEON_DATABASE_URL", "").strip()
    daily = fetch_twelve_ny17_hourly(api_key)
    monthly, counts = audit_twelve_coverage(daily)
    required_origins = pd.date_range(FIRST_FEATURE_ORIGIN, CURRENT_ORIGIN, freq="MS")
    gpr_norms = load_gpr_norms(database_url, required_origins)
    frame = build_feature_frame(daily, monthly, gpr_norms)

    # Contract-consistency assertion: 2024-09 has 24 outer rows but cannot tune; 2024-10 is the first tunable outer.
    sep24_train = frame[(frame.index < pd.Timestamp("2024-09-01")) & frame["y"].notna()]
    oct24_train = frame[(frame.index < pd.Timestamp("2024-10-01")) & frame["y"].notna()]
    if len(sep24_train) != 24 or len(oct24_train) != 25:
        raise RuntimeError(f"V2_ELIGIBILITY_ARITHMETIC_DRIFT:{len(sep24_train)}:{len(oct24_train)}")
    try:
        tune_for_outer(frame, pd.Timestamp("2024-09-01"))
    except ValueError as exc:
        if str(exc) != "NO_ELIGIBLE_INNER_ORIGINS":
            raise
    else:
        raise RuntimeError("V2_2024_09_UNEXPECTEDLY_TUNABLE")
    tune_for_outer(frame, pd.Timestamp("2024-10-01"))

    if not prefix_invariance_check(daily, monthly, gpr_norms):
        raise RuntimeError("PREFIX_INVARIANCE_FAIL")

    validation_a = replay_origins(frame, VALIDATION_ORIGIN_START, VALIDATION_ORIGIN_END)
    validation_b = replay_origins(frame, VALIDATION_ORIGIN_START, VALIDATION_ORIGIN_END)
    if prediction_fingerprint(validation_a) != prediction_fingerprint(validation_b):
        raise RuntimeError("DETERMINISTIC_RERUN_FAIL")

    locked = replay_origins(frame, LOCK_ORIGIN_START, LOCK_ORIGIN_END)
    vm = metrics(validation_a)
    lm = metrics(locked)
    bucket_ratios = origin_bucket_mae_ratios(validation_a)
    eligible, failed = validation_gate(vm, bucket_ratios)
    status = "HISTORICAL_REPLAY_SPECIALIZED_SHADOW_ELIGIBLE_PROSPECTIVE_BRIDGE_REQUIRED" if eligible else "REJECT_ALL_SUCCESSOR_CANDIDATES"

    evidence = {
        "engine_id": ENGINE_ID,
        "contract_version": CONTRACT_VERSION,
        "evidence_class": "HISTORICAL_REPLAY_SUCCESSOR_RESEARCH",
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "prospective_claim": False,
        "production_authorized": False,
        "db_writes": "NONE",
        "forecast_or_decision_store_write": False,
        "selector_or_ensemble_change": False,
        "archived_vw_status_changed": False,
        "source_audit": {
            "xau_series": "XAU_MONTHLY_AVG_NY17_HOURLY_RESEARCH_V1",
            "xau_source_months_expected": len(month_range(SOURCE_START, SOURCE_END)),
            "xau_source_months_passed": len(counts),
            "xau_min_daily_count": min(counts.values()),
            "gpr_series": GPR_SERIES,
            "gpr_origins_required_for_features": len(required_origins),
            "gpr_origins_loaded": len(gpr_norms),
            "input_fingerprint_sha256": stable_input_fingerprint(daily, gpr_norms),
            "raw_vendor_values_logged": False,
            "raw_vendor_values_committed": False,
        },
        "eligibility_correction": {
            "first_feature_complete_origin": "2022-09",
            "first_outer_origin_with_24_training_rows_but_no_eligible_inner": "2024-09",
            "first_fully_tunable_outer_origin": "2024-10",
        },
        "validation_origin_window": ["2024-10", "2025-09"],
        "validation_target_window": ["2024-11", "2025-10"],
        "validation_metrics": vm,
        "validation_origin_bucket_mae_ratio_vs_rw": bucket_ratios,
        "validation_gate_pass": eligible,
        "validation_failed_gates": failed,
        "locked_diagnostic_origin_window": ["2025-10", "2026-07"],
        "locked_diagnostic_target_window": ["2025-11", "2026-08"],
        "locked_metrics_diagnostic_only": lm,
        "deterministic_rerun": True,
        "prefix_invariance": True,
        "validation_prediction_fingerprint": prediction_fingerprint(validation_a),
        "locked_prediction_fingerprint": prediction_fingerprint(locked),
        "current_sep2026_reconstruction": {
            "status": "NOT_RUN_PROSPECTIVE_LINEAGE_BRIDGE_NOT_PROVEN",
            "origin": "2026-08-31",
            "target_month": "2026-09",
            "prospective_claim": False,
        },
        "prospective_bridge_status": "NOT_PROVEN_FINAL_BRIDGE_PASS",
        "maximum_v2_status": status,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "vw_midas_svr_xau_successor_v2_evidence.json").write_text(
        json.dumps(evidence, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8"
    )
    public_rows = validation_a[["origin", "target", "forecast", "rw", "actual", "C", "gamma", "epsilon", "inner_origins", "train_n"]].copy()
    public_rows.to_csv(out_dir / "vw_midas_svr_xau_successor_v2_validation.csv", index=False)
    locked_public = locked[["origin", "target", "forecast", "rw", "actual", "C", "gamma", "epsilon", "inner_origins", "train_n"]].copy()
    locked_public.to_csv(out_dir / "vw_midas_svr_xau_successor_v2_locked_diagnostic.csv", index=False)
    return evidence


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(ROOT / "vw_midas_svr_xau_successor_v2" / "runtime_evidence"))
    args = ap.parse_args()
    try:
        evidence = execute(Path(args.out_dir))
    except SourceGateError as exc:
        print("VW_V2_SOURCE_GATE=BLOCKED")
        print(f"VW_V2_BLOCK_REASON={exc}")
        print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
        print("DATABASE_WRITES=NONE")
        raise
    print("VW_V2_SOURCE_GATE=PASS")
    print(f"VALIDATION_GATE_PASS={str(evidence['validation_gate_pass']).upper()}")
    print(f"MAXIMUM_V2_STATUS={evidence['maximum_v2_status']}")
    print(f"VALIDATION_RELATIVE_MAE_VS_RW={evidence['validation_metrics']['relative_mae_vs_rw']:.9f}")
    print(f"VALIDATION_MAPE={evidence['validation_metrics']['mape']:.9f}")
    print(f"VALIDATION_RW_MAPE={evidence['validation_metrics']['rw_mape']:.9f}")
    print(f"VALIDATION_MONTHLY_WIN_RATE={evidence['validation_metrics']['monthly_win_rate_vs_rw']:.9f}")
    print(f"LOCK_RELATIVE_MAE_VS_RW_DIAGNOSTIC={evidence['locked_metrics_diagnostic_only']['relative_mae_vs_rw']:.9f}")
    print("CURRENT_SEP2026_V2_RECONSTRUCTION=NOT_RUN_PROSPECTIVE_LINEAGE_BRIDGE_NOT_PROVEN")
    print("DETERMINISTIC_RERUN=PASS")
    print("PREFIX_INVARIANCE=PASS")
    print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
    print("DATABASE_WRITES=NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
