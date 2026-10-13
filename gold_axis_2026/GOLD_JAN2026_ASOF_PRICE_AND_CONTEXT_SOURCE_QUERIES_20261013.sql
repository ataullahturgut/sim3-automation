-- Gold Jan2026 retrospective as-of source, READ ONLY.
-- HistData XAU15m from user's Neon Gold Control project.
-- 2025 Nov/Dec warmup and Jan 2026 results; DO NOT join 2026 events/manifest.
-- SOURCE TIMEZONE: EST_FIXED_UTC_MINUS_05; January DST=off.
-- Gold NY17 bar-ending timestamp belongs to session just ENDING at 17ET,
-- hence -1 microsecond before date-of(+7h) conversion.
WITH raw AS (
 SELECT
 ((bar_start_utc+INTERVAL '15 minutes') AT TIME ZONE 'America/New_York'
   +INTERVAL '7 hours' -INTERVAL '1 microsecond')::date AS ny17_day,
 bar_start_utc, open_price, high_price, low_price, close_price
 FROM gold_research_histdata_xau15m_candidate
 WHERE bar_start_utc >= '2025-11-01'
 AND bar_start_utc < '2026-02-01'
)
SELECT ny17_day, COUNT(*) AS bars,
 (ARRAY_AGG(close_price ORDER BY bar_start_utc ASC))[1] AS next_session_first_quote,
 (ARRAY_AGG(close_price ORDER BY bar_start_utc DESC))[1] AS completed_ny17_close,
 MIN(bar_start_utc) first_bar_utc, MAX(bar_start_utc) last_bar_utc
FROM raw GROUP BY ny17_day ORDER BY ny17_day;

-- Independent Jan 2026 Dukascopy coverage QC; missing dates DO NOT copy-fill
WITH b AS (
 SELECT ((bar_start_utc+INTERVAL '15 minutes') AT TIME ZONE 'America/New_York'
   +INTERVAL '7 hours' -INTERVAL '1 microsecond')::date AS ny17_day,
 bar_start_utc,(bid_close+ask_close)/2 mid
 FROM gold_research_dukascopy_2026_direct_m1_m15_bidask_v2
 WHERE bar_start_utc >= '2026-01-01' AND bar_start_utc<'2026-02-01'
)
SELECT ny17_day, COUNT(*) bars,(ARRAY_AGG(mid ORDER BY bar_start_utc DESC))[1] last_mid
FROM b GROUP BY ny17_day ORDER BY ny17_day;

-- External metal/risk date proxies (retrospectively ingested, not Jan PIT)
SELECT series_id,observation_ts,value,available_as_of
FROM observations
WHERE series_id IN ('XAG_STAKTRAKR_RESEARCH_DAILY_R1',
'XPT_STAKTRAKR_RESEARCH_DAILY_R1','XPD_STAKTRAKR_RESEARCH_DAILY_R1',
'NASDAQ100_FRED','SP500_FRED','DTWEXBGS_FRB_H10','DGS10_FRB_H15')
AND observation_ts >= '2025-12-01' AND observation_ts<'2026-02-01'
ORDER BY series_id,observation_ts;
