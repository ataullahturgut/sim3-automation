from __future__ import annotations

import hashlib
import io
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import requests

from gold_axis_2026.v159_thesis import run_v159_driver_corrected_meta_trust as core


def segmented_fred_fetch(series_id: str, start: str, end: str):
    """Same frozen FRED source and date range, retrieved in annual chunks.

    The first V1.59 run timed out before any model scoring while reading one
    multi-year fredgraph response. This wrapper changes transport only: no
    series, feature, target, threshold, candidate or date rule is changed.
    """
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    frames = []
    payload_hashes = []
    retrieved = []
    year = start_ts.year
    while year <= end_ts.year:
        a = max(start_ts, pd.Timestamp(f"{year}-01-01"))
        b = min(end_ts, pd.Timestamp(f"{year}-12-31"))
        last_exc = None
        response = None
        for _ in range(3):
            try:
                response = requests.get(
                    core.FRED_CSV,
                    params={"id": series_id, "cosd": a.date().isoformat(), "coed": b.date().isoformat()},
                    headers={"User-Agent": "Gold-Control-V159-Research/1.0"},
                    timeout=(15, 45),
                )
                if response.status_code == 200:
                    break
                last_exc = RuntimeError(f"HTTP_{response.status_code}")
            except requests.RequestException as exc:
                last_exc = exc
                response = None
        if response is None or response.status_code != 200:
            raise RuntimeError(f"V159_FRED_SEGMENT_FETCH_FAIL:{series_id}:{year}:{last_exc}")
        payload_hashes.append(hashlib.sha256(response.content).hexdigest())
        retrieved.append(datetime.now(timezone.utc).isoformat())
        d = pd.read_csv(io.BytesIO(response.content))
        if d.shape[1] < 2:
            raise RuntimeError(f"V159_FRED_SCHEMA_{series_id}_{year}")
        date_col = d.columns[0]
        value_col = series_id if series_id in d.columns else d.columns[1]
        d = d[[date_col, value_col]].rename(columns={date_col: "source_date", value_col: "value"})
        d["source_date"] = pd.to_datetime(d["source_date"], errors="coerce").dt.normalize()
        d["value"] = pd.to_numeric(d["value"], errors="coerce")
        d = d.dropna(subset=["source_date", "value"])
        frames.append(d)
        year += 1
    out = pd.concat(frames, ignore_index=True).sort_values("source_date").drop_duplicates("source_date", keep="last")
    out = out[np.isfinite(out["value"])].reset_index(drop=True)
    if out.empty:
        raise RuntimeError(f"V159_FRED_EMPTY_{series_id}")
    combined = hashlib.sha256("|".join(payload_hashes).encode()).hexdigest()
    evidence = {
        "provider": "FRED",
        "series_id": series_id,
        "retrieved_at": max(retrieved),
        "payload_sha256": combined,
        "payload_segments": len(payload_hashes),
        "segment_sha256": payload_hashes,
        "rows": int(len(out)),
        "first_source_date": out["source_date"].min().date().isoformat(),
        "last_source_date": out["source_date"].max().date().isoformat(),
        "evidence_class": "HISTORICAL_ECONOMIC_DATE_RECONSTRUCTION_NOT_PROSPECTIVE_PIT",
        "same_date_join_forbidden": True,
        "transport_note": "annual segmented fredgraph retrieval; scientific source and date contract unchanged",
    }
    return out, evidence


def main() -> int:
    core.fetch_fred_series = segmented_fred_fetch
    return core.main()


if __name__ == "__main__":
    raise SystemExit(main())
