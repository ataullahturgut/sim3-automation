from __future__ import annotations

import argparse
import hashlib
import io
import itertools
import json
import math
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import requests
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "vw_midas_svr_xau_successor_v1" / "frozen_contract_v1.json"
TWELVE_URL = "https://api.twelvedata.com/time_series"
GPR_VINTAGE_URL = "https://www.matteoiacoviello.com/gpr_files/data_gpr_export_{stamp}.xls"
ENGINE_ID = "VW_MIDAS_SVR_XAU_SUCCESSOR_V1"
SOURCE_START = pd.Timestamp("2020-03-01")
SOURCE_END = pd.Timestamp("2026-08-01")
VALIDATION_START = pd.Timestamp("2023-01-01")
VALIDATION_END = pd.Timestamp("2024-12-01")
LOCK_START = pd.Timestamp("2025-01-01")
LOCK_END = pd.Timestamp("2026-07-01")
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


@dataclass(frozen=True)
class SourceAudit:
    twelve_months_expected: int
    twelve_months_passed: int
    twelve_min_daily_count: int
    gpr_vintages_expected: int
    gpr_vintages_passed: int
    input_fingerprint_sha256: str


def month_range(a: pd.Timestamp, b: pd.Timestamp) -> list[pd.Timestamp]:
    return list(pd.date_range(a, b, freq="MS"))


def _request_json(session: requests.Session, params: dict, attempts: int = 6) -> dict:
    for attempt in range(attempts):
        try:
            r = session.get(TWELVE_URL, params=params, timeout=90)
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
            raise SourceGateError(f"TWELVE_HTTP_{r.status_code}_API_{code or 'NA'}")
        return payload
    raise AssertionError("unreachable")


def _three_month_windows(start: pd.Timestamp, end: pd.Timestamp) -> Iterable[tuple[pd.Timestamp, pd.Timestamp]]:
    cur = start
    while cur <= end:
        wend = min(cur + pd.offsets.MonthBegin(2), end)
        yield cur, wend
        cur = wend + pd.offsets.MonthBegin(1)


def fetch_twelve_ny17_hourly(api_key: str) -> pd.Series:
    if not api_key.strip():
        raise SourceGateError("TWELVE_DATA_API_KEY_MISSING")
    session = requests.Session()
    session.headers.update({"User-Agent": "Gold-Control-VW-Successor-V1/1.0"})
    rows: dict[pd.Timestamp, float] = {}
    for start, end in _three_month_windows(SOURCE_START, SOURCE_END):
        end_day = end + pd.offsets.MonthEnd(0)
        params = {
            "symbol": "XAU/USD",
            "interval": "1h",
            "start_date": start.strftime("%Y-%m-%d 00:00:00"),
            "end_date": end_day.strftime("%Y-%m-%d 23:59:59"),
            "timezone": "America/New_York",
            "order": "ASC",
            "outputsize": 5000,
            "apikey": api_key,
        }
        payload = _request_json(session, params)
        for item in payload.get("values") or []:
            dt = str(item.get("datetime", ""))
            if not dt.endswith("16:00:00"):
                continue
            try:
                ts = pd.Timestamp(dt).normalize()
                val = float(item["close"])
            except Exception:
                continue
            if val > 0 and SOURCE_START <= ts.to_period("M").to_timestamp() <= SOURCE_END:
                rows[ts] = val
        time.sleep(1.0)
    if not rows:
        raise SourceGateError("BLOCKED_TWELVE_HOURLY_NO_NY17_REFERENCES")
    s = pd.Series(rows, dtype=float).sort_index()
    s.name = "xau_ny17_hourly_research"
    return s


def audit_twelve_coverage(daily: pd.Series) -> tuple[pd.Series, dict[str, int]]:
    if daily.index.has_duplicates:
        raise SourceGateError("BLOCKED_TWELVE_DUPLICATE_DAILY_REFERENCE")
    if not np.isfinite(daily.to_numpy(float)).all() or (daily <= 0).any():
        raise SourceGateError("BLOCKED_TWELVE_INVALID_PRICE_REFERENCE")
    expected = month_range(SOURCE_START, SOURCE_END)
    counts = daily.groupby(daily.index.to_period("M")).size()
    out: dict[str, int] = {}
    for m in expected:
        key = m.to_period("M")
        n = int(counts.get(key, 0))
        out[m.strftime("%Y-%m")] = n
        if n < MIN_DAILY:
            raise SourceGateError(
                f"BLOCKED_TWELVE_HOURLY_COMMON_HISTORY_INSUFFICIENT_FOR_FROZEN_V1_WINDOW:{m.strftime('%Y-%m')}:{n}"
            )
    monthly = daily.groupby(daily.index.to_period("M")).mean()
    monthly.index = monthly.index.to_timestamp()
    monthly = monthly.reindex(expected)
    if monthly.isna().any():
        raise SourceGateError("BLOCKED_TWELVE_MONTHLY_AVERAGE_GAP")
    return monthly.astype(float), out


def _parse_gpr_book(content: bytes) -> pd.DataFrame:
    try:
        sheets = pd.read_excel(io.BytesIO(content), sheet_name=None, engine="xlrd")
    except Exception as exc:
        raise SourceGateError(f"GPR_VINTAGE_XLS_PARSE_{type(exc).__name__}") from exc
    best: pd.DataFrame | None = None
    for _, d in sheets.items():
        cols = {str(c).strip().upper(): c for c in d.columns}
        if "GPR" not in cols:
            continue
        date_col = None
        for candidate in ("MONTH", "DATE"):
            if candidate in cols:
                date_col = cols[candidate]
                break
        if date_col is None:
            date_col = d.columns[0]
        q = d[[date_col, cols["GPR"]]].copy()
        q.columns = ["date", "GPR"]
        q["date"] = pd.to_datetime(q["date"], errors="coerce")
        q["GPR"] = pd.to_numeric(q["GPR"], errors="coerce")
        q = q.dropna().copy()
        if q.empty:
            continue
        q["month"] = q["date"].dt.to_period("M").dt.to_timestamp()
        q = q.drop_duplicates("month", keep="last").set_index("month")[["GPR"]].sort_index()
        if best is None or len(q) > len(best):
            best = q
    if best is None or best.empty:
        raise SourceGateError("GPR_VINTAGE_GPR_COLUMN_NOT_FOUND")
    return best


def fetch_gpr_norms(session: requests.Session, origins: Iterable[pd.Timestamp]) -> tuple[dict[pd.Timestamp, float], int]:
    result: dict[pd.Timestamp, float] = {}
    passed = 0
    for origin in sorted(set(pd.Timestamp(x).to_period("M").to_timestamp() for x in origins)):
        stamp = origin.strftime("%Y%m")
        url = GPR_VINTAGE_URL.format(stamp=stamp)
        try:
            r = session.get(url, timeout=60)
        except requests.RequestException as exc:
            raise SourceGateError(f"BLOCKED_GPR_VINTAGE_PIT_NOT_PROVEN:{stamp}:TRANSPORT") from exc
        if r.status_code != 200 or len(r.content) < 1000:
            raise SourceGateError(f"BLOCKED_GPR_VINTAGE_PIT_NOT_PROVEN:{stamp}:HTTP_{r.status_code}")
        frame = _parse_gpr_book(r.content)
        known_month = origin - pd.offsets.MonthBegin(1)
        hist = frame.loc[:known_month, "GPR"].dropna()
        if hist.empty or known_month not in hist.index:
            raise SourceGateError(f"BLOCKED_GPR_VINTAGE_PIT_NOT_PROVEN:{stamp}:OBS_{known_month.strftime('%Y-%m')}")
        lo, hi = float(hist.min()), float(hist.max())
        norm = 0.5 if hi <= lo else float((float(hist.loc[known_month]) - lo) / (hi - lo))
        result[origin] = float(np.clip(norm, 0.0, 1.0))
        passed += 1
    return result, passed


def variable_weighted_daily_return(daily: pd.Series, origin_month: pd.Timestamp, gpr_norm: float) -> float:
    origin_month = pd.Timestamp(origin_month).to_period("M").to_timestamp()
    mask = daily.index.to_period("M") == origin_month.to_period("M")
    current = daily.loc[mask].sort_index()
    before = daily.loc[daily.index < origin_month].sort_index()
    if current.empty or before.empty:
        raise SourceGateError(f"INSUFFICIENT_DAILY_RETURN_CONTEXT:{origin_month.strftime('%Y-%m')}")
    values = np.r_[float(before.iloc[-1]), current.to_numpy(float)]
    returns = np.diff(np.log(values))
    if len(returns) < MIN_DAILY:
        raise SourceGateError(f"INSUFFICIENT_DAILY_RETURNS:{origin_month.strftime('%Y-%m')}")
    lam = 0.1 * math.exp(-10.0 * float(np.clip(gpr_norm, 0.0, 1.0)))
    ages = np.arange(len(returns) - 1, -1, -1, dtype=float)
    weights = np.exp(-lam * ages)
    weights /= weights.sum()
    return float(weights @ returns)


def build_feature_frame(
    daily: pd.Series,
    monthly: pd.Series,
    gpr_norms: dict[pd.Timestamp, float],
    include_current_unknown: bool = True,
) -> pd.DataFrame:
    mr = np.log(monthly / monthly.shift(1))
    rows: list[dict] = []
    max_target = CURRENT_TARGET if include_current_unknown else LOCK_END
    for target in pd.date_range(SOURCE_START + pd.offsets.MonthBegin(7), max_target, freq="MS"):
        origin = target - pd.offsets.MonthBegin(1)
        if origin not in monthly.index or origin not in gpr_norms:
            continue
        hist_r = mr.loc[:origin].dropna()
        if len(hist_r) < 6:
            continue
        g = float(gpr_norms[origin])
        vw = variable_weighted_daily_return(daily, origin, g)
        m = target.month
        rec = {
            "target": target,
            "origin": origin,
            "origin_price": float(monthly.loc[origin]),
            "actual": float(monthly.loc[target]) if target in monthly.index and pd.notna(monthly.loc[target]) else np.nan,
            "MR_lag1": float(hist_r.iloc[-1]),
            "MR_lag2": float(hist_r.iloc[-2]),
            "MR_lag3": float(hist_r.iloc[-3]),
            "MR_abs_lag1": abs(float(hist_r.iloc[-1])),
            "MR_MA_3": float(hist_r.iloc[-3:].mean()),
            "MR_MA_6": float(hist_r.iloc[-6:].mean()),
            "MR_sign_lag1": float(np.sign(hist_r.iloc[-1])),
            "VW_DAILY_RETURN": vw,
            "GPR_norm_lagged": g,
            "month_sin": math.sin(2.0 * math.pi * m / 12.0),
            "month_cos": math.cos(2.0 * math.pi * m / 12.0),
        }
        rec["y"] = (
            float(math.log(rec["actual"] / rec["origin_price"])) if np.isfinite(rec["actual"]) else np.nan
        )
        rows.append(rec)
    if not rows:
        raise SourceGateError("NO_ELIGIBLE_FEATURE_ROWS")
    return pd.DataFrame(rows).set_index("target").sort_index()


def fit_predict_return(train: pd.DataFrame, test: pd.DataFrame, params: tuple[float, float, float]) -> float:
    C, gamma, epsilon = params
    if len(train) < MIN_FIT:
        raise ValueError("MIN_FIT_NOT_MET")
    sx = StandardScaler().fit(train[list(FEATURES)])
    sy = StandardScaler().fit(train[["y"]])
    model = SVR(kernel="rbf", C=C, gamma=gamma, epsilon=epsilon)
    model.fit(sx.transform(train[list(FEATURES)]), sy.transform(train[["y"]]).ravel())
    pred_scaled = float(model.predict(sx.transform(test[list(FEATURES)]))[0])
    return float(sy.inverse_transform(np.array([[pred_scaled]], dtype=float))[0, 0])


def tune_for_outer(frame: pd.DataFrame, target: pd.Timestamp) -> tuple[tuple[float, float, float], int, float]:
    train_all = frame[(frame.index < target) & frame["y"].notna()].copy()
    if len(train_all) < MIN_FIT:
        raise ValueError("OUTER_MIN_FIT_NOT_MET")
    candidates = list(itertools.product(C_GRID, GAMMA_GRID, EPSILON_GRID))
    eligible_inner: list[pd.Timestamp] = []
    for vt in train_all.index[-INNER_MAX:]:
        inner_train = frame[(frame.index < vt) & frame["y"].notna()]
        if len(inner_train) >= MIN_FIT:
            eligible_inner.append(pd.Timestamp(vt))
    if not eligible_inner:
        raise ValueError("NO_ELIGIBLE_INNER_ORIGINS")
    scored: list[tuple[float, float, float, float]] = []
    for C, gamma, epsilon in candidates:
        errors: list[float] = []
        for vt in eligible_inner:
            tr = frame[(frame.index < vt) & frame["y"].notna()]
            te = frame.loc[[vt]]
            pr = fit_predict_return(tr, te, (C, gamma, epsilon))
            errors.append(abs(pr - float(te["y"].iloc[0])))
        scored.append((float(np.mean(errors)), C, gamma, epsilon))
    scored.sort(key=lambda z: (z[0], z[1], z[2], z[3]))
    best = scored[0]
    return (best[1], best[2], best[3]), len(eligible_inner), best[0]


def predict_target(frame: pd.DataFrame, target: pd.Timestamp) -> dict:
    target = pd.Timestamp(target).to_period("M").to_timestamp()
    if target not in frame.index:
        raise KeyError(target)
    params, inner_n, inner_mae = tune_for_outer(frame, target)
    train = frame[(frame.index < target) & frame["y"].notna()].copy()
    test = frame.loc[[target]]
    pred_return = fit_predict_return(train, test, params)
    origin_price = float(test["origin_price"].iloc[0])
    forecast = float(origin_price * math.exp(pred_return))
    return {
        "target": target,
        "origin": pd.Timestamp(test["origin"].iloc[0]),
        "forecast": forecast,
        "pred_return": pred_return,
        "rw": origin_price,
        "actual": float(test["actual"].iloc[0]) if np.isfinite(test["actual"].iloc[0]) else np.nan,
        "C": params[0],
        "gamma": params[1],
        "epsilon": params[2],
        "inner_origins": inner_n,
        "inner_mae_log_return": inner_mae,
        "train_n": len(train),
    }


def replay(frame: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    rows: list[dict] = []
    for target in pd.date_range(start, end, freq="MS"):
        if target not in frame.index or not np.isfinite(frame.loc[target, "actual"]):
            raise SourceGateError(f"REPLAY_TARGET_MISSING:{target.strftime('%Y-%m')}")
        row = predict_target(frame, target)
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


def yearly_mae_ratios(df: pd.DataFrame) -> dict[str, float]:
    out: dict[str, float] = {}
    x = df.copy()
    x["year"] = pd.to_datetime(x["target"]).dt.year
    for year, g in x.groupby("year"):
        cand = float(np.mean(np.abs(g["forecast"] - g["actual"])))
        rw = float(np.mean(np.abs(g["rw"] - g["actual"])))
        out[str(int(year))] = cand / rw if rw > 0 else math.inf
    return out


def validation_gate(validation_metrics: dict, year_ratios: dict[str, float]) -> tuple[bool, list[str]]:
    checks = {
        "relative_mae_vs_rw_lt_1": validation_metrics["relative_mae_vs_rw"] < 1.0,
        "mape_not_worse_than_rw": validation_metrics["mape"] <= validation_metrics["rw_mape"],
        "median_ae_not_worse_than_rw": validation_metrics["median_ae"] <= validation_metrics["rw_median_ae"],
        "monthly_win_rate_gte_0_5": validation_metrics["monthly_win_rate_vs_rw"] >= 0.5,
        "all_year_mae_ratios_lte_1_5": all(v <= 1.5 for v in year_ratios.values()),
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
    for _, r in df.sort_values("target").iterrows():
        h.update(
            f"{pd.Timestamp(r['target']).strftime('%Y-%m')}|{float(r['forecast']):.10f}|{float(r['pred_return']):.12f}|{r['C']}|{r['gamma']}|{r['epsilon']}\n".encode()
        )
    return h.hexdigest()


def prefix_invariance_check(
    daily: pd.Series,
    monthly: pd.Series,
    gpr_norms: dict[pd.Timestamp, float],
    target: pd.Timestamp = pd.Timestamp("2024-06-01"),
) -> bool:
    full = build_feature_frame(daily, monthly, gpr_norms, include_current_unknown=False)
    origin = target - pd.offsets.MonthBegin(1)
    daily_prefix = daily.loc[daily.index < (origin + pd.offsets.MonthEnd(0) + pd.Timedelta(days=1))]
    monthly_prefix = monthly.loc[:origin]
    gpr_prefix = {m: v for m, v in gpr_norms.items() if m <= origin}
    prefix = build_feature_frame(daily_prefix, monthly_prefix, gpr_prefix, include_current_unknown=False)
    if target not in full.index or target not in prefix.index:
        return False
    a = full.loc[target, list(FEATURES)].to_numpy(float)
    b = prefix.loc[target, list(FEATURES)].to_numpy(float)
    return bool(np.allclose(a, b, atol=1e-12, rtol=0.0))


def contract_self_audit() -> None:
    contract = json.loads(CONTRACT_PATH.read_text())
    assert contract["engine_id"] == ENGINE_ID
    assert contract["archived_engine_status_must_remain"] == "BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN"
    assert contract["production_authorized"] is False
    assert contract["prospective_claim"] is False
    assert contract["direction_vote_permitted"] is False
    assert contract["db_writes_permitted"] is False
    assert tuple(contract["features"]) == FEATURES
    assert tuple(contract["model"]["C_grid"]) == C_GRID
    assert tuple(contract["model"]["gamma_grid"]) == GAMMA_GRID
    assert tuple(contract["model"]["epsilon_grid"]) == EPSILON_GRID


def execute(out_dir: Path) -> dict:
    contract_self_audit()
    api_key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    daily = fetch_twelve_ny17_hourly(api_key)
    monthly, counts = audit_twelve_coverage(daily)

    # Origins needed for all eligible feature rows through the current reconstruction.
    eligible_origins = pd.date_range(pd.Timestamp("2020-09-01"), CURRENT_ORIGIN, freq="MS")
    gpr_session = requests.Session()
    gpr_session.headers.update({"User-Agent": "Gold-Control-VW-Successor-V1/1.0"})
    gpr_norms, gpr_passed = fetch_gpr_norms(gpr_session, eligible_origins)

    audit = SourceAudit(
        twelve_months_expected=len(month_range(SOURCE_START, SOURCE_END)),
        twelve_months_passed=len(counts),
        twelve_min_daily_count=min(counts.values()),
        gpr_vintages_expected=len(eligible_origins),
        gpr_vintages_passed=gpr_passed,
        input_fingerprint_sha256=stable_input_fingerprint(daily, gpr_norms),
    )
    frame = build_feature_frame(daily, monthly, gpr_norms, include_current_unknown=True)

    if not prefix_invariance_check(daily, monthly, gpr_norms):
        raise RuntimeError("PREFIX_INVARIANCE_FAIL")

    validation_a = replay(frame, VALIDATION_START, VALIDATION_END)
    validation_b = replay(frame, VALIDATION_START, VALIDATION_END)
    if prediction_fingerprint(validation_a) != prediction_fingerprint(validation_b):
        raise RuntimeError("DETERMINISTIC_RERUN_FAIL")

    lock = replay(frame, LOCK_START, LOCK_END)
    vm = metrics(validation_a)
    lm = metrics(lock)
    yr = yearly_mae_ratios(validation_a)
    eligible, failed = validation_gate(vm, yr)
    current = predict_target(frame, CURRENT_TARGET)

    status = (
        "HISTORICAL_REPLAY_SPECIALIZED_SHADOW_ELIGIBLE_PROSPECTIVE_VALIDATION_REQUIRED"
        if eligible
        else "HISTORICAL_REPLAY_SPECIALIZED_NOT_SHADOW_ELIGIBLE"
    )
    evidence = {
        "engine_id": ENGINE_ID,
        "contract_version": "V1_2026-09-04",
        "evidence_class": "HISTORICAL_REPLAY_SUCCESSOR_RESEARCH",
        "prospective_claim": False,
        "production_authorized": False,
        "db_writes": "NONE",
        "archived_vw_status_changed": False,
        "source_audit": audit.__dict__,
        "validation_window": ["2023-01", "2024-12"],
        "validation_metrics": vm,
        "validation_year_mae_ratio_vs_rw": yr,
        "validation_gate_pass": eligible,
        "validation_failed_gates": failed,
        "locked_window": ["2025-01", "2026-07"],
        "locked_metrics_diagnostic_only": lm,
        "deterministic_rerun": True,
        "prefix_invariance": True,
        "validation_prediction_fingerprint": prediction_fingerprint(validation_a),
        "locked_prediction_fingerprint": prediction_fingerprint(lock),
        "current_origin_reconstruction": {
            "origin": "2026-08-31",
            "target_month": "2026-09",
            "forecast_usd_oz": current["forecast"],
            "predicted_log_return": current["pred_return"],
            "rw_reference_usd_oz": current["rw"],
            "hyperparameters": {"C": current["C"], "gamma": current["gamma"], "epsilon": current["epsilon"]},
            "inner_origins": current["inner_origins"],
            "train_n": current["train_n"],
            "prospective_claim": False,
            "evidence_semantic": "ORIGIN_RECONSTRUCTION/HISTORICAL_REPLAY",
        },
        "maximum_v1_status": status,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "vw_midas_svr_xau_successor_v1_evidence.json").write_text(json.dumps(evidence, indent=2, sort_keys=True))
    source_public = {
        "twelve_months_expected": audit.twelve_months_expected,
        "twelve_months_passed": audit.twelve_months_passed,
        "twelve_min_daily_count": audit.twelve_min_daily_count,
        "gpr_vintages_expected": audit.gpr_vintages_expected,
        "gpr_vintages_passed": audit.gpr_vintages_passed,
        "input_fingerprint_sha256": audit.input_fingerprint_sha256,
        "raw_vendor_values_logged": False,
        "raw_vendor_values_committed": False,
    }
    (out_dir / "vw_midas_svr_xau_successor_v1_source_audit.json").write_text(json.dumps(source_public, indent=2, sort_keys=True))
    return evidence


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(ROOT / "vw_midas_svr_xau_successor_v1" / "runtime_evidence"))
    args = ap.parse_args()
    try:
        evidence = execute(Path(args.out_dir))
    except SourceGateError as exc:
        print(f"VW_SUCCESSOR_SOURCE_GATE=BLOCKED")
        print(f"VW_SUCCESSOR_BLOCK_REASON={exc}")
        print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
        print("DATABASE_WRITES=NONE")
        raise
    print("VW_SUCCESSOR_SOURCE_GATE=PASS")
    print(f"VALIDATION_GATE_PASS={str(evidence['validation_gate_pass']).upper()}")
    print(f"MAXIMUM_V1_STATUS={evidence['maximum_v1_status']}")
    print(f"VALIDATION_RELATIVE_MAE_VS_RW={evidence['validation_metrics']['relative_mae_vs_rw']:.9f}")
    print(f"VALIDATION_MAPE={evidence['validation_metrics']['mape']:.9f}")
    print(f"VALIDATION_RW_MAPE={evidence['validation_metrics']['rw_mape']:.9f}")
    print(f"VALIDATION_MONTHLY_WIN_RATE={evidence['validation_metrics']['monthly_win_rate_vs_rw']:.9f}")
    print(f"LOCK_RELATIVE_MAE_VS_RW_DIAGNOSTIC={evidence['locked_metrics_diagnostic_only']['relative_mae_vs_rw']:.9f}")
    print(f"CURRENT_SEP2026_RECON_FORECAST_USD_OZ={evidence['current_origin_reconstruction']['forecast_usd_oz']:.9f}")
    print("CURRENT_SEP2026_PROSPECTIVE_CLAIM=FALSE")
    print("DETERMINISTIC_RERUN=PASS")
    print("PREFIX_INVARIANCE=PASS")
    print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
    print("DATABASE_WRITES=NONE")


if __name__ == "__main__":
    main()
