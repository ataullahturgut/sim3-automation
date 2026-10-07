# GOLD SESSION VEGA V1 — PREREGISTRATION

**Date:** 2026-10-07  
**Identity:** `SESSION_VEGA_V1`  
**Role:** Stage-2 GVZ/options-implied-volatility reversal specialist  
**Warm-up:** 2022 only  
**Development:** 2023-2024 only  
**2025:** not used for VEGA fitting or gate selection  
**2026:** unopened

## Target

VEGA is not a new primary direction engine.

It predicts:

`REVERSAL = 1[ actual session direction != sign(pre-target 12h XAU momentum) ]`.

## GVZ information-time contract

Source: governed official Cboe GVZ daily history `GOLD_GVZCLS_RAW_2021_2025.csv`.

For a session whose target start occurs on New York calendar date D, VEGA may use only GVZ observations dated **D-1 calendar day or earlier**.

No same-day GVZ value is permitted because same-day publication readiness has not been proven for every session head.

## Fixed feature set

1. `gvz_z252`
2. `gvz_r1`
3. `gvz_r3`
4. `gvz_r5`
5. `gvz_vs_med20`
6. `iv_rv24_gap`
7. `iv_rv48_gap`
8. `trend_strength`
9. `gvz_shock_x_trend`

XAU state uses the governed maintenance-aware exact-clock XAU15 representation at the session target start.

## Model

- StandardScaler
- LogisticRegression
- C = 1.0
- class_weight = balanced
- random_state = 20261007
- same-window monthly expanding causal refit
- minimum training rows = 80
- only matured labels before the test-month cutoff enter training

## Fixed correction rule

For each frozen Stage-1 upstream baseline separately:

- if baseline direction already opposes 12h XAU momentum: do not override;
- if baseline follows 12h momentum and `p_reversal >= 0.70`: flip;
- otherwise retain the baseline.

Threshold 0.70 is fixed before the run. No threshold search is allowed.

## Upstream baselines audited separately

- A0 CORE3
- A1 ARCR
- PATH_GLOBAL 1h
- canonical STRUCTURAL_IRIS A1+1h

VEGA does not choose among upstream baselines.

## Development pass rule per window/baseline

Eligible for later 2025 transport only if:

- 2023 accuracy >= baseline - 1 pp;
- 2024 accuracy >= baseline - 1 pp;
- 2023 Brier <= baseline + 0.003;
- 2024 Brier <= baseline + 0.003;
- combined 2023-2024 Balanced Accuracy >= baseline;
- combined net rescue > 0;
- corrected min(UP recall, DOWN recall) >= 30%.

No 2025 outcome may change the feature set, D-1 lag rule, threshold, model form or gate.
