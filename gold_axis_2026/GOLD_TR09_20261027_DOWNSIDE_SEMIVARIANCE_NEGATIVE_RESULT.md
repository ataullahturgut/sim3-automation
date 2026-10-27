# TR09 H3 — downside semivariance dominance: executed negative result (2026-10-27)

**Verdict: REJECT / NO MODEL PROMOTION / NO USER ALERT.** One new, preregistered hypothesis actually tested using connected Neon and an independent second SQL subgroup check. No change to canonical manifest or any existing model. Previous 2026-10-22 through 2026-10-26 studies preserved.

## Evidence and provenance
- First inspected branch HEAD `0775ec433353dbb7f6ffe10a92578313a25098f0` and canonical `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md` blob `279dae0b2d5694593adda076d644a5d186241304`.
- Hypothesis preregistration `GOLD_TR09_20261027_DOWNSIDE_SEMIVARIANCE_SHARE_PREREG.md` committed **before** outcome scoring: `8bf6808359264dbbf080e75c5a9a902ed354f843`.
- Reproducible read-only SQL `tools/gold_tr09_20261027_downside_semivariance_reproduce.sql` committed **before** outcome scoring: `46af9a37cc3ddbf6c57cb0c8563bf088bef069e8`. Executed via connected Neon project `winter-art-94880101`, source `public.gold_research_histdata_xau15m_candidate`. A **second read-only SQL**, independently grouping `rows` by year and new flag, confirmed group N, UP/DOWN and severe tail counts and chronology.
- Historical source HistData fixed EST M1->M15, 08:45–09:00 Europe/Istanbul completed 15-minute close used as local 09:00 reference; vendor historical firstprint and bank executable quote at 09:00 **NOT certified**. Data backfill retrieved 2026-10-08. Exactly three NEXT eligible weekdays target and fixed holiday exclusions; 2026-09-25 missing 09:00 quote is an outage. Five prior and current origin anchors and target must be present. Train target_date<=2024-12-31; no 2025/26 refitting or target lookahead. Frozen comparator parity with 2026-10-26 reproduction exact to seven printed decimals.

## Hypothesis and fixed training
Five 09-to-09 log returns `r1..r5`. Downside semivariance share `D5=sum(r_i^2 if r_i<0)/sum(r_i^2)`. NEW gate `D5>0.5`, a fixed sign-dominance threshold; if all returns zero, gate FALSE. Fit two Laplace conditional rates `(k+1)/(n+2)` from purged 2023–24 **N496**. Same rows as constant, two-UP, vol Q75, max drawdown Q75, calendar>=5, and two matured60 controls. The matured60 controls use extra already-matured historical outcomes; the NEW arm does not.

## Exact same-row annual results
BA=balanced accuracy. UP/DOWN recall are direction classification; two Brier columns score continuous UP and >=2% severe DOWN probabilities separately (smaller is better).

| Year | Arm | N | BA % | UP recall % | DOWN recall % | UP Brier | Severe DOWN Brier |
|---|---|---:|---:|---:|---:|---:|---:|
| 2025 | Constant | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2400672 | 0.0822839 |
| 2025 | Two-UP | 258 | 52.5133 | 68.9441 | 36.0825 | 0.2406951 | 0.0822271 |
| 2025 | Vol Q75 | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2440358 | **0.0795049** |
| 2025 | MDD Q75 | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2402204 | 0.0820787 |
| 2025 | Calendar>=5 | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2401858 | 0.0821760 |
| 2025 | Matured60 pooled | 258 | 47.2850 | 83.2298 | 11.3402 | 0.2448019 | 0.0843355 |
| 2025 | Matured60 vol-strat | 258 | 45.9499 | 85.7143 | 6.1856 | 0.2471405 | 0.0787308 |
| 2025 | **NEW downside semivar** | **258** | **50.0000** | **100.0000** | **0.0000** | **0.2397261** | **0.0814371** |
| 2026 Jan–Sep | Constant | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2535882 | 0.1920017 |
| 2026 Jan–Sep | Two-UP | 188 | 46.2183 | 68.4783 | 23.9583 | 0.2609284 | 0.1922523 |
| 2026 Jan–Sep | Vol Q75 | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2585391 | **0.1882070** |
| 2026 Jan–Sep | MDD Q75 | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2545877 | 0.1908302 |
| 2026 Jan–Sep | Calendar>=5 | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2531117 | 0.1914909 |
| 2026 Jan–Sep | Matured60 pooled | 188 | 57.0199 | 61.9565 | 52.0833 | 0.2512439 | 0.1767554 |
| 2026 Jan–Sep | Matured60 vol-strat | 188 | 57.7672 | 72.8261 | 42.7083 | 0.2480173 | 0.1792687 |
| 2026 Jan–Sep | **NEW downside semivar** | **188** | **50.0000** | **100.0000** | **0.0000** | **0.2547399** | **0.1916616** |

2025 actual UP161/DOWN97/severe DOWN23; 2026 UP92/DOWN96/severe DOWN40. NEW tail Brier improves relative to constant by **0.0008468** (2025) and **0.0003401** (2026), but **worsens relative to frozen Vol Q75 by 0.0019322 (2025) and 0.0034546 (2026)**; also worse than pooled matured60 in 2026 by 0.0149062. NEW direction predicts UP on **every** origin (DOWN recall 0%), and 2026 direction Brier worse than constant by 0.0011517. Predeclared acceptance fails unequivocally.

## Independent year × gate audit
| Period | Downside semivar dominance | N | UP | DOWN | >=2% DOWN | Tail rate |
|---|---|---:|---:|---:|---:|---:|
| 2023–24 purged train | FALSE | 268 | 156 | 112 | 18 | 6.7164% |
| 2023–24 purged train | TRUE | 228 | 117 | 111 | 9 | 3.9474% |
| 2025 | FALSE | 178 | 111 | 67 | 19 | 10.6742% |
| 2025 | TRUE | 80 | 50 | 30 | 4 | 5.0000% |
| 2026 Jan–Sep | FALSE | 93 | 45 | 48 | 21 | 22.5806% |
| 2026 Jan–Sep | TRUE | 95 | 47 | 48 | 19 | 20.0000% |

Counterintuitively, prior five-session downside-dominant squared returns correspond to *lower*, not higher, subsequent severe-DOWN incidence in each inspected period, but the magnitude is weak and 2026 separation is only 2.58pp. This is descriptive, not causal or a verified trading signal. It does not justify reversing the sign, adjusting thresholds, or selecting 2025/26 after seeing results. Independent audit verified group totals N496/N258/N188 and chronological 2025 year-end target spillover handled correctly.

## Decision and limits
Reject the new model; leave canonical manifest, existing risk alerts and model files untouched. Historical firstprint unverified; zero-latency 09:00 bank execution unverified; three-session outcomes overlap. Repeatedly inspected 2025/26 are **not independent holdouts**. Real 2027 prospective issue-before-outcome tests with certified vendor release/availability, 09:00 quote and bank BID/ASK cost are mandatory before model promotion. The observed weak conditional-rate inversion is not a user-notification-worthy advance; store negative result to avoid redundant tests.
