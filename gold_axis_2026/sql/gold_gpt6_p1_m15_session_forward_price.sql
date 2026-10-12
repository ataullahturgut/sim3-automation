-- Replace YYYY/YYNEXT only; strict 2020–25 EV-Dukascopy XAU/USD bar completeness.
WITH bars AS (
 SELECT bar_start_utc, bar_start_utc AT TIME ZONE 'Europe/Istanbul' trt,
 (bid_open+ask_open)/2.0 open_mid,(bid_close+ask_close)/2.0 close_mid,
 (bid_open>0 AND ask_open>=bid_open AND bid_close>0 AND ask_close>=bid_close) valid
 FROM gold_research_evduka_xau15m_bidask_candidate
 WHERE bar_start_utc>='YYYY-01-01' AND bar_start_utc<'YYNEXT-01-02'
), dated AS (
 SELECT *, (CASE WHEN trt::time<'09:00' THEN trt::date-1 ELSE trt::date END)::date d,
 CASE WHEN trt::time>='09:00' AND trt::time<'16:45' THEN 'DAY' ELSE 'OVN' END sn
 FROM bars
), lagged AS (
 SELECT *, lag(bar_start_utc) OVER(PARTITION BY d,sn ORDER BY bar_start_utc) pts,
 lag(close_mid) OVER(PARTITION BY d,sn ORDER BY bar_start_utc) pcm
 FROM dated
), agg AS (
 SELECT d,sn,count(*) n,
 count(*) FILTER(WHERE NOT valid) invalid,
 count(*) FILTER(WHERE pts IS NOT NULL AND bar_start_utc-pts=interval '15 minutes') n15,
 count(*) FILTER(WHERE pts IS NOT NULL AND bar_start_utc-pts=interval '75 minutes') n75,
 min(bar_start_utc) first_ts,max(bar_start_utc) last_ts,
 (array_agg(open_mid ORDER BY bar_start_utc))[1] entry,
 (array_agg(close_mid ORDER BY bar_start_utc DESC))[1] exit,
 sum(CASE WHEN pcm>0 AND close_mid>0 AND pts IS NOT NULL AND bar_start_utc-pts=interval '15 minutes' THEN power(ln(close_mid/pcm),2) ELSE 0 END) rv
 FROM lagged WHERE (sn='DAY' AND extract(isodow FROM d)<=5) OR (sn='OVN' AND extract(isodow FROM d)<=4) GROUP BY 1,2
)
SELECT to_char(d,'YYYY-MM-DD') AS trade_date,sn,
 CASE WHEN sn='DAY' THEN ((d::timestamp+time '08:45') AT TIME ZONE 'Europe/Istanbul') ELSE ((d::timestamp+time '16:30') AT TIME ZONE 'Europe/Istanbul') END issue_utc,
 entry,exit,ln(exit/entry) realized_r,rv,n,n15,n75
FROM agg WHERE d>='YYYY-01-01' AND d<'YYNEXT-01-01'
AND invalid=0 AND entry>0 AND exit>0 AND rv>0 AND
((sn='DAY' AND n=31 AND n15=30 AND (first_ts AT TIME ZONE 'Europe/Istanbul')::time='09:00' AND (last_ts AT TIME ZONE 'Europe/Istanbul')::time='16:30')
OR (sn='OVN' AND n=61 AND n15=59 AND n75=1 AND (first_ts AT TIME ZONE 'Europe/Istanbul')::time='16:45' AND (last_ts AT TIME ZONE 'Europe/Istanbul')::time='08:45'))
ORDER BY d,sn;
