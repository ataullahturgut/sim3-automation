-- R72 / 2026-10-12: read-only historical 09:00 Europe/Istanbul price-label audit.
-- Source: Neon public.gold_research_histdata_xau15m_candidate (HistData noncanonical).
-- Three BUSINESS WEEKDAYS after origin, not 72 hours, not H3 D0->D3 daily means.
-- Missing exact 09:00 quotes exclude an origin; this does NOT model holiday-specific calendars.
-- Query was executed 2026-10-12 and returned 2023:9/192, 2024:14/193,
-- 2025:12/192, 2026:40/187 for January-September.
WITH prices AS (
  SELECT (bar_start_utc AT TIME ZONE 'Europe/Istanbul')::date AS d,
         open_price AS p
  FROM public.gold_research_histdata_xau15m_candidate
  WHERE (bar_start_utc AT TIME ZONE 'Europe/Istanbul')::time = TIME '09:00:00'
    AND EXTRACT(ISODOW FROM bar_start_utc AT TIME ZONE 'Europe/Istanbul') BETWEEN 1 AND 5
), pairs AS (
  SELECT a.d, a.p, b.p AS target_p
  FROM prices a
  CROSS JOIN LATERAL (
    SELECT dd::date AS target_d
    FROM generate_series(a.d::timestamp + interval '1 day',
                         a.d::timestamp + interval '7 day',
                         interval '1 day') dd
    WHERE EXTRACT(ISODOW FROM dd) <= 5
    ORDER BY dd
    OFFSET 2 LIMIT 1
  ) tgt
  JOIN prices b ON b.d = tgt.target_d
  WHERE EXTRACT(MONTH FROM a.d) <= 9
    AND EXTRACT(YEAR FROM a.d) BETWEEN 2023 AND 2026
)
SELECT EXTRACT(YEAR FROM d)::int AS yr,
       COUNT(*) AS n,
       COUNT(*) FILTER (WHERE target_p / p <= 0.98) AS large_down_2pct,
       ROUND(100 * COUNT(*) FILTER (WHERE target_p / p <= 0.98)::numeric
             / NULLIF(COUNT(*), 0), 2) AS event_pct
FROM pairs
GROUP BY 1
ORDER BY 1;
