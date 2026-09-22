# GOLD CONTROL — LEGACY 12 UP-INCLUSION AUDIT V1 RESULT

**Date:** 2026-09-22  
**Identity:** `LEGACY12_UP_INCLUSION_AUDIT_V1_RESEARCH`  
**Preregistration:** `3a3f1344bc7240271d9f7369af91664147b39883`

## 1. Correction

The user's concern is valid: UP Expert Router V1 used only the newer same-clock daily models and did not carry the original 12-engine Gold Control stack back into the UP-selection architecture.

Original 12:
CAUSAL_PATCH, VW_MIDAS_MSVR_SUCCESSOR_V1, MOMENTUM_3M, RANDOM_WALK, MONTHLY_DIRECTION_3M, FAST, SLOW, MACRO_EVENT_SUCCESSOR_V2, BOCPD_RETURN_SUCCESSOR_V1, EMERGENCY_LEVEL, EMERGENCY_REVERSAL, GVZ_RISK.

They must not all become equal daily votes, but they must not be discarded.

## 2. Same-clock legacy directional-state audit

FAST, SLOW and MONTHLY_DIRECTION_3M were reconstructed with their frozen rules on the exact same next-day daily-close axis used by the modern daily UP candidates.

| State | 2023 UP precision / false-UP FPR | 2024 UP precision / false-UP FPR | 2025 UP precision / false-UP FPR |
|---|---:|---:|---:|
| FAST ROBUST_UP | 51.89% / 50.00% | 54.84% / 65.12% | 57.80% / 75.26% |
| **SLOW ROBUST_UP** | **54.43% / 35.29%** | 52.25% / 61.63% | 57.06% / 75.26% |
| MONTHLY_DIRECTION_3M UP | 51.88% / 62.75% | 58.05% / **100%** | 57.73% / 95.88% |

SLOW is genuinely noteworthy in 2023: it emitted fewer UP states and had the lowest false-UP FPR among these legacy direction states. But it did not transport; its FPR rose materially in 2024 and 2025.

FAST improved nominal UP precision over time but also became more permissive, so false-UP FPR increased.

MONTHLY_DIRECTION_3M cannot be treated as a daily UP expert: in the 2024 reconstruction it was UP on every daily origin.

## 3. Original monthly/core engines

Retained governed direction evidence:
- CAUSAL_PATCH: 2025 10/12 = 83.33%; available 2026 2/7 = 28.57%.
- VW_MIDAS_MSVR_SUCCESSOR_V1: 2025 9/12 = 75.00%; available 2026 3/7 = 42.86%.
- MOMENTUM_3M: 2025 11/12 = 91.67%; available 2026 5/7 = 71.43%.
- RANDOM_WALK: benchmark only.

These remain strategic monthly priors, not next-day experts.

## 4. Specialist/context engines

- MACRO_EVENT_SUCCESSOR_V2: event-time direction specialist only.
- GVZ_RISK: risk context only; never convert to UP vote.
- BOCPD_RETURN_SUCCESSOR_V1: pre-2025 daily origin state blocked/not found.
- EMERGENCY_LEVEL / EMERGENCY_REVERSAL: context/reversal states remain NOT_PROVEN as independent next-day predictors.

## 5. Router V2 implication

The original 12-engine work should be reintegrated role-preservingly:
- modern daily models remain the actual UP experts;
- FAST/SLOW/MONTHLY_DIRECTION become causal regime/context inputs to expert competence;
- CAUSAL_PATCH/VW-MIDAS/MOMENTUM remain slower strategic priors;
- Macro Event is activated only on its event clock;
- GVZ qualifies risk;
- BOCPD/Emergency remain blocked/not-proven until historical evidence supports them.

**Binding conclusion:** Router V1 is incomplete as a full Gold Control UP architecture because it omitted the legacy 12 context layer.
