# HAZARD-H3 V1 — PREREGISTRATION

**Date:** 2026-10-03  
**Identity:** `HAZARD_H3_V1`  
**Branch:** `gold-h3-hazard-v1-20261003`  
**Role:** duration-dependent momentum-termination / reversal candidate specialist.

## 1. Purpose

Estimate the conditional probability that the current 12-hour momentum state terminates within the H3 target horizon.

Target:
`reversal_target = 1[y_up != momentum_up]`

Operational candidate universe:
`aurora_follows_momentum == True`.

HAZARD-H3 does not replace AURORA or HELIOS V5-DCE and does not directly route a trade in V1.

## 2. Research motivation

The architecture is intentionally duration-dependent:
- state age can alter the hazard that a bull/bear/trend regime terminates;
- run length and recent switching frequency can contain reversal information;
- very strong trends may exhibit nonlinear reversion behavior.

Therefore HAZARD-H3 adds state-duration information that the existing RIFT feature set does not explicitly encode.

## 3. Frozen input authority

Base panel:
`GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv`

Only origin-safe fields already frozen in the clean H3 lineage are used.

No new external data source is required.

## 4. Frozen feature construction

For each origin in chronological order:

### Duration state
1. `trend_age`: consecutive eligible origin observations with the same `momentum_up`, including current origin.
2. `log_trend_age = log1p(trend_age)`
3. `trend_age_sq = min(trend_age,20)^2 / 400`

### Recent regime instability
4. `switches_10`: number of momentum-sign changes over the preceding 10 origin transitions.
5. `switches_20`: number of momentum-sign changes over the preceding 20 origin transitions.

### Nonlinear trend state
6. `trend_strength`
7. `trend_strength_sq = min(trend_strength,5)^2`
8. `trend_strength_cu = min(trend_strength,5)^3`

### Exhaustion / adverse-path state
9. `deceleration_6h`
10. `session_against_trend`
11. `opposite_semivar_share`
12. `distance_from_trend_extreme = 1 - trend_close_location`
13. `adverse_excursion`
14. `jump_concentration`

### Duration interactions
15. `age_x_deceleration = log_trend_age * deceleration_6h`
16. `age_x_opposite_semivar = log_trend_age * opposite_semivar_share`
17. `age_x_adverse_excursion = log_trend_age * adverse_excursion`

No feature search is allowed after 2026 outcomes are inspected.

## 5. Model

Discrete-time hazard classifier:
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

## 6. Period roles

- DEV / threshold selection: 2023-01-01 through 2024-12-31
- confirmation: 2025-01-01 through 2025-12-31
- final holdout: 2026 only after confirmation PASS

2026 may not choose features, interactions, model family, threshold, or gates.

## 7. Candidate threshold selection

Frozen threshold grid:
`[0.35, 0.40, 0.45, 0.50, 0.55, 0.60]`

Use only DEV origins where AURORA follows momentum.

Primary objective:
- maximize reversal F2.

Eligibility:
- candidate precision >= 0.45
- candidate rate <= 0.40

Tie-break:
1. higher reversal recall
2. higher precision
3. lower candidate rate
4. higher threshold

No eligible threshold => `NO_ELIGIBLE_HAZARD_THRESHOLD`.

## 8. 2025 confirmation gate

All required:
1. HAZARD reversal recall > OPAL candidate recall on the same eligible universe.
2. HAZARD finds >=1 true reversal where OPAL candidate is false.
3. HAZARD candidate precision >=0.40.
4. Candidate-union recall `OPAL ∪ HAZARD` is strictly greater than OPAL recall.

Failure => 2026 formal holdout remains unopened.

## 9. 2026 final holdout

Only after 2025 PASS:
- reversal recall
- precision
- candidate rate
- FLOW? none: this is HAZARD-only comparison against OPAL
- OPAL overlap
- HAZARD-only true reversal count
- OPAL ∪ HAZARD recall
- count of V5-missed + OPAL-no-candidate reversals nominated by HAZARD
- diagnostic forced-flip rescue / broken / net relative to V5

No HELIOS routing rule is promoted from this stage.

## 10. Governance

HAZARD-H3 is an independent challenger.
It does not alter:
- FLOW-H3 blocked contract
- SKEW-H3 blocked contract
- OPAL
- HELIOS V1-V5
- CLEAN_H3_PROSPECTIVE_V1.

Any later union/router work occurs only after this specialist is frozen and scored.
