-- H3A annual read-only extraction. Replace only YYYY (year), never change window rules.
-- Strict observed XAU/USD EV-Dukascopy M15 complete DAY/OVN bars.
WITH bars AS (
 SELECT bar_start_utc, bar_start_utc AT TIME ZONE 'Europe/Istanbul' trt,
 (bid_close+ask_close)/2.0 mid,
 (bid_close>0 AND ask_close>=bid_close AND bid_open>0 AND ask_open>=bid_open) valid
 FROM gold_research_evduka_xau15m_bidask_candidate
 WHERE bar_start_utc>='YYYY-01-01' AND bar_start_utc<'YYYY_NEXT-01-02'
), series AS (
 SELECT bar_start_utc,mid,valid,
 (CASE WHEN trt::time<'09:00' THEN trt::date-1 ELSE trt::date END)::date dt,
 CASE WHEN trt::time>='09:00' AND trt::time<'16:45' THEN 'DAY' ELSE 'OVN' END sn
 FROM bars
), lagged AS (
 SELECT *, LAG(mid) OVER(PARTITION BY dt,sn ORDER BY bar_start_utc) pm,
 LAG(bar_start_utc) OVER(PARTITION BY dt,sn ORDER BY bar_start_utc) pt
 FROM series
), summary AS (
 SELECT dt,sn,count(*) n, count(*) FILTER(WHERE NOT valid) bad,
 count(*) FILTER(WHERE pt IS NOT NULL AND bar_start_utc-pt=interval '15 minutes') n15,
 count(*) FILTER(WHERE pt IS NOT NULL AND bar_start_utc-pt=interval '75 minutes') n75,
 min(bar_start_utc) first_bar,max(bar_start_utc) last_bar,
 sum(CASE WHEN pt IS NOT NULL AND bar_start_utc-pt=interval '15 minutes' AND pm>0 AND mid>0 THEN POWER(LN(mid/pm),2) ELSE 0 END) rv
 FROM lagged
 WHERE (sn='DAY' AND extract(isodow FROM dt)<=5)
 OR (sn='OVN' AND extract(isodow FROM dt)<=4)
 GROUP BY 1,2
)
SELECT to_char(dt,'YYYY-MM-DD') decision_date,sn AS session,n,n15,n75,rv
FROM summary
WHERE dt>='YYYY-01-01' AND dt<'YYYY_NEXT-01-01' AND bad=0 AND rv>0
AND (
 (sn='DAY' AND n=31 AND n15=30 AND (first_bar AT TIME ZONE 'Europe/Istanbul')::time='09:00' AND (last_bar AT TIME ZONE 'Europe/Istanbul')::time='16:30')
 OR
 (sn='OVN' AND n=61 AND n15=59 AND n75=1 AND (first_bar AT TIME ZONE 'Europe/Istanbul')::time='16:45' AND (last_bar AT TIME ZONE 'Europe/Istanbul')::time='08:45')
)
ORDER BY dt,sn;
