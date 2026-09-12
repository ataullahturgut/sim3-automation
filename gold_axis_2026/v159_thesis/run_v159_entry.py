from __future__ import annotations

import hashlib
import html
import re
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import requests

from gold_axis_2026.v159_thesis import run_v159_driver_corrected_meta_trust as core


_DATE_VALUE = re.compile(r"(\d{4}-\d{2}-\d{2})\s*(?:\||\s)\s*([+-]?\d+(?:\.\d+)?)")


def fred_table_fetch(series_id: str, start: str, end: str):
    """Read the same frozen FRED series from FRED's lightweight table endpoint.

    Earlier CI attempts timed out on fredgraph CSV before any model scoring.
    This is transport-only hardening: provider, series identity, historical
    date window, transformation, strict previous-date join, models, thresholds
    and evaluation contract are unchanged.
    """
    url = f"https://fred.stlouisfed.org/data/{series_id}"
    last_exc = None
    response = None
    for _ in range(3):
        try:
            response = requests.get(
                url,
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
        raise RuntimeError(f"V159_FRED_TABLE_FETCH_FAIL:{series_id}:{last_exc}")

    text = html.unescape(response.text)
    # Preserve whitespace while removing tags so the server-rendered DATE/VALUE
    # table is parseable without executing browser JavaScript.
    plain = re.sub(r"<[^>]+>", " ", text)
    plain = re.sub(r"[\t\r\n]+", " ", plain)
    pairs = _DATE_VALUE.findall(plain)
    if not pairs:
        # FRED currently also renders old rows in compact '#date|value' text.
        pairs = re.findall(r"#?(\d{4}-\d{2}-\d{2})\s*\|\s*([+-]?\d+(?:\.\d+)?)", text)
    if not pairs:
        raise RuntimeError(f"V159_FRED_TABLE_PARSE_FAIL:{series_id}")

    d = pd.DataFrame(pairs, columns=["source_date", "value"])
    d["source_date"] = pd.to_datetime(d["source_date"], errors="coerce").dt.normalize()
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    d = d.dropna(subset=["source_date", "value"])
    # Duplicate renderings are acceptable only when they agree exactly.
    conflicts = d.groupby("source_date")["value"].nunique(dropna=True)
    if (conflicts > 1).any():
        bad = conflicts[conflicts > 1].index.min()
        raise RuntimeError(f"V159_FRED_TABLE_CONFLICT:{series_id}:{bad.date().isoformat()}")
    d = d.drop_duplicates("source_date", keep="last")
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    d = d[(d["source_date"] >= a) & (d["source_date"] <= b)].copy()
    d = d[np.isfinite(d["value"])].sort_values("source_date").reset_index(drop=True)
    if d.empty:
        raise RuntimeError(f"V159_FRED_EMPTY_{series_id}")

    evidence = {
        "provider": "FRED",
        "series_id": series_id,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "payload_sha256": hashlib.sha256(response.content).hexdigest(),
        "rows": int(len(d)),
        "first_source_date": d["source_date"].min().date().isoformat(),
        "last_source_date": d["source_date"].max().date().isoformat(),
        "evidence_class": "HISTORICAL_ECONOMIC_DATE_RECONSTRUCTION_NOT_PROSPECTIVE_PIT",
        "same_date_join_forbidden": True,
        "transport_note": "FRED server-rendered table endpoint used after pre-score fredgraph timeouts; scientific source/date contract unchanged",
    }
    return d, evidence


def main() -> int:
    core.fetch_fred_series = fred_table_fetch
    return core.main()


if __name__ == "__main__":
    raise SystemExit(main())
