-- GOLD JAN2026 RISK V2 — SOURCE AUTHORITY: Neon read-only query
-- Source: EV (2022-2025) and HistData (2025Aug-Jan2026). NO use of 2026 event manifest.
-- Use only already COMPLETED NY17 15min bars at decision t. Intraday daily
-- ordered high-to-subsequent-low = min_j(low[j]/running_max_high_through_j -1).
-- M15 bid/ask midpoint research quote is NOT a Turkish bank executable BID/ASK.
-- Correct NY17 labels: last completed bar ending 17NY belongs to ending day.
-- HistData 'EST_FIXED_UTC_MINUS_05' is winter clock valid Jan2026;
-- HIST 2025 summer warmup's NY17 grouping needs provider DST QC.
WITH b AS(
 SELECT 'EV' AS src,
 ((bar_start_utc+INTERVAL '15 minutes') AT TIME ZONE 'America/New_York'
    + INTERVAL '7 hours'-INTERVAL '1 microsecond')::date AS d,
 bar_start_utc,(bid_close+ask_close)/2 AS px,
 (bid_high+ask_high)/2 AS hi,(bid_low+ask_low)/2 AS lo
 FROM gold_research_evduka_xau15m_bidask_candidate
 WHERE bar_start_utc>='2022-01-01' AND bar_start_utc<'2026-01-01'
 UNION ALL
 SELECT 'HIST',
 ((bar_start_utc+INTERVAL '15 minutes') AT TIME ZONE 'America/New_York'
    + INTERVAL '7 hours'-INTERVAL '1 microsecond')::date,
 bar_start_utc,close_price,high_price,low_price
 FROM gold_research_histdata_xau15m_candidate
 WHERE bar_start_utc>='2025-08-01' AND bar_start_utc<'2026-02-01'
), ordered AS (
 SELECT *,max(hi) OVER(PARTITION BY src,d ORDER BY bar_start_utc
 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) hi_sofar FROM b
), daily AS (
 SELECT src,d,count(*) bars,
 (array_agg(px ORDER BY bar_start_utc))[1] first_px,
 (array_agg(px ORDER BY bar_start_utc DESC))[1] close_px,
 max(hi) day_high,min(lo) day_low,
 min(100*(lo/hi_sofar-1)) sequential_ordered_drawdown_pct,
 max(bar_start_utc) last_completed_bar_start
 FROM ordered
 GROUP BY src,d HAVING COUNT(*)>=70 AND EXTRACT(ISODOW FROM d) BETWEEN 1 AND 5
), ratios AS (
 SELECT *,lag(close_px) OVER(PARTITION BY src ORDER BY d) prev_close
 FROM daily
)
SELECT src,d,bars,
 first_px/COALESCE(prev_close,close_px) open_factor,
 close_px/COALESCE(prev_close,close_px) close_factor,
 day_high/COALESCE(prev_close,close_px) high_factor,
 day_low/COALESCE(prev_close,close_px) low_factor,
 sequential_ordered_drawdown_pct,last_completed_bar_start
FROM ratios ORDER BY src,d;

-- For the Jan29 intraday *time* inspection (NOT pre-frozen end-day model),
-- derive running high/ordered drawdown at EACH bar of 2026-01-29 and
-- calculate current close_from_running_high. Alarm first crosses at the M15
-- bar_start 2026-01-29 15:00 UTC, visible only after 15:15 UTC completion.
-- Original first time after 17:00 Turkey bank low-spread trading window.
