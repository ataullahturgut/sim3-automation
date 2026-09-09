from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo
from datetime import datetime, time

NY = ZoneInfo("America/New_York")
NY17 = time(17, 0)
ACCEPTED_TIME = "16:59:00"
EVIDENCE_CLASS = "HISTORICAL_REPLAY_RECONSTRUCTION"
NY17_LANE_ID = "XAU_EOD_TWELVE_NY17_HISTORICAL_REPLAY_V145"
GVZ_LANE_ID = "GVZ_CBOE_HISTORICAL_REPLAY_V145"
ALLOWED_FINAL = {"VALID_EXACT_BAR", "PROVIDER_NO_BAR"}
BLOCKING = {
    "ENTITLEMENT_BLOCKED",
    "AUTHENTICATION_ERROR",
    "INVALID_REQUEST",
    "SERVER_ERROR",
    "MALFORMED_BAR",
    "REQUEST_ERROR",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in fields})


def parse_json_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(x) for x in value]
    if value in (None, ""):
        return []
    parsed = json.loads(str(value))
    if not isinstance(parsed, list):
        raise ValueError("IMPACTED_READINESS_CELLS_NOT_LIST")
    return [str(x) for x in parsed]


def finite_positive(value: Any, field: str, trade_date: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"NY17_{field.upper()}_PARSE_FAIL:{trade_date}") from exc
    if not math.isfinite(out) or out <= 0:
        raise ValueError(f"NY17_{field.upper()}_NOT_POSITIVE_FINITE:{trade_date}")
    return out


def validate_ny17_probe(
    inventory_rows: list[dict[str, str]], probe: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    candidates = [r for r in inventory_rows if r.get("gap_action") != "NO_WRITE_ALREADY_CANONICAL"]
    expected_dates = [r["trade_date"] for r in candidates]
    expected_set = set(expected_dates)
    if len(expected_dates) != len(expected_set):
        raise ValueError("NY17_INVENTORY_DUPLICATE_TRADE_DATE")

    rows = probe.get("rows")
    if probe.get("probe_id") != "GOLD_CONTROL_HISTORICAL_NY17_EXACT_DATE_PROBE_V145":
        raise ValueError("NY17_PROBE_ID_MISMATCH")
    if probe.get("production_write") != "NONE":
        raise ValueError("NY17_PROBE_PRODUCTION_WRITE_NOT_NONE")
    if not isinstance(rows, list):
        raise ValueError("NY17_PROBE_ROWS_MISSING")

    by_date: dict[str, dict[str, Any]] = {}
    for row in rows:
        d = str(row.get("trade_date") or "")
        if d in by_date:
            raise ValueError(f"NY17_PROBE_DUPLICATE_TRADE_DATE:{d}")
        by_date[d] = row

    missing = sorted(expected_set - set(by_date))
    extra = sorted(set(by_date) - expected_set)
    if missing or extra:
        raise ValueError(f"NY17_PROBE_COVERAGE_MISMATCH:missing={len(missing)}:extra={len(extra)}")

    inventory_map = {r["trade_date"]: r for r in candidates}
    valid_rows: list[dict[str, Any]] = []
    no_bar_rows: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()

    for d in expected_dates:
        row = by_date[d]
        status = str(row.get("acquisition_status") or "NOT_PROVEN")
        counts[status] += 1
        if status not in ALLOWED_FINAL:
            if status in BLOCKING or status == "NOT_PROVEN":
                continue
            raise ValueError(f"NY17_UNKNOWN_STATUS:{d}:{status}")

        common = {
            "artifact_lane_id": NY17_LANE_ID,
            "governed_source_series_id": "XAU_EOD_TWELVE_NY17",
            "trade_date": d,
            "provider": row.get("provider"),
            "symbol": row.get("symbol"),
            "interval": row.get("interval"),
            "timezone": row.get("timezone"),
            "accepted_source_time": row.get("accepted_source_time"),
            "stored_semantic": row.get("stored_semantic"),
            "evidence_class": EVIDENCE_CLASS,
            "prospective_claim": False,
            "retrieved_at": row.get("retrieved_at"),
            "payload_sha256": row.get("payload_sha256"),
            "impacted_readiness_cells": json.dumps(
                parse_json_list(row.get("impacted_readiness_cells") or inventory_map[d].get("impacted_readiness_cells")),
                separators=(",", ":"),
            ),
        }

        if common["provider"] != "Twelve Data" or common["symbol"] != "XAU/USD":
            raise ValueError(f"NY17_SOURCE_IDENTITY_MISMATCH:{d}")
        if common["interval"] != "1min" or common["timezone"] != "America/New_York":
            raise ValueError(f"NY17_SOURCE_SEMANTIC_MISMATCH:{d}")
        if common["accepted_source_time"] != ACCEPTED_TIME or common["stored_semantic"] != "17:00 ET":
            raise ValueError(f"NY17_TIME_SEMANTIC_MISMATCH:{d}")

        if status == "PROVIDER_NO_BAR":
            no_bar_rows.append({**common, "acquisition_status": status, "provider_code": row.get("provider_code"), "provider_message": row.get("provider_message")})
            continue

        if not common["retrieved_at"] or not common["payload_sha256"]:
            raise ValueError(f"NY17_LINEAGE_MISSING:{d}")
        if len(str(common["payload_sha256"])) != 64:
            raise ValueError(f"NY17_PAYLOAD_HASH_INVALID:{d}")
        source_dt = str(row.get("source_bar_datetime") or "")
        if not source_dt.endswith(f" {ACCEPTED_TIME}") or not source_dt.startswith(d):
            raise ValueError(f"NY17_SOURCE_BAR_DATETIME_MISMATCH:{d}:{source_dt}")
        o = finite_positive(row.get("open"), "open", d)
        h = finite_positive(row.get("high"), "high", d)
        l = finite_positive(row.get("low"), "low", d)
        c = finite_positive(row.get("close"), "close", d)
        if h < max(o, l, c) or l > min(o, h, c):
            raise ValueError(f"NY17_OHLC_RANGE_INVALID:{d}")
        cutoff = datetime.combine(datetime.fromisoformat(d).date(), NY17, tzinfo=NY).astimezone(ZoneInfo("UTC"))
        valid_rows.append({
            **common,
            "acquisition_status": status,
            "source_bar_datetime": source_dt,
            "observation_ts_utc": cutoff.isoformat(),
            "open": o,
            "high": h,
            "low": l,
            "close": c,
        })

    blocker_count = sum(v for k, v in counts.items() if k not in ALLOWED_FINAL)
    if blocker_count:
        summary = ",".join(f"{k}={v}" for k, v in sorted(counts.items()) if k not in ALLOWED_FINAL)
        raise RuntimeError(f"BLOCKED_DATA:NY17_EXACT_PROBE_INCOMPLETE:{summary}")
    return valid_rows, no_bar_rows, dict(sorted(counts.items()))


def validate_gvz(gvz_rows: list[dict[str, str]], summary: dict[str, Any]) -> list[dict[str, Any]]:
    source = summary["gvz"]["official_source"]
    if summary["gvz"].get("series_id") != "GVZ_CBOE":
        raise ValueError("GVZ_SOURCE_IDENTITY_MISMATCH")
    expected = int(summary["gvz"]["missing_rows_to_write"])
    rows = [r for r in gvz_rows if r.get("gap_action") == "CONTROLLED_HISTORICAL_RECONSTRUCTION_WRITE_REQUIRED"]
    if len(rows) != expected:
        raise ValueError(f"GVZ_ROW_COUNT_MISMATCH:{len(rows)}:{expected}")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        d = row["observation_date"]
        if d in seen:
            raise ValueError(f"GVZ_DUPLICATE_DATE:{d}")
        seen.add(d)
        value = finite_positive(row["value"], "gvz", d)
        if row.get("acquisition_status") != "AVAILABLE":
            raise ValueError(f"GVZ_NOT_AVAILABLE:{d}")
        out.append({
            "artifact_lane_id": GVZ_LANE_ID,
            "governed_source_series_id": "GVZ_CBOE",
            "observation_date": d,
            "value": value,
            "provider": "Cboe",
            "source_url": source["source_url"],
            "source_payload_sha256": source["payload_sha256"],
            "source_retrieved_at": source["retrieved_at"],
            "evidence_class": EVIDENCE_CLASS,
            "prospective_claim": False,
            "impacted_readiness_cells": row.get("impacted_readiness_cells") or "[]",
        })
    return out


def build(args: argparse.Namespace) -> dict[str, Any]:
    inventory_path = Path(args.ny_inventory)
    probe_path = Path(args.ny_probe)
    gvz_path = Path(args.gvz_inventory)
    gap_summary_path = Path(args.gap_summary)

    inventory_rows = read_csv(inventory_path)
    probe = json.loads(probe_path.read_text(encoding="utf-8"))
    gvz_rows = read_csv(gvz_path)
    gap_summary = json.loads(gap_summary_path.read_text(encoding="utf-8"))

    ny_valid, ny_no_bar, ny_counts = validate_ny17_probe(inventory_rows, probe)
    gvz_valid = validate_gvz(gvz_rows, gap_summary)

    out_dir = Path(args.output_dir)
    ny_valid_path = out_dir / "historical_ny17_replay_lane_v145.csv"
    ny_no_bar_path = out_dir / "historical_ny17_no_bar_adjudications_v145.csv"
    gvz_valid_path = out_dir / "historical_gvz_replay_lane_v145.csv"

    ny_valid_fields = [
        "artifact_lane_id", "governed_source_series_id", "trade_date", "observation_ts_utc",
        "source_bar_datetime", "open", "high", "low", "close", "provider", "symbol", "interval",
        "timezone", "accepted_source_time", "stored_semantic", "retrieved_at", "payload_sha256",
        "evidence_class", "prospective_claim", "impacted_readiness_cells",
    ]
    ny_no_bar_fields = [
        "artifact_lane_id", "governed_source_series_id", "trade_date", "provider", "symbol", "interval",
        "timezone", "accepted_source_time", "stored_semantic", "retrieved_at", "payload_sha256",
        "provider_code", "provider_message", "acquisition_status", "evidence_class", "prospective_claim",
        "impacted_readiness_cells",
    ]
    gvz_fields = [
        "artifact_lane_id", "governed_source_series_id", "observation_date", "value", "provider",
        "source_url", "source_payload_sha256", "source_retrieved_at", "evidence_class", "prospective_claim",
        "impacted_readiness_cells",
    ]
    write_csv(ny_valid_path, ny_valid, ny_valid_fields)
    write_csv(ny_no_bar_path, ny_no_bar, ny_no_bar_fields)
    write_csv(gvz_valid_path, gvz_valid, gvz_fields)

    inputs = {
        "ny_inventory": {"path": str(inventory_path), "sha256": sha256_file(inventory_path)},
        "ny_probe": {"path": str(probe_path), "sha256": sha256_file(probe_path)},
        "gvz_inventory": {"path": str(gvz_path), "sha256": sha256_file(gvz_path)},
        "gap_summary": {"path": str(gap_summary_path), "sha256": sha256_file(gap_summary_path)},
    }
    outputs = {
        "ny17_valid": {"path": str(ny_valid_path), "rows": len(ny_valid), "sha256": sha256_file(ny_valid_path)},
        "ny17_no_bar": {"path": str(ny_no_bar_path), "rows": len(ny_no_bar), "sha256": sha256_file(ny_no_bar_path)},
        "gvz_valid": {"path": str(gvz_valid_path), "rows": len(gvz_valid), "sha256": sha256_file(gvz_valid_path)},
    }
    manifest = {
        "bundle_id": "GOLD_CONTROL_HISTORICAL_RECONSTRUCTION_BUNDLE_V145",
        "status": "PASS",
        "storage": "IMMUTABLE_GITHUB_ARTIFACT_LANES",
        "production_database_write": "NONE",
        "performance_scoring": False,
        "prospective_claim": False,
        "ny17_lane_id": NY17_LANE_ID,
        "gvz_lane_id": GVZ_LANE_ID,
        "ny17_status_counts": ny_counts,
        "inputs": inputs,
        "outputs": outputs,
    }
    manifest_path = out_dir / "historical_reconstruction_bundle_v145.json"
    write_json(manifest_path, manifest)
    manifest["manifest_sha256"] = sha256_file(manifest_path)
    return manifest


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    audits = root / "gold_axis_2026/data_pipeline/audits"
    parser = argparse.ArgumentParser()
    parser.add_argument("--ny-inventory", default=str(audits / "historical_ny17_gap_inventory_v145.csv"))
    parser.add_argument("--ny-probe", default=str(audits / "historical_ny17_exact_date_probe_v145.json"))
    parser.add_argument("--gvz-inventory", default=str(audits / "historical_gvz_gap_inventory_v145.csv"))
    parser.add_argument("--gap-summary", default=str(audits / "historical_gap_inventory_v145.json"))
    parser.add_argument("--output-dir", default=str(audits / "historical_reconstruction_bundle_v145"))
    args = parser.parse_args()
    try:
        result = build(args)
    except RuntimeError as exc:
        print(str(exc))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
