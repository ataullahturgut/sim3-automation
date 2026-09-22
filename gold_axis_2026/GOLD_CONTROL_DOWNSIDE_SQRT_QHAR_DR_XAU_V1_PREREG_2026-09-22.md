# GOLD CONTROL — SOURCE-CONSISTENT SQRT-QLIKE HAR-DR V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `DOWNSIDE_SQRT_QHAR_DR_XAU_V1_RESEARCH`  
**Parent benchmark:** `DOWNSIDE_HAR_DR_XAU_V1_RESEARCH`  
**Failed precursor:** `DOWNSIDE_QHAR_DR_XAU_V1_RESEARCH`  
**External method authority:** Puke & Schweikert (2026), *Coherent Forecasting of Realized Volatility*, plus the authors' public replication code, which applies QLIKE-HAR on a square-root volatility scale.  
**Manifest update:** DEFERRED UNTIL USER REVIEWS RESULTS  
**Runtime authority:** NONE  
**Production writes:** NONE

## 1. Why this is a new identity

Raw-DR QHAR V1 directly minimized QLIKE on downside realized semivariance and failed badly on 2024. A source audit then confirmed that the published qlikeHAR replication applies a square-root transform before QLIKE estimation.

This V1 is therefore a separately preregistered, source-consistent adaptation:
- target = downside realized **semideviation**, `SD_t=sqrt(DR_t)`;
- QLIKE estimation occurs on the SD scale;
- forecasts are squared back to DR for Gold Control downside-risk evaluation.

No 2024/2025 result from raw-QHAR changes the frozen parameters below.

## 2. Data contract

Identical governed source:
`public.xau_intraday_research_cache_5m`.

Daily construction:
- timezone `America/New_York`;
- Monday-Friday only;
- retain a date if it contains at least 240 five-minute closes;
- intraday returns are consecutive within-date log-close differences only;
- no cross-date return inside realized semivariance.

Daily downside realized semivariance:
`DR_t = sum_i r_(t,i)^2 * I(r_(t,i)<=0)`.

Daily downside semideviation:
`SD_t = sqrt(DR_t)`.

## 3. Frozen transformed HAR structure

Source-consistent semideviation regressors:
- daily: `SD_t^d = SD_t`;
- weekly: `SD_t^w = mean(SD_t,...,SD_(t-4))`;
- monthly: `SD_t^m = mean(SD_t,...,SD_(t-21))`.

One-day linear semideviation forecast:
`f_SD(t+1)=c + beta_d*SD_t^d + beta_w*SD_t^w + beta_m*SD_t^m`.

Gold Control DR forecast:
`f_DR(t+1)=f_SD(t+1)^2`.

Formation targets: all eligible targets through 2023-12-31.  
2024: fixed pre-2025 validation.  
2025: locked retrospective challenge, scored only after 2024 evidence is committed.

## 4. Models scored

1. `SQRT_QHAR_DR` — same transformed HAR, coefficients minimize SD-scale QLIKE.
2. `SQRT_OLS_HAR_DR` — identical transformed HAR, coefficients minimize squared error on SD.
3. `RAW_OLS_HAR_DR` — original parent HAR-DR on raw DR, re-estimated on identical formation rows.

No model averaging or selection among them.

## 5. QLIKE estimation

Primary QLIKE objective on semideviation scale, up to target-only constants:
`L(beta)=mean[log(f_SD)+SD/f_SD]`.

Frozen implementation:
- SciPy SLSQP;
- deterministic single start = transformed-HAR OLS coefficients;
- formation-only centering/scaling is a numerical reparameterization only;
- no coefficient sign constraints;
- QLIKE domain constraint only: all formation `f_SD >= 1e-14`;
- max iterations 5000;
- tolerance `1e-12`;
- optimizer failure or any nonpositive validation/challenge SD forecast is fatal;
- no clipping, multistart search, ridge penalty, rolling window or adaptive calibration.

## 6. Frozen formation thresholds

From formation targets only:
- historical-mean DR benchmark = mean formation DR;
- high-risk threshold = empirical nearest-rank 80th percentile of formation DR;
- extreme-negative-return threshold = empirical nearest-rank 5th percentile of formation next-day close return.

The same thresholds apply to all three models.

## 7. Mandatory metrics

For transformed models:
- SD-scale QLIKE;
- SD-scale MSE.

For all models after conversion to DR scale:
- DR QLIKE;
- DR MSE, MAE, OOS R2 vs frozen historical mean;
- correlation;
- forecast mean and realized mean;
- Mincer-Zarnowitz-style calibration intercept/slope;
- high-risk ROC AUC;
- high-risk alert coverage, precision, recall, F1;
- DOWN-day rate conditional on alert versus unconditional;
- extreme-negative-return rate conditional on alert versus unconditional;
- forecast min/median/max.

## 8. Primary 2024 gate

The source-consistent QLIKE hypothesis is supported only if all hold:

1. `SQRT_QHAR_DR` SD-scale QLIKE < `SQRT_OLS_HAR_DR` SD-scale QLIKE;
2. relative SD-QLIKE improvement versus SQRT-OLS >= 2%;
3. squared QHAR forecast DR-QLIKE <= `RAW_OLS_HAR_DR` DR-QLIKE;
4. QHAR high-risk ROC AUC >= 0.55;
5. QHAR alert precision > unconditional 2024 high-risk event rate;
6. all QHAR SD forecasts are positive.

MSE improvement is not required because the intervention targets QLIKE coherence.

## 9. Locked 2025 transport gate

2025 cannot rescue a failed 2024 gate.

If and only if 2024 passes, unchanged 2025 transport is supported when:

1. QHAR SD-QLIKE <= SQRT-OLS SD-QLIKE;
2. squared QHAR DR-QLIKE <= RAW-OLS-HAR-DR DR-QLIKE;
3. QHAR high-risk ROC AUC >= 0.50;
4. QHAR alert precision > unconditional 2025 high-risk event rate;
5. all QHAR SD forecasts remain positive.

## 10. Interpretation lock

Possible conclusions:
- `PRE2025_SOURCE_CONSISTENT_QLIKE_SUPPORTED`
- `PRE2025_SOURCE_CONSISTENT_QLIKE_NOT_SUPPORTED`
- `2025_SOURCE_CONSISTENT_QLIKE_TRANSPORT_SUPPORTED`
- `2025_SOURCE_CONSISTENT_QLIKE_TRANSPORT_NOT_SUPPORTED`.

No CA-HAR-DR, dynamic score state, rolling recalibration, feature expansion, threshold search, window search or 2025-driven rescue is allowed under this identity.
