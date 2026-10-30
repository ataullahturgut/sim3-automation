-- 2026-10-30: original BASE14/CFTC21/V22 research-only pipeline.
-- Separate, append-only source/research. These are never canonical live
-- weekly_forecast_records or downside_signal_records.

CREATE SCHEMA IF NOT EXISTS gold_weekly_live;

CREATE TABLE IF NOT EXISTS gold_weekly_live.cftc_gc_si_futuresonly_official_v1 (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 market text NOT NULL CHECK(market IN ('GC','SI')),
 contract_code text NOT NULL CHECK(contract_code IN ('088691','084691')),
 report_date date NOT NULL,
 open_interest numeric(20,4) NOT NULL CHECK(open_interest>0),
 managed_money_long numeric(20,4) NOT NULL CHECK(managed_money_long>=0),
 managed_money_short numeric(20,4) NOT NULL CHECK(managed_money_short>=0),
 managed_money_net_over_oi numeric(24,12) NOT NULL,
 managed_money_short_over_oi numeric(24,12) NOT NULL,
 api_dataset text NOT NULL DEFAULT '72hh-3qpy' CHECK(api_dataset='72hh-3qpy'),
 raw_row_sha256 text NOT NULL CHECK(raw_row_sha256~'^[a-f0-9]{64}$'),
 retrieved_utc timestamptz NOT NULL DEFAULT now(),
 earliest_model_use_date date NOT NULL,
 historical_firstprint_verified boolean NOT NULL DEFAULT false
    CHECK(historical_firstprint_verified=false),
 source_url text NOT NULL,
 UNIQUE(market,report_date,raw_row_sha256)
);

CREATE TABLE IF NOT EXISTS gold_weekly_live.staktrakr_v22_risk_shadow_v1 (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 origin_date date NOT NULL,
 scenario text NOT NULL CHECK(scenario IN (
  'AM_MIXED_FIX_REFERENCE_NOT_SAME_SERIES',
  'PM_MIXED_CLOSE_REFERENCE_NOT_SAME_SERIES')),
 source_sha256 text NOT NULL CHECK(source_sha256~'^[a-f0-9]{64}$'),
 base14_level text NOT NULL CHECK(base14_level IN ('NORMAL','YELLOW','RED')),
 base14_score double precision NOT NULL,
 cftc21_level text NOT NULL CHECK(cftc21_level IN ('NORMAL','YELLOW','RED')),
 cftc21_score double precision NOT NULL,
 v22_level text NOT NULL CHECK(v22_level IN (
 'ACTIVE_REVIEW','CONTINUATION_REVIEW','FRAGILITY_WATCH',
 'ORIGINAL_RED_REVIEW_ONLY','NO_ACTIONABLE_REVIEW')),
 effective_review boolean NOT NULL,
 evidence jsonb NOT NULL CHECK(jsonb_typeof(evidence)='object'),
 recorded_utc timestamptz NOT NULL DEFAULT now(),
 evidence_class text NOT NULL DEFAULT 'RESEARCH_SHADOW_NOT_FIRSTPRINT'
  CHECK(evidence_class='RESEARCH_SHADOW_NOT_FIRSTPRINT'),
 is_production_signal boolean NOT NULL DEFAULT false
  CHECK(is_production_signal=false),
 UNIQUE(origin_date,scenario,source_sha256)
);

-- The next two tables are created by their own dedicated source/ANN migrations:
-- gold_weekly_live.staktrakr_daily_utc_reference_v1
-- gold_weekly_live.staktrakr_v34_ann_shadow_v1
-- The installed view gold_weekly_live.gold_research_model_panel_v1 combines
-- scenario-consensus risk history with forecast research shadow. It never
-- emits a live buy/sell recommendation.
