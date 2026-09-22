# GOLD CONTROL — CROSS-MARKET SP500 VETO V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `DOWNSIDE_SP500_CROSSMARKET_VETO_V1_RESEARCH`  
**Primary model:** frozen annual-origin `SQRT_HAR_DR` alarm surface  
**External sensor:** `SP500_FRED` daily close observations already registered in Gold Control  
**Manifest update:** FORBIDDEN in this experiment  
**Runtime / production authority:** NONE

## 1. Research question

Can an independent equity-market sensor identify Gold downside-risk alarms that are more likely to resolve as safe-haven rebound/UP rather than next-day DOWN?

Mechanism:
- the primary SQRT-HAR-DR model detects high downside risk in Gold;
- extreme equity-market weakness can trigger flight-to-gold behavior;
- therefore some Gold high-risk alarms may be false DOWN interpretations when contemporaneous equity stress is severe.

This experiment tests external confirmation/veto rather than extracting more features from the same Gold path.

## 2. Parent alarm authority

Use the frozen parent forecast surface:

`gold_axis_2026/GOLD_CONTROL_DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_FORECASTS_2026-09-22.csv`.

A primary alarm is exactly:
`sqrt_high_risk_alert == 1`.

Reference:
`ALL_PRIMARY_ALARMS_AS_DOWN`.

## 3. SP500 authority and alignment

Source:
`public.observations`, `series_id='SP500_FRED'`.

For each observation date, use one deduplicated close value.

At Gold origin date t:
- use the latest SP500 observation whose calendar date is <= origin date;
- no later observation may be used;
- if the most recent SP500 observation is more than 4 calendar days old, the row is `SP500_STALE` and excluded from model evaluation.

SP500 values are treated as historical research observations, not as a pristine PIT reconstruction.

## 4. External-sensor features

From the latest available SP500 close sequence:

1. `sp_ret1` = log return from previous SP500 observation;
2. `sp_ret5` = log return over the previous 5 SP500 observations;
3. `sp_vol20` = standard deviation of the previous 20 one-day SP500 returns;
4. `sp_z1 = sp_ret1 / sp_vol20`.

Primary risk context:
5. `gold_risk_margin = log(sqrt_normalized_risk_score)`.

No other Gold path features are allowed.

## 5. Variant A — FLIGHT_TO_GOLD_Q10 rule

At each annual origin, using only historical aligned context rows:
- compute formation Q10 of `sp_ret1`.

For a Gold primary alarm:
- if `sp_ret1 <= formation_Q10`, VETO the DOWN interpretation;
- otherwise CONFIRM.

This is a mechanism-first rule: an unusually negative equity return is treated as a potential safe-haven rebound environment.

No threshold search.

## 6. Variant B — CROSSMARKET_CONTEXT_LOGIT

Training pool:
all historical parent rows with
`sqrt_normalized_risk_score >= 0.80`.

Target:
`1` if next-day Gold close return < 0, else 0.

Features:
- sp_ret1
- sp_ret5
- sp_z1
- gold_risk_margin

Model:
ridge logistic regression:
- C=1.0;
- standardized on training only;
- no class weights;
- L-BFGS;
- no hyperparameter search.

Evaluation:
ONLY actual Gold primary alarms.

Two thresholds:

### P050
CONFIRM if probability >=0.50.

### RECALL75
Threshold selected from leave-one-out cross-fitted training probabilities:
- require training DOWN recall >=0.75;
- maximize precision;
- tie-break by balanced accuracy;
- final tie-break by higher threshold.

No target-year threshold tuning.

## 7. Chronology

Evaluation years:
- 2024: training outcomes through 2023-12-31;
- 2025: training outcomes through 2024-12-31;
- 2026 YTD: training outcomes through 2025-12-31.

2024 is the only pre-2025 chronological falsification point for this V1.

2025/2026 are retrospective stress only.

No random split.

## 8. Mandatory metrics

On actual primary alarms:
- n;
- actual DOWN;
- CONFIRM count;
- TP / FP / FN / TN;
- precision;
- recall;
- specificity;
- balanced accuracy;
- false-alarm reduction;
- true-DOWN retention.

For logistic:
- ROC AUC;
- Brier.

For Q10 rule:
- number/rate of equity-stress vetoes;
- empirical DOWN rate under veto vs non-veto.

Also report aligned-data coverage and staleness exclusions.

## 9. Frozen pre-2025 gate

A variant earns `PRE2025_CROSSMARKET_VETO_SIGNAL` only if 2024 satisfies all:

1. false alarms < reference;
2. DOWN recall >=0.70;
3. balanced accuracy >0.55;
4. for logistic, AUC >0.55;
5. for Q10 rule, the vetoed subset has lower DOWN rate than non-veto subset.

If 2024 fails, 2025/2026 may not rescue V1.

No post-result threshold or feature rescue.
