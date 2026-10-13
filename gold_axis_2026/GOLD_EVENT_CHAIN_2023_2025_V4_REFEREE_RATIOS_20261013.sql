-- Referee audit #2 (2026-10-13): derived cross-metal / miner / equity ratio panel. READ-ONLY on Neon project Gold Control.
-- Output is NOT committed: Twelve Data / FRED / StakTrakr rows carry rights_policy PRIVATE ... NO_PUBLIC_RAW_REDISTRIBUTION.
-- Save the single returned string to a text file and pass its path to GOLD_EVENT_CHAIN_2023_2025_V4_REFEREE_REPRODUCE_20261013.py.
-- Columns per record: yymmdd, 100*ln(XAG/XAU), 100*ln(XPT/XAU), 100*ln(NEM/XAU), 100*ln(SPX); records separated by ';'.
-- Timing caveats: StakTrakr metal series are labelled LBMA, evidence_class HISTORICAL_RECONSTRUCTION_NO_ORIGIN_PIT_CLAIM (fix time not encoded);
-- NEM/SPX are NYSE/FRED daily closes (16:00 ET), before the XAU NY17 close of the same date. None has a proven first-publication timestamp.
WITH s AS (
  SELECT observation_ts::date d,
         max(value) FILTER (WHERE series_id='XAU_STAKTRAKR_RESEARCH_DAILY_R1') au,
         max(value) FILTER (WHERE series_id='XAG_STAKTRAKR_RESEARCH_DAILY_R1') ag,
         max(value) FILTER (WHERE series_id='XPT_STAKTRAKR_RESEARCH_DAILY_R1') pt
  FROM observations
  WHERE series_id IN ('XAU_STAKTRAKR_RESEARCH_DAILY_R1','XAG_STAKTRAKR_RESEARCH_DAILY_R1','XPT_STAKTRAKR_RESEARCH_DAILY_R1')
    AND observation_ts BETWEEN '2022-09-01' AND '2026-01-01'
  GROUP BY 1),
e AS (
  SELECT observation_ts::date d,
         max(value) FILTER (WHERE series_id='NEM_TWELVEDATA') nem,
         max(value) FILTER (WHERE series_id='SP500_FRED') spx
  FROM observations
  WHERE series_id IN ('NEM_TWELVEDATA','SP500_FRED') AND observation_ts BETWEEN '2022-09-01' AND '2026-01-01'
  GROUP BY 1),
j AS (SELECT s.d, au, ag, pt, nem, spx FROM s LEFT JOIN e USING(d) WHERE extract(isodow from s.d) < 6),
f AS (SELECT d, ln(ag/au) lsr, ln(pt/au) lpr, ln(nem) lnem, ln(au) lau, ln(spx) lspx FROM j)
SELECT string_agg(to_char(d,'YYMMDD')||','||coalesce(round((100*lsr)::numeric,2)::text,'')||','||coalesce(round((100*lpr)::numeric,2)::text,'')
       ||','||coalesce(round((100*(lnem-lau))::numeric,2)::text,'')||','||coalesce(round((100*lspx)::numeric,2)::text,''), ';' ORDER BY d)
FROM f;
