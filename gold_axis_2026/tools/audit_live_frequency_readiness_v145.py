from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

import psycopg
from psycopg.rows import dict_row

CONTRACT = "GOLD_CONTROL_LIVE_FREQUENCY_READINESS_V145"


def _db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL is not set")
    return value


def _one(cur, sql: str, params: tuple = ()) -> dict[str, Any] | None:
    cur.execute(sql, params)
    row = cur.fetchone()
    return None if row is None else dict(row)


def _source(cur, series_id: str) -> dict[str, Any]:
    reg = _one(
        cur,
        "select series_id,source_name,source_symbol,frequency,model_role,status from source_registry where series_id=%s",
        (series_id,),
    )
    latest = _one(
        cur,
        """
        select observation_ts,available_as_of,retrieved_at,value,quality_status,lineage_id
        from canonical_latest where series_id=%s order by observation_ts desc limit 1
        """,
        (series_id,),
    )
    cur.execute("select count(*) as n from observations where series_id=%s", (series_id,))
    n = int(cur.fetchone()["n"])
    return {"registry": reg, "latest": latest, "observation_count": n}


def run() -> dict[str, Any]:
    out: dict[str, Any] = {
        "contract": CONTRACT,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "engine_frequency_policy": {
            "VW_MIDAS_MSVR_SUCCESSOR_V1": "MONTHLY_ORIGIN_FROZEN",
            "CAUSAL_PATCH": "MONTHLY_ORIGIN_FROZEN",
            "MOMENTUM_3M": "MONTHLY_ORIGIN_FROZEN",
            "RANDOM_WALK": "MONTHLY_ORIGIN_FROZEN",
            "MONTHLY_DIRECTION_3M": "MONTH_OPEN_FROZEN",
            "FAST": "COMPLETED_TRADE_DATE_DAILY",
            "SLOW": "COMPLETED_WEEK",
            "EMERGENCY_LEVEL": "INTRADAY_ALERT_PLUS_EOD_CONFIRMATION",
            "EMERGENCY_REVERSAL": "INTRADAY_ALERT_PLUS_EOD_CONFIRMATION",
            "MACRO_EVENT_SUCCESSOR_V2": "OFFICIAL_RELEASE_TIME",
            "GVZ_RISK": "INTRADAY_IF_USED_AS_LIVE_RISK_CAP_ELSE_EOD",
            "BOCPD_RETURN_SUCCESSOR_V1": "COMPLETED_MONTH",
        },
    }

    with psycopg.connect(_db_url(), autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("set transaction read only")
            sources = {
                key: _source(cur, key)
                for key in (
                    "XAU_EOD_TWELVE_NY17",
                    "XAU_SPOT_XAUS",
                    "XAU_INTRADAY_XAUS",
                    "XAU_LIVE_TWELVE_WS",
                    "GVZ_CBOE",
                    "GVZ_CBOE_LIVE",
                    "MACRO_NFP_ACTUAL_FIRST_PRINT",
                    "MACRO_NFP_CONSENSUS_PIT",
                )
            }
            out["sources"] = sources

            emergency_ws = sources["XAU_LIVE_TWELVE_WS"]
            emergency_live_ready = bool(
                emergency_ws["registry"]
                and emergency_ws["observation_count"] > 0
                and emergency_ws["latest"]
                and str(emergency_ws["registry"].get("status") or "").startswith("APPROVED")
            )

            macro_actual = sources["MACRO_NFP_ACTUAL_FIRST_PRINT"]
            macro_consensus = sources["MACRO_NFP_CONSENSUS_PIT"]
            macro_history_present = bool(macro_actual["observation_count"] and macro_consensus["observation_count"])
            macro_operational_status = "NOT_YET_PROVEN"
            if macro_actual["registry"] and macro_consensus["registry"]:
                statuses = " ".join(
                    str(x.get("status") or "") for x in (macro_actual["registry"], macro_consensus["registry"])
                )
                if "LIVE_PRODUCTION" in statuses or "PROSPECTIVE_EVENT_TIME" in statuses:
                    macro_operational_status = "PROVEN"

            gvz_live = sources["GVZ_CBOE_LIVE"]
            gvz_intraday_ready = bool(
                gvz_live["registry"]
                and gvz_live["observation_count"] > 0
                and gvz_live["latest"]
                and str(gvz_live["registry"].get("status") or "").startswith("APPROVED")
            )

            out["readiness"] = {
                "EMERGENCY_LIVE_DATA_READY": emergency_live_ready,
                "MACRO_EVENT_HISTORICAL_EVENT_DATA_PRESENT": macro_history_present,
                "MACRO_EVENT_LIVE_DATA_READY": macro_operational_status,
                "GVZ_INTRADAY_RISK_READY": gvz_intraday_ready,
                "FAST_REQUIRES_INTRADAY": False,
                "SLOW_REQUIRES_INTRADAY": False,
                "BOCPD_REQUIRES_INTRADAY": False,
                "MONTHLY_H1_REQUIRES_INTRADAY": False,
            }

            blockers: list[str] = []
            if not emergency_live_ready:
                blockers.append("EMERGENCY_LIVE_AUTHORITY_NOT_PROVEN")
            if macro_operational_status != "PROVEN":
                blockers.append("MACRO_EVENT_PROSPECTIVE_EVENT_TIME_INGESTION_NOT_PROVEN")
            if not gvz_intraday_ready:
                blockers.append("GVZ_INTRADAY_AUTHORITY_NOT_PROVISIONED")
            out["blockers"] = blockers
            out["live_operational_ready"] = not blockers
        conn.rollback()

    return out


def main() -> int:
    result = run()
    print(json.dumps(result, indent=2, default=str))
    # Audit is informational until V1.45 activation. It must accurately expose
    # blockers but does not fail CI simply because unprovisioned live feeds are
    # intentionally still blocked.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
