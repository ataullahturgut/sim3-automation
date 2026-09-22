# GOLD CONTROL — UP COUNTERSIGN VETO V2 FULL-HISTORY RESULT

**Date:** 2026-09-22  
**Identity:** `DOWNSIDE_UP_COUNTERSIGN_VETO_V2_FULLHISTORY_RESEARCH`  
**Preregistration:** `06276faa56483465eeed135cfdd4fcdbb6ffee99`  
**FAST clock-normalized preregistration:** `100feec892d2b23c5d6bdf648eeb5e1210103b40`  
**Runtime authority:** NONE  
**Final status:** `NO_EXISTING_HISTORICAL_UP_ENGINE_SAFELY_CLEANS_SQRT_FALSE_ALARMS_UNDER_V2`

## 1. What was tested

This V2 executes the user's full counter-model idea on the historical UP candidates explicitly requested after the first narrow V1:

- FAST ROBUST_UP;
- RV_LOGIT UP;
- RM_LOGIT UP;
- AR1_RM_LOGIT UP;
- TTSM-S1 UP;
- TTSM-S2 UP.

The primary common-support test is 2023–2024. There are 19 SQRT alarm origins: 8 true next-day DOWN and 11 false forced-DOWN / actual-UP cases. Baseline forced-DOWN precision is 42.11%.

A useful veto must remove false forced-DOWN calls while retaining at least 80% of true DOWN alarms.

## 2. General UP false-alarm rates before conditioning on SQRT

On the common daily 2023–2024 panel, these generic UP signals are not high-precision experts:

| Model | UP calls | True UP | False UP | UP precision | False-UP rate |
|---|---:|---:|---:|---:|---:|
| RV_LOGIT | 291 | 166 | 125 | 57.04% | 42.96% |
| AR1_RM_LOGIT | 252 | 140 | 112 | 55.56% | 44.44% |
| RM_LOGIT | 254 | 141 | 113 | 55.51% | 44.49% |
| FAST original | 216 | 116 | 100 | 53.70% | 46.30% |
| TTSM-S1 | 194 | 104 | 90 | 53.61% | 46.39% |
| TTSM-S2 | 178 | 95 | 83 | 53.37% | 46.63% |

This already shows why raw UP sensitivity cannot be used as a veto-quality measure.

## 3. Primary SQRT-alarm test — 2023–2024

| Candidate | Vetoes | Good veto | Bad veto | Veto precision | False DOWN removed | True DOWN retained | Remaining DOWN precision | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| TTSM-S1 | 0 | 0 | 0 | — | 0% | 100% | 42.11% | INSUFFICIENT_ACTION_SUPPORT |
| TTSM-S2 | 0 | 0 | 0 | — | 0% | 100% | 42.11% | INSUFFICIENT_ACTION_SUPPORT |
| RV_LOGIT | 19 | 11 | 8 | 57.89% | 100% | **0%** | — | UNSAFE_VETO |
| RM_LOGIT | 19 | 11 | 8 | 57.89% | 100% | **0%** | — | UNSAFE_VETO |
| AR1_RM_LOGIT | 18 | 10 | 8 | 55.56% | 90.91% | **0%** | 0% | UNSAFE_VETO |
| FAST original | 10 | 5 | 5 | 50.00% | 45.45% | 37.50% | 33.33% | BLOCKED_TARGET_CLOCK_MISMATCH |
| FAST SQRT-clock reconstruction | 13 | 6 | 7 | 46.15% | 54.55% | **12.50%** | 16.67% | UNSAFE_VETO |

No active candidate satisfies the preregistered 80% true-DOWN-retention safety rule.

### Interpretation

The logit family looks attractive if only false alarms removed are counted, because RV_LOGIT and RM_LOGIT remove all 11 false forced-DOWN calls. But they also remove all 8 true DOWN alarms. They are therefore not false-alarm filters; on this subset they are effectively broad UP states that erase the parent.

TTSM-S1/S2 do no damage pre-2025, but only because neither produces an UP veto on the 19 parent-alarm dates. They do not clean any false alarm.

## 4. FAST clock audit

The original FAST research series and SQRT parent do not have sufficiently identical daily target clocks on the primary alarm subset:

- exact origins: 19;
- next target date matched: 14/19;
- recorded next-direction sign matched: 13/19;
- max absolute next-return difference: 0.04347.

Therefore original FAST is `BLOCKED_TARGET_CLOCK_MISMATCH` as a same-target next-day veto.

A separately preregistered reconstruction applied the unchanged FAST SMA20 + two-day-persistence rule to the exact SQRT daily-close panel. Clock integrity then passed 19/19, but veto performance became worse:

- 13 vetoes;
- 6 good / 7 bad;
- false-alarm reduction 54.55%;
- true-DOWN retention 12.50%;
- remaining forced-DOWN precision 16.67% versus 42.11% baseline.

Thus the failure is not rescued by normalizing FAST onto the SQRT clock.

## 5. 2025 unchanged stress

Baseline: 90 SQRT alarms = 45 true DOWN + 45 false forced-DOWN.

| Candidate | Vetoes | Good | Bad | Veto precision | False DOWN removed | True DOWN retained |
|---|---:|---:|---:|---:|---:|---:|
| RV_LOGIT | 90 | 45 | 45 | 50.00% | 100% | 0% |
| RM_LOGIT | 88 | 45 | 43 | 51.14% | 100% | 4.44% |
| AR1_RM_LOGIT | 86 | 44 | 42 | 51.16% | 97.78% | 6.67% |
| TTSM-S1 | 20 | 11 | 9 | 55.00% | 24.44% | **80.00%** |
| TTSM-S2 | 15 | 8 | 7 | 53.33% | 17.78% | **84.44%** |
| FAST SQRT-clock recon | 59 | 28 | 31 | 47.46% | 62.22% | 31.11% |

2025 cannot rescue pre-2025 failures. It does show that TTSM became somewhat selective in 2025, but that behavior did not exist on the pre-2025 SQRT alarm subset and therefore cannot be used to retroactively select it.

## 6. Frozen ranking interpretation

Under the preregistered safety-first rule:

1. TTSM-S1 and TTSM-S2 are tied as `INSUFFICIENT_ACTION_SUPPORT`: they preserve true DOWNs but clean zero pre-2025 false alarms.
2. RV_LOGIT and RM_LOGIT have the largest raw false-alarm removal but are `UNSAFE_VETO` because true-DOWN retention is 0%.
3. AR1_RM_LOGIT is also `UNSAFE_VETO`; retention is 0%.
4. FAST SQRT-clock reconstruction is `UNSAFE_VETO`; retention is 12.5%.
5. Original FAST is not rankable as same-target evidence because the clock audit fails.

The key conclusion is therefore not that TTSM is a good verifier. It is that **none of the tested existing historical UP engines is a useful safe verifier**.

## 7. Binding decision

`NO_EXISTING_HISTORICAL_UP_ENGINE_SAFELY_CLEANS_SQRT_FALSE_ALARMS_UNDER_V2`

The counter-model architecture remains conceptually open, but a successor must be a deliberately high-specificity UP/rebound verifier rather than a generic UP classifier or trend state.

No threshold tuning, Boolean rescue, GVZ qualification, SLOW overlay or 2025-driven rule change is authorized under V2.
