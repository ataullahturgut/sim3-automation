# SESSION VEGA — FINAL AUTHORITY

**Date:** 2026-10-07  
**Status:** COMPLETE / NOT PROMOTED

## Role

VEGA is a Stage-2 GVZ/options-implied-volatility reversal specialist. It is not a primary direction engine.

## Canonical identity

Authority:
- `GOLD_SESSION_VEGA_IDENTITY_AUTHORITY_2026-10-07.md`

Model:
- StandardScaler
- LogisticRegression(C=1.0, class_weight=balanced)
- fixed reversal threshold = 0.70
- same-window monthly expanding causal refit
- minimum matured training rows = 80

Canonical features:
- gvz_z252
- gvz_r1
- gvz_r3
- gvz_r5
- gvz_vs_med20
- iv_rv24_gap
- iv_rv48_gap
- trend_strength
- gvz_shock_x_trend

Information-time contract:
- GVZ <= New York origin date D-1 calendar day
- exact-clock pre-target XAU15 state only
- no target-window information

## Development gate

Only one canonical pair passed the frozen 2023-2024 gate:

**WGC_2026_NY3 / US / PATH_GLOBAL_1H**

Combined development:
- N = 162
- baseline BA = 46.28%
- VEGA BA = 46.88%
- baseline Brier = 0.2816
- VEGA Brier = 0.2798
- overrides = 1
- rescued = 1
- broken = 0
- net rescue = +1

The development correction activity was therefore extremely sparse.

## Variable-selection challenger

Authority:
- `GOLD_SESSION_VEGA_V1B_VARIABLE_SELECTION_PREREG_2026-10-07.md`
- `GOLD_SESSION_VEGA_V1B_VARSEL_RESULT_2026-10-07.md`
- `GOLD_SESSION_VEGA_V1B_VARSEL_TRANSPORT_ELIGIBILITY_2026-10-07.csv`

Development-only feature selection was performed inside the canonical VEGA feature family.

Result:
- no selected VEGA session/baseline pair passed the frozen pre-2025 transport gate;
- therefore selected VEGA 2025 remained closed.

## Frozen 2025 canonical transport

Authority:
- `GOLD_SESSION_VEGA_FROZEN_2025_TRANSPORT_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_VEGA_FROZEN_2025_TRANSPORT_RESULT_2026-10-07.md`

Eligible pair:
**WGC US + PATH_GLOBAL_1H**

2025:
- N = 140
- baseline accuracy = 47.14%
- corrected accuracy = 47.14%
- baseline Balanced Accuracy = 49.38%
- corrected Balanced Accuracy = 49.38%
- baseline Brier = 0.2825
- corrected Brier = 0.2825
- corrected UP recall = 37.35%
- corrected DOWN recall = 61.40%
- overrides = 0
- rescues = 0
- breaks = 0
- net rescue = 0

## Binding decision

1. VEGA identity is valid and clock-safe.
2. Canonical VEGA is **not promoted** after frozen 2025 transport.
3. Development eligibility did not transport into actual correction activity: VEGA made zero 2025 overrides.
4. Feature-selected VEGA is also not promoted; it failed the pre-2025 gate entirely.
5. VEGA may remain only as negative/diagnostic specialist evidence.
6. No 2025 retuning or rescue was performed.
7. 2026 remains unopened.
8. Next specialist in the binding execution order: **OPAL**.
