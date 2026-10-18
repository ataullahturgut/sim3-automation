from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

import emergency_reversal_volnorm_successor_v1 as core

MODEL_ID = "EMERGENCY_REVERSAL_VOLNORM_SUCCESSOR_V2"
SOURCE_ID = "XAU_TWELVE_1H_SELECT_14_00_NY_RESEARCH_V2"
SELECTED_HOUR = 14
MIN_YEAR_COVERAGE = 0.95


def config() -> core.Config:
    return core.Config(
        model_id=MODEL_ID,
        source_id=SOURCE_ID,
        vol_window=core.VOL_WINDOW,
        leg_threshold=core.LEG_THRESHOLD,
        reversal_threshold=core.REVERSAL_THRESHOLD,
        extreme_threshold=core.EXTREME_THRESHOLD,
    )


def fetch_twelve_closes(years: Iterable[int], api_key: str | None = None) -> tuple[pd.Series, dict[str, Any]]:
    key = (api_key or __import__("os").environ.get("TWELVE_DATA_API_KEY", "")).strip()
    if not key:
        raise RuntimeError("AUTHENTICATION_ERROR:TWELVE_DATA_API_KEY_NOT_SET")
    selected: dict[pd.Timestamp, float] = {}
    segment_hashes: list[str] = []
    years_sorted = sorted(set(int(y) for y in years))
    for year in years_sorted:
        for start, end in core._half_year_segments(year):
            payload = core._request(
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
            segment_hashes.append(core.stable_sha(payload))
            for item in payload.get("values") or []:
                text = str(item.get("datetime") or "")
                if len(text) < 19:
                    continue
                ts = pd.Timestamp(text)
                if ts.year != year or ts.hour != SELECTED_HOUR or ts.minute != 0 or ts.second != 0:
                    continue
                day = ts.normalize()
                value = float(item["close"])
                if not math.isfinite(value) or value <= 0:
                    raise RuntimeError(f"MALFORMED_BAR:{text}")
                if day in selected:
                    raise RuntimeError(f"DUPLICATE_SELECTED_BAR:{text}")
                selected[day] = value
    series = pd.Series(selected, dtype=float).sort_index()
    if series.empty or series.index.has_duplicates:
        raise RuntimeError("EMPTY_OR_DUPLICATE_SERIES")
    cov = core.coverage_by_year(series, years_sorted)
    failed = [y for y, row in cov.items() if float(row["ratio"]) < MIN_YEAR_COVERAGE]
    if failed:
        raise RuntimeError(f"BLOCKED_DATA_COVERAGE:{','.join(map(str, failed))}:{cov}")
    evidence = {
        "source_id": SOURCE_ID,
        "provider": "Twelve Data",
        "symbol": "XAU/USD",
        "interval": "1h",
        "timezone": "America/New_York",
        "selected_bar_open_time": "14:00:00",
        "selected_value": "close",
        "coverage": cov,
        "segment_payload_hashes": segment_hashes,
        "evidence_class": "HISTORICAL_RESEARCH_RECONSTRUCTION",
        "prospective_claim": False,
    }
    return series, evidence


def run_detector(closes: pd.Series) -> pd.DataFrame:
    return core.run_detector(closes, config())


def timeline_hash(timeline: pd.DataFrame) -> str:
    return core.timeline_hash(timeline)


def config_sha() -> str:
    payload = config().as_dict() | {"selected_hour": SELECTED_HOUR, "min_year_coverage": MIN_YEAR_COVERAGE}
    return core.stable_sha(payload)


def implementation_hash() -> str:
    h = hashlib.sha256()
    h.update(Path(core.__file__).read_bytes())
    h.update(Path(__file__).read_bytes())
    return h.hexdigest()
