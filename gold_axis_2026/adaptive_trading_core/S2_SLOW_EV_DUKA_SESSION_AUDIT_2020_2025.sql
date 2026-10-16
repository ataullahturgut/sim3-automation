-- EVTRADINGLABS/DUKASCOPY recovered M15 bid+ask: alternative S2-only archive.
-- NEON READ-ONLY. No interpolation, no vendor merging, no native M1 assertion.
-- This SQL emits private reconstructed prices; never commit its output.
-- Fixed UTC+2 research session convention and UTC22 cut, NOT official settlement.
WITH source_rows AS (
 SELECT (bar_start_utc+interval '2 hours')::date AS d,source_id,
        bar_start_utc,bid_close,ask_close,
        LAG(bar_start_utc) OVER (
          PARTITION BY (bar_start_utc+interval '2 hours')::date,source_id
          ORDER BY bar_start_utc
        ) AS previous_bar
 FROM gold_research_evduka_xau15m_bidask_candidate
 WHERE bar_start_utc>='2020-01-01' AND bar_start_utc<'2026-01-01'
), session_stats AS (
 SELECT d,source_id,COUNT(*)::int n,
  COUNT(*) FILTER (WHERE bid_close>0 AND ask_close>=bid_close)::int valid_quotes,
  MIN(bar_start_utc) first_bar,MAX(bar_start_utc) last_bar,
  MAX(COALESCE(EXTRACT(EPOCH FROM(bar_start_utc-previous_bar))/60,0)) max_gap_minutes,
  (array_agg((bid_close+ask_close)/2 ORDER BY bar_start_utc DESC))[1] close_price,
  (array_agg((bid_close>0 AND ask_close>=bid_close) ORDER BY bar_start_utc DESC))[1] terminal_bar_valid
 FROM source_rows GROUP BY d,source_id
)
SELECT d::text AS session,source_id,n,valid_quotes,first_bar,last_bar,
 max_gap_minutes,close_price,terminal_bar_valid,
 'BIDASK_M15_RECONSTRUCTED_NOT_M1' AS "sessionEvidence"
FROM session_stats
WHERE EXTRACT(ISODOW FROM d) BETWEEN 1 AND 5
ORDER BY d,source_id;
