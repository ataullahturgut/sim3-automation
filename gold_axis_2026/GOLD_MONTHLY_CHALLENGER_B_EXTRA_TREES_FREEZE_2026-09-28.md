# GOLD MONTHLY FORECAST — CHALLENGER B / EXTRA TREES V1 FREEZE

**Freeze date:** 2026-09-28
**Branch:** `gold-midas-headswap-v1-20260925`
**Status:** PRE-RUN METHOD FREEZE

## Provenance
Faithful adaptation of the actually executed Grup-ARGE Extra Trees screening protocol.

Historical executed candidates:
1. n_estimators=300, max_depth=3, min_samples_leaf=3, max_features=0.7
2. n_estimators=300, max_depth=None, min_samples_leaf=5, max_features=1.0

The wider theoretical screening grid is NOT used here because the goal is to port the actually executed Grup-ARGE challenger, not redesign it post hoc.

## Gold Monthly contract
- Business target: H=1 next-calendar-month average XAU/USD.
- Model target: next-month Gold log return.
- Price reconstruction: prior completed-month Gold average × exp(predicted Gold return).
- Representation: CURRENT8 only.
- Predictors: Gold/Silver/Platinum/Palladium × MR/VW = 8 frozen origin-safe features.
- No StandardScaler or other scaling: tree models receive the frozen engineered CURRENT8 features directly.
- GPR geopolitical-risk input remains exact-origin PIT, p-1 lagged and causally normalized inside VW construction.
- Training start: 2010-05.
- Random split: NONE.
- Outer evaluation: chronological expanding origin.
- Inner candidate selection: last 12 eligible pre-target months only.
- Inner objective: cumulative Gold price absolute error / Random-Walk cumulative absolute error.
- Tie-break: candidate order shown above.
- Estimator: sklearn ExtraTreesRegressor(random_state=42, n_jobs=1).
- Outer feature builder does not dereference target-month metal values.
- Actual target used only after forecast for scoring.
- Primary metric: DEV SigmaAE.
- Secondary: direction accuracy, MAE, RMSE, MAPE, WAPE, relative MAE vs RW, worst month, yearly stability.
- Diagnostics: feature importances and chosen-candidate counts only.

## Period roles
- DEV 2022-04..2024-12 (n=33): sole selection authority.
- 2025: LOCKED_REPORT_ONLY.
- 2026-01..2026-07: QUARANTINED_REPORT_ONLY.

## Frozen context-only comparison pool
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
- GPReg-Matérn V1: 1637.916541466211 / 19
- GPReg-RBF V1: 1696.3365035638303 / 16

## Governance
- DB READ_ONLY.
- Existing Gold Monthly / Challenger-A path unchanged.
- No metal ablation in Extra Trees V1.
- 2025/2026 cannot promote, rescue, retune or alter the model.
