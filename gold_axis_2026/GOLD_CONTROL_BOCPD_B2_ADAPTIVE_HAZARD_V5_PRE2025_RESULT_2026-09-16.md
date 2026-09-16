# GOLD CONTROL — BOCPD B2 ADAPTIVE HAZARD V5 PRE-2025 RESULT

**Date:** 2026-09-16  
**Branch:** `gold-bocpd-hourly-b2-selective-20260916`  
**Workflow:** `Gold BOCPD B2 adaptive hazard pre-2025`  
**Workflow run:** `35150900487`  
**Artifact:** `bocpd-b2-adaptive-hazard-pre2025` / ID `10469570027`  
**Artifact SHA-256:** `f23f94696e3773815327571e1c9e6f56e5117e94717960aa32ea1fb43fd7fc0f`  
**Evidence class:** `PRE2025_RETROSPECTIVE_TIME_ORDERED_COMPARISON_NOT_PRISTINE`  
**2025 accessed by model script:** **NO**  
**Database model-output writes:** **NONE**

## 1. Chronology and governance

- 2022: hour-of-day normalization and NIG prior formation.
- 2023: challenger parameter development/selection only.
- 2024: pre-2025 chronological validation comparison.
- 2025: not queried or used.
- Random split: none.
- Runtime/production promotion: none.

2024 is not represented as a pristine untouched holdout because earlier BOCPD research had already exposed 2024 evidence. It is used only as a time-ordered pre-2025 comparison period in this phase.

## 2. Challenger

Identity: `BOCPD_HOURLY_B2_ADAPTIVE_HAZARD_V5_RESEARCH`

The BOCPD hazard is no longer constant. At each hourly observation it is updated causally from:

1. current BOCPD run length; and
2. lagged EWMA volatility calculated only from information available before the current observation.

The hazard is logistic and bounded. No future observation, 2024 selection, or 2025 information is used to select challenger parameters.

## 3. 2023 development-selected configuration

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

For comparison, the frozen pre-2025 baseline selected on the same 2023 development period had 61 episodes, captured 6/17 events, precision 0.1148, recall 0.3529 and F0.5 0.13266.

## 4. 2024 validation comparison

| Model | Episodes | Matched episodes | False episodes | Events captured | Precision | Recall | F0.5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| B2 baseline R2 | 57 | 12 | 45 | 11/17 | 0.2105 | 0.6471 | 0.24336 |
| Adaptive-hazard V5 | 65 | 15 | 50 | 14/17 | 0.2308 | 0.8235 | **0.26958** |

Adaptive-hazard V5 lead times for the 14 captured validation events were 102, 32, 104, 69, 25, 91, 93, 66, 42, 77, 34, 40, 102 and 72 hours.

## 5. Interpretation

Adaptive-hazard V5 improves the pre-2025 comparison relative to the constant-hazard baseline on all three primary event metrics: precision, recall and F0.5. It captures three additional 2024 abnormal-volatility events (14/17 versus 11/17), while the number of warning episodes rises from 57 to 65 and unmatched episodes rise from 45 to 50.

The improvement is therefore meaningful but not sufficient for production/runtime promotion. False-warning burden remains material. The result supports continuing the adaptive-hazard research line rather than the earlier Weibull residual-risk or simple clipping variants, which did not beat baseline in the same pre-2025 comparison.

## 6. Next research step

Keep V5 frozen as the current pre-2025 research reference and test narrowly defined successors without using 2025 for tuning. Priority candidates are:

- a richer but still causal hazard using separate short/medium lagged volatility states;
- empirical/learned duration structure combined with the adaptive hazard;
- principled generalized-Bayes or heavy-tail robustness rather than return clipping;
- warning episode consolidation aimed specifically at reducing the 50 unmatched 2024 episodes without sacrificing the 14/17 event coverage.

No automatic promotion is authorized by this result.
