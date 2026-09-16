# GOLD CONTROL — BOCPD B2 PRE-2025 SUCCESSOR COMPARISON

**Date:** 2026-09-16  
**Branch:** `gold-bocpd-hourly-b2-selective-20260916`  
**Workflow:** `Gold BOCPD B2 successors pre-2025`  
**Workflow run:** `35149774834`  
**Artifact:** `bocpd-b2-successors-pre2025` / ID `10467909577`  
**Artifact SHA-256:** `8af60326babc985ceffe367a80ea06c8a30867ea5398309724aa68212ee3c6c3`  
**Evidence class:** `PRE2025_RETROSPECTIVE_TIME_ORDERED_COMPARISON_NOT_PRISTINE`  
**2025 accessed by model script:** **NO**  
**Database model-output writes:** **NONE**

## 1. Chronology

- 2022: hour-of-day normalization + NIG prior fit only.
- 2023: model/parameter development and selection.
- 2024: pre-2025 chronological validation comparison.
- 2025: not queried or used by this script.

2024 is not represented as a pristine untouched holdout because prior BOCPD research had already exposed 2024 evidence. It is nevertheless a strictly pre-2025, time-ordered comparison and 2025 is not used for tuning.

## 2. Data coverage used

| Year | Stored session-gated 1h rows | Eligible exact-1h returns |
|---|---:|---:|
| 2022 | 5,893 | 5,635 |
| 2023 | 5,841 | 5,579 |
| 2024 | 5,910 | 5,650 |

2022 is treated as high-coverage research formation data, not as a formally certified gap-free market calendar.

The common event construction is the frozen daily abnormal-volatility formula (`abs(z) >= 2`, lagged trailing-20 volatility). There are 17 such events in 2023 development and 17 in 2024 validation.

Formal warning validity remains: an episode must be available no later than the previous governed daily close and no more than 120 calendar hours before event-close availability. F0.5 emphasizes selectivity/precision.

## 3. Models evaluated

1. `BOCPD_HOURLY_B2_PRE2025_BASELINE_R2_RESEARCH` — constant-hazard BOCPD, reset-strength filtering and 24h episode cooldown.
2. `BOCPD_HOURLY_B2_DURATION_RESIDUAL_V2_RESEARCH` — run-length-dependent Weibull hazard + posterior residual-time risk within roughly five trading-session days.
3. `BOCPD_HOURLY_B2_ROBUST_CLIPPED_V3_RESEARCH` — engineering robustness test using clipped hour-normalized returns. This is **not** claimed to reproduce Altamirano et al.'s generalized-Bayes robust BOCD.
4. `BOCPD_HOURLY_B2_DURATION_ROBUST_V4_RESEARCH` — duration/residual-time model plus the same clipping robustness layer.

## 4. 2023 development-selected settings

### Baseline R2
- expected regime: 20 days / 440 eligible hourly observations;
- reset threshold: 0.70;
- 61 episodes;
- 6/17 development events captured;
- precision 0.1148;
- recall 0.3529;
- F0.5 0.1327.

### Duration / residual V2
- expected regime: 20 days / 440 observations;
- Weibull shape: 0.70;
- residual-risk threshold: 0.30;
- 4 episodes;
- 1/17 development events captured;
- precision 0.2500;
- recall 0.0588;
- F0.5 0.1515.

### Robust clipped V3
- expected regime: 20 days / 440 observations;
- reset threshold: 0.70;
- clip level: 2.5 standardized-return units;
- 61 episodes;
- 6/17 development events captured;
- precision 0.1311;
- recall 0.3529;
- F0.5 0.1500.

### Duration + robust V4
- duration structure inherited from V2: 20 days / Weibull shape 0.70;
- clip level: 6.0;
- residual-risk threshold: 0.30;
- 4 episodes;
- 1/17 development events captured;
- precision 0.2500;
- recall 0.0588;
- F0.5 0.1515.

## 5. 2024 validation comparison

| Model | Episodes | Matched episodes | False episodes | Events captured | Precision | Recall | F0.5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| B2 baseline R2 | 57 | 12 | 45 | 11/17 | 0.2105 | 0.6471 | **0.2434** |
| Robust clipped V3 | 77 | 11 | 66 | 11/17 | 0.1429 | 0.6471 | 0.1692 |
| Duration/residual V2 | 7 | 1 | 6 | 1/17 | 0.1429 | 0.0588 | 0.1111 |
| Duration + robust V4 | 6 | 0 | 6 | 0/17 | 0.0000 | 0.0000 | 0.0000 |

Baseline R2 captured 11 events at lead times 96, 32, 104, 68, 25, 90, 93, 77, 39, 102 and 72 hours.

## 6. Binding interpretation

The first duration/residual-time implementation does **not** improve the B2 line under this pre-2025 comparison. It becomes too selective and loses event coverage. The simple clipping robustness test also fails to improve the precision/false-warning trade-off: it retains 11/17 event coverage but increases episode burden from 57 to 77 and lowers F0.5.

Therefore none of V2/V3/V4 is promoted over the baseline on this evidence. The baseline itself is not runtime-promoted: 45/57 2024 episodes remain unmatched under the frozen 120h rule, so false-warning burden is still material.

The scientifically clean next research step is **not** to tune these failed variants on 2024 or 2025. A separately named phase-2 challenger may test (a) causally learned/adaptive hazard rather than a fixed hazard, and/or (b) a principled heavy-tail/robust likelihood rather than simple clipping, with selection confined to 2023 and 2024 retained only for comparison.

## 7. Governance

- random split: prohibited;
- 2025 tuning: prohibited;
- direction vote: prohibited;
- runtime/production promotion: none;
- DB model-output write: none;
- PR merge: none;
- 2022 data status: high-coverage research formation, not formally certified gap-free.
