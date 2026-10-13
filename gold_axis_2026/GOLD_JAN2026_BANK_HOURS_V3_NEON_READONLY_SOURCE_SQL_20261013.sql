-- BANK-HOUR JAN2026 V3 — precise SOURCE SQL, READ ONLY
-- Primary: EV Duke bidask-mid XAU 2022-25. Jan2026: HIST M15.
-- Bank 16:30TR cutoff = last completed bar starting at 16:15 Europe/Istanbul;
-- first next quote = bar starting 16:30; an optional delayed fill is bar ending 16:45.
-- No XAG/XPT/XPD 15m panel authenticated in connected Neon.
WITH bars AS (
 SELECT 'EV' src,bar_start_utc,
    (bar_start_utc AT TIME ZONE 'Europe/Istanbul')::date AS bank_date,
    (bar_start_utc AT TIME ZONE 'Europe/Istanbul')::time AS bank_time,
    (bid_close+ask_close)/2 AS close_px,
    (bid_open+ask_open)/2 AS open_px,
    (bid_high+ask_high)/2 AS high_px,
    (bid_low+ask_low)/2 AS low_px
 FROM gold_research_evduka_xau15m_bidask_candidate
 WHERE bar_start_utc>='2022-01-01' AND bar_start_utc<'2026-01-01'
 UNION ALL
 SELECT 'HIST',bar_start_utc,
    (bar_start_utc AT TIME ZONE 'Europe/Istanbul')::date,
    (bar_start_utc AT TIME ZONE 'Europe/Istanbul')::time,
    close_price,open_price,high_price,low_price
 FROM gold_research_histdata_xau15m_candidate
 WHERE bar_start_utc>='2025-09-01' AND bar_start_utc<'2026-02-01'
), bank AS (
 SELECT *,
 MAX(high_px) OVER(PARTITION BY src,bank_date ORDER BY bar_start_utc
   ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) high_sofar
 FROM bars
 WHERE bank_time BETWEEN '09:00:00' AND '16:30:00'
   AND EXTRACT(ISODOW FROM bank_date)<=5
), day AS (
 SELECT src,bank_date,
 COUNT(*) FILTER(WHERE bank_time<='16:15:00') prior_completed_bars,
 MAX(close_px) FILTER(WHERE bank_time='16:15:00') cutoff_close_1630_tr,
 MAX(open_px) FILTER(WHERE bank_time='16:30:00') hypothetical_immediate_quote_open_1630_tr,
 MAX(close_px) FILTER(WHERE bank_time='16:30:00') hypothetical_delayed_quote_close_1645_tr,
 MAX(close_px) FILTER(WHERE bank_time='09:00:00') morning_first_bar_close_0915_tr,
 MAX(high_px) FILTER(WHERE bank_time<='16:15:00') high_up_to_1630,
 MIN(low_px) FILTER(WHERE bank_time<='16:15:00') low_up_to_1630,
 MIN(100*(low_px/high_sofar-1)) FILTER(WHERE bank_time<='16:15:00') ordered_dd_until_1630
 FROM bank GROUP BY src,bank_date
), eligible AS (
 SELECT *,LAG(cutoff_close_1630_tr) OVER(PARTITION BY src ORDER BY bank_date) last_bank_cutoff
 FROM day
 WHERE prior_completed_bars>=26
 AND cutoff_close_1630_tr>0
 AND hypothetical_immediate_quote_open_1630_tr>0
)
SELECT src,bank_date,prior_completed_bars,
 cutoff_close_1630_tr/COALESCE(last_bank_cutoff,cutoff_close_1630_tr) close_factor,
 hypothetical_immediate_quote_open_1630_tr/COALESCE(last_bank_cutoff,cutoff_close_1630_tr) exec_first_open_factor,
 hypothetical_delayed_quote_close_1645_tr / cutoff_close_1630_tr AS next_1645_over_cutoff1630,
 high_up_to_1630/COALESCE(last_bank_cutoff,cutoff_close_1630_tr) high_factor,
 low_up_to_1630/COALESCE(last_bank_cutoff,cutoff_close_1630_tr) low_factor,
 ordered_dd_until_1630
FROM eligible ORDER BY src,bank_date;

-- Separate strict intra-bar ordering QA: uses high from STRICTLY PREVIOUS
-- 15m bank bars, rather than same-bar high that may occur after same-bar low.
-- MAX(high_px) OVER(PARTITION BY src,bank_date ORDER BY bar_start_utc
--  ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS prior_bar_high
-- then MIN(100*(low_px/prior_bar_high-1)).
-- Exact quote first-publication / bank ask-bid not available; do not assert PIT.
