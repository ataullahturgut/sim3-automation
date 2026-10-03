# TRES-H3 V1 — STAGE 2 V5 ERROR-RISK META MODEL PREREGISTRATION

**Freeze date:** 2026-10-04  
**Identity:** `TRES_H3_V1_STAGE2`  
**Dependency:** Stage 1 = TRES_EVENT_SIGNAL_PASS  
**Status:** **FROZEN BEFORE STAGE-2 RESULTS**

## 1. Question

Within origins where HELIOS V5 follows the prevailing 12h momentum:

> does the Stage-1 competing-risk survival output add out-of-sample information about whether V5 will be wrong?

Target:

`error_target = rescue_target = 1[v5_pred != y_up]`

Eligible universe:

`eligible_v5_continuation == True`

## 2. Stacking governance

Stage-2 may use only **out-of-sample Stage-1 survival predictions**.

Stage-1 predictions begin in 2024 after their own expanding-history warm-up.

For every Stage-2 test month:
- training rows must be prior Stage-1 OOS predictions;
- each training row must have `target_end_date_h3 <= first feature_cutoff of the test month`;
- no in-sample survival fitted value may enter Stage 2.

Minimum matured eligible Stage-2 training rows:
- 120

Thus the first Stage-2 scored month is determined automatically.

## 3. Baseline error-risk model

Frozen baseline inputs:

- v5_confidence
- abs_h_ret_12
- trend_strength
- opposite_semivar_share
- deceleration_6h
- path_consistency
- adverse_excursion
- gc_volume_z20
- signed_opt_pressure
- signed_d_opt_pressure
- opt_total_z20

Model:
- StandardScaler
- LogisticRegression
- L2
- C=0.50
- lbfgs
- no class weighting
- max_iter=3000
- seed=20261004

## 4. Survival-augmented error-risk model

Same baseline inputs plus exactly four Stage-1 OOS survival summaries:

- F_reversal
- F_continuation
- hR1
- expected_event_day

No survival feature is selected after results.

The model specification is otherwise identical to baseline.

## 5. Evaluation

Monthly expanding-origin replay.

Primary metrics:
- ROC AUC for V5 error
- Brier
- log loss

Risk concentration:
- error rate in top vs bottom quintile of augmented p_error.

Block reporting:
- 2025 H1/H2
- 2026 H1/H2 as available after automatic warm-up

## 6. Incremental-information gate

Stage 2 PASS requires all:

1. aggregate augmented ROC AUC >= 0.62;
2. augmented ROC AUC >= baseline ROC AUC + 0.01;
3. augmented Brier < baseline Brier;
4. augmented log loss < baseline log loss;
5. augmented top-bottom error-rate separation >= 25 percentage points;
6. in at least ceil(0.75 × available half-year blocks), augmented AUC is not worse than baseline by more than 0.02;
7. in at least half of available blocks, augmented AUC > baseline AUC;
8. training-maturity leakage failures = 0.

No threshold for intervention is selected here.

If PASS:
`TRES_ERROR_RISK_PASS`

If FAIL:
`NO_INCREMENTAL_TRES_ERROR_RISK`

## 7. Secondary diagnostics

Report:
- coefficients of the four survival features by monthly refit;
- p_error calibration by quintile;
- correlation between F_reversal and p_error_aug;
- error rate conditional on high F_reversal but low p_error and vice versa.

These diagnostics do not change the gate.

## 8. Governance

Stage 2 is an information test only.

A PASS authorizes Stage 3 fuzzy/neutrosophic confidence-governor design.

No FLIP/DAMP/ABSTAIN rule is permitted before Stage 3 is separately preregistered.
