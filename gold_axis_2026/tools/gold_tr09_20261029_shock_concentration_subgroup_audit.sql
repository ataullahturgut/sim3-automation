-- Independent read-only year x gate subgroup audit of frozen 2026-10-29 H3 shock concentration protocol.
-- The source calendar/anchor CTE is reused unchanged, but the aggregate independently verifies N, labels and time order.
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
 COALESCE(GREATEST(ABS(LN(b.p1/b.p0)), ABS(LN(b.p2/b.p1)), ABS(LN(b.p3/b.p2)), ABS(LN(b.p4/b.p3)), ABS(LN(b.p5/b.p4))) / NULLIF(ABS(LN(b.p1/b.p0)) + ABS(LN(b.p2/b.p1)) + ABS(LN(b.p3/b.p2)) + ABS(LN(b.p4/b.p3)) + ABS(LN(b.p5/b.p4)),0.0) >= 0.50, FALSE) shock_concentration_ge50,
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
)
SELECT CASE WHEN d<='2024-12-31' AND target_d<='2024-12-31' THEN 'TRAIN_2023_24' ELSE EXTRACT(YEAR FROM d)::text END period,
 shock_concentration_ge50 gate, COUNT(*) n,
 SUM(y_up) actual_up,COUNT(*)-SUM(y_up) actual_down,SUM(y_tail) actual_tail,
 ROUND(AVG(y_tail::numeric)*100,4) severe_down_rate_pct,
 MIN(d) min_origin,MAX(d) max_origin,MAX(target_d) max_target,
 COUNT(*) FILTER (WHERE target_d<=d) invalid_target_order
FROM rows
WHERE (d BETWEEN '2023-01-01' AND '2024-12-31' AND target_d<='2024-12-31') OR d BETWEEN '2025-01-01' AND '2026-09-30'
GROUP BY 1,2 ORDER BY 1,2;
