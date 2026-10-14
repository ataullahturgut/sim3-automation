-- CLAUDE_INDEPENDENT R72 — analog (olay örgüsü) tabloları, Neon winter-art-94880101, 2026-10-14. Yalnız YENİ araştırma tabloları.
-- 1) NY17 seans kapanışları ve olay öncesi durum (2019-10 .. 2025-12)
CREATE TABLE gold_research_r72_claude_analog_sessions_v1 AS
WITH b AS (
  SELECT date(((bar_start_utc + interval '15 min') AT TIME ZONE 'America/New_York') + interval '7 hour' - interval '1 microsecond') sess,
         bar_start_utc ts, (bid_close+ask_close)/2 mid
  FROM gold_research_evduka_xau15m_bidask_candidate WHERE bar_start_utc >= '2019-10-01'
), s AS (SELECT sess, max(ts)+interval '15 min' close_ts, count(*) n, (array_agg(mid ORDER BY ts DESC))[1] c FROM b GROUP BY sess HAVING count(*)>=20)
SELECT sess, close_ts, c, c/avg(c) OVER w20 - 1 trend20, c/lag(c,10) OVER (ORDER BY sess) - 1 mom10, c/lag(c,20) OVER (ORDER BY sess) - 1 mom20,
       c/max(c) OVER (ORDER BY sess ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) - 1 dd_from_20hi
FROM s WINDOW w20 AS (ORDER BY sess ROWS BETWEEN 19 PRECEDING AND CURRENT ROW);

-- 2) 2020–2025 NFP/CPI/FOMC olayları: sürpriz bileşenleri, olay öncesi rejim, 15/60/240dk XAU tepkisi, 5/10/20 seans sonrası
CREATE TABLE gold_research_r72_claude_macro_analogs_v1 AS
WITH o AS (
  SELECT observation_ts ts, series_id, value FROM observations
  WHERE observation_ts >= '2020-01-01' AND observation_ts < '2026-01-01' AND series_id IN
   ('MACRO_NFP_ACTUAL_FIRST_PRINT','MACRO_NFP_CONSENSUS_PIT','MACRO_AHE_ACTUAL_FIRST_PRINT','MACRO_AHE_CONSENSUS_PIT',
    'MACRO_UNEMP_ACTUAL_FIRST_PRINT','MACRO_UNEMP_CONSENSUS_PIT','MACRO_CPI_ACTUAL_FIRST_PRINT','MACRO_CPI_CONSENSUS_PIT','MACRO_CORE_CPI_ACTUAL_FIRST_PRINT','MACRO_CORE_CPI_CONSENSUS_PIT','MACRO_FOMC_GSS_PATH_FROZEN2015')
), p AS (
  SELECT ts,
    max(value) FILTER (WHERE series_id='MACRO_NFP_ACTUAL_FIRST_PRINT') - max(value) FILTER (WHERE series_id='MACRO_NFP_CONSENSUS_PIT') s_nfp,
    max(value) FILTER (WHERE series_id='MACRO_AHE_ACTUAL_FIRST_PRINT') - max(value) FILTER (WHERE series_id='MACRO_AHE_CONSENSUS_PIT') s_ahe,
    max(value) FILTER (WHERE series_id='MACRO_UNEMP_ACTUAL_FIRST_PRINT') - max(value) FILTER (WHERE series_id='MACRO_UNEMP_CONSENSUS_PIT') s_un,
    max(value) FILTER (WHERE series_id='MACRO_CPI_ACTUAL_FIRST_PRINT') - max(value) FILTER (WHERE series_id='MACRO_CPI_CONSENSUS_PIT') s_cpi,
    max(value) FILTER (WHERE series_id='MACRO_CORE_CPI_ACTUAL_FIRST_PRINT') - max(value) FILTER (WHERE series_id='MACRO_CORE_CPI_CONSENSUS_PIT') s_ccpi,
    max(value) FILTER (WHERE series_id='MACRO_FOMC_GSS_PATH_FROZEN2015') s_fomc
  FROM o GROUP BY ts
), q AS (
  SELECT p.*, CASE WHEN s_fomc IS NOT NULL THEN 'FOMC' WHEN s_cpi IS NOT NULL OR s_ccpi IS NOT NULL THEN 'CPI' ELSE 'NFP' END etype,
   (SELECT (bid_close+ask_close)/2 FROM gold_research_evduka_xau15m_bidask_candidate x WHERE x.bar_start_utc + interval '15 min' <= p.ts ORDER BY bar_start_utc DESC LIMIT 1) p0
  FROM p
), r AS (
  SELECT q.*,
   (SELECT (bid_close+ask_close)/2 FROM gold_research_evduka_xau15m_bidask_candidate x WHERE x.bar_start_utc + interval '15 min' >= q.ts + interval '15 min' ORDER BY bar_start_utc LIMIT 1)/p0-1 r15,
   (SELECT (bid_close+ask_close)/2 FROM gold_research_evduka_xau15m_bidask_candidate x WHERE x.bar_start_utc + interval '15 min' >= q.ts + interval '60 min' ORDER BY bar_start_utc LIMIT 1)/p0-1 r60,
   (SELECT (bid_close+ask_close)/2 FROM gold_research_evduka_xau15m_bidask_candidate x WHERE x.bar_start_utc + interval '15 min' >= q.ts + interval '240 min' ORDER BY bar_start_utc LIMIT 1)/p0-1 r240,
   (SELECT row(trend20, mom10, mom20, dd_from_20hi)::text FROM gold_research_r72_claude_analog_sessions_v1 s WHERE s.close_ts <= q.ts ORDER BY close_ts DESC LIMIT 1) pre_state,
   (SELECT trend20 FROM gold_research_r72_claude_analog_sessions_v1 s WHERE s.close_ts <= q.ts ORDER BY close_ts DESC LIMIT 1) pre_trend20,
   (SELECT mom10 FROM gold_research_r72_claude_analog_sessions_v1 s WHERE s.close_ts <= q.ts ORDER BY close_ts DESC LIMIT 1) pre_mom10,
   (SELECT mom20 FROM gold_research_r72_claude_analog_sessions_v1 s WHERE s.close_ts <= q.ts ORDER BY close_ts DESC LIMIT 1) pre_mom20,
   (SELECT c FROM gold_research_r72_claude_analog_sessions_v1 s WHERE s.close_ts > q.ts ORDER BY close_ts OFFSET 4 LIMIT 1)/p0-1 f5,
   (SELECT c FROM gold_research_r72_claude_analog_sessions_v1 s WHERE s.close_ts > q.ts ORDER BY close_ts OFFSET 9 LIMIT 1)/p0-1 f10,
   (SELECT c FROM gold_research_r72_claude_analog_sessions_v1 s WHERE s.close_ts > q.ts ORDER BY close_ts OFFSET 19 LIMIT 1)/p0-1 f20
  FROM q
)
SELECT * FROM r WHERE p0 IS NOT NULL;

-- 3) Rapor §1 özet tablosu. cont = sign(r60) * kalan hareket (4s sonrası → k. seans); pozitif = ilk tepki yönünde sürdü, negatif = geri alındı
WITH a AS (SELECT *, CASE WHEN pre_trend20>0 AND pre_mom10>0 THEN 'UP' WHEN pre_trend20<0 AND pre_mom10<0 THEN 'DOWN' ELSE 'MIXED' END reg,
  CASE WHEN r60>0 THEN 'gold_UP_reaction' ELSE 'gold_DOWN_reaction' END rx,
  CASE WHEN ts < '2023-01-01' THEN 'asof_2020_22' ELSE 'later_2023_25' END era,
  sign(r60) * ((1+f10)/(1+r240)-1) cont10, sign(r60)*((1+f20)/(1+r240)-1) cont20, sign(r60)*((1+f5)/(1+r240)-1) cont5
  FROM gold_research_r72_claude_macro_analogs_v1 WHERE abs(r60) >= 0.004 AND f10 IS NOT NULL)
SELECT era, rx, reg, count(*) n, avg(cont5), avg(cont10), avg(cont20),
 sum(CASE WHEN cont10>0.0162 THEN 1 ELSE 0 END) n_cont10_gt_cost, sum(CASE WHEN cont10< -0.0162 THEN 1 ELSE 0 END) n_reverse10_gt_cost
FROM a GROUP BY ROLLUP(era), rx, reg;
