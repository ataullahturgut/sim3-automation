from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

TRANCHES = [
    ("2024_JAN_AUG", date(2024, 1, 1), date(2024, 8, 31)),
    ("2023_FULL", date(2023, 1, 1), date(2023, 12, 31)),
    ("2022_FULL", date(2022, 1, 1), date(2022, 12, 31)),
    ("2021_NOV_DEC", date(2021, 11, 1), date(2021, 12, 31)),
]


def build_inventory(path: Path, start: date, end: date) -> int:
    rows = []
    d = start
    while d <= end:
        rows.append(
            {
                "trade_date": d.isoformat(),
                "gap_action": "EXACT_DATE_PROVIDER_PROBE_REQUIRED",
                "impacted_readiness_cells": json.dumps(
                    [f"GC_BREAK_WP1_FORMATION:{d:%Y-%m}"], separators=(",", ":")
                ),
            }
        )
        d += timedelta(days=1)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["trade_date", "gap_action", "impacted_readiness_cells"],
        )
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pacing-seconds", type=float, default=8.5)
    parser.add_argument("--output-dir", default="formation_ny17_v1")
    args = parser.parse_args()

    if not os.environ.get("TWELVE_DATA_API_KEY", "").strip():
        raise SystemExit("BLOCKED_DATA:TWELVE_DATA_API_KEY_NOT_SET")

    root = Path(__file__).resolve().parents[2]
    probe = root / "gold_axis_2026/tools/probe_historical_ny17_gaps_v145.py"
    if not probe.exists():
        raise SystemExit(f"PROBE_NOT_FOUND:{probe}")

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "audit_id": "GC_BREAK_WP1_FORMATION_NY17_BACKFILL_V1",
        "source_semantic": (
            "Twelve Data XAU/USD 1min exact 16:59:00 America/New_York; "
            "close after OHLC validation"
        ),
        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
        "prospective_claim": False,
        "production_database_write": "NONE",
        "performance_scoring": False,
        "pacing_seconds": args.pacing_seconds,
        "tranches": {},
    }

    for name, start, end in TRANCHES:
        inv = out_dir / f"{name}_inventory.csv"
        out_json = out_dir / f"{name}_probe.json"
        out_csv = out_dir / f"{name}_probe.csv"
        candidate_dates = build_inventory(inv, start, end)
        print(
            json.dumps(
                {
                    "tranche": name,
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "candidate_dates": candidate_dates,
                },
                sort_keys=True,
            ),
            flush=True,
        )

        cmd = [
            sys.executable,
            str(probe),
            "--inventory",
            str(inv),
            "--pacing-seconds",
            str(args.pacing_seconds),
            "--out-json",
            str(out_json),
            "--out-csv",
            str(out_csv),
        ]
        subprocess.run(cmd, check=True)

        payload = json.loads(out_json.read_text(encoding="utf-8"))
        counts = Counter(row["acquisition_status"] for row in payload["rows"])
        summary["tranches"][name] = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "rows": payload["row_count"],
            "status_counts": dict(counts),
            "probe_json_sha256": sha256(out_json),
            "probe_csv_sha256": sha256(out_csv),
            "inventory_sha256": sha256(inv),
        }
        print(
            json.dumps(
                {
                    "tranche": name,
                    "row_count": payload["row_count"],
                    "status_counts": dict(counts),
                    "production_write": payload["production_write"],
                    "performance_scoring": payload["performance_scoring"],
                },
                sort_keys=True,
            ),
            flush=True,
        )

    summary_path = out_dir / "gc_break_wp1_formation_ny17_backfill_v1_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
