# GOLD CONTROL — SQRT MEMORY POLICY FREEZE V1

**Date:** 2026-09-24  
**Identity:** `GOLD_CONTROL_SQRT_MEMORY_POLICY_FREEZE_V1`  
**Scope:** SQRT-HAR-DR estimation memory only  
**Status:** `PRE2025_SQRT_MEMORY_POLICY_FROZEN_READY_FOR_LOCKED_2025_TRANSPORT`

## 1. Authority basis

The history-window methodology must be frozen entirely on pre-2025 evidence. Locked 2025 may be opened only after that freeze, and the memory rule may not be changed after seeing 2025.

SQRT is a risk engine, so the binding selection dimensions are MSE, QLIKE, high-risk AUC and alarm stability. The same memory rule is not automatically transferred to Primary UP V2 or UP-2.

Multi-window pooling is not introduced under this identity because a robust single memory regime was found; pooling would be a separate successor hypothesis.

## 2. Frozen SQRT memory policy

**Family:** rolling estimation window  
**Primary operational window:** **500 matured observations**  
**Frozen robustness envelope:** **475 / 500 / 525 / 550** matured observations  
**Mandatory comparator:** expanding history  
**Structural-break policy:** diagnostic challenger only

W=500 is not being declared a unique mathematical optimum. It is frozen as the deterministic operational representative of the contiguous approximately-500-observation plateau identified before 2025.

The other three band members are sensitivity checks only. They may not replace W=500 after 2025 is opened.

SQRT formula, features, q80 high-risk semantics and evaluation clock remain unchanged.

## 3. Evidence that is now closed

The pre-2025 evidence showed that every member of the contiguous 475–550 band improved both MSE and QLIKE versus expanding in each of the 2022, 2023 and 2024 origins, while high-risk AUC was broadly preserved.

The origin-safe structural-break challenger repeatedly selected 2020-03-20, but was not chosen as the primary policy because its alarm coverage became too sparse, including one alarm in 2023.

No further pre-2025 window search is authorized under V1.

## 4. Locked-2025 transport contract — frozen before opening 2025

Primary specification: **W=500**.

Mandatory simultaneous reporting:
- EXPANDING;
- W=475;
- W=500;
- W=525;
- W=550;
- BREAK-CONDITIONED as diagnostic only.

Metrics:
- MSE;
- QLIKE;
- high-risk AUC;
- alarm coverage;
- alarm precision;
- alarm recall.

### Primary W=500 transport label

**SUPPORTIVE** only if:
1. MSE <= expanding;
2. QLIKE <= expanding;
3. high-risk AUC >= expanding AUC - 0.02;
4. at least one high-risk alarm is emitted.

**MIXED** if the supportive rule is not fully met, but both loss metrics are not simultaneously worse than expanding and alarms do not collapse to zero.

**NOT_SUPPORTIVE** if both MSE and QLIKE are worse than expanding, or W=500 emits zero high-risk alarms.

### Frozen-band robustness label

- **SUPPORTIVE:** at least 3/4 of 475/500/525/550 satisfy the primary supportive rule.
- **MIXED:** exactly 2/4 satisfy it.
- **NOT_SUPPORTIVE:** 0/4 or 1/4 satisfy it.

These labels are frozen now, before locked 2025 is evaluated.

## 5. Forbidden after 2025 is opened

- changing W=500;
- changing the 475–550 envelope;
- promoting whichever window looks best in 2025;
- changing SQRT formula/features/q80 semantics;
- using 2026 for selection;
- silently introducing multi-window pooling.

A disappointing 2025 result must be recorded as transport failure/mixed evidence, not repaired by retuning this identity.

## 6. Scope boundary

This freeze applies only to **SQRT-HAR-DR estimation memory**.

Primary UP V2 uses matured expert-competence history and UP-2 uses route-consistent residual-case history. Their memory policies require role-specific evidence and must not inherit W=500 automatically.

## 7. Governance

- 2025 used for freeze: **NO**
- 2026 used for freeze: **NO**
- random split: **NO**
- production writes: **NO**
- runtime promotion: **NO**
- canonical manifest modified: **NO**
