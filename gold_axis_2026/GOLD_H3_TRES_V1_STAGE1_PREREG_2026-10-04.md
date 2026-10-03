# TRES-H3 V1 — STAGE 1 DISCRETE COMPETING-RISK MODEL PREREGISTRATION

**Freeze date:** 2026-10-04  
**Identity:** `TRES_H3_V1_STAGE1`  
**Stage-0 dependency:** PASS required and satisfied  
**Status:** **FROZEN BEFORE STAGE-1 MODEL RESULTS**

## 1. Target

Primary label is the Stage-0 first-passage process using the fixed 1.00×sigma20 barrier.

For each origin create person-period rows for h ∈ {1,2,3} until the first event:

- class 0 = NO_EVENT_YET at h
- class 1 = CONTINUATION first passage at h
- class 2 = REVERSAL first passage at h

If an event occurs at day h, no later person-period rows exist for that origin.

Censored origins contribute class 0 at h=1,2,3.

## 2. Predictor information

Only origin-available state is allowed.

Frozen market/path features:
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

Frozen V5 state:
- v5_confidence

Frozen CME participation / Gold option-pressure features:
- gc_dlog_volume_1
- gc_volume_z20
- gc_volume_accel_5
- signed_opt_pressure
- signed_d_opt_pressure
- opt_total_z20

Time basis:
- day2 indicator
- day3 indicator

No p_rte, p_material, future path, target_r3, y_up, rescue_target or counterfactual-gap feature is used in the Stage-1 competing-risk model.

## 3. Model

Low-capacity multinomial discrete-time hazard model:

- StandardScaler on continuous features
- LogisticRegression
- multinomial likelihood
- L2 regularization
- C = 0.50
- solver = lbfgs
- no class weighting
- max_iter = 3000
- seed = 20261004

No hyperparameter search.

## 4. Chronology

Monthly expanding-origin replay.

A training origin is admissible for a test month only when:

`target_end_date_h3 <= first feature_cutoff_date of test month`

Minimum matured training origins:
- 250

First scored month is therefore determined automatically by maturity, not manually.

## 5. Prediction

For each test origin predict three conditional step probabilities:

`p0_h, pC_h, pR_h`

where p0 is no event at h conditional on survival to h.

Cumulative incidence:

`S_0 = 1`

`F_R = sum_h S_{h-1} * pR_h`

`F_C = sum_h S_{h-1} * pC_h`

`S_h = S_{h-1} * p0_h`

Identity must hold:

`F_R + F_C + S_3 = 1`

within 1e-10.

Additional outputs:
- expected event day conditional on event
- Day-1 reversal hazard
- Day-2 reversal hazard
- Day-3 reversal hazard

## 6. Stage-1 information gate

Historical replay is development evidence.

For each half-year block available from 2024 onward:

### First-passage discrimination
Compare top vs bottom quintile of `F_R`:
- actual primary first-passage REVERSAL rate.

### Terminal reversal transfer
Using the existing H3 terminal reversal label only for diagnosis:
- compare terminal reversal rate in top vs bottom quintile of `F_R`.

Stage-1 is information-positive only if all hold:

1. aggregate top-bottom first-passage reversal-rate separation >= 20 percentage points;
2. at least 4 of 5 available half-year blocks have positive first-passage separation;
3. aggregate top-bottom terminal-reversal separation >= 10 percentage points;
4. at least 4 of 5 blocks have non-negative terminal-reversal separation;
5. cumulative-incidence identity failures = 0;
6. training-maturity leakage failures = 0.

If the number of scored half-year blocks differs from 5 because of automatic warm-up, apply the count rule as:
- at least ceil(0.8 × available blocks).

If Stage 1 fails:
`NO_TRES_EVENT_SIGNAL`
and Stage 2 error-risk modeling is not authorized.

## 7. Evaluation metrics

Also report:
- multiclass first-event log loss for {CENSORED, CONTINUATION, REVERSAL} using {S3, F_C, F_R};
- Brier for first-passage REVERSAL;
- annual/half-year event calibration;
- terminal reversal rate by F_R quintile;
- V5 wrong rate by F_R quintile in V5-continuation eligible origins.

These secondary metrics do not alter the gate.

## 8. Governance

No threshold for FLIP / DAMP / ABSTAIN is selected in Stage 1.

Stage 1 answers only:
> does origin-time state contain a transportable signal about the timing and type of the next H3 directional first-passage event?

Only a PASS authorizes Stage 2.
