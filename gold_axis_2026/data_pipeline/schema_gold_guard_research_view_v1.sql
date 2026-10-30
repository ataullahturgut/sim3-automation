-- Gold Control -> GOLD/GUARD model read-only research contract, 2026-10-30
-- Depends on append-only research tables. No canonical live issuance and no
-- forecast/model re-training. Nulls represent no recorded result, not zero.
CREATE OR REPLACE VIEW gold_weekly_live.gold_research_model_panel_v1 AS
WITH risk_recent AS (
 SELECT DISTINCT ON (origin_date,scenario)
  origin_date,scenario,base14_level,base14_score,
  cftc21_level,cftc21_score,v22_level,effective_review,recorded_utc
 FROM gold_weekly_live.staktrakr_v22_risk_shadow_v1
 ORDER BY origin_date,scenario,recorded_utc DESC,id DESC
), risk_consensus AS (
 SELECT origin_date,count(DISTINCT scenario) AS scenario_count,
  CASE WHEN count(DISTINCT scenario)=2 AND count(DISTINCT base14_level)=1
   THEN min(base14_level) ELSE 'UNVERIFIED_SCENARIO_DIFFERENCE' END AS base14_level,
  CASE WHEN count(DISTINCT scenario)=2 AND count(DISTINCT cftc21_level)=1
   THEN min(cftc21_level) ELSE 'UNVERIFIED_SCENARIO_DIFFERENCE' END AS cftc21_level,
  CASE WHEN count(DISTINCT scenario)=2 AND count(DISTINCT v22_level)=1
   THEN min(v22_level) ELSE 'UNVERIFIED_SCENARIO_DIFFERENCE' END AS v22_level,
  CASE WHEN count(DISTINCT scenario)=2 AND count(DISTINCT effective_review)=1
   THEN bool_or(effective_review) ELSE NULL END AS v22_priority_review,
  max(recorded_utc) AS recorded_at_utc
 FROM risk_recent GROUP BY origin_date
), ann_recent AS (
 SELECT DISTINCT ON (target_week)
  target_week,origin_week,forecast_week_mean_usd_oz,
  forecast_week_last_shared_day_usd_oz,generated_at_utc
 FROM gold_weekly_live.staktrakr_v34_ann_shadow_v1
 ORDER BY target_week,generated_at_utc DESC,id DESC
)
SELECT 'RISK_BASE14_CFTC21_V22'::text AS model_group,
 origin_date AS reference_date,
 NULL::numeric AS forecast_mean_usd_oz,
 NULL::numeric AS forecast_last_day_usd_oz,
 base14_level,cftc21_level,v22_level,v22_priority_review,
 'RESEARCH_SHADOW_NOT_FIRSTPRINT'::text AS evidence_class,
 false AS production_live,recorded_at_utc,scenario_count
FROM risk_consensus
UNION ALL
SELECT 'WEEKLY_ANN_V34'::text,target_week,
 forecast_week_mean_usd_oz,forecast_week_last_shared_day_usd_oz,
 NULL::text,NULL::text,NULL::text,NULL::boolean,
 'RESEARCH_BACKFILL_SHADOW_NOT_FIRSTPRINT'::text,
 false,generated_at_utc,NULL::bigint
FROM ann_recent;
