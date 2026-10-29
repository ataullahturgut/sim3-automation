# TR09 H3 — five-return shock concentration: executed negative result (2026-10-29)

**Verdict: REJECT / NO MODEL PROMOTION / NO USER ALERT.** A new frozen-before-scoring hypothesis was executed against real connected Neon historical observations, with an independently grouped second SQL audit. The new method failed the preregistered two-year criteria. Canonical manifest and existing models were not altered.

## Provenance and chronological protocol
- First inspected live branch `gold-execution-channel-audit-20261006` HEAD **`58f987a7de81b49aff0f49efc9a20382f33c521a`**, and canonical manifest `gold_axis_2026/GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md` blob **`279dae0b2d5694593adda076d644a5d186241304`**. Verified existing 2026-10-21 through 2026-10-28 TR09 research and avoided repeating its gate.
- Before outcome queries, preregistered `GOLD_TR09_20261029_FIVE_RETURN_SHOCK_CONCENTRATION_PREREG.md` commit **`7864750bfd5a27371a001238bcd7f308074eb440`**, then froze exact read-only `tools/gold_tr09_20261029_shock_concentration_reproduce.sql` commit **`b608d5529183e995b5b50a9442b6c52a3c4068a9`**. Both preceded scoring.
- Ran frozen SQL via connected Neon project `winter-art-94880101` against `public.gold_research_histdata_xau15m_candidate`, then independently grouped subgroup audit `tools/gold_tr09_20261029_shock_concentration_subgroup_audit.sql` (commit `7da0865d9415d950bd2c81e5d3a1ae9f5f891c8c`). All queries read-only.
- Historical 08:45–09:00 TRT M15 BID bar CLOSE defines the reference at 09:00; the exact same eligible-weekday calendar, 3-next-eligible-day H3 target, missing-anchor rules and 2023–24 train purging as 2026-10-28. Historical vendor firstprint, quote receipt latency, exact executable bank 09:00 ASK/BID and real transaction cost **NOT proven**. This is retrospective source-timestamp-aligned research, not certified PIT bank execution.
- Frozen binary feature: `max(abs(log(p_i/p_(i-1)))) / sum(abs(log(p_i/p_(i-1)))) >= 0.50` across five completed 09-to-09 intervals. Zero denominator => FALSE. Laplace `(k+1)/(n+2)` conditional UP and >=2% severe-DOWN rates fitted **only** on 2023–24 with `target_d<=2024-12-31` (N496). Matured60 comparators use `target_d<origin`; zero maturity violations and zero max-target violations in both test periods.
- Additional source integrity check (read-only): 984 eligible 08:45 TRT source anchors spanning 2022-12-01 to 2026-09-30, zero duplicated anchor dates, zero nonpositive closes, zero bar-completion clock mismatches (08:45 +15min =09:00 TRT). These checks do not certify provider firstprint.

## Same-origin-row retrospective annual comparison
BA is balanced accuracy; UP/DOWN recalls are classification recall, Brier columns score continuous UP and severe DOWN probabilities (lower is better). **All eight arms use the same 258 origins in 2025 and 188 origins in 2026 Jan–Sep**.

| Period | Arm | N | BA % | UP recall % | DOWN recall % | UP Brier | Severe DOWN Brier |
|---|---|---:|---:|---:|---:|---:|---:|
| 2025 | Constant | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2400672 | 0.0822839 |
| 2025 | Two-UP | 258 | 52.5133 | 68.9441 | 36.0825 | 0.2406951 | 0.0822271 |
| 2025 | Vol Q75 | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2440358 | 0.0795049 |
| 2025 | MDD Q75 | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2402204 | 0.0820787 |
| 2025 | Calendar >=5 | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2401858 | 0.0821760 |
| 2025 | Matured60 pooled | 258 | 47.2850 | 83.2298 | 11.3402 | 0.2448019 | 0.0843355 |
| 2025 | Matured60 vol-strat | 258 | 45.9499 | 85.7143 | 6.1856 | 0.2471405 | 0.0787308 |
| 2025 | **NEW shock concentration >=50%** | **258** | **50.0000** | **100.0000** | **0.0000** | **0.2413584** | **0.0821507** |
| 2026 Jan–Sep | Constant | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2535882 | 0.1920017 |
| 2026 Jan–Sep | Two-UP | 188 | 46.2183 | 68.4783 | 23.9583 | 0.2609284 | 0.1922523 |
| 2026 Jan–Sep | Vol Q75 | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2585391 | 0.1882070 |
| 2026 Jan–Sep | MDD Q75 | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2545877 | 0.1908302 |
| 2026 Jan–Sep | Calendar >=5 | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2531117 | 0.1914909 |
| 2026 Jan–Sep | Matured60 pooled | 188 | 57.0199 | 61.9565 | 52.0833 | 0.2512439 | 0.1767554 |
| 2026 Jan–Sep | Matured60 vol-strat | 188 | 57.7672 | 72.8261 | 42.7083 | 0.2480173 | 0.1792687 |
| 2026 Jan–Sep | **NEW shock concentration >=50%** | **188** | **50.0000** | **100.0000** | **0.0000** | **0.2546104** | **0.1915787** |

Actual 2025 UP/DOWN/severe-DOWN = **161/97/23**, 2026 = **92/96/40**. Frozen comparator scores match prior 2026-10-28 published baseline metrics to 7 decimals. The NEW severe-DOWN Brier loses to Vol Q75 by **0.0026458 (2025)** and **0.0033717 (2026)**, and to Matured60 vol-strat by **0.0034199** and **0.0123100** respectively. The NEW method classifies **every** date as UP, so DOWN recall =0% in both periods; BA=50%.

## Independent year-by-gate subgroup audit
| Period | Gate | N | UP | DOWN | Severe DOWN | Severe DOWN rate |
|---|---|---:|---:|---:|---:|---:|
| 2023–24 purged train | FALSE | 389 | 205 | 184 | 22 | 5.6555% |
| 2023–24 purged train | TRUE | 107 | 68 | 39 | 5 | 4.6729% |
| 2025 | FALSE | 224 | 138 | 86 | 20 | 8.9286% |
| 2025 | TRUE | 34 | 23 | 11 | 3 | 8.8235% |
| 2026 Jan–Sep | FALSE | 145 | 70 | 75 | 28 | 19.3103% |
| 2026 Jan–Sep | TRUE | 43 | 22 | 21 | 12 | 27.9070% |

Second SQL verified subgroup totals **496/258/188**, target-date ordering violation **0** in all groups. Concentration predicts *lower* tail frequency in train, almost no separation in 2025, and higher frequency in 2026. The 2026 difference is descriptive and not stable transport; do not reverse or retune the gate after results.

## Scientific decision
All frozen acceptance criteria fail (both years BA<52.5%, DOWN recall<20%, severe-tail Brier worse than both predeclared controls). The subgroup sample minimum 30 is satisfied (2025 TRUE34, 2026 TRUE43), so failure is not merely due to unsupported gate. **Reject new arm; no forecast-skill gain and no new alert.** Three-day outcomes overlap; 2025/2026 are heavily previously inspected and **not** independent validation. Source-provider firstprint and bank execution clock remain unproven. Future promotion requires 2027 truly prospective, timestamped, before-outcome predictions with certified quote readiness and realistic all-in bank ASK/BID cost. Keep previous models and canonical manifest untouched.
