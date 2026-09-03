-- GOLD_CONTROL_DATA_EVIDENCE_SPINE_RUNTIME_V1
-- Must be applied after schema_patch_data_evidence_spine_v1.sql.

DO $$
BEGIN
    IF to_regclass('public.engine_execution_runs') IS NULL
       OR to_regclass('public.engine_execution_derived_outputs') IS NULL
       OR to_regclass('public.engine_execution_expert_outputs') IS NULL THEN
        RAISE EXCEPTION 'BLOCKED_DATA_EVIDENCE_SPINE_V1_NOT_APPLIED';
    END IF;
END
$$;

CREATE OR REPLACE FUNCTION register_gold_control_expert_engine_execution()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    runtime_run_id uuid;
    runtime_role text;
    runtime_status_code text;
BEGIN
    runtime_role := CASE WHEN NEW.expert_role='BENCHMARK' THEN 'MONTHLY_H1_BENCHMARK' ELSE 'MONTHLY_H1_EXPERT' END;
    runtime_status_code := NEW.forecast_track || '_ISSUED';

    INSERT INTO engine_execution_runs(
        run_id,engine_id,engine_version,engine_role,as_of,target_context,evidence_class,
        runtime_status,status_code,direction_vote_permitted,git_commit,input_fingerprint,metadata
    ) VALUES (
        gen_random_uuid(),NEW.expert_id,NEW.model_version,runtime_role,NEW.as_of,
        to_char(NEW.target_month,'YYYY-MM'),NEW.evidence_class,'ISSUED',runtime_status_code,
        false,NEW.git_commit,NEW.input_fingerprint,
        jsonb_build_object(
            'forecast_track',NEW.forecast_track,
            'input_set_id',NEW.input_set_id,
            'selector_status',NEW.selector_status,
            'auto_selector',NEW.auto_selector,
            'auto_ensemble',NEW.auto_ensemble,
            'canonical_authority',NEW.canonical_authority,
            'contract','FROZEN_DATA_EVIDENCE_SPINE_V1'
        )
    ) ON CONFLICT DO NOTHING;

    SELECT run_id INTO runtime_run_id
      FROM engine_execution_runs
     WHERE engine_id=NEW.expert_id
       AND engine_version=NEW.model_version
       AND as_of=NEW.as_of
       AND coalesce(target_context,'')=to_char(NEW.target_month,'YYYY-MM')
       AND evidence_class=NEW.evidence_class
       AND status_code=runtime_status_code
     ORDER BY created_at DESC,run_id DESC LIMIT 1;

    IF runtime_run_id IS NULL THEN
        RAISE EXCEPTION 'BLOCKED_EXPERT_RUNTIME_LEDGER_BINDING_FAILED';
    END IF;

    INSERT INTO engine_execution_expert_outputs(run_id,monthly_expert_forecast_id)
    VALUES (runtime_run_id,NEW.id)
    ON CONFLICT DO NOTHING;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_monthly_expert_runtime_ledger ON monthly_expert_forecasts;
CREATE TRIGGER trg_monthly_expert_runtime_ledger
AFTER INSERT ON monthly_expert_forecasts
FOR EACH ROW EXECUTE FUNCTION register_gold_control_expert_engine_execution();

CREATE OR REPLACE FUNCTION register_gold_control_derived_engine_execution()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
    runtime_engine_id text;
    runtime_role text;
    runtime_direction_vote boolean;
    runtime_evidence text;
    runtime_target text;
    runtime_fingerprint text;
    runtime_run_id uuid;
BEGIN
    runtime_engine_id := CASE NEW.feature_name
        WHEN 'MONTHLY_DIRECTION_3M' THEN 'MONTHLY_DIRECTION_3M'
        WHEN 'FAST_STATE' THEN 'FAST'
        WHEN 'SLOW_STATE' THEN 'SLOW'
        WHEN 'GVZ_VALUE' THEN 'GVZ_RISK'
        WHEN 'GVZ_CAP' THEN 'GVZ_RISK'
        WHEN 'GVZ_PANIC' THEN 'GVZ_RISK'
        WHEN 'GVZ_REGIME' THEN 'GVZ_RISK'
        ELSE NULL
    END;
    IF runtime_engine_id IS NULL THEN
        RETURN NEW;
    END IF;

    runtime_role := CASE runtime_engine_id
        WHEN 'MONTHLY_DIRECTION_3M' THEN 'STRATEGIC_DIRECTION_CONTEXT'
        WHEN 'FAST' THEN 'TACTICAL_DIRECTION_CONTEXT'
        WHEN 'SLOW' THEN 'TACTICAL_DIRECTION_CONTEXT'
        WHEN 'GVZ_RISK' THEN 'RISK_ONLY_CONTEXT'
    END;
    runtime_direction_vote := runtime_engine_id IN ('MONTHLY_DIRECTION_3M','FAST','SLOW');
    runtime_target := NULLIF(NEW.metadata->>'target_context','');
    runtime_fingerprint := COALESCE(NULLIF(NEW.metadata->>'input_fingerprint',''),NULLIF(NEW.input_lineage->>'input_fingerprint',''));
    runtime_evidence := CASE
        WHEN NEW.quality_status IN ('HISTORICAL_REPLAY','LATE_BOOTSTRAP_SHADOW_CONTEXT','PROSPECTIVE_SHADOW','LIVE_PRODUCTION')
            THEN NEW.quality_status
        WHEN NEW.metadata->>'evidence_class' IN ('HISTORICAL_REPLAY','LATE_BOOTSTRAP_SHADOW_CONTEXT','PROSPECTIVE_SHADOW','LIVE_PRODUCTION')
            THEN NEW.metadata->>'evidence_class'
        ELSE 'RUNTIME_GOVERNANCE_AUDIT'
    END;

    INSERT INTO engine_execution_runs(
        run_id,engine_id,engine_version,engine_role,as_of,target_context,evidence_class,
        runtime_status,status_code,direction_vote_permitted,git_commit,input_fingerprint,metadata
    ) VALUES (
        gen_random_uuid(),runtime_engine_id,NEW.feature_version,runtime_role,NEW.calculation_ts,
        runtime_target,runtime_evidence,'ACTIVE','STORED_CONTEXT_AVAILABLE',runtime_direction_vote,
        NEW.git_commit,runtime_fingerprint,
        jsonb_build_object(
            'derived_feature_name',NEW.feature_name,
            'derived_quality_status',NEW.quality_status,
            'contract','FROZEN_DATA_EVIDENCE_SPINE_V1'
        )
    ) ON CONFLICT DO NOTHING;

    SELECT run_id INTO runtime_run_id
      FROM engine_execution_runs
     WHERE engine_id=runtime_engine_id
       AND engine_version=NEW.feature_version
       AND as_of=NEW.calculation_ts
       AND coalesce(target_context,'')=coalesce(runtime_target,'')
       AND evidence_class=runtime_evidence
       AND status_code='STORED_CONTEXT_AVAILABLE'
     ORDER BY created_at DESC,run_id DESC LIMIT 1;

    IF runtime_run_id IS NULL THEN
        RAISE EXCEPTION 'BLOCKED_DERIVED_RUNTIME_LEDGER_BINDING_FAILED:%', NEW.feature_name;
    END IF;

    INSERT INTO engine_execution_derived_outputs(run_id,derived_feature_snapshot_id)
    VALUES (runtime_run_id,NEW.id)
    ON CONFLICT DO NOTHING;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_derived_feature_runtime_ledger ON derived_feature_snapshots;
CREATE TRIGGER trg_derived_feature_runtime_ledger
AFTER INSERT ON derived_feature_snapshots
FOR EACH ROW EXECUTE FUNCTION register_gold_control_derived_engine_execution();
