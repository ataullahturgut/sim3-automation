from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import psycopg

import vw_midas_msvr_successor_v1 as base

SCHEMA_VERSION = "GOLD_MONTHLY_DEV_SNAPSHOT_V1_2026-09-28"
DEV_START, DEV_END = "2022-04", "2024-12"
DEV_ORIGIN_START, DEV_ORIGIN_END = "2022-03", "2024-11"
HARD_CUTOFF = datetime(2025, 1, 1, tzinfo=timezone.utc)

METALS = base.METALS
DAILY_SERIES = base.DAILY_SERIES
CORE_GOLD = base.CORE_GOLD
GPR_PIT = base.GPR_PIT


def canonical_bytes(obj) -> bytes:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def read_invariants(cur) -> dict:
    return base.authority_invariants(cur)


def export_payload(dsn: str) -> tuple[dict, dict]:
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            invariants = read_invariants(cur)

            cur.execute(
                "SELECT observation_ts,value FROM observations "
                "WHERE series_id=%s AND observation_ts < %s ORDER BY observation_ts",
                (CORE_GOLD, HARD_CUTOFF),
            )
            core_gold = {base.month_key(ts): float(v) for ts, v in cur.fetchall()}
            if not core_gold:
                raise RuntimeError("SNAPSHOT_CORE_GOLD_EMPTY")

            raw = {m: {} for m in METALS}
            for metal, sid in DAILY_SERIES.items():
                cur.execute(
                    "SELECT observation_ts,value FROM observations "
                    "WHERE series_id=%s AND observation_ts < %s ORDER BY observation_ts",
                    (sid, HARD_CUTOFF),
                )
                for ts, value in cur.fetchall():
                    raw[metal][ts.date()] = float(value)

            common_dates = sorted(set.intersection(*(set(raw[m]) for m in METALS)))
            if not common_dates:
                raise RuntimeError("SNAPSHOT_NO_COMMON_DAILY_METAL_ROWS")

            daily_common_rows = [
                {
                    "date": d.isoformat(),
                    **{m: float(raw[m][d]) for m in METALS},
                }
                for d in common_dates
            ]

            daily_month_values = {m: defaultdict(list) for m in METALS}
            for d in common_dates:
                mk = f"{d.year:04d}-{d.month:02d}"
                for m in METALS:
                    daily_month_values[m][mk].append(float(raw[m][d]))

            monthly_metal = {
                m: {
                    k: float(np.asarray(v, dtype=float).mean())
                    for k, v in vv.items()
                }
                for m, vv in daily_month_values.items()
            }

            cur.execute(
                "SELECT observation_ts,value,available_as_of,metadata->>'origin_month' "
                "FROM observations "
                "WHERE series_id=%s "
                "AND metadata->>'origin_month' >= %s "
                "AND metadata->>'origin_month' <= %s "
                "ORDER BY metadata->>'origin_month',observation_ts",
                (GPR_PIT, DEV_ORIGIN_START, DEV_ORIGIN_END),
            )
            vintages = defaultdict(dict)
            availability = {}
            for ts, value, available_as_of, origin_month in cur.fetchall():
                if not origin_month:
                    continue
                vintages[origin_month][base.month_key(ts)] = float(value)
                prev = availability.get(origin_month)
                if prev is None or available_as_of < prev:
                    availability[origin_month] = available_as_of

            required = [
                base.month_shift(t, -1)
                for t in base.month_range(DEV_START, DEV_END)
            ]
            missing = [m for m in required if m not in vintages]
            late = [
                m
                for m in required
                if availability.get(m) is None
                or availability[m] > base.month_end_utc(m)
            ]
            missing_lag = [
                m
                for m in required
                if m in vintages and base.month_shift(m, -1) not in vintages[m]
            ]

            checks = {
                "core_gold_rows_loaded": len(core_gold),
                "core_gold_first_loaded": min(core_gold),
                "core_gold_last_loaded": max(core_gold),
                "common_daily_rows_loaded": len(common_dates),
                "common_daily_first_loaded": common_dates[0].isoformat(),
                "common_daily_last_loaded": common_dates[-1].isoformat(),
                "metal_months_loaded": {m: len(monthly_metal[m]) for m in METALS},
                "gpr_origin_vintages_loaded": len(vintages),
                "gpr_origin_first_loaded": min(vintages),
                "gpr_origin_last_loaded": max(vintages),
                "missing_required_gpr_origins": missing,
                "late_required_gpr_origins": late,
                "missing_required_gpr_lag_month": missing_lag,
                "hard_cutoff_exclusive": HARD_CUTOFF.isoformat(),
                "modeling_rows_2025_loaded": 0,
                "modeling_rows_2026_loaded": 0,
            }

            if missing or late or missing_lag:
                raise RuntimeError(f"SNAPSHOT_GPR_PIT_SOURCE_GATE_FAIL {checks}")
            if max(core_gold) > DEV_END:
                raise RuntimeError(
                    f"SNAPSHOT_POST_DEV_CORE_GOLD_LOADED max={max(core_gold)}"
                )
            if common_dates[-1] >= HARD_CUTOFF.date():
                raise RuntimeError("SNAPSHOT_POST_DEV_DAILY_METAL_LOADED")
            if max(vintages) > DEV_ORIGIN_END:
                raise RuntimeError("SNAPSHOT_POST_DEV_GPR_VINTAGE_LOADED")

            payload = {
                "authority": {
                    "database_access": "READ_ONLY",
                    "neon_is_authority": True,
                    "snapshot_role": "EXECUTION_CACHE_ONLY",
                    "dev_start": DEV_START,
                    "dev_end": DEV_END,
                    "dev_origin_start": DEV_ORIGIN_START,
                    "dev_origin_end": DEV_ORIGIN_END,
                    "hard_cutoff_exclusive": HARD_CUTOFF.isoformat(),
                    "series": {
                        "core_gold": CORE_GOLD,
                        "daily_metals": dict(DAILY_SERIES),
                        "gpr_pit": GPR_PIT,
                    },
                },
                "authority_invariants": invariants,
                "source_checks": checks,
                "core_gold": {k: core_gold[k] for k in sorted(core_gold)},
                "daily_common_rows": daily_common_rows,
                "gpr_vintages": {
                    origin: {
                        "available_as_of_min": availability[origin].isoformat()
                        if availability.get(origin) is not None
                        else None,
                        "history": {
                            k: vintages[origin][k]
                            for k in sorted(vintages[origin])
                        },
                    }
                    for origin in sorted(vintages)
                },
            }

            after = read_invariants(cur)
            if after != invariants:
                raise RuntimeError(
                    f"SNAPSHOT_AUTHORITY_INVARIANTS_CHANGED before={invariants} after={after}"
                )

            export_gate = {
                "read_only": True,
                "authority_invariants_unchanged": after == invariants,
                "no_2025_modeling_rows": checks["modeling_rows_2025_loaded"] == 0,
                "no_2026_modeling_rows": checks["modeling_rows_2026_loaded"] == 0,
                "core_gold_max_le_dev_end": max(core_gold) <= DEV_END,
                "daily_max_before_2025": common_dates[-1] < HARD_CUTOFF.date(),
                "gpr_origin_max_le_2024_11": max(vintages) <= DEV_ORIGIN_END,
                "gpr_pit_complete": not missing and not late and not missing_lag,
            }
            if not all(export_gate.values()):
                raise RuntimeError(f"SNAPSHOT_EXPORT_GATE_FAIL {export_gate}")

            return payload, export_gate


def write_snapshot(dsn: str, output: str, manifest_output: str) -> dict:
    payload, export_gate = export_payload(dsn)
    payload_sha = sha256_bytes(canonical_bytes(payload))
    doc = {
        "schema_version": SCHEMA_VERSION,
        "payload_sha256": payload_sha,
        "payload": payload,
    }
    raw = (
        json.dumps(doc, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")
    Path(output).write_bytes(raw)
    file_sha = sha256_bytes(raw)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "snapshot_file": Path(output).name,
        "payload_sha256": payload_sha,
        "file_sha256": file_sha,
        "exported_at_utc": datetime.now(timezone.utc).isoformat(),
        "export_gate": export_gate,
        "source_checks": payload["source_checks"],
        "authority_invariants": payload["authority_invariants"],
        "counts": {
            "core_gold_months": len(payload["core_gold"]),
            "common_daily_rows": len(payload["daily_common_rows"]),
            "gpr_origin_vintages": len(payload["gpr_vintages"]),
        },
    }
    Path(manifest_output).write_text(
        json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def load_snapshot(path: str) -> tuple[base.DataBundle, dict]:
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if doc.get("schema_version") != SCHEMA_VERSION:
        raise RuntimeError(
            f"SNAPSHOT_SCHEMA_MISMATCH got={doc.get('schema_version')}"
        )
    payload = doc["payload"]
    expected = doc["payload_sha256"]
    actual = sha256_bytes(canonical_bytes(payload))
    if actual != expected:
        raise RuntimeError(
            f"SNAPSHOT_PAYLOAD_HASH_FAIL expected={expected} actual={actual}"
        )

    checks = payload["source_checks"]
    if checks["modeling_rows_2025_loaded"] != 0:
        raise RuntimeError("SNAPSHOT_2025_ROWS_PRESENT")
    if checks["modeling_rows_2026_loaded"] != 0:
        raise RuntimeError("SNAPSHOT_2026_ROWS_PRESENT")
    if checks["core_gold_last_loaded"] > DEV_END:
        raise RuntimeError("SNAPSHOT_CORE_GOLD_AFTER_DEV")
    if checks["common_daily_last_loaded"] >= "2025-01-01":
        raise RuntimeError("SNAPSHOT_DAILY_AFTER_DEV")
    if checks["gpr_origin_last_loaded"] > DEV_ORIGIN_END:
        raise RuntimeError("SNAPSHOT_GPR_ORIGIN_AFTER_DEV")
    if (
        checks["missing_required_gpr_origins"]
        or checks["late_required_gpr_origins"]
        or checks["missing_required_gpr_lag_month"]
    ):
        raise RuntimeError("SNAPSHOT_GPR_SOURCE_CHECK_NOT_CLEAN")

    rows = payload["daily_common_rows"]
    daily_month_values = {m: defaultdict(list) for m in METALS}
    for row in rows:
        mk = row["date"][:7]
        for m in METALS:
            daily_month_values[m][mk].append(float(row[m]))
    daily_month_values = {
        m: {
            k: np.asarray(v, dtype=float)
            for k, v in vv.items()
        }
        for m, vv in daily_month_values.items()
    }
    monthly_metal = {
        m: {
            k: float(v.mean())
            for k, v in daily_month_values[m].items()
        }
        for m in METALS
    }
    gpr_vintages = {
        origin: {
            k: float(v)
            for k, v in item["history"].items()
        }
        for origin, item in payload["gpr_vintages"].items()
    }

    bundle = base.DataBundle(
        core_gold={k: float(v) for k, v in payload["core_gold"].items()},
        core_gpr={},
        daily_month_values=daily_month_values,
        monthly_metal=monthly_metal,
        gpr_vintages=gpr_vintages,
        source_checks=checks,
        invariants_before=payload["authority_invariants"],
    )
    meta = {
        "schema_version": doc["schema_version"],
        "payload_sha256": expected,
        "source_checks": checks,
        "authority_invariants": payload["authority_invariants"],
    }
    return bundle, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=("export", "verify"))
    ap.add_argument("--input")
    ap.add_argument("--output")
    ap.add_argument("--manifest-output")
    args = ap.parse_args()

    if args.mode == "export":
        dsn = os.environ.get("NEON_DATABASE_URL")
        if not dsn:
            raise SystemExit("NEON_DATABASE_URL required for export")
        if not args.output or not args.manifest_output:
            raise SystemExit("--output and --manifest-output required for export")
        manifest = write_snapshot(dsn, args.output, args.manifest_output)
        print("SNAPSHOT_EXPORT_GATE=PASS")
        print(json.dumps(manifest, sort_keys=True))
    else:
        if not args.input:
            raise SystemExit("--input required for verify")
        bundle, meta = load_snapshot(args.input)
        print("SNAPSHOT_VERIFY_GATE=PASS")
        print(
            json.dumps(
                {
                    **meta,
                    "core_gold_months": len(bundle.core_gold),
                    "common_daily_rows": meta["source_checks"]["common_daily_rows_loaded"],
                    "gpr_origin_vintages": len(bundle.gpr_vintages),
                },
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
