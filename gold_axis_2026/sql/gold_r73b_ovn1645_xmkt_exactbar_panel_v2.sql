-- R73B exact-bar correction panel (executed 2026-10-12, Neon project "Gold Control", default branch).
-- New object only; the R73 v1 table/view and all market tables are read, never modified.
-- CME ts_event = bar START. W7 start = close of bar ts=D 05:00 UTC (ends 09:00 TR), end = close of bar ts=D 12:00 UTC
-- (ends 16:00 TR); W3 start = close of bar ts=D 09:00 UTC (ends 13:00 TR). Equality joins only: no fallback, no fill.
-- Start/end bars must share instrument_id. XAU features and overnight target are copied unchanged from v1.
CREATE TABLE gold_research_r73b_ovn1645_xmkt_exactbar_panel_v2 AS
WITH c AS (SELECT symbol, ts_event, instrument_id, close FROM gold_research_cme_glbx_futures_2023_2026_h1_5roots_continuous_c WHERE symbol IN ('ZN.c.0','NQ.c.0','CL.c.0')),
hrs AS (SELECT symbol, (ts_event AT TIME ZONE 'UTC')::date d, count(*) FILTER (WHERE extract(hour from ts_event AT TIME ZONE 'UTC') BETWEEN 6 AND 12) n_in7 FROM c GROUP BY 1,2),
r AS (SELECT p.decision_date, s.symbol,
   CASE WHEN b5.instrument_id=b12.instrument_id THEN ln(b12.close/b5.close) END r7,
   CASE WHEN b9.instrument_id=b12.instrument_id THEN ln(b12.close/b9.close) END r3,
   coalesce(h.n_in7,0) n_in7
  FROM gold_research_r73_ovn1645_xmkt_residual_panel_v1 p CROSS JOIN (VALUES ('ZN.c.0'),('NQ.c.0'),('CL.c.0')) s(symbol)
  LEFT JOIN c b5  ON b5.symbol=s.symbol  AND b5.ts_event = p.decision_date + interval '5 hour'
  LEFT JOIN c b9  ON b9.symbol=s.symbol  AND b9.ts_event = p.decision_date + interval '9 hour'
  LEFT JOIN c b12 ON b12.symbol=s.symbol AND b12.ts_event = p.decision_date + interval '12 hour'
  LEFT JOIN hrs h ON h.symbol=s.symbol AND h.d=p.decision_date)
SELECT p.decision_date, p.isodow, p.xau_source, p.g7, p.g3,
  zn.r7 zn7, nq.r7 nq7, cl.r7 cl7, zn.r3 zn3, nq.r3 nq3, cl.r3 cl3,
  (zn.n_in7=7 AND nq.n_in7=7 AND cl.n_in7=7) full7,
  p.ovn_mid, p.ovn_long_crossed, p.ovn_short_crossed, p.entry_spread_frac, p.exit_source, now() generated_at,
  'R73B prereg a6f716ed: CME exact bars only (ts_event = D 05:00/09:00/12:00 UTC, bar START), same instrument_id, no fallback; XAU features and target copied unchanged from v1'::text notes
FROM gold_research_r73_ovn1645_xmkt_residual_panel_v1 p
JOIN r zn ON zn.decision_date=p.decision_date AND zn.symbol='ZN.c.0'
JOIN r nq ON nq.decision_date=p.decision_date AND nq.symbol='NQ.c.0'
JOIN r cl ON cl.decision_date=p.decision_date AND cl.symbol='CL.c.0'
ORDER BY 1;

-- Identity check (result 2026-10-12: value_mismatch_where_v2_present = 0 and v2_present_v1_null = 0 in every year;
-- complete W7 CME days v1 227/230/235/181 -> v2 216/214/221/170; full7 days 209/208/208/162 for 2023/24/25/26):
-- SELECT extract(year from v2.decision_date)::int yr,
--  count(*) FILTER (WHERE (v2.zn7 IS NOT NULL AND abs(v2.zn7-v1.zn7)>1e-12) OR (v2.nq7 IS NOT NULL AND abs(v2.nq7-v1.nq7)>1e-12)
--    OR (v2.cl7 IS NOT NULL AND abs(v2.cl7-v1.cl7)>1e-12) OR (v2.zn3 IS NOT NULL AND abs(v2.zn3-v1.zn3)>1e-12)
--    OR (v2.nq3 IS NOT NULL AND abs(v2.nq3-v1.nq3)>1e-12) OR (v2.cl3 IS NOT NULL AND abs(v2.cl3-v1.cl3)>1e-12)) value_mismatch_where_v2_present,
--  sum(round(v2.zn7*1e5)), sum(round(v2.nq7*1e5)), sum(round(v2.cl7*1e5)), sum(round(v2.zn3*1e5)), sum(round(v2.nq3*1e5)), sum(round(v2.cl3*1e5))
-- FROM gold_research_r73b_ovn1645_xmkt_exactbar_panel_v2 v2 JOIN gold_research_r73_ovn1645_xmkt_residual_panel_v1 v1 USING (decision_date) GROUP BY 1 ORDER BY 1;
-- Local CSV GOLD_R73B_20261012_OVN1645_XMKT_EXACTBAR_PANEL_LOGRET_E5.csv reproduces these sums exactly.
