# GOLD CONTROL — BONATO QBOOST REALIZED-MOMENTS SPOT-XAU V1 PREREGISTRATION

**Date:** 2026-09-21  
**Identity:** `DIRECTION_BONATO_QBOOST_REALIZED_MOMENTS_SPOT_XAU_V1_RESEARCH`  
**Primary literature:** Bonato, Demirer, Gupta & Pierdzioch (2018), Resources Policy 57:196-212, DOI 10.1016/j.resourpol.2018.03.004  
**Evidence class:** `SOURCE_CONSTRAINED_SPOT_XAU_ADAPTATION / LOCKED_RETROSPECTIVE_RESEARCH`  
**Runtime authority:** NONE  
**Production/Neon writes:** NONE

## 1. Scientific purpose

Test whether the Bonato et al. quantile-boosting mechanism gains directionally useful information from intraday realized volatility and realized skewness when adapted from gold futures to governed spot XAU/USD intraday close data.

This is **not** an exact gold-futures replication. The source paper uses gold futures and a broader market/sentiment control panel that is not currently complete in Gold Control. No silent futures, VIX, S&P500, oil, exchange-rate, EPU or EMU proxy substitution is allowed.

## 2. Source-faithful elements frozen before 2025

From the primary paper:
- recursively expanding OOS estimation;
- target horizons h in {1,5,10} trading days;
- quantiles alpha = 0.10,0.15,...,0.90;
- check/pinball loss;
- component-wise functional-gradient boosting;
- median response as starting value;
- demeaned estimation data;
- learning-rate / step size v = 0.1;
- choose at each boosting iteration the single predictor that best fits the negative gradient by least squares;
- final iteration m* minimizes quantile loss;
- source stopping rule checks m* <= 0.75*m_break, extends m_break by 10 otherwise, hard maximum m_max=500;
- recursively re-estimate at every forecast origin;
- classical realized variance RV_t = sum_i r_{t,i}^2;
- realized skewness RSK_t = sqrt(M) * sum_i r_{t,i}^3 / RV_t^(3/2).

Primary-source searchable text does not establish the initial value of `m_break` with enough precision. This adaptation freezes `m_break_initial=10` as an explicit reconstruction choice; it is not attributed to the paper.

## 3. Adaptation data contract

Source table: `public.xau_intraday_research_cache_5m`.

Read-only fields:
- `observation_ts`;
- `close`.

Clock:
- timestamps grouped by `America/New_York` calendar date;
- Monday-Friday only;
- day retained only if it contains at least 240 five-minute close observations;
- daily close = final completed 5m close of retained date;
- intraday log returns are consecutive within-date log-close differences.

No forward fill, interpolation or cross-date intraday return is permitted.

## 4. Predictor sets

Because the source control panel is incomplete, this V1 freezes two directly testable source-constrained specifications:

1. `AR1_QBOOST`: lagged one-day spot-XAU log return only.
2. `AR1_RM_QBOOST`: lagged one-day spot-XAU log return + same-origin realized variance + same-origin realized skewness.

The scientific question is incremental realized-moment value over the boosted AR(1) baseline. The broader Bonato controls-with/without-RM horse race remains `BLOCKED_INCOMPLETE_CONTROL_PANEL`.

## 5. Target and leakage contract

At origin date t, predictors use information completed no later than t.

For horizon h, target is the forward spot-XAU log return:
`y_(t,h)=log(C_(t+h)/C_t)`, using the h-th subsequent retained trading date.

2025 target outcomes, realized moments and model errors may not select:
- horizon;
- quantile;
- predictor set;
- boosting step size;
- stopping rule;
- coverage rule;
- direction threshold;
- model family.

## 6. Chronology

- formation/history available from 2020 onward;
- development checkpoint: target dates in 2023;
- fixed pre-2025 validation: target dates in 2024;
- locked retrospective challenge: target dates in 2025;
- no random split.

The model is recursively expanding at every OOS origin.

## 7. Direction mapping and selection

The source is quantile-native rather than a binary classifier.

For project direction scoring:
- primary direction surface = alpha=0.50 conditional-median forecast sign;
- UP iff median forecast > 0; otherwise DOWN.

No quantile or horizon may be selected using 2025.

Pre-2025 promotion gate is evaluated separately at h=1,5,10. A horizon is considered directionally viable only if 2024:
- balanced accuracy >= 0.55;
- UP sensitivity >= 0.40;
- DOWN sensitivity >= 0.40;
- raw accuracy strictly exceeds always-UP and always-DOWN baselines.

No best-horizon cherry-pick from 2025 is permitted.

## 8. Mandatory outputs

For every horizon and model:
- pinball loss for all 17 quantiles;
- median-forecast MAE/RMSE;
- accuracy;
- balanced accuracy;
- UP/DOWN sensitivity;
- TP/TN/FP/FN;
- forecast UP/DOWN counts;
- always-UP, always-DOWN and previous-sign baselines.

Also report whether adding RV/RSK improves median pinball loss and direction metrics relative to AR1_QBOOST.

For h>1, report a non-overlapping-origin direction diagnostic in addition to ordinary origin-by-origin scoring.

## 9. Interpretation lock

A positive result is evidence for this **spot-XAU source-constrained adaptation**, not proof that the exact Bonato gold-futures model was replicated.

A failed 2024 validation may still be replayed unchanged on 2025 for audit completeness, but 2025 cannot rescue the identity.

