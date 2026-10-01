# GOLD MONTHLY — Contextual Relative-Loss / Rescue-Gain Predictor V1 Authority

**Date:** 2026-10-01  
**Status:** PREDICTOR AUTHORITY / DEV-ONLY / NO PRODUCTION SWITCH

## 1. Research question
When frozen Specialist Hedge warns, can origin-known context predict whether ChHHO should be kept, blended with, or replaced by one of the frozen Exact16 challengers?

The predictor does **not** refit the gold-price target. It predicts relative rescue gain only.

## 2. Frozen outcome
For challenger j and target month t:

`gain(j,t) = |error_ChHHO,t| - |error_j,t|`

For statistical stability the fitted target is:

`scaled_gain(j,t) = gain(j,t) / |ChHHO_forecast_t|`

This denominator is known at origin. Reported gains are converted back to USD for evaluation.

## 3. Frozen model universe
Main:
- ChHHO_ANFIS

Challengers:
- exact frozen 15 alternatives from the Stage-1 Exact16 matrix.

No challenger may be added or removed after predictor results are seen.

## 4. Selection authority and chronology
- Authority: DEV targets 2022-04..2024-12 only.
- First 8 DEV targets are warm-up.
- Evaluation is expanding-origin, one target month at a time, from 2022-12..2024-12.
- The selector is evaluated operationally only when the frozen Specialist Hedge warns.
- All earlier DEV targets may be used to fit gain functions at each origin.
- 2025/2026 must not choose features, model class, alpha, confidence threshold, challenger, or policy.

## 5. Origin-known feature sets

CORE numeric context:
- p_HIGH
- p_ELEVATED
- semantic regime confidence
- Exact16 direction agreement
- Exact16 dispersion
- ChHHO absolute gap from Exact16 median
- ChHHO IQR distance
- ChHHO forecast percentile
- active-signal count
- awake-expert count

STATE adds one-hot origin-known categories:
- semantic regime label R0/R1/R2/BELIRSIZ
- NORMAL/EXTREME/TRANSITION/DEFER state category
- transition V2 status
- extreme status
- OOD flag

Realized severity, target-month actual, ChHHO realized error, best challenger, and any future information are forbidden features.

## 6. Pre-registered predictor candidates

All context models are multi-output Ridge regressions predicting the 15 scaled challenger gains jointly.

Candidates:
1. EXPANDING_MEAN — past mean scaled gain per challenger, no context.
2. RIDGE_CORE_A1
3. RIDGE_CORE_A10
4. RIDGE_CORE_A100
5. RIDGE_STATE_A1
6. RIDGE_STATE_A10
7. RIDGE_STATE_A100

Continuous features are standardized using training history only. Ridge intercept is enabled.

## 7. Pre-registered action policies

For every warning origin, a predictor supplies the challenger with largest predicted gain.

Three execution policies are evaluated without changing the predictor:

- **DIRECT_SWITCH:** switch when top predicted gain > 0; otherwise KEEP.
- **CONSERVATIVE_SWITCH:** estimate the selected challenger's training residual RMSE; switch only when predicted gain exceeds 0.5 × residual RMSE in USD-equivalent terms; if predicted gain is positive but below this bound, ABSTAIN (operationally KEEP).
- **CONSERVATIVE_BLEND:** same confidence gate; above the gate SWITCH, between 0 and the gate use a fixed 50/50 ChHHO-challenger blend, otherwise KEEP.

ABSTAIN is scored operationally as KEEP MAIN. Blend weight 50/50 is frozen and is not tuned.

## 8. Primary evaluation
On chronologically evaluated DEV warning targets:
- action-policy cumulative AE;
- gain versus KEEP ChHHO;
- number of beneficial and harmful non-KEEP actions;
- action coverage;
- worst incremental harm;
- oracle headroom for context only.

Baselines:
- KEEP MAIN;
- best fixed challenger diagnostics from Stage 1 (not operationally selectable by hindsight).

## 9. Scientific gate
A candidate may be named the DEV research leader only if its chronological warning-month cumulative AE is lower than KEEP MAIN.

No V1 result authorizes production switching. Even a positive DEV result must next be transported to already-opened 2025/2026 without retuning and must retain KEEP/ABSTAIN as valid actions.
