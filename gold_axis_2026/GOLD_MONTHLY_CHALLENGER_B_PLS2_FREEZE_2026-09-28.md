# GOLD MONTHLY FORECAST — CHALLENGER B / PLS2 V1 FREEZE

**Freeze date:** 2026-09-28
**Branch:** `gold-midas-headswap-v1-20260925`
**Status:** PRE-RUN METHOD FREEZE

## Purpose
Test PLS2 as Challenger-B method #5. Unlike PLS1, PLS2 jointly learns next-month log returns for Gold, Silver, Platinum and Palladium from the same frozen CURRENT8 predictors. Gold remains the only business/evaluation target.

## Binding contract
- Forecast target: H=1 next-calendar-month average XAU/USD price.
- Training outputs: next-month log returns of Gold, Silver, Platinum, Palladium (4-output PLS2).
- Evaluation/promotion objective: Gold price only.
- Gold price reconstruction: prior completed-month Gold average × exp(predicted Gold return).
- Representation: CURRENT8 only; 8 predictors = MR + VW for each of 4 metals.
- GPR: GPR_OFFICIAL_GIT_PIT; exact-origin vintage; publication-lagged p-1; causal normalization.
- Training start: 2010-05.
- Random split: NONE; chronological expanding-origin outer evaluation.
- Estimator: sklearn.cross_decomposition.PLSRegression(scale=True).
- n_components grid frozen before results: [1,2,3,4,5,6,7,8].
- max_iter=2000; tol=1e-08.
- Per-origin component selection: last 12 eligible pre-target months only.
- Inner selection objective: Gold cumulative absolute price error / Gold Random-Walk cumulative absolute price error.
- Tie-break: lower objective, then fewer components.
- PLS internal X/Y scaling is fitted only on the corresponding training fold; no external scaler.
- Outer CURRENT8 feature builder never dereferences target-month metal values.
- All four target returns used in training are matured historical targets only.
- Target-month Gold actual used only after forecast for scoring.
- Primary metric: DEV Gold SigmaAE.
- Secondary: Gold direction accuracy, MAE, RMSE, MAPE, WAPE, relative MAE vs RW, worst month, yearly stability.
- Diagnostics only: predicted 4-metal return vector, selected component count, NIPALS iterations, coefficient norm.

## Period roles
- DEV 2022-04..2024-12 (n=33): sole selection authority.
- 2025: LOCKED_REPORT_ONLY.
- 2026-01..2026-07: QUARANTINED_REPORT_ONLY.

## Frozen comparison frontier (context only)
- ChHHO-ANFIS: 1413.029779 / 23/33.
- RBFNN DE-ABC: ~1415.8371 / 25/33.
- PLS1 V1: 1420.0291314697745 / 20/33.
- GPR/MOGP LMC2_RBF_M32: ~1424.17 / 19/33.
- FULL7 Equal ANN: 1428.86 / 22/33.
- REDUCED4 Equal ANN: 1431.46 / 24/33.
- SVR frozen parent: 1449.187363 / 19/33.
- CatBoost PRICE: 1460.433935309605 / 20/33.
- Random Forest: 1491.550693715667 / 20/33.
- Ridge V1: 1520.9926031249222 / 21/33.
- Huber V1: 1530.1299616481554 / 20/33.
- Elastic Net V1: 1590.3570524947138 / 16/33.

## Governance
- Database READ_ONLY.
- Existing Gold Monthly and Challenger-A paths remain unchanged.
- No metal ablation in PLS2 V1.
- 2025/2026 cannot promote, rescue, retune or modify PLS2.
