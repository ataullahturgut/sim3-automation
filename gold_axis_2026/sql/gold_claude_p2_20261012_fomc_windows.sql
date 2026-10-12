-- CLAUDE P2 FOMC / placebo window prices (read-only; run inside SET TRANSACTION READ ONLY).
-- 2020-2025: EV/Dukascopy M15; 2026: direct Dukascopy M15. Price at clock c = mid close of bar starting c-15min.
-- Dates: every Wednesday 2020-01-01..2026-10-07 plus scheduled FOMC dates (USMPD unscheduled=0).
WITH ev AS (
  SELECT (metadata->>'event_date')::date AS d, (metadata->>'unscheduled')::int AS unsch
  FROM observations WHERE series_id = 'MACRO_FOMC_USMPD_MP1' AND observation_ts >= '2019-12-01'
), dates AS (
  SELECT g::date AS d FROM generate_series('2020-01-01'::date, '2026-10-07'::date, interval '1 day') g
  WHERE extract(isodow FROM g) = 3
  UNION SELECT d FROM ev WHERE unsch = 0 AND d >= '2020-01-01'
), t AS (
  SELECT d, (d + time '14:00') AT TIME ZONE 'America/New_York' AS t0,
         ((d + 1) + time '08:15') AT TIME ZONE 'Europe/Istanbul' AS b0815
  FROM dates
), needed AS (
  SELECT t.d, v.kind, v.ts FROM t CROSS JOIN LATERAL (VALUES
    ('pre', t.t0 - interval '24 hours 30 minutes'), ('m15', t.t0 - interval '30 minutes'),
    ('p45', t.t0 + interval '30 minutes'), ('n0830', t.b0815)) AS v(kind, ts)
), priced AS (
  SELECT n.d, n.kind,
    COALESCE(
      CASE WHEN e.bid_close > 0 AND e.ask_close >= e.bid_close THEN (e.bid_close + e.ask_close) / 2.0 END,
      CASE WHEN x.bid_close > 0 AND x.ask_close >= x.bid_close THEN (x.bid_close + x.ask_close) / 2.0 END) AS mid
  FROM needed n
  LEFT JOIN gold_research_evduka_xau15m_bidask_candidate e ON e.bar_start_utc = n.ts AND n.ts < '2026-01-01'
  LEFT JOIN gold_research_dukascopy_2026_direct_m1_m15_bidask_v2 x ON x.bar_start_utc = n.ts AND n.ts >= '2026-01-01'
), p AS (
  SELECT d,
    EXISTS (SELECT 1 FROM ev WHERE ev.d = priced.d AND ev.unsch = 0) AS is_sched,
    EXISTS (SELECT 1 FROM ev WHERE abs(ev.d - priced.d) <= 1) AS near_any,
    max(mid) FILTER (WHERE kind = 'pre') AS p_pre, max(mid) FILTER (WHERE kind = 'm15') AS p_m15,
    max(mid) FILTER (WHERE kind = 'p45') AS p_p45, max(mid) FILTER (WHERE kind = 'n0830') AS p_n0830
  FROM priced GROUP BY d
)
SELECT count(*) AS n, count(*) FILTER (WHERE is_sched) AS n_sched,
  round(sum(p_pre)::numeric, 3) AS chk_pre, round(sum(p_m15)::numeric, 3) AS chk_m15,
  round(sum(p_p45)::numeric, 3) AS chk_p45, round(sum(p_n0830)::numeric, 3) AS chk_n0830,
  string_agg(to_char(d, 'YYYYMMDD') || ',' || is_sched::int || ',' || near_any::int || ','
    || COALESCE(round(p_pre::numeric, 3)::text, '') || ',' || COALESCE(round(p_m15::numeric, 3)::text, '') || ','
    || COALESCE(round(p_p45::numeric, 3)::text, '') || ',' || COALESCE(round(p_n0830::numeric, 3)::text, ''),
    ';' ORDER BY d) AS csv
FROM p;
