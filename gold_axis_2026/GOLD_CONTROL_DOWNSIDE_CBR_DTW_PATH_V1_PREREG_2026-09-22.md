# GOLD CONTROL — CASE-BASED PATH MORPHOLOGY / DTW V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `DOWNSIDE_CBR_DTW_PATH_V1_RESEARCH`  
**Primary model:** frozen annual-origin `SQRT_HAR_DR` alarm surface  
**Manifest update:** FORBIDDEN in this experiment  
**Runtime / production authority:** NONE

## 1. Research question

Can a false-alarm veto be learned from the **shape of the completed intraday path itself**, rather than from global scalar summaries?

This is a cross-domain transfer from:
- case-based reasoning in industrial fault diagnosis / predictive maintenance;
- dynamic-time-warping based signal matching;
- false-alarm suppression using waveform morphology in medical monitoring.

The primary SQRT-HAR-DR model is not changed.

For each primary alarm, the case-based layer asks:

> Which historical elevated-risk intraday paths look most similar to today, and how often did those analogous cases lead to next-day DOWN?

## 2. Parent alarm authority

Use:

`gold_axis_2026/GOLD_CONTROL_DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_FORECASTS_2026-09-22.csv`

A primary alarm is exactly:

`sqrt_high_risk_alert == 1`.

Reference decision:

`ALL_PRIMARY_ALARMS_AS_DOWN`.

## 3. Intraday path representation

Source:
`public.xau_intraday_research_cache_5m`.

For each completed origin date:
- America/New_York;
- weekdays;
- retained only if parent row exists;
- within-date consecutive log returns only;
- no overnight return.

For returns `r_i`, define:

`RV_t = sum_i r_i^2`.

Two causal path channels are built:

### Channel A — volatility-normalized cumulative price path

`P_j = (sum_{i<=j} r_i) / sqrt(RV_t)`.

### Channel B — cumulative signed variance-pressure path

`S_j = [sum_{i<=j}(r_i^2 I(r_i<0) - r_i^2 I(r_i>0))] / RV_t`.

Each channel is linearly resampled to exactly **48 equally spaced relative-time points** over the completed trading day.

No future day information enters the representation.

The purpose is to retain:
- order of selling / recovery;
- persistence versus reversal;
- where in the day downside pressure accumulated;
- whether the day ended after sustained or recovered stress.

Risk magnitude itself is deliberately normalized out because the primary SQRT-HAR already supplies the risk-level decision.

## 4. Case similarity

Primary similarity engine:

**multivariate Dynamic Time Warping** over the 48x2 path.

Frozen local cost:
squared Euclidean distance across the two channels.

Frozen Sakoe-Chiba band:
**6 resampled points**.

Final case distance:
square root of terminal DTW cost divided by path length.

No learned distance metric.

## 5. Historical case pools

Two prespecified pools.

### STRICT_CASES
Only prior parent rows with:
`sqrt_high_risk_alert == 1`.

### CONTEXT_CASES
Prior elevated-risk rows with:
`sqrt_normalized_risk_score >= 0.80`.

Evaluation is ALWAYS only on actual primary alarms.

## 6. Case-based prediction

Frozen nearest-neighbor count:

`k=3`.

For each target alarm:
- identify 3 nearest historical cases by DTW distance;
- weight neighbors by `1/(distance + 1e-8)`;
- estimate:
  `p_case = weighted mean(next-day DOWN label)`.

If fewer than 3 historical cases exist, the variant is `NOT_PROVEN`.

No k-grid search.

## 7. Veto rules

### P050
CONFIRM if `p_case >= 0.50`, otherwise VETO.

### RECALL75
Using only the historical training case pool:
- obtain leave-one-out kNN-DTW probabilities;
- among candidate thresholds from unique LOO probabilities plus 0 and 1,
- retain thresholds with LOO DOWN recall >=0.75;
- select maximum precision;
- tie-break by balanced accuracy;
- final tie-break by higher threshold.

Then freeze this threshold for the target year.

No target-year threshold tuning.

## 8. Chronology

Evaluation:
- 2024: use only cases whose target outcomes completed through 2023-12-31;
- 2025: through 2024-12-31;
- 2026 YTD: through 2025-12-31.

2024 is the only pre-2025 chronological falsification point for this identity and is small-sample retrospective evidence.

2025/2026 are retrospective stress only.

No random split.

## 9. Mandatory metrics

On actual primary alarms only:
- n alarms;
- actual DOWN;
- CONFIRM count;
- TP / FP / FN / TN;
- precision;
- recall;
- specificity;
- balanced accuracy;
- ROC AUC of `p_case`;
- Brier score;
- false-alarm reduction versus reference;
- true-DOWN retention versus reference.

Also retain:
- train-pool size and class counts;
- selected RECALL75 threshold;
- mean nearest-neighbor DTW distance.

## 10. Frozen gate

A variant earns `PRE2025_PATH_MORPHOLOGY_SIGNAL` only if in 2024:

1. false alarms < reference false alarms;
2. true-DOWN recall >=0.70;
3. balanced accuracy >0.55;
4. AUC >0.55.

If 2024 fails, 2025/2026 cannot rescue V1.

No result-dependent feature, k, band, context-boundary or threshold rescue.
