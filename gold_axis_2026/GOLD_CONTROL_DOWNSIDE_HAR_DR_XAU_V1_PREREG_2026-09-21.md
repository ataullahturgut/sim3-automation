# GOLD CONTROL — HAR-DR DOWNSIDE REALIZED-SEMIVARIANCE V1 PREREGISTRATION

**Date:** 2026-09-21  
**Identity:** `DOWNSIDE_HAR_DR_XAU_V1_RESEARCH`  
**Primary authority:** Xie, Wang, Chen & Gong (2019), *Forecasting downside risk in China's stock market based on high-frequency data*, DOI 10.1016/j.physa.2018.11.028.  
**Downside-risk authority:** Barndorff-Nielsen, Kinnebrock & Shephard, *Measuring Downside Risk: Realised Semivariance*.  
**Manifest update:** DEFERRED UNTIL USER REVIEWS RESULTS  
**Runtime authority:** NONE  
**Production writes:** NONE

## 1. Scientific target

Forecast next-day **downside realized semivariance (DR)** from heterogeneous daily/weekly/monthly downside-risk components.

This is a downside-risk-intensity model, not a generic direction classifier.

## 2. Data contract

Source: `public.xau_intraday_research_cache_5m`.

Daily construction:
- timezone `America/New_York`;
- weekdays only;
- retain date if >=240 5-minute closes;
- within-date 5m log returns only;
- no cross-date return in realized-semivariance construction.

Daily downside risk:
`DR_t = sum_i r_(t,i)^2 * I(r_(t,i)<=0)`.

## 3. Frozen HAR-DR model

Source-form heterogeneous components:
- daily: `DR_t^d = DR_t`;
- weekly: `DR_t^w = mean(DR_t,...,DR_(t-4))`;
- monthly: `DR_t^m = mean(DR_t,...,DR_(t-21))`.

One-day model:
`DR_(t+1) = c + beta_d*DR_t^d + beta_w*DR_t^w + beta_m*DR_t^m + epsilon_(t+1)`.

Estimation:
- ordinary least squares;
- no regularization;
- no log transform;
- no jumps, leverage, external covariates or nonlinear terms.

Chronology:
- all eligible origins through target date 2023-12-31 = formation;
- 2024 fixed validation;
- 2025 locked retrospective challenge;
- coefficients frozen before 2024 and unchanged in 2025.

## 4. Benchmarks

- formation historical-mean DR forecast;
- persistence forecast `DR_hat_(t+1)=DR_t`.

Mandatory continuous metrics:
- MSE;
- MAE;
- QLIKE with epsilon floor only for numerical safety;
- OOS R2 versus historical-mean benchmark;
- correlation forecast vs realized DR.

## 5. High-downside-risk diagnostic

For interpretability only:
- high-risk target threshold = formation 80th percentile of realized next-day DR;
- high-risk forecast alert = HAR-DR forecast above that same frozen DR threshold.

Report:
- alert coverage;
- high-risk-day recall;
- precision;
- F1;
- ROC AUC using continuous HAR-DR forecast;
- actual DOWN-day rate conditional on alert versus unconditional DOWN-day rate;
- actual extreme-negative-return rate conditional on alert versus unconditional rate, where extreme negative return uses a formation-frozen 5th percentile daily close-return threshold.

Research-interest gate on 2024:
- OOS R2 versus historical mean > 0;
- HAR-DR MSE < persistence MSE;
- high-risk ROC AUC >= 0.55;
- high-risk alert precision > unconditional high-risk event rate.

2025 cannot rescue failed 2024 evidence.

## 6. Interpretation lock

Possible conclusions:
- `PRE2025_DOWNSIDE_RISK_FORECAST_SUPPORTED`
- `PRE2025_DOWNSIDE_RISK_FORECAST_NOT_SUPPORTED`
- `2025_DOWNSIDE_RISK_TRANSPORT_SUPPORTED`
- `2025_DOWNSIDE_RISK_TRANSPORT_NOT_SUPPORTED`.

No manifest change occurs in the workflow.
