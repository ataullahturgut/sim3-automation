-- S2 slow session daily aggregate. READ-ONLY, 2023-2025 retro discovery only.
-- Shift UTC +2 hours: Sunday evening belongs to Monday session.
-- RESEARCH cutoff UTC22, NOT verified exchange settlement/real-time vintage.
-- Output contains historical gold close_price: KEEP PRIVATE; no GitHub raw data.
WITH raw AS (
 SELECT (bar_start_utc+interval '2 hours')::date AS trading_session,
 source_id,bar_start_utc,close_price,native_minute_bars,
 lag(bar_start_utc) OVER(
  PARTITION BY (bar_start_utc+interval '2 hours')::date,source_id
  ORDER BY bar_start_utc) AS prev_time
 FROM gold_research_histdata_xau15m_candidate
 WHERE bar_start_utc >= '2023-01-01' AND bar_start_utc < '2026-01-01'
)
SELECT trading_session::text AS session,source_id,
 COUNT(*)::int AS n,
 COUNT(*) FILTER(WHERE native_minute_bars=15)::int AS full_n,
 MIN(bar_start_utc) AS first_bar,
 MAX(bar_start_utc) AS last_bar,
 (array_agg(close_price ORDER BY bar_start_utc DESC))[1] AS close_price,
 (array_agg(native_minute_bars ORDER BY bar_start_utc DESC))[1] AS last_native_minute_bars,
 COALESCE(MAX(EXTRACT(epoch FROM (bar_start_utc-prev_time))/60),0) AS max_gap_minutes
FROM raw
GROUP BY 1,2
ORDER BY 1,2;
