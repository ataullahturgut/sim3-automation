-- Read-only GC hourly completed before issue16:30 TRT and source-matched preissue 4 M15 spot bars.
WITH days AS (
 SELECT d::date d,
 ((d::date::timestamp+time '16:30') AT TIME ZONE 'Europe/Istanbul') issue_utc
 FROM generate_series('2023-01-01'::date,'2025-12-31'::date,interval '1 day') d
 WHERE extract(isodow FROM d)<=4
)
SELECT to_char(days.d,'YYYY-MM-DD') issue_date,
 gc.ts_event gc_bar_start_utc,gc.open gc_open,gc.close gc_close,gc.volume gc_volume,
 CASE WHEN gc.open>0 AND gc.close>0 AND gc.volume>0 THEN ln(gc.close/gc.open) END gc_last1h_r,
 s.n_spot,s.bad_spot,s.first_bar,s.last_bar,s.spot_open,s.spot_lastclose,
 CASE WHEN s.n_spot=4 AND s.bad_spot=0 AND s.spot_open>0 AND s.spot_lastclose>0
 AND s.first_bar=days.issue_utc-interval '75 minutes' AND s.last_bar=days.issue_utc-interval '30 minutes'
 THEN ln(s.spot_lastclose/s.spot_open) END spot_pre1h_r
FROM days
LEFT JOIN LATERAL (
 SELECT ts_event,open,close,volume FROM gold_research_cme_glbx_futures_2023_2026_h1_5roots_continuous_c
 WHERE symbol='GC.c.0' AND ts_event<=days.issue_utc-interval '1 hour'
 AND ts_event>=days.issue_utc-interval '3 hours'
 ORDER BY ts_event DESC LIMIT 1
) gc ON TRUE
LEFT JOIN LATERAL (
 SELECT COUNT(*) n_spot,
 COUNT(*) FILTER (WHERE bid_open<=0 OR ask_open<bid_open OR bid_close<=0 OR ask_close<bid_close) bad_spot,
 MIN(bar_start_utc) first_bar,MAX(bar_start_utc) last_bar,
 (array_agg((bid_open+ask_open)/2 ORDER BY bar_start_utc))[1] spot_open,
 (array_agg((bid_close+ask_close)/2 ORDER BY bar_start_utc DESC))[1] spot_lastclose
 FROM gold_research_evduka_xau15m_bidask_candidate
 WHERE bar_start_utc>=days.issue_utc-interval '75 minutes'
 AND bar_start_utc<days.issue_utc-interval '15 minutes'
) s ON TRUE
ORDER BY days.d;