-- CLAUDE_INDEPENDENT R71 — Neon project winter-art-94880101 (Gold Control), executed 2026-10-14 via Neon MCP.
-- Creates NEW research objects only (no existing table modified). Raw prices stay in Neon; nothing here exports them.
-- Order of execution = order below. Results quoted in CLAUDE_COSTED_BACKTEST_RESULTS.json.

-- 1) Per-bar features (bar_start labelled; usable at avail_ts = start+15m)
CREATE TABLE gold_research_r71_claude_indep_xau15m_features_v1 AS
WITH b AS (
  SELECT bar_start_utc ts, bid_open, ask_open, bid_close, ask_close,
         (bid_close+ask_close)/2 mid, ask_close-bid_close spr,
         lag(bar_start_utc) OVER w prev_ts, lag((bid_close+ask_close)/2) OVER w prev_mid,
         lag((bid_close+ask_close)/2,16) OVER w mid_l16, lag((bid_close+ask_close)/2,48) OVER w mid_l48,
         date(((bar_start_utc + interval '15 min') AT TIME ZONE 'America/New_York') + interval '7 hour' - interval '1 microsecond') sess
  FROM gold_research_evduka_xau15m_bidask_candidate
  WHERE bar_start_utc >= '2019-10-01' AND bar_start_utc < '2023-03-06'
  WINDOW w AS (ORDER BY bar_start_utc)
), r AS (
  SELECT *, CASE WHEN ts - prev_ts = interval '15 min' THEN ln(mid/prev_mid) END r15 FROM b
)
SELECT ts, ts + interval '15 min' avail_ts, sess, bid_open, ask_open, bid_close, ask_close, mid, spr, r15,
       stddev_samp(r15) OVER (ORDER BY ts ROWS BETWEEN 1919 PRECEDING AND CURRENT ROW) sig15,
       ln(mid/mid_l16) r4, ln(mid/mid_l48) r12
FROM r;

-- 2) NY17 sessions and daily regime (sessions with < 20 bars dropped)
CREATE TABLE gold_research_r71_claude_indep_xau_sessions_v1 AS
WITH s AS (
  SELECT sess, max(avail_ts) close_ts, count(*) nbars, (array_agg(mid ORDER BY ts DESC))[1] c_mid
  FROM gold_research_r71_claude_indep_xau15m_features_v1 GROUP BY sess
), s2 AS (
  SELECT *, avg(c_mid) OVER (ORDER BY sess ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) sma20,
         count(*) OVER (ORDER BY sess ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) n20,
         lag(c_mid,10) OVER (ORDER BY sess) c_l10
  FROM s WHERE nbars >= 20
)
SELECT sess, close_ts, nbars, c_mid, sma20, c_mid/sma20-1 trend20, c_mid/c_l10-1 mom10,
  CASE WHEN n20<20 OR c_l10 IS NULL THEN NULL
       WHEN c_mid/sma20>1 AND c_mid/c_l10>1 THEN 'UP'
       WHEN c_mid/sma20<1 AND c_mid/c_l10<1 THEN 'DOWN' ELSE 'NEUTRAL' END reg
FROM s2;

-- 3) z12 crossing events (+/-2 onset, +/-1 re-arm) with next in-window execution bar (Mon-Fri 06:00-14:00 UTC)
CREATE TABLE gold_research_r71_claude_indep_xau_zevents_v1 AS
WITH f AS (
  SELECT ts, avail_ts, sess, mid, r12/(sig15*sqrt(48)) z12, r4/(sig15*4) z4,
         lag(r12/(sig15*sqrt(48))) OVER (ORDER BY ts) z12p
  FROM gold_research_r71_claude_indep_xau15m_features_v1 WHERE ts >= '2020-01-01'
), e AS (
  SELECT * FROM f WHERE z12p IS NOT NULL AND (
     (z12>=2 AND z12p<2) OR (z12<1 AND z12p>=1) OR (z12<=-2 AND z12p>-2) OR (z12>-1 AND z12p<=-1))
)
SELECT e.ts, e.avail_ts, e.sess, e.mid, e.z12, e.z4,
  CASE WHEN z12>=2 AND z12p<2 THEN 'UP2' WHEN z12<1 AND z12p>=1 THEN 'UP_REARM'
       WHEN z12<=-2 AND z12p>-2 THEN 'DN2' ELSE 'DN_REARM' END kind,
  x.ts exec_ts, x.bid_open exec_bid, x.ask_open exec_ask, (x.bid_open+x.ask_open)/2 exec_mid
FROM e LEFT JOIN LATERAL (
  SELECT ts, bid_open, ask_open FROM gold_research_r71_claude_indep_xau15m_features_v1 g
  WHERE g.ts >= e.avail_ts AND extract(isodow FROM g.ts) <= 5
    AND (g.ts AT TIME ZONE 'UTC')::time >= '06:00' AND (g.ts AT TIME ZONE 'UTC')::time < '14:00'
  ORDER BY g.ts LIMIT 1) x ON true;

-- 4) Macro signals (NFP+AHE+UNEMP same timestamp = one event; CPI; FOMC path known at +30m)
CREATE TABLE gold_research_r71_claude_indep_macro_signals_v1 AS
WITH o AS (
  SELECT observation_ts ts, series_id, value FROM observations
  WHERE observation_ts >= '2019-12-01' AND observation_ts < '2023-03-01' AND series_id IN
   ('MACRO_NFP_ACTUAL_FIRST_PRINT','MACRO_NFP_CONSENSUS_PIT','MACRO_AHE_ACTUAL_FIRST_PRINT','MACRO_AHE_CONSENSUS_PIT',
    'MACRO_UNEMP_ACTUAL_FIRST_PRINT','MACRO_UNEMP_CONSENSUS_PIT','MACRO_CPI_ACTUAL_FIRST_PRINT','MACRO_CPI_CONSENSUS_PIT','MACRO_FOMC_GSS_PATH_FROZEN2015')
), p AS (
  SELECT ts,
    max(value) FILTER (WHERE series_id='MACRO_NFP_ACTUAL_FIRST_PRINT') - max(value) FILTER (WHERE series_id='MACRO_NFP_CONSENSUS_PIT') s_nfp,
    max(value) FILTER (WHERE series_id='MACRO_AHE_ACTUAL_FIRST_PRINT') - max(value) FILTER (WHERE series_id='MACRO_AHE_CONSENSUS_PIT') s_ahe,
    max(value) FILTER (WHERE series_id='MACRO_UNEMP_ACTUAL_FIRST_PRINT') - max(value) FILTER (WHERE series_id='MACRO_UNEMP_CONSENSUS_PIT') s_un,
    max(value) FILTER (WHERE series_id='MACRO_CPI_ACTUAL_FIRST_PRINT') - max(value) FILTER (WHERE series_id='MACRO_CPI_CONSENSUS_PIT') s_cpi,
    max(value) FILTER (WHERE series_id='MACRO_FOMC_GSS_PATH_FROZEN2015') s_fomc
  FROM o GROUP BY ts
), q AS (
  SELECT *, CASE WHEN s_fomc IS NOT NULL THEN 'FOMC' WHEN s_cpi IS NOT NULL THEN 'CPI' ELSE 'NFP' END etype,
    (coalesce(s_nfp,0)>0 OR coalesce(s_ahe,0)>0 OR coalesce(s_un,0)<0 OR coalesce(s_cpi,0)>0 OR coalesce(s_fomc,0)>0) hawk,
    (coalesce(s_nfp,0)<0 OR coalesce(s_ahe,0)<0 OR coalesce(s_un,0)>0 OR coalesce(s_cpi,0)<0 OR coalesce(s_fomc,0)<0) dove
  FROM p
), base AS (
  SELECT q.*, (SELECT mid FROM gold_research_r71_claude_indep_xau15m_features_v1 f WHERE f.avail_ts <= q.ts ORDER BY f.ts DESC LIMIT 1) p0
  FROM q
), hit AS (
  SELECT b.*, h.avail_ts sig_ts, h.mid sig_mid, CASE WHEN h.mid/b.p0-1 >= 0.004 THEN 1 ELSE -1 END dir
  FROM base b LEFT JOIN LATERAL (
    SELECT avail_ts, mid FROM gold_research_r71_claude_indep_xau15m_features_v1 f
    WHERE f.avail_ts > b.ts AND f.avail_ts <= b.ts + interval '60 min'
      AND f.avail_ts >= b.ts + CASE WHEN b.etype='FOMC' THEN interval '30 min' ELSE interval '0' END
      AND ((f.mid/b.p0-1 >= 0.004 AND b.dove) OR (f.mid/b.p0-1 <= -0.004 AND b.hawk))
    ORDER BY f.avail_ts LIMIT 1) h ON true
)
SELECT h.*, x.ts exec_ts, x.bid_open exec_bid, x.ask_open exec_ask, (x.bid_open+x.ask_open)/2 exec_mid
FROM hit h LEFT JOIN LATERAL (
  SELECT ts, bid_open, ask_open FROM gold_research_r71_claude_indep_xau15m_features_v1 g
  WHERE h.sig_ts IS NOT NULL AND g.ts >= h.sig_ts AND extract(isodow FROM g.ts) <= 5
    AND (g.ts AT TIME ZONE 'UTC')::time >= '06:00' AND (g.ts AT TIME ZONE 'UTC')::time < '14:00'
  ORDER BY g.ts LIMIT 1) x ON true;

-- 5) Unified v1 signal table (armed onsets, regime flips, macro)
CREATE TABLE gold_research_r71_claude_indep_signals_v1 AS
WITH ev AS (
  SELECT *, lag(kind) OVER (PARTITION BY left(kind,2) ORDER BY ts) pk FROM gold_research_r71_claude_indep_xau_zevents_v1
), onset AS (
  SELECT e.avail_ts sig_ts, CASE WHEN kind='UP2' THEN 1 ELSE -1 END dir, 'ONSET' cls, e.mid sig_mid, e.z12,
         (SELECT reg FROM gold_research_r71_claude_indep_xau_sessions_v1 s WHERE s.close_ts <= e.avail_ts ORDER BY s.close_ts DESC LIMIT 1) reg_asof,
         exec_ts, exec_bid, exec_ask, exec_mid
  FROM ev e WHERE kind IN ('UP2','DN2') AND (pk IS NULL OR pk LIKE '%REARM')
), flips AS (
  SELECT s.close_ts sig_ts, CASE WHEN s.reg='UP' THEN 1 ELSE -1 END dir, 'REGFLIP' cls, s.c_mid sig_mid, NULL::float8 z12, s.reg reg_asof,
         x.ts exec_ts, x.bid_open exec_bid, x.ask_open exec_ask, (x.bid_open+x.ask_open)/2 exec_mid
  FROM (SELECT *, lag(reg) OVER (ORDER BY sess) preg FROM gold_research_r71_claude_indep_xau_sessions_v1) s
  LEFT JOIN LATERAL (SELECT ts, bid_open, ask_open FROM gold_research_r71_claude_indep_xau15m_features_v1 g
     WHERE g.ts >= s.close_ts AND extract(isodow FROM g.ts) <= 5 AND (g.ts AT TIME ZONE 'UTC')::time >= '06:00' AND (g.ts AT TIME ZONE 'UTC')::time < '14:00'
     ORDER BY g.ts LIMIT 1) x ON true
  WHERE s.reg IN ('UP','DOWN') AND s.reg IS DISTINCT FROM s.preg AND s.preg IS NOT NULL
), macro AS (
  SELECT sig_ts, dir, 'MACRO_'||etype cls, sig_mid, NULL::float8, NULL, exec_ts, exec_bid, exec_ask, exec_mid
  FROM gold_research_r71_claude_indep_macro_signals_v1 WHERE sig_ts IS NOT NULL
)
SELECT * FROM onset UNION ALL SELECT * FROM flips UNION ALL SELECT * FROM macro;

-- 6) Variant admission (V-A FULL, V-B MACRO+REGIME, V-C REGIME ONLY); same-exec-bar supersede; queue validity +/-0.5%
CREATE OR REPLACE VIEW gold_research_r71_claude_indep_variant_signals_v1 AS
WITH v AS (SELECT unnest(ARRAY['VA','VB','VC']) variant),
f AS (
  SELECT v.variant, s.* FROM v JOIN gold_research_r71_claude_indep_signals_v1 s ON
   (s.cls='REGFLIP')
   OR (v.variant IN ('VA','VB') AND s.cls LIKE 'MACRO%')
   OR (v.variant='VA' AND s.cls='ONSET' AND ((s.dir=1 AND s.reg_asof IS DISTINCT FROM 'DOWN') OR (s.dir=-1 AND s.reg_asof IS DISTINCT FROM 'UP')))
  WHERE s.exec_ts IS NOT NULL
), g AS (
  SELECT f.*, row_number() OVER (PARTITION BY variant, exec_ts ORDER BY sig_ts DESC, cls) rk FROM f
)
SELECT variant, sig_ts, dir, cls, sig_mid, z12, reg_asof, exec_ts, exec_bid, exec_ask, exec_mid,
  CASE WHEN dir=1 THEN exec_mid >= sig_mid*0.995 ELSE exec_mid <= sig_mid*1.005 END valid
FROM g WHERE rk=1;

-- 7) v1 simulator (full position, 0.8% per side, BUY at ASK / SELL at BID of execution bar open)
CREATE OR REPLACE FUNCTION gold_research_r71_claude_indep_sim_v1(p_variant text, p_t0 timestamptz, p_t1 timestamptz, p_cash float8, p_units float8, p_fee float8 DEFAULT 0.008)
RETURNS TABLE(seq int, variant text, sig_ts timestamptz, cls text, dir int, exec_ts timestamptz, action text, px float8, fee_usd float8, cash_after float8, units_after float8, nav_bid float8)
LANGUAGE plpgsql AS $$
DECLARE r record; c float8 := p_cash; u float8 := p_units; n int := 0; mk float8;
BEGIN
  FOR r IN SELECT * FROM gold_research_r71_claude_indep_variant_signals_v1 s
           WHERE s.variant=p_variant AND s.sig_ts >= p_t0 AND s.exec_ts < p_t1 ORDER BY s.exec_ts, s.sig_ts LOOP
    IF r.valid AND r.dir=1 AND u=0 AND c>0 THEN
      n:=n+1; u := c*(1-p_fee)/r.exec_ask; seq:=n; variant:=p_variant; sig_ts:=r.sig_ts; cls:=r.cls; dir:=r.dir; exec_ts:=r.exec_ts;
      action:='BUY'; px:=r.exec_ask; fee_usd:=c*p_fee; c:=0; cash_after:=c; units_after:=u; nav_bid:=u*r.exec_bid; RETURN NEXT;
    ELSIF r.valid AND r.dir=-1 AND u>0 THEN
      n:=n+1; seq:=n; variant:=p_variant; sig_ts:=r.sig_ts; cls:=r.cls; dir:=r.dir; exec_ts:=r.exec_ts; action:='SELL'; px:=r.exec_bid;
      fee_usd:=u*r.exec_bid*p_fee; c := u*r.exec_bid*(1-p_fee); u:=0; cash_after:=c; units_after:=u; nav_bid:=c; RETURN NEXT;
    END IF;
  END LOOP;
  SELECT bid_close INTO mk FROM gold_research_r71_claude_indep_xau15m_features_v1 WHERE avail_ts <= p_t1 ORDER BY ts DESC LIMIT 1;
  seq:=n+1; variant:=p_variant; sig_ts:=NULL; cls:='END_MARK'; dir:=0; exec_ts:=p_t1; action:='MARK'; px:=mk; fee_usd:=u*mk*p_fee;
  cash_after:=c; units_after:=u; nav_bid:=c+u*mk; RETURN NEXT;
END $$;

-- 8) v2 hysteresis band family (L in {20,50}, h in {1,2,3}%), transition-only signals
CREATE TABLE gold_research_r71_claude_indep_signals_v2 AS
WITH s AS (
  SELECT sess, close_ts, c_mid,
    avg(c_mid) OVER (ORDER BY sess ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) sma20,
    avg(c_mid) OVER (ORDER BY sess ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) sma50,
    count(*) OVER (ORDER BY sess ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) n50
  FROM gold_research_r71_claude_indep_xau_sessions_v1
), cfg AS (SELECT l, h FROM (VALUES (20),(50)) a(l) CROSS JOIN (VALUES (0.01),(0.02),(0.03)) b(h)
), raw AS (
  SELECT 'L'||l||'_H'||(h*100)::int variant, s.*, CASE WHEN l=20 THEN sma20 ELSE sma50 END sma, h,
    CASE WHEN n50 < l THEN NULL WHEN c_mid > (CASE WHEN l=20 THEN sma20 ELSE sma50 END)*(1+h) THEN 1
         WHEN c_mid < (CASE WHEN l=20 THEN sma20 ELSE sma50 END)*(1-h) THEN -1 END breach
  FROM s CROSS JOIN cfg
), st AS (SELECT *, count(breach) OVER (PARTITION BY variant ORDER BY sess) grp FROM raw
), st2 AS (SELECT *, first_value(breach) OVER (PARTITION BY variant, grp ORDER BY sess) state FROM st
), fl AS (SELECT *, lag(state) OVER (PARTITION BY variant ORDER BY sess) pstate FROM st2)
SELECT fl.variant, fl.close_ts sig_ts, fl.state dir, 'BANDFLIP' cls, fl.c_mid sig_mid, fl.sma, fl.h, fl.sess,
  x.ts exec_ts, x.bid_open exec_bid, x.ask_open exec_ask, (x.bid_open+x.ask_open)/2 exec_mid, true valid
FROM fl LEFT JOIN LATERAL (SELECT ts, bid_open, ask_open FROM gold_research_r71_claude_indep_xau15m_features_v1 g
     WHERE g.ts >= fl.close_ts AND extract(isodow FROM g.ts) <= 5 AND (g.ts AT TIME ZONE 'UTC')::time >= '06:00' AND (g.ts AT TIME ZONE 'UTC')::time < '14:00'
     ORDER BY g.ts LIMIT 1) x ON true
WHERE fl.state IS NOT NULL AND fl.state IS DISTINCT FROM fl.pstate;

-- gold_research_r71_claude_indep_sim_v2(...) is identical to sim_v1 except it reads gold_research_r71_claude_indep_signals_v2
-- (filter: s.exec_ts IS NOT NULL) and has no `valid` gate.

-- 9) 15m check log (2023-01-03 .. 2023-02-28): stage = REVERSAL > ONSET > EXHAUSTION > CONTINUATION > PRE_ONSET > UNCERTAIN
CREATE TABLE gold_research_r71_claude_indep_15m_check_log_v1 AS
WITH f AS (
  SELECT f.ts, f.avail_ts, f.sess, f.mid, f.spr, r4, r12, r12/(sig15*sqrt(48)) z12, r4/(sig15*4) z4,
    ln(f.mid/lag(f.mid,4) OVER (ORDER BY f.ts)) r1h,
    (SELECT reg FROM gold_research_r71_claude_indep_xau_sessions_v1 s WHERE s.close_ts <= f.avail_ts ORDER BY s.close_ts DESC LIMIT 1) reg
  FROM gold_research_r71_claude_indep_xau15m_features_v1 f WHERE f.ts >= '2022-12-30' AND f.ts < '2023-03-01'
), g AS (
  SELECT f.*, CASE
    WHEN (reg='UP' AND z12<=-2) OR (reg='DOWN' AND z12>=2) THEN 'REVERSAL'
    WHEN abs(z12)>=2 THEN 'ONSET'
    WHEN (reg='UP' AND z12>=1 AND z4<=-1) OR (reg='DOWN' AND z12<=-1 AND z4>=1) THEN 'EXHAUSTION'
    WHEN (reg='UP' AND z12>=1) OR (reg='DOWN' AND z12<=-1) THEN 'CONTINUATION'
    WHEN abs(z12)<1 THEN 'PRE_ONSET' ELSE 'UNCERTAIN' END stage,
    CASE WHEN z12>=1 THEN 'UP' WHEN z12<=-1 THEN 'DOWN' ELSE '-' END dir_hint
  FROM f
)
SELECT g.*, (SELECT string_agg(s.cls||(CASE WHEN s.dir=1 THEN '+' ELSE '-' END), '|') FROM gold_research_r71_claude_indep_signals_v1 s WHERE s.sig_ts = g.avail_ts) raw_signals,
  (SELECT string_agg(v.variant, '|') FROM gold_research_r71_claude_indep_variant_signals_v1 v WHERE v.sig_ts = g.avail_ts) admitted_in,
  ((g.avail_ts AT TIME ZONE 'UTC')::time >= '06:00' AND (g.avail_ts AT TIME ZONE 'UTC')::time <= '14:00' AND extract(isodow from g.avail_ts)<=5) bank_open
FROM g WHERE g.ts >= '2023-01-03';
