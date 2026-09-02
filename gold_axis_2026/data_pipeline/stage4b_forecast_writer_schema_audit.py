from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "stage4b" / "forecast_writer_schema_evidence.json"
TABLES = ("forecast_input_snapshots", "derived_feature_snapshots", "monthly_forecast_contracts")


def jsonable(v):
    if v is None or isinstance(v, (str, int, float, bool)):
        return v
    if hasattr(v, "isoformat"):
        return v.isoformat()
    return str(v)


def main() -> int:
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_MISSING")

    evidence = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
        "raw_market_values_logged": False,
        "database_write": "NONE",
        "tables": {},
    }

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute("select current_database() as database_name, current_setting('server_version') as server_version")
            evidence["database"] = {k: jsonable(v) for k, v in dict(cur.fetchone()).items()}

            for table in TABLES:
                cur.execute("select to_regclass(%s) as reg", (f"public.{table}",))
                row = cur.fetchone()
                if not row or row["reg"] is None:
                    evidence["tables"][table] = {"exists": False}
                    continue

                cur.execute(
                    """
                    select ordinal_position, column_name, data_type, is_nullable,
                           column_default, is_identity, identity_generation
                    from information_schema.columns
                    where table_schema='public' and table_name=%s
                    order by ordinal_position
                    """,
                    (table,),
                )
                columns = [{k: jsonable(v) for k, v in dict(r).items()} for r in cur.fetchall()]

                cur.execute(
                    """
                    select c.conname, c.contype, pg_get_constraintdef(c.oid) as definition
                    from pg_constraint c
                    join pg_class t on t.oid=c.conrelid
                    join pg_namespace n on n.oid=t.relnamespace
                    where n.nspname='public' and t.relname=%s
                    order by c.contype, c.conname
                    """,
                    (table,),
                )
                constraints = [{k: jsonable(v) for k, v in dict(r).items()} for r in cur.fetchall()]

                cur.execute(
                    """
                    select indexname, indexdef
                    from pg_indexes
                    where schemaname='public' and tablename=%s
                    order by indexname
                    """,
                    (table,),
                )
                indexes = [{k: jsonable(v) for k, v in dict(r).items()} for r in cur.fetchall()]

                cur.execute(
                    """
                    select tgname, pg_get_triggerdef(oid) as definition
                    from pg_trigger
                    where tgrelid=%s::regclass and not tgisinternal
                    order by tgname
                    """,
                    (f"public.{table}",),
                )
                triggers = [{k: jsonable(v) for k, v in dict(r).items()} for r in cur.fetchall()]

                cur.execute("select pg_get_serial_sequence(%s, 'id') as serial_sequence", (f"public.{table}",))
                seq = cur.fetchone()["serial_sequence"]

                cur.execute(f'SELECT count(*) AS row_count, max(id) AS max_id FROM "{table}"')
                counts = dict(cur.fetchone())

                id_col = next((c for c in columns if c["column_name"] == "id"), None)
                pk = [c for c in constraints if c["contype"] == "p"]
                unique = [c for c in constraints if c["contype"] == "u"]
                immutable = [t for t in triggers if "immutable" in str(t["tgname"]).lower()]
                evidence["tables"][table] = {
                    "exists": True,
                    "columns": columns,
                    "constraints": constraints,
                    "indexes": indexes,
                    "triggers": triggers,
                    "serial_sequence": jsonable(seq),
                    "row_count": int(counts["row_count"]),
                    "max_id": None if counts["max_id"] is None else int(counts["max_id"]),
                    "id_column": id_col,
                    "primary_key_count": len(pk),
                    "unique_constraint_count": len(unique),
                    "immutable_trigger_count": len(immutable),
                }
        conn.rollback()

    required = [evidence["tables"].get(t, {}) for t in TABLES]
    passed = bool(
        all(x.get("exists") for x in required)
        and all(x.get("primary_key_count", 0) >= 1 for x in required)
        and all(x.get("immutable_trigger_count", 0) >= 1 for x in required)
        and evidence["tables"]["forecast_input_snapshots"].get("row_count") == 0
        and evidence["tables"]["monthly_forecast_contracts"].get("row_count") == 0
    )
    evidence["schema_audit_pass"] = passed
    evidence["decision"] = "FORECAST_WRITER_SCHEMA_AUDIT_PASS" if passed else "BLOCKED_FORECAST_WRITER_SCHEMA_NOT_PROVEN"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")

    for table in TABLES:
        t = evidence["tables"][table]
        print(f"TABLE_{table.upper()}_EXISTS={str(t.get('exists', False)).lower()}")
        if t.get("exists"):
            print(f"TABLE_{table.upper()}_ROWS={t['row_count']}")
            print(f"TABLE_{table.upper()}_PK_COUNT={t['primary_key_count']}")
            print(f"TABLE_{table.upper()}_UNIQUE_COUNT={t['unique_constraint_count']}")
            print(f"TABLE_{table.upper()}_IMMUTABLE_TRIGGER_COUNT={t['immutable_trigger_count']}")
            print(f"TABLE_{table.upper()}_ID_DEFAULT_PRESENT={str(bool((t.get('id_column') or {}).get('column_default'))).lower()}")
            print(f"TABLE_{table.upper()}_ID_IDENTITY={str((t.get('id_column') or {}).get('is_identity'))}")
            print(f"TABLE_{table.upper()}_SERIAL_SEQUENCE_PRESENT={str(bool(t.get('serial_sequence'))).lower()}")
    print(f"FORECAST_WRITER_SCHEMA_AUDIT_PASS={str(passed).lower()}")
    print("RAW_MARKET_VALUES_LOGGED=NO")
    print("DATABASE_WRITES=NONE")
    return 0 if passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
