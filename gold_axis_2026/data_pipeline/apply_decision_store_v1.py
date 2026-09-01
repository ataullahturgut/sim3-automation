from __future__ import annotations

import os
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parent
PATCH = ROOT / "schema_patch_decision_store_v1.sql"
EXPECTED_SCHEMA_VERSION = "GOLD_CONTROL_DECISION_STORE_V1_2026-09-01"
EXPECTED_ACTION_STATUS = "NOT_PROVEN_POSITION_MAPPING"
TABLES = (
    "decision_runs",
    "decision_signal_snapshots",
    "decision_events",
)
VIEW = "latest_decision_snapshot_by_evidence"


def db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL is not set")
    return value


def _regclass(cur: psycopg.Cursor, name: str) -> str | None:
    cur.execute("SELECT to_regclass(%s)::text", (f"public.{name}",))
    row = cur.fetchone()
    return row[0] if row else None


def _metadata(cur: psycopg.Cursor, key: str) -> str | None:
    cur.execute("SELECT value FROM system_metadata WHERE key = %s", (key,))
    row = cur.fetchone()
    return row[0] if row else None


def main() -> int:
    sql = PATCH.read_text(encoding="utf-8")
    if not sql.strip():
        raise RuntimeError("decision-store schema patch is empty")

    with psycopg.connect(db_url(), autocommit=False) as conn:
        with conn.cursor() as cur:
            existing_tables = {name: _regclass(cur, name) is not None for name in TABLES}
            existing_view = _regclass(cur, VIEW) is not None
            current_version = _metadata(cur, "decision_store_schema_version")

            present_count = sum(existing_tables.values()) + int(existing_view)
            if present_count not in (0, len(TABLES) + 1):
                raise RuntimeError(
                    "PARTIAL_DECISION_STORE_SCHEMA_PRESENT: refusing production migration"
                )
            if present_count and current_version != EXPECTED_SCHEMA_VERSION:
                raise RuntimeError(
                    "UNEXPECTED_DECISION_STORE_VERSION: refusing production migration"
                )

            # Exact versioned SQL is executed as one transaction. Any failure rolls back.
            cur.execute(sql, prepare=False)

            missing = [name for name in TABLES if _regclass(cur, name) is None]
            if _regclass(cur, VIEW) is None:
                missing.append(VIEW)
            if missing:
                raise RuntimeError(f"POST_MIGRATION_OBJECTS_MISSING: {missing}")

            version = _metadata(cur, "decision_store_schema_version")
            action_status = _metadata(cur, "decision_action_mapping_status")
            if version != EXPECTED_SCHEMA_VERSION:
                raise RuntimeError(
                    f"SCHEMA_VERSION_MISMATCH: expected={EXPECTED_SCHEMA_VERSION} got={version}"
                )
            if action_status != EXPECTED_ACTION_STATUS:
                raise RuntimeError(
                    f"ACTION_MAPPING_STATUS_MISMATCH: expected={EXPECTED_ACTION_STATUS} got={action_status}"
                )

            counts: dict[str, int] = {}
            for table in TABLES:
                cur.execute(f"SELECT count(*) FROM {table}")
                row = cur.fetchone()
                counts[table] = int(row[0]) if row else -1
            if any(count != 0 for count in counts.values()):
                raise RuntimeError(
                    f"DECISION_STORE_NOT_EMPTY_BEFORE_WRITER_ACTIVATION: {counts}"
                )

        conn.commit()

    canonical_ref = os.environ.get("GOLD_CONTROL_CANONICAL_REF", "UNSET")
    print(
        "GOLD_CONTROL_STAGE3_PRODUCTION_MIGRATION_PASS "
        f"schema_version={EXPECTED_SCHEMA_VERSION} "
        f"action_mapping={EXPECTED_ACTION_STATUS} "
        f"canonical_ref={canonical_ref} "
        "decision_rows=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
