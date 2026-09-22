# GOLD CONTROL — QLIKE-ESTIMATED HAR-DR V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `DOWNSIDE_QHAR_DR_XAU_V1_RESEARCH`  
**Parent benchmark:** `DOWNSIDE_HAR_DR_XAU_V1_RESEARCH`  
**Research question:** Does loss-consistent QLIKE estimation improve the transportability and calibration of the same HAR-DR downside-risk structure without adding features, regimes, thresholds, or model complexity?  
**Manifest update:** DEFERRED UNTIL USER REVIEWS RESULTS  
**Runtime authority:** NONE  
**Production writes:** NONE

## 1. Scientific hypothesis

The parent HAR-DR uses OLS/MSE estimation but is evaluated as a positive realized-risk forecast where QLIKE is a principal volatility loss. The 2024->2025 parent result preserved strong high-risk discrimination while level calibration weakened.

V1 isolates one methodological change only:

> keep the exact same HAR-DR regressors and linear forecast form, but estimate coefficients by minimizing QLIKE rather than squared error.

No adaptive state, rolling window, new feature, threshold search, class weighting, regime variable, macro variable, or post-2025 recalibration is allowed.

## 2. Data and target contract

Identical to parent HAR-DR:

Source: `public.xau_intraday_research_cache_5m`.

Daily construction:
- timezone `America/New_York`;
- Monday-Friday only;
- retain a date if it contains at least 240 five-minute closes;
- intraday returns are consecutive within-date log-close differences only;
- no cross-date return in realized-semivariance construction.

Daily downside realized semivariance:
`DR_t = sum_i r_(t,i)^2 * I(r_(t,i)<=0)`.

Predictors:
- `DR_t^d = DR_t`;
- `DR_t^w = mean(DR_t,...,DR_(t-4))`;
- `DR_t^m = mean(DR_t,...,DR_(t-21))`.

One-day linear forecast:
`f_(t+1)=c + beta_d*DR_t^d + beta_w*DR_t^w + beta_m*DR_t^m`.

Formation targets: all eligible targets through 2023-12-31.  
2024: fixed pre-2025 validation.  
2025: locked retrospective challenge, run only after 2024 evidence is committed.

## 3. QLIKE estimation

QLIKE objective, up to target-only constants:
`L(beta)=mean[ log(f_t) + DR_t/f_t ]`.

The optimization changes only the estimation loss.

Frozen implementation:
- deterministic SciPy SLSQP;
- initial coefficients = formation OLS solution for the identical HAR-DR design;
- predictors are centered/scaled using formation-only moments purely as a numerical reparameterization; the saved model is converted back to the original linear HAR-DR coefficient scale;
- no coefficient sign constraints;
- QLIKE domain constraint only: every fitted formation forecast must satisfy `f_t >= 1e-14`;
- maximum iterations = 5000;
- tolerance = `1e-12`;
- one deterministic OLS start; no multistart search;
- optimizer failure, nonfinite coefficients, or any nonpositive 2024/2025 forecast is a fatal model failure rather than being clipped or rescued.

Parent OLS HAR-DR is re-estimated inside the same workflow from the identical formation rows for a fair comparator.

## 4. Frozen thresholds and diagnostics

From formation targets only:
- historical-mean DR benchmark = formation mean DR;
- high-risk threshold = empirical nearest-rank 80th percentile of formation target DR;
- extreme-negative-return threshold = empirical nearest-rank 5th percentile of formation next-day close return.

These thresholds are shared identically by OLS HAR-DR and QHAR-DR.

Mandatory metrics for both models:
- MSE, MAE, QLIKE;
- QLIKE versus persistence and frozen historical-mean forecast;
- OOS R2 versus frozen historical mean;
- correlation forecast vs realized DR;
- high-risk ROC AUC;
- alert coverage, precision, recall, F1;
- unconditional vs alert-conditional DOWN-day rate;
- unconditional vs alert-conditional extreme-negative-return rate;
- forecast mean / realized mean;
- Mincer-Zarnowitz-style calibration intercept and slope from realized DR on forecast;
- minimum/median/maximum forecast.

## 5. Primary pre-2025 gate

The QLIKE-estimation hypothesis is considered supported on 2024 only if all hold:

1. QHAR-DR QLIKE is strictly below OLS HAR-DR QLIKE;
2. QHAR-DR QLIKE is strictly below persistence QLIKE;
3. relative QLIKE improvement versus OLS HAR-DR is at least 2%;
4. QHAR-DR high-risk ROC AUC >= 0.55;
5. QHAR-DR high-risk alert precision > 2024 unconditional high-risk event rate;
6. all 2024 QHAR-DR forecasts are positive.

MSE improvement is **not** required because the scientific intervention deliberately changes the loss from MSE to QLIKE.

## 6. Locked 2025 transport gate

2025 cannot rescue a failed 2024 gate.

If and only if the 2024 gate passes, unchanged 2025 transport is supported when:

1. QHAR-DR QLIKE <= OLS HAR-DR QLIKE;
2. QHAR-DR QLIKE < persistence QLIKE;
3. QHAR-DR high-risk ROC AUC >= 0.50;
4. QHAR-DR high-risk alert precision > 2025 unconditional high-risk event rate;
5. all 2025 QHAR-DR forecasts are positive.

MSE/OOS-R2 remain mandatory diagnostics but do not veto QLIKE transport under this QLIKE-targeted identity.

## 7. Interpretation lock

Possible conclusions:
- `PRE2025_QLIKE_ESTIMATION_SUPPORTED`
- `PRE2025_QLIKE_ESTIMATION_NOT_SUPPORTED`
- `2025_QLIKE_TRANSPORT_SUPPORTED`
- `2025_QLIKE_TRANSPORT_NOT_SUPPORTED`

No CA-HAR-DR, dynamic scale state, rolling recalibration, feature expansion, window search, QLIKE/MSE blending, or 2025-driven rescue is permitted under this identity.
