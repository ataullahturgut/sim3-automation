-- CLAUDE P1 daily exact-clock panel (read-only). Run inside: SET TRANSACTION READ ONLY.
-- Replace SRC_TABLE (2020-25: gold_research_evduka_xau15m_bidask_candidate;
-- 2026: gold_research_dukascopy_2026_direct_m1_m15_bidask_v2) and YYYY / YYYY_NEXT only.
-- Price at clock c = mid close of the bar starting c-15min (bar_start_utc is the bar START).
-- Output: one CSV text cell + checksums. Returns in basis points (x1e4 log), rounded 0.01bp.
WITH bars AS (
  SELECT bar_start_utc,
         (bar_start_utc AT TIME ZONE 'Europe/Istanbul') AS trt,
         (bid_close + ask_close) / 2.0 AS mid,
         (bid_close > 0 AND ask_close >= bid_close AND bid_open > 0 AND ask_open >= bid_open) AS valid
  FROM SRC_TABLE
  WHERE bar_start_utc >= 'YYYY-01-01'::date - 7 AND bar_start_utc < 'YYYY_NEXT-01-01'::date + 7
), g AS (
  SELECT *, lead(bar_start_utc) OVER (ORDER BY bar_start_utc) - bar_start_utc AS gap_next,
         bar_start_utc - lag(bar_start_utc) OVER (ORDER BY bar_start_utc) AS gap_prev
  FROM bars
-- clk: price at clocks 08:30, 09:00, 16:15, 16:45 per TR calendar date
), clk AS (
  SELECT trt::date AS d,
    max(mid) FILTER (WHERE trt::time = '08:15') AS p0830,
    max(mid) FILTER (WHERE trt::time = '08:45') AS p0900,
    max(mid) FILTER (WHERE trt::time = '16:00') AS p1615,
    max(mid) FILTER (WHERE trt::time = '16:30') AS p1645,
    max(bar_start_utc) FILTER (WHERE trt::time = '16:30') AS b1630,
    max(bar_start_utc) FILTER (WHERE trt::time = '08:15') AS b0815,
    bool_and(valid) FILTER (WHERE trt::time IN ('08:15','08:45','16:00','16:30')) AS clk_valid,
    count(*) FILTER (WHERE trt::time >= '09:00' AND trt::time <= '16:30') AS day_n,
    count(*) FILTER (WHERE trt::time > '09:00' AND trt::time <= '16:30' AND gap_prev = interval '15 minutes') AS day_n15,
    bool_and(valid) FILTER (WHERE trt::time >= '08:45' AND trt::time <= '16:30') AS day_valid
  FROM g GROUP BY 1
-- ovn: OVN session of decision date d: 16:45 on d .. 08:45 on d+1 (H3A rule)
), ovn AS (
  SELECT (CASE WHEN trt::time < '09:00' THEN trt::date - 1 ELSE trt::date END) AS d,
    count(*) AS n,
    count(*) FILTER (WHERE gap_prev = interval '15 minutes' AND NOT (trt::time = '16:45')) AS n15,
    count(*) FILTER (WHERE gap_prev = interval '75 minutes') AS n75,
    min(trt) AS first_trt, max(trt) AS last_trt, bool_and(valid) AS ok_valid
  FROM g WHERE trt::time >= '16:45' OR trt::time < '09:00'
  GROUP BY 1
), panel AS (
  SELECT c.d, extract(isodow FROM c.d)::int AS wd,
    c.p0830, c.p0900, c.p1615, c.p1645, n1.p0900 AS p0900_next,
    (c.day_n = 31 AND c.day_n15 = 30 AND c.day_valid AND c.p0900 IS NOT NULL) AS day_ok,
    (extract(isodow FROM c.d) <= 4 AND o.n = 61 AND o.n15 = 59 AND o.n75 = 1 AND o.ok_valid
       AND o.first_trt::time = '16:45' AND o.last_trt::time = '08:45' AND o.last_trt::date = c.d + 1) AS ovn_ok,
    prev.p1645 AS p1645_prev,
    (SELECT gg.mid FROM g gg
      WHERE gg.bar_start_utc >= prev.b1630 AND gg.bar_start_utc < c.b0815
        AND gg.gap_next >= interval '75 minutes'
      ORDER BY gg.bar_start_utc LIMIT 1) AS pb
  FROM clk c
  LEFT JOIN ovn o ON o.d = c.d
  LEFT JOIN clk n1 ON n1.d = c.d + 1
  LEFT JOIN LATERAL (SELECT p.p1645, p.b1630 FROM clk p
                     WHERE p.d < c.d AND p.b1630 IS NOT NULL ORDER BY p.d DESC LIMIT 1) prev ON true
  WHERE c.d >= 'YYYY-01-01' AND c.d < 'YYYY_NEXT-01-01' AND extract(isodow FROM c.d) <= 5
    AND COALESCE(c.clk_valid, false)
), out AS (
  SELECT d, wd, day_ok, ovn_ok, p0900, p1645,
    round((1e4 * ln(p1645 / p0900))::numeric, 2) AS y_day,
    CASE WHEN ovn_ok THEN round((1e4 * ln(p0900_next / p1645))::numeric, 2) END AS y_ovn,
    round((1e4 * ln(pb / p1645_prev))::numeric, 2) AS f_us,
    round((1e4 * ln(p0830 / pb))::numeric, 2) AS f_asia,
    round((1e4 * ln(p1615 / p0900))::numeric, 2) AS g_daysofar
  FROM panel
)
SELECT count(*) AS n_rows, count(*) FILTER (WHERE f_us IS NULL) AS n_fus_null,
  count(*) FILTER (WHERE day_ok) AS n_day_ok, count(*) FILTER (WHERE ovn_ok) AS n_ovn_ok,
  sum(y_day) FILTER (WHERE day_ok) AS chk_y_day, sum(y_ovn) AS chk_y_ovn,
  sum(f_us) AS chk_f_us, sum(f_asia) AS chk_f_asia, sum(g_daysofar) AS chk_g,
  string_agg(to_char(d,'YYYYMMDD') || ',' || wd || ',' || COALESCE(day_ok::int::text,'0') || ','
             || COALESCE(ovn_ok::int::text,'0') || ',' || COALESCE(round(p0900::numeric,2)::text,'')
             || ',' || COALESCE(y_day::text,'')
             || ',' || COALESCE(y_ovn::text,'') || ',' || COALESCE(f_us::text,'') || ','
             || COALESCE(f_asia::text,'') || ',' || COALESCE(g_daysofar::text,''),
             ';' ORDER BY d) AS csv
FROM out;
