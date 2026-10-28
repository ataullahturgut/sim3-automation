# TR09 H3 — Five-day sign-chop >=3: executed negative result (2026-10-28)

**Verdict: REJECT / NO PROMOTION / NO USER ALERT.** Executed a genuinely new frozen hypothesis, compared all models on identical dated rows, and independently audited group counts with a second SQL expression. No production model or canonical manifest modified.

## Traceable chronology
- Inspected branch HEAD `979fe7d33095830e15112d7f436f616f38ea6a22` and canonical manifest blob `279dae0b2d5694593adda076d644a5d186241304` before any write.
- Preregistered `GOLD_TR09_20261028_SIGN_CHOP_PREREG.md` in commit `d7acf967ffe1163355e0dce35ba7ac86f51d7916`, before scoring.
- Saved runnable read-only `tools/gold_tr09_20261028_sign_chop_reproduce.sql` in commit `429b325cf7f48bf2e0fa7ba7dd52974774fdfcc2`, before scoring.
- Executed that SQL via connected Neon project `winter-art-94880101`, table `public.gold_research_histdata_xau15m_candidate`; then executed independent SQL using `SIGN(delta_i)*SIGN(delta_{i+1})=-1` instead of original boolean predicates. 2023–24 purged train N496; 2025 N258; 2026 Jan–Sep N188. No target_date<=origin violations in the independently checked cohort.

## Frozen experiment
Five previous complete 09-to-09 BID M15-anchor returns; gate TRUE if at least 3 of 4 adjacent return-sign pairs reverse. Zero returns never contribute a reversal. Binary UP and >=2% DOWN next-three-eligible-weekday targets; original HistData fixed EST, bar-start 08:45 TRT with 09:00 bar completion. 2023–24 purged fit; Laplace-smoothed conditional event rates; no threshold tuning on 2025/2026. Comparator logic unchanged from 2026-10-27.

## Exact same-row results

| Year | Arm | N | BA % | UP recall % | DOWN recall % | UP Brier | >=2% DOWN Brier |
|---|---|---:|---:|---:|---:|---:|---:|
| 2025 | Constant | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2400672 | 0.0822839 |
| 2025 | Two-UP | 258 | 52.5133 | 68.9441 | 36.0825 | 0.2406951 | 0.0822271 |
| 2025 | Vol Q75 | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2440358 | 0.0795049 |
| 2025 | MDD Q75 | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2402204 | 0.0820787 |
| 2025 | Calendar >=5 | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2401858 | 0.0821760 |
| 2025 | Matured60 pooled | 258 | 47.2850 | 83.2298 | 11.3402 | 0.2448019 | 0.0843355 |
| 2025 | Matured60 vol-strat | 258 | 45.9499 | 85.7143 | 6.1856 | 0.2471405 | 0.0787308 |
| 2025 | **NEW sign-chop >=3** | **258** | **50.0000** | **100.0000** | **0.0000** | **0.2394150** | **0.0833596** |
| 2026 Jan–Sep | Constant | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2535882 | 0.1920017 |
| 2026 Jan–Sep | Two-UP | 188 | 46.2183 | 68.4783 | 23.9583 | 0.2609284 | 0.1922523 |
| 2026 Jan–Sep | Vol Q75 | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2585391 | 0.1882070 |
| 2026 Jan–Sep | MDD Q75 | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2545877 | 0.1908302 |
| 2026 Jan–Sep | Calendar >=5 | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2531117 | 0.1914909 |
| 2026 Jan–Sep | Matured60 pooled | 188 | 57.0199 | 61.9565 | 52.0833 | 0.2512439 | 0.1767554 |
| 2026 Jan–Sep | Matured60 vol-strat | 188 | 57.7672 | 72.8261 | 42.7083 | 0.2480173 | 0.1792687 |
| 2026 Jan–Sep | **NEW sign-chop >=3** | **188** | **50.0000** | **100.0000** | **0.0000** | **0.2551491** | **0.1878763** |

Train/2025/2026 actual UP/DOWN/tail: 273/223/27; 161/97/23; 92/96/40. Frozen comparator scores exactly replicate 2026-10-27 report to printed seven decimals. Matured60 origin-safe check: bad maturity 0 and bad max target 0 in both years; minimum 60 eligible matured observations and vol-strat minimum matched count 4.

## Independent subgroup falsification

| Period | Flag | N | UP | DOWN | >=2% DOWN | Tail rate |
|---|---|---:|---:|---:|---:|---:|
| 2023–24 purged train | FALSE | 351 | 191 | 160 | 14 | 3.99% |
| 2023–24 purged train | TRUE | 145 | 82 | 63 | 13 | 8.97% |
| 2025 | FALSE | 186 | 111 | 75 | 18 | 9.68% |
| 2025 | TRUE | 72 | 50 | 22 | 5 | 6.94% |
| 2026 Jan–Sep | FALSE | 135 | 73 | 62 | 21 | 15.56% |
| 2026 Jan–Sep | TRUE | 53 | 19 | 34 | 19 | 35.85% |

Conditional tail-risk association varies substantially by year: high sign-chop is riskier in training and 2026 but *less* risky in 2025. This is not a robust predictor. 2026 new risk Brier beats frozen vol Q75 by only **0.0003307**, but loses badly to matured60 vol-strat by **0.0086076**; 2025 loses to both vol Q75 and matured60 vol-strat by **0.0038547** and **0.0046288**. Direction BA 50% and DOWN recall 0% in both. Prespecified acceptance fails on all three performance criteria, despite sufficient subgroup N.

## Scientific limits and decision
No automatic reversal or posthoc cutoff selection. The 2026 subgroup concentration is exploratory and is NOT a tradeable alert: 2025/26 were repeatedly inspected, H3 labels overlap, and historical price availability at the exact decision instant is not independently proven. HistData historical BID archive and retrospective 08:45–09:00 M15 close do not certify provider firstprint or 09:00 zero-latency bank ASK/BID. Historical holiday set remains limited and may omit special closures. Require true timestamp-certified 2027 prospective issues and bank execution-cost evidence before any promotion. Preserve original models, manifest, source data and earlier negative-result files.