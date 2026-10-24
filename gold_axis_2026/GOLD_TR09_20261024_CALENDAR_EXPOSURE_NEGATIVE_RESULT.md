# TR09 H3 — Calendar-exposure (>=5 calendar days) experiment, executed negative result (2026-10-24)

**Verdict: REJECT / NO MODEL PROMOTION.** This is a new, pre-registered, read-only Neon SQL test, not a proposed unrun model. It does not meet the meaningful-progress notification threshold. Canonical manifest and all original models remain unchanged.

## Provenance and reproducibility
- GitHub branch `gold-execution-channel-audit-20261006` HEAD **before preregistration**: `cbb8cfb8035915db5b05ed2d36c7f5b6a7f09768`; canonical `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md` blob `279dae0b2d5694593adda076d644a5d186241304` checked first.
- Hypothesis frozen **before outcome SQL** in `GOLD_TR09_20261024_CALENDAR_EXPOSURE_H3_PREREG.md` at commit `cb180b321c2827e26895395f45b27451909857fb`.
- Executable **read-only PostgreSQL** reproduction `tools/gold_tr09_20261024_calendar_exposure_reproduce.sql`, committed `0ed67435af447c0879c5d9ccc1074d23e0ace2ed` before execution.
- Actually executed in Neon project `winter-art-94880101`, source `public.gold_research_histdata_xau15m_candidate`; separate second read-only query independently confirmed year × long-calendar counts, UP counts, tail counts and calendar gaps.
- 08:45–09:00 Europe/Istanbul historical HistData M15 close_price is the **09:00 reference quote**, NOT evidence of a zero-latency 09:00 executable fill. Source backfill retrieval was 2026-10-08; historical vendor firstprint/vintage not proven. Calendar-day exposure itself is preknown, but outcome price availability is **NOT source-certified PIT**.
- Fixed calendar excludes enumerated New Year/Good Friday/Christmas closures; missing 2026-09-25 quote is quarantined as outage. All models use exact same qualified origin rows and three subsequent eligible business-date 09:00 target; no crossing missing 09:00 quote in required 5-history/target. Label: UP iff Ptarget>P09; severe DOWN iff Ptarget/P09<=0.98.
- 2023–24 purged training N**496** (247 in 2023, 249 in 2024). Train 2023–24 2%-tail count **27**. No 2025/26 fitting. Long calendar flag `target_date-origin_date>=5` (weekend/holiday span), no optimized threshold. Laplace rates (count+1)/(N+2) for both signed and tail probabilities; UP decision if p>=.5. Five-session vol control Q75 training **0.010206552832574104**.

## Full same-row comparison
All entries in each year share identical scored rows and frozen training; BA = mean of UP and DOWN recall; Brier lower is better.

| Year | Arm | N | BA | UP recall | DOWN recall | UP Brier | >=2% DOWN Brier |
|---|---|---:|---:|---:|---:|---:|---:|
| 2025 | Constant | 258 | 50.00% | 100.00% | 0.00% | 0.2400672 | 0.0822839 |
| 2025 | Two-UP | 258 | 52.51% | 68.94% | 36.08% | 0.2406951 | 0.0822271 |
| 2025 | Volatility Q75 | 258 | 50.00% | 100.00% | 0.00% | 0.2440358 | **0.0795049** |
| 2025 | **Calendar >=5** | 258 | **50.00%** | **100.00%** | **0.00%** | **0.2401858** | **0.0821760** |
| 2026 Jan–Sep | Constant | 188 | 50.00% | 100.00% | 0.00% | 0.2535882 | 0.1920017 |
| 2026 Jan–Sep | Two-UP | 188 | 46.22% | 68.48% | 23.96% | 0.2609284 | 0.1922523 |
| 2026 Jan–Sep | Volatility Q75 | 188 | 50.00% | 100.00% | 0.00% | 0.2585391 | **0.1882070** |
| 2026 Jan–Sep | **Calendar >=5** | 188 | **50.00%** | **100.00%** | **0.00%** | **0.2531117** | **0.1914909** |

2025: 161 UP, 97 DOWN, 23 severe DOWN. 2026: 92 UP, 96 DOWN, 40 severe DOWN.

## Calendar subgroup checks (second SQL independently counted)
- 2023 train: long 4/150=2.67% tail, short 3/97=3.09%.
- 2024 train: long 12/150=8.00%, short 8/99=8.08%.
- 2023–24 pooled train: long 16/300=5.33%, short 11/196=5.61% (hypothesized elevation NOT present).
- 2025: long **14/157=8.92%**, short **9/101=8.91%**, essentially identical.
- 2026 Jan–Sep: long **25/114=21.93%**, short **15/74=20.27%**, weak and not validated.

**Gate:** Calendar tail Brier improves over constant only 0.0001079 in 2025 and 0.0005108 in 2026, but loses to already-tested 5-session volatility in BOTH years (worse by 0.0026711 and 0.0032839). Signed classifier always predicts UP (DOWN recall 0%), no BA gain. Predeclared acceptance failed.

**Scientific limitations:** Repeatedly inspected 2025/2026 are NOT independent holdouts, three-session outcomes overlap, source firstprints and bank bid/ask execution unproven. Do not assert causal weekend effect or trading advantage. Real independent qualification needs 2027 prospective issue-before-outcome, source-vintage certification, same-sample balanced accuracy/UP-DOWN recalls and Brier plus bank spread/slippage.

**Disposition:** Negative result recorded to avoid repetition; no user notification warranted, no production switch, no manifest overwrite.
