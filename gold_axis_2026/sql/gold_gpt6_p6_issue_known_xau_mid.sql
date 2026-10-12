-- Exact as-of XAU/USD spot M15 MID CLOSE 15 minutes BEFORE issue to avoid theoretical zero latency.
-- Replace YYYY YYNEXT by year/year+1, both DAY/OVN issue times independent of P1 outcomes.
WITH calendar AS (
 SELECT gs::date d FROM generate_series('YYYY-01-01'::date, 'YYNEXT-01-01'::date-interval '1 day',interval '1 day') gs
), issue AS (
 SELECT d, sn, ((d::timestamp + issue_time) AT TIME ZONE 'Europe/Istanbul') issue_utc
 FROM calendar CROSS JOIN (VALUES ('DAY',time '08:45'),('OVN',time '16:30')) w(sn,issue_time)
 WHERE (sn='DAY' AND extract(isodow FROM d)<=5) OR (sn='OVN' AND extract(isodow FROM d)<=4)
)
SELECT to_char(i.d,'YYYY-MM-DD') trade_date,i.sn,
 i.issue_utc, b.bar_start_utc issue_reference_bar_start_utc,
 b.bid_close,b.ask_close,(b.bid_close+b.ask_close)/2.0 issue_mid
FROM issue i
JOIN gold_research_evduka_xau15m_bidask_candidate b
ON b.bar_start_utc=i.issue_utc-interval '30 minutes'
WHERE b.bid_close>0 AND b.ask_close>=b.bid_close
ORDER BY i.d,i.sn;
