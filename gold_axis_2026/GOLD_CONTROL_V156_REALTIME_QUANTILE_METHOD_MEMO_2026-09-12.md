# Gold Control V1.56 — Real-Time Quantile Selective Direction

**Status:** research-only successor; no production authority.  
**Freeze:** contract written before V1.56 2025/2026 scoring.

## Motivation

V1.55 confirmed that conventional rolling classifiers and a simple log-loss DMA do not solve the general H1/H20 direction problem across the visible 2025→2026 regime break. This successor changes the statistical object rather than tuning V1.55: forecast the conditional distribution of the future gold return and issue a direction only when a central predictive interval lies fully on one side of zero.

## Literature basis

- Pierdzioch, Risse & Rohloff, *A real-time quantile-regression approach to forecasting gold returns under asymmetric loss*, Resource Policy 45 (2015), DOI `10.1016/j.resourpol.2015.07.002`: real-time quantile forecasting is proposed specifically for gold returns under model uncertainty and instability.
- Pierdzioch, Risse & Rohloff, *Forecasting gold-price fluctuations: a real-time boosting approach*, Applied Economics Letters 22(1), DOI `10.1080/13504851.2014.925040`: financial and macro predictors contain time-varying out-of-sample information for gold.
- Aye, Gupta, Hammoudeh & Kim (2015), DOI `10.1016/j.irfa.2015.03.010`: gold predictor relevance changes through time and DMA/DMS outperform static alternatives in their setting.
- El-Yaniv & Wiener (2010), JMLR 11:1605–1641: selective classification formalizes abstention/risk-coverage; difficult cases need not be forced into a class.

The V1.56 implementation is an adaptation of these ideas to the existing Gold Control panel. It is not claimed to reproduce any cited paper exactly.

## Frozen method

For both H1 and H20, use the V1.55 FULL information surface and fit rolling/recency-weighted histogram gradient-boosting quantile regressors for q25, q50 and q75. Historical targets may enter a fit only after their forecast horizon has matured.

Three independently estimated quantiles are monotonically rearranged by sorting them at each origin. The primary selective rule is:

- q25 > 0 → UP;
- q75 < 0 → DOWN;
- otherwise → NO_SIGNAL.

Median direction (`sign(q50)`) is a diagnostic sensitivity, not the primary selective claim.

## Why this may help

A point classifier can be highly confident yet wrong when the class prior or regime shifts. A conditional return distribution exposes predictive uncertainty directly. If the interquartile interval crosses zero, Gold Control abstains rather than forcing an UP/DOWN output. This is intended to convert unstable universal direction prediction into a lower-coverage but potentially more reliable specialist lane.

## Evidence limits

2025 and 2026 were already visible in predecessor research. V1.56 scoring on those years is retrospective successor diagnosis only. No promotion claim is permitted without future prospective shadow observations frozen before outcomes occur.

## Governance

`AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`, no production writes, no action/trade mapping, and no post-score threshold/model changes inside V1.56.
