from __future__ import annotations

import gzip
import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"
OUT = AX / "DATABENTO_RAW_ARCHIVE_2022_2024_OUT"
OUT.mkdir(exist_ok=True)

DATASET = "GLBX.MDP3"
SCHEMA = "ohlcv-1h"
START = "2022-01-01"
END = "2025-01-01"  # Databento end-exclusive; covers through 2024-12-31.
ROOTS = ["GC", "SI", "NQ", "ZN", "CL"]
ROLLS = ["c", "n", "v"]
MAX_COST_USD = 3.00

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def serialize_obj(x):
    if hasattr(x, "to_dict"):
        return x.to_dict()
    if hasattr(x, "__dict__"):
        return {k: v for k, v in x.__dict__.items() if not k.startswith("_")}
    return str(x)

def validate_and_normalize(store, roll: str) -> pd.DataFrame:
    q = store.to_df().reset_index()
    if "ts_event" not in q.columns and "index" in q.columns:
        q = q.rename(columns={"index": "ts_event"})
    required = ["ts_event", "symbol", "instrument_id", "open", "high", "low", "close", "volume"]
    miss = [c for c in required if c not in q.columns]
    if miss:
        raise RuntimeError(f"{roll}_MISSING_COLUMNS:{miss}; cols={q.columns.tolist()}")

    q = q[required].copy()
    q["ts_event"] = pd.to_datetime(q["ts_event"], utc=True, errors="raise")
    q["symbol"] = q["symbol"].astype(str)
    q["instrument_id"] = pd.to_numeric(q["instrument_id"], errors="raise").astype("int64")
    for c in ["open", "high", "low", "close", "volume"]:
        q[c] = pd.to_numeric(q[c], errors="raise")

    expected = {f"{root}.{roll}.0" for root in ROOTS}
    got = set(q["symbol"].unique())
    missing_symbols = sorted(expected - got)
    unexpected_symbols = sorted(got - expected)
    if missing_symbols:
        raise RuntimeError(f"{roll}_MISSING_SYMBOLS:{missing_symbols}")
    if unexpected_symbols:
        raise RuntimeError(f"{roll}_UNEXPECTED_SYMBOLS:{unexpected_symbols}")

    dup = int(q.duplicated(["ts_event", "symbol"]).sum())
    if dup:
        raise RuntimeError(f"{roll}_DUPLICATE_TS_SYMBOL:{dup}")

    bad_ohlc = (
        (q["high"] < q[["open", "close", "low"]].max(axis=1))
        | (q["low"] > q[["open", "close", "high"]].min(axis=1))
        | (q[["open", "high", "low", "close"]] <= 0).any(axis=1)
    )
    if bad_ohlc.any():
        raise RuntimeError(f"{roll}_BAD_OHLC_ROWS:{int(bad_ohlc.sum())}")
    if (q["volume"] < 0).any():
        raise RuntimeError(f"{roll}_NEGATIVE_VOLUME_ROWS:{int((q['volume'] < 0).sum())}")

    # Every root must have usable history in 2022, 2023 and 2024.
    q["year"] = q["ts_event"].dt.year
    for sym, g in q.groupby("symbol"):
        years = set(g["year"].unique())
        miss_years = {2022, 2023, 2024} - years
        if miss_years:
            raise RuntimeError(f"{sym}_MISSING_YEARS:{sorted(miss_years)}")

    q = q.sort_values(["symbol", "ts_event"]).reset_index(drop=True)
    return q

def archive_csv_gz(q: pd.DataFrame, roll: str) -> Path:
    path = OUT / f"databento_glbx_ohlcv1h_{roll}_2022_2024.csv.gz"
    export = q.drop(columns=["year"])
    with gzip.open(path, "wt", encoding="utf-8", newline="") as f:
        export.to_csv(f, index=False)
    return path

def main():
    key = os.environ.get("DATABENTO_API_KEY", "").strip()
    if not key:
        raise RuntimeError("DATABENTO_API_KEY_MISSING")

    import databento as db
    client = db.Historical(key)

    cost_by_roll = {}
    requests = {}
    for roll in ROLLS:
        symbols = [f"{root}.{roll}.0" for root in ROOTS]
        req = dict(
            dataset=DATASET,
            schema=SCHEMA,
            symbols=symbols,
            stype_in="continuous",
            start=START,
            end=END,
        )
        cost_by_roll[roll] = float(client.metadata.get_cost(**req))
        requests[roll] = req

    total_cost = float(sum(cost_by_roll.values()))
    if total_cost > MAX_COST_USD:
        raise RuntimeError(f"COST_CAP_EXCEEDED estimated={total_cost:.6f} cap={MAX_COST_USD:.2f}")

    sym = client.symbology.resolve(
        dataset=DATASET,
        symbols=[f"{root}.{roll}.0" for root in ROOTS for roll in ROLLS],
        stype_in="continuous",
        stype_out="instrument_id",
        start_date=START,
        end_date=END,
    )
    sym_payload = serialize_obj(sym)
    sym_path = OUT / "databento_continuous_symbology_2022_2024.json"
    sym_path.write_text(json.dumps(sym_payload, indent=2, default=str) + "\n", encoding="utf-8")

    archives = {}
    coverage_rows = []

    for roll in ROLLS:
        store = client.timeseries.get_range(**requests[roll])
        q = validate_and_normalize(store, roll)
        p = archive_csv_gz(q, roll)

        symbol_stats = {}
        for sym_name, g in q.groupby("symbol", sort=True):
            yr = {
                str(int(y)): {
                    "rows": int(len(gg)),
                    "first": gg["ts_event"].min().isoformat(),
                    "last": gg["ts_event"].max().isoformat(),
                    "instrument_ids": sorted(int(x) for x in gg["instrument_id"].unique()),
                }
                for y, gg in g.groupby("year", sort=True)
            }
            symbol_stats[sym_name] = {
                "rows": int(len(g)),
                "first": g["ts_event"].min().isoformat(),
                "last": g["ts_event"].max().isoformat(),
                "years": yr,
            }
            for y, gg in g.groupby("year", sort=True):
                coverage_rows.append({
                    "roll": roll,
                    "symbol": sym_name,
                    "year": int(y),
                    "rows": int(len(gg)),
                    "first_ts_utc": gg["ts_event"].min().isoformat(),
                    "last_ts_utc": gg["ts_event"].max().isoformat(),
                    "instrument_id_count": int(gg["instrument_id"].nunique()),
                })

        archives[roll] = {
            "file": p.name,
            "sha256": sha256(p),
            "bytes": int(p.stat().st_size),
            "rows": int(len(q)),
            "first": q["ts_event"].min().isoformat(),
            "last": q["ts_event"].max().isoformat(),
            "duplicate_ts_symbol": 0,
            "bad_ohlc_rows": 0,
            "negative_volume_rows": 0,
            "symbols": symbol_stats,
        }

    coverage = pd.DataFrame(coverage_rows).sort_values(["roll", "symbol", "year"])
    coverage_path = OUT / "databento_raw_archive_coverage_2022_2024.csv"
    coverage.to_csv(coverage_path, index=False)

    summary = {
        "status": "DATABENTO_RAW_ARCHIVE_2022_2024_COMPLETE",
        "purpose": "Raw governed CME/Globex hourly archive only; no model fitting or derived state reuse.",
        "dataset": DATASET,
        "schema": SCHEMA,
        "window": [START, END],
        "roots": ROOTS,
        "rolls": ROLLS,
        "symbols": [f"{root}.{roll}.0" for root in ROOTS for roll in ROLLS],
        "estimated_cost_usd": total_cost,
        "cost_by_roll_usd": cost_by_roll,
        "cost_cap_usd": MAX_COST_USD,
        "symbology_file": sym_path.name,
        "symbology_sha256": sha256(sym_path),
        "coverage_file": coverage_path.name,
        "coverage_sha256": sha256(coverage_path),
        "archives": archives,
        "clock_contract": {
            "raw_timestamp": "Databento ts_event retained in UTC",
            "feature_availability": "For ohlcv-1h, model feature use must treat a bar as available only after that hourly bar has completed; exact per-model t_ready <= target_start is a separate gate.",
            "continuous_rolls": "c/n/v are all archived. No roll rule is selected by outcome performance.",
        },
        "guardrails": [
            "No historical FEATURE_PANEL/PREDICTIONS/STATE/SCORES used.",
            "No model fit performed.",
            "No outcome labels used to choose continuous roll.",
            "Archive contains vendor hourly OHLCV plus continuous symbol and instrument_id for raw reconstruction.",
        ],
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": summary["status"],
        "estimated_cost_usd": total_cost,
        "cost_by_roll_usd": cost_by_roll,
        "archives": {k: {"rows": v["rows"], "sha256": v["sha256"], "bytes": v["bytes"]} for k, v in archives.items()},
    }, indent=2))

if __name__ == "__main__":
    main()
