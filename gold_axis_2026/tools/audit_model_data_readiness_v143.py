from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row

EXPECTED_ENGINES = {
    "MONTHLY_DIRECTION_3M",
    "FAST",
    "SLOW",
    "GVZ_RISK",
    "BOCPD_RETURN_SUCCESSOR_V1",
    "MACRO_EVENT_SUCCESSOR_V2",
    "VW_MIDAS_MSVR_SUCCESSOR_V1",
    "CAUSAL_PATCH",
    "MOMENTUM_3M",
    "RANDOM_WALK",
    "EMERGENCY_LEVEL",
    "EMERGENCY_REVERSAL",
}
EXPECTED_FEATURES = {
    "MONTHLY_DIRECTION_3M",
    "FAST_STATE",
    "SLOW_STATE",
    "GVZ_VALUE",
    "GVZ_CAP",
    "GVZ_PANIC",
    "GVZ_REGIME",
}
MONTHLY_REFERENCE_ENGINES = {
    "VW_MIDAS_MSVR_SUCCESSOR_V1",
    "CAUSAL_PATCH",
    "MOMENTUM_3M",
    "RANDOM_WALK",
}
CANONICAL_XAU = "XAU_EOD_TWELVE_NY17"
XAU_CROSSCHECK = "XAU_DAILY_XAUS"
GVZ_SOURCE = "GVZ_CBOE"
XAU_QUALITY = "APPROVED_CANONICAL_TWELVE_NY17"


def _db_url() -> str:
    value = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError("NEON_DATABASE_URL is not set")
    return value


def _iso(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _iso(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_iso(v) for v in value]
    return value


def _fail(checks: list[dict[str, Any]], code: str, detail: Any = None) -> None:
    checks.append({"check": code, "status": "FAIL", "detail": _iso(detail)})


def _pass(checks: list[dict[str, Any]], code: str, detail: Any = None) -> None:
    checks.append({"check": code, "status": "PASS", "detail": _iso(detail)})


def _query_one(cur, sql: str, params: tuple = ()) -> dict[str, Any] | None:
    cur.execute(sql, params)
    return cur.fetchone()


def _query_all(cur, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
    cur.execute(sql, params)
    return list(cur.fetchall())


def _date_from_xau_row(row: dict[str, Any] | None) -> date | None:
    if not row:
        return None
    meta = row.get("metadata") or {}
    raw = meta.get("trade_date")
    if raw:
        return date.fromisoformat(str(raw)[:10])
    obs = row.get("observation_ts")
    return obs.date() if obs else None


def _date_from_obs(row: dict[str, Any] | None) -> date | None:
    if not row or not row.get("observation_ts"):
        return None
    return row["observation_ts"].date()


def _target_month_start(target_context: str) -> date:
    return date.fromisoformat(f"{target_context}-01")


def run_audit() -> dict[str, Any]:
    checked_at = datetime.now(timezone.utc)
    checks: list[dict[str, Any]] = []
    details: dict[str, Any] = {}

    with psycopg.connect(_db_url(), autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("set transaction read only")

            runtimes = _query_all(
                cur,
                """
                select engine_id, engine_version, engine_role, as_of, target_context,
                       runtime_status, status_code, input_fingerprint, metadata
                from current_engine_runtime_state_v1
                order by engine_id
                """,
            )
            runtime_map = {r["engine_id"]: r for r in runtimes}
            runtime_ids = set(runtime_map)
            target_contexts = {str(r.get("target_context") or "") for r in runtimes}

            current_surface_registered = (
                runtime_ids == EXPECTED_ENGINES
                and len(target_contexts) == 1
                and all(r.get("runtime_status") == "ACTIVE" for r in runtimes)
            )
            if current_surface_registered:
                _pass(checks, "CURRENT_SURFACE_12_ACTIVE", sorted(runtime_ids))
            else:
                _fail(
                    checks,
                    "CURRENT_SURFACE_12_ACTIVE",
                    {
                        "missing": sorted(EXPECTED_ENGINES - runtime_ids),
                        "extra": sorted(runtime_ids - EXPECTED_ENGINES),
                        "target_contexts": sorted(target_contexts),
                        "non_active": [
                            {"engine_id": r["engine_id"], "runtime_status": r.get("runtime_status")}
                            for r in runtimes
                            if r.get("runtime_status") != "ACTIVE"
                        ],
                    },
                )

            target_context = next(iter(target_contexts)) if len(target_contexts) == 1 else ""
            details["target_context"] = target_context or None

            features = _query_all(
                cur,
                """
                select c.id, c.feature_name, c.feature_version, c.calculation_ts,
                       c.input_cutoff, c.value_num, c.value_text, c.git_commit,
                       c.quality_status, c.metadata, d.input_lineage
                from current_context_feature_state_v1 c
                join derived_feature_snapshots d on d.id=c.id
                order by c.feature_name
                """,
            )
            feature_map = {r["feature_name"]: r for r in features}
            if set(feature_map) == EXPECTED_FEATURES:
                _pass(checks, "CURRENT_FEATURE_INVENTORY_7", sorted(feature_map))
            else:
                _fail(
                    checks,
                    "CURRENT_FEATURE_INVENTORY_7",
                    {
                        "missing": sorted(EXPECTED_FEATURES - set(feature_map)),
                        "extra": sorted(set(feature_map) - EXPECTED_FEATURES),
                    },
                )

            canonical_xau = _query_one(
                cur,
                """
                select series_id, observation_ts, available_as_of, retrieved_at,
                       quality_status, lineage_id, metadata
                from canonical_latest
                where series_id=%s
                order by observation_ts desc
                limit 1
                """,
                (CANONICAL_XAU,),
            )
            xau_crosscheck = _query_one(
                cur,
                """
                select series_id, observation_ts, available_as_of, retrieved_at,
                       quality_status, lineage_id, metadata
                from canonical_latest
                where series_id=%s
                order by observation_ts desc
                limit 1
                """,
                (XAU_CROSSCHECK,),
            )
            gvz_source = _query_one(
                cur,
                """
                select series_id, observation_ts, available_as_of, retrieved_at,
                       quality_status, lineage_id, metadata
                from canonical_latest
                where series_id=%s
                order by observation_ts desc
                limit 1
                """,
                (GVZ_SOURCE,),
            )
            details["latest_sources"] = {
                CANONICAL_XAU: _iso(canonical_xau),
                XAU_CROSSCHECK: _iso(xau_crosscheck),
                GVZ_SOURCE: _iso(gvz_source),
            }

            canonical_xau_ok = bool(
                canonical_xau
                and canonical_xau.get("quality_status") == XAU_QUALITY
                and _date_from_xau_row(canonical_xau)
            )
            if canonical_xau_ok:
                _pass(
                    checks,
                    "CANONICAL_XAU_IDENTITY_QUALITY",
                    {
                        "trade_date": _date_from_xau_row(canonical_xau),
                        "quality_status": canonical_xau.get("quality_status"),
                    },
                )
            else:
                _fail(checks, "CANONICAL_XAU_IDENTITY_QUALITY", canonical_xau)

            canonical_date = _date_from_xau_row(canonical_xau)
            crosscheck_date = _date_from_obs(xau_crosscheck)
            xau_not_behind_crosscheck = bool(
                canonical_date and (not crosscheck_date or canonical_date >= crosscheck_date)
            )
            if xau_not_behind_crosscheck:
                _pass(
                    checks,
                    "CANONICAL_XAU_NOT_BEHIND_CROSSCHECK",
                    {"canonical_trade_date": canonical_date, "crosscheck_date": crosscheck_date},
                )
            else:
                _fail(
                    checks,
                    "CANONICAL_XAU_NOT_BEHIND_CROSSCHECK",
                    {"canonical_trade_date": canonical_date, "crosscheck_date": crosscheck_date},
                )

            # FAST/SLOW are live intramonth candidates and must consume the newest
            # eligible canonical XAU that was available before their calculation.
            tactical_ready = True
            latest_xau_available = canonical_xau.get("available_as_of") if canonical_xau else None
            for name in ("FAST_STATE", "SLOW_STATE"):
                row = feature_map.get(name)
                lineage = (row or {}).get("input_lineage") or {}
                bound = lineage.get("series_id") == CANONICAL_XAU
                fresh = bool(
                    row
                    and latest_xau_available
                    and row.get("input_cutoff")
                    and row["input_cutoff"] >= latest_xau_available
                )
                if bound:
                    _pass(checks, f"{name}_CANONICAL_XAU_LINEAGE", lineage.get("series_id"))
                else:
                    tactical_ready = False
                    _fail(checks, f"{name}_CANONICAL_XAU_LINEAGE", lineage)
                if fresh:
                    _pass(
                        checks,
                        f"{name}_FRESH_RELATIVE_TO_XAU",
                        {"input_cutoff": row.get("input_cutoff"), "latest_xau_available": latest_xau_available},
                    )
                else:
                    tactical_ready = False
                    _fail(
                        checks,
                        f"{name}_FRESH_RELATIVE_TO_XAU",
                        {"input_cutoff": (row or {}).get("input_cutoff"), "latest_xau_available": latest_xau_available},
                    )

            gvz_ready = True
            latest_gvz_available = gvz_source.get("available_as_of") if gvz_source else None
            gvz_rows = [feature_map.get(n) for n in ("GVZ_VALUE", "GVZ_CAP", "GVZ_PANIC", "GVZ_REGIME")]
            for row in gvz_rows:
                name = row.get("feature_name") if row else "MISSING_GVZ_FEATURE"
                fresh = bool(
                    row
                    and latest_gvz_available
                    and row.get("input_cutoff")
                    and row["input_cutoff"] >= latest_gvz_available
                )
                if fresh:
                    _pass(
                        checks,
                        f"{name}_FRESH_RELATIVE_TO_GVZ",
                        {"input_cutoff": row.get("input_cutoff"), "latest_gvz_available": latest_gvz_available},
                    )
                else:
                    gvz_ready = False
                    _fail(
                        checks,
                        f"{name}_FRESH_RELATIVE_TO_GVZ",
                        {"input_cutoff": (row or {}).get("input_cutoff"), "latest_gvz_available": latest_gvz_available},
                    )
            gvz_regime_lineage = (feature_map.get("GVZ_REGIME") or {}).get("input_lineage") or {}
            if gvz_regime_lineage.get("series_id") == GVZ_SOURCE:
                _pass(checks, "GVZ_CANONICAL_LINEAGE", GVZ_SOURCE)
            else:
                gvz_ready = False
                _fail(checks, "GVZ_CANONICAL_LINEAGE", gvz_regime_lineage)

            emergency_ready = True
            target_month_has_xau = False
            if target_context:
                month_start = _target_month_start(target_context)
                target_month_has_xau = bool(
                    _query_one(
                        cur,
                        """
                        select 1 as found
                        from canonical_latest
                        where series_id=%s
                          and coalesce((metadata->>'trade_date')::date, observation_ts::date) >= %s
                        limit 1
                        """,
                        (CANONICAL_XAU, month_start),
                    )
                )
            for engine_id in ("EMERGENCY_LEVEL", "EMERGENCY_REVERSAL"):
                runtime = runtime_map.get(engine_id) or {}
                ref = (runtime.get("metadata") or {}).get("current_month_reference") or {}
                reason = str(ref.get("reason") or "")
                stale_month_open = target_month_has_xau and (
                    "NO_SEPTEMBER_EOD_OBSERVATION" in reason
                    or "NO_TARGET_MONTH_EOD_OBSERVATION" in reason
                    or "MONTH_OPEN_INITIALIZED" in reason
                )
                if stale_month_open:
                    emergency_ready = False
                    _fail(
                        checks,
                        f"{engine_id}_NOT_STALE_MONTH_OPEN",
                        {"reason": reason, "target_month_has_xau": target_month_has_xau},
                    )
                else:
                    _pass(
                        checks,
                        f"{engine_id}_NOT_STALE_MONTH_OPEN",
                        {"reason": reason, "target_month_has_xau": target_month_has_xau},
                    )

            # H=1 monthly references must remain origin-bounded. September intramonth
            # observations are not grounds to refresh these references.
            monthly_reference_valid = True
            monthly_details: dict[str, Any] = {}
            for engine_id in sorted(MONTHLY_REFERENCE_ENGINES):
                runtime = runtime_map.get(engine_id) or {}
                meta = runtime.get("metadata") or {}
                ref = meta.get("current_month_reference") or {}
                monthly_details[engine_id] = ref
                try:
                    target_ok = str(ref.get("target_month") or "")[:7] == target_context
                    origin = datetime.fromisoformat(str(ref["forecast_origin"]).replace("Z", "+00:00"))
                    cutoff = datetime.fromisoformat(str(ref["information_cutoff"]).replace("Z", "+00:00"))
                    origin_cutoff_ok = cutoff <= origin
                    evidence_ok = ref.get("evidence_class") == "HISTORICAL_REPLAY"
                    claim_ok = ref.get("prospective_claim") is False and ref.get("canonical_authority") is False
                    selector_ok = ref.get("auto_selector") == "OFF" and ref.get("auto_ensemble") == "OFF"
                    ok = target_ok and origin_cutoff_ok and evidence_ok and claim_ok and selector_ok
                except (KeyError, TypeError, ValueError):
                    ok = False
                if ok:
                    _pass(checks, f"{engine_id}_MONTHLY_REFERENCE_ORIGIN_BOUND", ref)
                else:
                    monthly_reference_valid = False
                    _fail(checks, f"{engine_id}_MONTHLY_REFERENCE_ORIGIN_BOUND", ref)
            details["monthly_references"] = _iso(monthly_details)

            # RW/Momentum must use the audited source-bound R2 identities and their
            # persisted input sets must contain only the governed monthly-mean series.
            simple_expert_ready = True
            expected_versions = {
                "RANDOM_WALK": "RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND",
                "MOMENTUM_3M": "MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND",
            }
            for expert_id, expected_version in expected_versions.items():
                runtime = runtime_map.get(expert_id) or {}
                version_ok = runtime.get("engine_version") == expected_version
                rows = _query_all(
                    cur,
                    """
                    select s.input_set_id, s.model_version, s.forecast_origin, s.target_month,
                           s.forecast_track, s.evidence_class, s.input_fingerprint,
                           array_agg(distinct f.series_id order by f.series_id) as series_ids,
                           max(f.available_as_of) as max_available_as_of
                    from forecast_input_sets s
                    join forecast_input_set_members m on m.input_set_id=s.input_set_id
                    join forecast_input_snapshots f on f.id=m.snapshot_id
                    where s.expert_id=%s and to_char(s.target_month, 'YYYY-MM')=%s
                    group by s.input_set_id, s.model_version, s.forecast_origin, s.target_month,
                             s.forecast_track, s.evidence_class, s.input_fingerprint
                    order by s.as_of desc
                    limit 1
                    """,
                    (expert_id, target_context),
                ) if target_context else []
                input_ok = bool(
                    rows
                    and rows[0].get("model_version") == expected_version
                    and rows[0].get("series_ids") == ["SIMPLE_EXPERT_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V2"]
                    and rows[0].get("forecast_track") == "HISTORICAL_REPLAY"
                    and rows[0].get("evidence_class") == "HISTORICAL_REPLAY"
                    and rows[0].get("max_available_as_of") <= rows[0].get("forecast_origin")
                )
                if version_ok and input_ok:
                    _pass(checks, f"{expert_id}_R2_SOURCE_BOUND_INPUT_SET", rows[0])
                else:
                    simple_expert_ready = False
                    _fail(
                        checks,
                        f"{expert_id}_R2_SOURCE_BOUND_INPUT_SET",
                        {"runtime_version": runtime.get("engine_version"), "input_set": rows[0] if rows else None},
                    )

            # Authority locks are intentionally conservative: this readiness audit
            # must never normalize a stale context by enabling model selection.
            locks_ok = all(
                (r.get("metadata") or {}).get("auto_selector") == "OFF"
                and (r.get("metadata") or {}).get("auto_ensemble") == "OFF"
                and (r.get("metadata") or {}).get("canonical_forecast_authority") is False
                for r in runtimes
            )
            if locks_ok:
                _pass(checks, "AUTHORITY_LOCKS_REMAIN_CLOSED")
            else:
                _fail(checks, "AUTHORITY_LOCKS_REMAIN_CLOSED")

            # A prospective Emergency reference is not silently manufactured from
            # the current replay reference. Record whether an eligible persisted
            # Patch reference exists for the target month.
            patch_prospective = None
            if target_context:
                patch_prospective = _query_one(
                    cur,
                    """
                    select id, expert_id, model_version, target_month, forecast_origin,
                           forecast_track, evidence_class, input_set_id, canonical_authority,
                           auto_selector, auto_ensemble, selector_status
                    from monthly_expert_forecasts
                    where expert_id='CAUSAL_PATCH'
                      and to_char(target_month, 'YYYY-MM')=%s
                      and forecast_track='MONTH_END_EXPERT'
                      and evidence_class in ('PROSPECTIVE_SHADOW','LIVE_PRODUCTION')
                    order by as_of desc
                    limit 1
                    """,
                    (target_context,),
                )
            details["eligible_patch_emergency_reference"] = _iso(patch_prospective)

            intramonth_data_ready = (
                canonical_xau_ok
                and xau_not_behind_crosscheck
                and tactical_ready
                and gvz_ready
                and emergency_ready
            )
            operational_ready = (
                current_surface_registered
                and monthly_reference_valid
                and simple_expert_ready
                and locks_ok
                and intramonth_data_ready
            )

            conn.rollback()

    failed = [c for c in checks if c["status"] == "FAIL"]
    return {
        "contract": "GOLD_CONTROL_MODEL_DATA_READINESS_V143",
        "checked_at": checked_at.isoformat(),
        "database_writes": "NONE_READ_ONLY_AUDIT",
        "current_surface_registered": current_surface_registered,
        "monthly_reference_valid": monthly_reference_valid,
        "simple_expert_source_binding_valid": simple_expert_ready,
        "intramonth_data_ready": intramonth_data_ready,
        "operational_model_data_ready": operational_ready,
        "failed_check_count": len(failed),
        "failed_checks": [c["check"] for c in failed],
        "checks": _iso(checks),
        "details": _iso(details),
    }


def _self_test() -> None:
    assert _target_month_start("2026-09") == date(2026, 9, 1)
    assert _date_from_xau_row({"metadata": {"trade_date": "2026-09-04"}}) == date(2026, 9, 4)
    assert _date_from_obs({"observation_ts": datetime(2026, 9, 4, tzinfo=timezone.utc)}) == date(2026, 9, 4)
    print("MODEL_DATA_READINESS_V143_SELF_TEST_PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--report-only", action="store_true", help="emit report but do not fail process on readiness blockers")
    args = parser.parse_args()

    if args.self_test:
        _self_test()
        if not os.environ.get("NEON_DATABASE_URL"):
            return 0

    report = run_audit()
    text = json.dumps(report, indent=2, sort_keys=True)
    print(text)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")

    if report["operational_model_data_ready"]:
        print("GOLD_CONTROL_MODEL_DATA_READINESS_V143_PASS")
        return 0
    print("GOLD_CONTROL_MODEL_DATA_READINESS_V143_BLOCKED")
    return 0 if args.report_only else 1


if __name__ == "__main__":
    raise SystemExit(main())
