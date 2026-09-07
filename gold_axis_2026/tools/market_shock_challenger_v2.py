from __future__ import annotations

import argparse
import json
import math
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from scipy.special import gamma
from scipy.stats import genpareto, norm

SYMBOL = "XAU/USD"
INTERVAL = "5min"
TIME_SERIES_URL = "https://api.twelvedata.com/time_series"
EARLIEST_URL = "https://api.twelvedata.com/earliest_timestamp"
MAX_OUTPUT = 5000
MIN_REQUEST_INTERVAL_SECONDS = float(os.environ.get("TWELVE_MIN_REQUEST_INTERVAL_SECONDS", "9.0"))
K_LM = 270
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


@dataclass
class EVTModel:
    threshold_u: float
    shape: float
    scale: float
    critical_score: float
    n_train: int
    n_exceed: int


class TwelveClient:
    def __init__(self) -> None:
        key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
        if not key:
            raise RuntimeError("TWELVE_DATA_API_KEY is not set")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"apikey {key}",
            "User-Agent": "GoldControl-Market-Shock-Challenger-V2/1.0",
        })
        self.last_request = 0.0

    def _pace(self) -> None:
        wait = MIN_REQUEST_INTERVAL_SECONDS - (time.monotonic() - self.last_request)
        if wait > 0:
            time.sleep(wait)

    def get_json(self, url: str, params: dict) -> dict:
        waits = [0, 10, 20, 40, 65]
        last_error: Exception | None = None
        for extra in waits:
            if extra:
                time.sleep(extra)
            self._pace()
            try:
                response = self.session.get(url, params=params, timeout=(8, 75))
                self.last_request = time.monotonic()
                payload = response.json()
                if payload.get("status") == "error":
                    code = str(payload.get("code"))
                    msg = payload.get("message")
                    if code in {"429", "500", "502", "503", "504"}:
                        last_error = RuntimeError(f"TWELVE_RETRYABLE:{code}:{msg}")
                        continue
                    raise RuntimeError(f"TWELVE_API_ERROR:{code}:{msg}")
                response.raise_for_status()
                return payload
            except (requests.RequestException, ValueError, RuntimeError) as exc:
                last_error = exc
        raise RuntimeError(f"TWELVE_REQUEST_FAILED:{last_error}")

    def earliest(self) -> str | None:
        payload = self.get_json(EARLIEST_URL, {"symbol": SYMBOL, "interval": INTERVAL})
        for key in ("datetime", "timestamp", "earliest_timestamp"):
            if payload.get(key) is not None:
                return str(payload[key])
        data = payload.get("data")
        if isinstance(data, dict):
            for key in ("datetime", "timestamp", "earliest_timestamp"):
                if data.get(key) is not None:
                    return str(data[key])
        return None

    def history(self, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
        rows: dict[pd.Timestamp, float] = {}
        cursor_end = end
        previous_oldest: pd.Timestamp | None = None
        page = 0
        while cursor_end >= start:
            payload = self.get_json(TIME_SERIES_URL, {
                "symbol": SYMBOL,
                "interval": INTERVAL,
                "start_date": start.strftime("%Y-%m-%d %H:%M:%S"),
                "end_date": cursor_end.strftime("%Y-%m-%d %H:%M:%S"),
                "timezone": "UTC",
                "outputsize": MAX_OUTPUT,
                "order": "DESC",
                "format": "JSON",
            })
            meta = payload.get("meta") or {}
            if meta.get("symbol") not in (None, SYMBOL):
                raise RuntimeError(f"TWELVE_SYMBOL_MISMATCH:{meta.get('symbol')}")
            if meta.get("interval") not in (None, INTERVAL):
                raise RuntimeError(f"TWELVE_INTERVAL_MISMATCH:{meta.get('interval')}")
            values = payload.get("values") or []
            if not values:
                break
            page_ts: list[pd.Timestamp] = []
            for item in values:
                ts = pd.to_datetime(item.get("datetime"), utc=True, errors="coerce")
                close = pd.to_numeric(item.get("close"), errors="coerce")
                if pd.isna(ts) or pd.isna(close):
                    continue
                ts = pd.Timestamp(ts).floor("5min")
                if ts < start or ts > end:
                    continue
                value = float(close)
                if value <= 0:
                    raise RuntimeError(f"TWELVE_INVALID_CLOSE:{ts.isoformat()}")
                if ts in rows and not math.isclose(rows[ts], value, rel_tol=0.0, abs_tol=1e-12):
                    raise RuntimeError(f"TWELVE_DUPLICATE_CONFLICT:{ts.isoformat()}")
                rows[ts] = value
                page_ts.append(ts)
            if not page_ts:
                break
            oldest, newest = min(page_ts), max(page_ts)
            page += 1
            print(json.dumps({
                "fetch_page": page,
                "rows": len(page_ts),
                "oldest": oldest.isoformat(),
                "newest": newest.isoformat(),
                "unique_total": len(rows),
            }, sort_keys=True))
            if oldest <= start:
                break
            if previous_oldest is not None and oldest >= previous_oldest:
                raise RuntimeError(f"TWELVE_PAGINATION_NOT_ADVANCING:{oldest.isoformat()}")
            previous_oldest = oldest
            cursor_end = oldest - pd.Timedelta(minutes=5)
        if not rows:
            raise RuntimeError("NO_TWELVE_HISTORY_ROWS")
        return (
            pd.DataFrame({"ts": list(rows.keys()), "close": list(rows.values())})
            .sort_values("ts")
            .drop_duplicates("ts", keep="last")
            .reset_index(drop=True)
        )


def build_returns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["logp"] = np.log(out["close"].astype(float))
    out["gap_s"] = out["ts"].diff().dt.total_seconds()
    out["ret"] = out["logp"].diff()
    valid_gap = out["gap_s"].between(240, 600, inclusive="both")
    out.loc[~valid_gap, "ret"] = np.nan
    out["slot"] = out["ts"].dt.weekday * 288 + out["ts"].dt.hour * 12 + (out["ts"].dt.minute // 5)
    out["utc_date"] = out["ts"].dt.floor("D")

    pair = out["ret"].abs() * out["ret"].shift(1).abs()
    out["local_var"] = pair.rolling(K_LM - 2, min_periods=K_LM - 2).mean().shift(1)
    out["local_sigma"] = np.sqrt(out["local_var"])

    six_valid = out["ret"].notna().rolling(6, min_periods=6).sum().eq(6)
    six_span = (out["ts"] - out["ts"].shift(6)).dt.total_seconds()
    out["move30"] = out["logp"] - out["logp"].shift(6)
    out.loc[~(six_valid & six_span.between(1500, 2100, inclusive="both")), "move30"] = np.nan

    ny = out["ts"].dt.tz_convert("America/New_York")
    out["ny17_bucket"] = (ny + pd.Timedelta(hours=7)).dt.date.astype(str)
    return out


def _day_bpv_scale(g: pd.DataFrame) -> float:
    r = g["ret"]
    bp = r.abs() * r.shift(1).abs()
    m = float(bp.mean(skipna=True))
    return math.sqrt(m) if math.isfinite(m) and m > 0 else float("nan")


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


def fit_periodicity(train: pd.DataFrame) -> dict[int, float]:
    day_scales = train.groupby("utc_date", sort=False).apply(_day_bpv_scale, include_groups=False)
    tmp = train[["utc_date", "slot", "ret"]].copy()
    tmp["day_scale"] = tmp["utc_date"].map(day_scales)
    tmp["rbar"] = tmp["ret"] / tmp["day_scale"]
    raw: dict[int, float] = {}
    for slot, group in tmp.groupby("slot"):
        x = group["rbar"].dropna().to_numpy(float)
        if len(x) < 20:
            continue
        sh = _short_half_scale(x)
        if not math.isfinite(sh) or sh <= 0:
            continue
        keep = (x / sh) ** 2 <= WSD_CUTOFF_CHISQ
        if int(keep.sum()) < 10:
            continue
        wsd = math.sqrt(1.081 * float(np.mean(x[keep] ** 2)))
        if math.isfinite(wsd) and wsd > 0:
            raw[int(slot)] = wsd
    if len(raw) < 500:
        raise RuntimeError(f"PERIODICITY_TOO_SPARSE:{len(raw)}")
    rms = math.sqrt(float(np.mean(np.square(list(raw.values())))))
    if not math.isfinite(rms) or rms <= 0:
        raise RuntimeError("PERIODICITY_NORMALIZATION_INVALID")
    return {k: v / rms for k, v in raw.items()}


def lm_constants(n: int = N_INTRADAY) -> tuple[float, float]:
    if n < 2:
        raise ValueError(n)
    c = math.sqrt(2.0 / math.pi)
    root = math.sqrt(2.0 * math.log(n))
    cn = root / c - (math.log(math.pi) + math.log(math.log(n))) / (2.0 * c * root)
    # Primary Lee-Mykland Eq. (13): S_n = 1 / [c * sqrt(2 log n)].
    sn = 1.0 / (c * root)
    return cn, sn


def lm_critical(alpha: float, n: int = N_INTRADAY) -> float:
    if not 0 < alpha < 1:
        raise ValueError(alpha)
    cn, sn = lm_constants(n)
    beta = -math.log(-math.log(1.0 - alpha))
    return cn + sn * beta


def add_scores(frame: pd.DataFrame, periodicity: dict[int, float]) -> pd.DataFrame:
    out = frame.copy()
    out["period_factor"] = out["slot"].map(periodicity)
    denom = out["local_sigma"] * out["period_factor"]
    out["score5"] = out["ret"].abs() / denom
    out["score30"] = out["move30"].abs() / (math.sqrt(6.0) * denom)
    return out


def fit_evt(x: pd.Series) -> EVTModel:
    arr = x.replace([np.inf, -np.inf], np.nan).dropna().to_numpy(float)
    if len(arr) < 5000:
        raise RuntimeError(f"EVT_TRAIN_TOO_SMALL:{len(arr)}")
    u = float(np.quantile(arr, POT_Q))
    excess = arr[arr > u] - u
    if len(excess) < 100:
        raise RuntimeError(f"EVT_EXCEED_TOO_SMALL:{len(excess)}")
    shape, _, scale = genpareto.fit(excess, floc=0.0)
    if not (math.isfinite(shape) and math.isfinite(scale) and scale > 0):
        raise RuntimeError(f"EVT_FIT_INVALID:{shape}:{scale}")
    cond_cdf = 1.0 - TAIL_P / (1.0 - POT_Q)
    critical = u + float(genpareto.ppf(cond_cdf, shape, loc=0.0, scale=scale))
    if not math.isfinite(critical) or critical <= u:
        raise RuntimeError(f"EVT_CRITICAL_INVALID:{critical}")
    return EVTModel(u, float(shape), float(scale), critical, len(arr), len(excess))


def bns_daily_audit(frame: pd.DataFrame) -> pd.DataFrame:
    mu1 = math.sqrt(2.0 / math.pi)
    mu43 = (2.0 ** (2.0 / 3.0)) * float(gamma(7.0 / 6.0)) / math.sqrt(math.pi)
    variance_const = mu1 ** -4 + 2.0 * mu1 ** -2 - 5.0
    zcrit = float(norm.ppf(1.0 - BNS_ALPHA))
    rows = []
    for bucket, g in frame.groupby("ny17_bucket", sort=True):
        g = g.sort_values("ts")
        r = g["ret"]
        valid_n = int(r.notna().sum())
        if valid_n < BNS_MIN_RETURNS:
            continue
        rv = float((r ** 2).sum(skipna=True))
        bp_prod = r.abs() * r.shift(1).abs()
        bpv = float(mu1 ** -2 * bp_prod.sum(skipna=True))
        tq_prod = (r.abs() ** (4.0 / 3.0)) * (r.shift(1).abs() ** (4.0 / 3.0)) * (r.shift(2).abs() ** (4.0 / 3.0))
        tq = float(valid_n * mu43 ** -3 * tq_prod.sum(skipna=True))
        if not (rv > 0 and bpv > 0 and tq >= 0 and math.isfinite(tq)):
            continue
        denom = math.sqrt(variance_const * max(1.0, tq / (bpv * bpv)))
        z = math.sqrt(valid_n) * ((rv - bpv) / rv) / denom if denom > 0 else float("nan")
        rows.append({
            "ny17_bucket": bucket,
            "valid_returns": valid_n,
            "rv": rv,
            "bpv": bpv,
            "jump_variation_share": max(rv - bpv, 0.0) / rv,
            "bns_z": z,
            "bns_sig_999": bool(math.isfinite(z) and z > zcrit),
        })
    return pd.DataFrame(rows)


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


def score_segment(data: pd.DataFrame, year: int, periodicity: dict[int, float], evt30: EVTModel) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
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
    report = {
        "year": year,
        "bars": int(len(seg)),
        "lm": _metrics(seg, "lm_sig", "lm_eligible"),
        "evt30": _metrics(seg, "evt30_sig", "evt30_eligible"),
        "market_shock_v2": _metrics(seg, "shock_sig", "shock_eligible"),
        "compound_bars": int(seg["compound_sig"].sum()),
        "instant_jump_only_bars": int((seg["lm_sig"] & ~seg["evt30_sig"]).sum()),
        "fast_move_only_bars": int((seg["evt30_sig"] & ~seg["lm_sig"]).sum()),
        "up_shock_bars": int((shock & (seg["shock_direction"] > 0)).sum()),
        "down_shock_bars": int((shock & (seg["shock_direction"] < 0)).sum()),
        "median_abs_5m_return_shock": float(seg.loc[shock, "ret"].abs().median()) if shock.any() else None,
        "median_abs_30m_move_shock": float(seg.loc[shock, "move30"].abs().median()) if shock.any() else None,
        "median_abs_5m_return_nonshock": float(seg.loc[eligible & ~shock, "ret"].abs().median()),
        "bns": {
            "eligible_buckets": int(len(bns)),
            "significant_buckets_999": int(bns["bns_sig_999"].sum()) if not bns.empty else 0,
            "shock_bars_on_bns_significant_bucket": int((shock & seg["bns_day_sig_expost"]).sum()),
            "shock_bars_with_scored_bns_bucket": int((shock & seg["ny17_bucket"].isin(set(bns["ny17_bucket"]) if not bns.empty else set())).sum()),
            "role": "EX_POST_ROBUSTNESS_ONLY_NOT_LIVE_VOTE",
        },
    }
    return report, seg, bns


def synthetic_injection(seg: pd.DataFrame, evt30: EVTModel, year: int) -> dict:
    eligible = seg[
        seg["ret"].notna()
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
                "market_shock_v2_power": float(shock.mean()),
            })

    by_size = {}
    for size in SYNTHETIC_SIZES:
        vals = [r["market_shock_v2_power"] for r in rows if math.isclose(r["jump_abs_pct"], size * 100.0)]
        by_size[str(size)] = float(np.mean(vals))
    powers = [by_size[str(s)] for s in SYNTHETIC_SIZES]
    monotone = all(powers[i + 1] + 0.02 >= powers[i] for i in range(len(powers) - 1))
    return {
        "year": year,
        "sample_n": SYNTHETIC_N,
        "no_injection_market_shock_rate": float(base_shock.mean()),
        "power_rows": rows,
        "market_shock_v2_power_by_abs_size": by_size,
        "monotone_with_2pp_tolerance": bool(monotone),
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
        "bns_day_sig_expost": bool(r["bns_day_sig_expost"]),
    } for _, r in x.iterrows()]


def _gate_status(segments: list[dict], synths: list[dict]) -> dict:
    p2 = [s["market_shock_v2_power_by_abs_size"][str(0.02)] for s in synths]
    p15 = [s["market_shock_v2_power_by_abs_size"][str(0.015)] for s in synths]
    rates = [s["market_shock_v2"]["signal_rate"] for s in segments]
    null_rates = [s["no_injection_market_shock_rate"] for s in synths]
    monotone = all(s["monotone_with_2pp_tolerance"] for s in synths)
    checks = {
        "POWER_2PCT_EVERY_SEGMENT_GTE_095": all(x >= 0.95 for x in p2),
        "POWER_1P5PCT_EVERY_SEGMENT_GTE_080": all(x >= 0.80 for x in p15),
        "POWER_MONOTONE_WITH_2PP_TOLERANCE": monotone,
        "HISTORICAL_SHOCK_BAR_RATE_EVERY_SEGMENT_LT_001": all(x is not None and x < 0.01 for x in rates),
        "NO_INJECTION_SAMPLE_RATE_EVERY_SEGMENT_LT_001": all(x < 0.01 for x in null_rates),
    }
    return {
        "checks": checks,
        "research_numeric_gates": "PASS" if all(checks.values()) else "FAIL",
        "min_2pct_power": float(min(p2)),
        "min_1p5pct_power": float(min(p15)),
        "max_historical_shock_bar_rate": float(max(rates)),
        "max_no_injection_sample_rate": float(max(null_rates)),
        "FALSE_POSITIVE_RATE_REAL_HISTORY": "NOT_PROVEN_NO_AUTHORITATIVE_EVENT_LABEL_SET",
        "SESSION_CALENDAR": "NOT_PROVEN_17ET_MARKET_CONVENTION_BUCKET_ONLY",
        "PRODUCTION_PROMOTION": "BLOCKED_RESEARCH_CHALLENGER_ONLY",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2020-04-06 00:00:00")
    parser.add_argument("--end", default="2026-08-31 23:59:59")
    parser.add_argument("--output", default="market_shock_challenger_v2_report.json")
    args = parser.parse_args()

    report: dict = {
        "contract": "GOLD_CONTROL_MARKET_SHOCK_CHALLENGER_V2",
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
        "session_semantics": "17ET_CME_EBS_MARKET_CONVENTION_BUCKET_FOR_EXPOST_BNS_ONLY; EXACT_TWELVE_SESSION_CALENDAR_NOT_PROVEN",
        "frozen_parameters": {
            "K_LM": K_LM,
            "lm_main_alpha": LM_MAIN_ALPHA,
            "lm_n_intraday": N_INTRADAY,
            "pot_quantile": POT_Q,
            "evt_tail_p": TAIL_P,
            "bns_alpha": BNS_ALPHA,
            "bns_min_returns": BNS_MIN_RETURNS,
            "shock_rule": "LM_JUMP_5M_OR_EVT_FAST_MOVE_30M",
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
            "gaps_gt_10min": int(data["gap_s"].gt(600).sum()),
        }
        cn, sn = lm_constants()
        report["lm_primary_formula_check"] = {
            "c": math.sqrt(2.0 / math.pi),
            "Cn": cn,
            "Sn": sn,
            "critical_95": lm_critical(0.05),
            "critical_99": lm_critical(0.01),
            "critical_999": lm_critical(0.001),
            "sn_formula": "1/(c*sqrt(2*log(n)))",
        }

        segments: list[dict] = []
        synths: list[dict] = []
        fits: list[dict] = []
        events: list[dict] = []
        bns_summary: list[dict] = []

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
            fits.append({
                "year": year,
                "train_end_exclusive": cutoff.isoformat(),
                "train_rows": int(len(train)),
                "periodicity_slots": int(len(periodicity)),
                "evt30": asdict(evt30),
            })
            bns_summary.append({
                "year": year,
                "eligible_buckets": int(len(bns)),
                "significant_buckets_999": int(bns["bns_sig_999"].sum()) if not bns.empty else 0,
            })
            print(json.dumps({
                "segment": year,
                "shock_rate": segment_report["market_shock_v2"]["signal_rate"],
                "shock_episodes": segment_report["market_shock_v2"]["episodes"],
                "power_1p5": synth["market_shock_v2_power_by_abs_size"][str(0.015)],
                "power_2p0": synth["market_shock_v2_power_by_abs_size"][str(0.02)],
            }, sort_keys=True))

        report["fits"] = fits
        report["segments"] = segments
        report["synthetic_injection"] = synths
        report["bns_expost_summary"] = bns_summary
        report["top_shock_events"] = sorted(
            events,
            key=lambda x: max(x["score5"] or 0.0, x["score30"] or 0.0),
            reverse=True,
        )[:40]
        report["gates"] = _gate_status(segments, synths)
        report["status"] = (
            "RESEARCH_GATES_PASS_NOT_PROMOTED"
            if report["gates"]["research_numeric_gates"] == "PASS"
            else "REJECT_OR_REVISE_CHALLENGER_V2"
        )
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
