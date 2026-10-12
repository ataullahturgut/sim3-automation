-- 2026 direct Dukascopy M15 (M1 15/15) DAY-only 09:00..16:30 bar START; 16:45 is last bar CLOSE.
WITH b AS (
 SELECT bar_start_utc,
   bar_start_utc AT TIME ZONE 'Europe/Istanbul' local_ts,
   (bid_close+ask_close)/2.0 AS mid_close,
   (bid_open>0 AND bid_close>0 AND ask_open>=bid_open AND ask_close>=bid_close AND m1_matched=15) AS ok
 FROM gold_research_dukascopy_2026_direct_m1_m15_bidask_v2
 WHERE bar_start_utc >= '2026-01-01' AND bar_start_utc < '2026-10-09'
), w AS(
 SELECT local_ts::date tr_date,bar_start_utc,mid_close,ok,
 LAG(mid_close) OVER(PARTITION BY local_ts::date ORDER BY bar_start_utc) prev_mid,
 LAG(bar_start_utc) OVER(PARTITION BY local_ts::date ORDER BY bar_start_utc) prev_ts
 FROM b WHERE local_ts::time>='09:00' AND local_ts::time<'16:45'
 AND EXTRACT(isodow FROM local_ts)<=5
), agg AS (
 SELECT tr_date,COUNT(*) n,COUNT(*) FILTER(WHERE NOT ok) nbad,
 COUNT(*) FILTER(WHERE prev_ts IS NOT NULL AND bar_start_utc-prev_ts=interval '15 minutes') n15,
 MIN((bar_start_utc AT TIME ZONE 'Europe/Istanbul')::time) first_hr,
 MAX((bar_start_utc AT TIME ZONE 'Europe/Istanbul')::time) last_hr,
 SUM(CASE WHEN prev_ts IS NOT NULL AND bar_start_utc-prev_ts=interval '15 minutes'
 AND mid_close>0 AND prev_mid>0 THEN POWER(LN(mid_close/prev_mid),2) ELSE 0 END) rv
 FROM w GROUP BY tr_date
)
SELECT TO_CHAR(tr_date,'YYYY-MM-DD') trade_date, rv, n,n15 FROM agg
WHERE n=31 AND n15=30 AND nbad=0 AND first_hr='09:00' AND last_hr='16:30' AND rv>0
ORDER BY tr_date;
