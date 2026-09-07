from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any

import psycopg
from psycopg.rows import dict_row

CONTRACT = "GOLD_CONTROL_LIVE_INTRAMONTH_POSTWRITE_AUDIT_V144"
XAU = "XAU_EOD_TWELVE_NY17"
XAU_CROSSCHECK = "XAU_DAILY_XAUS"
GVZ = "GVZ_CBOE"
TACTICAL = ("FAST_STATE", "SLOW_STATE")
GVZ_FEATURES = ("GVZ_VALUE", "GVZ_CAP", "GVZ_PANIC", "GVZ_REGIME")
EMERGENCY = ("EMERGENCY_LEVEL", "EMERGENCY_REVERSAL")
AUTHORITY_TABLES = (
    "monthly_forecast_contracts",
    "decision_signal_snapshots",
    "decision_runs",
    "decision_events",
)


def _db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL is not set")
    return value


def _one(cur, sql: str, params: tuple = ()) -> dict[str, Any] | None:
    cur.execute(sql, params)
    return cur.fetchone()


def _all(cur, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
    cur.execute(sql, params)
    return list(cur.fetchall())


def _iso(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _iso(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_iso(v) for v in value]
    return value


def run() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, detail: Any = None) -> None:
        checks.append({"check": name, "status": "PASS" if ok else "FAIL", "detail": _iso(detail)})

    with psycopg.connect(_db_url(), autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("set transaction read only")

            runtime = _all(cur, "select * from current_engine_runtime_state_v1 order by engine_id")
            target_contexts = {str(r.get("target_context") or "") for r in runtime}
            target_context = next(iter(target_contexts)) if len(target_contexts) == 1 else None
            check(
                "CURRENT_RUNTIME_12_ACTIVE_ONE_CONTEXT",
                len(runtime) == 12 and target_context is not None and all(r.get("runtime_status") == "ACTIVE" for r in runtime),
                {"count": len(runtime), "target_contexts": sorted(target_contexts)},
            )
            runtime_map = {r["engine_id"]: r for r in runtime}

            xau = _one(
                cur,
                "select observation_ts,available_as_of,quality_status,metadata from canonical_latest where series_id=%s order by observation_ts desc limit 1",
                (XAU,),
            )
            cross = _one(
                cur,
                "select observation_ts,available_as_of,quality_status,metadata from canonical_latest where series_id=%s order by observation_ts desc limit 1",
                (XAU_CROSSCHECK,),
            )
            gvz = _one(
                cur,
                "select observation_ts,available_as_of,quality_status,metadata from canonical_latest where series_id=%s order by observation_ts desc limit 1",
                (GVZ,),
            )
            xau_date = None if not xau else (xau.get("metadata") or {}).get("trade_date") or xau["observation_ts"].date().isoformat()
            cross_date = None if not cross else cross["observation_ts"].date().isoformat()
            check(
                "CANONICAL_XAU_CAUGHT_UP_TO_ACCEPTED_CROSSCHECK",
                bool(xau and (not cross_date or str(xau_date) >= str(cross_date))),
                {"canonical_trade_date": xau_date, "crosscheck_date": cross_date},
            )

            latest_features: dict[str, dict[str, Any]] = {}
            for name in TACTICAL + GVZ_FEATURES:
                row = _one(
                    cur,
                    """
                    select id,feature_name,feature_version,calculation_ts,input_cutoff,quality_status,input_lineage,metadata
                    from derived_feature_snapshots
                    where feature_name=%s and metadata->>'target_context'=%s
                    order by calculation_ts desc,id desc limit 1
                    """,
                    (name, target_context),
                )
                if row:
                    latest_features[name] = row

            for name in TACTICAL:
                row = latest_features.get(name) or {}
                lineage = row.get("input_lineage") or {}
                ok = bool(
                    xau
                    and row
                    and lineage.get("series_id") == XAU
                    and row.get("input_cutoff") is not None
                    and row["input_cutoff"] >= xau["available_as_of"]
                    and str((row.get("metadata") or {}).get("contract") or "") == "GOLD_CONTROL_LIVE_INTRAMONTH_RECOMPUTE_V144"
                    and bool((row.get("metadata") or {}).get("input_fingerprint"))
                )
                check(
                    f"{name}_CURRENT_SOURCE_LINEAGE_FRESH",
                    ok,
                    {
                        "input_cutoff": row.get("input_cutoff"),
                        "source_available_as_of": None if not xau else xau.get("available_as_of"),
                        "lineage_series_id": lineage.get("series_id"),
                        "feature_version": row.get("feature_version"),
                    },
                )

            for name in GVZ_FEATURES:
                row = latest_features.get(name) or {}
                lineage = row.get("input_lineage") or {}
                ok = bool(
                    gvz
                    and row
                    and lineage.get("series_id") == GVZ
                    and row.get("input_cutoff") is not None
                    and row["input_cutoff"] >= gvz["available_as_of"]
                    and str((row.get("metadata") or {}).get("contract") or "") == "GOLD_CONTROL_LIVE_INTRAMONTH_RECOMPUTE_V144"
                    and bool((row.get("metadata") or {}).get("input_fingerprint"))
                )
                check(
                    f"{name}_CURRENT_SOURCE_LINEAGE_FRESH",
                    ok,
                    {
                        "input_cutoff": row.get("input_cutoff"),
                        "source_available_as_of": None if not gvz else gvz.get("available_as_of"),
                        "lineage_series_id": lineage.get("series_id"),
                        "feature_version": row.get("feature_version"),
                    },
                )

            for engine_id in EMERGENCY:
                row = runtime_map.get(engine_id) or {}
                meta = row.get("metadata") or {}
                ref = meta.get("current_month_reference") or {}
                state_value = ref.get("state_value")
                ok = bool(
                    xau
                    and meta.get("source_series_id") == XAU
                    and meta.get("operational_refresh_contract") == "GOLD_CONTROL_LIVE_INTRAMONTH_RECOMPUTE_V144"
                    and meta.get("information_cutoff")
                    and datetime.fromisoformat(str(meta["information_cutoff"]).replace("Z", "+00:00")) >= xau["available_as_of"]
                    and ref.get("reference_kind") == "CURRENT_INTRAMONTH_RECOMPUTED_STATE"
                    and state_value is not None
                    and not str(ref.get("reason") or "").startswith("MONTH_OPEN_INITIALIZED")
                    and ref.get("prospective_claim") is False
                    and ref.get("canonical_authority") is False
                )
                check(
                    f"{engine_id}_RECOMPUTED_FROM_CURRENT_XAU",
                    ok,
                    {
                        "state_value": state_value,
                        "reference_kind": ref.get("reference_kind"),
                        "reference_evidence_class": meta.get("reference_evidence_class"),
                        "information_cutoff": meta.get("information_cutoff"),
                        "source_available_as_of": None if not xau else xau.get("available_as_of"),
                    },
                )

            for engine_id in ("FAST", "SLOW", "GVZ_RISK"):
                row = runtime_map.get(engine_id) or {}
                meta = row.get("metadata") or {}
                expected_source = XAU if engine_id in {"FAST", "SLOW"} else GVZ
                check(
                    f"{engine_id}_RUNTIME_REFRESH_BOUND",
                    bool(
                        row.get("input_fingerprint")
                        and meta.get("operational_refresh_contract") == "GOLD_CONTROL_LIVE_INTRAMONTH_RECOMPUTE_V144"
                        and meta.get("source_series_id") == expected_source
                        and meta.get("prospective_claim") is False
                        and meta.get("canonical_forecast_authority") is False
                    ),
                    {"status_code": row.get("status_code"), "metadata": meta},
                )

            authority_counts: dict[str, int] = {}
            for table in AUTHORITY_TABLES:
                cur.execute(f"select count(*) as n from {table}")
                authority_counts[table] = int(cur.fetchone()["n"])
            check("AUTHORITY_STORES_REMAIN_ZERO", all(v == 0 for v in authority_counts.values()), authority_counts)
            conn.rollback()

    failed = [c for c in checks if c["status"] == "FAIL"]
    result = {
        "contract": CONTRACT,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failed else "BLOCKED",
        "checks": checks,
        "failed_count": len(failed),
        "database_writes": "NONE",
    }
    print(json.dumps(result, indent=2, default=str))
    if failed:
        raise RuntimeError(f"V144_POSTWRITE_AUDIT_BLOCKED:{[c['check'] for c in failed]}")
    return result


if __name__ == "__main__":
    run()
