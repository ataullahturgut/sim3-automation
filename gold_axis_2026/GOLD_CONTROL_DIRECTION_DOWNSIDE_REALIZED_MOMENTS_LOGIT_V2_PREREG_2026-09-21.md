# GOLD CONTROL — DOWNSIDE REALIZED-MOMENTS LOGIT V2 PREREGISTRATION

**Date:** 2026-09-21  
**Identity:** `DIRECTION_DOWNSIDE_REALIZED_MOMENTS_LOGIT_V2_RESEARCH`  
**Parent observation:** `DIRECTION_BONATO_QBOOST_REALIZED_MOMENTS_SPOT_XAU_V1_RESEARCH`  
**Evidence class:** `NEW_PREDECLARED_CROSS_MODEL_FEATURE_CONFIRMATION / LOCKED_RETROSPECTIVE_RESEARCH`  
**Runtime authority:** NONE  
**Production/Neon writes:** NONE

## 1. Scientific question

Bonato QBoost V1 showed that adding same-origin realized variance (RV) and realized skewness (RSK) to a lagged-return baseline materially increased DOWN sensitivity in both 2024 and 2025, even though the full model failed its promotion gate.

This V2 does **not** retune or rescue Bonato V1. It asks a new, narrower question:

> Do same-origin intraday realized variance and realized skewness contain directionally useful, transferable information for next-retained-day DOWN discrimination under a different, deliberately simple model family?

The primary hypothesis is tested with fixed logistic regression rather than quantile boosting. If the effect survives the model-family change, the realized-moment signal is less likely to be an artifact of the Bonato boosting implementation.

## 2. Data contract

Source table: `public.xau_intraday_research_cache_5m`.

Read-only fields:
- `observation_ts`
- `close`

Clock and daily construction are frozen identically to Bonato V1:
- timezone: `America/New_York`;
- Monday-Friday only;
- retain a date only if it contains at least 240 five-minute close observations;
- daily close = final completed 5m close on the retained date;
- intraday returns = consecutive within-date log-close differences only;
- RV = sum of squared within-date intraday log returns;
- RSK = sqrt(M) * sum(r_i^3) / RV^(3/2), with RSK=0 only when RV=0;
- no interpolation, forward fill, cross-date intraday return or alternate-provider substitution.

Predictors at origin t use only information completed by the end of retained date t.

## 3. Target and horizon

Primary horizon is fixed at **h=1 retained trading day** because the parent observation was strongest and most two-sided at h=1.

Target:
`y_t = 1[ log(C_(t+1)/C_t) > 0 ]`.

UP is 1, DOWN is 0.

No h=5 or h=10 scoring is allowed under this identity.

## 4. Fixed predictor representations

All features are available at origin t.

- `lag1_return` = log(C_t/C_(t-1))
- `log_rv` = log(max(RV_t, 1e-12))
- `rsk` = realized skewness at t

Five frozen ablations are scored:

1. `AR1_LOGIT` = lag1_return
2. `RV_LOGIT` = log_rv
3. `RSK_LOGIT` = rsk
4. `RM_LOGIT` = log_rv + rsk
5. `AR1_RM_LOGIT` = lag1_return + log_rv + rsk

`AR1_RM_LOGIT` is the **primary model**. The other four are attribution controls and may not replace the primary after 2025 inspection.

## 5. Fixed model family

At every forecast origin:
- expanding, strictly time-ordered estimation;
- only targets matured by the origin are eligible for training;
- continuous predictors are standardized using training-sample mean and standard deviation at that origin only;
- constant or numerically degenerate predictors are assigned unit scale after centering;
- logistic maximum-likelihood fit by deterministic Newton/IRLS;
- intercept unpenalized;
- L2 penalty = `1e-6` on non-intercept coefficients **only for numerical stabilization**, not tuned;
- maximum iterations = 100;
- convergence tolerance = `1e-10`;
- no class weights;
- no threshold search;
- no random split;
- no hyperparameter search.

Direction:
- UP iff P(UP) >= 0.5;
- DOWN otherwise.

## 6. Chronology

- expanding formation/history begins when at least 250 matured training rows are available;
- 2023 = development/audit only;
- 2024 = fixed pre-2025 validation;
- 2025 = locked retrospective challenge;
- no 2025 outcome may change features, model, penalty, threshold, horizon, chronology, standardization or gate.

## 7. Primary pre-2025 feature-contribution gate

The realized-moment hypothesis is considered **pre-2025 supported** only if `AR1_RM_LOGIT` versus `AR1_LOGIT` on 2024 satisfies all of:

1. DOWN sensitivity improvement >= +0.10 absolute;
2. balanced-accuracy improvement >= +0.02 absolute;
3. balanced accuracy >= 0.52;
4. UP sensitivity >= 0.35;
5. DOWN sensitivity >= 0.35;
6. forecast DOWN share between 10% and 90%.

This is a feature-contribution gate, not a production promotion gate.

## 8. Strong promotion gate

A stronger standalone-direction result requires, on 2024:

- balanced accuracy >= 0.55;
- UP sensitivity >= 0.40;
- DOWN sensitivity >= 0.40;
- raw accuracy strictly above both always-UP and always-DOWN;
- Brier score <= expanding-frequency benchmark Brier.

2025 cannot rescue a failed 2024 gate.

## 9. Mandatory metrics

For every model and period:
- n;
- accuracy;
- balanced accuracy;
- UP sensitivity;
- DOWN sensitivity;
- TP/TN/FP/FN;
- forecast UP/DOWN counts and shares;
- Brier score;
- log loss;
- always-UP / always-DOWN accuracy;
- expanding-frequency Brier benchmark.

For the primary comparison `AR1_RM_LOGIT` vs `AR1_LOGIT` also report:
- delta DOWN sensitivity;
- delta balanced accuracy;
- delta Brier;
- actual-DOWN paired correctness table:
  - both correct;
  - RM-only correct;
  - AR1-only correct;
  - both wrong;
- exact two-sided sign-test p-value on discordant actual-DOWN cases.

The sign test is diagnostic only and does not override the frozen gates.

## 10. Interpretation lock

Possible conclusions are restricted to:

- `PRE2025_FEATURE_SIGNAL_SUPPORTED`
- `PRE2025_FEATURE_SIGNAL_NOT_SUPPORTED`
- `STRONG_DIRECTION_GATE_PASSED`
- `STRONG_DIRECTION_GATE_FAILED`

A positive result means realized moments show cross-model next-day direction information in this governed Spot-XAU dataset. It does not prove exact Bonato-futures replication and does not authorize runtime/trading promotion.

No post-score threshold tuning, nonlinear interaction creation, feature clipping, model-family substitution or 2025-driven rescue is allowed under this identity.
