# Gold execution: 2026 causal regime research — scientific finding / no unsupported direction edge
**Date:** 2026-10-08. **Targets:** Istanbul DAY 09:00→17:00 and regular weekday OVN 17:00→next09:00; Friday→Monday 64h excluded. **Evidence type:** executed retrospective tests with strictly past-feature origin, multiple years and two 2026 quote-source populations; **not** a new blind 2026 evaluation and **not** bank-executable.

## I. The failed attempt to rescue DOWN classification, actually run
Preregistered `GOLD_EXECUTION_2026_DRIFT_AWARE_PREQUENTIAL_PREREGISTRATION_2026-10-08.md`, script `tools/gold_execution_drift_probe_placeholder_20261008.py`, actual metrics `GOLD_EXECUTION_2026_PREREG_CAUSAL_EW_CLASSBALANCED_20261008_YEAR_METRICS.csv` and paired `..._PAIRED.csv`. Evaluated causal monthly online exponential age-weighting (252-day half-life) with balanced UP/DOWN loss on GVZ and VIX features, 504-day class-balanced rolling window, and their 50:50 probability average versus frozen predecessor HGB. Models had 2020–25 audited source and 2026 Dukascopy-upstream gated mirror (OVN N97, DAY N130), with completed prequential 2023 N187, 2024 N190 and 2025 N192 OVN.
**OVN 2026 balanced accuracy:** previous 2021-start HGB **54.79%**, new EW_GVZ **45.30%**, EW_VIX **46.11%**, rolling 504d **49.29%**, equal blend **44.04%**. Paired relative to HGB: net -8, -7, -4, -9 correct respectively. Even 2025: HGB **53.02% BA** versus all four candidates **46.51–51.21%**. Historical 2023/24 also does not establish consistent gain. Thus class balancing/recency weighting changes prediction prevalence but **does not manufacture predictive information**; reject as direction remedy. Not evidence that the conditional XAU direction is intrinsically impossible; these specific features and models fail to establish a reliable edge.

## II. New target: magnitude before direction, preregistered and run
Registration `GOLD_EXECUTION_ABSOLUTE_MOVE_RISK_ORIGIN_SAFE_PREREG_20261008.md`, program `tools/gold_execution_2026_absolute_move_risk_20261008.py`. Predict **absolute log-return of subsequent OVN session**, not its sign. Ridge(alpha=20, standardized) on strictly prior 4h RV, previous completed DAY absolute return, previous-day GVZ, pre-origin jump fraction, and down semivariance ratio. Monthly chronological refits in 2023/24; 2025 fixed pre2025, 2026 fixed pre2026, **no 2026 target in Ridge fit**. Benchmarked against historical-median absolute move; actual source-qualified samples 2025 N192, 2026 mirror N97 (Jan–Aug20), 2026 direct-primary native N72 (Jan–Oct07). Sources overlap but are NOT independent replications.
- 2025 MAE historical median **42.06bp**, frozen Ridge **41.10bp** (**+2.30%**).
- 2026 mirror MAE historical median **90.62bp**, frozen Ridge **83.08bp** (**+8.32%**).
- 2026 direct primary MAE historical median **90.26bp**, frozen Ridge **81.57bp** (**+9.63%**).
- Crucial failure: 2026 fixed historical alarm threshold marked **100% of nights** as high risk, so it was **not a usable warning**. Signed severe DOWN-risk detection is a separate unproven task.

## III. Causal online risk scale adjustment — empirically improved MAE, NOT signed direction
Registration `GOLD_EXECUTION_2026_DYNAMIC_RELATIVE_VOLATILITY_RISK_PREREG_20261008.md`, implementation `tools/gold_execution_2026_dynamic_relative_vol_risk_20261008.py`. For each issue date t, forecast is frozen Ridge absolute overnight return F_t. Correct it only with **past 63 matured** sessions' log absolute forecast residuals (n/(n+32) shrinkage, multiplier clipped to [0.5,2]). Relative-risk alert threshold is the past 63 corrected prediction 75th percentile, minimum 20 earlier predictions. No intraday future target or in-window 2026 model-fitting leakage. 2026 earlier *matured* outcomes legitimately inform the risk scale on later dates, so this is an **online prequential strategy, not frozen 2026**.

Actual paired 2026 / 2025 MAE:
| Cohort | N | No-skill median (bps) | Frozen Ridge (bps) | Dynamic Ridge (bps) | Dynamic vs no-skill |
|---|---:|---:|---:|---:|---:|
| 2023 DEV | 187 | 26.77 | 27.18 | 27.02 | **-0.96%** |
| 2024 DEV | 190 | 31.58 | 31.01 | 31.39 | **+0.63%** |
| 2025 retrospective | 192 | 42.06 | 41.10 | **39.75** | **+5.49%** |
| 2026 mirror same-upstream | 97 | 90.62 | 83.08 | **79.33** | **+12.46%** |
| 2026 native direct broker | 72 | 90.26 | 81.57 | **77.45** | **+14.20%** |

These gains are descriptive comparisons on already-inspected periods, not causal financial alpha. 2026 direct and mirror source cohorts overlap. Paired daily dynamic-versus-frozen absolute-error wins/losses: 2025 **118/74** (naive paired sign-test p≈.00184, serial dependence caveat), 2026 mirror **58/39** (p≈.067), primary **40/32** (p≈.410). Block-bootstrap month-level dependence audit is separately registered and must be checked before inferential claims.

**Relative DOWN alarm not validated:** 2025 top-risk warning coverage 44.79%, signed extreme-DOWN enrichment **1.28×** baseline; 2026 mirror coverage 34.02%, DOWN enrichment **0.73×** (worse than random-baseline prevalence), 2026 direct coverage 27.78%, enrichment **1.15×** (weak). Thus the risk model helps **magnitude scaling** somewhat but does NOT give a reliable DOWN/reversal alert or a directional trading strategy. No promotion to live intervention.

## IV. Realistic next architecture (hypothesis, not an achieved result)
Two separate heads, with explicit data and authority gates: (1) conditional expected *absolute move* and predicted tail exposure by the existing risk scale, (2) event-specific **signed direction / severe-downside** specialist using exact release-time US macro surprise, intraday US real yields/DXY and Fed preannounced calendar, all point-in-time and available before 17:00 Turkey decision. Avoid pretending same-day published after-17 macro actual was known at 17. Treat macro releases after 17 as **uncertainty/event hazard**, never use the surprise before its publication. Third head is action policy with **ABSTAIN** by expected executable gain after real Turkish bank BID/ASK spread, not raw 50/50 direction. A directional model can be approved only with earlier pre-registered later prospective cohorts; 2026 outcomes have already been studied. Evaluate each forecast class's conditional payoff (UP opportunity / DOWN hedge / abstain), error size, coverage, false alarms, worst-tail misses, and bank cost.

**Scientific decision today:** direction improvement experiments were falsified; a **measurable but unpromoted absolute-size risk forecasting channel** has emerged. Distinguish this technical progress from a proven profitable trade or a reliably caught severe decline.
