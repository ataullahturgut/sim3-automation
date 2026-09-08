from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg

from gold_axis_2026.tools import market_shock_challenger_v2 as v2
from gold_axis_2026.tools import market_shock_v2_realized_move_proxy_audit as proxy
from gold_axis_2026.tools import market_shock_v2_lm_corroboration_audit as corr

ONE_MIN_EXPECTED_ROWS = 1_305_943
ONE_MIN_EXPECTED_FIRST = "2023-01-02T23:00:00+00:00"
ONE_MIN_EXPECTED_LAST = "2026-05-31T23:59:00+00:00"
AUDIT_START = pd.Timestamp("2026-01-01T00:00:00Z")
AUDIT_END_EXCLUSIVE = pd.Timestamp("2026-06-01T00:00:00Z")
ALPHAS = (0.001, 0.01, 0.05)
FREQ_SPECS = {
    "1m": {"minutes": 1, "N": 1440, "K": 1350, "tolerance_minutes": 5},
    "3m": {"minutes": 3, "N": 480, "K": 450, "tolerance_minutes": 5},
    "10m": {"minutes": 10, "N": 144, "K": 135, "tolerance_minutes": 10},
}


def _db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL is not set")
    return value


def load_one_minute_common_support() -> pd.DataFrame:
    with psycopg.connect(_db_url()) as conn, conn.cursor() as cur:
        cur.execute(
            """
            select observation_ts, close
            from xau_intraday_research_cache_1m
            where observation_ts < %s
            order by observation_ts
            """,
            (AUDIT_END_EXCLUSIVE.to_pydatetime(),),
        )
        rows = cur.fetchall()
    frame = pd.DataFrame({
        "ts": [pd.Timestamp(r[0]) for r in rows],
        "close": [float(r[1]) for r in rows],
    })
    if len(frame) != ONE_MIN_EXPECTED_ROWS:
        raise RuntimeError(f"ONE_MIN_ROW_COUNT_MISMATCH:{len(frame)}:{ONE_MIN_EXPECTED_ROWS}")
    if frame["ts"].min().isoformat() != ONE_MIN_EXPECTED_FIRST:
        raise RuntimeError(f"ONE_MIN_FIRST_TS_MISMATCH:{frame['ts'].min().isoformat()}:{ONE_MIN_EXPECTED_FIRST}")
    if frame["ts"].max().isoformat() != ONE_MIN_EXPECTED_LAST:
        raise RuntimeError(f"ONE_MIN_LAST_TS_MISMATCH:{frame['ts'].max().isoformat()}:{ONE_MIN_EXPECTED_LAST}")
    if (frame["close"] <= 0).any():
        raise RuntimeError("ONE_MIN_NONPOSITIVE_CLOSE")
    return frame


def build_frequency(raw1: pd.DataFrame, minutes: int, n_intraday: int, k_local: int) -> pd.DataFrame:
    if minutes == 1:
        x = raw1[["ts", "close"]].copy()
    else:
        x = (
            raw1.set_index("ts")[["close"]]
            .resample(f"{minutes}min", label="right", closed="right")
            .last()
            .dropna()
            .reset_index()
        )
    x = x.sort_values("ts").reset_index(drop=True)
    x["logp"] = np.log(x["close"].astype(float))
    x["gap_s"] = x["ts"].diff().dt.total_seconds()
    x["ret"] = x["logp"].diff()
    expected_gap = float(minutes * 60)
    valid_gap = x["gap_s"].between(expected_gap - 1.0, expected_gap + 1.0, inclusive="both")
    x.loc[~valid_gap, "ret"] = np.nan
    slots_per_hour = 60 // minutes
    x["slot"] = (
        x["ts"].dt.weekday * n_intraday
        + x["ts"].dt.hour * slots_per_hour
        + (x["ts"].dt.minute // minutes)
    )
    x["utc_date"] = x["ts"].dt.floor("D")
    pair = x["ret"].abs() * x["ret"].shift(1).abs()
    x["local_var"] = pair.rolling(k_local - 2, min_periods=k_local - 2).mean().shift(1)
    x["local_sigma"] = np.sqrt(x["local_var"])
    return x


def score_frequency(raw1: pd.DataFrame, label: str, spec: dict) -> tuple[pd.DataFrame, dict]:
    minutes = int(spec["minutes"])
    n_intraday = int(spec["N"])
    k_local = int(spec["K"])
    data = build_frequency(raw1, minutes, n_intraday, k_local)
    train = data[data["ts"] < AUDIT_START].copy()
    hold = data[(data["ts"] >= AUDIT_START) & (data["ts"] < AUDIT_END_EXCLUSIVE)].copy()
    if len(train) < 50_000:
        raise RuntimeError(f"ALT_TRAIN_TOO_SMALL:{label}:{len(train)}")
    periodicity = v2.fit_periodicity(train)
    hold["period_factor"] = hold["slot"].map(periodicity)
    denom = hold["local_sigma"] * hold["period_factor"]
    hold["lm_score"] = hold["ret"].abs() / denom
    hold["lm_eligible"] = hold["lm_score"].replace([np.inf, -np.inf], np.nan).notna()
    criticals = {}
    for alpha in ALPHAS:
        key = f"sig_{alpha:g}"
        critical = float(v2.lm_critical(alpha, n=n_intraday))
        criticals[str(alpha)] = critical
        hold[key] = hold["lm_eligible"] & hold["lm_score"].gt(critical)
    meta = {
        "label": label,
        "minutes": minutes,
        "N": n_intraday,
        "K": k_local,
        "temporal_bandwidth_minutes": minutes * k_local,
        "train_rows": int(len(train)),
        "train_first_ts": train["ts"].min().isoformat(),
        "train_last_ts": train["ts"].max().isoformat(),
        "holdout_rows": int(len(hold)),
        "holdout_eligible": int(hold["lm_eligible"].sum()),
        "periodicity_slots": int(len(periodicity)),
        "criticals": criticals,
        "signal_bars": {str(a): int(hold[f"sig_{a:g}"].sum()) for a in ALPHAS},
    }
    return hold.reset_index(drop=True), meta


def authoritative_jan_may() -> tuple[pd.DataFrame, list[dict], dict]:
    raw5 = corr.load_cache()
    data5 = v2.build_returns(raw5)
    train5 = data5[data5["ts"] < AUDIT_START].copy()
    periodicity5 = v2.fit_periodicity(train5)
    train5s = v2.add_scores(train5, periodicity5)
    evt30 = v2.fit_evt(train5s["score30"])
    segment_report, seg5, _ = v2.score_segment(data5, 2026, periodicity5, evt30)
    seg5 = seg5[(seg5["ts"] >= AUDIT_START) & (seg5["ts"] < AUDIT_END_EXCLUSIVE)].copy().reset_index(drop=True)
    seg5 = proxy.add_raw_moves(seg5)
    seg5, abd_meta = corr.add_abd_wsd(seg5)
    lm10_full, lm10_meta = corr.score_lm10(raw5)
    prior_rows = corr.classify_episodes(seg5, lm10_full)
    prior_rows = [r for r in prior_rows if r["has_lm"]]
    base = {
        "full_2026_segment_report_reference": segment_report,
        "jan_may_v2_signal_bars": int(seg5["shock_sig"].sum()),
        "jan_may_lm_signal_bars": int(seg5["lm_sig"].sum()),
        "jan_may_evt30_signal_bars": int(seg5["evt30_sig"].sum()),
        "jan_may_lm_episodes": int(len(prior_rows)),
        "abd5": abd_meta,
        "lm10": lm10_meta,
    }
    return seg5, prior_rows, base


def _times_for_episode(seg5: pd.DataFrame, ep: dict) -> pd.DatetimeIndex:
    g = seg5.iloc[ep["start_pos"] : ep["end_pos"] + 1]
    return pd.DatetimeIndex(pd.to_datetime(g.loc[g["lm_sig"], "ts"], utc=True))


def _signal_times(scored: pd.DataFrame, alpha: float) -> np.ndarray:
    col = f"sig_{alpha:g}"
    ts = pd.to_datetime(scored.loc[scored[col], "ts"], utc=True)
    return ts.astype("int64").to_numpy()


def _confirms(base_times: pd.DatetimeIndex, signal_ns: np.ndarray, tolerance_minutes: int) -> bool:
    if len(base_times) == 0 or len(signal_ns) == 0:
        return False
    tol_ns = int(pd.Timedelta(minutes=tolerance_minutes).value)
    arr = np.sort(signal_ns)
    for t in base_times.astype("int64"):
        pos = int(np.searchsorted(arr, t))
        if pos < len(arr) and abs(int(arr[pos]) - int(t)) <= tol_ns:
            return True
        if pos > 0 and abs(int(arr[pos - 1]) - int(t)) <= tol_ns:
            return True
    return False


def classify_multifrequency(seg5: pd.DataFrame, prior_rows: list[dict], scored: dict[str, pd.DataFrame]) -> list[dict]:
    caches: dict[tuple[str, float], np.ndarray] = {}
    for label, frame in scored.items():
        for alpha in ALPHAS:
            caches[(label, alpha)] = _signal_times(frame, alpha)

    rows: list[dict] = []
    for ep in prior_rows:
        base_times = _times_for_episode(seg5, ep)
        confirms: dict[str, dict[str, bool]] = {}
        for label, spec in FREQ_SPECS.items():
            confirms[label] = {}
            for alpha in ALPHAS:
                confirms[label][str(alpha)] = _confirms(
                    base_times,
                    caches[(label, alpha)],
                    int(spec["tolerance_minutes"]),
                )

        p1 = confirms["1m"]["0.001"]
        p3 = confirms["3m"]["0.001"]
        p10 = confirms["10m"]["0.001"]
        primary_count = int(p1) + int(p3) + int(p10)
        if primary_count >= 2 and (p3 or p10):
            freq_class = "FREQ_STRONG"
        elif p3 or p10:
            freq_class = "FREQ_CONFIRMED"
        elif p1:
            freq_class = "MICRO_ONLY"
        else:
            freq_class = "FREQ_ISOLATED"

        marginal_class = None
        if freq_class == "FREQ_ISOLATED":
            any99 = any(confirms[label]["0.01"] for label in FREQ_SPECS)
            any95 = any(confirms[label]["0.05"] for label in FREQ_SPECS)
            if any99:
                marginal_class = "MARGINAL_99"
            elif any95:
                marginal_class = "MARGINAL_95"
            else:
                marginal_class = "ISOLATED_EVEN_95"

        row = dict(ep)
        row.update({
            "frequency_confirms": confirms,
            "frequency_class": freq_class,
            "marginal_class": marginal_class,
            "prior_lm_only_uncorroborated": ep["tier"] == "LM_ONLY_UNCORROBORATED",
        })
        rows.append(row)
    return rows


def _class_summary(rows: list[dict], field: str, value: str) -> dict:
    x = [r for r in rows if r.get(field) == value]
    n = len(x)
    supported = sum(bool(r.get("proxy_supported")) for r in x)
    moves = np.array([r["max_abs_raw_5m"] for r in x if r.get("max_abs_raw_5m") is not None], dtype=float)
    return {
        "episodes": n,
        "rate": n / len(rows) if rows else None,
        "raw_0p5_supported": supported,
        "raw_0p5_precision": supported / n if n else None,
        "median_abs_raw_5m": float(np.median(moves)) if len(moves) else None,
        "p90_abs_raw_5m": float(np.quantile(moves, 0.90)) if len(moves) else None,
    }


def _target_summary(rows: list[dict]) -> dict:
    x = [r for r in rows if r["prior_lm_only_uncorroborated"]]
    return {
        "prior_lm_only_uncorroborated": len(x),
        "recovered_freq_strong": sum(r["frequency_class"] == "FREQ_STRONG" for r in x),
        "recovered_freq_confirmed": sum(r["frequency_class"] == "FREQ_CONFIRMED" for r in x),
        "micro_only": sum(r["frequency_class"] == "MICRO_ONLY" for r in x),
        "freq_isolated": sum(r["frequency_class"] == "FREQ_ISOLATED" for r in x),
        "marginal_99": sum(r.get("marginal_class") == "MARGINAL_99" for r in x),
        "marginal_95": sum(r.get("marginal_class") == "MARGINAL_95" for r in x),
        "isolated_even_95": sum(r.get("marginal_class") == "ISOLATED_EVEN_95" for r in x),
    }


def run() -> dict:
    raw1 = load_one_minute_common_support()
    scored: dict[str, pd.DataFrame] = {}
    freq_meta = {}
    for label, spec in FREQ_SPECS.items():
        frame, meta = score_frequency(raw1, label, spec)
        scored[label] = frame
        freq_meta[label] = meta

    seg5, prior_rows, base_meta = authoritative_jan_may()
    rows = classify_multifrequency(seg5, prior_rows, scored)
    target = _target_summary(rows)

    report = {
        "contract": "GOLD_CONTROL_MARKET_SHOCK_V2_2026_MULTIFREQUENCY_LM_AUDIT",
        "status": "AUDIT_EXECUTION_PASS_RESEARCH_ONLY",
        "evidence_class": "HISTORICAL_COMMON_SUPPORT_MULTIFREQUENCY_ROBUSTNESS",
        "prospective_claim": False,
        "scope": {
            "start": AUDIT_START.isoformat(),
            "end_exclusive": AUDIT_END_EXCLUSIVE.isoformat(),
            "one_min_rows": int(len(raw1)),
            "one_min_first_ts": raw1["ts"].min().isoformat(),
            "one_min_last_ts": raw1["ts"].max().isoformat(),
            "interpolation": "NONE",
            "zero_fill": "NONE",
        },
        "frequency_models": freq_meta,
        "authoritative_5m": base_meta,
        "all_lm_episodes": {
            "episodes": len(rows),
            "FREQ_STRONG": _class_summary(rows, "frequency_class", "FREQ_STRONG"),
            "FREQ_CONFIRMED": _class_summary(rows, "frequency_class", "FREQ_CONFIRMED"),
            "MICRO_ONLY": _class_summary(rows, "frequency_class", "MICRO_ONLY"),
            "FREQ_ISOLATED": _class_summary(rows, "frequency_class", "FREQ_ISOLATED"),
            "MARGINAL_99": _class_summary(rows, "marginal_class", "MARGINAL_99"),
            "MARGINAL_95": _class_summary(rows, "marginal_class", "MARGINAL_95"),
            "ISOLATED_EVEN_95": _class_summary(rows, "marginal_class", "ISOLATED_EVEN_95"),
        },
        "prior_unconfirmed_target": target,
        "interpretation_contract": {
            "micro_only_rehabilitates_event": False,
            "isolated_even_95_equals_false_positive": False,
            "fixed_0p5_proxy_primary_ground_truth": False,
            "authoritative_false_positive_rate": "NOT_PROVEN_NO_INDEPENDENT_EVENT_LABEL_SET",
            "model_parameters_changed": False,
            "production_filter_created": False,
            "production_promotion": "BLOCKED_RESEARCH_ONLY",
            "canonical_merge": "NOT_AUTHORIZED",
            "run_2025_authorized_by_this_execution_alone": False,
        },
        "top_prior_unconfirmed_isolated": sorted(
            [r for r in rows if r["prior_lm_only_uncorroborated"] and r["frequency_class"] == "FREQ_ISOLATED"],
            key=lambda r: r.get("max_abs_raw_5m") or 0.0,
            reverse=True,
        )[:30],
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="market_shock_v2_2026_multifrequency_lm_audit.json")
    args = parser.parse_args()
    out = Path(args.output)
    try:
        report = run()
        out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps({
            "status": report["status"],
            "frequency_models": report["frequency_models"],
            "all_lm_episodes": report["all_lm_episodes"],
            "prior_unconfirmed_target": report["prior_unconfirmed_target"],
        }, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        report = {
            "contract": "GOLD_CONTROL_MARKET_SHOCK_V2_2026_MULTIFREQUENCY_LM_AUDIT",
            "status": "BLOCKED_EXECUTION",
            "error": f"{type(exc).__name__}:{exc}",
            "production_promotion": "BLOCKED_RESEARCH_ONLY",
        }
        out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
