-- R73 panel builder (executed 2026-10-12 on Neon project "Gold Control", default branch).
-- Creates a NEW research table only; reads existing market tables without modifying them.
-- CME ts_event = bar START (verified: 2024 GC vs EV/Dukascopy XAU corr 0.649 for [ts,ts+1h), 0.065 for [ts-1h,ts)).
-- Features end 13:00 UTC (16:00 TR). Target 13:45 UTC open -> next calendar day 06:00 UTC open. Mon-Thu only.
CREATE TABLE gold_research_r73_ovn1645_xmkt_residual_panel_v1 AS
WITH days AS (SELECT d::date d FROM generate_series('2023-01-02'::date,'2026-10-07'::date,'1 day') d WHERE extract(isodow from d)<=5),
x AS (SELECT 'EVDUKA_2020_2025' src, bar_start_utc t, bid_open,ask_open,bid_close,ask_close FROM gold_research_evduka_xau15m_bidask_candidate WHERE bar_start_utc>='2023-01-01'
      UNION ALL SELECT 'DUKA_DIRECT_2026', bar_start_utc, bid_open,ask_open,bid_close,ask_close FROM gold_research_dukascopy_2026_direct_m1_m15_bidask_v2),
c AS (SELECT symbol, ts_event, instrument_id, close FROM gold_research_cme_glbx_futures_2023_2026_h1_5roots_continuous_c WHERE symbol IN ('ZN.c.0','NQ.c.0','CL.c.0')),
cp AS (SELECT dd.d, r.symbol, w.k,
  (SELECT row(c.close,c.instrument_id)::text FROM c WHERE c.symbol=r.symbol AND c.ts_event BETWEEN dd.d+w.h0 AND dd.d+w.h1 ORDER BY c.ts_event DESC LIMIT 1) px
  FROM days dd CROSS JOIN (VALUES ('ZN.c.0'),('NQ.c.0'),('CL.c.0')) r(symbol)
  CROSS JOIN (VALUES ('s7', interval '3 hour', interval '5 hour'), ('s3', interval '7 hour', interval '9 hour'), ('e', interval '10 hour', interval '12 hour')) w(k,h0,h1)),
cw AS (SELECT d, symbol,
  max(CASE WHEN k='s7' THEN split_part(trim(both '()' from px),',',1)::float8 END) ps7, max(CASE WHEN k='s7' THEN split_part(trim(both '()' from px),',',2) END) is7,
  max(CASE WHEN k='s3' THEN split_part(trim(both '()' from px),',',1)::float8 END) ps3, max(CASE WHEN k='s3' THEN split_part(trim(both '()' from px),',',2) END) is3,
  max(CASE WHEN k='e' THEN split_part(trim(both '()' from px),',',1)::float8 END) pe, max(CASE WHEN k='e' THEN split_part(trim(both '()' from px),',',2) END) ie
  FROM cp GROUP BY d, symbol),
cr AS (SELECT d, symbol, CASE WHEN is7=ie THEN ln(pe/ps7) END r7, CASE WHEN is3=ie THEN ln(pe/ps3) END r3,
  (is7 IS NOT NULL AND ie IS NOT NULL AND is7<>ie) roll7, (is3 IS NOT NULL AND ie IS NOT NULL AND is3<>ie) roll3 FROM cw)
SELECT dd.d AS decision_date, extract(isodow from dd.d)::int AS isodow, xe.src AS xau_source,
  ln(((xe.bid_close+xe.ask_close)/2)/((x7.bid_close+x7.ask_close)/2)) AS g7,
  ln(((xe.bid_close+xe.ask_close)/2)/((x3.bid_close+x3.ask_close)/2)) AS g3,
  zn.r7 zn7, nq.r7 nq7, cl.r7 cl7, zn.r3 zn3, nq.r3 nq3, cl.r3 cl3,
  (zn.roll7 OR nq.roll7 OR cl.roll7) AS roll7, (zn.roll3 OR nq.roll3 OR cl.roll3) AS roll3,
  ln(((xx.bid_open+xx.ask_open)/2)/((xn.bid_open+xn.ask_open)/2)) AS ovn_mid,
  ln(xx.bid_open/xn.ask_open) AS ovn_long_crossed, ln(xn.bid_open/xx.ask_open) AS ovn_short_crossed,
  (xn.ask_open-xn.bid_open)/((xn.bid_open+xn.ask_open)/2) AS entry_spread_frac,
  xx.src AS exit_source, now() AS generated_at,
  'R73 prereg 2371b588; CME ts_event=bar start; features end 13:00UTC=16:00TR; entry 13:45UTC open, exit next-calendar-day 06:00UTC open; mid=(bid+ask)/2; Mon-Thu only'::text AS notes
FROM days dd
LEFT JOIN x xe ON xe.t=dd.d+interval '12 hour 45 minute'
LEFT JOIN x x7 ON x7.t=dd.d+interval '5 hour 45 minute' AND x7.src=xe.src
LEFT JOIN x x3 ON x3.t=dd.d+interval '9 hour 45 minute' AND x3.src=xe.src
LEFT JOIN x xn ON xn.t=dd.d+interval '13 hour 45 minute' AND xn.src=xe.src
LEFT JOIN x xx ON xx.t=dd.d+interval '1 day 6 hour' AND xx.src=xe.src AND extract(isodow from dd.d)<=4
LEFT JOIN cr zn ON zn.d=dd.d AND zn.symbol='ZN.c.0'
LEFT JOIN cr nq ON nq.d=dd.d AND nq.symbol='NQ.c.0'
LEFT JOIN cr cl ON cl.d=dd.d AND cl.symbol='CL.c.0'
ORDER BY 1;

-- Compact export view (log-returns x 1e5) used to produce GOLD_R73_20261012_OVN1645_XMKT_PANEL_LOGRET_E5.csv
CREATE VIEW gold_research_r73_ovn1645_panel_compact_v1 AS
SELECT decision_date, extract(year from decision_date)::int yr, isodow,
 round(g7*1e5)::int g7, round(g3*1e5)::int g3, round(zn7*1e5)::int zn7, round(nq7*1e5)::int nq7, round(cl7*1e5)::int cl7,
 round(zn3*1e5)::int zn3, round(nq3*1e5)::int nq3, round(cl3*1e5)::int cl3,
 round(ovn_mid*1e5)::int ovn, round(ovn_long_crossed*1e5)::int lc, round(ovn_short_crossed*1e5)::int sc
FROM gold_research_r73_ovn1645_xmkt_residual_panel_v1;

-- Integrity checksums (must equal CSV column sums per year; verified 2026-10-12 for all four years)
-- SELECT yr, count(*), sum(g7), sum(g3), sum(zn7), sum(nq7), sum(cl7), sum(zn3), sum(nq3), sum(cl3), sum(ovn), sum(lc), sum(sc)
-- FROM gold_research_r73_ovn1645_panel_compact_v1 GROUP BY yr ORDER BY yr;
