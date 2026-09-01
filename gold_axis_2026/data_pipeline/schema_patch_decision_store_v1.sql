-- GOLD_CONTROL_DECISION_STORE_V1_2026-09-01
-- Stage 3 decision-state persistence contract.
--
-- IMPORTANT:
-- - Stores descriptive R4.1 classifications only.
-- - action_state is deliberately constrained to NULL until a separate audited
--   position/exposure mapping is frozen under change control.
-- - Tables are append-only after insert; corrections require a new run/snapshot/event.
-- - No historical replay row may be relabeled as prospective/live by mutation.
-- - There is deliberately no cross-evidence "latest decision" view: replay,
--   prospective shadow and live production must remain explicitly separated.

CREATE TABLE IF NOT EXISTS decision_runs (
    run_id uuid PRIMARY KEY,
    decision_as_of timestamptz NOT NULL,
    generated_at timestamptz NOT NULL,
    engine_version text NOT NULL,
    config_version text NOT NULL,
    config_hash text,
    code_sha text,
    trigger_type text NOT NULL,
    evidence_class text NOT NULL,
    status text NOT NULL,
    input_snapshot_ref text,
    forecast_contract_ref text,
    fingerprint text NOT NULL UNIQUE,
    notes text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT decision_runs_evidence_class_chk CHECK (
        evidence_class IN ('HISTORICAL_REPLAY', 'PROSPECTIVE_SHADOW', 'LIVE_PRODUCTION')
    )
);

CREATE INDEX IF NOT EXISTS decision_runs_asof_idx
    ON decision_runs (decision_as_of DESC, generated_at DESC);
CREATE INDEX IF NOT EXISTS decision_runs_evidence_idx
    ON decision_runs (evidence_class, decision_as_of DESC);

CREATE TABLE IF NOT EXISTS decision_signal_snapshots (
    snapshot_id uuid PRIMARY KEY,
    run_id uuid NOT NULL REFERENCES decision_runs(run_id) ON DELETE RESTRICT,
    decision_as_of timestamptz NOT NULL,
    target_month date NOT NULL,
    close_value double precision NOT NULL,
    close_source_ref text NOT NULL,
    vw_forecast_frozen double precision NOT NULL,
    forecast_contract_ref text,
    monthly_direction_3m text NOT NULL,
    level_emergency text NOT NULL,
    reversal_emergency text NOT NULL,
    fast_state text NOT NULL,
    slow_state text NOT NULL,
    gvz_value double precision,
    gvz_cap double precision,
    gvz_panic boolean,
    macro_event_down boolean,
    bocpd_context text,
    classification text NOT NULL,
    default_execution_session date,
    quality_status text NOT NULL,
    fingerprint text NOT NULL UNIQUE,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT decision_snapshot_target_month_chk CHECK (target_month = date_trunc('month', target_month)::date),
    CONSTRAINT decision_snapshot_monthly_direction_chk CHECK (monthly_direction_3m IN ('UP', 'DOWN', 'NEUTRAL')),
    CONSTRAINT decision_snapshot_level_direction_chk CHECK (level_emergency IN ('UP', 'DOWN', 'NEUTRAL')),
    CONSTRAINT decision_snapshot_reversal_chk CHECK (reversal_emergency IN ('UP_ALERT', 'DOWN_ALERT', 'OFF')),
    CONSTRAINT decision_snapshot_fast_chk CHECK (fast_state IN ('ROBUST_UP', 'ROBUST_DOWN', 'MIXED', 'INSUFFICIENT_DATA')),
    CONSTRAINT decision_snapshot_slow_chk CHECK (slow_state IN ('ROBUST_UP', 'ROBUST_DOWN', 'NOT_YET_ROBUST', 'INSUFFICIENT_DATA')),
    CONSTRAINT decision_snapshot_classification_chk CHECK (
        classification IN (
            'MACRO_DOWN_RISK', 'REVERSAL_RISK_DOWN', 'REVERSAL_RISK_UP',
            'ALIGNED_UP', 'ALIGNED_DOWN', 'CONFLICT', 'UNRESOLVED_MIXED'
        )
    ),
    CONSTRAINT decision_snapshot_gvz_cap_chk CHECK (gvz_cap IS NULL OR (gvz_cap >= 0.0 AND gvz_cap <= 1.0)),
    CONSTRAINT decision_snapshot_one_per_run UNIQUE (run_id)
);

CREATE INDEX IF NOT EXISTS decision_snapshots_asof_idx
    ON decision_signal_snapshots (decision_as_of DESC, created_at DESC);
CREATE INDEX IF NOT EXISTS decision_snapshots_classification_idx
    ON decision_signal_snapshots (classification, decision_as_of DESC);

CREATE TABLE IF NOT EXISTS decision_events (
    event_id uuid PRIMARY KEY,
    run_id uuid NOT NULL REFERENCES decision_runs(run_id) ON DELETE RESTRICT,
    snapshot_id uuid NOT NULL REFERENCES decision_signal_snapshots(snapshot_id) ON DELETE RESTRICT,
    event_ts timestamptz NOT NULL,
    previous_classification text,
    classification text NOT NULL,
    classification_changed boolean NOT NULL,
    reason_code text NOT NULL,
    action_state text,
    execution_session date,
    fingerprint text NOT NULL UNIQUE,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT decision_event_previous_classification_chk CHECK (
        previous_classification IS NULL OR previous_classification IN (
            'MACRO_DOWN_RISK', 'REVERSAL_RISK_DOWN', 'REVERSAL_RISK_UP',
            'ALIGNED_UP', 'ALIGNED_DOWN', 'CONFLICT', 'UNRESOLVED_MIXED'
        )
    ),
    CONSTRAINT decision_event_classification_chk CHECK (
        classification IN (
            'MACRO_DOWN_RISK', 'REVERSAL_RISK_DOWN', 'REVERSAL_RISK_UP',
            'ALIGNED_UP', 'ALIGNED_DOWN', 'CONFLICT', 'UNRESOLVED_MIXED'
        )
    ),
    CONSTRAINT decision_event_reason_chk CHECK (
        reason_code IN (
            'MACRO_EVENT_DOWN_TRUE',
            'REVERSAL_DOWN_ALERT_ACTIVE',
            'REVERSAL_UP_ALERT_ACTIVE',
            'LEVEL_FAST_SLOW_ALIGNED_UP',
            'LEVEL_FAST_SLOW_ALIGNED_DOWN',
            'MONTHLY_VS_TACTICAL_CONFLICT',
            'NO_DECISIVE_ALIGNMENT'
        )
    ),
    CONSTRAINT decision_event_action_not_proven_chk CHECK (action_state IS NULL),
    CONSTRAINT decision_event_one_per_snapshot UNIQUE (snapshot_id)
);

CREATE INDEX IF NOT EXISTS decision_events_ts_idx
    ON decision_events (event_ts DESC, created_at DESC);

CREATE OR REPLACE FUNCTION reject_gold_control_decision_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'GOLD_CONTROL_DECISION_STORE_APPEND_ONLY';
END;
$$;

DROP TRIGGER IF EXISTS decision_runs_append_only ON decision_runs;
CREATE TRIGGER decision_runs_append_only
BEFORE UPDATE OR DELETE ON decision_runs
FOR EACH ROW EXECUTE FUNCTION reject_gold_control_decision_mutation();

DROP TRIGGER IF EXISTS decision_snapshots_append_only ON decision_signal_snapshots;
CREATE TRIGGER decision_snapshots_append_only
BEFORE UPDATE OR DELETE ON decision_signal_snapshots
FOR EACH ROW EXECUTE FUNCTION reject_gold_control_decision_mutation();

DROP TRIGGER IF EXISTS decision_events_append_only ON decision_events;
CREATE TRIGGER decision_events_append_only
BEFORE UPDATE OR DELETE ON decision_events
FOR EACH ROW EXECUTE FUNCTION reject_gold_control_decision_mutation();

-- Remove the earlier candidate view if it ever existed in a rehearsal branch.
-- It was ambiguous because it could return HISTORICAL_REPLAY as a generic latest state.
DROP VIEW IF EXISTS latest_decision_snapshot;

CREATE OR REPLACE VIEW latest_decision_snapshot_by_evidence AS
SELECT DISTINCT ON (r.evidence_class)
    s.*,
    r.generated_at,
    r.engine_version,
    r.config_version,
    r.config_hash,
    r.code_sha,
    r.trigger_type,
    r.evidence_class,
    r.status AS run_status,
    r.input_snapshot_ref,
    r.forecast_contract_ref AS run_forecast_contract_ref
FROM decision_signal_snapshots s
JOIN decision_runs r ON r.run_id = s.run_id
WHERE r.status = 'SUCCESS'
ORDER BY r.evidence_class, s.decision_as_of DESC, r.generated_at DESC;

COMMENT ON TABLE decision_runs IS
'Append-only Gold Control decision-engine run ledger. Evidence class distinguishes historical replay, prospective shadow, and live production.';
COMMENT ON TABLE decision_signal_snapshots IS
'Immutable exact R4.1 descriptive signal vector for a successful decision run; no inferred position action.';
COMMENT ON TABLE decision_events IS
'Append-only classification-change ledger. action_state is constrained NULL until position mapping is independently proven and frozen.';
COMMENT ON VIEW latest_decision_snapshot_by_evidence IS
'Latest successful stored descriptive decision snapshot separately for each evidence class. Consumers must choose the evidence class explicitly.';

INSERT INTO system_metadata (key, value)
VALUES
    ('decision_store_schema_version', 'GOLD_CONTROL_DECISION_STORE_V1_2026-09-01'),
    ('decision_action_mapping_status', 'NOT_PROVEN_POSITION_MAPPING')
ON CONFLICT (key)
DO UPDATE SET value = EXCLUDED.value, updated_at = now();
