-- Read-only extraction of 2023--Jan 2026 XAU M15 from Neon.
-- Execute: psql "$DATABASE_URL" -f export_m15.sql > xau_m15.csv
-- IMPORTANT: time is UTC. A bar is available only at bar_start_utc + 15 min.
COPY (
 SELECT bar_start_utc,open_price,high_price,low_price,close_price,native_minute_bars
 FROM public.gold_research_histdata_xau15m_candidate
 WHERE bar_start_utc >= '2023-01-01 00:00:00+00'
   AND bar_start_utc < '2026-02-01 00:00:00+00'
 ORDER BY bar_start_utc
) TO STDOUT WITH CSV HEADER;
