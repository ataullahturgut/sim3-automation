-- Independent H3 negative five-return path-efficiency subgroup audit (2026-10-31).
-- Unlike main query's six per-date joins, this builds one eligible-calendar timeline with window LAG/LEAD.
-- Read-only, does not refit or modify any data. Firstprint and bank ASK/BID remain unverified.
WITH cal AS (
 SELECT d::date d
 FROM generate_series('2022-12-01'::date,'2026-10-15'::date,'1 day') d
 WHERE EXTRACT(ISODOW FROM d)<6 AND d::date NOT IN
 ('2023-01-02','2023-04-07','2023-12-25','2024-01-01','2024-03-29','2024-12-25',
  '2025-01-01','2025-04-18','2025-12-25','2026-01-01','2026-04-03')
), anchor AS (
 SELECT (bar_start_utc AT TIME ZONE 'Europe/Istanbul')::date d,close_price p,
        (bar_start_utc AT TIME ZONE 'Europe/Istanbul')::time bar_local,
        native_minute_bars, bar_start_utc
 FROM public.gold_research_histdata_xau15m_candidate
 WHERE native_minute_bars=15
   AND (bar_start_utc AT TIME ZONE 'Europe/Istanbul')::time=TIME '08:45:00'
   AND bar_start_utc >= '2022-12-01'::timestamptz
   AND bar_start_utc < '2026-10-16'::timestamptz
), timeline AS (
 SELECT c.d, a.p,
 LAG(a.p,1) OVER w p4, LAG(a.p,2) OVER w p3,
 LAG(a.p,3) OVER w p2, LAG(a.p,4) OVER w p1,
 LAG(a.p,5) OVER w p0,
 LEAD(a.p,3) OVER w pt, LEAD(c.d,3) OVER w target_d
 FROM cal c LEFT JOIN anchor a ON a.d=c.d
 WINDOW w AS (ORDER BY c.d)
), scored AS (
 SELECT d,target_d,
 COALESCE(LN(p/p0)/NULLIF(ABS(LN(p1/p0))+ABS(LN(p2/p1))+ABS(LN(p3/p2))+ABS(LN(p4/p3))+ABS(LN(p/p4)),0.0),0.0)<=-0.50 gate,
 (pt>p)::int y_up,(pt/p<=0.98)::int y_tail
 FROM timeline
 WHERE d BETWEEN '2023-01-01' AND '2026-09-30'
 AND p IS NOT NULL AND p0 IS NOT NULL AND p1 IS NOT NULL AND p2 IS NOT NULL
 AND p3 IS NOT NULL AND p4 IS NOT NULL AND pt IS NOT NULL
), classified AS (
 SELECT CASE WHEN d<='2024-12-31' AND target_d<='2024-12-31' THEN '2023-24_PURGED_TRAIN'
             WHEN d BETWEEN '2025-01-01' AND '2025-12-31' THEN '2025'
             WHEN d BETWEEN '2026-01-01' AND '2026-09-30' THEN '2026_JAN_SEP'
             ELSE 'EXCLUDED' END period,*
 FROM scored
)
SELECT period,gate,COUNT(*) n,SUM(y_up) up_count,
 COUNT(*)-SUM(y_up) down_count,SUM(y_tail) tail_count,
 ROUND(100.0*SUM(y_tail)/NULLIF(COUNT(*),0),4) tail_rate_pct,
 COUNT(*) FILTER (WHERE target_d<=d) bad_target_order,
 COUNT(*) FILTER (WHERE period='2023-24_PURGED_TRAIN' AND target_d>'2024-12-31') bad_train_purge
FROM classified WHERE period<>'EXCLUDED'
GROUP BY period,gate ORDER BY period,gate;
