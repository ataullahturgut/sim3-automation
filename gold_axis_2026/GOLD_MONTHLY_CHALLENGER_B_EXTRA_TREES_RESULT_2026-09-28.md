# GOLD MONTHLY FORECAST — CHALLENGER B / EXTRA TREES V1 RESULT

**Date:** 2026-09-28
**Status:** COMPLETE / SCIENTIFIC GATE PASS / NOT PROMOTED
**Workflow run:** 36435162378
**Commit:** 0a6d97bdb803981fb6eccae08348aabc01337bfd
**Freeze:** `GOLD_MONTHLY_CHALLENGER_B_EXTRA_TREES_FREEZE_2026-09-28.md`

## Provenance
This run ports the actually executed Grup-ARGE Extra Trees protocol, not a redesigned post-hoc grid.

Candidates:
- ET_A: n_estimators=300, max_depth=3, min_samples_leaf=3, max_features=0.7
- ET_B: n_estimators=300, max_depth=None, min_samples_leaf=5, max_features=1.0

Estimator: sklearn ExtraTreesRegressor(random_state=42, n_jobs=1).

## Data / preprocessing
- CURRENT8 frozen representation.
- 8 origin-safe predictors: Gold/Silver/Platinum/Palladium × MR/VW.
- No scaling. Tree-native inputs use the engineered CURRENT8 values directly.
- GPR geopolitical-risk chronology remains exact-origin PIT / p-1 / causally normalized inside VW.
- Random split: NONE.
- DB: READ_ONLY.
- Authority invariants unchanged.

## DEV — selection authority, 2022-04..2024-12
- n = 33
- SigmaAE = **1539.9220718606994**
- MAE = **46.66430520789998**
- RMSE = **58.55083258377693**
- MAPE = **2.2763778311528355%**
- WAPE = **2.2661649337388394%**
- Direction = **20/33 = 60.61%**
- Relative MAE vs Random Walk = **0.8759511216499997**
- Random-Walk SigmaAE = **1758.0**
- Worst AE = **137.07032323453768**, 2024-03

Candidate selection counts:
- ET_A: 6 origins
- ET_B: 27 origins

The less depth-constrained ET_B candidate was selected in 27/33 DEV origins under the frozen inner-validation objective.

## Mean DEV feature importances
These are tree-model importance diagnostics, not causal effects.

- Gold_VW: **0.4890**
- Silver_VW: **0.2085**
- Platinum_VW: **0.0834**
- Gold_MR: **0.0737**
- Palladium_VW: **0.0500**
- Platinum_MR: **0.0376**
- Silver_MR: **0.0340**
- Palladium_MR: **0.0239**

The VW block accounts for most fitted tree importance, especially Gold_VW and Silver_VW. This does not authorize feature deletion without a separately frozen DEV ablation.

## Cross-family placement
Extra Trees V1 is price-error rank **13/16** in the frozen comparison pool.

It is Pareto-dominated by:
- ChHHO-ANFIS
- RBFNN DE-ABC
- PLS1 V1
- FULL7 Equal ANN Ensemble
- REDUCED4 Equal ANN Ensemble
- CatBoost PRICE
- PLS2 V1
- Random Forest comparator
- Ridge V1
- Huber V1

Therefore it does not enter the active two-objective frontier.

## Challenger-B internal DEV ordering by SigmaAE
1. PLS1 V1 — 1420.03 / 20
2. PLS2 V1 — 1489.33 / 23
3. Ridge V1 — 1520.99 / 21
4. Huber V1 — 1530.13 / 20
5. Extra Trees V1 — **1539.92 / 20**
6. Elastic Net V1 — 1590.36 / 16
7. GPReg-Matérn V1 — 1637.92 / 19
8. GPReg-RBF V1 — 1696.34 / 16

## 2025 — LOCKED REPORT ONLY
- SigmaAE = **1019.7207781475963**
- MAE = **84.9767315122997**
- RMSE = **113.50563701331556**
- Direction = **11/12 = 91.67%**
- Relative MAE vs RW = **0.6044580783328964**
- Worst AE = **241.52931152937254**, 2025-10

Strong retrospective transport, but not used for model selection or rescue.

## 2026 Jan-Jul — QUARANTINED REPORT ONLY
- SigmaAE = **1462.6348891194048**
- MAE = **208.9478413027721**
- RMSE = **260.4187279283232**
- Direction = **6/7 = 85.71%**
- Relative MAE vs RW = **0.8821682081540438**
- Worst AE = **425.758163499685**, 2026-01

Not used for model selection or tuning.

## Decision
**NOT PROMOTED.**

Extra Trees is scientifically valid and shows strong report-only transport in 2025/2026, but the DEV selection authority places it behind Random Forest, PLS1/PLS2, Ridge and Huber and outside the current cross-family frontier.

Existing Gold Monthly / Challenger-A path remains unchanged.

Result payload SHA256:
`6d2b3b470ccac4deccedff7ea21380db7a60298f28ac6e46db3393deb67ab46d`
