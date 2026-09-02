from __future__ import annotations

import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parent
PATCH = ROOT / "schema_patch_multi_expert_forecast_v1.sql"


def db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL_MISSING")
    return value


def main() -> int:
    sql = PATCH.read_text(encoding="utf-8")
    if not sql.strip():
        raise RuntimeError("MULTI_EXPERT_SCHEMA_PATCH_EMPTY")

    with psycopg.connect(db_url(), autocommit=False, row_factory=dict_row) as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(sql, prepare=False)
                cur.execute("select to_regclass('public.monthly_expert_forecasts') as reg")
                if cur.fetchone()["reg"] is None:
                    raise RuntimeError("MULTI_EXPERT_LEDGER_NOT_CREATED")
                cur.execute(
                    """
                    select count(*) as n
                    from pg_trigger
                    where tgrelid='public.monthly_expert_forecasts'::regclass
                      and not tgisinternal
                      and tgname='trg_monthly_expert_forecasts_immutable'
                    """
                )
                if int(cur.fetchone()["n"]) != 1:
                    raise RuntimeError("MULTI_EXPERT_IMMUTABILITY_TRIGGER_NOT_PROVEN")
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    print("MULTI_EXPERT_FORECAST_LEDGER_SCHEMA=APPLIED")
    print("AUTO_SELECTOR=OFF")
    print("AUTO_ENSEMBLE=OFF")
    print("SELECTOR_STATUS=NOT_PROVEN_EXPERT_SELECTION_RULE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
