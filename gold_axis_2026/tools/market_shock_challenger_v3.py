from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

# V3 inherits only transport, corrected Lee-Mykland constants/critical,
# EVT fitting and BNS ex-post audit from the frozen V2 implementation.
V2_PATH = Path(__file__).with_name("market_shock_challenger_v2.py")
_v2_spec = importlib.util.spec_from_file_location("market_shock_challenger_v2_shared", V2_PATH)
if not _v2_spec or not _v2_spec.loader:
    raise RuntimeError(f"V2_SHARED_MODULE_NOT_FOUND:{V2_PATH}")
v2 = importlib.util.module_from_spec(_v2_spec)
sys.modules[_v2_spec.name] = v2
_v2_spec.loader.exec_module(v2)

SYMBOL = "XAU/USD"
INTERVAL = "5min"
GAP_MAX_SECONDS = 600
REOPEN_WARMUP_BARS = 6
MEDRV_MAX_TERMS = 270
MEDRV_MIN_TERMS = 96
MEDRV_MAX_AGE_HOURS = 72
MEDRV_CONST = math.pi / (6.0 - 4.0 * math.sqrt(3.0) + math.pi)
PERIOD_EXACT_MIN = 20
PERIOD_TOD_MIN = 50
WSD_CUTOFF_CHISQ = 6.635
POT_Q = 0.975
TAIL_P = 0.001
LM_MAIN_ALPHA = 0.001
N_INTRADAY = 288
BNS_ALPHA = 0.001
BNS_MIN_RETURNS = 200
SYNTHETIC_SEED = 20260907
SYNTHETIC_N = 300
SYNTHETIC_SIZES = [0.0025, 0.0050, 0.0075, 0.0100, 0.0150, 0.0200]
COVERAGE_GATE = 0.90

EVTModel = v2.EVTModel
fit_evt = v2.fit_evt
bns_daily_audit = v2.bns_daily_audit
lm_constants = v2.lm_constants
lm_critical = v2.lm_critical


class TwelveClient(v2.TwelveClient):
    def __init__(self) -> None:
        super().__init__()
        self.session.headers.update({"User-Agent": "GoldControl-Market-Shock-Challenger-V3/1.0"})


@dataclass
class PeriodicityModel:
    exact: dict[int, float]
    tod: dict[int, float]
    normalization_rms: float


def _causal_medrv_scale(out: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series]:
    r = out["ret"]
    triple_valid = r.notna() & r.shift(1).notna() & r.shift(2).notna()
    med = pd.concat([r.abs(), r.shift(1).abs(), r.shift(2).abs()], axis=1).median(axis=1)
    term = med.pow(2).where(triple_valid)

    dense = term.dropna()
    roll_mean = dense.rolling(MEDRV_MAX_TERMS, min_periods=MEDRV_MIN_TERMS).mean()
    roll_count = dense.rolling(MEDRV_MAX_TERMS, min_periods=MEDRV_MIN_TERMS).count()
    finite_sample = roll_count / (roll_count - 2.0)
    scale_dense = np.sqrt(MEDRV_CONST * finite_sample * roll_mean)

    at_term = pd.Series(np.nan, index=out.index, dtype=float)
    at_term.loc[scale_dense.index] = scale_dense.to_numpy(float)
    sigma = at_term.ffill().shift(1)

    last_term_ts = pd.Series(pd.NaT, index=out.index, dtype="datetime64[ns, UTC]")
    last_term_ts.loc[term.notna()] = out.loc[term.notna(), "ts"]
    last_term_ts = last_term_ts.ffill().shift(1)
    age_s = (out["ts"] - last_term_ts).dt.total_seconds()
    sigma = sigma.where(age_s.le(MEDRV_MAX_AGE_HOURS * 3600))
    return sigma, age_s, term


def build_returns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy().sort_values("ts").drop_duplicates("ts", keep="last").reset_index(drop=True)
    out["logp"] = np.log(out["close"].astype(float))
    out["gap_s"] = out["ts"].diff().dt.total_seconds()
    out["raw_ret"] = out["logp"].diff()
    valid_gap = out["gap_s"].between(240, GAP_MAX_SECONDS, inclusive="both")
    out["ret"] = out["raw_ret"].where(valid_gap)
    out["gap_reopen_context"] = out["gap_s"].gt(GAP_MAX_SECONDS).fillna(False)
    out["reopen_log_move"] = out["raw_ret"].where(out["gap_reopen_context"])

    reset = ~valid_gap.fillna(False)
    group = reset.cumsum()
    out["bars_since_gap"] = out.groupby(group, sort=False).cumcount()
    out["gap_reopen_warmup"] = out["bars_since_gap"].lt(REOPEN_WARMUP_BARS)
    out["base_scoreable"] = out["ret"].notna() & ~out["gap_reopen_warmup"]

    out["local_sigma"], out["local_scale_age_s"], out["medrv_term"] = _causal_medrv_scale(out)

    six_valid = out["ret"].notna().rolling(6, min_periods=6).sum().eq(6)
    six_span = (out["ts"] - out["ts"].shift(6)).dt.total_seconds()
    out["move30"] = out["logp"] - out["logp"].shift(6)
    valid_30 = six_valid & six_span.between(1500, 2100, inclusive="both") & ~out["gap_reopen_warmup"]
    out.loc[~valid_30, "move30"] = np.nan

    out["slot_day"] = out["ts"].dt.hour * 12 + (out["ts"].dt.minute // 5)
    out["week_slot"] = out["ts"].dt.weekday * 288 + out["slot_day"]
    out["utc_date"] = out["ts"].dt.floor("D")
    ny = out["ts"].dt.tz_convert("America/New_York")
    out["ny17_bucket"] = (ny + pd.Timedelta(hours=7)).dt.date.astype(str)
    return out


def _day_medrv_scale(g: pd.DataFrame) -> float:
    r = g["ret"]
    valid = r.notna() & r.shift(1).notna() & r.shift(2).notna()
    med = pd.concat([r.abs(), r.shift(1).abs(), r.shift(2).abs()], axis=1).median(axis=1)
    x = med.pow(2).where(valid).dropna().to_numpy(float)
    n = len(x)
    if n < 20:
        return float("nan")
    variance = MEDRV_CONST * (n / max(n - 2, 1)) * float(np.mean(x))
    return math.sqrt(variance) if math.isfinite(variance) and variance > 0 else float("nan")


def _short_half_scale(x: np.ndarray) -> float:
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 8:
        return float("nan")
    sx = np.sort(x)
    h = n // 2 + 1
    widths = sx[h - 1:] - sx[: n - h + 1]
    if not len(widths):
        return float("nan")
    sh = 0.741 * float(np.min(widths))
    if sh <= 0 or not math.isfinite(sh):
        med = float(np.median(x))
        sh = 1.4826 * float(np.median(np.abs(x - med)))
    return sh if math.isfinite(sh) and sh > 0 else float("nan")


def _wsd(x: np.ndarray, min_n: int) -> float:
    x = x[np.isfinite(x)]
    if len(x) < min_n:
        return float("nan")
    sh = _short_half_scale(x)
    if not math.isfinite(sh) or sh <= 0:
        return float("nan")
    keep = (x / sh) ** 2 <= WSD_CUTOFF_CHISQ
    if int(keep.sum()) < max(10, min_n // 2):
        return float("nan")
    val = math.sqrt(1.081 * float(np.mean(x[keep] ** 2)))
    return val if math.isfinite(val) and val > 0 else float("nan")


def fit_periodicity(train: pd.DataFrame) -> PeriodicityModel:
    day_scales = train.groupby("utc_date", sort=False).apply(_day_medrv_scale, include_groups=False)
    tmp = train[["utc_date", "week_slot", "slot_day", "ret"]].copy()
    tmp["day_scale"] = tmp["utc_date"].map(day_scales)
    tmp["rbar"] = tmp["ret"] / tmp["day_scale"]

    exact_raw: dict[int, float] = {}
    for slot, group in tmp.groupby("week_slot"):
        val = _wsd(group["rbar"].dropna().to_numpy(float), PERIOD_EXACT_MIN)
        if math.isfinite(val) and val > 0:
            exact_raw[int(slot)] = val

    tod_raw: dict[int, float] = {}
    for slot, group in tmp.groupby("slot_day"):
        val = _wsd(group["rbar"].dropna().to_numpy(float), PERIOD_TOD_MIN)
        if math.isfinite(val) and val > 0:
            tod_raw[int(slot)] = val

    if len(exact_raw) < 500:
        raise RuntimeError(f"PERIODICITY_EXACT_TOO_SPARSE:{len(exact_raw)}")
    if len(tod_raw) < 200:
        raise RuntimeError(f"PERIODICITY_TOD_TOO_SPARSE:{len(tod_raw)}")
    rms = math.sqrt(float(np.mean(np.square(list(exact_raw.values())))))
    if not math.isfinite(rms) or rms <= 0:
        raise RuntimeError("PERIODICITY_NORMALIZATION_INVALID")
    return PeriodicityModel(
        exact={k: v / rms for k, v in exact_raw.items()},
        tod={k: v / rms for k, v in tod_raw.items()},
        normalization_rms=rms,
    )


def add_scores(frame: pd.DataFrame, periodicity: PeriodicityModel) -> pd.DataFrame:
    out = frame.copy()
    exact = out["week_slot"].map(periodicity.exact)
    fallback = out["slot_day"].map(periodicity.tod)
    out["period_factor"] = exact.where(exact.notna(), fallback)
    out["period_source"] = np.select(
        [exact.notna(), exact.isna() & fallback.notna()],
        ["EXACT_WEEK_SLOT", "TOD_FALLBACK"],
        default="MISSING",
    )
    denom = out["local_sigma"] * out["period_factor"]
    valid_denom = denom.replace([np.inf, -np.inf], np.nan).gt(0)
    out["score5"] = (out["ret"].abs() / denom).where(out["base_scoreable"] & valid_denom)
    out["score30"] = (out["move30"].abs() / (math.sqrt(6.0) * denom)).where(
        out["move30"].notna() & out["base_scoreable"] & valid_denom
    )
    return out


def _episode_count(sig: pd.Series, ts: pd.Series) -> int:
    mask = sig.fillna(False).to_numpy(bool)
    times = pd.to_datetime(ts, utc=True)
    count = 0
    prev_signal_i: int | None = None
    for i, on in enumerate(mask):
        if not on:
            continue
        if prev_signal_i is None or i != prev_signal_i + 1 or (times.iloc[i] - times.iloc[prev_signal_i]).total_seconds() > 600:
            count += 1
        prev_signal_i = i
    return count


def _metrics(seg: pd.DataFrame, signal_col: str, eligible_col: str) -> dict:
    eligible = seg[eligible_col].fillna(False).astype(bool)
    signal = seg[signal_col].fillna(False).astype(bool) & eligible
    n = int(eligible.sum())
    return {
        "eligible_bars": n,
        "signal_bars": int(signal.sum()),
        "signal_rate": float(signal.sum() / n) if n else None,
        "episodes": _episode_count(signal, seg["ts"]),
    }


def score_segment(data: pd.DataFrame, year: int, periodicity: PeriodicityModel, evt30: EVTModel) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    seg = add_scores(data[data["ts"].dt.year.eq(year)].copy(), periodicity)
    if year == 2026:
        seg = seg[seg["ts"] < pd.Timestamp("2026-09-01", tz="UTC")].copy()

    seg["lm_eligible"] = seg["score5"].replace([np.inf, -np.inf], np.nan).notna()
    seg["evt30_eligible"] = seg["score30"].replace([np.inf, -np.inf], np.nan).notna()
    seg["lm_sig"] = seg["lm_eligible"] & (seg["score5"] > lm_critical(LM_MAIN_ALPHA))
    seg["evt30_sig"] = seg["evt30_eligible"] & (seg["score30"] >= evt30.critical_score)
    seg["shock_eligible"] = seg["lm_eligible"] | seg["evt30_eligible"]
    seg["shock_sig"] = seg["lm_sig"] | seg["evt30_sig"]
    seg["compound_sig"] = seg["lm_sig"] & seg["evt30_sig"]
    seg["shock_state"] = np.select(
        [seg["compound_sig"], seg["lm_sig"], seg["evt30_sig"]],
        ["COMPOUND_SHOCK", "INSTANT_JUMP", "FAST_MOVE"],
        default="OFF",
    )
    seg["shock_direction"] = np.where(
        seg["shock_sig"],
        np.where(seg["evt30_sig"], np.sign(seg["move30"]), np.sign(seg["ret"])),
        0,
    )

    bns = bns_daily_audit(seg)
    bns_map = bns.set_index("ny17_bucket")["bns_sig_999"].to_dict() if not bns.empty else {}
    seg["bns_day_sig_expost"] = seg["ny17_bucket"].map(bns_map).fillna(False).astype(bool)

    shock = seg["shock_sig"]
    eligible = seg["shock_eligible"]
    base = seg["base_scoreable"].fillna(False).astype(bool)
    coverage = float(eligible.sum() / base.sum()) if int(base.sum()) else None
    raw_coverage = float(eligible.sum() / len(seg)) if len(seg) else None
    period_missing = base & seg["period_factor"].isna()

    report = {
        "year": year,
        "bars": int(len(seg)),
        "valid_return_bars": int(seg["ret"].notna().sum()),
        "base_scoreable_outside_warmup": int(base.sum()),
        "adjusted_scoring_coverage": coverage,
        "raw_scoring_coverage": raw_coverage,
        "reopen_gap_context_rows": int(seg["gap_reopen_context"].sum()),
        "gap_reopen_warmup_rows": int(seg["gap_reopen_warmup"].sum()),
        "signals_during_gap_reopen_warmup": int((seg["gap_reopen_warmup"] & shock).sum()),
        "periodicity": {
            "exact_rows": int((base & seg["period_source"].eq("EXACT_WEEK_SLOT")).sum()),
            "tod_fallback_rows": int((base & seg["period_source"].eq("TOD_FALLBACK")).sum()),
            "missing_rows": int(period_missing.sum()),
        },
        "local_scale": {
            "missing_on_base_rows": int((base & seg["local_sigma"].isna()).sum()),
            "stale_gt_72h_rows": int((base & seg["local_scale_age_s"].gt(MEDRV_MAX_AGE_HOURS * 3600)).sum()),
        },
        "lm": _metrics(seg, "lm_sig", "lm_eligible"),
        "evt30": _metrics(seg, "evt30_sig", "evt30_eligible"),
        "market_shock_v3": _metrics(seg, "shock_sig", "shock_eligible"),
        "compound_bars": int(seg["compound_sig"].sum()),
        "instant_jump_only_bars": int((seg["lm_sig"] & ~seg["evt30_sig"]).sum()),
        "fast_move_only_bars": int((seg["evt30_sig"] & ~seg["lm_sig"]).sum()),
        "up_shock_bars": int((shock & (seg["shock_direction"] > 0)).sum()),
        "down_shock_bars": int((shock & (seg["shock_direction"] < 0)).sum()),
        "median_abs_5m_return_shock": float(seg.loc[shock, "ret"].abs().median()) if shock.any() else None,
        "median_abs_30m_move_shock": float(seg.loc[shock, "move30"].abs().median()) if shock.any() else None,
        "bns": {
            "eligible_buckets": int(len(bns)),
            "significant_buckets_999": int(bns["bns_sig_999"].sum()) if not bns.empty else 0,
            "shock_bars_on_bns_significant_bucket": int((shock & seg["bns_day_sig_expost"]).sum()),
            "role": "EX_POST_ROBUSTNESS_ONLY_NOT_LIVE_VOTE",
        },
    }
    return report, seg, bns


def synthetic_injection(seg: pd.DataFrame, evt30: EVTModel, year: int) -> dict:
    eligible = seg[
        seg["shock_eligible"]
        & seg["ret"].notna()
        & seg["move30"].notna()
        & seg["local_sigma"].gt(0)
        & seg["period_factor"].gt(0)
    ].copy()
    if len(eligible) < SYNTHETIC_N:
        raise RuntimeError(f"SYNTHETIC_ELIGIBLE_TOO_SMALL:{year}:{len(eligible)}")
    rng = np.random.default_rng(SYNTHETIC_SEED + year)
    sample = eligible.loc[rng.choice(eligible.index.to_numpy(), size=SYNTHETIC_N, replace=False)].copy()
    denom = sample["local_sigma"].to_numpy(float) * sample["period_factor"].to_numpy(float)
    base_r = sample["ret"].to_numpy(float)
    base_m30 = sample["move30"].to_numpy(float)
    lmcrit = lm_critical(LM_MAIN_ALPHA)

    base_lm = np.abs(base_r) / denom > lmcrit
    base_evt30 = np.abs(base_m30) / (math.sqrt(6.0) * denom) >= evt30.critical_score
    base_shock = base_lm | base_evt30

    rows = []
    for size in SYNTHETIC_SIZES:
        for sign in (-1, 1):
            jump = math.log(1.0 + size) if sign > 0 else math.log(1.0 - size)
            rj = base_r + jump
            m30j = base_m30 + jump
            lm = np.abs(rj) / denom > lmcrit
            e30 = np.abs(m30j) / (math.sqrt(6.0) * denom) >= evt30.critical_score
            shock = lm | e30
            rows.append({
                "year": year,
                "jump_abs_pct": size * 100.0,
                "sign": "UP" if sign > 0 else "DOWN",
                "n": SYNTHETIC_N,
                "lm_power": float(lm.mean()),
                "evt30_power": float(e30.mean()),
                "market_shock_v3_power": float(shock.mean()),
            })

    by_size = {}
    for size in SYNTHETIC_SIZES:
        vals = [r["market_shock_v3_power"] for r in rows if math.isclose(r["jump_abs_pct"], size * 100.0)]
        by_size[str(size)] = float(np.mean(vals))
    powers = [by_size[str(s)] for s in SYNTHETIC_SIZES]
    return {
        "year": year,
        "sample_n": SYNTHETIC_N,
        "no_injection_market_shock_rate": float(base_shock.mean()),
        "power_rows": rows,
        "market_shock_v3_power_by_abs_size": by_size,
        "monotone_with_2pp_tolerance": bool(all(powers[i + 1] + 0.02 >= powers[i] for i in range(len(powers) - 1))),
    }


def top_events(seg: pd.DataFrame, year: int, n: int = 20) -> list[dict]:
    x = seg[seg["shock_sig"]].copy()
    if x.empty:
        return []
    x["rank_score"] = x[["score5", "score30"]].max(axis=1, skipna=True)
    x = x.sort_values("rank_score", ascending=False).head(n)
    return [{
        "year": year,
        "ts": pd.Timestamp(r["ts"]).isoformat(),
        "state": str(r["shock_state"]),
        "direction": "UP" if r["shock_direction"] > 0 else "DOWN",
        "return_5m_pct": float(r["ret"] * 100.0) if pd.notna(r["ret"]) else None,
        "move_30m_pct": float(r["move30"] * 100.0) if pd.notna(r["move30"]) else None,
        "score5": float(r["score5"]) if pd.notna(r["score5"]) else None,
        "score30": float(r["score30"]) if pd.notna(r["score30"]) else None,
        "period_source": str(r["period_source"]),
        "bns_day_sig_expost": bool(r["bns_day_sig_expost"]),
    } for _, r in x.iterrows()]


def top_reopen_contexts(seg: pd.DataFrame, year: int, n: int = 10) -> list[dict]:
    x = seg[seg["gap_reopen_context"] & seg["reopen_log_move"].notna()].copy()
    if x.empty:
        return []
    x = x.assign(abs_move=x["reopen_log_move"].abs()).sort_values("abs_move", ascending=False).head(n)
    return [{
        "year": year,
        "ts": pd.Timestamp(r["ts"]).isoformat(),
        "preceding_gap_minutes": float(r["gap_s"] / 60.0),
        "reopen_move_pct_log": float(r["reopen_log_move"] * 100.0),
        "role": "REOPEN_GAP_CONTEXT_NOT_INTRADAY_SHOCK_VOTE",
    } for _, r in x.iterrows()]


def _gate_status(segments: list[dict], synths: list[dict]) -> dict:
    p2 = [s["market_shock_v3_power_by_abs_size"][str(0.02)] for s in synths]
    p15 = [s["market_shock_v3_power_by_abs_size"][str(0.015)] for s in synths]
    rates = [s["market_shock_v3"]["signal_rate"] for s in segments]
    null_rates = [s["no_injection_market_shock_rate"] for s in synths]
    coverages = [s["adjusted_scoring_coverage"] for s in segments]
    warmup_signals = [s["signals_during_gap_reopen_warmup"] for s in segments]
    checks = {
        "POWER_2PCT_EVERY_SEGMENT_GTE_095": all(x >= 0.95 for x in p2),
        "POWER_1P5PCT_EVERY_SEGMENT_GTE_080": all(x >= 0.80 for x in p15),
        "POWER_MONOTONE_WITH_2PP_TOLERANCE": all(s["monotone_with_2pp_tolerance"] for s in synths),
        "HISTORICAL_SHOCK_BAR_RATE_EVERY_SEGMENT_LT_001": all(x is not None and x < 0.01 for x in rates),
        "NO_INJECTION_SAMPLE_RATE_EVERY_SEGMENT_LT_001": all(x < 0.01 for x in null_rates),
        "ADJUSTED_SCORING_COVERAGE_EVERY_SEGMENT_GTE_090": all(x is not None and x >= COVERAGE_GATE for x in coverages),
        "ZERO_INTRADAY_SIGNALS_DURING_GAP_REOPEN_WARMUP": all(x == 0 for x in warmup_signals),
    }
    return {
        "checks": checks,
        "research_numeric_gates": "PASS" if all(checks.values()) else "FAIL",
        "min_2pct_power": float(min(p2)),
        "min_1p5pct_power": float(min(p15)),
        "max_historical_shock_bar_rate": float(max(rates)),
        "max_no_injection_sample_rate": float(max(null_rates)),
        "min_adjusted_scoring_coverage": float(min(coverages)),
        "warmup_signal_count_total": int(sum(warmup_signals)),
        "FALSE_POSITIVE_RATE_REAL_HISTORY": "NOT_PROVEN_NO_AUTHORITATIVE_EVENT_LABEL_SET",
        "TWELVE_SESSION_CALENDAR": "NOT_PROVEN_OBSERVED_GAP_SEMANTICS_ONLY",
        "PRODUCTION_PROMOTION": "BLOCKED_RESEARCH_CHALLENGER_ONLY",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2020-04-06 00:00:00")
    parser.add_argument("--end", default="2026-08-31 23:59:59")
    parser.add_argument("--output", default="market_shock_challenger_v3_report.json")
    args = parser.parse_args()

    report: dict = {
        "contract": "GOLD_CONTROL_MARKET_SHOCK_CHALLENGER_V3",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "code_sha": os.environ.get("GOLD_CODE_SHA", "NOT_PROVIDED"),
        "provider": "Twelve Data",
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "evidence_class": "HISTORICAL_RESEARCH_RETRIEVAL",
        "prospective_claim": False,
        "database_write": "NONE",
        "raw_market_values_logged": False,
        "raw_market_values_artifacted": False,
        "monthly_forecast_anchor_used": False,
        "v1_status": "REJECTED_PRIMARY_FORMULA_AUDIT",
        "v2_status": "REJECT_OR_REVISE_CHALLENGER_V2",
        "session_semantics": "OBSERVED_GAP_REOPEN_CONTEXT_ONLY; EXACT_TWELVE_SESSION_CALENDAR_NOT_PROVEN",
        "frozen_parameters": {
            "gap_max_seconds": GAP_MAX_SECONDS,
            "reopen_warmup_bars": REOPEN_WARMUP_BARS,
            "medrv_max_terms": MEDRV_MAX_TERMS,
            "medrv_min_terms": MEDRV_MIN_TERMS,
            "medrv_max_age_hours": MEDRV_MAX_AGE_HOURS,
            "medrv_const": MEDRV_CONST,
            "period_exact_min": PERIOD_EXACT_MIN,
            "period_tod_min": PERIOD_TOD_MIN,
            "lm_main_alpha": LM_MAIN_ALPHA,
            "lm_n_intraday": N_INTRADAY,
            "pot_quantile": POT_Q,
            "evt_tail_p": TAIL_P,
            "coverage_gate": COVERAGE_GATE,
            "shock_rule": "LM_JUMP_5M_V3_OR_EVT_FAST_MOVE_30M_V3",
            "synthetic_seed": SYNTHETIC_SEED,
            "synthetic_n": SYNTHETIC_N,
            "synthetic_sizes": SYNTHETIC_SIZES,
        },
    }
    output = Path(args.output)
    try:
        client = TwelveClient()
        report["provider_earliest_timestamp_5m"] = client.earliest()
        start = pd.Timestamp(args.start, tz="UTC")
        end = pd.Timestamp(args.end, tz="UTC")
        data = build_returns(client.history(start, end))
        report["history"] = {
            "rows": int(len(data)),
            "first_ts": data["ts"].min().isoformat(),
            "last_ts": data["ts"].max().isoformat(),
            "valid_returns": int(data["ret"].notna().sum()),
            "gaps_gt_10min": int(data["gap_reopen_context"].sum()),
            "medrv_terms": int(data["medrv_term"].notna().sum()),
        }
        cn, sn = lm_constants()
        report["lm_primary_formula_check"] = {
            "Cn": cn,
            "Sn": sn,
            "critical_999": lm_critical(0.001),
            "sn_formula": "1/(c*sqrt(2*log(n)))",
        }

        segments, synths, fits, events, reopens, bns_summary = [], [], [], [], [], []
        for year in (2024, 2025, 2026):
            cutoff = pd.Timestamp(f"{year}-01-01", tz="UTC")
            train = data[data["ts"] < cutoff].copy()
            if len(train) < 100000:
                raise RuntimeError(f"TRAIN_TOO_SMALL:{year}:{len(train)}")
            periodicity = fit_periodicity(train)
            train_scored = add_scores(train, periodicity)
            evt30 = fit_evt(train_scored["score30"])
            segment_report, seg, bns = score_segment(data, year, periodicity, evt30)
            synth = synthetic_injection(seg, evt30, year)
            segments.append(segment_report)
            synths.append(synth)
            events.extend(top_events(seg, year))
            reopens.extend(top_reopen_contexts(seg, year))
            fits.append({
                "year": year,
                "train_end_exclusive": cutoff.isoformat(),
                "train_rows": int(len(train)),
                "periodicity_exact_slots": int(len(periodicity.exact)),
                "periodicity_tod_slots": int(len(periodicity.tod)),
                "periodicity_normalization_rms": periodicity.normalization_rms,
                "evt30": asdict(evt30),
            })
            bns_summary.append({
                "year": year,
                "eligible_buckets": int(len(bns)),
                "significant_buckets_999": int(bns["bns_sig_999"].sum()) if not bns.empty else 0,
            })
            print(json.dumps({
                "segment": year,
                "coverage": segment_report["adjusted_scoring_coverage"],
                "shock_rate": segment_report["market_shock_v3"]["signal_rate"],
                "power_1p5": synth["market_shock_v3_power_by_abs_size"][str(0.015)],
                "power_2p0": synth["market_shock_v3_power_by_abs_size"][str(0.02)],
            }, sort_keys=True))

        report["fits"] = fits
        report["segments"] = segments
        report["synthetic_injection"] = synths
        report["bns_expost_summary"] = bns_summary
        report["top_shock_events"] = sorted(events, key=lambda x: max(x["score5"] or 0.0, x["score30"] or 0.0), reverse=True)[:40]
        report["top_reopen_contexts"] = sorted(reopens, key=lambda x: abs(x["reopen_move_pct_log"]), reverse=True)[:30]
        report["gates"] = _gate_status(segments, synths)
        report["status"] = "RESEARCH_GATES_PASS_NOT_PROMOTED" if report["gates"]["research_numeric_gates"] == "PASS" else "REJECT_OR_REVISE_CHALLENGER_V3"
        output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["status"] == "RESEARCH_GATES_PASS_NOT_PROMOTED" else 2
    except Exception as exc:
        report["status"] = "BLOCKED_EXECUTION"
        report["error"] = f"{type(exc).__name__}:{exc}"
        output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
