# GOLD CONTROL — UP EXPERT ROUTER V1 RESULT

**Date:** 2026-09-22  
**Identity:** `UP_EXPERT_ROUTER_V1_RESEARCH`  
**Preregistration commit:** `aaad05b7773b021a7485e07aec48332596cca8cb`  
**Final status:** `ROUTER_V1_NOT_PROMOTED_2024_PRECISION_GAIN_GATE_FAILED`  
**Runtime authority:** NONE

## 1. What was built

A causal class-specific selector was tested over the five highest-ranked same-clock daily UP candidates from manifest v2.00:

- TTSM-S2;
- TTSM-S1;
- Bonato AR1_RM QBoost h=1;
- AR1_RM_LOGIT;
- RM_LOGIT.

At each origin the router:
1. looked only at matured prior outcomes;
2. checked which experts currently said UP;
3. kept only experts with >=30 historical UP calls, historical UP precision >50%, and historical false-UP FPR <50%;
4. ranked eligible experts by a one-sided 90% Wilson lower bound on historical UP precision;
5. selected one expert or abstained.

No 2024/2025 threshold tuning, majority vote, top-2 combination or post-score rescue was allowed.

## 2. Alignment integrity

TTSM, Bonato h=1 and realized-moment-logit artifacts aligned exactly:

- total common rows: 645;
- 2023: 203;
- 2024: 205;
- 2025: 237;
- target-date mismatches: 0;
- actual-sign mismatches: 0;
- max absolute actual-return difference: 0.

## 3. 2023 development and fixed benchmark

| Expert | UP calls | True UP | False UP | UP precision | False-UP FPR |
|---|---:|---:|---:|---:|---:|
| TTSM-S2 | 101 | 52 | 49 | 51.49% | 48.04% |
| TTSM-S1 | 108 | 56 | 52 | 51.85% | 50.98% |
| Bonato AR1_RM h=1 | 119 | 58 | 61 | 48.74% | 59.80% |
| AR1_RM_LOGIT | 103 | 54 | 49 | 52.43% | 48.04% |
| RM_LOGIT | 107 | 58 | 49 | **54.21%** | **48.04%** |

Under the preregistered 2023-only benchmark rule, `RM_LOGIT` became the fixed benchmark before 2024 was scored.

## 4. Frozen 2024 validation

| Metric | UP Expert Router | Fixed RM_LOGIT |
|---|---:|---:|
| Common origins | 205 | 205 |
| UP outputs | 135 | 149 |
| Coverage | 65.85% | 72.68% |
| True UP | 77 | 84 |
| False UP | 58 | 65 |
| **UP precision** | **57.04%** | 56.38% |
| **False-UP FPR** | **67.44%** | 75.58% |
| Actual-UP recall | 64.71% | 70.59% |

Router expert selections in 2024:
- RM_LOGIT: 64;
- TTSM-S1: 55;
- TTSM-S2: 14;
- AR1_RM_LOGIT: 2;
- Bonato: 0.

The router reduced false-UP FPR by **8.14 percentage points**, which passed the frozen false-UP-reduction gate.

However UP precision improved only from **56.38% to 57.04%**, a gain of about **+0.66 percentage point**. The preregistered gate required at least +3 pp.

Therefore the 2024 promising gate **FAILED**.

## 5. Locked 2025 challenge

Rules were unchanged.

| Metric | UP Expert Router | Fixed RM_LOGIT |
|---|---:|---:|
| Origins | 237 | 237 |
| UP outputs | 137 | 229 |
| Coverage | 57.81% | 96.62% |
| True UP | 87 | 135 |
| False UP | 50 | 94 |
| **UP precision** | **63.50%** | 58.95% |
| **False-UP FPR** | **51.55%** | 96.91% |
| Actual-UP recall | 62.14% | 96.43% |

In 2025 the router selected:
- TTSM-S2: **109** times;
- TTSM-S1: **28** times;
- all other experts: **0** times.

Descriptively, the router:
- improved UP precision by about **+4.55 pp**;
- reduced false-UP FPR by about **45.36 pp**;
- deliberately abstained much more often.

This is a strong transport pattern, but 2025 cannot rescue a failed 2024 preregistered gate.

## 6. Interpretation

The core idea is **not falsified**, but V1 is not promoted.

The important result is that the selector did what it was designed to do on false-UP burden:
- 2024 false-UP FPR fell materially;
- 2025 false-UP FPR fell dramatically;
- by 2025 the causal competence state had effectively stopped trusting the broad logit UP experts and routed all UP decisions through TTSM-S1/S2.

The weakness is that the expanding-history V1 selector did **not** create enough UP-precision lift in the frozen 2024 validation.

This suggests the next scientifically defensible successor is not a larger model zoo. It is a preregistered **recency-aware competence** or **conservative probability-combination** layer that can react faster when an expert's class-specific reliability changes, while preserving abstention and the false-UP objective.

## 7. Binding decision

`UP_EXPERT_ROUTER_V1_RESEARCH = ROUTER_V1_NOT_PROMOTED_2024_PRECISION_GAIN_GATE_FAILED / NOT_RUNTIME / NOT_PRODUCTION_AUTHORITY`

2025 is diagnostic transport only. No 2025-driven threshold change is authorized.
