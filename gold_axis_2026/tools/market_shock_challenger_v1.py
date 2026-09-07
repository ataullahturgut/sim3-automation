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
from scipy.stats import genpareto

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
N_INTRADAY = 288
SYNTHETIC_SEED = 20260907
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
            "User-Agent": "GoldControl-Market-Shock-Challenger-V1/1.0",
        })
        self.last_request = 0.0

    def _pace(self) -> None:
        elapsed = time.monotonic() - self.last_request
        wait = MIN_REQUEST_INTERVAL_SECONDS - elapsed
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
        pages = 0
        while cursor_end >= start:
            payload = self.get_json(
                TIME_SERIES_URL,
                {
                    "symbol": SYMBOL,
                    "interval": INTERVAL,
                    "start_date": start.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_date": cursor_end.strftime("%Y-%m-%d %H:%M:%S"),
                    "timezone": "UTC",
                    "outputsize": MAX_OUTPUT,
                    "order": "DESC",
                    "format": "JSON",
                },
            )
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
                close = float(close)
                if close <= 0:
                    raise RuntimeError(f"TWELVE_INVALID_CLOSE:{ts.isoformat()}")
                if ts in rows and not math.isclose(rows[ts], close, rel_tol=0, abs_tol=1e-12):
                    raise RuntimeError(f"TWELVE_DUPLICATE_CONFLICT:{ts.isoformat()}")
                rows[ts] = close
                page_ts.append(ts)
            if not page_ts:
                break
            oldest = min(page_ts)
            newest = max(page_ts)
            pages += 1
            print(json.dumps({
                "fetch_page": pages,
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
        df = pd.DataFrame({"ts": list(rows.keys()), "close": list(rows.values())}).sort_values("ts")
        df = df.drop_duplicates("ts", keep="last").reset_index(drop=True)
        return df


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
    return out


def _day_bpv_scale(g: pd.DataFrame) -> float:
    r = g["ret"].dropna().to_numpy(float)
    if len(r) < 50:
        return float("nan")
    bp = np.abs(r[1:]) * np.abs(r[:-1])
    m = float(np.nanmean(bp)) if len(bp) else float("nan")
    return math.sqrt(m) if m > 0 and math.isfinite(m) else float("nan")


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
        mad = 1.4826 * float(np.median(np.abs(x - med)))
        sh = mad
    return sh if sh > 0 and math.isfinite(sh) else float("nan")


def fit_periodicity(train: pd.DataFrame) -> dict[int, float]:
    day_scales = train.groupby("utc_date", sort=False).apply(_day_bpv_scale)
    tmp = train[["utc_date", "slot", "ret"]].copy()
    tmp["day_scale"] = tmp["utc_date"].map(day_scales)
    tmp["rbar"] = tmp["ret"] / tmp["day_scale"]
    raw: dict[int, float] = {}
    for slot, g in tmp.groupby("slot"):
        x = g["rbar"].dropna().to_numpy(float)
        if len(x) < 20:
            continue
        sh = _short_half_scale(x)
        if not math.isfinite(sh) or sh <= 0:
            continue
        z2 = (x / sh) ** 2
        keep = z2 <= WSD_CUTOFF_CHISQ
        if keep.sum() < 10:
            continue
        wsd = math.sqrt(1.081 * float(np.mean(x[keep] ** 2)))
        if wsd > 0 and math.isfinite(wsd):
            raw[int(slot)] = wsd
    if len(raw) < 500:
        raise RuntimeError(f"PERIODICITY_TOO_SPARSE:{len(raw)}")
    norm = math.sqrt(float(np.mean(np.square(list(raw.values())))))
    if not math.isfinite(norm) or norm <= 0:
        raise RuntimeError("PERIODICITY_NORMALIZATION_INVALID")
    return {k: v / norm for k, v in raw.items()}


def lm_critical(alpha: float, n: int = N_INTRADAY) -> float:
    if not (0 < alpha < 1):
        raise ValueError(alpha)
    c = math.sqrt(2.0 / math.pi)
    root = math.sqrt(2.0 * math.log(n))
    cn = root / c - (math.log(math.pi) + math.log(math.log(n))) / (2.0 * c * root)
    sn = 1.0 / (2.0 * c * root)
    beta = -math.log(-math.log(1.0 - alpha))
    return cn + sn * beta


def add_scores(frame: pd.DataFrame, periodicity: dict[int, float]) -> pd.DataFrame:
    out = frame.copy()
    out["period_factor"] = out["slot"].map(periodicity).fillna(1.0)
    denom = out["local_sigma"] * out["period_factor"]
    out["score5"] = out["ret"].abs() / denom
    out["score30"] = out["move30"].abs() / (math.sqrt(6.0) * denom)
    return out


def fit_evt(x: pd.Series) -> EVTModel:
    arr = x.replace([np.inf, -np.inf], np.nan).dropna().to_numpy(float)
    if len(arr) < 5000:
        raise RuntimeError(f"EVT_TRAIN_TOO_SMALL:{len(arr)}")
    u = float(np.quantile(arr, POT_Q))
    exc = arr[arr > u] - u
    if len(exc) < 100:
        raise RuntimeError(f"EVT_EXCEED_TOO_SMALL:{len(exc)}")
    shape, loc, scale = genpareto.fit(exc, floc=0.0)
    if not (math.isfinite(shape) and math.isfinite(scale) and scale > 0):
        raise RuntimeError(f"EVT_FIT_INVALID:{shape}:{scale}")
    cond_cdf = 1.0 - TAIL_P / (1.0 - POT_Q)
    critical = u + float(genpareto.ppf(cond_cdf, shape, loc=0.0, scale=scale))
    if not math.isfinite(critical) or critical <= u:
        raise RuntimeError(f"EVT_CRITICAL_INVALID:{critical}")
    return EVTModel(u, float(shape), float(scale), critical, len(arr), len(exc))


def episode_count(sig: pd.Series, ts: pd.Series) -> int:
    mask = sig.fillna(False).to_numpy(bool)
    t = pd.to_datetime(ts, utc=True)
    n = 0
    prev_idx: int | None = None
    for i, on in enumerate(mask):
        if not on:
            continue
        if prev_idx is None or (t.iloc[i] - t.iloc[prev_idx]).total_seconds() > 600 or prev_idx != i - 1:
            n += 1
        prev_idx = i
    return n


def detector_metrics(seg: pd.DataFrame, col: str) -> dict:
    valid = seg[col].notna() if col.startswith("score") else pd.Series(True, index=seg.index)
    sig = seg[col].fillna(False).astype(bool) if col.endswith("_sig") else pd.Series(False, index=seg.index)
    return {
        "bars": int(len(seg)),
        "signal_bars": int(sig.sum()),
        "signal_rate": float(sig.mean()) if len(sig) else None,
        "episodes": episode_count(sig, seg["ts"]),
    }


def summarize_segment(scored: pd.DataFrame, year: int, evt5: EVTModel, evt30: EVTModel) -> tuple[dict, pd.DataFrame]:
    seg = scored[scored["ts"].dt.year.eq(year)].copy()
    if year == 2026:
        seg = seg[seg["ts"] < pd.Timestamp("2026-09-01", tz="UTC")].copy()
    for a in (0.05, 0.01, 0.001):
        tag = {0.05: "95", 0.01: "99", 0.001: "999"}[a]
        seg[f"lm_{tag}_sig"] = seg["score5"] > lm_critical(a)
    seg["evt5_sig"] = seg["score5"] >= evt5.critical_score
    seg["evt30_sig"] = seg["score30"] >= evt30.critical_score
    votes = seg[["lm_999_sig", "evt5_sig", "evt30_sig"]].fillna(False).astype(int).sum(axis=1)
    seg["consensus_sig"] = votes >= 2
    seg["consensus_dir"] = np.where(
        seg["consensus_sig"],
        np.where(seg["evt30_sig"], np.sign(seg["move30"]), np.sign(seg["ret"])),
        0,
    )

    abs5 = seg["ret"].abs()
    abs30 = seg["move30"].abs()
    alert = seg["consensus_sig"]
    report = {
        "year": year,
        "bars": int(len(seg)),
        "scored_5m": int(seg["score5"].notna().sum()),
        "scored_30m": int(seg["score30"].notna().sum()),
        "lm_95": detector_metrics(seg, "lm_95_sig"),
        "lm_99": detector_metrics(seg, "lm_99_sig"),
        "lm_999": detector_metrics(seg, "lm_999_sig"),
        "evt5": detector_metrics(seg, "evt5_sig"),
        "evt30": detector_metrics(seg, "evt30_sig"),
        "consensus": detector_metrics(seg, "consensus_sig"),
        "consensus_up_bars": int(((seg["consensus_dir"] > 0) & alert).sum()),
        "consensus_down_bars": int(((seg["consensus_dir"] < 0) & alert).sum()),
        "median_abs_5m_return_alert": float(abs5[alert].median()) if alert.any() else None,
        "median_abs_5m_return_nonalert": float(abs5[~alert].median()),
        "p95_abs_5m_return_alert": float(abs5[alert].quantile(0.95)) if alert.any() else None,
        "median_abs_30m_move_alert": float(abs30[alert].median()) if alert.any() else None,
        "median_abs_30m_move_nonalert": float(abs30[~alert].median()),
        "agreement": {
            "lm999_evt5": int((seg["lm_999_sig"] & seg["evt5_sig"]).sum()),
            "lm999_evt30": int((seg["lm_999_sig"] & seg["evt30_sig"]).sum()),
            "evt5_evt30": int((seg["evt5_sig"] & seg["evt30_sig"]).sum()),
            "all3": int((seg["lm_999_sig"] & seg["evt5_sig"] & seg["evt30_sig"]).sum()),
        },
    }
    return report, seg


def synthetic_injection(seg: pd.DataFrame, evt5: EVTModel, evt30: EVTModel, year: int, sample_n: int = 300) -> dict:
    eligible = seg[
        seg["ret"].notna()
        & seg["move30"].notna()
        & seg["local_sigma"].gt(0)
        & seg["period_factor"].gt(0)
    ].copy()
    if len(eligible) < sample_n:
        raise RuntimeError(f"SYNTHETIC_ELIGIBLE_TOO_SMALL:{year}:{len(eligible)}")
    rng = np.random.default_rng(SYNTHETIC_SEED + year)
    take = rng.choice(eligible.index.to_numpy(), size=sample_n, replace=False)
    s = eligible.loc[take].copy()
    denom = s["local_sigma"].to_numpy(float) * s["period_factor"].to_numpy(float)
    base_r = s["ret"].to_numpy(float)
    base_m30 = s["move30"].to_numpy(float)
    lmcrit = lm_critical(0.001)

    base_lm = np.abs(base_r) / denom > lmcrit
    base_evt5 = np.abs(base_r) / denom >= evt5.critical_score
    base_evt30 = np.abs(base_m30) / (math.sqrt(6.0) * denom) >= evt30.critical_score
    base_cons = (base_lm.astype(int) + base_evt5.astype(int) + base_evt30.astype(int)) >= 2

    rows = []
    for size in SYNTHETIC_SIZES:
        for sign in (-1, 1):
            j = sign * math.log1p(size)
            rj = base_r + j
            m30j = base_m30 + j
            lm = np.abs(rj) / denom > lmcrit
            e5 = np.abs(rj) / denom >= evt5.critical_score
            e30 = np.abs(m30j) / (math.sqrt(6.0) * denom) >= evt30.critical_score
            cons = (lm.astype(int) + e5.astype(int) + e30.astype(int)) >= 2
            rows.append({
                "year": year,
                "jump_abs_pct": size * 100.0,
                "sign": "UP" if sign > 0 else "DOWN",
                "n": sample_n,
                "lm_power": float(lm.mean()),
                "evt5_power": float(e5.mean()),
                "evt30_power": float(e30.mean()),
                "consensus_power": float(cons.mean()),
            })
    by_size = {}
    for size in SYNTHETIC_SIZES:
        vals = [r["consensus_power"] for r in rows if math.isclose(r["jump_abs_pct"], size * 100.0)]
        by_size[str(size)] = float(np.mean(vals))
    powers = [by_size[str(x)] for x in SYNTHETIC_SIZES]
    monotone = all(powers[i + 1] + 0.02 >= powers[i] for i in range(len(powers) - 1))
    return {
        "year": year,
        "sample_n": sample_n,
        "null_consensus_rate_on_sample": float(base_cons.mean()),
        "rows": rows,
        "consensus_power_by_abs_size": by_size,
        "monotone_with_2pct_tolerance": monotone,
    }


def top_consensus_events(seg: pd.DataFrame, year: int, n: int = 20) -> list[dict]:
    x = seg[seg["consensus_sig"]].copy()
    if x.empty:
        return []
    x["rank_score"] = x[["score5", "score30"]].max(axis=1)
    x = x.sort_values("rank_score", ascending=False).head(n)
    out = []
    for _, r in x.iterrows():
        out.append({
            "year": year,
            "ts": pd.Timestamp(r["ts"]).isoformat(),
            "direction": "UP" if r["consensus_dir"] > 0 else "DOWN",
            "return_5m_pct": float(r["ret"] * 100.0),
            "move_30m_pct": float(r["move30"] * 100.0) if pd.notna(r["move30"]) else None,
            "score5": float(r["score5"]),
            "score30": float(r["score30"]) if pd.notna(r["score30"]) else None,
            "lm999": bool(r["lm_999_sig"]),
            "evt5": bool(r["evt5_sig"]),
            "evt30": bool(r["evt30_sig"]),
        })
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2020-04-06 00:00:00")
    parser.add_argument("--end", default="2026-08-31 23:59:59")
    parser.add_argument("--output", default="market_shock_challenger_v1_report.json")
    args = parser.parse_args()

    generated_at = datetime.now(timezone.utc).isoformat()
    report: dict = {
        "contract": "GOLD_CONTROL_MARKET_SHOCK_CHALLENGER_V1",
        "generated_at": generated_at,
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
        "session_calendar_authority": "UNRESOLVED_GAPS_GT_10MIN_NOT_SCORED",
        "frozen_parameters": {
            "K_LM": K_LM,
            "pot_quantile": POT_Q,
            "tail_p": TAIL_P,
            "lm_main_alpha": 0.001,
            "lm_sensitivity_alpha": [0.05, 0.01, 0.001],
            "synthetic_sizes": SYNTHETIC_SIZES,
            "consensus": "AT_LEAST_2_OF_3",
        },
    }

    try:
        client = TwelveClient()
        report["provider_earliest_timestamp_5m"] = client.earliest()
        start = pd.Timestamp(args.start, tz="UTC")
        end = pd.Timestamp(args.end, tz="UTC")
        raw = client.history(start, end)
        data = build_returns(raw)
        report["history"] = {
            "rows": int(len(data)),
            "first_ts": data["ts"].min().isoformat(),
            "last_ts": data["ts"].max().isoformat(),
            "valid_5m_returns": int(data["ret"].notna().sum()),
            "gaps_gt_10min": int(data["gap_s"].gt(600).sum()),
        }

        segment_reports = []
        synth_reports = []
        top_events = []
        fit_reports = []

        for year in (2024, 2025, 2026):
            train = data[data["ts"] < pd.Timestamp(f"{year}-01-01", tz="UTC")].copy()
            test = data[data["ts"].dt.year.eq(year)].copy()
            if year == 2026:
                test = test[test["ts"] < pd.Timestamp("2026-09-01", tz="UTC")].copy()
            if len(train) < 100000 or len(test) < 10000:
                raise RuntimeError(f"SEGMENT_COVERAGE_TOO_SMALL:{year}:{len(train)}:{len(test)}")
            periodicity = fit_periodicity(train)
            train_scored = add_scores(train, periodicity)
            evt5 = fit_evt(train_scored["score5"])
            evt30 = fit_evt(train_scored["score30"])
            scored_all = add_scores(data, periodicity)
            seg_report, seg_scored = summarize_segment(scored_all, year, evt5, evt30)
            segment_reports.append(seg_report)
            synth_reports.append(synthetic_injection(seg_scored, evt5, evt30, year))
            top_events.extend(top_consensus_events(seg_scored, year, n=20))
            fit_reports.append({
                "year": year,
                "train_end_exclusive": f"{year}-01-01T00:00:00+00:00",
                "train_rows": int(len(train)),
                "periodicity_slots": int(len(periodicity)),
                "evt5": asdict(evt5),
                "evt30": asdict(evt30),
                "lm_critical_95": lm_critical(0.05),
                "lm_critical_99": lm_critical(0.01),
                "lm_critical_999": lm_critical(0.001),
            })
            print(json.dumps({
                "segment": year,
                "consensus_bars": seg_report["consensus"]["signal_bars"],
                "consensus_episodes": seg_report["consensus"]["episodes"],
                "synthetic_2pct_power": synth_reports[-1]["consensus_power_by_abs_size"][str(0.02)],
            }, sort_keys=True))

        power2 = [x["consensus_power_by_abs_size"][str(0.02)] for x in synth_reports]
        monotone = all(x["monotone_with_2pct_tolerance"] for x in synth_reports)
        consensus_rates = [x["consensus"]["signal_rate"] for x in segment_reports]
        max_rate = max(consensus_rates)
        report["fits"] = fit_reports
        report["segments"] = segment_reports
        report["synthetic_injection"] = synth_reports
        report["top_consensus_events"] = sorted(top_events, key=lambda x: max(x["score5"], x["score30"] or 0), reverse=True)[:30]
        report["gates"] = {
            "FORECAST_INDEPENDENCE": "PASS",
            "WALK_FORWARD_NO_FUTURE_TRAINING": "PASS",
            "SYNTHETIC_POWER_MONOTONE": "PASS" if monotone else "REVIEW",
            "MIN_2PCT_SYNTHETIC_CONSENSUS_POWER": float(min(power2)),
            "MAX_HISTORICAL_CONSENSUS_BAR_RATE": float(max_rate),
            "TRUE_FALSE_POSITIVE_RATE_REAL_HISTORY": "NOT_PROVEN_NO_AUTHORITATIVE_EVENT_LABEL_SET",
            "SESSION_CALENDAR": "NOT_PROVEN_GAPS_GT_10MIN_EXCLUDED_NOT_CLASSIFIED",
            "PRODUCTION_PROMOTION": "BLOCKED_RESEARCH_CHALLENGER_ONLY",
        }
        report["status"] = "REPLAY_PASS_RESEARCH_CHALLENGER_NOT_PROMOTED"
        Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        report["status"] = "BLOCKED"
        report["error"] = f"{type(exc).__name__}:{exc}"
        Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
