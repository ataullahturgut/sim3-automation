# RTE-H3 V4 — MATERIAL REVERSAL TARGET PREREGISTRATION

**Date:** 2026-10-03  
**Identity:** `RTE_MATERIAL_H3_V4`  
**Branch:** `gold-h3-rte-v4-material-20261003`  
**Status:** **PREREGISTERED BEFORE 2026 OPENING**

## 1. Why the target changes

RTE V1-V3 show that the binary reversal class is too heterogeneous: many small/noisy reversals are statistically similar to continuations and create false flips.

V4 changes the target, not merely the router.

Within the V5-continuation eligible universe:
- `rescue_target = 1[v5_pred != y_up]`
- `material_reversal_target = 1[rescue_target == 1 AND abs(target_r3) >= 0.01]`

The 1.0% H3 magnitude floor is fixed before V4 results and represents a materially sized three-business-day reversal.

Candidate action is still to flip V5 direction.

## 2. Inputs

Use the already origin-safe RTE V1 feature panel.

No new source or lag is added.

Frozen features are the same low-capacity transition inputs and counterfactual gaps from RTE V1:
- V5 confidence and path-state features
- prior-trade-date CME GC volume features
- Gold call/put volume pressure features
- seven matched-continuation counterfactual-gap features

## 3. Model

- StandardScaler
- LogisticRegression
- C=0.25
- class_weight=balanced
- monthly expanding-origin refit
- minimum matured rows=100
- seed=20261003

Training target is `material_reversal_target`.

No sequential tension layer is used in V4; the experiment isolates whether target reformulation itself improves selectivity.

## 4. Development / holdout

2023 is primarily warm-up because of the 100-row maturity requirement.

Development:
- 2024 H1
- 2024 H2
- 2025 H1
- 2025 H2

2026 remains unopened until a robust rule passes.

## 5. Threshold family

Frozen grid:
`[0.50, 0.55, 0.60, 0.65, 0.70]`

For each threshold:
- candidate if `p_material >= q`
- action = flip V5

## 6. Robustness gate

Aggregate over 2024-2025:
- candidate count >= 10
- net rescue >= +5
- rescue precision >= 0.60
- candidate rate <= 0.20
- at least 3 of 4 half-year blocks have net rescue > 0
- no half-year block has net rescue < -1

Selection:
1. maximum aggregate net rescue
2. higher precision
3. more rescued
4. lower candidate rate
5. higher threshold

No eligible q => `NO_ROBUST_RTE_V4_RULE`; 2026 stays unopened.

## 7. 2026 final holdout

Only after robustness PASS:
- candidate count/rate
- rescued/broken/net
- rescue precision
- eligible V5 vs assisted accuracy
- whole-clean-2026 correct count / accuracy
- V5 missed reversal + OPAL-no-candidate coverage
- material-reversal recall

No 2026 outcome may change target, model, threshold or gate.
