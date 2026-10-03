# ARVE-H3 V1 — ADAPTIVE RESCUE VALUE ENGINE DEVELOPMENT CONTRACT

**Freeze-development date:** 2026-10-04  
**Identity:** `ARVE_H3_V1`  
**Branch:** `gold-h3-arve-v1-20261004`  
**Scientific status:** historical 2026 is development only; first clean claim must be post-freeze prospective.

## 1. Core reformulation

Prior systems followed:

`reversal signal -> candidate -> router -> flip V5`.

This creates a candidate ceiling and repeatedly forces heterogeneous reversal states into the same alarm class.

ARVE removes the candidate layer.

Within the exact V5-continuation universe:
- keep action utility = +1 if V5 is correct, -1 if V5 is wrong;
- flip action utility = +1 if V5 is wrong, -1 if V5 is correct.

Because the forecast is binary UP/DOWN, the flip counterfactual is observed deterministically.

Define:
`rescue_value_target = 1[v5_pred != y_up]`.

ARVE estimates:
`P(flip has positive utility | current market state, current V5 state, recent matured V5 health)`.

It may propose a flip even when OPAL/RTE specialists produced no candidate.

## 2. Frozen base feature family

### Current market / model state
- v5_confidence
- abs_h_ret_12
- trend_strength
- opposite_semivar_share
- deceleration_6h
- path_consistency
- adverse_excursion
- gc_volume_z20
- gc_volume_accel_5
- signed_opt_pressure
- signed_d_opt_pressure
- opt_total_z20
- p_rte
- p_inst

### Origin-safe model-health state

For every origin, using only earlier rows whose H3 target has already matured by the current feature cutoff:

- `health_error_20`: V5 error rate over most recent 20 eligible matured origins
- `health_error_60`: same over most recent 60
- `health_same_momentum_20`: error rate over most recent 20 matured origins with the same momentum direction
- `health_large_error_20`: rate of V5 errors with |H3 return| >=1% over most recent 20
- `health_mean_abs_move_20`: mean |H3 return| over most recent 20
- `health_since_last_error`: number of eligible matured origins since the most recent V5 error, clipped at 20

No current or future target enters these features.

## 3. Estimator

Low-capacity direct intervention-value model:
- StandardScaler
- LogisticRegression
- C = 0.5
- no random split
- monthly expanding-origin refit

Nonstationarity adaptation:
- training sample weight decays exponentially by age;
- candidate half-lives are limited to **[90, 180, 360] calendar days**.

Uncertainty:
- **21 monthly-block bootstrap** logistic models per monthly refit;
- deterministic seeds 20261004..20261024;
- candidate probability = ensemble mean;
- conservative probability = ensemble 20th percentile.

## 4. Action policy development family

A flip is accepted only if:
- ensemble 20th percentile > 0.50;
- ensemble mean >= mean floor.

Frozen mean-floor grid:
- **[0.58, 0.62, 0.66]**

Thus there are exactly 9 development configurations:
3 half-lives × 3 mean floors.

No other feature, threshold, C, quantile or bootstrap count is searched.

## 5. Historical development replay

All historical replay is retrospective development evidence.

Forward blocks:
- 2024 H2
- 2025 H1
- 2025 H2
- 2026 H1
- 2026 H2 through available September history

Each monthly prediction is generated from a model fit only on matured prior rows.

Metrics:
- flips
- rescue / broken / net
- rescue precision
- V5 vs ARVE-assisted accuracy
- block stability
- coverage of V5 missed reversal / OPAL-no-candidate states

## 6. Development configuration selection

A configuration is eligible if:
- accepted flips >= 12
- aggregate net rescue >= +5
- rescue precision >= 0.60
- at least 3 of 5 half-year blocks have net rescue > 0
- no block net < -2

Selection:
1. highest aggregate net rescue
2. higher rescue precision
3. more rescued
4. fewer flips
5. longer half-life
6. higher mean floor

If no configuration passes:
`NO_ELIGIBLE_ARVE_V1_POLICY`.

## 7. Prospective freeze

If a configuration passes, it is frozen on 2026-10-04 for the first clean origin on/after 2026-10-05.

Promotion cannot occur from retrospective replay.

Prospective promotion evidence requires:
- at least 20 accepted flips AND
- at least 6 calendar months,
with cumulative net rescue >0 and rescue precision >=0.60.

Safety:
- cumulative prospective net rescue <= -3 => fail-closed shadow mode pending a new version.

## 8. Governance

- Historical 2026 is development, not validation.
- No post-freeze prospective outcome may alter features, half-life, mean floor, C, bootstrap scheme or action rule under V1.
- HELIOS V5-DCE remains champion/binding until separately promoted.
