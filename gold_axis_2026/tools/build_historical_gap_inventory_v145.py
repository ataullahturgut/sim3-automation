from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import copy
import urllib.request
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


CBOE_GVZ_URL = "https://cdn.cboe.com/api/global/us_indices/daily_prices/GVZ_History.csv"
PILOT_MONTHS = tuple([f"2025-{m:02d}" for m in range(1, 13)] + [f"2026-{m:02d}" for m in range(1, 9)])
NY17_ENGINES = ("MONTHLY_DIRECTION_3M", "FAST", "SLOW", "EMERGENCY_LEVEL", "EMERGENCY_REVERSAL")


def add_month(month: str, delta: int) -> str:
    y, m = map(int, month.split("-")); idx = y * 12 + m - 1 + delta
    return f"{idx // 12:04d}-{idx % 12 + 1:02d}"


def impacted_ny17_cells(trade_date: str) -> list[str]:
    month = trade_date[:7]; cells: set[str] = set()
    if month in PILOT_MONTHS:
        for engine in ("FAST", "SLOW", "EMERGENCY_LEVEL", "EMERGENCY_REVERSAL"):
            cells.add(f"{engine}:{month}")
    for delta in range(1, 5):
        target = add_month(month, delta)
        if target in PILOT_MONTHS: cells.add(f"MONTHLY_DIRECTION_3M:{target}")
    # The frozen tactical lookbacks can carry a late-month gap into the next target month.
    next_month = add_month(month, 1)
    if next_month in PILOT_MONTHS:
        cells.add(f"FAST:{next_month}"); cells.add(f"SLOW:{next_month}")
    return sorted(cells)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_cboe_gvz() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    request = urllib.request.Request(CBOE_GVZ_URL, headers={"User-Agent": "GoldControl-V145-HistoricalReadiness/1.0"})
    retrieved_at = datetime.now(timezone.utc).isoformat()
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read()
        content_type = response.headers.get("Content-Type")
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    rows: list[dict[str, Any]] = []
    for row in reader:
        raw_date = (row.get("DATE") or row.get("Date") or "").strip()
        if not raw_date: continue
        parsed = datetime.strptime(raw_date, "%m/%d/%Y").date()
        if date(2025, 1, 1) <= parsed <= date(2026, 8, 31):
            close = float((row.get("GVZ") or row.get("CLOSE") or row.get("Close") or "nan").strip())
            if not (close > 0): raise RuntimeError(f"INVALID_GVZ_CLOSE:{parsed}")
            rows.append({"observation_date": parsed.isoformat(), "value": close})
    dates = [r["observation_date"] for r in rows]
    if len(dates) != len(set(dates)): raise RuntimeError("DUPLICATE_OFFICIAL_CBOE_GVZ_DATE")
    return rows, {"source_url": CBOE_GVZ_URL, "retrieved_at": retrieved_at, "payload_sha256": hashlib.sha256(raw).hexdigest(), "content_type": content_type, "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION", "prospective_claim": False}


def build_inventory(ny_source: dict[str, Any], gvz_production: dict[str, Any]) -> dict[str, Any]:
    ny_rows: list[dict[str, Any]] = []
    for row in ny_source["rows"]:
        canonical = int(row["canonical_n"]) == 1
        if canonical:
            action = "NO_WRITE_ALREADY_CANONICAL"
        elif row["acquisition_status"] == "AVAILABLE":
            action = "EXACT_OHLC_REPROBE_REQUIRED_BEFORE_CONTROLLED_WRITE"
        else:
            action = "EXACT_DATE_PROVIDER_PROBE_REQUIRED"
        ny_rows.append({**row, "gap_action": action, "impacted_readiness_cells": impacted_ny17_cells(row["trade_date"])})

    official, cboe_evidence = fetch_cboe_gvz()
    production_dates = {r["observation_date"] for r in gvz_production["rows"]}
    gvz_rows: list[dict[str, Any]] = []
    for row in official:
        month = row["observation_date"][:7]
        if row["observation_date"] in production_dates:
            status, action = "AVAILABLE", "NO_WRITE_ALREADY_PRESENT"
        else:
            status, action = "AVAILABLE", "CONTROLLED_HISTORICAL_RECONSTRUCTION_WRITE_REQUIRED"
        gvz_rows.append({**row, "acquisition_status": status, "gap_action": action,
                          "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION", "prospective_claim": False,
                          "impacted_readiness_cells": [f"GVZ_RISK:{month}"] if month in PILOT_MONTHS else []})

    missing_gvz = [r for r in gvz_rows if r["gap_action"].endswith("WRITE_REQUIRED")]
    gvz_by_month = Counter(r["observation_date"][:7] for r in missing_gvz)
    ny_counts = Counter(r["gap_action"] for r in ny_rows)
    ny_status = Counter(r["acquisition_status"] for r in ny_rows if r["gap_action"] != "NO_WRITE_ALREADY_CANONICAL")
    cells: dict[str, set[str]] = defaultdict(set)
    for row in ny_rows:
        if row["gap_action"] != "NO_WRITE_ALREADY_CANONICAL":
            for cell in row["impacted_readiness_cells"]: cells[cell].add(row["trade_date"])
    for row in missing_gvz:
        for cell in row["impacted_readiness_cells"]: cells[cell].add(row["observation_date"])
    return {
        "inventory_id": "GOLD_CONTROL_HISTORICAL_GAP_INVENTORY_V145",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "performance_scoring": False, "production_write": "NONE", "auto_selector": "OFF", "auto_ensemble": "OFF",
        "ny17": {
            "series_id": "XAU_EOD_TWELVE_NY17", "provider": "Twelve Data", "symbol": "XAU/USD", "interval": "1min",
            "timezone": "America/New_York", "accepted_source_time": "16:59:00", "stored_semantic": "17:00 ET",
            "fallback": "NONE", "interpolation": "FORBIDDEN", "forward_fill": "FORBIDDEN", "synthetic_bar": "FORBIDDEN",
            "candidate_calendar_dates": len(ny_rows), "already_canonical_dates": ny_counts["NO_WRITE_ALREADY_CANONICAL"],
            "candidate_dates_requiring_probe_or_upgrade": len(ny_rows) - ny_counts["NO_WRITE_ALREADY_CANONICAL"],
            "candidate_status_counts": dict(ny_status),
            "write_count": "NOT_PROVEN_UNTIL_EXACT_DATE_PROBES_COMPLETE",
            "write_target": "SEPARATELY_IDENTIFIABLE_HISTORICAL_RECONSTRUCTION_LANE_SERIES_ID_NOT_YET_FROZEN",
            "rows": ny_rows,
        },
        "gvz": {
            "series_id": "GVZ_CBOE", "official_source": cboe_evidence,
            "official_rows_in_pilot": len(gvz_rows), "production_distinct_dates": len(production_dates),
            "missing_rows_to_write": len(missing_gvz), "missing_start": missing_gvz[0]["observation_date"] if missing_gvz else None,
            "missing_end": missing_gvz[-1]["observation_date"] if missing_gvz else None,
            "missing_by_month": dict(sorted(gvz_by_month.items())),
            "write_target": "observations / GVZ_CBOE",
            "quality_status": "HISTORICAL_REPLAY_RECONSTRUCTION_OFFICIAL_CBOE",
            "rows": gvz_rows,
        },
        "readiness_cell_date_dependencies": {k: sorted(v) for k, v in sorted(cells.items())},
    }


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields); writer.writeheader()
        for row in rows:
            flat = {k: row.get(k) for k in fields}
            for k, v in flat.items():
                if isinstance(v, (list, dict)): flat[k] = json.dumps(v, sort_keys=True, separators=(",", ":"))
            writer.writerow(flat)


def main() -> int:
    parser = argparse.ArgumentParser()
    root = Path(__file__).resolve().parents[2]
    parser.add_argument("--ny-source", default=str(root / "gold_axis_2026/data_pipeline/audits/historical_ny17_gap_inventory_source_v145.json"))
    parser.add_argument("--gvz-production", default=str(root / "gold_axis_2026/data_pipeline/audits/historical_gvz_production_source_v145.json"))
    parser.add_argument("--out-json", default=str(root / "gold_axis_2026/data_pipeline/audits/historical_gap_inventory_v145.json"))
    parser.add_argument("--ny-csv", default=str(root / "gold_axis_2026/data_pipeline/audits/historical_ny17_gap_inventory_v145.csv"))
    parser.add_argument("--gvz-csv", default=str(root / "gold_axis_2026/data_pipeline/audits/historical_gvz_gap_inventory_v145.csv"))
    args = parser.parse_args()
    inventory = build_inventory(load_json(Path(args.ny_source)), load_json(Path(args.gvz_production)))
    summary = copy.deepcopy(inventory)
    summary["ny17"].pop("rows")
    summary["gvz"].pop("rows")
    dependencies = summary.pop("readiness_cell_date_dependencies")
    summary["readiness_cell_dependency_counts"] = {cell: len(dates) for cell, dates in dependencies.items()}
    summary["row_artifacts"] = {
        "ny17": Path(args.ny_csv).name,
        "gvz": Path(args.gvz_csv).name,
    }
    Path(args.out_json).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(Path(args.ny_csv), inventory["ny17"]["rows"], ["trade_date", "acquisition_status", "evidence_status", "canonical_n", "cache_exact_n", "exact_close", "lineage_id", "retrieved_at", "gap_action", "impacted_readiness_cells"])
    write_csv(Path(args.gvz_csv), inventory["gvz"]["rows"], ["observation_date", "value", "acquisition_status", "gap_action", "evidence_class", "prospective_claim", "impacted_readiness_cells"])
    print(json.dumps({"ny17": {k: inventory["ny17"][k] for k in ("already_canonical_dates", "candidate_dates_requiring_probe_or_upgrade", "candidate_status_counts", "write_count")}, "gvz": {k: inventory["gvz"][k] for k in ("official_rows_in_pilot", "production_distinct_dates", "missing_rows_to_write", "missing_start", "missing_end", "missing_by_month")}}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
