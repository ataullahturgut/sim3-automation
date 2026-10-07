# SESSION RIFT — IDENTITY AUTHORITY

**Date:** 2026-10-07  
**Status:** COMPLETE / RIFT V1 BASELINE IDENTITY ACCEPTED / 2025 UNOPENED

## Role

RIFT is a **Stage-2 reversal/correction specialist**, not a new primary UP/DOWN engine.

It predicts:

`REVERSAL = 1[actual session direction != sign(pre-target 12h XAU momentum)]`

and may flip an upstream Stage-1 baseline only under the fixed correction rule.

## Binding RIFT V1 identity

Authority:
- `GOLD_SESSION_RIFT_V1_PREREG_2026-10-07.md`
- `GOLD_SESSION_RIFT_V1_SUMMARY_2026-10-07.json`
- `GOLD_SESSION_RIFT_V1_TRANSPORT_ELIGIBILITY_2026-10-07.csv`

Model:
- StandardScaler
- LogisticRegression(C=1.0, class_weight=balanced)
- fixed reversal threshold = 0.70
- minimum matured same-window training rows = 80
- same-window monthly expanding causal refit

Fixed correction rule:
1. if upstream baseline already opposes 12h momentum: do not override;
2. if baseline follows 12h momentum and `p_reversal >= 0.70`: flip;
3. otherwise keep baseline.

RIFT is not allowed to choose among upstream baselines.

## Origin-known feature identity

Nine fixed pre-target XAU15 features:
- trend_strength
- opposite_semivar_share
- deceleration_6h
- path_consistency
- trend_close_location
- opposite_extreme_recency
- jump_concentration_24
- trend_to_range
- adverse_excursion

Historical H3 `session_against_trend` is deliberately omitted because its old clock identity is not binding for the V5 session project.

## Clock / leakage gate

PASS.

- predictors are rebuilt from governed XAU/USD 15-minute data;
- exact-clock maintenance-aware feature helper is used;
- `g_anchor_available < target_start` is mandatory;
- maximum reference staleness <= 60 minutes;
- no target-window observation is used.

## Development chronology

- 2022 = warm-up only
- 2023–2024 = RIFT development and downstream correction gate
- 2025 = still unopened
- 2026 = unopened

## Upstream baseline identities

RIFT V1 audits correction value separately against:
- A0 CORE3
- A1 ARCR
- PATH_GLOBAL 1H
- canonical STRUCTURAL_IRIS A1+1H

These are existing governed session Stage-1 identities, not old DAILY/H3 models.

## Pre-2025 transport eligibility

Only one session window is eligible:

**SOBTI_5_ET / ASIA_AFTERNOON_LIT**

and it passes for all four upstream baselines.

### A0 CORE3
2023–2024:
- N = 210
- base BA = 46.03%
- RIFT BA = 47.51%
- base Brier = 0.2677
- RIFT Brier = 0.2650
- overrides = 5
- rescued = 4
- broken = 1
- net rescue = +3

### A1 ARCR
2023–2024:
- N = 190
- base BA = 46.25%
- RIFT BA = 47.89%
- base Brier = 0.2595
- RIFT Brier = 0.2564
- overrides = 5
- rescued = 4
- broken = 1
- net rescue = +3

### PATH_GLOBAL 1H
2023–2024:
- N = 175
- base BA = 45.79%
- RIFT BA = 47.99%
- base Brier = 0.2820
- RIFT Brier = 0.2754
- overrides = 4
- rescued = 4
- broken = 0
- net rescue = +4

### STRUCTURAL_IRIS A1+1H
2023–2024:
- N = 190
- base BA = 51.02%
- RIFT BA = 51.59%
- base Brier = 0.2908
- RIFT Brier = 0.2891
- overrides = 3
- rescued = 2
- broken = 1
- net rescue = +1

All other window/baseline pairs fail closed before 2025.

## Binding identity decision

1. RIFT V1 is a valid session-native reversal/correction specialist.
2. RIFT V1 is not a primary direction engine.
3. Only Sobti Asia Afternoon is eligible for eventual frozen 2025 transport.
4. 2025 has not yet been opened for RIFT.
5. Before opening 2025, a separate development-only RIFT variable-analysis challenger may test subsets of the nine fixed RIFT variables while preserving:
   - reversal target identity;
   - threshold 0.70;
   - correction rule;
   - upstream baseline separation.
6. Any feature-selected RIFT representation must be frozen using 2023–2024 only.
7. 2026 remains unopened.
