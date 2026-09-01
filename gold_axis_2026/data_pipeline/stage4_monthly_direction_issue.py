from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
R4_SRC = ROOT / "r4_1" / "src"
sys.path.insert(0, str(R4_SRC))

from gold_r4.monthly import three_month_direction  # noqa: E402

SERIES_ID = "XAU_EOD_TWELVE_NY17"
QUALITY_INPUT = "APPROVED_CANONICAL_TWELVE_NY17"
FEATURE_NAME = "MONTHLY_DIRECTION_3M"
FEATURE_VERSION = "R4_1_3M_SIMPLE_RETURN_V1"
TARGET_CONTEXT = "2026-09"
EVIDENCE_CLASS = "LATE_BOOTSTRAP_SHADOW_CONTEXT"
REQUIRED_MONTHS = ("2026-05", "2026-06", "2026-07", "2026-08")


def _git_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def _select_inputs(cur, calc_ts: datetime):
    cur.execute(
        """
        SELECT id, series_id, observation_ts, value, source, source_symbol,
               available_as_of, retrieved_at, lineage_id, quality_status
        FROM observations_as_of(%s)
        WHERE series_id=%s AND quality_status=%s
          AND observation_ts >= timestamptz '2026-05-01 00:00:00+00'
          AND observation_ts <  timestamptz '2026-09-01 23:59:59+00'
        ORDER BY observation_ts, retrieved_at, id
        """,
        (calc_ts, SERIES_ID, QUALITY_INPUT),
    )
    rows = [dict(r) for r in cur.fetchall()]
    if not rows:
        raise RuntimeError("MONTHLY_DIRECTION_ISSUE_NO_CANONICAL_INPUTS")

    lineages = sorted({r["lineage_id"] for r in rows})
    sources = sorted({r["source"] for r in rows})
    if len(lineages) != 1:
        raise RuntimeError(f"MONTHLY_DIRECTION_ISSUE_LINEAGE_COUNT:{len(lineages)}")
    if sources != ["Twelve Data"]:
        raise RuntimeError("MONTHLY_DIRECTION_ISSUE_SOURCE_MISMATCH")

    month_rows: dict[str, dict] = {}
    for r in rows:
        if r["available_as_of"] > calc_ts or r["retrieved_at"] > calc_ts:
            raise RuntimeError("MONTHLY_DIRECTION_ISSUE_PIT_VIOLATION")
        key = r["observation_ts"].astimezone(timezone.utc).strftime("%Y-%m")
        if key in REQUIRED_MONTHS:
            current = month_rows.get(key)
            if current is None or r["observation_ts"] > current["observation_ts"]:
                month_rows[key] = r

    missing = [m for m in REQUIRED_MONTHS if m not in month_rows]
    if missing:
        raise RuntimeError("MONTHLY_DIRECTION_ISSUE_MISSING_MONTHS:" + ",".join(missing))

    ordered = [month_rows[m] for m in REQUIRED_MONTHS]
    prices = [float(r["value"]) for r in ordered]
    if any(not (x > 0) for x in prices):
        raise RuntimeError("MONTHLY_DIRECTION_ISSUE_INVALID_LEVEL")
    completed_returns = [prices[i] / prices[i - 1] - 1.0 for i in range(1, len(prices))]
    direction = three_month_direction(completed_returns).value
    return ordered, lineages[0], completed_returns, direction


def _input_fingerprint(ordered, lineage_id: str) -> str:
    payload = {
        "series_id": SERIES_ID,
        "feature_name": FEATURE_NAME,
        "feature_version": FEATURE_VERSION,
        "target_context": TARGET_CONTEXT,
        "required_months": list(REQUIRED_MONTHS),
        "input_ids": [int(r["id"]) for r in ordered],
        "input_observation_ts": [r["observation_ts"].isoformat() for r in ordered],
        "input_available_as_of": [r["available_as_of"].isoformat() for r in ordered],
        "lineage_id": lineage_id,
        "return_definition": "simple_close_to_close_monthly_return",
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--persist", action="store_true")
    args = p.parse_args()

    calc_ts = datetime.now(timezone.utc)
    git_commit = _git_commit()
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            # The context must not be issued before DB-level immutability exists.
            cur.execute(
                """
                select count(distinct trigger_name) as n
                from information_schema.triggers
                where event_object_schema='public'
                  and event_object_table='derived_feature_snapshots'
                  and trigger_name='trg_derived_feature_snapshots_immutable'
                """
            )
            if int(cur.fetchone()["n"]) != 1:
                raise RuntimeError("DERIVED_FEATURE_IMMUTABILITY_GUARD_NOT_ACTIVE")

            ordered, lineage_id, completed_returns, direction = _select_inputs(cur, calc_ts)
            fingerprint = _input_fingerprint(ordered, lineage_id)
            input_cutoff = max(r["available_as_of"] for r in ordered)
            return_signs = ["POS" if r > 0 else "NEG" if r < 0 else "ZERO" for r in completed_returns]

            cur.execute(
                """
                select id, value_text, metadata
                from derived_feature_snapshots
                where feature_name=%s and feature_version=%s
                  and metadata->>'target_context'=%s
                  and metadata->>'evidence_class'=%s
                order by calculation_ts desc, id desc
                """,
                (FEATURE_NAME, FEATURE_VERSION, TARGET_CONTEXT, EVIDENCE_CLASS),
            )
            existing = cur.fetchall()
            if existing:
                row = dict(existing[0])
                old_fp = (row.get("metadata") or {}).get("input_fingerprint")
                if row["value_text"] == direction and old_fp == fingerprint:
                    conn.rollback()
                    print(json.dumps({
                        "status": "IDEMPOTENT_EXISTING",
                        "row_id": int(row["id"]),
                        "target_context": TARGET_CONTEXT,
                        "direction": direction,
                        "input_fingerprint": fingerprint,
                        "raw_market_values_logged": False,
                        "prospective_h1_claim": False,
                    }, indent=2))
                    print("MONTHLY_DIRECTION_LATE_BOOTSTRAP_ISSUE_PASS")
                    return 0
                raise RuntimeError("CONFLICT_EXISTING_BOOTSTRAP_CONTEXT")

            input_lineage = {
                "series_id": SERIES_ID,
                "source": "Twelve Data",
                "lineage_id": lineage_id,
                "selected_input_ids": [int(r["id"]) for r in ordered],
                "selected_observation_ts": [r["observation_ts"].isoformat() for r in ordered],
                "selected_available_as_of": [r["available_as_of"].isoformat() for r in ordered],
                "return_definition": "simple_close_to_close_monthly_return",
                "input_fingerprint": fingerprint,
            }
            metadata = {
                "target_context": TARGET_CONTEXT,
                "evidence_class": EVIDENCE_CLASS,
                "manifest_contract": "GOLD_CONTROL_PROJECT_MANIFEST.md v1.9 prospective-origin cutoff",
                "prospective_h1_claim": False,
                "h1_forecast_blocker_closed": False,
                "late_bootstrap_reason": "SEPTEMBER_2026_H1_PROSPECTIVE_ORIGIN_MISSED",
                "required_months": list(REQUIRED_MONTHS),
                "selected_observation_dates": [r["observation_ts"].date().isoformat() for r in ordered],
                "return_signs": return_signs,
                "input_fingerprint": fingerprint,
                "raw_market_values_logged": False,
            }

            if not args.persist:
                conn.rollback()
                print(json.dumps({
                    "status": "DRY_RUN_PASS",
                    "target_context": TARGET_CONTEXT,
                    "direction": direction,
                    "input_cutoff": input_cutoff.isoformat(),
                    "selected_input_ids": [int(r["id"]) for r in ordered],
                    "selected_observation_dates": [r["observation_ts"].date().isoformat() for r in ordered],
                    "input_fingerprint": fingerprint,
                    "raw_market_values_logged": False,
                    "database_writes": "NONE",
                    "prospective_h1_claim": False,
                }, indent=2))
                print("MONTHLY_DIRECTION_LATE_BOOTSTRAP_DRY_RUN_PASS")
                return 0

            cur.execute(
                """
                insert into derived_feature_snapshots
                  (feature_name, feature_version, calculation_ts, input_cutoff,
                   value_text, git_commit, input_lineage, quality_status, metadata)
                values (%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s::jsonb)
                returning id
                """,
                (
                    FEATURE_NAME, FEATURE_VERSION, calc_ts, input_cutoff,
                    direction, git_commit, json.dumps(input_lineage), EVIDENCE_CLASS, json.dumps(metadata),
                ),
            )
            row_id = int(cur.fetchone()["id"])
        conn.commit()

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute(
                """
                select id, feature_name, feature_version, calculation_ts, input_cutoff,
                       value_text, git_commit, quality_status, metadata
                from derived_feature_snapshots where id=%s
                """,
                (row_id,),
            )
            verified = dict(cur.fetchone())
        conn.rollback()
    if verified["quality_status"] != EVIDENCE_CLASS or verified["value_text"] != direction:
        raise RuntimeError("MONTHLY_DIRECTION_POST_COMMIT_VERIFY_FAILED")

    print(json.dumps({
        "status": "INSERTED_VERIFIED",
        "row_id": row_id,
        "target_context": TARGET_CONTEXT,
        "direction": direction,
        "calculation_ts": calc_ts.isoformat(),
        "input_cutoff": input_cutoff.isoformat(),
        "git_commit": git_commit,
        "quality_status": EVIDENCE_CLASS,
        "selected_input_ids": [int(r["id"]) for r in ordered],
        "selected_observation_dates": [r["observation_ts"].date().isoformat() for r in ordered],
        "input_fingerprint": fingerprint,
        "raw_market_values_logged": False,
        "prospective_h1_claim": False,
        "h1_forecast_blocker_closed": False,
    }, indent=2))
    print("MONTHLY_DIRECTION_LATE_BOOTSTRAP_ISSUE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
