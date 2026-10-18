-- E2E3N actual retrospective computation. Fixed prereg commit 5709d3f.
-- Neon project Gold Control; no modifications.
WITH ovn AS (
 SELECT decision_date, EXTRACT(YEAR FROM decision_date)::int yr, xau_source src, ovn_mid r
 FROM gold_research_r73b_ovn1645_xmkt_exactbar_panel_v2
 WHERE isodow<=4 AND ovn_mid IS NOT NULL AND ovn_mid<>0 AND xau_source IS NOT NULL
), hist AS (
 SELECT *,
 COUNT(*) OVER (PARTITION BY src ORDER BY decision_date ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING) n60,
 AVG(r) OVER (PARTITION BY src ORDER BY decision_date ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING) mu60,
 STDDEV_SAMP(r) OVER (PARTITION BY src ORDER BY decision_date ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING) s60,
 STDDEV_SAMP(r) OVER (PARTITION BY src ORDER BY decision_date ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) s20,
 AVG((r>0)::int) OVER (PARTITION BY src ORDER BY decision_date ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING) up60,
 AVG((ABS(r)>0.001)::int) OVER (PARTITION BY src ORDER BY decision_date ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING) q01,
 AVG((ABS(r)>0.002)::int) OVER (PARTITION BY src ORDER BY decision_date ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING) q02,
 AVG((ABS(r)>0.003)::int) OVER (PARTITION BY src ORDER BY decision_date ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING) q03
 FROM ovn
), p AS (
 SELECT decision_date,yr,src,r,up60,q01,q02,q03,
 1.0/(1+EXP(-1.702*mu60/s20)) e2dyn,
 1.0/(1+EXP(-1.702*mu60/s60)) e2const,
 2.0/(1+EXP(1.702*0.001/s20)) e3dyn01,
 2.0/(1+EXP(1.702*0.001/s60)) e3const01,
 2.0/(1+EXP(1.702*0.002/s20)) e3dyn02,
 2.0/(1+EXP(1.702*0.002/s60)) e3const02,
 2.0/(1+EXP(1.702*0.003/s20)) e3dyn03,
 2.0/(1+EXP(1.702*0.003/s60)) e3const03
 FROM hist WHERE n60=60 AND s20>0 AND s60>0
)
SELECT TO_CHAR(DATE_TRUNC('month', decision_date), 'YYYY-MM') AS month,yr,src,COUNT(*) n,
 SUM(POWER((r>0)::int-e2dyn,2)) e2dyn_loss,
 SUM(POWER((r>0)::int-e2const,2)) e2const_loss,
 SUM(POWER((r>0)::int-up60,2)) e2freq_loss,
 SUM(POWER((ABS(r)>0.001)::int-e3dyn01,2)) e3dyn01_loss,
 SUM(POWER((ABS(r)>0.001)::int-e3const01,2)) e3const01_loss,
 SUM(POWER((ABS(r)>0.001)::int-q01,2)) e3freq01_loss,
 SUM(POWER((ABS(r)>0.002)::int-e3dyn02,2)) e3dyn02_loss,
 SUM(POWER((ABS(r)>0.002)::int-e3const02,2)) e3const02_loss,
 SUM(POWER((ABS(r)>0.002)::int-q02,2)) e3freq02_loss,
 SUM(POWER((ABS(r)>0.003)::int-e3dyn03,2)) e3dyn03_loss,
 SUM(POWER((ABS(r)>0.003)::int-e3const03,2)) e3const03_loss,
 SUM(POWER((ABS(r)>0.003)::int-q03,2)) e3freq03_loss
FROM p GROUP BY 1,2,3 ORDER BY 1,2,3;
