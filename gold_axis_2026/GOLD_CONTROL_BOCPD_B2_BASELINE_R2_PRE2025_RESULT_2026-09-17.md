# GOLD CONTROL — BOCPD B2 BASELINE R2 PRE-2025 RESULT

**Authority status:** frozen comparison baseline only  
**Identity:** `BOCPD_HOURLY_B2_PRE2025_BASELINE_R2_RESEARCH`  
**Evidence class:** `PRE2025_RETROSPECTIVE_TIME_ORDERED_COMPARISON_NOT_PRISTINE`  
**2025 used for model selection/tuning:** **NO**  
**Runtime/production promotion:** **NONE**

## Chronology

- 2022: hour-of-day normalization and NIG prior formation.
- 2023: parameter development/selection.
- 2024: pre-2025 chronological retrospective comparison.
- 2025: not queried or used by this baseline evaluation.

2024 is not called a pristine untouched holdout because prior BOCPD research had already exposed 2024 evidence.

## 2023 development-selected configuration

- constant hazard;
- expected regime: 20 days / 440 eligible hourly observations;
- reset threshold: 0.70;
- episodes: 61;
- matched episodes: 7;
- false episodes: 54;
- events captured: 6/17;
- precision: 0.114754;
- recall: 0.352941;
- F0.5: 0.132660.

## 2024 comparison result

- episodes: **57**;
- matched episodes: **12**;
- false/unmatched episodes: **45**;
- events captured: **11/17**;
- precision: **0.210526**;
- recall: **0.647059**;
- F0.5: **0.243363**.

Lead hours for the 11 captured events: 96, 32, 104, 68, 25, 90, 93, 77, 39, 102, 72.

## Binding interpretation

This model is retained only as the frozen BOCPD benchmark against which the active Adaptive Hazard V5 research model is compared. It is not a runtime engine, production engine, flat direction voter or automatic promotion candidate.
