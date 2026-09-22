# GOLD CONTROL — HIGH-RISK HURDLE RESOLUTION V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `HIGH_RISK_HURDLE_RESOLUTION_V1_RESEARCH`  
**Parent risk motor:** frozen `DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_RESEARCH` / SQRT-HAR-DR  
**Trigger:** frozen SQRT high-risk alarm only  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Motivation

The semantic audit showed that a next-day UP close does not imply failure of the SQRT downside-risk sensor. Across 2020–2024, 103 of 143 UP-close SQRT alarms were nevertheless realized high-risk hits under the same frozen annual Q80 risk boundary.

Therefore the next research problem is not "which SQRT alarms should be deleted?" It is:

> Given that SQRT has issued a high-risk alarm, can we causally distinguish whether the target day will be a realized high-risk DOWN-close event, a realized high-risk UP-close event, or a realized-risk miss?

This V1 uses a two-stage hurdle architecture so that risk realization and direction conditional on risk realization are modeled separately.

## 2. Frozen target semantics

For each evaluation year Y, use the already-frozen annual Q80 downside-RV threshold.

For any target row:

- `RISK_HIT = 1` iff `target_dr >= Q80_Y`.
- If `RISK_HIT = 1`, conditional direction is:
  - `DOWN` iff target close-to-close log return < 0;
  - `UP` iff target close-to-close log return > 0.

Three joint outcome classes:

1. `HIT_DOWN`
2. `HIT_UP`
3. `MISS` = realized target DR < Q80, regardless of close direction.

Flat target returns are not expected; any flat evaluated alarm is an integrity error.

The model is scored only on frozen SQRT alarm rows for the evaluation year.

## 3. Frozen two-stage hurdle model

For each evaluation year Y:

### Stage A — risk realization

Fit a binary L2 logistic regression on all matured formation rows whose target date is <= 31 December Y-1:

`RISK_HIT ~ origin-side features`

Target:
- 1 if target DR >= Q80_Y
- 0 otherwise.

### Stage B — direction conditional on realized high risk

Fit a second binary L2 logistic regression using only matured formation rows with `RISK_HIT=1`:

`DOWN | RISK_HIT ~ same origin-side features`

Target:
- 1 for DOWN close
- 0 for UP close.

No Router output or legacy expert vote enters V1. The purpose of V1 is to test whether the conditional-resolution structure is learnable from risk-state geometry itself before adding directional experts.

## 4. Frozen origin-side features

Exactly seven features are allowed. All are known by the forecast origin.

1. `log_dr_d_q80 = log((DR_d + eps)/(Q80 + eps))`
2. `log_dr_w_q80 = log((mean DR over latest 5 completed days + eps)/(Q80 + eps))`
3. `log_dr_m_q80 = log((mean DR over latest 22 completed days + eps)/(Q80 + eps))`
4. `log_rv_d_q80 = log((RV_d + eps)/(Q80 + eps))`
5. `rsk_d` = frozen realized-skewness construction already used in the project
6. `origin_return_1d = log(close_d / close_{d-1})`
7. `recent20_high_share` = fraction of latest 20 completed days ending at origin d with DR >= Q80_Y

`eps = 1e-12`.

No target-day feature, Router result, future close, future intraday path, 2025 value, or 2026 value is allowed.

## 5. Frozen preprocessing and estimators

For each evaluation year independently:

- compute feature mean and standard deviation on Stage-A formation rows only;
- z-standardize all seven features using those formation statistics;
- standard deviation <= 1e-12 is replaced by 1.0;
- Stage A estimator: scikit-learn `LogisticRegression`, L2 penalty, `C=1.0`, `solver="lbfgs"`, `max_iter=2000`, no class weighting;
- Stage B estimator: same fixed specification;
- no hyperparameter search;
- no calibration fit;
- no random split.

The same Stage-A normalization is used for Stage B and the evaluation year.

## 6. Frozen joint probability construction

For a scored SQRT alarm row:

- `p_hit = P(RISK_HIT=1)` from Stage A;
- `p_down_given_hit = P(DOWN | RISK_HIT)` from Stage B;
- `P(HIT_DOWN) = p_hit * p_down_given_hit`;
- `P(HIT_UP) = p_hit * (1 - p_down_given_hit)`;
- `P(MISS) = 1 - p_hit`.

These three probabilities sum to 1 up to numerical tolerance.

## 7. Frozen selective decision rule

Let `p_max` be the largest of the three joint probabilities.

- if `p_max > 0.50`, emit the corresponding class;
- otherwise emit `UNCERTAIN`.

The 0.50 threshold is not tuned: it means one joint outcome is estimated to be more likely than the other two outcomes combined.

No margin threshold, per-class threshold, or year-specific confidence threshold is allowed.

## 8. Evaluation years and chronology

Score:
- 2020 using only formation targets <= 2019-12-31;
- 2021 using only formation targets <= 2020-12-31;
- 2022 using only formation targets <= 2021-12-31;
- 2023 using only formation targets <= 2022-12-31;
- 2024 using only formation targets <= 2023-12-31.

Data authority:
- 2018–2021 corrected external 276-bar session-masked spine: research only;
- 2022–2024 governed source;
- governed DB read-only.

2025 and 2026 are excluded entirely from model definition, fitting, threshold selection and scoring.

## 9. Integrity gate

The evaluation set must reproduce the frozen SQRT alarm counts exactly:

- 2020=212
- 2021=28
- 2022=11
- 2023=2
- 2024=17
- pooled=270

The three-class observed alarm anatomy must reproduce the semantic audit exactly:

- `HIT_DOWN=115`
- `HIT_UP=103`
- `MISS=52`

Any mismatch => `BLOCKED_INTEGRITY_MISMATCH`.

## 10. Required metrics

Report by year and pooled:

- alarm count;
- observed HIT_DOWN / HIT_UP / MISS counts;
- emitted HIT_DOWN / HIT_UP / MISS / UNCERTAIN counts;
- selective coverage;
- selective accuracy among emitted rows;
- non-selective argmax accuracy;
- per-class precision and recall among all scored alarm rows, treating abstention as no prediction;
- confusion matrix for emitted classes;
- Brier score for the three joint probabilities;
- multiclass log loss;
- mean max probability;
- class probability calibration summaries by observed class.

Also report the conditional binary direction diagnostic on rows that actually realize high risk:
- AUC of `p_down_given_hit` where defined;
- accuracy of `p_down_given_hit >= 0.5` on realized-risk-hit alarm rows.

These are diagnostics only; they do not alter the frozen three-class decision rule.

## 11. Decision semantics

This V1 is an architecture probe, not a promotion gate.

Possible statuses:

- `BLOCKED_INTEGRITY_MISMATCH`
- `NO_SELECTIVE_SIGNAL`: selective coverage=0 or selective accuracy <= largest observed class share among alarm rows
- `SELECTIVE_SIGNAL_PRESENT_NOT_CERTIFIED`: selective coverage >0 and selective accuracy exceeds the largest observed class share among alarm rows
- `DEGENERATE_CLASS_FIT`: either logistic stage lacks both classes in a required formation sample

No result authorizes runtime promotion.

## 12. Next-step rule

If V1 shows selective signal, freeze it and only then test whether adding Router/context information improves conditional resolution under a new preregistered identity.

If V1 shows no selective signal, do not tune C, confidence threshold, feature list, class weights or lookback under V1. The next lane should move to a different model family such as regime-state / hidden-state, survival/competing-risk, or conformal/selective classification with a new identity.

