# CHANGEPOINT-H3 V1 — PREREGISTRATION

**Date:** 2026-10-03  
**Identity:** `CHANGEPOINT_H3_V1`  
**Branch:** `gold-h3-changepoint-v1-20261003`  
**Role:** momentum-structure break / reversal-candidate specialist.  
**Status:** **PREREGISTERED BEFORE MODEL FIT**

## 1. Purpose

CHANGEPOINT-H3 asks a different question from HAZARD-H3.

HAZARD-H3 tested whether the current trend state is old/exhausted.

CHANGEPOINT-H3 tests:

> Is the observed intraday path state **changing against the current 12h momentum now**, relative to the immediately preceding H3 origins?

Target:
`reversal_target = 1[y_up != momentum_up]`

Operational candidate universe:
`aurora_follows_momentum == True`.

It is not a general UP/DOWN model and does not replace AURORA, OPAL or HELIOS V5-DCE.

## 2. Frozen source

Only:
`GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv`

No new external data source, source-lag search, or 2026 outcome inspection is required.

The panel contains only origin-safe path state already admitted into the clean H3 lineage.

## 3. Frozen state variables

Underlying path states:
- trend_strength
- opposite_semivar_share
- deceleration_6h
- session_against_trend
- path_consistency
- trend_close_location
- jump_concentration
- adverse_excursion

For each variable `x` in chronological feature-cutoff order:
- `dx_1 = x_t - x_(t-1)`
- selected second differences `ddx_1 = dx_t - dx_(t-1)`

No future row may enter any difference.

## 4. Frozen break-direction mapping

All first differences are converted so **positive means weakening of the current momentum state**:

- `weak_trend_strength = -d_trend_strength_1`
- `weak_opposite_semivar = +d_opposite_semivar_share_1`
- `weak_deceleration = +d_deceleration_6h_1`
- `weak_session = +d_session_against_trend_1`
- `weak_path_consistency = -d_path_consistency_1`
- `weak_close_location = -d_trend_close_location_1`
- `weak_adverse_excursion = +d_adverse_excursion_1`
- `weak_jump = +d_jump_concentration_1`

Each weakening innovation is additionally standardized against its **preceding 60 available origin innovations**, using rolling mean/std shifted by one origin.

This creates eight `*_z60` features with no current/future contamination.

## 5. Frozen local change-point summaries

Composite:
- `weakening_impulse = mean(8 weakening z60 values)`

Persistence:
- `weakening_cusum_3 = sum(max(weakening_impulse,0)) over current + previous 2 origins`
- `weakening_cusum_5 = sum(max(weakening_impulse,0)) over current + previous 4 origins`
- `weakening_share_5 = fraction of last 5 origins where weakening_impulse > 0`

Acceleration:
- `dd_deceleration_1`
- `dd_path_consistency_1`
- `dd_adverse_excursion_1`

The second-difference signs are not hand-flipped after results; the logistic model learns them.

## 6. Frozen feature set

1. weak_trend_strength_z60
2. weak_opposite_semivar_z60
3. weak_deceleration_z60
4. weak_session_z60
5. weak_path_consistency_z60
6. weak_close_location_z60
7. weak_adverse_excursion_z60
8. weak_jump_z60
9. weakening_impulse
10. weakening_cusum_3
11. weakening_cusum_5
12. weakening_share_5
13. dd_deceleration_1
14. dd_path_consistency_1
15. dd_adverse_excursion_1

No post-result feature search is allowed in V1.

## 7. Model

- StandardScaler
- LogisticRegression
- C=1.0
- solver=lbfgs
- class_weight=balanced
- seed=20261003
- monthly expanding-origin refit
- minimum matured training rows=80

Training rows for a monthly refit must satisfy:
`target_end_date_h3 <= current month first feature cutoff`.

## 8. Period roles

- DEV / threshold selection: 2023-01-01 through 2024-12-31
- confirmation: 2025 only
- final holdout: 2026 only after confirmation PASS

2026 may not choose features, signs, windows, model, threshold, or gate.

## 9. Candidate threshold selection

Frozen grid:
`[0.35, 0.40, 0.45, 0.50, 0.55, 0.60]`

Use only DEV rows with `aurora_follows_momentum=True`.

Objective:
- maximize reversal F2.

Eligibility:
- candidate precision >= 0.45
- candidate rate <= 0.40

Tie-break:
1. higher reversal recall
2. higher precision
3. lower candidate rate
4. higher threshold

No eligible threshold =>
`NO_ELIGIBLE_CHANGEPOINT_THRESHOLD`.

## 10. 2025 confirmation gate

All must pass:
1. CHANGEPOINT reversal recall > OPAL candidate recall on the same eligible universe.
2. CHANGEPOINT nominates >=1 true reversal where OPAL candidate is false.
3. CHANGEPOINT candidate precision >=0.40.
4. OPAL union CHANGEPOINT reversal recall > OPAL recall.

Failure => formal 2026 holdout remains unopened.

## 11. 2026 final holdout

Only after confirmation PASS:
- reversal recall
- precision
- candidate rate
- OPAL overlap
- CHANGEPOINT-only true reversals
- OPAL-union-CHANGEPOINT recall
- number of V5-missed / OPAL-no-candidate reversals nominated
- diagnostic forced-flip rescue/broken/net

No HELIOS router promotion occurs from this specialist result alone.

## 12. Governance

CHANGEPOINT-H3 is a new independent specialist and is not a renamed HAZARD model.

Its distinction is explicit:
- HAZARD used state levels, age, switching history and duration interactions;
- CHANGEPOINT uses **innovations, standardized adverse changes, persistence and acceleration of path deterioration**.

FLOW/SKEW access blocks and prior failed DEV challengers are not altered.
