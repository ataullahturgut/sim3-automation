# GOLD CONTROL — DIRECTION_COVLMC_X3_V1_RESEARCH PREREGISTRATION

**Date:** 2026-09-18  
**Identity:** `DIRECTION_COVLMC_X3_V1_RESEARCH`  
**Parent:** `DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH`  
**Status:** `FROZEN_BEFORE_COVLMC_REPLAY`  
**Evidence class:** historical research only; no runtime or production authority

## 1. Scientific motivation

The corrected VLMC-BS family contains two-sided signal but does not generalize stably across 2024 and 2025. Fixed-Share window adaptation also failed in 2025.

Zambom, Kim & Garcia (2022) extend VLMC so that next-state transition probabilities depend jointly on the variable-length state context and exogenous covariates through a generalized/logistic regression. Their empirical application predicts Hang Seng gains/losses from its own state history plus external market indices.

This successor tests that direct model-class extension for Gold rather than another voting or window-rescue layer.

## 2. Reference implementation

Pinned reference package:
- R 4.4.1;
- CRAN `VLMCX` version 1.0;
- function `VLMCX::VLMCX`.

Package-default structural parameters are frozen:
- `alpha.level = 0.05`;
- `max.depth = 5`;
- `n.min = 5`;
- `trace = FALSE`.

No package parameter is selected from 2024 or 2025.

## 3. Gold state target

Target sequence is unchanged from corrected VLMC-BS V2:
- daily simple XAU percentage returns;
- sum within Monday-start calendar week;
- `y_w = 1` iff summed weekly return > 0, else 0;
- forecast next represented weekly sign.

## 4. Exogenous covariates

Exactly three covariates are frozen from literature/domain reasoning before the COVLMC replay:

1. `DGS10_ALFRED_PIT_ME` — U.S. 10-year Treasury yield, latest approved value whose `available_as_of` is no later than forecast origin;
2. `DEXCHUS_ALFRED_PIT_ME` — USD/CNY exchange rate, same PIT rule;
3. `GPR_OFFICIAL_GIT_PIT` — geopolitical risk index, latest approved vintage whose `available_as_of` is no later than forecast origin.

The historical panel is:
`gold_axis_2026/research_inputs/XAU_COVLMC_PIT_X3_WEEKLY_2022_2025.csv`.

All 200 governed weeks from 2022-03-07 through 2025-12-29 contain all three covariates.

No GVZ, FAST, BOCPD or other Gold Control runtime context is used because a governed historical point-in-time weekly panel is not available for those states.

## 5. Window and scaling

Rolling estimation window is exactly **104 weeks**.

Reason frozen before replay:
- COVLMC estimates context-specific regression coefficients in addition to the context tree;
- 26/52-week samples are too small relative to the three-covariate parameter burden;
- 104 weeks is the longest same-source window that yields meaningful pre-2025 OOS evidence.

At each origin:
- use exactly the prior 104 y/X observations;
- standardize each covariate using mean and standard deviation computed only inside that 104-week training window;
- no target-week covariate is used;
- prediction uses only state/covariate history through the origin week.

If a training-window covariate standard deviation is zero, fail closed.

## 6. Rolling fit and prediction

For every target week:
1. build `train_y` and `train_X` from the prior 104 weeks;
2. standardize `train_X` origin-safely;
3. fit:
   `VLMCX(train_y, train_X_scaled, alpha.level=0.05, max.depth=5, n.min=5, trace=FALSE)`;
4. obtain the next-state probability vector using `predict(fit)`, which uses the fitted original y/X history;
5. define `P(UP)` as the probability corresponding to state 1;
6. forecast UP iff `P(UP) >= 0.5`, else DOWN.

Any fit/prediction failure is persisted and fails the governed replay; no fallback model is substituted.

## 7. Chronology and evidence interpretation

Primary pre-2025 evaluation:
- 2024 OOS targets after 104-week warm-up;
- compare directly with corrected VLMC-BS-104 on identical target support.

2025:
- run unchanged only after the 2024 forecast/result table is committed;
- because the broader research program had already inspected 2025 before this successor was conceived, this is labeled `POST_DIAGNOSTIC_2025_HISTORICAL_REPLAY`, not a pristine untouched holdout;
- 2025 cannot tune or rescue COVLMC.

Event overlay may be applied only after the complete COVLMC 2025 weekly forecast table is frozen.

## 8. Required metrics

- accuracy;
- balanced accuracy;
- Brier score;
- log loss;
- UP/DOWN sensitivity;
- confusion counts;
- forecast class distribution;
- always-UP and previous-sign baselines;
- direct delta versus corrected VLMC-BS-104 on identical support.

## 9. Forbidden

- changing covariate set after seeing results;
- adding/removing covariates based on 2025;
- tuning alpha.level/max.depth/n.min from 2024 or 2025;
- threshold changes;
- smoothing/calibration rescue;
- NO_SIGNAL band;
- provider substitution;
- event-conditioned tuning;
- adding Fixed-Share or any other ensemble layer under this identity.
