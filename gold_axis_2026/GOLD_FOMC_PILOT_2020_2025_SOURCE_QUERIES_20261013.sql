-- GOLD FOMC PILOT 2020-2025 SOURCE & DATA ACCEPTANCE QUERIES
-- Neon project winter-art-94880101, read-only; 2026-10-13 audit.
-- Rows published in EVENT_LEVEL_V1 derived CSV; do not redistribute vendor raw price panel.
-- Correct canonical NY17 session label: bar ending at exactly 17:00 ET
-- belongs to the session ending that day (not the new session).
--
-- QUERY A: all USMPD event timestamps, unit=pct points; reconstructed vintage from 2026.
WITH e AS (
 SELECT observation_ts AS t,
 MAX(value) FILTER(WHERE series_id='MACRO_FOMC_GSS_PATH_FROZEN2015') path,
 MAX(value) FILTER(WHERE series_id='MACRO_FOMC_USMPD_MP1') mp1,
 MAX((metadata->>'unscheduled')::int) special
 FROM observations
 WHERE series_id IN ('MACRO_FOMC_GSS_PATH_FROZEN2015','MACRO_FOMC_USMPD_MP1')
   AND observation_ts>='2020-01-01' AND observation_ts<'2026-01-01'
 GROUP BY observation_ts
), b AS (
 SELECT bar_start_utc t,(bid_close+ask_close)/2 p
 FROM gold_research_evduka_xau15m_bidask_candidate
 WHERE bar_start_utc>='2020-01-01' AND bar_start_utc<'2026-01-02'
)
SELECT e.t,e.mp1,e.path,e.special,
 a.p AS p_tminus60,c.p AS p_tminus15,d.p AS p_tplus15,f.p AS p_tplus120
FROM e
LEFT JOIN b a ON a.t=e.t-interval '75 minutes'
LEFT JOIN b c ON c.t=e.t-interval '30 minutes'
LEFT JOIN b d ON d.t=e.t
LEFT JOIN b f ON f.t=e.t+interval '105 minutes'
ORDER BY e.t;

-- QUERY B: pre-event r20 and 60 PREVIOUS completed session returns.
-- Only latest completed NY17 session strictly before the EVENT calendar date.
WITH b AS (
 SELECT ((bar_start_utc+interval '15 minutes') AT TIME ZONE 'America/New_York'
             +interval '7 hours'-interval '1 microsecond')::date d,
 bar_start_utc,(bid_close+ask_close)/2 p,
 row_number() over(
  PARTITION BY ((bar_start_utc+interval '15 minutes') AT TIME ZONE 'America/New_York'
             +interval '7 hours'-interval '1 microsecond')::date
  ORDER BY bar_start_utc DESC) rn
 FROM gold_research_evduka_xau15m_bidask_candidate
 WHERE bar_start_utc>='2020-01-01' AND bar_start_utc<'2026-01-02'
),day AS(
 SELECT d,count(*) n,max(p) FILTER(WHERE rn=1) px FROM b
 GROUP BY d HAVING count(*)>=70 AND extract(isodow FROM d)<6
),ret AS (
 SELECT d,100*(px/lag(px) over(order by d)-1) r1,
 100*(px/lag(px,20) over(order by d)-1) r20 FROM day
),feat AS (
 SELECT d,r20,
 stddev_samp(r1) over(order by d rows between 60 preceding and 1 preceding) sd60,
 count(r1) over(order by d rows between 60 preceding and 1 preceding) n
 FROM ret
), ev AS (
 SELECT observation_ts t FROM observations
 WHERE series_id='MACRO_FOMC_USMPD_MP1'
 AND observation_ts>='2020-01-01' AND observation_ts<'2026-01-01'
)
SELECT ev.t,f.d,f.r20,f.sd60,f.n FROM ev
LEFT JOIN LATERAL (
 SELECT * FROM feat WHERE d<(ev.t AT TIME ZONE 'America/New_York')::date
 ORDER BY d DESC LIMIT 1
) f ON true ORDER BY ev.t;

-- QUERY C: official USMPD statement window is t-10→t+20; with M15 quotes
-- we cannot reproduce that exact window. Sensitivity: t-15→t+30 (45min).
WITH ev AS (
 SELECT observation_ts t FROM observations
 WHERE series_id='MACRO_FOMC_USMPD_MP1'
 AND observation_ts>='2020-01-01' AND observation_ts<'2026-01-01'
)
SELECT ev.t,p1.bar_start_utc start_bar,p2.bar_start_utc end_bar,
 100*ln(((p2.bid_close+p2.ask_close)/2)/((p1.bid_close+p1.ask_close)/2)) AS y_45min_pct
FROM ev
LEFT JOIN gold_research_evduka_xau15m_bidask_candidate p1
 ON p1.bar_start_utc=ev.t-interval '30 minutes'
LEFT JOIN gold_research_evduka_xau15m_bidask_candidate p2
 ON p2.bar_start_utc=ev.t+interval '15 minutes'
ORDER BY ev.t;
