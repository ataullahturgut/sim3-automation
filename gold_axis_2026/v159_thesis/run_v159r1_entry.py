from __future__ import annotations

import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from gold_axis_2026.v159_thesis import run_v159_driver_corrected_meta_trust as core

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "v159_thesis/contracts/v159_driver_corrected_meta_trust_freeze_v1.json"
OVERLAY = ROOT / "v159_thesis/contracts/v159r1_fedboard_source_binding_freeze_v1.json"
FED_OUTPUT = "https://www.federalreserve.gov/datadownload/Output.aspx"


def merged_contract() -> dict:
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    if overlay["status"] != "FROZEN_BEFORE_V159R1_RETROSPECTIVE_SCORING":
        raise RuntimeError("V159R1_OVERLAY_NOT_FROZEN")
    if overlay["parent_contract"] != parent["contract_id"]:
        raise RuntimeError("V159R1_PARENT_CONTRACT_MISMATCH")
    if overlay["parent_scoring_status"] != "NO_PERFORMANCE_SCORE_PRODUCED":
        raise RuntimeError("V159R1_PREDECESSOR_SCORE_LOCK_FAIL")
    # Preserve every scientific field from the parent. Only contract identity
    # and source provenance are revised by the pre-score source-binding overlay.
    out = json.loads(json.dumps(parent))
    out["contract_id"] = overlay["contract_id"]
    out["status"] = overlay["status"]
    out["source_binding_revision"] = overlay
    out["source"]["corrected_public_driver_reconstruction"] = {
        "provider": overlay["source_binding"]["provider"],
        "program": overlay["source_binding"]["program"],
        "series": overlay["source_binding"]["series"],
        "join_rule": "strict previous economic source date only; same-date driver observation is forbidden",
        "evidence_warning": overlay["source_binding"]["historical_reconstruction_warning"],
    }
    return out


def _release_for_alias(series_id: str) -> str:
    return "H10" if series_id == "DTWEXBGS" else "H15"


def fedboard_fetch(series_id: str, start: str, end: str):
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    meta = overlay["source_binding"]["series"].get(series_id)
    if meta is None:
        raise KeyError(series_id)
    params = {
        "rel": _release_for_alias(series_id),
        "series": meta["package_hash"],
        "lastObs": "",
        "from": pd.Timestamp(start).strftime("%m/%d/%Y"),
        "to": pd.Timestamp(end).strftime("%m/%d/%Y"),
        "filetype": "csv",
        "label": "include",
        "layout": "seriescolumn",
        "type": "package",
    }
    last_exc = None
    response = None
    for _ in range(3):
        try:
            response = requests.get(
                FED_OUTPUT,
                params=params,
                headers={"User-Agent": "Gold-Control-V159R1-Research/1.0"},
                timeout=(15, 60),
            )
            if response.status_code == 200:
                break
            last_exc = RuntimeError(f"HTTP_{response.status_code}")
        except requests.RequestException as exc:
            last_exc = exc
            response = None
    if response is None or response.status_code != 200:
        raise RuntimeError(f"V159R1_FEDBOARD_FETCH_FAIL:{series_id}:{last_exc}")

    text = response.content.decode("utf-8-sig", errors="strict")
    rows = list(csv.reader(io.StringIO(text)))
    header_i = next((i for i, row in enumerate(rows) if row and row[0].strip() == "Time Period"), None)
    if header_i is None:
        raise RuntimeError(f"V159R1_FEDBOARD_TIME_HEADER_NOT_FOUND:{series_id}")
    header = [x.strip() for x in rows[header_i]]
    wanted = meta["package_column"]
    if wanted not in header:
        raise RuntimeError(f"V159R1_FEDBOARD_COLUMN_NOT_FOUND:{series_id}:{wanted}:{header}")
    value_i = header.index(wanted)
    parsed = []
    for row in rows[header_i + 1:]:
        if len(row) <= value_i:
            continue
        day = pd.to_datetime(row[0].strip(), errors="coerce")
        raw = row[value_i].strip()
        if pd.isna(day) or raw in {"", "ND", "NA"}:
            continue
        try:
            value = float(raw)
        except ValueError:
            continue
        if np.isfinite(value):
            parsed.append((pd.Timestamp(day).normalize(), value))
    d = pd.DataFrame(parsed, columns=["source_date", "value"])
    if d.empty:
        raise RuntimeError(f"V159R1_FEDBOARD_EMPTY:{series_id}")
    conflicts = d.groupby("source_date")["value"].nunique()
    if (conflicts > 1).any():
        raise RuntimeError(f"V159R1_FEDBOARD_DUPLICATE_CONFLICT:{series_id}")
    d = d.drop_duplicates("source_date", keep="last").sort_values("source_date").reset_index(drop=True)
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    if d["source_date"].min() > a + pd.Timedelta(days=10) or d["source_date"].max() < b - pd.Timedelta(days=10):
        raise RuntimeError(f"V159R1_FEDBOARD_DATE_COVERAGE_FAIL:{series_id}:{d.source_date.min()}:{d.source_date.max()}")
    evidence = {
        "provider": overlay["source_binding"]["provider"],
        "program": overlay["source_binding"]["program"],
        "release": _release_for_alias(series_id),
        "series_alias": series_id,
        "unique_id": meta["unique_id"],
        "package_hash": meta["package_hash"],
        "package_column": wanted,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "payload_sha256": hashlib.sha256(response.content).hexdigest(),
        "rows": int(len(d)),
        "first_source_date": d["source_date"].min().date().isoformat(),
        "last_source_date": d["source_date"].max().date().isoformat(),
        "evidence_class": "HISTORICAL_ECONOMIC_DATE_RECONSTRUCTION_NOT_PROSPECTIVE_PIT",
        "same_date_join_forbidden": True,
        "source_binding_revision": overlay["contract_id"],
    }
    return d, evidence


def main() -> int:
    core.load_contract = merged_contract
    core.fetch_fred_series = fedboard_fetch
    return core.main()


if __name__ == "__main__":
    raise SystemExit(main())
