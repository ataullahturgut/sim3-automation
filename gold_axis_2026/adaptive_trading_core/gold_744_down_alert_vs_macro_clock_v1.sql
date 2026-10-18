-- GOLD-ADAPTIVE-MODEL-APP-01
-- Pure SELECT reproducing the full 744-alert timeline 2023-2025.
-- No trades, no future outcomes permitted as real-time input.
-- Macros: 93 time-stamped CPI/NFP/FOMC release references,
-- gold_research_r72_claude_macro_analogs_v1, firstprint vintage NOT certified.
-- After-24h macro column is EVALUATION ONLY (future at alert time).
-- Following 480 recorded M15 bars are NOT five guaranteed whole sessions.
-- Many alarms and forward outcomes overlap. The five-minute and sixteen-hour etc.
-- clock standards should be read explicitly as data times, not causal proof.
WITH quotes AS (
 SELECT bar_start_utc + INTERVAL '15 minutes' AS closed_at,
 (bid_close + ask_close) / 2.0 AS mid,
 LAG(bar_start_utc) OVER(ORDER BY bar_start_utc) AS prior_start,
 LAG((bid_close+ask_close)/2.0) OVER(ORDER BY bar_start_utc) AS prior_mid
 FROM gold_research_evduka_xau15m_bidask_candidate
 WHERE bar_start_utc >= '2023-01-01'
   AND bar_start_utc < '2026-01-01'
),
segmented AS (
 SELECT q.*,
 SUM(CASE WHEN prior_start IS NULL
              OR closed_at-prior_start <> INTERVAL '30 minutes'
          THEN 1 ELSE 0 END)
   OVER(ORDER BY closed_at) AS segment_id
 FROM quotes q
),
rolling AS (
 SELECT s.*,
 COUNT(*) OVER(PARTITION BY segment_id
               ORDER BY closed_at ROWS BETWEEN 95 PRECEDING AND CURRENT ROW) AS n_history,
 MAX(mid) OVER(PARTITION BY segment_id
               ORDER BY closed_at ROWS BETWEEN 95 PRECEDING AND CURRENT ROW) AS rolling_max
 FROM segmented s
),
drawdowns AS (
 SELECT r.*,
 CASE WHEN n_history >= 17 THEN 100*LN(rolling_max/mid) END AS drawdown_pct,
 CASE WHEN prior_start IS NOT NULL
            AND closed_at-prior_start <> INTERVAL '30 minutes'
            AND mid/prior_mid <= 0.995
      THEN 1 ELSE 0 END AS gap_down
 FROM rolling r
),
episodes AS (
 SELECT d.*,
 SUM(CASE WHEN (n_history >= 17 AND drawdown_pct < 0.20)
               OR (prior_start IS NOT NULL AND closed_at-prior_start <> INTERVAL '30 minutes')
          THEN 1 ELSE 0 END)
 OVER(ORDER BY closed_at) AS fall_episode_id
 FROM drawdowns d
),
alarms AS (
 SELECT DISTINCT ON(fall_episode_id)
   closed_at AS alarm_utc,mid AS price_mid,gap_down
 FROM episodes
 WHERE (n_history >= 17 AND drawdown_pct >= 0.50) OR gap_down=1
 ORDER BY fall_episode_id,closed_at
),
future_path AS (
 SELECT closed_at,
 COUNT(mid) OVER(ORDER BY closed_at
      ROWS BETWEEN 1 FOLLOWING AND 480 FOLLOWING) AS forward_n,
 MIN(mid) OVER(ORDER BY closed_at
      ROWS BETWEEN 1 FOLLOWING AND 480 FOLLOWING) AS forward_min
 FROM quotes
),
macro_clock AS (
 SELECT ts,etype FROM gold_research_r72_claude_macro_analogs_v1
 WHERE ts >= '2023-01-01' AND ts < '2026-01-01'
)
SELECT
 a.alarm_utc,a.price_mid,a.gap_down,
 ARRAY(SELECT m.etype||'@'||to_char(m.ts AT TIME ZONE 'UTC','YYYY-MM-DD HH24:MI')
       FROM macro_clock m
       WHERE m.ts<=a.alarm_utc AND m.ts>a.alarm_utc-INTERVAL '4 hours'
       ORDER BY m.ts DESC) AS macro_before_4h,
 ARRAY(SELECT m.etype||'@'||to_char(m.ts AT TIME ZONE 'UTC','YYYY-MM-DD HH24:MI')
       FROM macro_clock m
       WHERE m.ts<=a.alarm_utc AND m.ts>a.alarm_utc-INTERVAL '24 hours'
       ORDER BY m.ts DESC) AS macro_before_24h,
 ARRAY(SELECT m.etype||'@'||to_char(m.ts AT TIME ZONE 'UTC','YYYY-MM-DD HH24:MI')
       FROM macro_clock m
       WHERE m.ts<=a.alarm_utc AND m.ts>a.alarm_utc-INTERVAL '72 hours'
       ORDER BY m.ts DESC) AS macro_before_72h,
 ARRAY(SELECT m.etype||'@'||to_char(m.ts AT TIME ZONE 'UTC','YYYY-MM-DD HH24:MI')
       FROM macro_clock m
       WHERE m.ts>a.alarm_utc AND m.ts<=a.alarm_utc+INTERVAL '24 hours'
       ORDER BY m.ts) AS macro_after_24h__FUTURE_LABEL_ONLY,
 CASE WHEN f.forward_n=480 THEN f.forward_min/a.price_mid<=0.96 END
   AS new_4pct_fall_in_next_480_observed_M15__FUTURE_LABEL_ONLY,
 CASE WHEN f.forward_n=480 THEN 100*(f.forward_min/a.price_mid-1) END
   AS worst_return_in_next_480_M15_pct__FUTURE_LABEL_ONLY,
 FALSE AS news_firstprint_verified,
 FALSE AS economic_causality_established,
 FALSE AS trade_allowed
FROM alarms a JOIN future_path f ON f.closed_at=a.alarm_utc
ORDER BY a.alarm_utc;
