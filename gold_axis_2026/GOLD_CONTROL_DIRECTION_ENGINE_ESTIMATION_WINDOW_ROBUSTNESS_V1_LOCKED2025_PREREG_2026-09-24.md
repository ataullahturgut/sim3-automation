# GOLD CONTROL — Direction Engine Estimation-Window Robustness V1 Locked-2025 Transport Preregistration

**Identity:** `DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_LOCKED2025_TRANSPORT`  
**Date:** 2026-09-24  
**Parent V1 result:** `19b815289469b0354b6edc502b5831253b4bc162`  
**Branch:** `gold-direction-history-window-transport-2025-v1-20260924`

## Purpose

Carry the **entire already-preregistered V1 estimation-window surface** into locked retrospective 2025 transport without selecting, removing, adding or retuning any window using 2025.

This is not a new window search. The candidate grids were frozen before 2025 scoring in:

`GOLD_CONTROL_DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_PREREG_2026-09-24.md`

The completed pre-2025 surface is frozen at parent commit:

`19b815289469b0354b6edc502b5831253b4bc162`.

## Non-negotiable governance

- 2025 is transport only. It may not choose or retune a window, threshold, feature, route, support minimum, confidence level or model parameter.
- 2026 is not used.
- No random split.
- No production/runtime write.
- Research DB read-only.
- No window is deleted because of poor 2025 performance.
- No window is promoted because of strong 2025 performance if it lacked pre-2025 support.
- HIGH RISK != DOWN; ABSTAIN != DOWN.
- Frozen baseline identities remain immutable comparators.

## Surface carried unchanged

### SQRT-HAR-DR

Carry exactly:
- `GOVERNED_FROZEN_EXPANDING`;
- `EXTENDED_EXPANDING`;
- `EXTENDED_ROLLING_W`, W = 250,275,...,1000.

Target year: 2025 only.

The governed frozen baseline must reproduce:
- 2025 HIGH-RISK alarms = 90.

Report:
- MSE;
- QLIKE;
- OOS R2 vs training mean;
- HIGH-RISK AUC;
- alarm count/coverage;
- risk precision/recall;
- training n;
- Q80.

No 2025 metric selects W.

### Primary UP Verifier V2 competence-memory surface

Carry exactly:
- frozen Router V2 continuation baseline;
- `EXPANDING`;
- `ROLLING_W`, W = 30,40,...,500.

The frozen 2025 baseline must reproduce:
- calls = 37;
- TP = 27;
- FP = 10;
- precision = 72.972972...%;
- false-UP FPR = 10.309278...%.

Alternative policies use only matured rows available before each 2025 target and update causally within 2025 according to the already-preregistered competence-memory policy.

Report:
- calls;
- TP/FP;
- precision;
- false-UP FPR;
- actual-UP recall;
- coverage;
- Wilson90 precision LCB;
- selected expert counts.

No 2025 result rescues an unstable pre-2025 policy.

### One-Sided UP-2 Logit V1 residual-memory surface

Keep the exact frozen 2025 residual route:
- SQRT frozen high-risk;
- frozen Primary Router V2 ABSTAIN.

Do not let SQRT/Router alternative windows alter the UP-2 test population in this transport audit.

Carry exactly:
- `EXPANDING_FROZEN`;
- rolling W = 60,65,...,95 residual cases.

Frozen expanding must reproduce locked 2025:
- residual n = 74 = 35 UP + 39 DOWN;
- calls = 25 = 13 true UP + 12 false UP;
- precision = 52%;
- false-UP FPR = 30.769230...%.

Apply the already-frozen transport interpretation:
- calls >= 5;
- precision > residual UP base rate 35/74;
- FPR < 0.50.

But a rolling policy that failed the pre-2025 gate remains NOT_SUPPORTED even if 2025 itself looks good.

## Interpretation

The principal question is **transport stability of the full pre-registered surface**.

Allowed conclusions:
- broad pre-2025 region transports;
- broad pre-2025 region does not transport;
- result is metric-tradeoff dependent;
- no stable memory policy is established;
- frozen expanding memory remains supported for a component.

Forbidden conclusion:
- "2025 says W=X is best, therefore choose W=X."

A later V2 policy may be preregistered only after this transport surface is frozen and interpreted jointly with V1.

## Required outputs

- `GOLD_CONTROL_DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1_LOCKED2025_RESULT_2026-09-24.json`
- `..._SQRT_2025_SURFACE_2026-09-24.csv`
- `..._ROUTER_2025_SURFACE_2026-09-24.csv`
- `..._UP2_2025_SURFACE_2026-09-24.csv`
- concise Markdown result.

No canonical manifest update and no runtime promotion in this task.
