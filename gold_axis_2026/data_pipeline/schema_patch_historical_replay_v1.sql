BEGIN;

ALTER TABLE forecast_input_sets
  DROP CONSTRAINT forecast_input_sets_forecast_track_check,
  DROP CONSTRAINT forecast_input_sets_evidence_class_check;

ALTER TABLE forecast_input_sets
  ADD CONSTRAINT forecast_input_sets_forecast_track_check
    CHECK (forecast_track = ANY (ARRAY['MONTH_END_EXPERT'::text, 'EARLY_INDICATIVE'::text, 'HISTORICAL_REPLAY'::text])),
  ADD CONSTRAINT forecast_input_sets_evidence_class_check
    CHECK (evidence_class = ANY (ARRAY['PROSPECTIVE_SHADOW'::text, 'LIVE_PRODUCTION'::text, 'HISTORICAL_REPLAY'::text])),
  ADD CONSTRAINT forecast_input_sets_replay_pair_chk
    CHECK (
      (forecast_track = 'HISTORICAL_REPLAY' AND evidence_class = 'HISTORICAL_REPLAY')
      OR
      (forecast_track <> 'HISTORICAL_REPLAY' AND evidence_class IN ('PROSPECTIVE_SHADOW','LIVE_PRODUCTION'))
    ),
  ADD CONSTRAINT forecast_input_sets_replay_time_chk
    CHECK (forecast_track <> 'HISTORICAL_REPLAY' OR as_of > forecast_origin),
  ADD CONSTRAINT forecast_input_sets_replay_metadata_chk
    CHECK (
      forecast_track <> 'HISTORICAL_REPLAY'
      OR (
        metadata->>'historical_replay' = 'true'
        AND metadata->>'prospective_claim' = 'false'
        AND metadata ? 'information_cutoff'
        AND metadata ? 'replay_executed_at'
        AND (metadata->>'information_cutoff')::timestamptz = forecast_origin
        AND (metadata->>'replay_executed_at')::timestamptz = as_of
      )
    );

ALTER TABLE monthly_expert_forecasts
  DROP CONSTRAINT monthly_expert_forecasts_forecast_track_check,
  DROP CONSTRAINT monthly_expert_forecasts_evidence_class_check;

ALTER TABLE monthly_expert_forecasts
  ADD CONSTRAINT monthly_expert_forecasts_forecast_track_check
    CHECK (forecast_track = ANY (ARRAY['MONTH_END_EXPERT'::text, 'EARLY_INDICATIVE'::text, 'HISTORICAL_REPLAY'::text])),
  ADD CONSTRAINT monthly_expert_forecasts_evidence_class_check
    CHECK (evidence_class = ANY (ARRAY['PROSPECTIVE_SHADOW'::text, 'LIVE_PRODUCTION'::text, 'HISTORICAL_REPLAY'::text])),
  ADD CONSTRAINT monthly_expert_forecasts_replay_pair_chk
    CHECK (
      (forecast_track = 'HISTORICAL_REPLAY' AND evidence_class = 'HISTORICAL_REPLAY')
      OR
      (forecast_track <> 'HISTORICAL_REPLAY' AND evidence_class IN ('PROSPECTIVE_SHADOW','LIVE_PRODUCTION'))
    ),
  ADD CONSTRAINT monthly_expert_forecasts_replay_time_chk
    CHECK (forecast_track <> 'HISTORICAL_REPLAY' OR as_of > forecast_origin),
  ADD CONSTRAINT monthly_expert_forecasts_replay_provenance_chk
    CHECK (
      forecast_track <> 'HISTORICAL_REPLAY'
      OR (
        provenance->>'historical_replay' = 'true'
        AND provenance->>'prospective_claim' = 'false'
        AND provenance ? 'information_cutoff'
        AND provenance ? 'replay_executed_at'
        AND (provenance->>'information_cutoff')::timestamptz = forecast_origin
        AND (provenance->>'replay_executed_at')::timestamptz = as_of
      )
    );

CREATE OR REPLACE VIEW latest_engine_runtime_state AS
SELECT DISTINCT ON (engine_id)
       run_id,
       engine_id,
       engine_version,
       engine_role,
       as_of,
       target_context,
       evidence_class,
       runtime_status,
       status_code,
       direction_vote_permitted,
       git_commit,
       input_fingerprint,
       metadata,
       created_at
FROM engine_execution_runs
WHERE evidence_class <> 'HISTORICAL_REPLAY'
ORDER BY engine_id, as_of DESC, created_at DESC, run_id DESC;

CREATE OR REPLACE VIEW latest_historical_replay_engine_state AS
SELECT DISTINCT ON (engine_id, target_context)
       run_id,
       engine_id,
       engine_version,
       engine_role,
       as_of,
       target_context,
       evidence_class,
       runtime_status,
       status_code,
       direction_vote_permitted,
       git_commit,
       input_fingerprint,
       metadata,
       created_at
FROM engine_execution_runs
WHERE evidence_class = 'HISTORICAL_REPLAY'
ORDER BY engine_id, target_context, as_of DESC, created_at DESC, run_id DESC;

COMMIT;
