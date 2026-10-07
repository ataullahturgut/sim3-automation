# GOLD SESSION RIFT V1 — PREREGISTRATION

**Date:** 2026-10-07  
**Identity:** `SESSION_RIFT_V1`  
**Role:** Stage-2 specialist reversal/correction layer  
**Upstream:** fresh governed Stage-1 predictions only  
**Development:** 2023-2024 only  
**Warm-up:** 2022 only  
**2025:** closed until this RIFT representation is frozen  
**2026:** unopened

## Target

RIFT does not predict session UP/DOWN as a new primary engine.

It predicts:

`REVERSAL = 1[ actual session direction != sign(pre-target 12h XAU momentum) ]`.

## Fixed origin-known feature set

Built from governed XAU/USD 15-minute data with the existing strict pre-target / maintenance-aware exact-clock contract:

1. `trend_strength = abs(ret_12h)/(rv_12+eps)`
2. `opposite_semivar_share`
3. `deceleration_6h`
4. `path_consistency`
5. `trend_close_location`
6. `opposite_extreme_recency`
7. `jump_concentration_24`
8. `trend_to_range`
9. `adverse_excursion`

The old H3 `session_against_trend` feature is deliberately omitted because its historical session-return clock is not binding in the current session project. No replacement feature is searched.

## Model

- StandardScaler
- LogisticRegression
- C = 1.0
- class_weight = balanced
- random_state = 20261007
- same-window monthly expanding causal refit
- only matured labels before the test-month cutoff enter training
- minimum training rows = 80

## Fixed correction rule

For each upstream Stage-1 baseline separately:

- if baseline direction already opposes 12h momentum: do not override;
- if baseline follows 12h momentum and `p_reversal >= 0.70`: flip;
- otherwise keep the baseline.

No threshold search is permitted.

## Upstream baselines audited separately

- A0 CORE3
- A1 ARCR
- PATH_GLOBAL 1h
- canonical STRUCTURAL_IRIS A1+1h

RIFT is not allowed to choose among these baselines. It only measures correction value relative to each one on exact matched rows.

## Development pass rule per window/baseline

A window/baseline pair is eligible for later 2025 transport only if:

- 2023 accuracy >= baseline accuracy - 1 pp;
- 2024 accuracy >= baseline accuracy - 1 pp;
- 2023 Brier <= baseline Brier + 0.003;
- 2024 Brier <= baseline Brier + 0.003;
- combined 2023-2024 Balanced Accuracy >= baseline;
- combined net rescue > 0;
- corrected model satisfies min(UP recall, DOWN recall) >= 30%.

No 2025 outcome may alter the feature set, threshold, model form, or pass rule.
