# GOLD MONTHLY FORECAST — CHALLENGER B / HISTGRADIENTBOOSTING V1 FREEZE

**Freeze date:** 2026-09-28
**Branch:** `gold-midas-headswap-v1-20260925`
**Status:** PRE-RUN METHOD FREEZE

## Provenance
Faithful adaptation of the actually executed Grup-ARGE HistGradientBoosting screening candidates:

1. HGB_A
   - learning_rate=0.05
   - max_iter=250
   - max_leaf_nodes=7
   - min_samples_leaf=12
   - l2_regularization=5.0

2. HGB_B
   - learning_rate=0.10
   - max_iter=150
   - max_leaf_nodes=7
   - min_samples_leaf=15
   - l2_regularization=10.0

Implementation: sklearn HistGradientBoostingRegressor.
For the Gold Monthly leakage-safe adaptation, **early_stopping=False** is binding. Hyperparameter selection is handled only by the explicit chronological inner validation; sklearn must not create its own internal holdout.

## Gold Monthly contract
- Business target: H=1 next-calendar-month average XAU/USD.
- Model target: next-month Gold log return.
- Price reconstruction: prior completed-month Gold average × exp(predicted Gold return).
- Representation: CURRENT8 only.
- Predictors: Gold/Silver/Platinum/Palladium × MR/VW.
- Tree-native input: no StandardScaler.
- GPR geopolitical-risk input inside VW remains exact-origin PIT, p-1 lagged, causal normalized.
- Training start: 2010-05.
- Random split: NONE.
- Outer evaluation: chronological expanding origin.
- Inner candidate selection: last 12 eligible pre-target months only.
- Objective: cumulative Gold price absolute error / Random-Walk cumulative absolute error.
- Tie-break: candidate order HGB_A then HGB_B.
- Actual target used only after forecast for scoring.
- Outer feature builder never dereferences target-month metal values.
- Primary metric: DEV SigmaAE.
- Secondary: direction, MAE, RMSE, MAPE, WAPE, relative MAE vs RW, worst month, yearly stability.
- No post-hoc feature selection or metal ablation.

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
- Extra Trees V1: 1539.9220718606994 / 20
- Elastic Net V1: 1590.3570524947138 / 16
- GPReg-Matérn V1: 1637.916541466211 / 19
- GPReg-RBF V1: 1696.3365035638303 / 16

## Governance
- DB READ_ONLY.
- Existing Gold Monthly / Challenger-A path unchanged.
- 2025/2026 cannot promote, rescue, retune or alter HGB V1.
