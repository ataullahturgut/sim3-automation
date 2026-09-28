# GOLD MONTHLY FORECAST — CHALLENGER B / GPREG-MATERN V1 FREEZE

**Freeze date:** 2026-09-28
**Branch:** `gold-midas-headswap-v1-20260925`
**Status:** PRE-RUN METHOD FREEZE

## Provenance
Faithful Gold Monthly adaptation of the prior Grup-ARGE / GA111 GPR-Matérn implementation:
- X scaling: StandardScaler fit only on the corresponding training fold.
- Kernel = ConstantKernel(signal_scale, fixed) * Matern(length_scale, nu, fixed length scale).
- GaussianProcessRegressor(alpha=..., normalize_y=True, optimizer=None, random_state=42).

Exact prior Grup-ARGE grid preserved:
- length_scale: [0.5, 1.0, 2.0, 5.0]
- signal_scale: [1.0]
- alpha: [0.001, 0.01, 0.1]
- nu: [0.5, 1.5, 2.5]

## Gold Monthly contract
- Target: H=1 next-calendar-month average XAU/USD.
- Training target: next-month Gold log return.
- Price reconstruction: prior completed-month Gold average × exp(predicted Gold return).
- Representation: CURRENT8 only (Gold/Silver/Platinum/Palladium × MR/VW).
- Exact-origin GPR geopolitical-risk PIT vintage, p-1 publication lag, causal normalization.
- Training start: 2010-05.
- Random split: NONE.
- Outer evaluation: chronological expanding origin.
- Inner selection: last 12 eligible pre-target months.
- Objective: Gold cumulative absolute price error / Random-Walk cumulative absolute price error.
- Tie-break: lower objective, then lower length_scale, lower alpha, lower nu.
- Predictive std is diagnostic only.
- Target-month metal values are not dereferenced in outer feature construction.
- Target actual is read only after forecast for scoring.

## Period roles
- DEV 2022-04..2024-12 (n=33): sole selection authority.
- 2025: LOCKED_REPORT_ONLY.
- 2026-01..2026-07: QUARANTINED_REPORT_ONLY.

## Context-only frontier
- ChHHO-ANFIS: 1413.029779 / 23
- RBFNN DE-ABC: ~1415.8371 / 25
- PLS1 V1: 1420.0291314697745 / 20
- GPR/MOGP LMC2_RBF_M32: ~1424.17 / 19
- FULL7 Equal ANN: 1428.86 / 22
- REDUCED4 Equal ANN: 1431.46 / 24
- SVR parent: 1449.187363 / 19
- CatBoost PRICE: 1460.433935309605 / 20
- PLS2 V1: 1489.3300296660234 / 23
- Random Forest: 1491.550693715667 / 20
- Ridge V1: 1520.9926031249222 / 21
- Huber V1: 1530.1299616481554 / 20
- Elastic Net V1: 1590.3570524947138 / 16
- GPReg-RBF V1: 1696.3365035638303 / 16

## Governance
- DB READ_ONLY.
- Existing Gold Monthly / Challenger-A path unchanged.
- No metal ablation.
- 2025/2026 cannot promote, rescue, retune, or alter GPReg-Matérn V1.
