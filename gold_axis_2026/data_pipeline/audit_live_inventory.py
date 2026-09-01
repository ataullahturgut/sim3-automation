from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from psycopg import sql
from psycopg.rows import dict_row


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "audits" / "GOLD_CONTROL_LIVE_DB_INVENTORY.json"


def _jsonable(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _jsonable_rows(rows):
    return [{k: _jsonable(v) for k, v in dict(row).items()} for row in rows]


def _display_policy(series_id: str, status: str | None) -> str:
    status = status or ""
    if "INTERNAL_NON_DISPLAY" in status or "NO_PUBLIC_RAW_REDISTRIBUTION" in status:
        return "NO_RAW_DISPLAY"
    explicit = {
        "XAU_SPOT_XAUS": "DISPLAY_INDICATIVE_NOT_SETTLEMENT",
        "XAU_DAILY_XAUS": "DISPLAY_OPERATIONAL_CROSSCHECK",
        "GVZ_CBOE": "DISPLAY_OFFICIAL_CLOSE",
        "VIX_CBOE": "SECONDARY_CONTEXT_IF_NEEDED",
    }
    if series_id in explicit:
        return explicit[series_id]
    if "BLOCKED" in status or "LICENSE_REQUIRED" in status or "PAID_" in status:
        return "NO_DISPLAY_BLOCKED"
    return "NOT_EXPLICITLY_FROZEN_FOR_PRIMARY_UI"


def _trigger_candidates(series_id: str) -> list[str]:
    if series_id == "XAU_SPOT_XAUS":
        return ["hourly:xau", "daily:xau"]
    if series_id == "XAU_DAILY_XAUS":
        return ["daily:xau"]
    if series_id in {"GVZ_CBOE", "VIX_CBOE"}:
        return ["daily:cboe"]
    if series_id in {"DGS10_FRB_H15", "DEXCHUS_FRB_H10", "DTWEXBGS_FRB_H10", "EFFR_NYFED"}:
        return ["daily:fed"]
    if series_id in {"GPR_OFFICIAL", "GPRT_OFFICIAL", "GPRA_OFFICIAL"}:
        return ["daily:gpr"]
    if series_id in {"SP500_FRED", "DJIA_FRED", "NASDAQ100_FRED"}:
        return ["daily:fred_indices"]
    if series_id in {
        "NEM_TWELVEDATA", "BARRICK_B_TWELVEDATA", "GLL_TWELVEDATA",
        "DZZ_TWELVEDATA", "HL_PB_TWELVEDATA",
    }:
        return ["daily:twelve_market"]
    return []


def _run_sort_key(run: dict) -> str:
    return str(run.get("finished_at") or run.get("started_at") or "")


def _latest_mapped_run(series_id: str, by_trigger: dict[str, dict]) -> dict | None:
    candidates = [by_trigger[t] for t in _trigger_candidates(series_id) if t in by_trigger]
    if not candidates:
        return None
    return max(candidates, key=_run_sort_key)


def _table_meta(cur, table_name: str) -> dict:
    cur.execute("SELECT to_regclass(%s) AS object_name", (f"public.{table_name}",))
    exists = cur.fetchone()["object_name"] is not None
    if not exists:
        return {"exists": False, "row_count": 0, "columns": [], "temporal_bounds": {}, "identity_sample": []}

    cur.execute(
        """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema='public' AND table_name=%s
        ORDER BY ordinal_position
        """,
        (table_name,),
    )
    column_rows = cur.fetchall()
    columns = [r["column_name"] for r in column_rows]
    cur.execute(sql.SQL("SELECT count(*) AS n FROM {}").format(sql.Identifier(table_name)))
    row_count = int(cur.fetchone()["n"])

    temporal_bounds = {}
    temporal_candidates = [
        "issued_at", "forecast_origin", "origin_ts", "target_month", "snapshot_ts",
        "as_of_ts", "decision_ts", "generated_at", "created_at", "updated_at",
    ]
    for col in temporal_candidates:
        if col not in columns or row_count == 0:
            continue
        q = sql.SQL("SELECT min({c}) AS min_v, max({c}) AS max_v FROM {t}").format(
            c=sql.Identifier(col), t=sql.Identifier(table_name)
        )
        cur.execute(q)
        bounds = cur.fetchone()
        temporal_bounds[col] = {"min": _jsonable(bounds["min_v"]), "max": _jsonable(bounds["max_v"])}

    identity_whitelist = [
        "snapshot_id", "forecast_id", "contract_id", "run_id", "decision_run_id",
        "forecast_origin", "origin_ts", "target_month", "issued_at", "as_of_ts",
        "decision_ts", "model_id", "model_version", "engine_version", "config_version",
        "code_sha", "git_sha", "status", "evidence_class",
    ]
    selected = [c for c in identity_whitelist if c in columns]
    identity_sample = []
    if selected and row_count:
        order_col = next((c for c in ["issued_at", "decision_ts", "as_of_ts", "created_at", "origin_ts"] if c in columns), None)
        q = sql.SQL("SELECT {cols} FROM {table}").format(
            cols=sql.SQL(", ").join(sql.Identifier(c) for c in selected),
            table=sql.Identifier(table_name),
        )
        if order_col:
            q += sql.SQL(" ORDER BY {} DESC NULLS LAST").format(sql.Identifier(order_col))
        q += sql.SQL(" LIMIT 5")
        cur.execute(q)
        identity_sample = _jsonable_rows(cur.fetchall())

    return {
        "exists": True,
        "row_count": row_count,
        "columns": columns,
        "temporal_bounds": temporal_bounds,
        "identity_sample": identity_sample,
    }


def main() -> int:
    url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not url:
        print("AUDIT_FAILED:NEON_DATABASE_URL_MISSING")
        return 2

    try:
        generated_at = datetime.now(timezone.utc)
        with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                # Binding safety rule: inventory/audit is read-only and always rolled back.
                cur.execute("SET TRANSACTION READ ONLY")

                cur.execute(
                    """
                    SELECT
                        series_id, semantic_id, source_name, source_symbol, source_tier,
                        frequency, unit, model_role, status, license_note
                    FROM source_registry
                    ORDER BY series_id
                    """
                )
                registry_rows = _jsonable_rows(cur.fetchall())

                cur.execute(
                    """
                    SELECT
                        series_id,
                        min(observation_ts) AS first_observation_ts,
                        max(observation_ts) AS last_observation_ts,
                        min(first_seen_at) AS first_retrieval_ts,
                        max(retrieved_at) AS last_retrieval_ts,
                        max(provider_as_of) AS latest_provider_as_of,
                        count(*) AS observation_count,
                        count(DISTINCT lineage_id) AS lineage_count,
                        (array_agg(source ORDER BY observation_ts DESC, retrieved_at DESC))[1] AS actual_latest_source,
                        (array_agg(lineage_id ORDER BY observation_ts DESC, retrieved_at DESC))[1] AS latest_lineage_id,
                        (array_agg(quality_status ORDER BY observation_ts DESC, retrieved_at DESC))[1] AS latest_quality_status
                    FROM usable_observations
                    GROUP BY series_id
                    ORDER BY series_id
                    """
                )
                observation_rows = _jsonable_rows(cur.fetchall())

                cur.execute(
                    """
                    SELECT
                        run_id, started_at, finished_at, git_sha, pipeline_version,
                        trigger_type, status, observations_read, observations_written
                    FROM retrieval_runs
                    ORDER BY COALESCE(finished_at, started_at) DESC
                    LIMIT 100
                    """
                )
                runs = _jsonable_rows(cur.fetchall())

                cur.execute(
                    """
                    SELECT DISTINCT ON (trigger_type)
                        run_id, started_at, finished_at, git_sha, pipeline_version,
                        trigger_type, status, observations_read, observations_written
                    FROM retrieval_runs
                    WHERE trigger_type IN (
                        'hourly:xau', 'daily:xau', 'daily:cboe', 'daily:fed', 'daily:gpr',
                        'daily:fred_indices', 'daily:twelve_market'
                    )
                    ORDER BY trigger_type, COALESCE(finished_at, started_at) DESC
                    """
                )
                source_runs = _jsonable_rows(cur.fetchall())
                by_trigger = {r["trigger_type"]: r for r in source_runs}

                cur.execute("SELECT key, value, updated_at FROM system_metadata ORDER BY key")
                metadata = _jsonable_rows(cur.fetchall())

                cur.execute(
                    """
                    SELECT
                        count(*) FILTER (WHERE severity = 'ERROR') AS quality_error_events,
                        count(*) FILTER (WHERE severity = 'WARNING') AS quality_warning_events,
                        max(event_ts) AS latest_quality_event_ts
                    FROM quality_events
                    """
                )
                quality_summary = _jsonable_rows(cur.fetchall())[0]

                cur.execute(
                    """
                    SELECT series_id, event_ts, severity, code
                    FROM quality_events
                    ORDER BY event_ts DESC, id DESC
                    LIMIT 30
                    """
                )
                recent_quality_events = _jsonable_rows(cur.fetchall())

                forecast_store_audit = {
                    name: _table_meta(cur, name)
                    for name in [
                        "forecast_input_snapshots", "derived_feature_snapshots",
                        "monthly_forecast_contracts", "decision_runs",
                        "decision_signal_snapshots", "decision_events",
                    ]
                }

            conn.rollback()

        registry = {r["series_id"]: r for r in registry_rows}
        observations = {r["series_id"]: r for r in observation_rows}
        inventory = []
        for sid in sorted(set(registry) | set(observations)):
            reg = registry.get(sid, {})
            obs = observations.get(sid, {})
            mapped_run = _latest_mapped_run(sid, by_trigger)
            run_status = None if mapped_run is None else mapped_run.get("status")

            if not obs.get("observation_count"):
                freshness_state = "NOT_PERSISTED_CURRENT_DB"
            elif mapped_run is None:
                freshness_state = "UNRESOLVED_NO_MAPPED_PIPELINE_RUN"
            elif run_status == "SUCCESS":
                freshness_state = "CURRENT_LAST_MAPPED_RUN_SUCCESS"
            else:
                freshness_state = f"DEGRADED_LAST_MAPPED_RUN_{run_status or 'UNKNOWN'}"

            blocker_parts = []
            contract_status = str(reg.get("status") or "UNRESOLVED")
            if any(token in contract_status for token in ["BLOCKED", "LICENSE_REQUIRED", "PAID_"]):
                blocker_parts.append(contract_status)
            if sid == "XAU_SPOT_XAUS" and obs.get("actual_latest_source"):
                actual = str(obs.get("actual_latest_source")).lower()
                contract = str(reg.get("source_name") or "").lower()
                if "xaus" in contract and "xaus" not in actual:
                    blocker_parts.append("UNRESOLVED_PERSISTED_SOURCE_LABEL_DIFFERS_FROM_XAUS_CONTRACT")
            if mapped_run is not None and run_status != "SUCCESS":
                blocker_parts.append(f"LATEST_PIPELINE_{run_status}")

            pit_note = (
                "ELIGIBLE_ONLY_VIA_PIT_FUNCTION_OR_IMMUTABLE_SNAPSHOT"
                if obs.get("observation_count")
                else "NO_CURRENT_USABLE_ROWS"
            )

            retrieval_age_hours = None
            if obs.get("last_retrieval_ts"):
                dt = datetime.fromisoformat(str(obs["last_retrieval_ts"]).replace("Z", "+00:00"))
                retrieval_age_hours = round((generated_at - dt).total_seconds() / 3600.0, 3)

            inventory.append({
                "series_id": sid,
                "semantic_id": reg.get("semantic_id") or "UNRESOLVED_NOT_IN_REGISTRY",
                "contract_source": reg.get("source_name") or "UNRESOLVED_NOT_IN_REGISTRY",
                "source_symbol": reg.get("source_symbol"),
                "source_tier": reg.get("source_tier") or "UNRESOLVED",
                "frequency": reg.get("frequency"),
                "unit": reg.get("unit"),
                "model_role": reg.get("model_role"),
                "display_policy": _display_policy(sid, reg.get("status")),
                "model_use_status": reg.get("status") or "UNRESOLVED_NOT_IN_REGISTRY",
                "license_note": reg.get("license_note"),
                "first_observation_ts": obs.get("first_observation_ts"),
                "last_observation_ts": obs.get("last_observation_ts"),
                "first_retrieval_ts": obs.get("first_retrieval_ts"),
                "last_retrieval_ts": obs.get("last_retrieval_ts"),
                "latest_provider_as_of": obs.get("latest_provider_as_of"),
                "observation_count": obs.get("observation_count") or 0,
                "lineage_count": obs.get("lineage_count") or 0,
                "actual_latest_source": obs.get("actual_latest_source"),
                "latest_lineage_id": obs.get("latest_lineage_id"),
                "latest_quality_status": obs.get("latest_quality_status"),
                "latest_pipeline_trigger": None if mapped_run is None else mapped_run.get("trigger_type"),
                "latest_pipeline_status": run_status,
                "freshness_state": freshness_state,
                "retrieval_age_hours": retrieval_age_hours,
                "pit_note": pit_note,
                "blocker_note": "; ".join(blocker_parts) if blocker_parts else None,
            })

        payload = {
            "audit_version": "GOLD_CONTROL_LIVE_DB_INVENTORY_R2",
            "generated_at_utc": generated_at.isoformat(),
            "mode": "READ_ONLY_ROLLBACK",
            "contains_observation_values": False,
            "contains_quality_messages": False,
            "source_registry_count": len(registry_rows),
            "usable_series_count": len(observation_rows),
            "inventory": inventory,
            "latest_source_runs": by_trigger,
            "recent_retrieval_runs": runs,
            "system_metadata": metadata,
            "quality_event_summary": quality_summary,
            "recent_quality_events": recent_quality_events,
            "forecast_store_audit": forecast_store_audit,
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(
            f"AUDIT_OK registry={len(registry_rows)} usable_series={len(observation_rows)} "
            f"inventory={len(inventory)} output={OUT.name}"
        )
        return 0
    except Exception as exc:
        # Do not print DSN/provider connection details into public CI logs.
        print(f"AUDIT_FAILED:{type(exc).__name__}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
