from __future__ import annotations

import os
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parent
PATCH = ROOT / "schema_patch_r2_6.sql"


def db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL is not set")
    return value


def main() -> int:
    sql = PATCH.read_text(encoding="utf-8")
    if not sql.strip():
        raise RuntimeError("schema patch is empty")

    with psycopg.connect(db_url(), autocommit=False) as conn:
        with conn.cursor() as cur:
            # Explicit simple-query mode permits the audited multi-statement SQL
            # patch while retaining a single transaction and rollback on failure.
            cur.execute(sql, prepare=False)
        conn.commit()

    print("GOLD_DATA_R2.6 schema patch: APPLIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
