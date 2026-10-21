# TR09 H3 — Two consecutive UP sessions as downside-risk warning (2026-10-21)
Status: EXPLORATORY NEGATIVE RESULT — DO NOT PROMOTE. Separate note; no original model/manifest changes.
Branch HEAD read before experiment: `45aed5751b69186a3474a947039b24e94b14505a`.
Manifest `gold_axis_2026/GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md` blob SHA `279dae0b2d5694593adda076d644a5d186241304`.

## Frozen one-feature hypothesis
At the **09:00 Europe/Istanbul** decision point, two successive positive session-to-session 09:00 returns might warn of a reversal and a future >=2% loss over **three eligible weekdays**. Origin anchor is the **08:45–09:00 TR M15 close** (05:45 UTC bar start, completed by 06:00 UTC). Feature uses origin and two prior eligible sessions only. Outcome is `P(target09)/P(origin09)-1`; tail if <=-0.02. Calendar excludes weekends, Jan 2 2023, Jan 1 2024/25/26, Good Fridays 2023-04-07/2024-03-29/2025-04-18/2026-04-03, and Christmas 2023/24/25. **2026-09-25 is a missing 09:00 quote, NOT a holiday**, and any sample whose origin, prior, or target quote is missing is excluded; no gap jumping. Requires exactly 15 underlying M1 records for the M15 origin and historical anchors.

2023–24 train rows 503, with last 3 origins **purged** because their target labels land in 2025: 2024-12-27→2025-01-02, 2024-12-30→2025-01-03, 2024-12-31→2025-01-06. Train probabilities use Laplace (events+1)/(N+2), separately for streak vs nonstreak. Train P(UP): constant 0.548515; streak 0.470968; nonstreak 0.582386. Train P(tail): constant 0.061386; streak 0.064516; nonstreak 0.062500. Direction decision uses probability>=0.5.

## Exact-date results (full candidate HistData source)
| Year | N | Model | Balanced accuracy % | UP recall % | DOWN recall % | Direction Brier |
|---|---:|---|---:|---:|---:|---:|
| 2025 | 258 | Constant train rate | 50.00 | 100.00 | 0.00 | 0.240319 |
| 2025 | 258 | Two-UP streak | 52.51 | 68.94 | 36.08 | 0.240870 |
| 2026 | 188 | Constant train rate | 50.00 | 100.00 | 0.00 | 0.253386 |
| 2026 | 188 | Two-UP streak | 46.22 | 68.48 | 23.96 | 0.260452 |

2025 tail Brier constant 0.081971 vs streak 0.081885; 2026 constant 0.190412 vs streak 0.190040 (tiny, nonrobust). Streak tail frequency 2025 **7/85**, nonstreak **16/173**; 2026 streak **5/52**, nonstreak **35/136**. Hypothesis is not supported consistently, direction calibration worsens in both years, so reject.

## Same-date legacy comparison (diagnostic, NOT equal horizon)
Frozen `GOLD_R66_20261012_H3_09_CARRY_15_1645_EXECUTION_TARGET_MODELS_ALLROWS.csv`, `clock=09`, matched by `entry_date`. **ALL** old `source_D3` dates differ from this experiment's three-eligible-weekday target: 2025 247/247, 2026 184/184. Legacy H3 `h3prob` and R66 `logit_p` are therefore scored on a different outcome **for diagnostics only**, never a fair native-model ranking.

| Year | Same N | Model | BA % | UP recall % | DOWN recall % | Brier |
|---|---:|---|---:|---:|---:|---:|
| 2025 | 247 | Constant | 50.00 | 100.00 | 0.00 | 0.239587 |
| 2025 | 247 | Streak | 52.29 | 70.51 | 34.07 | 0.240020 |
| 2025 | 247 | Legacy H3 (mismatched horizon) | 43.54 | 59.62 | 27.47 | 0.301526 |
| 2025 | 247 | Legacy R66 (mismatched horizon) | 44.64 | 59.62 | 29.67 | 0.257864 |
| 2026 | 184 | Constant | 50.00 | 100.00 | 0.00 | 0.253936 |
| 2026 | 184 | Streak | 45.81 | 67.42 | 24.21 | 0.261427 |
| 2026 | 184 | Legacy H3 (mismatched horizon) | 57.11 | 58.43 | 55.79 | 0.298433 |
| 2026 | 184 | Legacy R66 (mismatched horizon) | 53.77 | 52.81 | 54.74 | 0.249456 |

## Reproduction: read-only anchor extraction
```sql
WITH cal AS (
 SELECT d::date d, ROW_NUMBER() OVER(ORDER BY d)::int rn
 FROM generate_series('2022-12-15'::date,'2026-10-10'::date,'1 day') d
 WHERE EXTRACT(ISODOW FROM d)<6 AND d::date NOT IN
 ('2023-01-02','2023-04-07','2023-12-25','2024-01-01','2024-03-29','2024-12-25',
  '2025-01-01','2025-04-18','2025-12-25','2026-01-01','2026-04-03')
), a AS (
 SELECT (bar_start_utc AT TIME ZONE 'Europe/Istanbul')::date d, close_price p
 FROM gold_research_histdata_xau15m_candidate
 WHERE native_minute_bars=15
 AND EXTRACT(HOUR FROM bar_start_utc AT TIME ZONE 'Europe/Istanbul')=8
 AND EXTRACT(MINUTE FROM bar_start_utc AT TIME ZONE 'Europe/Istanbul')=45
 AND bar_start_utc>='2022-12-15' AND bar_start_utc<'2026-10-01'
)
SELECT c.d::text d,t.d::text target_d,a.p p,b.p p1,e.p p2,z.p p3
FROM cal c JOIN cal v ON v.rn=c.rn-1 JOIN cal w ON w.rn=c.rn-2
JOIN cal t ON t.rn=c.rn+3 JOIN a ON a.d=c.d
JOIN a b ON b.d=v.d JOIN a e ON e.d=w.d JOIN a z ON z.d=t.d
WHERE c.d BETWEEN '2023-01-01' AND '2026-09-30' ORDER BY c.d;
```
For each row, `streak=(p>p1 && p1>p2)`, `y=(p3>p)`, `tail=(p3/p<=0.98)`; fit rates only for `year(d)<=2024 AND target_d<='2024-12-31'`; score 2025/2026 without refitting. Balanced accuracy = mean(UP recall, DOWN recall). Brier = mean((prob-y)^2). R66 diagnostic join by `entry_date=d`, filter `clock=09`.

**Source governance:** HistData candidate archived `retrieved_at_utc` 2026-10-08, not historical first publication; origin-time data availability cannot be independently certified. 2025/26 have been repeatedly examined and are NOT independent holdouts. Need 2027 locked prospective evaluation with true publication-time and executable bank bid/ask before any investment claim. No new model accepted.
