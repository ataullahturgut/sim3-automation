-- RESEARCH ONLY. Read-only Neon Gold Control. Derive price-agnostic daily ratio
-- sequence reproducing AL/SAT/TUT returns; raw third-party price data remain upstream.
-- 2023/24 DEV, 2025 validation, Jan26 previously exposed stress.
-- Correct NY17 as exact 17:00 local M15 completion belongs to ENDING day.
-- Every quoted bar must be completed by the as-of decision; actual source downloaded later.
WITH b AS(
 SELECT 'EV' AS source,((bar_start_utc +interval '15 minutes') AT TIME ZONE
  'America/New_York'+interval '7 hours'-interval '1 microsecond')::date AS d,
  bar_start_utc,
  (bid_close+ask_close)/2 AS p,(bid_high+ask_high)/2 AS high,
  (bid_low+ask_low)/2 AS low
 FROM gold_research_evduka_xau15m_bidask_candidate
 WHERE bar_start_utc>='2022-01-01' AND bar_start_utc<'2026-01-01'
 UNION ALL
 SELECT 'HIST',
  ((bar_start_utc+interval '15 minutes') AT TIME ZONE
   'America/New_York'+interval '7 hours'-interval '1 microsecond')::date,
   bar_start_utc,close_price,high_price,low_price
 FROM gold_research_histdata_xau15m_candidate
 WHERE bar_start_utc>='2025-09-01' AND bar_start_utc<'2026-02-01'
), sequenced AS(
 SELECT *,MAX(high) OVER(PARTITION BY source,d ORDER BY bar_start_utc
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) run_high
 FROM b
), dates AS(
 SELECT source,d,COUNT(*) AS bars,
  (ARRAY_AGG(p ORDER BY bar_start_utc))[1] AS opening_quote,
  (ARRAY_AGG(p ORDER BY bar_start_utc DESC))[1] AS latest_completed_quote,
  MIN(100*(low/run_high-1)) AS sequential_intraday_high_to_later_low_pct
 FROM sequenced
 GROUP BY source,d HAVING COUNT(*)>=70 AND extract(isodow FROM d)<6
), normalized AS (
 SELECT *,LAG(latest_completed_quote) OVER(PARTITION BY source ORDER BY d) prev_close
 FROM dates
)
SELECT source,d,bars,
 opening_quote / COALESCE(prev_close,latest_completed_quote) AS opening_quote_over_previous_close,
 latest_completed_quote / COALESCE(prev_close,latest_completed_quote) AS latest_close_over_previous_close,
 sequential_intraday_high_to_later_low_pct
FROM normalized
ORDER BY source,d;

-- All signal features (r3/r5/r20/r60,SMA10/20/50/60,rolling 10/60 highs,
-- ordered intraday drawdown) only use same/prior date completed session
-- observations; next-session execution uses normalized opening_quote (not prior close).
-- HistData source EST_FIXED_UTC_MINUS_05: DST mismatch outside January 2026.
-- In the January window UTC−05 is compatible with America/New_York.
