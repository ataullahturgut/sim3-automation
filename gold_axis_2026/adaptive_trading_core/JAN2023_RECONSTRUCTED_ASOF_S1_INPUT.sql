-- READ-ONLY / historical reconstructed as-of bar timing, NOT true vintage/PIT.
-- Run in user's connected Neon database. Do NOT commit result rows or licensed raw prices.
-- Complete XAU M15 bar known earliest at bar_start+15m; CME H1 known
-- earliest at ts_event+1h (must audit CME OHLCV ts_event semantics before OOS).
-- H1 market features only if latest complete H1 <= asof and <=75min old.
-- Continuous future-adjusted CME data may include ex-post roll knowledge.
WITH xb AS (
 SELECT bar_start_utc,bar_start_utc+interval '15 minutes' AS end_utc,
 close_price,source_id,native_minute_bars,
 lag(close_price,4) OVER(ORDER BY bar_start_utc) AS close_1h_before,
 lag(bar_start_utc,4) OVER(ORDER BY bar_start_utc) AS start_1h_before,
 min(native_minute_bars) OVER(ORDER BY bar_start_utc ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) AS min_native
 FROM gold_research_histdata_xau15m_candidate
 WHERE bar_start_utc >= '2023-01-01' AND bar_start_utc < '2023-02-01'
),
anchors AS (
 SELECT * FROM xb WHERE min_native=15
 AND start_1h_before=bar_start_utc-interval '1 hour'
 AND EXTRACT(MINUTE FROM end_utc)=0
 AND (EXTRACT(HOUR FROM end_utc)::integer%4)=0
),
h1 AS (
 SELECT symbol,source_id,ts_event+interval '1 hour' AS known_end_utc,
 lag(ts_event) OVER(PARTITION BY symbol ORDER BY ts_event) AS previous_start,
 ts_event,100*ln(close/nullif(lag(close) OVER(PARTITION BY symbol ORDER BY ts_event),0)) AS ret_1h
 FROM gold_research_cme_glbx_futures_2023_2026_h1_5roots_continuous_c
 WHERE ts_event >= '2022-12-30' AND ts_event < '2023-02-01'
)
SELECT a.end_utc,a.bar_start_utc,a.close_price,a.source_id,
 100*ln(a.close_price/a.close_1h_before) AS gold_1h_pct,
 nq.ret_1h AS nq_1h_pct,zn.ret_1h AS zn_1h_pct,cl.ret_1h AS cl_1h_pct,
 nq.known_end_utc AS nq_end,zn.known_end_utc AS zn_end,cl.known_end_utc AS cl_end
FROM anchors a
LEFT JOIN LATERAL (
 SELECT * FROM h1 WHERE symbol='NQ.c.0'
 AND ts_event-previous_start=interval '1 hour'
 AND known_end_utc<=a.end_utc AND known_end_utc>=a.end_utc-interval '75 minutes'
 ORDER BY known_end_utc DESC LIMIT 1
) nq ON TRUE
LEFT JOIN LATERAL (
 SELECT * FROM h1 WHERE symbol='ZN.c.0'
 AND ts_event-previous_start=interval '1 hour'
 AND known_end_utc<=a.end_utc AND known_end_utc>=a.end_utc-interval '75 minutes'
 ORDER BY known_end_utc DESC LIMIT 1
) zn ON TRUE
LEFT JOIN LATERAL (
 SELECT * FROM h1 WHERE symbol='CL.c.0'
 AND ts_event-previous_start=interval '1 hour'
 AND known_end_utc<=a.end_utc AND known_end_utc>=a.end_utc-interval '75 minutes'
 ORDER BY known_end_utc DESC LIMIT 1
) cl ON TRUE
ORDER BY a.end_utc;
