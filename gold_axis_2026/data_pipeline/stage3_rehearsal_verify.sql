-- GOLD CONTROL STAGE 3 — ISOLATED REHEARSAL VERIFICATION
-- RUN ONLY on branch: gc-stage3-rehearsal-20260901
-- Database: neondb
-- This script intentionally writes synthetic HISTORICAL_REPLAY rows to the rehearsal branch only.

DO $$
BEGIN
    IF to_regclass('public.decision_runs') IS NULL
       OR to_regclass('public.decision_signal_snapshots') IS NULL
       OR to_regclass('public.decision_events') IS NULL
       OR to_regclass('public.latest_decision_snapshot_by_evidence') IS NULL THEN
        RAISE EXCEPTION 'STAGE3_REHEARSAL_SCHEMA_MISSING';
    END IF;
END $$;

INSERT INTO decision_runs (
    run_id, decision_as_of, generated_at, engine_version, config_version,
    config_hash, code_sha, trigger_type, evidence_class, status,
    input_snapshot_ref, forecast_contract_ref, fingerprint, notes, metadata
) VALUES (
    '31000000-0000-0000-0000-000000000001',
    '2026-08-28 21:00:00+00',
    '2026-09-01 10:00:00+00',
    'R4.1-REHEARSAL',
    'FROZEN_R4_1',
    'rehearsal-config-hash',
    'rehearsal-code-sha',
    'MANUAL_REHEARSAL',
    'HISTORICAL_REPLAY',
    'SUCCESS',
    'REHEARSAL_INPUT_SNAPSHOT',
    'REHEARSAL_FORECAST_CONTRACT',
    'gc-stage3-rehearsal-run-001',
    'Synthetic isolated-branch rehearsal only',
    '{"synthetic":true,"purpose":"stage3_rehearsal"}'::jsonb
)
ON CONFLICT (fingerprint) DO NOTHING;

INSERT INTO decision_signal_snapshots (
    snapshot_id, run_id, decision_as_of, target_month, close_value,
    close_source_ref, vw_forecast_frozen, forecast_contract_ref,
    monthly_direction_3m, level_emergency, reversal_emergency,
    fast_state, slow_state, gvz_value, gvz_cap, gvz_panic,
    macro_event_down, bocpd_context, classification,
    default_execution_session, quality_status, fingerprint, metadata
) VALUES (
    '32000000-0000-0000-0000-000000000001',
    '31000000-0000-0000-0000-000000000001',
    '2026-08-28 21:00:00+00',
    '2026-08-01',
    4455.15,
    'SYNTHETIC_REHEARSAL_CLOSE',
    4093.038840,
    'REHEARSAL_FORECAST_CONTRACT',
    'DOWN',
    'UP',
    'DOWN_ALERT',
    'ROBUST_UP',
    'ROBUST_UP',
    25.17,
    1.0,
    false,
    false,
    'REHEARSAL_ONLY',
    'REVERSAL_RISK_DOWN',
    '2026-08-31',
    'REHEARSAL_SYNTHETIC',
    'gc-stage3-rehearsal-snapshot-001',
    '{"synthetic":true,"purpose":"stage3_rehearsal"}'::jsonb
)
ON CONFLICT (fingerprint) DO NOTHING;

INSERT INTO decision_events (
    event_id, run_id, snapshot_id, event_ts, previous_classification,
    classification, classification_changed, reason_code, action_state,
    execution_session, fingerprint, metadata
) VALUES (
    '33000000-0000-0000-0000-000000000001',
    '31000000-0000-0000-0000-000000000001',
    '32000000-0000-0000-0000-000000000001',
    '2026-08-28 21:00:00+00',
    NULL,
    'REVERSAL_RISK_DOWN',
    true,
    'REVERSAL_DOWN_ALERT_ACTIVE',
    NULL,
    '2026-08-31',
    'gc-stage3-rehearsal-event-001',
    '{"synthetic":true,"purpose":"stage3_rehearsal"}'::jsonb
)
ON CONFLICT (fingerprint) DO NOTHING;

DO $$
DECLARE
    blocked boolean := false;
BEGIN
    BEGIN
        UPDATE decision_runs
        SET notes = 'THIS MUST NOT PERSIST'
        WHERE run_id = '31000000-0000-0000-0000-000000000001';
    EXCEPTION WHEN OTHERS THEN
        IF position('GOLD_CONTROL_DECISION_STORE_APPEND_ONLY' in SQLERRM) > 0 THEN
            blocked := true;
        ELSE
            RAISE;
        END IF;
    END;

    IF NOT blocked THEN
        RAISE EXCEPTION 'APPEND_ONLY_GUARD_FAILED';
    END IF;
END $$;

DO $$
DECLARE
    blocked boolean := false;
BEGIN
    BEGIN
        INSERT INTO decision_events (
            event_id, run_id, snapshot_id, event_ts, previous_classification,
            classification, classification_changed, reason_code, action_state,
            execution_session, fingerprint, metadata
        ) VALUES (
            '33000000-0000-0000-0000-000000000099',
            '31000000-0000-0000-0000-000000000001',
            '32000000-0000-0000-0000-000000000001',
            '2026-08-28 21:01:00+00',
            'REVERSAL_RISK_DOWN',
            'REVERSAL_RISK_DOWN',
            false,
            'REVERSAL_DOWN_ALERT_ACTIVE',
            'HOLD_LONG',
            '2026-08-31',
            'gc-stage3-rehearsal-event-bad-action',
            '{"synthetic":true}'::jsonb
        );
    EXCEPTION WHEN OTHERS THEN
        IF position('decision_event_action_not_proven_chk' in SQLERRM) > 0
           OR position('action_state' in SQLERRM) > 0
           OR position('duplicate key' in SQLERRM) > 0 THEN
            blocked := true;
        ELSE
            RAISE;
        END IF;
    END;

    IF NOT blocked THEN
        RAISE EXCEPTION 'ACTION_MAPPING_GUARD_FAILED';
    END IF;
END $$;

SELECT
    'STAGE3_REHEARSAL_VERIFY_PASS' AS result,
    r.evidence_class,
    s.classification,
    e.reason_code,
    e.action_state,
    (SELECT value FROM system_metadata WHERE key = 'decision_store_schema_version') AS schema_version,
    (SELECT value FROM system_metadata WHERE key = 'decision_action_mapping_status') AS action_mapping_status
FROM decision_runs r
JOIN decision_signal_snapshots s ON s.run_id = r.run_id
JOIN decision_events e ON e.run_id = r.run_id AND e.snapshot_id = s.snapshot_id
WHERE r.fingerprint = 'gc-stage3-rehearsal-run-001';

SELECT
    evidence_class,
    classification,
    decision_as_of
FROM latest_decision_snapshot_by_evidence
WHERE evidence_class = 'HISTORICAL_REPLAY';
