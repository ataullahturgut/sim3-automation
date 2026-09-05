from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

from persist_neon import persist_bundle

CONTRACT_PATH = Path(__file__).with_name("source_contract_gpr_pit_v2.json")
SERIES_ID = "GPR_OFFICIAL_GIT_PIT"
AUTH_TOKEN = "MANIFEST_V1_33_GPR_PIT_DATA_PLANE"
CANONICAL_BRANCH = "gold-r4-direction-engine"
REQUIRED_VINTAGES = 54

DECISION_TABLES = (
    "monthly_forecast_contracts",
    "decision_signal_snapshots",
    "decision_runs",
    "decision_events",
)


def db_url() -> str:
    v = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not v:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    return v


def require_canonical_authority() -> None:
    if os.environ.get("GPR_PIT_PRODUCTION_WRITE_AUTHORIZED", "").strip() != AUTH_TOKEN:
        raise RuntimeError("GPR_PIT_PRODUCTION_WRITE_NOT_AUTHORIZED")
    ref = os.environ.get("GITHUB_REF_NAME", "").strip()
    if ref and ref != CANONICAL_BRANCH:
        raise RuntimeError(f"GPR_PIT_WRITE_REQUIRES_CANONICAL_BRANCH:{ref}")
    manifest_version = os.environ.get("GOLD_CONTROL_MANIFEST_VERSION", "").strip()
    if manifest_version != "1.33":
        raise RuntimeError(f"GPR_PIT_WRITE_REQUIRES_MANIFEST_1_33:{manifest_version or 'MISSING'}")


def load_contract() -> dict:
    payload = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    spec = payload.get("series", {}).get(SERIES_ID)
    if not isinstance(spec, dict):
        raise RuntimeError("GPR_PIT_SOURCE_CONTRACT_MISSING")
    if spec.get("required_origin_count") != REQUIRED_VINTAGES:
        raise RuntimeError("GPR_PIT_SOURCE_CONTRACT_REQUIRED_COUNT_MISMATCH")
    return spec


def load_bundle(path: Path) -> dict:
    bundle = json.loads(path.read_text(encoding="utf-8"))
    if bundle.get("evidence_class") != "HISTORICAL_REPLAY_RECONSTRUCTION":
        raise RuntimeError("GPR_PIT_BUNDLE_EVIDENCE_CLASS_INVALID")
    if bundle.get("quality_events"):
        raise RuntimeError(f"GPR_PIT_BUNDLE_HAS_QUALITY_EVENTS:{len(bundle['quality_events'])}")
    vintages = bundle.get("vintages") or []
    if len(vintages) != REQUIRED_VINTAGES:
        raise RuntimeError(f"GPR_PIT_BUNDLE_VINTAGE_COUNT:{len(vintages)}/{REQUIRED_VINTAGES}")
    observations = bundle.get("observations") or []
    if not observations:
        raise RuntimeError("GPR_PIT_BUNDLE_NO_OBSERVATIONS")
    bad_series = sorted({str(o.get("series_id")) for o in observations if o.get("series_id") != SERIES_ID})
    if bad_series:
        raise RuntimeError(f"GPR_PIT_BUNDLE_SERIES_MISMATCH:{bad_series}")
    if any(o.get("retrieved_at") != o.get("first_seen_at") for o in observations):
        raise RuntimeError("GPR_PIT_BUNDLE_FIRST_SEEN_RETRIEVAL_MISMATCH")
    if any((o.get("metadata") or {}).get("historical_reconstruction_not_original_retrieval") is not True for o in observations):
        raise RuntimeError("GPR_PIT_BUNDLE_RECONSTRUCTION_TRUTH_FLAG_MISSING")
    meta = bundle.get("metadata") or {}
    if meta.get("current_final_vintage_substitution_allowed") is not False:
        raise RuntimeError("GPR_PIT_FINAL_VINTAGE_SUBSTITUTION_NOT_LOCKED")
    # persist_neon derives write status from its own transaction; this field is evidence from the builder.
    meta["production_write"] = True
    meta["production_write_authority"] = AUTH_TOKEN
    bundle["metadata"] = meta
    return bundle


def source_registry_row(spec: dict) -> tuple:
    metadata = {k: v for k, v in spec.items() if k not in {
        "semantic", "source", "symbol", "tier", "frequency", "unit", "role", "status", "license_note"
    }}
    return (
        SERIES_ID,
        spec["semantic"],
        spec["source"],
        spec.get("symbol"),
        spec["tier"],
        spec["frequency"],
        spec.get("unit"),
        spec.get("role"),
        spec["status"],
        spec.get("license_note"),
        json.dumps(metadata),
    )


def decision_counts(conn) -> dict[str, int]:
    out: dict[str, int] = {}
    with conn.cursor(row_factory=dict_row) as cur:
        for table in DECISION_TABLES:
            cur.execute(f"select count(*)::bigint as n from {table}")
            out[table] = int(cur.fetchone()["n"])
    return out


def seed_registry(spec: dict) -> None:
    with psycopg.connect(db_url(), autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into source_registry
                (series_id, semantic_id, source_name, source_symbol, source_tier, frequency,
                 unit, model_role, status, license_note, metadata)
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
                on conflict (series_id) do update set
                  semantic_id=excluded.semantic_id,
                  source_name=excluded.source_name,
                  source_symbol=excluded.source_symbol,
                  source_tier=excluded.source_tier,
                  frequency=excluded.frequency,
                  unit=excluded.unit,
                  model_role=excluded.model_role,
                  status=excluded.status,
                  license_note=excluded.license_note,
                  metadata=excluded.metadata,
                  updated_at=now()
                """,
                source_registry_row(spec),
            )
        conn.commit()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--bundle", type=Path, required=True)
    args = p.parse_args()

    require_canonical_authority()
    spec = load_contract()
    bundle = load_bundle(args.bundle)

    with psycopg.connect(db_url()) as conn:
        before = decision_counts(conn)
    if any(before.values()):
        raise RuntimeError(f"DECISION_AUTHORITY_STORE_NOT_EMPTY_BEFORE_SOURCE_INGEST:{before}")

    seed_registry(spec)
    result = persist_bundle(bundle)

    with psycopg.connect(db_url()) as conn:
        after = decision_counts(conn)
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                select count(distinct (metadata->>'origin_month'))::bigint as origins,
                       count(*)::bigint as rows,
                       min(metadata->>'origin_month') as first_origin,
                       max(metadata->>'origin_month') as last_origin
                from observations
                where series_id=%s and quality_status='APPROVED_HISTORICAL_PIT_RECONSTRUCTION_RESEARCH'
                """,
                (SERIES_ID,),
            )
            coverage = dict(cur.fetchone())
            cur.execute("select count(*)::bigint as n from source_vintages where source_id like 'GPR_OFFICIAL_GIT_PIT_VINTAGE_%'")
            vintage_count = int(cur.fetchone()["n"])

    if after != before:
        raise RuntimeError(f"DECISION_AUTHORITY_STORE_CHANGED_DURING_SOURCE_INGEST:{before}->{after}")
    if int(coverage["origins"]) != REQUIRED_VINTAGES:
        raise RuntimeError(f"GPR_PIT_PRODUCTION_ORIGIN_COVERAGE:{coverage['origins']}/{REQUIRED_VINTAGES}")
    if vintage_count != REQUIRED_VINTAGES:
        raise RuntimeError(f"GPR_PIT_PRODUCTION_VINTAGES:{vintage_count}/{REQUIRED_VINTAGES}")

    print(json.dumps({
        "status": "SUCCESS",
        "series_id": SERIES_ID,
        "persist_result": result,
        "coverage": coverage,
        "source_vintages": vintage_count,
        "decision_counts_before": before,
        "decision_counts_after": after,
        "forecast_or_decision_write": False,
        "historical_reconstruction_only": True,
    }, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
