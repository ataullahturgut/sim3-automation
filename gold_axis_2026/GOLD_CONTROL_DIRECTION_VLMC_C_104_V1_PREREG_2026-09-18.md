# GOLD CONTROL — DIRECTION_VLMC_C_104_V1_RESEARCH PREREGISTRATION

**Date:** 2026-09-18  
**Identity:** `DIRECTION_VLMC_C_104_V1_RESEARCH`  
**Parent:** `DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH`  
**Status:** `FROZEN_BEFORE_VLMC_C_REPLAY`  
**Evidence class:** historical research only; no runtime or production authority

## 1. Motivation

An et al. (2022) show that the original Bühlmann-Wyner context-tree pruning statistic can be systematically biased because overlapping word counts are dependent. Their VLMC-Consistent (VLMC-C) replaces the common fixed chi-square pruning threshold with a branch-specific mixed-chi-square asymptotic distribution and controls family-wise error across tree layers.

This successor tests whether that adaptive pruning improves Gold weekly direction stability without adding exogenous variables or voting layers.

## 2. Input and target

Use the corrected source-faithful weekly sign series from:
`XAU_WEEKLY_SIGN_SOURCE_METHOD_V2_2022_2025.csv`.

- y=1 iff source weekly summed daily simple return > 0;
- y=0 otherwise;
- target = next represented weekly sign.

No other input feature is used.

## 3. Window

Rolling window exactly 104 prior weekly signs.

Reason:
- it is the longest same-source window with pre-2025 OOS evidence;
- VLMC-C's branch-specific asymptotic tests require more observations than the shorter 26/52-week windows;
- window choice is frozen before VLMC-C results.

## 4. VLMC-C tree construction and pruning

Implementation follows the published algorithm and the authors' public reference code semantics for binary alphabet X={0,1}.

For n=104 and |X|=2:

`THRESHOLD.GEN = max(2, round(sqrt(n)/|X|)) = 5`.

Initial tree:
- include every observed context string with occurrence count >= THRESHOLD.GEN;
- extend by prepending older symbols until no longer contexts meet the threshold.

Pruning:
- process currently untested leaves from greatest depth toward root;
- base family-wise significance `alpha0=0.05`;
- at each layer use authors' reference-code quantile level
  `q = 1 - alpha0/(current_leaf_count * initial_max_depth)`;
- for branch `uw -> w`, compute the authors' Pearson-type Delta statistic and plug-in covariance matrix from overlapping word counts;
- use eigenvalues of that covariance matrix to define the branch-specific mixed-chi-square null distribution;
- approximate the q quantile with exactly 100000 Gaussian Monte Carlo draws;
- R `set.seed(1)` independently for every branch test, matching the public reference function;
- prune iff Delta < branch-specific cutoff;
- if N(uw)=N(w), prune directly as in the reference code.

## 5. Prediction

After pruning:
- find the longest terminal context matching the suffix of the current 104-sign history;
- estimate P(UP) empirically from transitions following that context inside the training window;
- if no non-root terminal context matches, use the root unconditional UP frequency;
- UP iff P(UP)>=0.5, otherwise DOWN.

No probability smoothing is added.

## 6. Chronology

Pre-2025 primary validation:
- all eligible 2024 target weeks after 104-week warm-up;
- compare directly to corrected VLMC-BS-104 on identical support.

Persist/freeze the complete pre-2025 table before any VLMC-C 2025 execution.

2025:
- unchanged post-diagnostic historical replay only;
- not a pristine untouched holdout because 2025 had already been inspected in the wider research program before this successor was designed;
- no 2025 tuning or rescue.

Event overlay only after 2025 weekly forecasts are frozen.

## 7. Required metrics

Accuracy, balanced accuracy, Brier, log loss, UP/DOWN sensitivity, confusion counts, class distribution, always-UP and previous-sign baselines, and deltas versus corrected VLMC-BS-104.

Also persist tree diagnostics:
- initial/final maximum depth;
- initial/final leaf counts;
- active context and support.

## 8. Forbidden

- changing alpha0, threshold generation, simulation count, seed, window or decision threshold after results;
- adding exogenous covariates;
- adding smoothing or NO_SIGNAL;
- using 2025 to select or tune VLMC-C;
- event-conditioned tuning;
- ensemble rescue under this identity.
