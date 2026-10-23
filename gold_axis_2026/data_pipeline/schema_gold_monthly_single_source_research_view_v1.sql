-- Reproducible, non-destructive source-exclusive monthly research VIEW.
-- Applied in Neon on 2026-10-23. This does not rewrite or delete any observations.
-- STAKTRAKR LBMA/seed is only an archival label, not verified original LBMA price.
-- MIXED months are rejected wholesale; valid months require 4 matched weekday metals.
CREATE OR REPLACE VIEW public.gold_monthly_four_metals_single_source_research_v1 AS
WITH raw AS (
 SELECT id AS raw_observation_id, series_id, observation_ts::date AS price_date,
        date_trunc('month',observation_ts)::date AS month_start, value,
        source, metadata->>'payload_provider_label' AS provider_label,
        metadata->>'payload_source_label' AS payload_source_label
 FROM public.observations
 WHERE series_id IN (
   'XAU_STAKTRAKR_RESEARCH_DAILY_R1',
   'XAG_STAKTRAKR_RESEARCH_DAILY_R1',
   'XPT_STAKTRAKR_RESEARCH_DAILY_R1',
   'XPD_STAKTRAKR_RESEARCH_DAILY_R1'
 ) AND observation_ts >= '2010-01-01' AND observation_ts < '2026-10-01'
),
pure_months AS (
 SELECT month_start FROM raw
 GROUP BY month_start
 HAVING COUNT(*) FILTER (WHERE
     provider_label IS DISTINCT FROM 'LBMA'
     OR payload_source_label IS DISTINCT FROM 'seed'
     OR source IS DISTINCT FROM 'lbruton/StakTrakr@ed2e549f82ba0d1cd3ca32842b82d3888d301e01'
     OR EXTRACT(ISODOW FROM price_date)>5
  )=0
),
aligned_days AS (
 SELECT r.month_start, r.price_date
 FROM raw r JOIN pure_months m USING(month_start)
 GROUP BY r.month_start,r.price_date
 HAVING COUNT(*)=4 AND COUNT(DISTINCT r.series_id)=4
),
qualified_months AS (
 SELECT month_start
 FROM aligned_days
 GROUP BY month_start HAVING COUNT(*)>=15
)
SELECT r.raw_observation_id,r.series_id,r.price_date,r.month_start,r.value,
       r.source,r.provider_label,r.payload_source_label
FROM raw r
JOIN aligned_days d ON d.month_start=r.month_start AND d.price_date=r.price_date
JOIN qualified_months m ON m.month_start=r.month_start;

-- Non-mutating acceptance audit:
-- Expected at initial migration: 16244 rows, 4061 aligned dates, 193 months,
-- first 2010-01-04 and last 2026-01-30, one labelled archive lineage.
SELECT COUNT(*) AS rows,
       COUNT(DISTINCT price_date) AS aligned_days,
       COUNT(DISTINCT month_start) AS months,
       MIN(price_date) AS first_day,
       MAX(price_date) AS last_day,
       COUNT(DISTINCT source) AS archive_lineages
FROM public.gold_monthly_four_metals_single_source_research_v1;
