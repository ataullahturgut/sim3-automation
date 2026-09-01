from __future__ import annotations

from typing import Any

from decision_store import EVIDENCE_CLASSES


def read_latest_decision(conn, evidence_class: str) -> dict[str, Any] | None:
    """Read the latest successful stored decision for one explicit evidence class.

    Evidence class is deliberately mandatory so historical replay can never be
    silently surfaced as the current prospective/live decision.
    """
    if evidence_class not in EVIDENCE_CLASSES:
        raise ValueError(f"Invalid evidence_class: {evidence_class!r}")

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                r.run_id,
                r.decision_as_of,
                r.generated_at,
                r.engine_version,
                r.config_version,
                r.config_hash,
                r.code_sha,
                r.trigger_type,
                r.evidence_class,
                r.status,
                r.input_snapshot_ref,
                r.forecast_contract_ref AS run_forecast_contract_ref,
                r.fingerprint AS run_fingerprint,
                s.snapshot_id,
                s.target_month,
                s.close_value,
                s.close_source_ref,
                s.vw_forecast_frozen,
                s.forecast_contract_ref AS snapshot_forecast_contract_ref,
                s.monthly_direction_3m,
                s.level_emergency,
                s.reversal_emergency,
                s.fast_state,
                s.slow_state,
                s.gvz_value,
                s.gvz_cap,
                s.gvz_panic,
                s.macro_event_down,
                s.bocpd_context,
                s.classification,
                s.default_execution_session,
                s.quality_status,
                s.fingerprint AS snapshot_fingerprint,
                e.event_id,
                e.event_ts,
                e.previous_classification,
                e.classification AS event_classification,
                e.classification_changed,
                e.reason_code,
                e.action_state,
                e.execution_session,
                e.fingerprint AS event_fingerprint
            FROM decision_signal_snapshots s
            JOIN decision_runs r ON r.run_id = s.run_id
            LEFT JOIN decision_events e ON e.snapshot_id = s.snapshot_id
            WHERE r.status = 'SUCCESS'
              AND r.evidence_class = %s
            ORDER BY s.decision_as_of DESC, r.generated_at DESC, e.created_at DESC
            LIMIT 1
            """,
            (evidence_class,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        columns = [d.name for d in cur.description]

    result = dict(zip(columns, row))

    # Defensive read-time guards: the current V1 contract does not authorize a
    # position/action mapping and snapshot/event classification must not diverge.
    if result.get("action_state") is not None:
        raise RuntimeError("NOT_PROVEN_POSITION_MAPPING_VIOLATION")
    event_classification = result.get("event_classification")
    if event_classification is not None and event_classification != result.get("classification"):
        raise RuntimeError("DECISION_EVENT_SNAPSHOT_CLASSIFICATION_MISMATCH")

    return result
