# GOLD CONTROL — FROZEN UP CASCADE 2026 REPLAY AUTHORITY

**Date:** 2026-10-02  
**Status:** FROZEN PRE-RUN  
**Purpose:** Evaluate the already-frozen UP architecture on the available 2026 same-clock daily history without tuning.

## Frozen components

Primary:
- `UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH`
- exact direct expert pool: TTSM-S2, TTSM-S1, Bonato AR1_RM QBoost h=1, AR1_RM_LOGIT, RM_LOGIT
- exact FAST/SLOW/MONTHLY legacy competence context
- same >=30 call support, precision > 0.50, FPR < 0.50 eligibility
- same one-sided 90% Wilson LCB ranking and frozen tie order

Secondary:
- `RESIDUAL_ONE_SIDED_UP2_LOGIT_V1_RESEARCH`
- exact nine features
- L2 LogisticRegression C=1.0 / lbfgs / no class weighting
- exact annual training and strict-prequential DOWN-Q80 threshold rule
- exact route: SQRT HIGH RISK + Primary Router ABSTAIN only

Risk route:
- frozen SQRT-HAR-DR algorithm
- HIGH RISK remains a route condition, not a DOWN prediction

## 2026 extension semantics

- Use the same governed 5-minute research cache and target clock.
- Primary Router competence history continues causally from the original 2024 -> 2025 sequence into 2026.
- Direct expert algorithms may use only prior/matured observations as already specified by their frozen implementations.
- UP-2 is refit for target-year 2026 using only its historical formation rows through 2025.
- The 2026 target labels are used only for scoring, never for selection or tuning.
- No threshold, feature, expert membership, context rule, support threshold or tie-break is changed.

## Mandatory integrity checks

Before accepting 2026 output, the replay must reproduce:

Primary Router V2:
- 2024: 42 UP outputs = 26 true + 16 false
- 2025: 37 UP outputs = 27 true + 10 false
- 2025 selected expert: RM_LOGIT on all 37 emitted UP calls

UP-2 historical ledger:
- 2022-2024: 26 residual rows, 11 calls = 8 true + 3 false
- 2025: 74 residual rows, 25 calls = 13 true + 12 false

External source reconstruction:
- 2020 residual: 72 = 35 UP + 37 DOWN
- 2021 residual: 26 = 11 UP + 15 DOWN

If any integrity check fails, 2026 result is BLOCKED rather than repaired.

## Required 2026 metrics

Primary Router:
- eligible timeline n
- UP calls
- true / false UP
- precision
- call-error rate = false / UP calls
- false-UP FPR
- actual-UP recall
- coverage
- selected expert counts

SQRT route:
- HIGH RISK alarms
- actual UP / DOWN inside alarms
- Primary-UP overlap
- Primary-ABSTAIN residual composition

UP-2:
- residual n
- UP2 calls
- true / false UP
- precision
- call-error rate
- false-UP FPR
- missed-UP recall
- coverage
- AUC / Brier
- frozen 2026 threshold

Combined UP evidence:
- union of Primary UP and UP-2 calls
- true / false UP
- precision
- call-error rate
- daily coverage
- actual-UP recall
- false-UP FPR

## Interpretation constraint

2026 is already-observed retrospective stress evidence. It is important for transport robustness but is not a fresh blind holdout and cannot be used to retune the frozen components.
