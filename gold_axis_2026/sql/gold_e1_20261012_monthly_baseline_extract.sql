-- Source extraction for GOLD_E1_20261012_MONTHLY_KNOWN_SEGMENT_INPUT_ROWS.csv
-- Read-only. Stak archived first-publication time not certified. Query frozen ChHHO per-origin values
-- from GitHub Actions artifact 11049132605 separately; do NOT use actuals to construct forecasts.
WITH s AS (SELECT date_trunc('month',observation_ts AT TIME ZONE 'UTC')::date m,AVG(value) a,
 (array_agg(value ORDER BY observation_ts DESC))[1] e,
 (array_agg(observation_ts ORDER BY observation_ts DESC))[1] last_ts, COUNT(*) n
 FROM observations WHERE series_id='XAU_STAKTRAKR_RESEARCH_DAILY_R1' AND observation_ts>='2022-01-01' AND observation_ts<'2026-08-01' GROUP BY 1),
 w AS (SELECT date_trunc('month',observation_ts AT TIME ZONE 'UTC')::date m,value y FROM observations WHERE series_id='CORE5_GOLD_USD_OZ_RESEARCH_R1' AND observation_ts>='2022-01-01' AND observation_ts<'2026-08-01')
 SELECT to_char(t.m,'YYYY-MM') target,w.y actual,p.a origin_stak_avg,p.e origin_stak_last,p.n origin_stak_days,to_char(p.last_ts AT TIME ZONE 'UTC','YYYY-MM-DD') origin_last_date,wprev.y origin_wb_avg
 FROM s t JOIN w ON w.m=t.m JOIN s p ON p.m=t.m-interval '1 month' JOIN w wprev ON wprev.m=p.m
 WHERE t.m>='2022-04-01' AND t.m<='2026-07-01' ORDER BY t.m;
