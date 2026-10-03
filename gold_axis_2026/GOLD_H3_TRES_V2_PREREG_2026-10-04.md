# TRES-H3 V2 — LAST-DECISIVE PATH STATE / PICTURE GOVERNOR PREREGISTRATION

**Freeze date:** 2026-10-04  
**Branch:** `gold-h3-tres-v1-20261004`  
**Identity:** `TRES_H3_V2_LAST_STATE`  
**Status:** **FROZEN BEFORE V2 MODEL RESULTS**

## 1. Motivation

TRES V1 Stage 1 used an absorbing first-passage competing-risk label.

Post-Stage2 diagnosis showed that this loses a critical sequence:
- C_THEN_R paths are terminal reversals 95.65% of the time;
- R_THEN_C paths are terminal continuations 100% of the time.

Therefore V2 models the **last decisive barrier state** rather than the first barrier hit.

## 2. Frozen path-state target

Use the same Stage-0 primary barrier:

`B_t = 1.00 * sigma20`

For h=1,2,3:

- C if `g_h >= +B_t`
- R if `g_h <= -B_t`
- N otherwise

Path target:

- `REVERSAL_LAST` if the latest non-N state in h=1..3 is R
- `CONTINUATION_LAST` if the latest non-N state is C
- `UNRESOLVED` if all states are N

No barrier or state definition changes after model results.

## 3. Physical interpretation

The three predicted probabilities are treated directly as path memberships:

- `mu_R = P(REVERSAL_LAST)`
- `mu_C = P(CONTINUATION_LAST)`
- `mu_U = P(UNRESOLVED)`

They sum to 1 and form a probabilistically grounded Picture-style:
- reversal-positive membership
- continuation-negative membership
- neutral / unresolved membership

No arbitrary fuzzy membership function is fitted.

## 4. Predictor set

Identical low-capacity origin-state set to TRES V1 Stage 1:

- momentum_up
- abs_h_ret_12
- trend_strength
- opposite_semivar_share
- deceleration_6h
- path_consistency
- trend_close_location
- opposite_extreme_recency
- jump_concentration
- trend_to_range
- adverse_excursion
- v5_confidence
- gc_dlog_volume_1
- gc_volume_z20
- gc_volume_accel_5
- signed_opt_pressure
- signed_d_opt_pressure
- opt_total_z20

No p_rte, p_material, target, future path, or post-outcome state is used.

## 5. Model

- StandardScaler
- multinomial LogisticRegression
- L2
- C=0.50
- lbfgs
- no class weighting
- max_iter=3000
- seed=20261004
- monthly expanding-origin refit
- minimum 250 matured training origins
- training row admissible only if target_end_date_h3 <= first test-month feature cutoff

No hyperparameter search.

## 6. Natural reversal-governor policy

The model does **not** replace V5 globally.

For each origin:

If `v5_pred != momentum_up`:
- KEEP V5.

If `v5_pred == momentum_up`:
- FLIP V5 only when `mu_R > mu_C AND mu_R > mu_U`.
- otherwise KEEP V5.

Thus a reversal action requires REVERSAL_LAST to be the single most probable path state.

No numeric probability threshold is searched.

Secondary confidence semantics:
- if `mu_U` is largest: unresolved / possible future DAMP or ABSTAIN;
- no DAMP/ABSTAIN action is activated in V2.

## 7. Historical development replay

Monthly forward replay from the first month allowed by the 250-origin maturity rule through Sep-2026.

Historical 2026 is development/stress-test only.

Report:
- multiclass path-state log loss
- path-state accuracy
- terminal reversal rate by mu_R quintile
- FLIP count
- rescue / broken / net rescue
- FLIP precision
- candidate rate
- V5 accuracy vs V2-assisted accuracy
- block-level stability
- OPAL-no-candidate missed reversal hits

## 8. Development gate

V2 is development-promising only if all hold:

1. aggregate FLIP precision >= 0.55;
2. aggregate net rescue > 0;
3. FLIP candidate rate <= 0.25 of V5-continuation eligible origins;
4. assisted accuracy >= V5 accuracy + 0.005 on the same replay universe;
5. at least ceil(0.80 × available half-year blocks) have net rescue >= 0;
6. at least half of available blocks have net rescue > 0;
7. worst block net rescue >= -2;
8. top-vs-bottom mu_R quintile terminal-reversal separation >= 25 percentage points;
9. maturity leakage failures = 0.

If PASS:
`TRES_V2_PATH_GOVERNOR_PROMISING`

If FAIL:
`TRES_V2_PATH_GOVERNOR_FAIL`

## 9. Prospective governance

Even if development-promising:
- no historical result is a clean validation;
- V2 may only become a shadow challenger after a separate prospective freeze;
- HELIOS V5-DCE remains binding until prospective evidence.

No result may alter the barrier, class definition, features, model C, or argmax FLIP rule.
