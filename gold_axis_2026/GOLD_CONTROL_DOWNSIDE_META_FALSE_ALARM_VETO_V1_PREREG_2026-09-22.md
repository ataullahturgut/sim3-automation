# GOLD CONTROL — META FALSE-ALARM VETO V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `DOWNSIDE_META_FALSE_ALARM_VETO_V1_RESEARCH`  
**Primary model:** frozen annual-origin `SQRT_HAR_DR` forecasts from `DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_RESEARCH`  
**Manifest update:** FORBIDDEN in this experiment  
**Runtime / production authority:** NONE

## 1. Question

Can a second-stage meta-model reduce false DOWN interpretations of SQRT-HAR-DR high-risk alarms while retaining most true DOWN outcomes?

The primary model is NOT changed. The meta-model only evaluates whether an already-issued primary high-risk alarm should be:

- `CONFIRM`
- `VETO`

The meta target is therefore primary-alarm correctness with respect to next-day close direction:

`meta_y=1` if next retained trading-day close return < 0, else `meta_y=0`.

This is a false-alarm filtering problem, not a replacement direction model.

## 2. Primary alarm authority

Use the frozen parent forecast surface:

`gold_axis_2026/GOLD_CONTROL_DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_FORECASTS_2026-09-22.csv`

No SQRT-HAR refit or redefinition is permitted in this V1.

A primary alarm is exactly:

`sqrt_high_risk_alert == 1`.

The reference decision is:

`ALL_PRIMARY_ALARMS_AS_DOWN`.

## 3. Meta-training pools

Two frozen variants are tested.

### STRICT_META
Training rows are only historical origin-safe rows where:

`sqrt_high_risk_alert == 1`.

### CONTEXT_META
Because the strict pre-2025 alarm sample is small, a second prespecified training pool uses elevated-risk contexts:

`sqrt_normalized_risk_score >= 0.80`.

The model is still evaluated ONLY on actual primary alarms (`sqrt_high_risk_alert==1`).

The 0.80 context boundary is frozen before scoring and may not be altered after results.

## 4. Frozen meta-features

Exactly five origin-safe features:

1. `log_risk_margin = log(sqrt_normalized_risk_score)`;
2. `representation_disagreement = log(sqrt_har_dr_forecast / raw_har_dr_forecast)`;
3. `origin_close_return` = close-to-close return ending at the completed origin date;
4. `signed_semivariance_imbalance = (RSminus - RSplus)/(RSminus + RSplus)`, from within-origin-date 5m returns only;
5. `risk_acceleration = log(sd_d / sd_w)`.

No macro, options, futures, DXY, yields, FAST, GVZ, BOCPD, event labels, future observations or extra feature search.

## 5. Meta-model

Ridge logistic regression:

- standardized features using training mean/std only;
- L2 penalty;
- `C=1.0`;
- intercept included;
- no class weighting;
- solver L-BFGS;
- no hyperparameter search.

Output:

`p_meta = P(primary alarm is followed by DOWN)`.

## 6. Veto rules

Two fixed decision variants are reported for each training pool.

### P050
`CONFIRM` if `p_meta >= 0.50`; otherwise `VETO`.

### RECALL75
Threshold is selected using ONLY the historical training pool by leave-one-out cross-fitted probabilities.

Among candidate thresholds equal to unique cross-fitted probabilities plus 0 and 1:
- retain only thresholds with training cross-fitted DOWN recall >=0.75;
- choose the threshold with maximum precision;
- tie-break by higher balanced accuracy;
- final tie-break by higher threshold.

Then refit the logistic model on the full historical training pool and apply that frozen threshold to the next target year.

If cross-fitted prediction is impossible because a leave-one-out fold has only one class, RECALL75 is `NOT_PROVEN` for that origin.

## 7. Chronology

Evaluation years:
- 2024: meta-training uses only parent rows with target outcomes through 2023-12-31;
- 2025: meta-training uses only outcomes through 2024-12-31;
- 2026 YTD: meta-training uses only outcomes through 2025-12-31.

2024 is the only pre-2025 chronological evaluation available for the meta-veto identity. It is small-sample retrospective falsification, not pristine blind evidence.

2025 and 2026 are retrospective stress only and MUST NOT be used to tune features, context boundary, regularization or thresholds.

No random split.

## 8. Mandatory outputs

For each year, pool and veto rule, on actual primary alarms only:
- primary alarm count;
- actual DOWN count;
- CONFIRM count;
- true DOWN retained (TP);
- false alarms retained (FP);
- true DOWN vetoed (FN);
- false alarms vetoed (TN);
- precision;
- recall;
- specificity;
- balanced accuracy;
- false-alarm reduction versus reference;
- true-DOWN retention versus reference;
- meta ROC AUC and Brier score.

Also report historical meta-training sample size and positive count.

## 9. Frozen interpretation gate

This is NOT a runtime promotion gate.

A variant earns `PRE2025_META_VETO_SIGNAL` only if 2024 satisfies all:
1. false alarms are lower than the ALL_PRIMARY_ALARMS_AS_DOWN reference;
2. true-DOWN recall >=0.70;
3. balanced accuracy >0.55;
4. meta AUC >0.55.

If 2024 does not pass, 2025/2026 may be reported only as stress pockets and may not rescue V1.

No post-result threshold or feature rescue.
