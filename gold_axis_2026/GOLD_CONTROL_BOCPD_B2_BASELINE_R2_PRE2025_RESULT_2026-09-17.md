# GOLD CONTROL — BOCPD B2 BASELINE R2 PRE-2025 RESULT

**Authority status:** frozen comparison baseline only  
**Identity:** `BOCPD_HOURLY_B2_PRE2025_BASELINE_R2_RESEARCH`  
**Evidence class:** `PRE2025_RETROSPECTIVE_TIME_ORDERED_COMPARISON_NOT_PRISTINE`  
**2025 accessed by model script:** **NO**  
**Runtime/production promotion:** **NONE**  
**Direction vote:** **NONE**

## 1. Authority surface

Authoritative implementation:

`gold_axis_2026/tools/bocpd_hourly_b2_baseline_r2_pre2025.py`

Authoritative reproducibility workflow:

`.github/workflows/gold-bocpd-b2-baseline-r2-pre2025.yml`

This identity exists only as the frozen constant-hazard benchmark for `BOCPD_HOURLY_B2_ADAPTIVE_HAZARD_V5_RESEARCH`.

## 2. Chronology

- 2022: hour-of-day normalization and NIG prior formation.
- 2023: parameter development/selection.
- 2024: pre-2025 chronological retrospective comparison.
- 2025: not queried or used by this baseline model script.
- Random split: none.

2024 is not called a pristine untouched holdout because prior BOCPD program-level research had already exposed 2024 evidence.

The 2022 hourly history is accepted as sufficient high-coverage research formation data for this phase. This result does **not** claim that every theoretically expected 2022 market-hour slot has been independently certified complete.

## 3. 2023 development-selected configuration

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

## 4. 2024 auxiliary abnormal-volatility comparison

- episodes: **57**;
- matched episodes: **12**;
- false/unmatched episodes: **45**;
- events captured: **11/17**;
- precision: **0.210526**;
- recall: **0.647059**;
- F0.5: **0.243363**.

Lead hours for the 11 captured events: 96, 32, 104, 68, 25, 90, 93, 77, 39, 102, 72.

These metrics use the auxiliary abnormal-daily-volatility event construction used in the pre-2025 BOCPD comparison. They **do not establish performance against the primary structural GC-BREAK break-label universe**.

## 5. Binding interpretation

R2 is retained only as the frozen benchmark against which Adaptive Hazard V5 is compared. It is not an active challenger, runtime engine, production engine, trading signal, flat direction voter or automatic promotion candidate.

No parameter or threshold in this result may be retuned using 2025 and then represented as pre-2025 evidence.
