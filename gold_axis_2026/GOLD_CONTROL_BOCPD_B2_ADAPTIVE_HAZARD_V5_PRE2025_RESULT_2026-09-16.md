# GOLD CONTROL — BOCPD B2 ADAPTIVE HAZARD V5 PRE-2025 RESULT

**Date:** 2026-09-16  
**Authority status:** primary BOCPD research model  
**Identity:** `BOCPD_HOURLY_B2_ADAPTIVE_HAZARD_V5_RESEARCH`  
**Evidence class:** `PRE2025_RETROSPECTIVE_TIME_ORDERED_COMPARISON_NOT_PRISTINE`  
**2025 accessed by model script:** **NO**  
**Runtime/production promotion:** **NONE**  
**Direction vote:** **NONE**  
**Database model-output writes:** **NONE**

## 1. Authority surface

Authoritative implementation:

`gold_axis_2026/tools/bocpd_hourly_b2_adaptive_hazard_pre2025.py`

Authoritative reproducibility workflow:

`.github/workflows/gold-bocpd-b2-adaptive-hazard-pre2025-20260916.yml`

Frozen comparison baseline:

`BOCPD_HOURLY_B2_PRE2025_BASELINE_R2_RESEARCH`

No earlier Candidate B, optimized B2, daily/monthly BOCPD, duration/residual, clipped-robust or combined BOCPD identity is active authority.

## 2. Chronology and governance

- 2022: hour-of-day normalization and NIG prior formation.
- 2023: V5 parameter development/selection only.
- 2024: pre-2025 chronological retrospective comparison.
- 2025: not queried or used by this model script.
- Random split: none.
- Automatic selector/ensemble authority: none.

2024 is **not** represented as a pristine untouched holdout because earlier BOCPD program-level research had already exposed 2024 evidence. The result is therefore a time-ordered pre-2025 retrospective comparison, not prospective proof.

The 2022 hourly history is accepted as sufficient high-coverage research formation data for this phase. This result does **not** claim that every theoretically expected 2022 market-hour slot has been independently certified complete.

## 3. Model definition

V5 uses hourly Adams-MacKay-style BOCPD with a Gaussian unknown-mean/variance segment model and NIG/Student-t predictive distribution. Its changepoint hazard is causal and adaptive rather than constant.

At each eligible completed hourly observation, hazard depends only on:

1. current BOCPD run length; and
2. lagged EWMA volatility calculated from information available before the current observation.

The hazard is logistic and bounded. No future observation, 2024 score or 2025 information is used to select V5 parameters.

## 4. 2023 development-selected configuration

- base expected regime: 20 days / 440 eligible hourly observations;
- run-length coefficient (`gamma_run`): 0.75;
- lagged-volatility coefficient (`gamma_vol`): 0.50;
- EWMA volatility half-life: 22 eligible hourly observations;
- reset threshold: 0.70;
- episodes: 67;
- matched episodes: 9;
- false episodes: 58;
- events captured: 7/17;
- precision: 0.1343;
- recall: 0.4118;
- F0.5: 0.15525.

For comparison, Baseline R2 selected on the same 2023 development period had 61 episodes, captured 6/17 events, precision 0.1148, recall 0.3529 and F0.5 0.13266.

## 5. 2024 auxiliary abnormal-volatility comparison

| Model | Episodes | Matched episodes | False episodes | Events captured | Precision | Recall | F0.5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline R2 | 57 | 12 | 45 | 11/17 | 0.210526 | 0.647059 | 0.243363 |
| Adaptive Hazard V5 | 65 | 15 | 50 | 14/17 | 0.230769 | 0.823529 | 0.269576 |

V5 lead times for the 14 captured events were 102, 32, 104, 69, 25, 91, 93, 66, 42, 77, 34, 40, 102 and 72 hours.

These metrics are based on the auxiliary abnormal-daily-volatility event construction used in the pre-2025 BOCPD comparison. They **do not establish performance against the primary structural GC-BREAK break-label universe** and must not be presented as such.

## 6. Binding interpretation

V5 is retained because it improves the time-ordered 2024 auxiliary comparison over Baseline R2 on precision, recall and F0.5, while preserving causal information flow. However, 50 of 65 2024 warning episodes are unmatched under the frozen auxiliary rule, so false-warning burden remains material.

Therefore V5 is **research authority only**. It is not a runtime engine, production engine, trading signal, equal-weight direction voter or proof of structural GC-BREAK early-warning performance.

Any future BOCPD successor requires a separately named preregistration/change-control step. This result file authorizes no additional BOCPD variant and contains no active successor recommendation.
