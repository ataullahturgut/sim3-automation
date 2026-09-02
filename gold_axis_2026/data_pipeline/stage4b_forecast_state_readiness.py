from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from psycopg.rows import dict_row


TABLES = (
    "forecast_input_snapshots",
    "derived_feature_snapshots",
    "monthly_forecast_contracts",
)
EXPECTED_TRIGGERS = {
    "forecast_input_snapshots": "trg_forecast_input_snapshots_immutable",
    "derived_feature_snapshots": "trg_derived_feature_snapshots_immutable",
    "monthly_forecast_contracts": "trg_monthly_forecast_contracts_immutable",
}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    args = p.parse_args()

    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")

    checked_at = datetime.now(timezone.utc)
    result: dict[str, object] = {
        "audit": "STAGE4B_FORECAST_STATE_READINESS_V1",
        "checked_at": checked_at.isoformat(),
        "database_writes": "NONE",
        "raw_market_values_logged": False,
        "tables": {},
        "triggers": {},
        "row_counts": {},
    }

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")

            cur.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema='public' AND table_name = ANY(%s)
                ORDER BY table_name
                """,
                (list(TABLES),),
            )
            found = {r["table_name"] for r in cur.fetchall()}
            missing = sorted(set(TABLES) - found)
            if missing:
                raise RuntimeError("FORECAST_STATE_TABLES_MISSING:" + ",".join(missing))

            for table in TABLES:
                cur.execute(
                    """
                    SELECT column_name, data_type, udt_name, is_nullable, column_default,
                           ordinal_position
                    FROM information_schema.columns
                    WHERE table_schema='public' AND table_name=%s
                    ORDER BY ordinal_position
                    """,
                    (table,),
                )
                cols = [dict(r) for r in cur.fetchall()]
                if not cols:
                    raise RuntimeError(f"FORECAST_STATE_COLUMNS_MISSING:{table}")
                result["tables"][table] = cols

                cur.execute(f'SELECT count(*) AS n FROM public."{table}"')
                result["row_counts"][table] = int(cur.fetchone()["n"])

                cur.execute(
                    """
                    SELECT trigger_name, event_manipulation, action_timing
                    FROM information_schema.triggers
                    WHERE event_object_schema='public' AND event_object_table=%s
                    ORDER BY trigger_name, event_manipulation
                    """,
                    (table,),
                )
                triggers = [dict(r) for r in cur.fetchall()]
                result["triggers"][table] = triggers
                expected = EXPECTED_TRIGGERS[table]
                mutations = {
                    r["event_manipulation"]
                    for r in triggers
                    if r["trigger_name"] == expected and r["action_timing"] == "BEFORE"
                }
                if mutations != {"UPDATE", "DELETE"}:
                    raise RuntimeError(
                        f"FORECAST_STATE_IMMUTABILITY_TRIGGER_NOT_PROVEN:{table}:"
                        f"{expected}:{sorted(mutations)}"
                    )

            # No canonical H=1 forecast has been issued yet. Any pre-existing
            # input/contract row would materially change the manifest state and
            # must be audited before continuing.
            if int(result["row_counts"]["forecast_input_snapshots"]) != 0:
                raise RuntimeError("UNEXPECTED_PREEXISTING_FORECAST_INPUT_SNAPSHOT_ROWS")
            if int(result["row_counts"]["monthly_forecast_contracts"]) != 0:
                raise RuntimeError("UNEXPECTED_PREEXISTING_MONTHLY_FORECAST_CONTRACT_ROWS")

        conn.rollback()

    result["immutability_guards"] = "3/3_PASS"
    result["forecast_ledger_state"] = "EMPTY_PRE_ISSUANCE"
    result["readiness"] = "PASS"
    result["status"] = "STAGE4B_FORECAST_STATE_READINESS_PASS"

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")

    safe_summary = {
        "status": result["status"],
        "checked_at": result["checked_at"],
        "row_counts": result["row_counts"],
        "immutability_guards": result["immutability_guards"],
        "forecast_ledger_state": result["forecast_ledger_state"],
        "database_writes": "NONE",
        "raw_market_values_logged": False,
    }
    print(json.dumps(safe_summary, indent=2))
    print("STAGE4B_FORECAST_STATE_READINESS_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
