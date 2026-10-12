-- P2 fixed FOMC announcement windows, close timestamps relative to actual America/New_York 14:00.
-- Exclude irregular extra Fed actions in 2020; use only officially scheduled statement end-dates.
WITH ev AS (
 SELECT observation_ts::date d,
 ((observation_ts::date::timestamp + time '14:00') AT TIME ZONE 'America/New_York') t0
 FROM observations WHERE series_id='MACRO_FOMC_USMPD_MP1'
 AND observation_ts>='2020-01-01' AND observation_ts<'2026-01-01'
 AND (extract(year from observation_ts)>2020
   OR observation_ts::date IN ('2020-01-29'::date,'2020-04-29'::date,'2020-06-10'::date,'2020-07-29'::date,'2020-09-16'::date,'2020-11-05'::date,'2020-12-16'::date))
), vals AS (
 SELECT ev.d,ev.t0,
 MAX((bid_close+ask_close)/2.) FILTER(WHERE bar_start_utc=ev.t0-interval '75 minutes') p_pre60,
 MAX((bid_close+ask_close)/2.) FILTER(WHERE bar_start_utc=ev.t0-interval '30 minutes') p_pre15,
 MAX((bid_close+ask_close)/2.) FILTER(WHERE bar_start_utc=ev.t0+interval '30 minutes') p_post45,
 COUNT(*) FILTER(WHERE bid_close<=0 OR ask_close<bid_close) bad_quotes
 FROM ev
 LEFT JOIN LATERAL (
   SELECT bar_start_utc,bid_close,ask_close
   FROM gold_research_evduka_xau15m_bidask_candidate b
   WHERE b.bar_start_utc IN (ev.t0-interval '75 minutes',ev.t0-interval '30 minutes',ev.t0+interval '30 minutes')
 ) b ON TRUE
 GROUP BY 1,2
)
SELECT to_char(d,'YYYY-MM-DD') event_date,
 (t0 AT TIME ZONE 'UTC')::text event_time_utc,
 p_pre60,p_pre15,p_post45,
 CASE WHEN p_pre60>0 AND p_pre15>0 THEN ln(p_pre15/p_pre60) END x_pre,
 CASE WHEN p_pre15>0 AND p_post45>0 THEN ln(p_post45/p_pre15) END x_post,
 bad_quotes
 FROM vals ORDER BY d;