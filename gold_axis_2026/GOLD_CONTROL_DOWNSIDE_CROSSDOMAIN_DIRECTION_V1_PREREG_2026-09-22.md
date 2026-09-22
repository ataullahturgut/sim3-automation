# GOLD CONTROL — CROSS-DOMAIN DOWNSIDE / DIRECTION V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `DOWNSIDE_CROSSDOMAIN_DIRECTION_V1_RESEARCH`  
**Manifest update:** FORBIDDEN; user requested results first  
**Runtime / production authority:** NONE

## 1. Purpose

Test whether transferable methods from biostatistics, medical multi-state modelling, reliability / semi-Markov modelling, and robust estimation can solve two distinct Gold Control problems without feature proliferation:

A. **Direction bridge:** when downside risk is elevated, distinguish next-day DOWN from UP/rebound.  
B. **Risk forecast robustness:** improve next-day downside-risk level without suppressing genuine shocks.

This experiment does not claim pristine confirmation. All historical periods were researcher-visible before this identity was designed.

## 2. Common data

Source: `public.xau_intraday_research_cache_5m`.

- America/New_York;
- weekdays only;
- retain date with >=240 five-minute closes;
- intraday log returns stay within date;
- `DR_t=sum r_i^2 I(r_i<0)`;
- `SD_t=sqrt(DR_t)`;
- daily close = final retained 5m close;
- daily close return `R_t=log(C_t/C_(t-1))`.

A supervised row at origin t predicts retained trading day t+1.

## 3. Chronology

Annual expanding-origin:
- 2022: fit/estimate only on target outcomes completed by 2021-12-31;
- 2023: through 2022-12-31;
- 2024: through 2023-12-31;
- 2025: through 2024-12-31;
- 2026 YTD: through 2025-12-31.

No random split.

Evidence labels:
- 2022-2024 = retrospective development/falsification;
- 2025-2026 = retrospective stress;
- no year is pristine confirmatory evidence for this new cross-domain identity.

## 4. Shared direction features

Exactly four origin-safe continuous features are allowed:

1. `R_t` — current completed-day close return;
2. `log(SD_t)` — current downside-risk level;
3. `log(SD_t / mean5(SD))` — short-run downside-risk acceleration;
4. `log(mean5(SD) / mean22(SD))` — medium-run downside-risk slope.

For logistic models, each feature is standardized using formation mean/std only.

No macro, FAST, GVZ, BOCPD, event data, technical indicators, added lags or post-result feature selection.

Direction target:
`Y_(t+1)=1` iff next retained close return < 0.

Decision threshold:
`P(DOWN)>=0.5`.

## 5. Baseline — STATIC_LOGIT

Ordinary binary logistic regression with intercept and the four frozen features.

Purpose: determine whether a cross-domain dynamic/transition model adds value beyond a fixed-parameter classifier.

L2 penalty is disabled except a tiny numerical ridge `1e-8` in the Hessian.

## 6. Biostatistics — DYNAMIC_LOGIT_D99

State-space / dynamic logistic regression inspired by dynamic binary classification.

Coefficient state:
`beta_t = beta_(t-1) + omega_t`.

Implementation uses a causal Gaussian/EKF approximation with discount factor fixed at:

`delta=0.99`.

At the annual origin:
- beta initialized from STATIC_LOGIT fit;
- covariance initialized from inverse observed information.

Before each next-day forecast, only outcomes already completed are used. After a target outcome is realized, it updates the coefficient state for the next forecast.

No discount-factor grid or model averaging is allowed in V1.

## 7. Medical competing-risks transfer — COMPETING_RISK_MULTINOMIAL

Next-day outcome has three mutually exclusive causes:

0. `UP_OR_FLAT`: next-day return >= 0;
1. `DOWN_NONEXTREME`: next-day return < 0 but above formation Q05;
2. `DOWN_EXTREME`: next-day return <= formation nearest-rank Q05.

A multinomial softmax regression uses the same four standardized features.

Formation-only Q05 is recalculated at each annual origin.

Direction probability:
`P(DOWN)=P(DOWN_NONEXTREME)+P(DOWN_EXTREME)`.

Decision threshold remains 0.5.

The purpose is to test whether separating ordinary and extreme downside as competing outcomes improves the DOWN-vs-rebound bridge.

## 8. Reliability / semi-Markov transfer — EXPLICIT_DURATION_TRANSITION

This is an explicit-duration state-transition model, not a claimed hidden HSMM.

At each annual origin, formation-only SD thresholds define observed risk states:
- LOW: SD < Q50;
- ELEVATED: Q50 <= SD < Q80;
- HIGH: SD >= Q80.

Current return sign defines direction state:
- U: R_t >= 0;
- D: R_t < 0.

State = `{LOW,ELEVATED,HIGH} x {U,D}`.

Duration = consecutive retained days in the same **risk state**, bucketed:
- 1 day;
- 2 days;
- 3+ days.

For each `state x duration-bucket`, estimate:
`P(next-day DOWN)`
with Beta(1,1) smoothing.

Sparse-cell frozen backoff:
- if full cell formation count >=10, use full cell;
- else if risk-state x direction count >=20, use that;
- else if risk-state count >=30, use that;
- else use global formation DOWN rate.

No data-driven state-count, threshold or duration-grid search.

## 9. High-risk bridge evaluation

The existing SQRT-HAR-DR risk model is reconstructed independently at each annual origin:
- OLS on SD target;
- predictors daily SD, mean5 SD, mean22 SD;
- next-day DR forecast = squared SD forecast;
- formation high-risk threshold = nearest-rank Q80 target DR.

A row is a `SQRT_HIGH_RISK_ALERT` if its SQRT-HAR DR forecast >= formation Q80.

This subset directly measures the known false-alarm problem.

For each direction bridge model report on the high-risk subset:
- alert-subset n;
- actual DOWN count;
- model DOWN calls;
- true DOWN hits;
- false DOWN alarms;
- missed DOWNs;
- precision;
- recall;
- specificity;
- balanced accuracy.

Reference rule:
`ALL_HIGH_RISK_AS_DOWN`, i.e. every SQRT high-risk alert is interpreted as DOWN.

This reference reproduces the 2025 45-hit / 45-false-alarm diagnostic when chronology/data align.

## 10. Full direction metrics

Per year and pooled 2022-2024:
- accuracy;
- balanced accuracy;
- ROC AUC;
- Brier;
- log loss;
- DOWN precision;
- DOWN recall;
- DOWN-call rate;
- confusion matrix.

No direction model is successful merely by reducing false alarms if recall collapses.

## 11. Robust-estimation transfer — HUBER_SQRT_HAR

Risk-level model only.

Same transformed HAR as SQRT-HAR-DR:
`SD_(t+1)=b0+bd SD_t+bw mean5(SD)+bm mean22(SD)+e`.

Estimate coefficients with Huber loss:
- epsilon = 1.35 fixed;
- L2 regularization alpha = 0;
- formation-only feature scaling;
- no hyperparameter search.

Final DR forecast = squared positive SD forecast.

Compare to ordinary SQRT-HAR on:
- MSE;
- MAE;
- DR-QLIKE;
- OOS R2;
- calibration slope/error;
- high-risk AUC/precision/recall.

This is a robust-estimation test; it is NOT labelled exact H-infinity filtering.

## 12. Retrospective decision rules

### Direction bridge
A bridge method is `RETROSPECTIVE_DIRECTION_BRIDGE_SUPPORTED` only if on pooled 2022-2024:
1. full-sample balanced accuracy > 0.52;
2. full-sample AUC > 0.55;
3. on SQRT high-risk alerts, false DOWN alarms are lower than ALL_HIGH_RISK_AS_DOWN;
4. high-risk DOWN recall remains >=70% of the reference recall;
5. at least 2 of 3 annual high-risk subsets do not have lower balanced accuracy than the reference.

### Robust Huber risk model
`RETROSPECTIVE_ROBUST_RISK_SUPPORTED` only if:
1. MSE beats SQRT-HAR in >=2 of 3 years;
2. pooled MSE < SQRT-HAR;
3. pooled QLIKE <= SQRT-HAR;
4. calibration error improves in >=2 of 3 years;
5. AUC never degrades by >0.02.

No post-result tuning or alternate threshold is permitted under V1.
