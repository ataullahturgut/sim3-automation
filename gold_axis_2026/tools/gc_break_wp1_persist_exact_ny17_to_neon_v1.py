from __future__ import annotations

import argparse
import json
import sys
import uuid
from dataclasses import asdict
from datetime import datetime, time, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PIPELINE = ROOT / "data_pipeline"
if str(DATA_PIPELINE) not in sys.path:
    sys.path.insert(0, str(DATA_PIPELINE))

import collector_r2 as base  # noqa: E402
from persist_neon import _db_url, persist_bundle  # noqa: E402

SERIES_ID = "XAU_EOD_TWELVE_NY17"
SOURCE = "Twelve Data"
SYMBOL = "XAU/USD"
QUALITY_STATUS = "APPROVED_CANONICAL_TWELVE_NY17"
NY = ZoneInfo("America/New_York")
PREHISTORY_START = pd.Timestamp("2021-09-01")
FORMATION_END = pd.Timestamp("2024-12-31")
FINAL_STATUSES = {"VALID_EXACT_BAR", "PROVIDER_NO_BAR"}
PIPELINE_VERSION = "GC_BREAK_WP1_EXACT_NY17_NEON_PERSIST_V1"


def _parse_retrieved_at(value: str) -> datetime:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        raise RuntimeError(f"RETRIEVED_AT_NOT_TZ_AWARE:{value}")
    return ts.tz_convert("UTC").to_pydatetime()


def _validate_inputs(exact_csv: Path, closure_audit: Path) -> pd.DataFrame:
    audit = json.loads(closure_audit.read_text(encoding="utf-8"))
    if audit.get("audit_id") != "GC_BREAK_WP1_MANIFEST_CLOSURE_AUDIT_V1":
        raise RuntimeError("CLOSURE_AUDIT_ID_MISMATCH")
    if audit.get("status") != "PASS":
        raise RuntimeError("CLOSURE_AUDIT_NOT_PASS")
    if int(audit.get("unresolved_rows", -1)) != 0:
        raise RuntimeError("CLOSURE_AUDIT_UNRESOLVED_NONZERO")

    d = pd.read_csv(exact_csv, dtype=str, keep_default_na=False)
    required = {
        "trade_date", "acquisition_status", "provider", "symbol", "interval",
        "timezone", "accepted_source_time", "source_bar_datetime", "retrieved_at",
        "payload_sha256", "evidence_class", "prospective_claim",
        "open", "high", "low", "close",
    }
    if not required <= set(d.columns):
        raise RuntimeError(f"EXACT_SCHEMA_MISSING:{sorted(required-set(d.columns))}")

    d["trade_date"] = pd.to_datetime(d["trade_date"]).dt.normalize()
    expected = pd.date_range(PREHISTORY_START, FORMATION_END, freq="D")
    if set(d["trade_date"]) != set(expected) or len(d) != len(expected):
        raise RuntimeError(f"EXACT_CALENDAR_COVERAGE_FAIL:got={len(d)}:expected={len(expected)}")
    if d["trade_date"].duplicated().any():
        raise RuntimeError("EXACT_DUPLICATE_TRADE_DATE")
    if not set(d["acquisition_status"]) <= FINAL_STATUSES:
        raise RuntimeError("EXACT_UNRESOLVED_ROWS_PRESENT")

    valid = d[d["acquisition_status"].eq("VALID_EXACT_BAR")].copy()
    if valid.empty:
        raise RuntimeError("EXACT_NO_VALID_ROWS")
    bindings = {
        "provider": SOURCE,
        "symbol": SYMBOL,
        "interval": "1min",
        "timezone": "America/New_York",
        "accepted_source_time": "16:59:00",
        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
    }
    for col, wanted in bindings.items():
        if set(valid[col]) != {wanted}:
            raise RuntimeError(f"EXACT_BINDING_FAIL:{col}:{sorted(set(valid[col]))}")
    if valid["prospective_claim"].str.lower().ne("false").any():
        raise RuntimeError("EXACT_PROSPECTIVE_CLAIM_FAIL")
    for col in ("source_bar_datetime", "retrieved_at", "payload_sha256"):
        if valid[col].str.strip().eq("").any():
            raise RuntimeError(f"EXACT_LINEAGE_MISSING:{col}")

    for col in ("open", "high", "low", "close"):
        valid[col] = pd.to_numeric(valid[col], errors="raise")
    arr = valid[["open", "high", "low", "close"]].to_numpy(float)
    if not np.isfinite(arr).all() or (arr <= 0).any():
        raise RuntimeError("EXACT_NONFINITE_OR_NONPOSITIVE_OHLC")
    if (valid["high"] < valid[["open", "low", "close"]].max(axis=1)).any():
        raise RuntimeError("EXACT_HIGH_RANGE_FAIL")
    if (valid["low"] > valid[["open", "high", "close"]].min(axis=1)).any():
        raise RuntimeError("EXACT_LOW_RANGE_FAIL")
    return valid.sort_values("trade_date").reset_index(drop=True)


def _bundle(valid: pd.DataFrame) -> dict:
    run_started = datetime.now(timezone.utc)
    run_id = str(uuid.uuid4())
    observations = []
    for row in valid.itertuples(index=False):
        trade_date = pd.Timestamp(row.trade_date).date()
        cutoff_ny = datetime.combine(trade_date, time(17, 0), tzinfo=NY)
        cutoff_utc = cutoff_ny.astimezone(timezone.utc)
        retrieved_at = _parse_retrieved_at(str(row.retrieved_at))
        if retrieved_at < cutoff_utc:
            raise RuntimeError(f"RETRIEVAL_BEFORE_SESSION_CUTOFF:{trade_date}")
        observations.append(asdict(base.make_obs(
            run_id,
            SERIES_ID,
            cutoff_utc,
            float(row.close),
            SOURCE,
            SYMBOL,
            "trade_date_daily",
            "USD/troy_oz",
            retrieved_at,
            provider_as_of=cutoff_utc,
            available_as_of=retrieved_at,
            status=QUALITY_STATUS,
            payload_hash=str(row.payload_sha256),
            metadata={
                "endpoint": "https://api.twelvedata.com/time_series",
                "vendor_symbol": SYMBOL,
                "provider_interval": "1min",
                "requested_timezone": "America/New_York",
                "trade_date": trade_date.isoformat(),
                "trade_date_boundary": "17:00 ET",
                "source_bar_open_time": str(row.source_bar_datetime),
                "accepted_source_time": "16:59:00",
                "price_field": "close",
                "open": float(row.open),
                "high": float(row.high),
                "low": float(row.low),
                "close": float(row.close),
                "availability_policy": "historical_retrieval_time_floor",
                "fallback_policy": "NONE",
                "interpolation": "FORBIDDEN",
                "forward_fill": "FORBIDDEN",
                "retrieval_window_start": getattr(row, "retrieval_window_start", None),
                "retrieval_window_end": getattr(row, "retrieval_window_end", None),
                "retrieval_mode": getattr(row, "retrieval_mode", None),
                "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
                "prospective_claim": False,
                "wp1_manifest_scope": "2021-09-01_through_2024-12-31",
            },
        )))

    return {
        "run_id": run_id,
        "started_at": base.iso_utc(run_started),
        "finished_at": base.iso_utc(datetime.now(timezone.utc)),
        "pipeline_version": PIPELINE_VERSION,
        "mode": "backfill:gc_break_wp1_exact_ny17_audited",
        "observations": observations,
        "vintages": [],
        "quality_events": [],
    }


def _verify(expected_valid: int) -> dict:
    import psycopg

    start_utc = datetime(2021, 9, 1, 0, 0, tzinfo=timezone.utc)
    end_utc = datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)
    with psycopg.connect(_db_url(), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select count(*), count(distinct observation_ts),
                       min(observation_ts), max(observation_ts),
                       count(*) filter (where source<>%s or source_symbol<>%s or quality_status<>%s)
                from canonical_latest
                where series_id=%s and observation_ts >= %s and observation_ts < %s
                """,
                (SOURCE, SYMBOL, QUALITY_STATUS, SERIES_ID, start_utc, end_utc),
            )
            n, distinct_n, min_ts, max_ts, bad_lineage = cur.fetchone()
            if int(n) != expected_valid or int(distinct_n) != expected_valid:
                raise RuntimeError(
                    f"NEON_CANONICAL_COUNT_MISMATCH:rows={n}:distinct={distinct_n}:expected={expected_valid}"
                )
            if int(bad_lineage) != 0:
                raise RuntimeError(f"NEON_CANONICAL_LINEAGE_MISMATCH:{bad_lineage}")
            cur.execute(
                """
                select count(*)
                from canonical_latest
                where series_id=%s and observation_ts >= %s and observation_ts < %s
                  and available_as_of < provider_as_of
                """,
                (SERIES_ID, start_utc, end_utc),
            )
            bad_chronology = int(cur.fetchone()[0])
            if bad_chronology:
                raise RuntimeError(f"NEON_CANONICAL_CHRONOLOGY_FAIL:{bad_chronology}")
    return {
        "series_id": SERIES_ID,
        "expected_valid_rows": expected_valid,
        "verified_rows": int(n),
        "distinct_observation_ts": int(distinct_n),
        "min_observation_ts": min_ts.isoformat() if min_ts else None,
        "max_observation_ts": max_ts.isoformat() if max_ts else None,
        "lineage_mismatch_rows": int(bad_lineage),
        "chronology_violations": bad_chronology,
        "status": "PASS",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--exact-csv", type=Path, required=True)
    p.add_argument("--closure-audit", type=Path, required=True)
    p.add_argument("--persist", action="store_true")
    a = p.parse_args()

    valid = _validate_inputs(a.exact_csv, a.closure_audit)
    print(json.dumps({
        "audit_id": "GC_BREAK_WP1_EXACT_NY17_NEON_PERSIST_PREFLIGHT_V1",
        "status": "PASS",
        "valid_exact_rows": int(len(valid)),
        "calendar_start": PREHISTORY_START.date().isoformat(),
        "calendar_end": FORMATION_END.date().isoformat(),
        "database_write_requested": bool(a.persist),
    }, indent=2, sort_keys=True))
    if not a.persist:
        return 0

    bundle = _bundle(valid)
    result = persist_bundle(bundle)
    verified = _verify(len(valid))
    print(json.dumps({"persist": result, "verify": verified}, indent=2, sort_keys=True))
    if result.get("status") != "SUCCESS" or verified.get("status") != "PASS":
        return 1
    print("GC_BREAK_WP1_EXACT_NY17_NEON_PERSIST_SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
