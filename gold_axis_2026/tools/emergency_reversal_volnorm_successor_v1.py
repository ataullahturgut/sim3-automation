from __future__ import annotations

import hashlib
import json
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import requests

MODEL_ID = "EMERGENCY_REVERSAL_VOLNORM_SUCCESSOR_V1"
SOURCE_ID = "XAU_TWELVE_1H_SELECT_16_00_NY_RESEARCH_V1"
VOL_WINDOW = 20
LEG_THRESHOLD = 2.0
REVERSAL_THRESHOLD = 2.0
EXTREME_THRESHOLD = 3.0
MIN_YEAR_COVERAGE = 0.90
TWELVE_URL = "https://api.twelvedata.com/time_series"


@dataclass(frozen=True)
class Config:
    model_id: str = MODEL_ID
    source_id: str = SOURCE_ID
    vol_window: int = VOL_WINDOW
    leg_threshold: float = LEG_THRESHOLD
    reversal_threshold: float = REVERSAL_THRESHOLD
    extreme_threshold: float = EXTREME_THRESHOLD

    def as_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "source_id": self.source_id,
            "vol_window": self.vol_window,
            "leg_threshold": self.leg_threshold,
            "reversal_threshold": self.reversal_threshold,
            "extreme_threshold": self.extreme_threshold,
        }


def stable_sha(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def _calendar_weekdays(year: int) -> int:
    start = pd.Timestamp(f"{year}-01-01")
    end = pd.Timestamp(f"{year}-12-31")
    return int(sum(d.dayofweek < 5 for d in pd.date_range(start, end, freq="D")))


def coverage_by_year(closes: pd.Series, years: Iterable[int]) -> dict[int, dict[str, float | int]]:
    out: dict[int, dict[str, float | int]] = {}
    idx = pd.DatetimeIndex(closes.index)
    for year in years:
        selected = int((idx.year == year).sum())
        weekdays = _calendar_weekdays(year)
        ratio = selected / weekdays if weekdays else 0.0
        out[year] = {"selected": selected, "calendar_weekdays": weekdays, "ratio": ratio}
    return out


def _request(params: dict[str, Any], api_key: str) -> dict[str, Any]:
    response = requests.get(
        TWELVE_URL,
        params=params,
        headers={"Authorization": f"apikey {api_key}", "User-Agent": "Gold-Control-Emergency-Reversal-Volnorm-V1/1.0"},
        timeout=(20, 180),
    )
    try:
        payload = response.json()
    except Exception as exc:  # pragma: no cover - network guard
        raise RuntimeError(f"MALFORMED_PROVIDER_RESPONSE:HTTP_{response.status_code}") from exc
    if response.status_code in {401, 403}:
        raise RuntimeError(f"AUTHENTICATION_ERROR:HTTP_{response.status_code}")
    if response.status_code == 429:
        raise RuntimeError("ENTITLEMENT_OR_RATE_LIMIT_BLOCKED:HTTP_429")
    if response.status_code >= 500:
        raise RuntimeError(f"SERVER_ERROR:HTTP_{response.status_code}")
    if response.status_code >= 400 or payload.get("status") == "error":
        raise RuntimeError(f"REQUEST_ERROR:HTTP_{response.status_code}:CODE_{payload.get('code')}")
    meta = payload.get("meta") or {}
    if str(meta.get("symbol")) != "XAU/USD" or str(meta.get("interval")) != "1h":
        raise RuntimeError("SOURCE_BINDING_FAIL")
    return payload


def _half_year_segments(year: int) -> list[tuple[str, str]]:
    return [
        (f"{year}-01-01 00:00:00", f"{year}-06-30 23:59:59"),
        (f"{year}-07-01 00:00:00", f"{year}-12-31 23:59:59"),
    ]


def fetch_twelve_ny17_hourly_closes(years: Iterable[int], api_key: str | None = None) -> tuple[pd.Series, dict[str, Any]]:
    key = (api_key or os.environ.get("TWELVE_DATA_API_KEY", "")).strip()
    if not key:
        raise RuntimeError("AUTHENTICATION_ERROR:TWELVE_DATA_API_KEY_NOT_SET")
    selected: dict[pd.Timestamp, float] = {}
    segment_hashes: list[str] = []
    for year in sorted(set(int(y) for y in years)):
        for start, end in _half_year_segments(year):
            payload = _request(
                {
                    "symbol": "XAU/USD",
                    "interval": "1h",
                    "start_date": start,
                    "end_date": end,
                    "timezone": "America/New_York",
                    "outputsize": 5000,
                    "order": "ASC",
                    "format": "JSON",
                },
                key,
            )
            segment_hashes.append(stable_sha(payload))
            for item in payload.get("values") or []:
                text = str(item.get("datetime") or "")
                if not text.endswith("16:00:00"):
                    continue
                day = pd.Timestamp(text).normalize()
                if day.year != year:
                    raise RuntimeError(f"SOURCE_BOUNDARY_FAIL:{text}")
                value = float(item["close"])
                if not math.isfinite(value) or value <= 0:
                    raise RuntimeError(f"MALFORMED_BAR:{text}")
                if day in selected:
                    raise RuntimeError(f"DUPLICATE_SELECTED_BAR:{text}")
                selected[day] = value
    series = pd.Series(selected, dtype=float).sort_index()
    if series.empty or series.index.has_duplicates:
        raise RuntimeError("EMPTY_OR_DUPLICATE_SERIES")
    years_sorted = sorted(set(int(y) for y in years))
    cov = coverage_by_year(series, years_sorted)
    failed = [y for y, row in cov.items() if float(row["ratio"]) < MIN_YEAR_COVERAGE]
    if failed:
        raise RuntimeError(f"BLOCKED_DATA_COVERAGE:{','.join(map(str, failed))}:{cov}")
    evidence = {
        "source_id": SOURCE_ID,
        "provider": "Twelve Data",
        "symbol": "XAU/USD",
        "interval": "1h",
        "timezone": "America/New_York",
        "selected_bar_open_time": "16:00:00",
        "selected_value": "close",
        "coverage": cov,
        "segment_payload_hashes": segment_hashes,
        "evidence_class": "HISTORICAL_RESEARCH_RECONSTRUCTION",
        "prospective_claim": False,
    }
    return series, evidence


def prepare_daily_frame(closes: pd.Series, config: Config = Config()) -> pd.DataFrame:
    s = closes.astype(float).sort_index().copy()
    if s.empty or s.index.has_duplicates or not np.isfinite(s.to_numpy()).all() or (s <= 0).any():
        raise ValueError("INVALID_CLOSE_SERIES")
    frame = pd.DataFrame({"close": s})
    frame.index = pd.DatetimeIndex(frame.index).normalize()
    frame["log_return"] = np.log(frame["close"] / frame["close"].shift(1))
    # Strictly prior-only scale: rolling window ending at t-1.
    frame["sigma20"] = frame["log_return"].rolling(config.vol_window).std(ddof=1).shift(1)
    frame["eligible"] = np.isfinite(frame["sigma20"]) & (frame["sigma20"] > 0)
    frame["variance_contribution"] = np.where(frame["eligible"], frame["sigma20"] ** 2, 0.0)
    frame["cum_lagged_variance"] = frame["variance_contribution"].cumsum()
    return frame


def _path_sigma(frame: pd.DataFrame, extreme_pos: int, current_pos: int) -> float:
    if current_pos <= extreme_pos:
        return 0.0
    current = float(frame.iloc[current_pos]["cum_lagged_variance"])
    start = float(frame.iloc[extreme_pos]["cum_lagged_variance"])
    value = current - start
    return math.sqrt(max(value, 0.0))


def _score(move: float, scale: float) -> float | None:
    if not math.isfinite(scale) or scale <= 0:
        return None
    return move / scale


def run_detector(closes: pd.Series, config: Config = Config()) -> pd.DataFrame:
    frame = prepare_daily_frame(closes, config)
    rows: list[dict[str, Any]] = []
    state = "UNINITIALIZED"
    peak_pos: int | None = None
    trough_pos: int | None = None
    leg_start_pos: int | None = None

    for pos, (day, item) in enumerate(frame.iterrows()):
        close = float(item["close"])
        eligible = bool(item["eligible"])
        alert = "OFF"
        alert_score: float | None = None
        alert_severity: str | None = None
        up_score: float | None = None
        down_score: float | None = None
        reference_extreme_date: str | None = None

        if not eligible:
            rows.append(
                {
                    "date": day.date().isoformat(), "close": close, "sigma20": None,
                    "state": state, "state_age": None, "up_score": None, "down_score": None,
                    "alert": alert, "alert_score": None, "alert_severity": None,
                    "reference_extreme_date": None, "eligible": False,
                }
            )
            continue

        if peak_pos is None or trough_pos is None:
            peak_pos = trough_pos = pos
            leg_start_pos = pos
            state = "SEEKING_INITIAL_LEG"
        elif state == "SEEKING_INITIAL_LEG":
            if close > float(frame.iloc[peak_pos]["close"]):
                peak_pos = pos
            if close < float(frame.iloc[trough_pos]["close"]):
                trough_pos = pos
            up_scale = _path_sigma(frame, trough_pos, pos)
            down_scale = _path_sigma(frame, peak_pos, pos)
            up_score = _score(math.log(close / float(frame.iloc[trough_pos]["close"])), up_scale)
            down_score = _score(math.log(close / float(frame.iloc[peak_pos]["close"])), down_scale)
            up_hit = up_score is not None and up_score >= config.leg_threshold
            down_hit = down_score is not None and down_score <= -config.leg_threshold
            if up_hit or down_hit:
                if up_hit and down_hit:
                    choose_up = abs(float(up_score)) > abs(float(down_score))
                    if abs(abs(float(up_score)) - abs(float(down_score))) <= 1e-12:
                        choose_up = float(item["log_return"]) >= 0
                else:
                    choose_up = up_hit
                if choose_up:
                    state = "UP_LEG"
                    peak_pos = pos
                    leg_start_pos = pos
                else:
                    state = "DOWN_LEG"
                    trough_pos = pos
                    leg_start_pos = pos
        elif state == "UP_LEG":
            assert peak_pos is not None
            peak_close = float(frame.iloc[peak_pos]["close"])
            if close >= peak_close:
                peak_pos = pos
            else:
                scale = _path_sigma(frame, peak_pos, pos)
                down_score = _score(math.log(close / peak_close), scale)
                if down_score is not None and down_score <= -config.reversal_threshold:
                    alert = "DOWN_ALERT"
                    alert_score = float(down_score)
                    alert_severity = "EXTREME" if abs(alert_score) >= config.extreme_threshold else "MAJOR"
                    reference_extreme_date = frame.index[peak_pos].date().isoformat()
                    state = "DOWN_LEG"
                    trough_pos = pos
                    leg_start_pos = pos
        elif state == "DOWN_LEG":
            assert trough_pos is not None
            trough_close = float(frame.iloc[trough_pos]["close"])
            if close <= trough_close:
                trough_pos = pos
            else:
                scale = _path_sigma(frame, trough_pos, pos)
                up_score = _score(math.log(close / trough_close), scale)
                if up_score is not None and up_score >= config.reversal_threshold:
                    alert = "UP_ALERT"
                    alert_score = float(up_score)
                    alert_severity = "EXTREME" if abs(alert_score) >= config.extreme_threshold else "MAJOR"
                    reference_extreme_date = frame.index[trough_pos].date().isoformat()
                    state = "UP_LEG"
                    peak_pos = pos
                    leg_start_pos = pos
        else:  # pragma: no cover - fail closed
            raise RuntimeError(f"UNKNOWN_STATE:{state}")

        state_age = None if leg_start_pos is None else int(pos - leg_start_pos)
        rows.append(
            {
                "date": day.date().isoformat(), "close": close, "sigma20": float(item["sigma20"]),
                "state": state, "state_age": state_age, "up_score": up_score, "down_score": down_score,
                "alert": alert, "alert_score": alert_score, "alert_severity": alert_severity,
                "reference_extreme_date": reference_extreme_date, "eligible": True,
            }
        )

    return pd.DataFrame(rows)


def timeline_hash(timeline: pd.DataFrame) -> str:
    records = timeline.where(pd.notna(timeline), None).to_dict(orient="records")
    return stable_sha(records)


def implementation_hash() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
