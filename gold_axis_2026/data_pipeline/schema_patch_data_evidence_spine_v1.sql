-- GOLD_CONTROL_DATA_EVIDENCE_SPINE_V1
-- Contract: GOLD_CONTROL_DATA_EVIDENCE_SPINE_CONTRACT_2026-09-03.md
-- Purpose: normalized, append-only bindings from immutable forecast inputs to
-- individual expert outputs and runtime engine observability.

DO $$
BEGIN
    IF to_regclass('public.forecast_input_snapshots') IS NULL THEN
        RAISE EXCEPTION 'BLOCKED_FORECAST_INPUT_SNAPSHOTS_NOT_FOUND';
    END IF;
    IF to_regclass('public.monthly_expert_forecasts') IS NULL THEN
        RAISE EXCEPTION 'BLOCKED_MONTHLY_EXPERT_FORECASTS_NOT_FOUND';
    END IF;
    IF to_regclass('public.derived_feature_snapshots') IS NULL THEN
        RAISE EXCEPTION 'BLOCKED_DERIVED_FEATURE_SNAPSHOTS_NOT_FOUND';
    END IF;
    IF to_regclass('public.decision_signal_snapshots') IS NULL THEN
        RAISE EXCEPTION 'BLOCKED_DECISION_SIGNAL_SNAPSHOTS_NOT_FOUND';
    END IF;
    IF to_regprocedure('reject_gold_control_forecast_state_mutation()') IS NULL THEN
        RAISE EXCEPTION 'BLOCKED_FORECAST_IMMUTABILITY_GUARD_NOT_FOUND';
    END IF;
END
$$;

-- There must be no already-issued expert/input state when V1 is introduced.
-- This makes migration fail closed rather than silently inventing relationships.
DO $$
DECLARE
    n_inputs bigint;
    n_experts bigint;
BEGIN
    SELECT count(*) INTO n_inputs FROM forecast_input_snapshots;
    SELECT count(*) INTO n_experts FROM monthly_expert_forecasts;
    IF n_inputs <> 0 OR n_experts <> 0 THEN
        RAISE EXCEPTION 'BLOCKED_DATA_SPINE_REQUIRES_EXPLICIT_EXISTING_ROW_RECONCILIATION:inputs=% experts=%', n_inputs, n_experts;
    END IF;
END
$$;

CREATE TABLE IF NOT EXISTS forecast_input_sets (
    input_set_id uuid PRIMARY KEY,
    target_month date NOT NULL,
    forecast_origin timestamptz NOT NULL,
    as_of timestamptz NOT NULL,
    forecast_track text NOT NULL CHECK (forecast_track IN ('MONTH_END_EXPERT','EARLY_INDICATIVE')),
    expert_id text NOT NULL CHECK (expert_id IN ('CAUSAL_PATCH','VW_MIDAS_MSVR','MOMENTUM_3M','RANDOM_WALK')),
    model_name text NOT NULL,
    model_version text NOT NULL,
    evidence_class text NOT NULL CHECK (evidence_class IN ('PROSPECTIVE_SHADOW','LIVE_PRODUCTION')),
    input_fingerprint text NOT NULL CHECK (length(input_fingerprint) > 0),
    git_commit text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT forecast_input_sets_target_month_chk
      CHECK (target_month = date_trunc('month', target_month::timestamptz)::date),
    CONSTRAINT forecast_input_sets_time_chk CHECK (as_of >= forecast_origin),
    CONSTRAINT forecast_input_sets_month_end_time_chk
      CHECK (forecast_track <> 'MONTH_END_EXPERT' OR as_of = forecast_origin),
    UNIQUE (target_month, forecast_track, as_of, expert_id, model_version)
);

CREATE INDEX IF NOT EXISTS forecast_input_sets_identity_idx
    ON forecast_input_sets (expert_id, model_version, target_month DESC, as_of DESC);

ALTER TABLE forecast_input_snapshots
    ADD COLUMN IF NOT EXISTS input_set_id uuid;

ALTER TABLE forecast_input_snapshots
    DROP CONSTRAINT IF EXISTS forecast_input_snapshots_forecast_origin_target_period_mode_key;

ALTER TABLE forecast_input_snapshots
    DROP CONSTRAINT IF EXISTS forecast_input_snapshots_input_set_id_fkey;
ALTER TABLE forecast_input_snapshots
    ADD CONSTRAINT forecast_input_snapshots_input_set_id_fkey
    FOREIGN KEY (input_set_id) REFERENCES forecast_input_sets(input_set_id) ON DELETE RESTRICT;

ALTER TABLE forecast_input_snapshots
    ALTER COLUMN input_set_id SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS forecast_input_snapshots_set_semantic_uidx
    ON forecast_input_snapshots (
        input_set_id,
        series_id,
        COALESCE(semantic_id,''),
        observation_ts,
        transform
    );

CREATE TABLE IF NOT EXISTS forecast_input_set_members (
    input_set_id uuid NOT NULL REFERENCES forecast_input_sets(input_set_id) ON DELETE RESTRICT,
    snapshot_id bigint NOT NULL REFERENCES forecast_input_snapshots(id) ON DELETE RESTRICT,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (input_set_id, snapshot_id),
    UNIQUE (snapshot_id)
);

ALTER TABLE monthly_expert_forecasts
    ADD COLUMN IF NOT EXISTS input_set_id uuid;

ALTER TABLE monthly_expert_forecasts
    DROP CONSTRAINT IF EXISTS monthly_expert_forecasts_input_set_id_fkey;
ALTER TABLE monthly_expert_forecasts
    ADD CONSTRAINT monthly_expert_forecasts_input_set_id_fkey
    FOREIGN KEY (input_set_id) REFERENCES forecast_input_sets(input_set_id) ON DELETE RESTRICT;

ALTER TABLE monthly_expert_forecasts
    ALTER COLUMN input_set_id SET NOT NULL;

CREATE OR REPLACE FUNCTION enforce_gold_control_input_snapshot_binding()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    s forecast_input_sets%ROWTYPE;
BEGIN
    SELECT * INTO s FROM forecast_input_sets WHERE input_set_id = NEW.input_set_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'BLOCKED_INPUT_SET_NOT_FOUND:%', NEW.input_set_id;
    END IF;
    IF NEW.forecast_origin IS DISTINCT FROM s.forecast_origin THEN
        RAISE EXCEPTION 'BLOCKED_INPUT_SET_FORECAST_ORIGIN_MISMATCH';
    END IF;
    IF NEW.target_period IS DISTINCT FROM to_char(s.target_month, 'YYYY-MM') THEN
        RAISE EXCEPTION 'BLOCKED_INPUT_SET_TARGET_PERIOD_MISMATCH';
    END IF;
    IF NEW.model_name IS DISTINCT FROM s.model_name OR NEW.model_version IS DISTINCT FROM s.model_version THEN
        RAISE EXCEPTION 'BLOCKED_INPUT_SET_MODEL_IDENTITY_MISMATCH';
    END IF;
    IF NEW.available_as_of > s.as_of OR NEW.retrieved_at > s.as_of THEN
        RAISE EXCEPTION 'BLOCKED_INPUT_SET_PIT_VIOLATION';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_forecast_input_snapshot_binding ON forecast_input_snapshots;
CREATE TRIGGER trg_forecast_input_snapshot_binding
BEFORE INSERT ON forecast_input_snapshots
FOR EACH ROW EXECUTE FUNCTION enforce_gold_control_input_snapshot_binding();

CREATE OR REPLACE FUNCTION register_gold_control_input_set_member()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO forecast_input_set_members(input_set_id, snapshot_id)
    VALUES (NEW.input_set_id, NEW.id);
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_forecast_input_set_member ON forecast_input_snapshots;
CREATE TRIGGER trg_forecast_input_set_member
AFTER INSERT ON forecast_input_snapshots
FOR EACH ROW EXECUTE FUNCTION register_gold_control_input_set_member();

CREATE OR REPLACE FUNCTION enforce_gold_control_expert_input_set_binding()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    s forecast_input_sets%ROWTYPE;
    db_ids bigint[];
    row_ids bigint[];
BEGIN
    SELECT * INTO s FROM forecast_input_sets WHERE input_set_id = NEW.input_set_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'BLOCKED_EXPERT_INPUT_SET_NOT_FOUND:%', NEW.input_set_id;
    END IF;

    IF NEW.target_month IS DISTINCT FROM s.target_month
       OR NEW.forecast_origin IS DISTINCT FROM s.forecast_origin
       OR NEW.as_of IS DISTINCT FROM s.as_of
       OR NEW.forecast_track IS DISTINCT FROM s.forecast_track
       OR NEW.expert_id IS DISTINCT FROM s.expert_id
       OR NEW.model_name IS DISTINCT FROM s.model_name
       OR NEW.model_version IS DISTINCT FROM s.model_version
       OR NEW.evidence_class IS DISTINCT FROM s.evidence_class THEN
        RAISE EXCEPTION 'BLOCKED_EXPERT_INPUT_SET_IDENTITY_MISMATCH';
    END IF;

    IF NEW.input_fingerprint IS DISTINCT FROM s.input_fingerprint THEN
        RAISE EXCEPTION 'BLOCKED_EXPERT_INPUT_SET_FINGERPRINT_MISMATCH';
    END IF;

    SELECT array_agg(snapshot_id ORDER BY snapshot_id)
      INTO db_ids
      FROM forecast_input_set_members
     WHERE input_set_id = NEW.input_set_id;

    SELECT array_agg(x ORDER BY x)
      INTO row_ids
      FROM unnest(NEW.input_snapshot_ids) AS x;

    IF db_ids IS NULL OR cardinality(db_ids) = 0 THEN
        RAISE EXCEPTION 'BLOCKED_EXPERT_INPUT_SET_EMPTY';
    END IF;
    IF db_ids IS DISTINCT FROM row_ids THEN
        RAISE EXCEPTION 'BLOCKED_EXPERT_INPUT_SET_MEMBERSHIP_MISMATCH';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_monthly_expert_input_set_binding ON monthly_expert_forecasts;
CREATE TRIGGER trg_monthly_expert_input_set_binding
BEFORE INSERT ON monthly_expert_forecasts
FOR EACH ROW EXECUTE FUNCTION enforce_gold_control_expert_input_set_binding();

CREATE OR REPLACE FUNCTION reject_gold_control_data_spine_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'GOLD_CONTROL_DATA_SPINE_APPEND_ONLY:%', TG_TABLE_NAME;
END;
$$;

DROP TRIGGER IF EXISTS trg_forecast_input_sets_immutable ON forecast_input_sets;
CREATE TRIGGER trg_forecast_input_sets_immutable
BEFORE UPDATE OR DELETE ON forecast_input_sets
FOR EACH ROW EXECUTE FUNCTION reject_gold_control_data_spine_mutation();

DROP TRIGGER IF EXISTS trg_forecast_input_set_members_immutable ON forecast_input_set_members;
CREATE TRIGGER trg_forecast_input_set_members_immutable
BEFORE UPDATE OR DELETE ON forecast_input_set_members
FOR EACH ROW EXECUTE FUNCTION reject_gold_control_data_spine_mutation();

CREATE TABLE IF NOT EXISTS engine_execution_runs (
    run_id uuid PRIMARY KEY,
    engine_id text NOT NULL CHECK (engine_id IN (
        'CAUSAL_PATCH','VW_MIDAS_MSVR','MOMENTUM_3M','RANDOM_WALK',
        'MONTHLY_DIRECTION_3M','FAST','SLOW','MACRO_EVENT',
        'EMERGENCY_LEVEL','EMERGENCY_REVERSAL','BOCPD','GVZ_RISK'
    )),
    engine_version text NOT NULL,
    engine_role text NOT NULL,
    as_of timestamptz NOT NULL,
    target_context text,
    evidence_class text NOT NULL CHECK (evidence_class IN (
        'RUNTIME_GOVERNANCE_AUDIT','HISTORICAL_REPLAY','LATE_BOOTSTRAP_SHADOW_CONTEXT',
        'PROSPECTIVE_SHADOW','LIVE_PRODUCTION'
    )),
    runtime_status text NOT NULL CHECK (runtime_status IN ('ACTIVE','ISSUED','WAITING','BLOCKED','NOT_PROVEN')),
    status_code text NOT NULL CHECK (length(status_code) > 0),
    direction_vote_permitted boolean NOT NULL DEFAULT false,
    git_commit text,
    input_fingerprint text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS engine_execution_runs_identity_uidx
    ON engine_execution_runs (
        engine_id, engine_version, as_of, COALESCE(target_context,''), evidence_class, status_code
    );
CREATE INDEX IF NOT EXISTS engine_execution_runs_latest_idx
    ON engine_execution_runs (engine_id, as_of DESC, created_at DESC);

CREATE TABLE IF NOT EXISTS engine_execution_derived_outputs (
    run_id uuid NOT NULL REFERENCES engine_execution_runs(run_id) ON DELETE RESTRICT,
    derived_feature_snapshot_id bigint NOT NULL REFERENCES derived_feature_snapshots(id) ON DELETE RESTRICT,
    PRIMARY KEY (run_id, derived_feature_snapshot_id),
    UNIQUE (derived_feature_snapshot_id)
);

CREATE TABLE IF NOT EXISTS engine_execution_expert_outputs (
    run_id uuid NOT NULL REFERENCES engine_execution_runs(run_id) ON DELETE RESTRICT,
    monthly_expert_forecast_id bigint NOT NULL REFERENCES monthly_expert_forecasts(id) ON DELETE RESTRICT,
    PRIMARY KEY (run_id, monthly_expert_forecast_id),
    UNIQUE (monthly_expert_forecast_id)
);

CREATE TABLE IF NOT EXISTS engine_execution_decision_outputs (
    run_id uuid NOT NULL REFERENCES engine_execution_runs(run_id) ON DELETE RESTRICT,
    decision_snapshot_id uuid NOT NULL REFERENCES decision_signal_snapshots(snapshot_id) ON DELETE RESTRICT,
    PRIMARY KEY (run_id, decision_snapshot_id),
    UNIQUE (decision_snapshot_id)
);

DROP TRIGGER IF EXISTS trg_engine_execution_runs_immutable ON engine_execution_runs;
CREATE TRIGGER trg_engine_execution_runs_immutable
BEFORE UPDATE OR DELETE ON engine_execution_runs
FOR EACH ROW EXECUTE FUNCTION reject_gold_control_data_spine_mutation();

DROP TRIGGER IF EXISTS trg_engine_execution_derived_outputs_immutable ON engine_execution_derived_outputs;
CREATE TRIGGER trg_engine_execution_derived_outputs_immutable
BEFORE UPDATE OR DELETE ON engine_execution_derived_outputs
FOR EACH ROW EXECUTE FUNCTION reject_gold_control_data_spine_mutation();

DROP TRIGGER IF EXISTS trg_engine_execution_expert_outputs_immutable ON engine_execution_expert_outputs;
CREATE TRIGGER trg_engine_execution_expert_outputs_immutable
BEFORE UPDATE OR DELETE ON engine_execution_expert_outputs
FOR EACH ROW EXECUTE FUNCTION reject_gold_control_data_spine_mutation();

DROP TRIGGER IF EXISTS trg_engine_execution_decision_outputs_immutable ON engine_execution_decision_outputs;
CREATE TRIGGER trg_engine_execution_decision_outputs_immutable
BEFORE UPDATE OR DELETE ON engine_execution_decision_outputs
FOR EACH ROW EXECUTE FUNCTION reject_gold_control_data_spine_mutation();

CREATE OR REPLACE VIEW latest_engine_runtime_state AS
SELECT DISTINCT ON (engine_id)
    run_id, engine_id, engine_version, engine_role, as_of, target_context,
    evidence_class, runtime_status, status_code, direction_vote_permitted,
    git_commit, input_fingerprint, metadata, created_at
FROM engine_execution_runs
ORDER BY engine_id, as_of DESC, created_at DESC, run_id DESC;

CREATE OR REPLACE VIEW data_evidence_spine_health_v1 AS
SELECT
    (SELECT count(*) FROM forecast_input_sets) AS input_sets,
    (SELECT count(*) FROM forecast_input_snapshots) AS input_snapshots,
    (SELECT count(*) FROM forecast_input_set_members) AS input_members,
    (SELECT count(*) FROM monthly_expert_forecasts) AS expert_forecasts,
    (SELECT count(*) FROM engine_execution_runs) AS engine_runs,
    (SELECT count(*) FROM derived_feature_snapshots) AS derived_features,
    (SELECT count(*) FROM monthly_forecast_contracts) AS canonical_forecasts,
    (SELECT count(*) FROM decision_signal_snapshots) AS decision_snapshots,
    (SELECT count(*)
       FROM forecast_input_snapshots f
       LEFT JOIN forecast_input_set_members m ON m.snapshot_id=f.id
      WHERE m.snapshot_id IS NULL) AS orphan_input_snapshots,
    (SELECT count(*)
       FROM monthly_expert_forecasts e
       LEFT JOIN forecast_input_sets s ON s.input_set_id=e.input_set_id
      WHERE s.input_set_id IS NULL) AS expert_rows_without_input_set,
    (SELECT count(*)
       FROM monthly_expert_forecasts e
       JOIN forecast_input_sets s ON s.input_set_id=e.input_set_id
      WHERE e.input_fingerprint IS DISTINCT FROM s.input_fingerprint) AS expert_input_fingerprint_mismatches;

COMMENT ON TABLE forecast_input_sets IS
'Gold Control Data Evidence Spine V1: immutable header for one exact expert/as-of input set. Repeated Early Indicative revisions use distinct as_of/input_set identities.';
COMMENT ON TABLE forecast_input_set_members IS
'Normalized immutable membership between sealed forecast input sets and semantic forecast_input_snapshots.';
COMMENT ON TABLE engine_execution_runs IS
'Append-only runtime status ledger for all 12 governed Gold Control motors. Status-only rows are legitimate and do not imply a forecast/decision output.';
COMMENT ON VIEW latest_engine_runtime_state IS
'Read-only latest persisted runtime status per governed engine. It does not select experts or authorize a final decision.';
COMMENT ON VIEW data_evidence_spine_health_v1 IS
'Read-only integrity/count surface for the Gold Control Data Evidence Spine V1.';
