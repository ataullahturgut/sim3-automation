-- GOLD V34 ANN 2026-10-30: historical replay and research-only
-- weekday conditioning. Already installed in Gold Control; this file is the
-- idempotent non-destructive DDL contract for re-creation.
-- Historical archive: exact 147 GitHub original V34 shard0..3 CSV rows,
-- source ref research/gold-v34-forward-parity-safe-20261030,
-- research date 2026-10-27, scenario EXTERNAL_CLOSE_ONLY_SENSITIVITY.
-- Never promote these rows to firstprint, canonical NY17 or bank AL/SAT.
CREATE SCHEMA IF NOT EXISTS gold_weekly_live;
CREATE TABLE IF NOT EXISTS gold_weekly_live.v34_ann_historical_replay_v1 (
 target_week date PRIMARY KEY,
 origin_week date NOT NULL,
 forecast_mean_usd_oz numeric(18,6) NOT NULL CHECK(forecast_mean_usd_oz>0),
 actual_mean_usd_oz numeric(18,6) NOT NULL CHECK(actual_mean_usd_oz>0),
 forecast_last_usd_oz numeric(18,6) NOT NULL CHECK(forecast_last_usd_oz>0),
 actual_last_usd_oz numeric(18,6) NOT NULL CHECK(actual_last_usd_oz>0),
 training_weeks integer NOT NULL CHECK(training_weeks>550),
 feature_dim integer NOT NULL CHECK(feature_dim=16),
 model_id text NOT NULL CHECK(model_id='WEEKLY_H1_ANN_MLP8_TANH_ALPHA1_V1'),
 evidence_class text NOT NULL DEFAULT 'RETROSPECTIVE_MODEL_REPLAY_NOT_FIRSTPRINT'
  CHECK(evidence_class='RETROSPECTIVE_MODEL_REPLAY_NOT_FIRSTPRINT'),
 research_source text NOT NULL
  CHECK(research_source='V34_FROZEN_20261027_EXTERNAL_CLOSE_ONLY_SENSITIVITY'),
 original_model_frozen boolean NOT NULL DEFAULT true CHECK(original_model_frozen),
 historical_firstprint_certified boolean NOT NULL DEFAULT false CHECK(historical_firstprint_certified=false),
 production_live boolean NOT NULL DEFAULT false CHECK(production_live=false),
 source_row_sha256 text NOT NULL CHECK(source_row_sha256~'^[a-f0-9]{64}$'),
 evidence jsonb NOT NULL,
 imported_utc timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS gold_weekly_live.v34_ann_intraweek_estimates_v1 (
 target_week date NOT NULL,asof_price_date date NOT NULL,
 observed_weekdays smallint NOT NULL CHECK(observed_weekdays BETWEEN 1 AND 4),
 remaining_weekdays smallint NOT NULL CHECK(remaining_weekdays BETWEEN 1 AND 4),
 first_ann_mean_usd_oz numeric(18,6) NOT NULL CHECK(first_ann_mean_usd_oz>0),
 conditioned_week_mean_usd_oz numeric(18,6) NOT NULL CHECK(conditioned_week_mean_usd_oz>0),
 observed_price_sum_usd_oz numeric(20,6) NOT NULL CHECK(observed_price_sum_usd_oz>0),
 source_forecast_class text NOT NULL CHECK(source_forecast_class IN (
 'RETROSPECTIVE_V34_REPLAY','FORWARD_RESEARCH_SHADOW')),
 evidence_class text NOT NULL CHECK(evidence_class IN (
 'HISTORICAL_CONDITIONING_NOT_ORIGIN_FIRSTPRINT',
 'FORWARD_CONDITIONING_FIRST_CAPTURE_NOT_PRODUCTION')),
 calculation_version text NOT NULL DEFAULT 'SIMPLE_FIVE_WEEKDAY_ACCOUNTING_V1'
 CHECK(calculation_version='SIMPLE_FIVE_WEEKDAY_ACCOUNTING_V1'),
 source_firstprint_certified boolean NOT NULL DEFAULT false CHECK(source_firstprint_certified=false),
 production_live boolean NOT NULL DEFAULT false CHECK(production_live=false),
 captured_utc timestamptz NOT NULL DEFAULT now(),
 evidence jsonb NOT NULL,
 PRIMARY KEY(target_week,asof_price_date,source_forecast_class),
 CHECK(observed_weekdays+remaining_weekdays=5),
 CHECK(asof_price_date>=target_week AND asof_price_date<target_week+4)
);
-- Formula: (observed Mon..day sum + forecast_remainder * (5-k))/5.
-- Only Mon..Thu may be research conditioned; Friday is realized, not forecast.
-- Daily scheduled writer: gold_v34_weekday_conditioned_shadow_v1.py
-- It only consumes a pre-week first captured original V34 research shadow.
