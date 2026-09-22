# GOLD CONTROL — SQRT ALARM SEMANTIC AUDIT V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `SQRT_ALARM_SEMANTIC_AUDIT_V1_RESEARCH`  
**Purpose:** determine whether the current "false alarm" framing confounds downside-risk realization with next-day close direction.  
**Parent:** frozen `DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_RESEARCH` / SQRT-HAR-DR  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Question

The SQRT parent forecasts next-day downside realized variance (DR), not next-day close direction.

This audit asks:

> Among frozen SQRT alarms, how often does the forecasted high downside-risk state actually realize, independently of whether the next-day close ends UP or DOWN?

No suppressor, Router threshold, persistence rule, competence rule, or direction model is changed in this audit.

## 2. Frozen realized-risk definition

For evaluation year Y:

- retain the frozen annual SQRT formation and its nearest-rank `Q80_Y` threshold;
- `FORECAST_HIGH_RISK = 1` iff frozen SQRT forecast `>= Q80_Y`;
- `REALIZED_HIGH_RISK = 1` iff the realized target-day downside realized variance `target_dr >= Q80_Y`;
- next-day direction is `DOWN` iff frozen target close-to-close log return < 0, otherwise `UP` when > 0.

The same Q80 threshold is used for both forecast-state and realized-state classification because it is already the parent model's frozen annual high-risk boundary.

No alternative percentile is allowed.

## 3. Primary four-way alarm anatomy

On existing SQRT alarm rows only, assign exactly one category:

1. `RISK_HIT_DOWN_CLOSE`: realized DR >= Q80 and next-day close direction DOWN.
2. `RISK_HIT_UP_CLOSE`: realized DR >= Q80 and next-day close direction UP.
3. `RISK_MISS_DOWN_CLOSE`: realized DR < Q80 and next-day close direction DOWN.
4. `RISK_MISS_UP_CLOSE`: realized DR < Q80 and next-day close direction UP.

Important semantic constraint:

`RISK_HIT_UP_CLOSE` may indicate a high downside-risk day that nevertheless closed UP. It must not automatically be described as a chronological intraday rebound unless the available data prove the intraday path ordering. The audit may call it "high-risk + UP-close".

## 4. Secondary full-parent risk diagnostics

Across all frozen SQRT evaluation rows, not just alarms, report by year and pooled:

- risk alarm count;
- realized high-risk target count;
- true high-risk positives: alarm + realized high risk;
- false high-risk positives: alarm + realized low risk;
- false negatives: no alarm + realized high risk;
- true negatives: no alarm + realized low risk;
- risk precision = TP / (TP+FP);
- risk recall = TP / (TP+FN);
- risk specificity where defined.

These are risk-state metrics, not direction metrics.

## 5. Direction-framing audit

Among existing SQRT alarms:

- count next-day UP-close alarms currently liable to be called "direction false alarms";
- split those UP-close alarms into realized-high-risk versus realized-low-risk;
- report the fraction of UP-close alarms that were nevertheless realized-high-risk.

Also report the analogous split for next-day DOWN-close alarms.

## 6. Integrity gate

Reproduce frozen alarm counts exactly:

- 2020 = 212
- 2021 = 28
- 2022 = 11
- 2023 = 2
- 2024 = 17
- pooled = 270

Reproduce frozen direction counts on alarms:

- pooled actual DOWN = 127
- pooled actual UP = 143

Any mismatch => `BLOCKED_INTEGRITY_MISMATCH`.

## 7. Governance

- random split: forbidden;
- 2025: not used;
- 2026: not used;
- external 2018–2021: corrected 276-bar session-masked research-only spine;
- governed DB: read-only;
- no production writes;
- no model promotion;
- no result-dependent threshold tuning.

This is a descriptive semantic audit. It does not certify a direction model or a trading rule.

## 8. Interpretation rule

Possible conclusions:

- If a material fraction of UP-close SQRT alarms are `RISK_HIT_UP_CLOSE`, the phrase "false alarm" is semantically unsafe when applied to the SQRT risk sensor merely because direction ended UP.
- If most UP-close SQRT alarms are also realized-risk misses, then the existing false-alarm-cleaning framing remains broadly defensible.
- Regardless of outcome, risk forecasting and direction forecasting remain separate tasks.

No numerical cutoff for "material" is preregistered; the audit reports the empirical decomposition and leaves architecture decisions explicit rather than thresholding the narrative.
