# GOLD MONTHLY FORECAST — CHALLENGER B / GPREG-RBF V1 FREEZE

**Freeze date:** 2026-09-28
**Branch:** `gold-midas-headswap-v1-20260925`
**Status:** PRE-RUN METHOD FREEZE

## Provenance
This model is the Gold Monthly adaptation of the previously used Grup-ARGE GPR-RBF implementation (including GA111):
- StandardScaler on X only, fitted on training data only.
- Kernel = ConstantKernel(signal_scale, fixed) * RBF(length_scale, fixed).
- GaussianProcessRegressor(alpha=..., normalize_y=True, optimizer=None, random_state=42).

The original Grup-ARGE hyperparameter grid is preserved:
- length_scale: [0.5, 1.0, 2.0, 5.0]
- signal_scale: [0.5, 1.0, 2.0]
- alpha: [1e-4, 1e-3, 1e-2, 1e-1]

## Binding Gold Monthly contract
- Business target: H=1 next-calendar-month average XAU/USD price.
- Model target: next-month Gold log return.
- Price reconstruction: previous completed-month Gold average × exp(predicted Gold return).
- Representation: CURRENT8 only.
- Predictors: Gold, Silver, Platinum, Palladium; each contributes MR + GPR-adaptive VW.
- GPR geopolitical-risk source: exact-origin PIT vintage, publication-lagged p-1 observation, causal normalization.
- Training start: 2010-05.
- Random split: NONE.
- Outer evaluation: chronological expanding origin.
- Inner parameter selection: last 12 eligible pre-target months only.
- Inner objective: cumulative Gold price absolute error / Random-Walk cumulative absolute error.
- Deterministic tie-break: lower objective, then lower length_scale, lower signal_scale, lower alpha.
- Actual target price is used only after forecast for scoring.
- Outer feature construction never dereferences target-month metal values.
- Predictive standard deviation from Gaussian Process is diagnostic only and does not affect point forecast selection.
- Primary metric: DEV SigmaAE.
- Secondary: direction accuracy, MAE, RMSE, MAPE, WAPE, relative MAE vs RW, worst month, yearly stability.

## Period roles
- DEV: 2022-04..2024-12, n=33, sole selection authority.
- 2025: LOCKED_REPORT_ONLY.
- 2026-01..2026-07: QUARANTINED_REPORT_ONLY.

## Frozen comparison pool (context only)
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

## Governance
- Database READ_ONLY.
- Existing Gold Monthly / Challenger-A path remains unchanged.
- No metal ablation in GPReg-RBF V1.
- 2025/2026 cannot promote, rescue, retune or alter the model.
