# SESSION VEGA — IDENTITY AUTHORITY

**Date:** 2026-10-07  
**Status:** COMPLETE / VEGA V1 BASELINE IDENTITY ACCEPTED / 2025 UNOPENED

## Role

VEGA is a Stage-2 GVZ/options-implied-volatility reversal specialist. It is not a new primary UP/DOWN engine.

Target:
`REVERSAL = 1[actual session direction != sign(pre-target 12h XAU momentum)]`

## Binding VEGA V1 identity

Authorities:
- `GOLD_SESSION_VEGA_V1_PREREG_2026-10-07.md`
- `GOLD_SESSION_VEGA_V1_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_VEGA_V1_TRANSPORT_ELIGIBILITY_2026-10-07.csv`

Model:
- StandardScaler
- LogisticRegression(C=1.0, class_weight=balanced)
- fixed reversal threshold = 0.70
- same-window monthly expanding causal refit
- minimum matured training rows = 80

Correction rule is identical to RIFT:
- if baseline already opposes 12h momentum: keep;
- if baseline follows momentum and p_reversal >= 0.70: flip;
- otherwise keep.

## Information-time contract

GVZ source:
`GOLD_GVZCLS_RAW_2021_2025.csv`

For a session with New York origin date D:
- VEGA may use only GVZ observations dated <= D-1 calendar day;
- same-day GVZ is prohibited.

XAU state:
- governed exact-clock maintenance-aware XAU15;
- pre-target only;
- no target-window observation.

## Fixed feature identity

Nine canonical VEGA features:
- gvz_z252
- gvz_r1
- gvz_r3
- gvz_r5
- gvz_vs_med20
- iv_rv24_gap
- iv_rv48_gap
- trend_strength
- gvz_shock_x_trend

## Chronology

- 2022 = warm-up only
- 2023–2024 = development
- 2025 = unopened
- 2026 = unopened

## Pre-2025 transport eligibility

Only:

**WGC_2026_NY3 / US / PATH_GLOBAL_1H**

passes.

### 2023
- N = 20
- base accuracy = 50.00%
- VEGA accuracy = 55.00%
- base BA = 47.47%
- VEGA BA = 53.03%
- base Brier = 0.2769
- VEGA Brier = 0.2616
- overrides = 1
- rescued = 1
- broken = 0
- net rescue = +1

### 2024
- N = 142
- no override
- base and VEGA BA = 45.59%
- base and VEGA Brier = 0.2823

### Combined 2023–2024
- N = 162
- base BA = 46.28%
- VEGA BA = 46.88%
- base Brier = 0.2816
- VEGA Brier = 0.2798
- overrides = 1
- rescued = 1
- broken = 0
- net rescue = +1

All other window/baseline pairs fail closed before 2025.

## Binding identity decision

1. VEGA V1 is a valid session-native GVZ reversal specialist.
2. VEGA is not a primary direction engine.
3. Only WGC US / PATH_GLOBAL 1H is eligible for eventual frozen 2025 transport.
4. Development evidence is extremely sparse in actual correction activity: one changed call across the combined eligible development population.
5. Before opening 2025, a development-only feature-analysis challenger may test subsets of the nine canonical VEGA variables while preserving D-1 GVZ, threshold 0.70, reversal target and correction rule.
6. 2026 remains unopened.
