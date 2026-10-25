-- TR09 H3 matured60 prequential online base-rate recalibration preregistered 2026-10-25.
-- Distinct from fixed gates: each forecast uses only historical H3 labels with target_date < forecast date.
-- Retrospective HistData 09 reference; vendor firstprint and bank execution not certified.
-- Read-only. Source: public.gold_research_histdata_xau15m_candidate; 08:45-09:00TR M15 close.
-- Historical firstprint not independently verified; retrospective only.
WITH cal AS (
 SELECT d::date d, ROW_NUMBER() OVER(ORDER BY d)::int rn
 FROM generate_series('2022-12-01'::date,'2026-10-15'::date,'1 day') d
 WHERE EXTRACT(ISODOW FROM d)<6 AND d::date NOT IN
 ('2023-01-02','2023-04-07','2023-12-25','2024-01-01','2024-03-29','2024-12-25',
  '2025-01-01','2025-04-18','2025-12-25','2026-01-01','2026-04-03')
), anchor AS (
 SELECT (bar_start_utc AT TIME ZONE 'Europe/Istanbul')::date d, close_price p
 FROM public.gold_research_histdata_xau15m_candidate
 WHERE native_minute_bars=15
 AND (bar_start_utc AT TIME ZONE 'Europe/Istanbul')::time=TIME '08:45:00'
 AND bar_start_utc >= '2022-12-01'::timestamptz
 AND bar_start_utc < '2026-10-16'::timestamptz
), base AS (
 SELECT c.d,t.d target_d,
 a0.p p0, a1.p p1, a2.p p2, a3.p p3, a4.p p4, a5.p p5, at.p pt
 FROM cal c
 JOIN cal c0 ON c0.rn=c.rn-5
 JOIN cal c1 ON c1.rn=c.rn-4
 JOIN cal c2 ON c2.rn=c.rn-3
 JOIN cal c3 ON c3.rn=c.rn-2
 JOIN cal c4 ON c4.rn=c.rn-1
 JOIN cal t ON t.rn=c.rn+3
 JOIN anchor a0 ON a0.d=c0.d
 JOIN anchor a1 ON a1.d=c1.d
 JOIN anchor a2 ON a2.d=c2.d
 JOIN anchor a3 ON a3.d=c3.d
 JOIN anchor a4 ON a4.d=c4.d
 JOIN anchor a5 ON a5.d=c.d JOIN anchor at ON at.d=t.d
 WHERE c.d BETWEEN '2023-01-01' AND '2026-09-30'
), features AS (
 SELECT b.d,b.target_d,
 GREATEST(0.0, 1.0-b.p1/b.p0, 1.0-b.p2/b.p0, 1.0-b.p3/b.p0, 1.0-b.p4/b.p0, 1.0-b.p5/b.p0, 1.0-b.p2/b.p1, 1.0-b.p3/b.p1, 1.0-b.p4/b.p1, 1.0-b.p5/b.p1, 1.0-b.p3/b.p2, 1.0-b.p4/b.p2, 1.0-b.p5/b.p2, 1.0-b.p4/b.p3, 1.0-b.p5/b.p3, 1.0-b.p5/b.p4) mdd5,
 SQRT((POWER(LN(b.p1/b.p0),2)+POWER(LN(b.p2/b.p1),2)+POWER(LN(b.p3/b.p2),2)+POWER(LN(b.p4/b.p3),2)+POWER(LN(b.p5/b.p4),2))/5.0) v5,
 (b.p5>b.p4 AND b.p4>b.p3) two_up,
 (b.pt>b.p5)::int y_up,
 (b.pt/b.p5<=0.98)::int y_tail
 FROM base b
), train AS (
 SELECT * FROM features WHERE d BETWEEN '2023-01-01' AND '2024-12-31' AND target_d<='2024-12-31'
), quant AS (
 SELECT percentile_cont(.75) WITHIN GROUP(ORDER BY mdd5) q_mdd,
        percentile_cont(.75) WITHIN GROUP(ORDER BY v5) q_vol
 FROM train
), rows AS (
 SELECT f.*, (f.mdd5>q.q_mdd) high_mdd, (f.v5>q.q_vol) high_vol
 FROM features f CROSS JOIN quant q
), arms AS (
 SELECT r.*,a.arm,a.gate FROM rows r
 CROSS JOIN LATERAL (VALUES
 ('constant',true),('two_up',r.two_up),('vol_q75',r.high_vol),('mdd_q75',r.high_mdd),('calendar_ge5',(r.target_d-r.d)>=5)
 ) a(arm,gate)
), fit AS (
 SELECT arm,gate,COUNT(*) train_n,
 (SUM(y_up)::numeric+1)/(COUNT(*)+2) p_up,
 (SUM(y_tail)::numeric+1)/(COUNT(*)+2) p_tail
 FROM arms WHERE d<='2024-12-31' AND target_d<='2024-12-31'
 GROUP BY arm,gate
), train_base AS (
 SELECT (SUM(y_up)::numeric+1)/(COUNT(*)+2) train_p_up,
        (SUM(y_tail)::numeric+1)/(COUNT(*)+2) train_p_tail
 FROM train
), online AS (
 SELECT r.*,h.n_matured,
        (h.k_up+20*b.train_p_up)/(h.n_matured+20) p_up,
        (h.k_tail+20*b.train_p_tail)/(h.n_matured+20) p_tail
 FROM rows r CROSS JOIN train_base b
 CROSS JOIN LATERAL (
   SELECT COUNT(*)::numeric n_matured,
          COALESCE(SUM(z.y_up),0)::numeric k_up,
          COALESCE(SUM(z.y_tail),0)::numeric k_tail
   FROM (
     SELECT f.y_up,f.y_tail FROM features f
     WHERE f.target_d < r.d AND f.d < r.d
     ORDER BY f.d DESC LIMIT 60
   ) z
 ) h
 WHERE r.d BETWEEN '2025-01-01' AND '2026-09-30'
), scored AS (
 SELECT a.*,f.p_up,f.p_tail FROM arms a
 JOIN fit f USING(arm,gate)
 WHERE a.d BETWEEN '2025-01-01' AND '2026-09-30'
 UNION ALL
 SELECT o.d,o.target_d,o.mdd5,o.v5,o.two_up,o.y_up,o.y_tail,o.high_mdd,o.high_vol,
        'matured60_online'::text arm,TRUE gate,o.p_up,o.p_tail
 FROM online o
), metrics AS (
 SELECT EXTRACT(YEAR FROM d)::int yr,arm,
 COUNT(*) n, SUM(y_up) actual_up, COUNT(*)-SUM(y_up) actual_down,
 SUM(y_tail) actual_tail,
 SUM(CASE WHEN y_up=1 AND p_up>=0.5 THEN 1 ELSE 0 END)::numeric / NULLIF(SUM(y_up),0) up_recall,
 SUM(CASE WHEN y_up=0 AND p_up<0.5 THEN 1 ELSE 0 END)::numeric / NULLIF(COUNT(*)-SUM(y_up),0) down_recall,
 AVG(POWER((p_up-y_up)::double precision,2)) brier_up,
 AVG(POWER((p_tail-y_tail)::double precision,2)) brier_tail,
 COUNT(*) FILTER (WHERE gate) high_n,
 SUM(y_tail) FILTER (WHERE gate) high_tail,
 COUNT(*) FILTER (WHERE NOT gate) low_n,
 SUM(y_tail) FILTER (WHERE NOT gate) low_tail
 FROM scored GROUP BY 1,2
)
SELECT m.yr,m.arm,m.n,m.actual_up,m.actual_down,m.actual_tail,
 ROUND(((m.up_recall+m.down_recall)/2)*100,4) ba_pct,
 ROUND(m.up_recall*100,4) up_recall_pct,
 ROUND(m.down_recall*100,4) down_recall_pct,
 ROUND(m.brier_up::numeric,7) brier_up,
 ROUND(m.brier_tail::numeric,7) brier_tail,
 CASE WHEN m.arm='mdd_q75' THEN m.high_n END high_n,
 CASE WHEN m.arm='mdd_q75' THEN m.high_tail END high_tail,
 CASE WHEN m.arm='mdd_q75' THEN m.low_n END low_n,
 CASE WHEN m.arm='mdd_q75' THEN m.low_tail END low_tail,
 (SELECT COUNT(*) FROM train) train_n,
 (SELECT q_mdd FROM quant) q_mdd,
 (SELECT q_vol FROM quant) q_vol,
(SELECT MIN(n_matured) FROM online WHERE EXTRACT(YEAR FROM d)::int=m.yr) min_matured_n,
(SELECT MAX(n_matured) FROM online WHERE EXTRACT(YEAR FROM d)::int=m.yr) max_matured_n,
(SELECT train_p_tail FROM train_base) train_p_tail
FROM metrics m ORDER BY m.yr,m.arm;