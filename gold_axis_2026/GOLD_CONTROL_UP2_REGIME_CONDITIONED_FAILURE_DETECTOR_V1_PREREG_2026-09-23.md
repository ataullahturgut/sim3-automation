# GOLD CONTROL — UP-2 REGIME-CONDITIONED FAILURE DETECTOR V1 PREREGISTRATION

**Date:** 2026-09-23  
**Identity:** `UP2_REGIME_CONDITIONED_FAILURE_DETECTOR_V1_RESEARCH`  
**Role:** small post-UP2 veto model; never emits DOWN  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Exact task

Among existing frozen One-Sided UP-2 calls, predict whether the call is a **failure**:

- target = 1 for `FALSE_UP_ACTUAL_DOWN`;
- target = 0 for `CAPTURED_UP`.

The detector is applied only after UP-2 has already emitted UP.

Decision semantics:

```
UP-2 call
   |
failure detector
   |-- p_fail >= 0.50 -> VETO -> ABSTAIN
   |-- p_fail <  0.50 -> KEEP UP
```

A veto is **not** converted to DOWN.

## 2. Frozen features

Only these three origin-safe variables:

1. `last_hour_trend_r2`
2. `sqrt_score`
3. `late_downside_intensity`

No other feature is added under V1.

## 3. Frozen model

- `sklearn.linear_model.LogisticRegression`
- L2 penalty
- C = 1.0
- solver = lbfgs
- class_weight = None
- max_iter = 5000
- standardized using training-period mean/std only
- veto threshold = 0.50

No hyperparameter or threshold sweep.

## 4. Chronology

Because all three pre-2025 false-UP actual-DOWN cases occur in 2022, a strict chronological split is mandatory.

### Formation
Train only on **2022 frozen UP-2 calls**.

Expected:
- n = 7
- 4 CAPTURED_UP
- 3 FALSE_UP_ACTUAL_DOWN

### Pre-2025 forward guard
Apply unchanged model to:
- 2023 frozen UP-2 calls;
- 2024 frozen UP-2 calls.

Expected combined:
- n = 4
- all 4 are CAPTURED_UP
- no false-UP actual-DOWN exists in this forward guard.

Therefore this guard can test only over-veto / true-UP retention, not false-UP removal.

### Locked transport
Apply unchanged model to 2025 frozen UP-2 calls.

Expected:
- n = 25
- 13 CAPTURED_UP
- 12 FALSE_UP_ACTUAL_DOWN

2025 cannot alter features, model, standardization, C, or threshold.

## 5. Frozen evaluation criteria

### Pre-2025 forward guard
Pass only if:
- retains at least 3 of 4 captured-UP calls.

### Locked 2025 transport
Descriptively supportive only if:
- removes at least 3 of 12 false-UP calls;
- retains at least 10 of 13 captured-UP calls.

### Final interpretation
Because the pre-2025 forward guard contains no false-UP cases, V1 can **never** be called validated/certified from this experiment.

Allowed statuses:
- `FAILURE_DETECTOR_V1_NOT_SUPPORTED`
- `FORWARD_RETENTION_OK_TRANSPORT_NOT_SUPPORTED`
- `TRANSPORT_SIGNAL_SAMPLE_LIMITED_NOT_CERTIFIED`

## 6. Required outputs

Report:
- 2022 training fit confusion;
- standardized coefficients and intercept;
- 2023, 2024 and combined 2023–2024 veto counts;
- locked 2025 veto confusion;
- before/after UP2 precision for each period;
- row-level p_fail ledger.

## 7. Governance

- no random split;
- no result-dependent feature changes;
- no hyperparameter search;
- no threshold search;
- no 2025 tuning;
- no 2026 use;
- no DOWN conversion;
- no runtime/production promotion.
