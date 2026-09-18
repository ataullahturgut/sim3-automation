# GOLD CONTROL — DIRECTION_BCT_CTW_V1_RESEARCH PRE-2025 CHECKPOINT

**Date:** 2026-09-18  
**Identity:** `DIRECTION_BCT_CTW_V1_RESEARCH`  
**Status:** `PRE2025_CHECKPOINT_COMPLETE / FROZEN_BEFORE_BCT_V1_2025_REPLAY`  
**Evidence:** `PRE2025_RETROSPECTIVE_TIME_ORDERED_RESEARCH`  
**Preregistration:** `gold_axis_2026/GOLD_CONTROL_DIRECTION_BCT_CTW_V1_PREREG_2026-09-18.md`  
**Implementation:** `gold_axis_2026/tools/direction_bct_ctw_v1_research.py`

## 1. Frozen model actually evaluated

The model uses the same rolling 52 weekly Gold return signs as RSM-52 and VLMC-BS-52.

For weekly close `C_w`:

`r_w = ln(C_w/C_(w-1))`

`x_w = 1[r_w > 0]`.

Frozen BCT/CTW parameters:
- alphabet `m=2` = DOWN/UP;
- maximum context depth `D=10`;
- tree-prior parameter `beta=0.5`;
- independent Jeffreys transition prior `Dirichlet(1/2,1/2)`;
- no hyperparameter grid search;
- no randomization.

Each 52-symbol rolling window is partitioned as:
- first 10 signs = fixed initial context;
- final 42 signs = CTW observations.

At each tree node with transition count vector `a_s=(a_s(0),a_s(1))`, the exact integrated local likelihood is

`P_e(a_s)=Gamma(1)/Gamma(M_s+1) * product_j Gamma(a_s(j)+1/2)/Gamma(1/2)`.

The exact CTW recursion is:
- at depth 10: `P_w,s=P_e,s`;
- otherwise:
  `P_w,s=0.5*P_e,s+0.5*P_w,s0*P_w,s1`.

For each forecast origin, the two candidate continuations DOWN and UP are scored exactly. The normalized posterior predictive is

`P(UP)=q_1/(q_0+q_1)`.

Direction:
- UP if `P(UP)>=0.5`;
- DOWN otherwise.

## 2. Data and chronology

Source:
`XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`.

Weekly construction:
- Monday-Friday New York-local observations only;
- weekly close = last actually observed governed weekday in each Monday-start calendar week;
- no interpolation;
- no forward-fill;
- no alternate-provider substitution.

Chronology:
- 2022-03 onward: warm-up/history;
- 2023: implementation/development audit;
- 2024: fixed pre-2025 validation;
- 2025: not used to choose D, beta, window, prior, threshold or features under BCT V1.

The first valid BCT target week is 2023-03-06 after the 52-sign warm-up.

## 3. 2023 development/audit result

- n = 43
- accuracy = 0.5581395349
- balanced accuracy = 0.5877192982
- Brier score = 0.2578115669
- log loss = 0.7088809659
- actual UP / DOWN = 24 / 19
- forecast UP / DOWN = 11 / 32
- UP sensitivity = 0.3333333333
- DOWN sensitivity = 0.8421052632
- TP / TN / FP / FN = 8 / 16 / 3 / 16
- always-UP accuracy = 0.5581395349
- previous-week-sign accuracy = 0.5348837209
- mean P(UP) = 0.4788632325
- P(UP) range = 0.4250140970 .. 0.5739265923

## 4. 2024 fixed validation result

- n = 53
- accuracy = 0.4905660377
- balanced accuracy = 0.4829059829
- Brier score = 0.2669695096
- log loss = 0.7334270464
- actual UP / DOWN = 27 / 26
- forecast UP / DOWN = 48 / 5
- UP sensitivity = 0.8888888889
- DOWN sensitivity = 0.0769230769
- TP / TN / FP / FN = 24 / 2 / 24 / 3
- always-UP accuracy = 0.5094339623
- previous-week-sign accuracy = 0.5094339623
- mean P(UP) = 0.5644972306
- P(UP) range = 0.4477240575 .. 0.8670874066

## 5. Combined pre-2025 result

- n = 96
- accuracy = 0.5208333333
- balanced accuracy = 0.5137254902
- Brier score = 0.2628675144
- log loss = 0.7224324478
- actual UP / DOWN = 51 / 45
- forecast UP / DOWN = 59 / 37
- UP sensitivity = 0.6274509804
- DOWN sensitivity = 0.4000000000
- TP / TN / FP / FN = 32 / 18 / 27 / 19
- always-UP accuracy = 0.5312500000
- previous-week-sign accuracy = 0.5208333333
- mean P(UP) = 0.5261403356
- P(UP) range = 0.4250140970 .. 0.8670874066

## 6. Probability-quality comparison with VLMC-BS

The BCT/CTW posterior-predictive distribution removes the extreme-probability pathology observed in VLMC-BS V1.

VLMC-BS pre-2025:
- 70/96 origins produced exactly P(UP)=0 or P(UP)=1;
- combined Brier = 0.4474896337;
- combined log loss = 10.5618648721.

BCT/CTW pre-2025:
- no origin produced P(UP)=0 or P(UP)=1;
- P(UP) remained within 0.4250..0.8671;
- combined Brier = 0.2628675144;
- combined log loss = 0.7224324478.

This is consistent with the Bayesian parameter smoothing and model averaging built into CTW. It improves probability stability materially, but it does not establish a directional edge.

## 7. Independent implementation verification

The pre-2025 result was reconstructed independently in:
1. a JavaScript implementation operating directly on Neon weekly signs;
2. an independent Python implementation of the same exact CTW recursion.

The first eligible forecast matched:
- target week 2023-03-06;
- P(UP) = 0.4889328551;
- forecast DOWN;
- actual DOWN.

The final pre-2025 forecast matched:
- target week 2024-12-30;
- P(UP) = 0.5469856192;
- forecast UP;
- actual UP.

All aggregate 2023 and 2024 metrics matched to floating-point precision.

The sequential predictive identity
`P(DOWN|history)+P(UP|history)=1`
was also checked from the exact prior-predictive likelihood ratios at every origin.

## 8. Pre-2025 interpretation and lock

BCT/CTW-52 does not establish a robust standalone Gold direction edge before 2025.

Its probability forecasts are substantially better behaved than VLMC-BS, but 2024 validation remains below 50% balanced accuracy and below the always-UP baseline on raw accuracy.

No rescue action is authorized before the BCT V1 2025 historical replay:
- D remains 10;
- beta remains 0.5;
- prior remains Dirichlet(1/2,1/2);
- rolling window remains 52;
- threshold remains 0.5;
- no alternate depth is searched;
- no NO_SIGNAL band is added;
- no existing Gold Control motor is added.

The exact frozen model is carried unchanged into the 2025 historical replay.
