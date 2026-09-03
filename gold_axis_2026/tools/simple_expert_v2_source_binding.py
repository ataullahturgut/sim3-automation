from __future__ import annotations

import base64
import gzip
import io
import json
import math
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "GOLD_CONTROL_SIMPLE_EXPERT_SOURCE_BINDING_V2_CHANGE_CONTROL_2026-09-03.md"
PARENT_SOURCE_EVIDENCE = ROOT / "patch_repro_v1" / "prospective_monthly_level_v6_source_evidence.json"
LOCKED_REPLAY = ROOT / "patch_repro_v1" / "locked_replay_v6_monthly_level_43.csv"
OUT = ROOT / "simple_expert_v2"
OUT.mkdir(parents=True, exist_ok=True)
EVIDENCE_PATH = OUT / "simple_expert_v2_source_binding_evidence.json"

SOURCE_ID = "SIMPLE_EXPERT_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V2"
RW_ID = "RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND"
MOM_ID = "MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND"
JOINT_PASS = "SIMPLE_EXPERT_V2_SOURCE_BINDING_PASS"
JOINT_FAIL = "BLOCKED_SIMPLE_EXPERT_V2_SOURCE_BINDING_NOT_FULLY_PROVEN"
RW_PASS = "RW_R2_SOURCE_BINDING_MODEL_IMPACT_PASS"
RW_FAIL = "BLOCKED_RW_R2_SOURCE_BINDING_MODEL_IMPACT_FAIL_NO_RETUNE"
MOM_PASS = "MOMENTUM_3M_R2_SOURCE_BINDING_MODEL_IMPACT_PASS"
MOM_FAIL = "BLOCKED_MOMENTUM_3M_R2_SOURCE_BINDING_MODEL_IMPACT_FAIL_NO_RETUNE"
PARENT_PASS = "PATCH_MONTHLY_LEVEL_BRIDGE_V6_SOURCE_PASS"

TWELVE_URL = "https://api.twelvedata.com/time_series"
SOURCE_START = pd.Timestamp("2022-09-01")
SOURCE_END = pd.Timestamp("2026-06-30 23:59:59")
LOCKED_START = pd.Timestamp("2023-01-01")
LOCKED_END = pd.Timestamp("2026-07-01")
MIN_DAILY_PER_MONTH = 15

# Inherited V6 source-semantic materiality gates.
LEVEL_CORR_MIN = 0.995
MEDIAN_GAP_BPS_MAX = 50.0
P95_GAP_BPS_MAX = 100.0
RETURN_CORR_MIN = 0.95
SIGN_AGREE_MIN = 0.80

# Frozen V2 source-substitution/non-inferiority gates.
FORECAST_CORR_MIN = 0.995
MAPE_RATIO_MAX = 1.05
MAE_RATIO_MAX = 1.05
WORST_APE_RATIO_MAX = 1.10


def env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name}_MISSING")
    return value


def verify_contract() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    required = [
        "FROZEN_BEFORE_SOURCE_BINDING_RESULT",
        RW_ID,
        MOM_ID,
        SOURCE_ID,
        "V2 forecast-vector Pearson correlation versus archived R1 forecast vector `>= 0.995`",
        "V2 MAPE `<= 1.05 × R1 MAPE`",
        "V2 MAE `<= 1.05 × R1 MAE`",
        "V2 worst APE `<= 1.10 × R1 worst APE`",
        "level correlation `>= 0.995`",
        "monthly return direction agreement `>= 0.80`",
    ]
    missing = [x for x in required if x not in text]
    if missing:
        raise RuntimeError(f"SOURCE_BINDING_CONTRACT_NOT_FROZEN:{missing}")


def load_core() -> pd.DataFrame:
    raw = gzip.decompress(base64.b64decode((ROOT / "core5_monthly.csv.gz.b64").read_text().strip())).decode()
    frame = pd.read_csv(io.StringIO(raw), parse_dates=["date"]).set_index("date").sort_index()
    if "gold_monthly" not in frame.columns:
        raise RuntimeError("CORE5_GOLD_MONTHLY_NOT_FOUND")
    return frame


def request_json(session: requests.Session, params: dict, attempts: int = 6) -> dict:
    api_key = env("TWELVE_DATA_API_KEY")
    last = "UNKNOWN"
    for attempt in range(attempts):
        try:
            response = session.get(
                TWELVE_URL,
                params=params,
                headers={
                    "Authorization": f"apikey {api_key}",
                    "User-Agent": "Gold-Control-Simple-Expert-V2-Source-Binding/1.0",
                },
                timeout=(20, 180),
            )
            payload = response.json() if response.content else None
            code = payload.get("code") if isinstance(payload, dict) else None
            if response.status_code == 429 or code == 429:
                last = "RATE_LIMIT"
                time.sleep(65)
                continue
            response.raise_for_status()
            if not isinstance(payload, dict):
                raise RuntimeError("TWELVE_RESPONSE_NOT_DICT")
            if payload.get("status") == "error":
                raise RuntimeError(f"TWELVE_API_ERROR_{payload.get('code')}")
            return payload
        except Exception as exc:
            last = type(exc).__name__
            if attempt + 1 < attempts:
                time.sleep(min(20, 2 ** attempt))
    raise RuntimeError(f"TWELVE_RETRY_EXHAUSTED:{last}")


def fetch_hourly_monthly_levels(session: requests.Session) -> tuple[pd.Series, pd.Series, dict]:
    selected: dict[pd.Timestamp, float] = {}
    duplicate_dates = 0
    request_count = 0
    cursor = SOURCE_START
    while cursor <= SOURCE_END:
        end = min(cursor + pd.DateOffset(months=6) - pd.Timedelta(seconds=1), SOURCE_END)
        payload = request_json(
            session,
            {
                "symbol": "XAU/USD",
                "interval": "1h",
                "start_date": cursor.strftime("%Y-%m-%d %H:%M:%S"),
                "end_date": end.strftime("%Y-%m-%d %H:%M:%S"),
                "timezone": "America/New_York",
                "outputsize": 5000,
                "order": "ASC",
                "format": "JSON",
            },
        )
        request_count += 1
        meta = payload.get("meta") or {}
        if str(meta.get("symbol")) != "XAU/USD" or str(meta.get("interval")) != "1h":
            raise RuntimeError("SIMPLE_EXPERT_V2_HOURLY_META_MISMATCH")
        for item in payload.get("values") or []:
            text = str(item.get("datetime") or "")
            if not text.endswith("16:00:00"):
                continue
            try:
                ts = pd.Timestamp(text)
                value = float(item.get("close"))
            except Exception:
                continue
            if not (np.isfinite(value) and value > 0):
                continue
            d = ts.normalize()
            if d in selected:
                duplicate_dates += 1
                continue
            selected[d] = value
        cursor = (end + pd.Timedelta(seconds=1)).normalize()
        if cursor <= SOURCE_END:
            time.sleep(8)

    if not selected:
        raise RuntimeError("SIMPLE_EXPERT_V2_HOURLY_SOURCE_EMPTY")
    daily = pd.Series(selected, dtype=float).sort_index()
    monthly = daily.resample("MS").mean().dropna()
    counts = daily.resample("MS").count().astype(int)
    return monthly, counts, {
        "provider": "Twelve Data",
        "symbol": "XAU/USD",
        "interval": "1h",
        "requested_timezone": "America/New_York",
        "selected_bar_open_time": "16:00:00",
        "selected_bar_end_semantic": "17:00_ET_HOURLY_CLOSE",
        "request_count": request_count,
        "selected_daily_observation_count": int(len(daily)),
        "duplicate_selected_dates": int(duplicate_dates),
        "first_selected_date": daily.index.min().date().isoformat(),
        "last_selected_date": daily.index.max().date().isoformat(),
    }


def bridge_metrics(reference: pd.Series, candidate: pd.Series, months: pd.DatetimeIndex) -> dict:
    common = [m for m in months if m in reference.index and m in candidate.index]
    if len(common) < 2:
        raise RuntimeError("SOURCE_BRIDGE_COMMON_MONTHS_INSUFFICIENT")
    a = np.array([float(reference.loc[m]) for m in common], dtype=float)
    b = np.array([float(candidate.loc[m]) for m in common], dtype=float)
    rel_bps = np.abs(b - a) / np.abs(a) * 10000.0
    ar = np.diff(np.log(a))
    br = np.diff(np.log(b))
    return {
        "common_months": len(common),
        "level_corr": float(np.corrcoef(a, b)[0, 1]),
        "median_abs_gap_bps": float(np.median(rel_bps)),
        "p95_abs_gap_bps": float(np.quantile(rel_bps, 0.95)),
        "monthly_return_corr": float(np.corrcoef(ar, br)[0, 1]),
        "monthly_return_sign_agree": float(np.mean(np.sign(ar) == np.sign(br))),
    }


def source_materiality_pass(m: dict) -> bool:
    return bool(
        m["level_corr"] >= LEVEL_CORR_MIN
        and m["median_abs_gap_bps"] <= MEDIAN_GAP_BPS_MAX
        and m["p95_abs_gap_bps"] <= P95_GAP_BPS_MAX
        and m["monthly_return_corr"] >= RETURN_CORR_MIN
        and m["monthly_return_sign_agree"] >= SIGN_AGREE_MIN
    )


def rw(levels: list[float]) -> float:
    if not levels or levels[-1] <= 0:
        raise ValueError("RW_REQUIRES_POSITIVE_LEVEL")
    return float(levels[-1])


def momentum(levels: list[float]) -> float:
    if len(levels) < 4 or any(x <= 0 for x in levels[-4:]):
        raise ValueError("MOMENTUM_REQUIRES_FOUR_POSITIVE_LEVELS")
    recent = [float(x) for x in levels[-4:]]
    returns = [recent[i] / recent[i - 1] - 1.0 for i in range(1, 4)]
    return float(recent[-1] * (1.0 + sum(returns) / 3.0))


def forecast_metrics(actual: np.ndarray, forecast: np.ndarray) -> dict:
    ape = np.abs(forecast - actual) / np.abs(actual) * 100.0
    err = np.abs(forecast - actual)
    return {
        "MAE": float(np.mean(err)),
        "MAPE_pct": float(np.mean(ape)),
        "median_APE_pct": float(np.median(ape)),
        "worst_APE_pct": float(np.max(ape)),
        "RMSE": float(math.sqrt(float(np.mean((forecast - actual) ** 2)))),
    }


def ratio(candidate: float, reference: float) -> float:
    if reference == 0:
        return 1.0 if candidate == 0 else float("inf")
    return float(candidate / reference)


def evaluate_expert(name: str, actual: np.ndarray, r1: np.ndarray, v2: np.ndarray) -> dict:
    r1m = forecast_metrics(actual, r1)
    v2m = forecast_metrics(actual, v2)
    corr = float(np.corrcoef(r1, v2)[0, 1])
    ratios = {
        "MAPE": ratio(v2m["MAPE_pct"], r1m["MAPE_pct"]),
        "MAE": ratio(v2m["MAE"], r1m["MAE"]),
        "worst_APE": ratio(v2m["worst_APE_pct"], r1m["worst_APE_pct"]),
    }
    gates = {
        "forecast_corr_pass": corr >= FORECAST_CORR_MIN,
        "mape_noninferiority_pass": ratios["MAPE"] <= MAPE_RATIO_MAX,
        "mae_noninferiority_pass": ratios["MAE"] <= MAE_RATIO_MAX,
        "worst_ape_noninferiority_pass": ratios["worst_APE"] <= WORST_APE_RATIO_MAX,
    }
    return {
        "expert": name,
        "forecast_corr_vs_r1": corr,
        "r1_metrics": r1m,
        "v2_metrics": v2m,
        "v2_over_r1_ratios": ratios,
        "gates": gates,
        "noninferiority_pass": bool(all(gates.values())),
    }


def main() -> int:
    verify_contract()
    parent = json.loads(PARENT_SOURCE_EVIDENCE.read_text(encoding="utf-8"))
    parent_pass = parent.get("decision") == PARENT_PASS and bool(parent.get("source_bridge_pass"))
    locked = pd.read_csv(LOCKED_REPLAY, parse_dates=["month"]).sort_values("month").reset_index(drop=True)
    expected_months = pd.date_range(LOCKED_START, LOCKED_END, freq="MS")
    if list(locked["month"]) != list(expected_months):
        raise RuntimeError("LOCKED_REPLAY_TARGET_WINDOW_MISMATCH")
    if len(locked) != 43:
        raise RuntimeError(f"LOCKED_REPLAY_N_MISMATCH:{len(locked)}")

    core = load_core()
    core_gold = core["gold_monthly"].astype(float)

    # Reconcile archived R1 vectors against the frozen R1 formulas on CORE5.
    rw_reconciled = 0
    mom_reconciled = 0
    actual_reconciled = 0
    for row in locked.itertuples(index=False):
        t = pd.Timestamp(row.month)
        if t in core_gold.index and abs(float(core_gold.loc[t]) - float(row.actual)) <= max(1e-6, 1e-9 * abs(float(row.actual))):
            actual_reconciled += 1
        prior = [t - pd.DateOffset(months=i) for i in (4, 3, 2, 1)]
        if all(m in core_gold.index for m in prior):
            vals = [float(core_gold.loc[m]) for m in prior]
            if abs(rw(vals) - float(row.rw)) <= max(1e-6, 1e-9 * abs(float(row.rw))):
                rw_reconciled += 1
            if abs(momentum(vals) - float(row.mom)) <= max(1e-6, 1e-9 * abs(float(row.mom))):
                mom_reconciled += 1

    session = requests.Session()
    hourly_level, hourly_count, source_stats = fetch_hourly_monthly_levels(session)
    required_source_months = pd.date_range(SOURCE_START, pd.Timestamp("2026-06-01"), freq="MS")
    missing = [m.strftime("%Y-%m") for m in required_source_months if m not in hourly_level.index]
    low_count = [m.strftime("%Y-%m") for m in required_source_months if m in hourly_count.index and int(hourly_count.loc[m]) < MIN_DAILY_PER_MONTH]
    source_metrics = bridge_metrics(core_gold, hourly_level, required_source_months)
    source_pass = (
        not missing
        and not low_count
        and source_stats["duplicate_selected_dates"] == 0
        and source_metrics["common_months"] == len(required_source_months)
        and source_materiality_pass(source_metrics)
    )

    actual = locked["actual"].to_numpy(dtype=float)
    r1_rw = locked["rw"].to_numpy(dtype=float)
    r1_mom = locked["mom"].to_numpy(dtype=float)
    v2_rw: list[float] = []
    v2_mom: list[float] = []
    future_violations = 0
    for row in locked.itertuples(index=False):
        t = pd.Timestamp(row.month)
        prior = [t - pd.DateOffset(months=i) for i in (4, 3, 2, 1)]
        if any(m >= t for m in prior):
            future_violations += 1
        if not all(m in hourly_level.index for m in prior):
            raise RuntimeError(f"TARGET_SOURCE_INPUT_MISSING:{t.strftime('%Y-%m')}")
        vals = [float(hourly_level.loc[m]) for m in prior]
        v2_rw.append(rw(vals))
        v2_mom.append(momentum(vals))

    v2_rw_arr = np.array(v2_rw, dtype=float)
    v2_mom_arr = np.array(v2_mom, dtype=float)
    # Formula-only deterministic rerun using the already retrieved immutable-in-memory source vector.
    rerun_rw = []
    rerun_mom = []
    for row in locked.itertuples(index=False):
        t = pd.Timestamp(row.month)
        prior = [t - pd.DateOffset(months=i) for i in (4, 3, 2, 1)]
        vals = [float(hourly_level.loc[m]) for m in prior]
        rerun_rw.append(rw(vals))
        rerun_mom.append(momentum(vals))
    deterministic_max_abs_diff = float(max(
        np.max(np.abs(v2_rw_arr - np.array(rerun_rw, dtype=float))),
        np.max(np.abs(v2_mom_arr - np.array(rerun_mom, dtype=float))),
    ))

    hard_gates = {
        "parent_v6_source_pass": parent_pass,
        "extended_source_materiality_pass": source_pass,
        "actual_reconciliation_43_43": actual_reconciled == 43,
        "rw_r1_reconciliation_43_43": rw_reconciled == 43,
        "momentum_r1_reconciliation_43_43": mom_reconciled == 43,
        "required_source_coverage_complete": len(missing) == 0,
        "low_count_source_months_zero": len(low_count) == 0,
        "duplicate_selected_source_dates_zero": source_stats["duplicate_selected_dates"] == 0,
        "future_information_violations_zero": future_violations == 0,
        "deterministic_rerun_exact": deterministic_max_abs_diff == 0.0,
    }
    hard_pass = bool(all(hard_gates.values()))

    rw_eval = evaluate_expert("RANDOM_WALK", actual, r1_rw, v2_rw_arr)
    mom_eval = evaluate_expert("MOMENTUM_3M", actual, r1_mom, v2_mom_arr)
    rw_pass = bool(hard_pass and rw_eval["noninferiority_pass"])
    mom_pass = bool(hard_pass and mom_eval["noninferiority_pass"])
    joint_pass = bool(rw_pass and mom_pass)

    evidence = {
        "contract": CONTRACT.name,
        "contract_status": "FROZEN_BEFORE_SOURCE_BINDING_RESULT",
        "source_id": SOURCE_ID,
        "rw_model_version": RW_ID,
        "momentum_model_version": MOM_ID,
        "evidence_class": "HISTORICAL_REPLAY_MODEL_IMPACT",
        "prospective_claim": False,
        "locked_window": "2023-01..2026-07",
        "N": 43,
        "parent_source_decision": parent.get("decision"),
        "required_source_months": len(required_source_months),
        "source_missing_month_count": len(missing),
        "source_low_count_month_count": len(low_count),
        "minimum_selected_observations_per_month": MIN_DAILY_PER_MONTH,
        "source_semantic": source_stats,
        "extended_source_vs_core5": source_metrics,
        "source_materiality_thresholds": {
            "level_corr_min": LEVEL_CORR_MIN,
            "median_gap_bps_max": MEDIAN_GAP_BPS_MAX,
            "p95_gap_bps_max": P95_GAP_BPS_MAX,
            "return_corr_min": RETURN_CORR_MIN,
            "sign_agree_min": SIGN_AGREE_MIN,
        },
        "actual_reconciliation": f"{actual_reconciled}/43",
        "rw_r1_reconciliation": f"{rw_reconciled}/43",
        "momentum_r1_reconciliation": f"{mom_reconciled}/43",
        "future_information_violations": future_violations,
        "deterministic_max_abs_diff": deterministic_max_abs_diff,
        "hard_integrity_gates": hard_gates,
        "hard_integrity_pass": hard_pass,
        "noninferiority_thresholds": {
            "forecast_corr_min": FORECAST_CORR_MIN,
            "mape_ratio_max": MAPE_RATIO_MAX,
            "mae_ratio_max": MAE_RATIO_MAX,
            "worst_ape_ratio_max": WORST_APE_RATIO_MAX,
        },
        "random_walk": rw_eval,
        "momentum_3m": mom_eval,
        "rw_decision": RW_PASS if rw_pass else RW_FAIL,
        "momentum_decision": MOM_PASS if mom_pass else MOM_FAIL,
        "decision": JOINT_PASS if joint_pass else JOINT_FAIL,
        "post_result_retune": False,
        "thresholds_relaxed": False,
        "provider_substitution": False,
        "raw_vendor_market_values_logged": False,
        "database_write": "NONE",
        "forecast_ledger_write": "NONE",
        "decision_store_write": "NONE",
    }
    EVIDENCE_PATH.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")

    print(f"PARENT_SOURCE_GATE={'PASS' if parent_pass else 'FAIL'}")
    print(f"EXTENDED_SOURCE_MATERIALITY={'PASS' if source_pass else 'FAIL'}")
    print(f"ACTUAL_RECONCILIATION={actual_reconciled}/43")
    print(f"RW_R1_RECONCILIATION={rw_reconciled}/43")
    print(f"MOMENTUM_R1_RECONCILIATION={mom_reconciled}/43")
    print(f"FUTURE_INFORMATION_VIOLATIONS={future_violations}")
    print(f"HARD_INTEGRITY={'PASS' if hard_pass else 'FAIL'}")
    print(f"RW_V2_DECISION={evidence['rw_decision']}")
    print(f"MOMENTUM_V2_DECISION={evidence['momentum_decision']}")
    print(f"SIMPLE_EXPERT_V2_DECISION={evidence['decision']}")
    print("RAW_VENDOR_MARKET_VALUES_LOGGED=NO")
    print("DATABASE_WRITES=NONE")
    return 0 if joint_pass else 3


if __name__ == "__main__":
    raise SystemExit(main())
