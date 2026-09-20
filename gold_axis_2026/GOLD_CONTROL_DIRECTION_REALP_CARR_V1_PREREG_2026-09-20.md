# GOLD CONTROL — DIRECTION_REALP_CARR_V1_RESEARCH PREREGISTRATION

**Date:** 2026-09-20  
**Identity:** `DIRECTION_REALP_CARR_V1_RESEARCH`  
**Research lineage:** final Realized-Probability successor to the B-CARS direction family  
**Status:** `FROZEN_BEFORE_ANY_GOLD_REALP_RESULT`  
**Evidence class:** historical research replay only; no runtime or production authority

## 1. Authority boundary

A 2022 Academy of Mathematics and Systems Science seminar by Haibin Xie describes a **Conditional AutoRegressive Beta-distribution (CARB)** model for realized-probability direction forecasting and reports better in- and out-of-sample direction forecasts than dynamic probit. However, the exact CARB recursion, likelihood, initialization and reproducible implementation were not found in a primary source available to this project.

Therefore:

`CARB_EXACT_SPECIFICATION = NOT_PROVEN / DO_NOT_IMPLEMENT_BY_GUESSING`.

This experiment does **not** claim to implement CARB.

Instead it implements the source-verifiable Realized Probability construction and the published empirical forecasting mechanism in Xie, Wu, Sun & Wang, *Realized Probability Index is a Better Market Timing Indicator*, Studies in Nonlinear Dynamics & Econometrics, DOI 10.1515/snde-2024-0060:

1. construct Realized Probability from intraperiod log-price changes;
2. construct cumulative absolute return (CAR);
3. filter next-period expected CAR with the asymmetric CARR specification used in the paper;
4. regress Realized Probability on the filtered expected CAR;
5. forecast direction UP iff the predicted conditional Realized Probability exceeds 0.5.

This is a **weekly Gold adaptation** of the paper's daily-to-monthly empirical design, not an exact frequency replication.

## 2. Source-faithful Realized Probability construction

Provider:
- Twelve Data;
- symbol `XAU/USD`;
- interval `1h`;
- timezone `America/New_York`.

Weekly anchor semantics are inherited from the governed B-CARS OHLC lane:
- Monday-start calendar week;
- candidate weekly close = exact provider 16:00 New York 1h close on Monday-Friday;
- weekly close = last actually observed eligible 16:00 candidate in that week;
- no interpolation, no forward-fill, no provider substitution.

For consecutive weekly close anchors `T_(t-1)` and `T_t`, let `p_i=log(C_i)` for the previous anchor and every validated hourly close with
`T_(t-1) < timestamp_i <= T_t`.

Intraperiod log returns:
`r_i = p_i - p_(i-1)`.

Define:
- `CPR_t = sum_{r_i>0} r_i`;
- `CNR_t = sum_{r_i<0} r_i` (non-positive);
- `CAR_t = CPR_t - CNR_t = sum_i |r_i|`;
- `RealP_t = CPR_t / CAR_t`.

Identity audit:
`sum_i r_i = CAR_t * (2*RealP_t - 1)`.

Thus:
`weekly_return_t > 0 <=> RealP_t > 0.5`,
apart from an exact zero-return tie, which is classified DOWN under the existing direction convention.

No boundary transformation is required merely to construct RealP. RealP values of exactly 0 or 1 are retained as genuine data.

## 3. Forecast model

The source empirical specification uses:

`CAR_(t+1) = lambda_(t+1) * z_(t+1)`

`lambda_(t+1) = omega + a*lambda_t + b*CAR_t + g*CAR_t*I(r_t<0)`

where `z` has positive support and unit mean. The paper estimates the CARR equation by QMLE with exponential density.

For a training sample, the exponential QMLE objective is:

`NLL = sum_t [log(lambda_t) + CAR_t/lambda_t]`.

Gold implementation choices frozen before scoring:
- `omega > 0`;
- `a,b,g >= 0`;
- `a+b+g < 1`;
- first conditional mean `lambda_1 = mean(CAR)` of the current training sample;
- deterministic L-BFGS-B optimizer;
- fixed five-start initialization set;
- if no start converges to a finite admissible solution, origin is fail-closed.

After CARR fitting, estimate by OLS on the same training sample:

`RealP_t = theta + psi*lambda_t + e_t`.

The one-step forecast is:

`lambda_(t+1|t) = omega + a*lambda_t + b*CAR_t + g*CAR_t*I(r_t<0)`

`RealP_hat_(t+1|t) = theta + psi*lambda_(t+1|t)`.

No clipping to [0,1] is permitted. Clipping would be a post-model intervention not specified by the source empirical regression.

Native direction rule:
- UP iff `RealP_hat > 0.5`;
- DOWN otherwise.

## 4. Chronology

Weekly RealP sample begins only after a valid previous weekly 16:00 anchor exists.

Initial estimation window:
- first 52 valid weekly RealP/CAR observations.

Expanding one-step chronology:
- 2023 = development/audit;
- 2024 = fixed pre-2025 validation;
- complete 2024 result must be frozen before 2025 replay;
- 2025 = unchanged post-diagnostic historical replay;
- no 2025 outcome may alter any model rule.

No random split.

## 5. Baselines and required metrics

Direction:
- accuracy;
- balanced accuracy;
- UP sensitivity;
- DOWN sensitivity;
- TP/TN/FP/FN;
- forecast UP/DOWN counts;
- always-UP accuracy;
- previous-week-sign accuracy;
- historical-mean-RealP direction accuracy;
- previous-RealP direction accuracy.

Continuous RealP:
- MSE of `RealP_hat`;
- expanding historical-mean RealP MSE;
- `R2_oos = 1 - SSE_model/SSE_historical_mean`;
- forecast range.

CARR diagnostics:
- convergence count;
- parameter paths;
- lambda forecast range;
- OLS `psi` path/range.

## 6. Pre-registered decision gate

The RealP-CARR successor passes fixed 2024 validation only if all conditions hold:

1. balanced accuracy >= 0.55;
2. UP sensitivity >= 0.40;
3. DOWN sensitivity >= 0.40;
4. raw accuracy is strictly greater than always-UP;
5. raw accuracy is strictly greater than previous-week-sign;
6. continuous RealP `R2_oos > 0`.

If any condition fails:
- `NO_PROMOTION / PRE2025_VALIDATION_FAILED`;
- 2025 remains diagnostic only and cannot rescue the model;
- the B-CARS / Realized-Probability direction family closes for the current research sequence unless explicitly reopened by the user.

## 7. Forbidden

- inventing or labeling this model as CARB;
- reconstructing an unverified CARB likelihood or recursion;
- changing frequency after outcomes;
- changing the 52-week initial window after outcomes;
- threshold tuning;
- NO_SIGNAL band;
- alternate CARR orders;
- alternative error distributions;
- adding exogenous variables;
- FAST/GVZ/BOCPD/Macro/Emergency inputs;
- event-conditioned training or origin selection;
- parameter/grid rescue based on 2024 or 2025;
- production/Neon writes.

Any such change requires a separately named preregistered identity and explicit user reopening.
