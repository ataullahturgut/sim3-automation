# TR09 H3 — five-return volatility acceleration: executed negative result (2026-10-30)

**Decision: REJECT / NO PROMOTION / NO USER ALERT.** One new preregistered hypothesis was actually tested against connected Neon source observations, with a second independent SQL audit. It did **not** improve both-year tail-risk calibration or two-sided directional classification. No canonical manifest, previous model or earlier research file was changed.

## Exact chronology and evidence
- Inspected live research branch HEAD **`f52aa6c7e06cb5041cb945e169d2c88453bb18a8`** (2026-10-29 prior negative report) and canonical `gold_axis_2026/GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md` blob **`279dae0b2d5694593adda076d644a5d186241304`** before any new work. Read 2026-10-27/28/29 experiments and avoided duplicating them.
- Preregistered **`GOLD_TR09_20261030_VOL_ACCELERATION_PREREG.md`** commit **`4c54b918434ba141da054d1ccd248fefa06d0240`** before querying outcomes.
- Froze read-only, reproducible **`tools/gold_tr09_20261030_vol_acceleration_reproduce.sql`** commit **`4c221289f2bda8bf83abbfff8fc68d6ad2bfe4e6`** before querying outcomes. SQL blob **`78e3b88c7e3235205bbe1312c5df99fae1a21ade`**.
- Ran frozen SQL via connected Neon project **`winter-art-94880101`**, `public.gold_research_histdata_xau15m_candidate`. Independently rebuilt eligible calendar + LAG/LEAD 09:00 anchors and subgroup labels in separate read-only SQL **`tools/gold_tr09_20261030_vol_acceleration_independent_audit.sql`**, commit **`064b778e1ed33b6d241428e08f52004ba8fd9ab8`**; second query agreed on N and event counts.
- Five completed previous 09:00-to-09:00 log returns `r1..r5` (r1 oldest). Gate `RMS(r4,r5)/RMS(r1,r2,r3)>=1.5`; zero denominator => FALSE. Historical HistData fixed-EST BID M15 bars starting 08:45 TRT and completing 09:00. The source archive was backfilled later: vendor firstprint, 09:00 receipt latency, and executable Turkish-bank BID/ASK at 09:00 are **NOT certified**. This is source-clock-aligned retrospective research, not proven live PIT/09:00 bank-executable signal.
- Frozen target: third next eligible weekday 09:00 BID anchor vs origin, UP if target>origin, severe DOWN if target/origin<=0.98. Frozen holiday exclusions and source completeness as 2026-10-29. Purged 2023–24 fit **N496** with target_date<=2024-12-31. Fixed binary gate, Laplace `(k+1)/(n+2)` conditional UP/tail probabilities. No 2025/26 labels used to fit new arm. Matured60 comparator labels restricted to `target_d<origin_d`; observed maturity violations **0**.

## Same-row annual comparison (all eight arms)
BA=balanced accuracy; UP/DOWN recall are classification recall; lower Brier is better. **2025 all arms N258 (actual UP161/DOWN97/severe-DOWN23); 2026 Jan–Sep all arms N188 (UP92/DOWN96/severe-DOWN40).**

| Year | Arm | N | BA % | UP recall % | DOWN recall % | UP Brier | Severe-DOWN Brier |
|---|---|---:|---:|---:|---:|---:|---:|
| 2025 | Constant | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2400672 | 0.0822839 |
| 2025 | Two-UP | 258 | 52.5133 | 68.9441 | 36.0825 | 0.2406951 | 0.0822271 |
| 2025 | Vol Q75 | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2440358 | 0.0795049 |
| 2025 | MDD Q75 | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2402204 | 0.0820787 |
| 2025 | Calendar >=5 | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2401858 | 0.0821760 |
| 2025 | Matured60 pooled | 258 | 47.2850 | 83.2298 | 11.3402 | 0.2448019 | 0.0843355 |
| 2025 | Matured60 vol-strat | 258 | 45.9499 | 85.7143 | 6.1856 | 0.2471405 | 0.0787308 |
| 2025 | **NEW vol acceleration >=1.5** | **258** | **50.0000** | **100.0000** | **0.0000** | **0.2392180** | **0.0822277** |
| 2026 Jan–Sep | Constant | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2535882 | 0.1920017 |
| 2026 Jan–Sep | Two-UP | 188 | 46.2183 | 68.4783 | 23.9583 | 0.2609284 | 0.1922523 |
| 2026 Jan–Sep | Vol Q75 | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2585391 | 0.1882070 |
| 2026 Jan–Sep | MDD Q75 | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2545877 | 0.1908302 |
| 2026 Jan–Sep | Calendar >=5 | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2531117 | 0.1914909 |
| 2026 Jan–Sep | Matured60 pooled | 188 | 57.0199 | 61.9565 | 52.0833 | 0.2512439 | 0.1767554 |
| 2026 Jan–Sep | Matured60 vol-strat | 188 | 57.7672 | 72.8261 | 42.7083 | 0.2480173 | 0.1792687 |
| 2026 Jan–Sep | **NEW vol acceleration >=1.5** | **188** | **50.0000** | **100.0000** | **0.0000** | **0.2530764** | **0.1914003** |

Existing seven comparator metrics exactly match the 2026-10-29 frozen result to seven decimals. New method is **worse** than Vol Q75 tail Brier by **0.0027228 (2025)** and **0.0031933 (2026)**; worse than Matured60 vol-strat by **0.0034969** and **0.0121316**. Despite small improvements in UP Brier relative to constant, the new method predicts UP **on every origin**, DOWN recall **0%**, BA **50%** both years. No reliable two-sided skill.

## Independent subgroup audit

| Period | Acceleration >=1.5 | N | UP | DOWN | Severe DOWN | Tail frequency |
|---|---|---:|---:|---:|---:|---:|
| 2023–24 purged train | FALSE | 366 | 198 | 168 | 20 | 5.4645% |
| 2023–24 purged train | TRUE | 130 | 75 | 55 | 7 | 5.3846% |
| 2025 | FALSE | 191 | 115 | 76 | 19 | 9.9476% |
| 2025 | TRUE | 67 | 46 | 21 | 4 | 5.9701% |
| 2026 Jan–Sep | FALSE | 137 | 65 | 72 | 28 | 20.4380% |
| 2026 Jan–Sep | TRUE | 51 | 27 | 24 | 12 | 23.5294% |

Independent query agrees on totals **496/258/188**, all UP/DOWN/tail counts, target chronology violations **0**, train-purge violations **0**. The conditional association is flat in training, appears protective in 2025, and risky in 2026: **no stable risk direction**. All TRUE/FALSE subgroups exceed N30; the rejection is not merely insufficient subgroup count.

## Final scientific decision

**Reject.** Predeclared BA>=52.5%, DOWN recall>=20%, and severe-tail Brier beating BOTH controls in BOTH years all fail. Do not invert threshold, change year weights, re-fit after inspection, or promote a 2026-specific alarm. H3 target outcomes overlap; 2025/26 are repeatedly inspected and **not independent validation**. 2027 truly prospective, timestamped before-outcome issues and independently verified provider firstprint plus bank 09:00 BID/ASK and all-in costs are required before any operational model claim. Preserve canonical manifest and previous model authority.
