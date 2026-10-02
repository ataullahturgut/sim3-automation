# GOLD CONTROL — FROZEN UP CASCADE 2026 REPLAY V1 AUTHORITY

**Date:** 2026-10-02  
**Status:** FROZEN PRE-RUN  
**Identity:** `GOLD_CONTROL_UP_CASCADE_2026_REPLAY_V1`

## Purpose

Evaluate the already-frozen UP research architecture on the previously unreported 2026 observed-stress period without changing any rule.

This is a retrospective 2026 replay, not a fresh blind holdout and not a tuning stage.

## Frozen components

### Primary UP Verifier V2

Identity:
`UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH`

Direct experts, unchanged:
1. TTSM-S2
2. TTSM-S1
3. Bonato AR1_RM QBoost h=1
4. AR1_RM_LOGIT
5. RM_LOGIT

Legacy competence context, unchanged:
- FAST_UP
- SLOW_UP
- MONTHLY_DIRECTION_3M_UP

Eligibility/ranking, unchanged:
- matured prior outcomes only;
- same legacy bucket if that expert has at least 30 historical UP calls, otherwise global matured fallback;
- historical UP calls >= 30;
- precision > 50%;
- false-UP FPR < 50%;
- rank by one-sided 90% Wilson precision LCB, then lower FPR, higher precision, frozen expert order;
- output UP or ABSTAIN.

Chronology extension:
- reproduce 2024 and locked 2025 exactly;
- continue the same competence history causally from 2025 into 2026;
- no calendar-year reset at 2026-01-01.

### One-Sided UP-2 Logit V1

Identity:
`RESIDUAL_ONE_SIDED_UP2_LOGIT_V1_RESEARCH`

Route, unchanged:
`SQRT HIGH RISK + Primary UP Verifier V2 ABSTAIN`.

Features, unchanged:
- sqrt_score
- lag1_close_return
- downside_share
- intraday_end_norm
- close_location
- trough_recovery_norm
- last_quarter_return_norm
- direct_up_fraction
- legacy_up_fraction

Model, unchanged:
- L2 LogisticRegression
- C=1.0
- lbfgs
- no class weighting.

Threshold algorithm, unchanged:
`tau=max(0.50, nearest-rank Q80 of strictly-prequential historical actual-DOWN p_UP scores)`.

For the 2026 replay, the training set may contain only route-consistent residual cases whose target outcomes matured by 2025-12-31. No 2026 outcome enters model fitting or threshold calibration.

## Parent risk route

Use the frozen SQRT-HAR-DR parent forecast ledger:
`GOLD_CONTROL_DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_FORECASTS_2026-09-22.csv`
at commit:
`2926796b6a7e9048d2c091c9c571cb928b773e02`.

2026 parent facts to reproduce before scoring:
- 173 retained target rows through 2026-08-31;
- 148 SQRT HIGH RISK alarms;
- among those alarms: 74 actual UP and 74 actual DOWN.

## Integrity requirements

Before accepting a 2026 result, the replay must reproduce frozen historical checkpoints:

Primary Router:
- 2024: 42 UP outputs = 26 true + 16 false;
- 2025: 37 UP outputs = 27 true + 10 false;
- 2025 selected expert RM_LOGIT count = 37.

UP-2:
- pooled 2022-2024 residual: n=26, 11 calls = 8 true + 3 false;
- 2025 residual: n=74, 25 calls = 13 true + 12 false;
- 2025 tau = 0.5312265857773989 (numerical tolerance allowed).

If these checks fail, 2026 metrics are invalid.

## Required 2026 outputs

### Primary UP Verifier standalone
- eligible timeline n
- UP calls
- true UP
- false UP
- precision
- call-error rate = false / UP calls
- false-UP FPR = false UP / all actual DOWN
- actual-UP recall
- coverage
- selected-expert counts
- legacy-bucket counts.

### Primary inside SQRT HIGH RISK
Same metrics restricted to the 148 parent alarms.

### UP-2 residual
- residual n
- actual UP / DOWN
- UP2 calls
- true / false UP
- precision
- call-error rate
- recall
- false-UP FPR
- coverage
- AUC
- Brier
- frozen-algorithm 2026 tau.

### Combined positive-UP cascade inside SQRT HIGH RISK
Combine:
- Primary UP calls inside SQRT alarms;
- UP-2 calls only on Primary ABSTAIN alarms.

Report:
- total positive-UP calls
- true / false UP
- precision
- call-error rate
- false-UP FPR
- actual-UP recall
- alarm-route coverage
- remaining hard residual actual UP / DOWN.

## Governance

- 2026 results cannot alter any frozen parameter.
- No model/threshold/feature selection from 2026.
- No production writes.
- No runtime promotion.
- ABSTAIN remains ABSTAIN; it is never auto-labeled DOWN.
