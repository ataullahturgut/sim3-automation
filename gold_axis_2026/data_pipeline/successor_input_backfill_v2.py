from __future__ import annotations

import hashlib

import pandas as pd

import successor_input_backfill as base

base.PIPELINE_VERSION = "GOLD_SUCCESSOR_INPUT_BACKFILL_R2_2026-09-01"


def fred_asof_snapshot_with_bounded_staleness(series_id: str, asof: pd.Timestamp, api_key: str):
    """Return the latest value genuinely visible at the historical as-of date.

    Most daily series resolve inside 45 days. If an official series has a temporary
    publication/licensing gap, expand the lookback but never use a future observation.
    A value older than 370 days is rejected rather than silently imputed.
    """
    end = asof.date().isoformat()
    for lookback_days in (45, 180, 370):
        start = (asof - pd.Timedelta(days=lookback_days)).date().isoformat()
        params = {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "realtime_start": end,
            "realtime_end": end,
            "observation_start": start,
            "observation_end": end,
            "sort_order": "desc",
            "limit": 1000,
        }
        r = base.get_with_retry(base.FRED_URL, params=params)
        payload = r.json()
        obs = payload.get("observations", []) if isinstance(payload, dict) else []
        valid = []
        for z in obs:
            sv = str(z.get("value", "."))
            if sv in {".", "", "nan", "None"}:
                continue
            try:
                value = float(sv)
            except ValueError:
                continue
            d = pd.Timestamp(str(z.get("date")))
            if d <= asof:
                valid.append((d, value))
        if valid:
            d, value = max(valid, key=lambda x: x[0])
            age_days = int((asof.normalize() - d.normalize()).days)
            if age_days > 370:
                raise RuntimeError(f"ALFRED_STALE_VALUE:{series_id}:{end}:{age_days}")
            digest = hashlib.sha256(r.content).hexdigest()
            return value, d.date().isoformat(), digest
    raise RuntimeError(f"ALFRED_NO_VALID_VALUE_BOUNDED:{series_id}:{end}")


base.fred_asof_snapshot = fred_asof_snapshot_with_bounded_staleness

if __name__ == "__main__":
    base.main()
