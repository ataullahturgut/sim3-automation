-- Historical gold event-chain H03/H15 research source queries (read-only)
-- Database: Neon Gold Control; 2026-10-13.
-- Exact 15-minute bid/ask mid for EV, HistData close for HIST; NY 17:00 session date
-- Skip sparse/partial NY17 sessions (<70 15m bars) and weekends.
-- NOTE: research-provider historical data retrieved later; no contemporaneous archive receipt proof.

WITH quotes AS (
 SELECT 'EV' src, bar_start_utc,
        (bid_close+ask_close)/2 AS mid,
        ((bar_start_utc+interval '15 minutes') AT TIME ZONE 'America/New_York'+interval '7 hours')::date AS session_date
 FROM gold_research_evduka_xau15m_bidask_candidate
 WHERE bar_start_utc>='2020-01-01' AND bar_start_utc<'2026-01-03'
 UNION ALL
 SELECT 'HIST',bar_start_utc,close_price,
        ((bar_start_utc+interval '15 minutes') AT TIME ZONE 'America/New_York'+interval '7 hours')::date
 FROM gold_research_histdata_xau15m_candidate
 WHERE bar_start_utc>='2020-01-01' AND bar_start_utc<'2026-10-02'
), ranked AS (
 SELECT *, row_number() over(partition by src,session_date order by bar_start_utc desc) AS rn
 FROM quotes
)
SELECT src,session_date,count(*) AS bars,
       max(mid) FILTER (WHERE rn=1) AS ny17_mid_close
FROM ranked
WHERE extract(isodow from session_date)<6
GROUP BY src,session_date
HAVING count(*)>=70
ORDER BY src,session_date;

-- Third-party LBMA-labelled daily fixing, stored as research reconstruction with
-- original_timestamp 12:00 London and available_as_of uniformly in Sep 2026.
-- NOT a NY17 series; must not pool with the above without separate timing evidence.
SELECT observation_ts::date AS fixing_date, value AS research_fix,
       metadata->>'original_timestamp' AS source_local_timestamp,
       available_as_of, source
FROM observations
WHERE series_id='XAU_STAKTRAKR_RESEARCH_DAILY_R1'
  AND observation_ts BETWEEN '2016-01-01' AND '2025-12-31'
ORDER BY observation_ts;

-- Alternative 2026 hourly reconstructed Twelve Data NY17 research close.
-- Date labels fixed at 21:00 UTC even in winter; exclude weekends and verify clock.
SELECT observation_ts::date AS day_label,value AS twelve_hourly_derived_close,
       available_as_of
FROM observations
WHERE series_id='XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1'
  AND observation_ts>='2025-01-01' AND observation_ts<'2026-09-01'
  AND extract(isodow FROM observation_ts)<6
ORDER BY observation_ts;

-- Exogenous macro news coding universe. FOMC historical USMPD VALUE loaded in
-- Sep 2026, not an ex-ante shock measurement. Event DATE only is usable.
SELECT series_id,observation_ts,available_as_of
FROM observations
WHERE series_id IN (
 'MACRO_CPI_ACTUAL_FIRST_PRINT','MACRO_NFP_ACTUAL_FIRST_PRINT',
 'MACRO_FOMC_USMPD_MP1'
)
AND observation_ts>='2016-01-01' AND observation_ts<'2026-10-01'
AND (observation_ts<'2023-01-01' OR observation_ts>='2026-01-01')
ORDER BY observation_ts;
