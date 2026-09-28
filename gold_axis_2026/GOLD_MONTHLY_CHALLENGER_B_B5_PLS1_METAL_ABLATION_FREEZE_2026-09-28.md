# GOLD MONTHLY FORECAST — CHALLENGER B / B5 PLS1 METAL ABLATION FREEZE

**Freeze date:** 2026-09-28
**Branch:** `gold-midas-headswap-v1-20260925`
**Status:** PRE-RUN METHOD FREEZE

## Purpose
Measure whether the four-metal CURRENT8 representation used by PLS1 is improved or degraded when cross-metal blocks are removed. This is a DEV-only feature-set experiment. 2025/2026 are report-only and cannot determine the chosen metal set.

## Frozen variants
Feature order in CURRENT8 is:
0 Gold_MR, 1 Gold_VW, 2 Silver_MR, 3 Silver_VW, 4 Platinum_MR, 5 Platinum_VW, 6 Palladium_MR, 7 Palladium_VW.

- M0_GOLD_ONLY: [Gold] = indices [0,1]
- M1_GOLD_SILVER: [Gold, Silver] = [0,1,2,3]
- M2_ALL4_REFERENCE: [Gold, Silver, Platinum, Palladium] = [0..7]
- M3_NO_SILVER: [Gold, Platinum, Palladium] = [0,1,4,5,6,7]
- M4_NO_PLATINUM: [Gold, Silver, Palladium] = [0,1,2,3,6,7]
- M5_NO_PALLADIUM: [Gold, Silver, Platinum] = [0,1,2,3,4,5]

No other subset may be added after results are seen.

## Model contract
- Estimator: sklearn PLSRegression(scale=True), single-target Gold next-month log return.
- Business target: H=1 next-calendar-month average XAU/USD.
- Price reconstruction: previous completed-month Gold average × exp(predicted Gold return).
- Training start: 2010-05.
- Random split: NONE.
- Expanding outer origin.
- Per variant and per origin, n_components grid = 1..number_of_features_in_variant.
- Component selection uses only last 12 eligible pre-target months.
- Inner objective = cumulative Gold price AE / Random-Walk cumulative Gold price AE.
- Tie-break = lower objective, then fewer components.
- PLS internal scaling is fit only on each training fold.
- Outer feature construction never dereferences target-month metal values.
- Target actual is read only after forecast for scoring.

## Selection rule
The ablation comparison itself is allowed to use DEV 2022-04..2024-12 because DEV is the development/selection authority.
- Primary ordering: DEV SigmaAE ascending.
- Secondary interpretation: DEV direction count.
- Pareto dominance is reported across the six variants.
- 2025 and 2026 cannot rescue, select, or alter a metal set.

## Reproduction gate
M2_ALL4_REFERENCE must reproduce the frozen PLS1 V1 DEV result within numerical tolerance:
- SigmaAE = 1420.0291314697745
- direction = 20/33

If it does not, the ablation is invalid and must not be interpreted.

## Period roles
- DEV: 2022-04..2024-12 (n=33), sole metal-set selection authority.
- 2025: LOCKED_REPORT_ONLY.
- 2026-01..2026-07: QUARANTINED_REPORT_ONLY.

## Governance
- DB READ_ONLY.
- CURRENT8 feature definitions unchanged.
- No new raw metal levels are introduced.
- Existing Challenger-A/main path unchanged.
