# GOLD MONTHLY FORECAST — CHALLENGER B / HUBER V1 FREEZE

**Freeze date:** 2026-09-28
**Branch:** `gold-midas-headswap-v1-20260925`
**Status:** PRE-RUN METHOD FREEZE

## Purpose
Test Huber robust linear regression as Challenger-B method #3 under the same governed CURRENT8 monthly H=1 protocol used by Ridge and Elastic Net.

## Binding evaluation contract
- Target: H=1 next-calendar-month average XAU/USD price.
- Model target: next-month Gold log return.
- Price reconstruction: previous completed-month Gold average × exp(predicted Gold log return).
- Representation: CURRENT8 only.
- Features: Gold, Silver, Platinum, Palladium; per metal prior-month log return (MR) + GPR-adaptive within-origin-month weighted daily log return (VW).
- GPR: GPR_OFFICIAL_GIT_PIT; exact-origin vintage; publication-lagged p-1 observation; causal normalization.
- Common training start: 2010-05.
- Random split: NONE.
- Outer evaluation: chronological expanding origin.
- Scaling: StandardScaler fitted only on the corresponding training fold.
- Estimator: sklearn HuberRegressor, fit_intercept=True, max_iter=5000, tol=1e-8.
- Alpha grid frozen before results: [0.0, 0.0001, 0.001, 0.01, 0.1].
- Epsilon grid frozen before results: [1.10, 1.20, 1.35, 1.50, 1.75, 2.00].
- Per-origin parameter selection: last 12 eligible pre-target months only.
- Inner objective: cumulative absolute price error divided by Random-Walk cumulative absolute price error.
- Deterministic tie-break: lower objective, then lower alpha, then lower epsilon.
- Outer fit: all eligible completed pre-target rows after parameter selection.
- Outer CURRENT8 feature construction does not dereference target-month metal values.
- Actual target price is used only for post-forecast scoring.
- Primary metric: cumulative absolute price error (SigmaAE).
- Secondary: direction accuracy, MAE, RMSE, MAPE, WAPE, relative MAE vs Random Walk, worst month, yearly stability.
- Robust diagnostic only: fitted Huber scale and fraction of training rows flagged as outliers. Diagnostics do not change selection.

## Period roles
- DEV: 2022-04..2024-12 (n=33), sole development/selection authority.
- 2025: LOCKED_REPORT_ONLY.
- 2026-01..2026-07: QUARANTINED_REPORT_ONLY.

## Challenger-A comparison frontier (context only; never used to tune Huber)
Current known cross-family DEV references:
- ChHHO-ANFIS: SigmaAE 1413.029779; direction 23/33.
- RBFNN DE-ABC: SigmaAE approximately 1415.8371; direction 25/33.
- GPR/MOGP LMC2_RBF_M32: SigmaAE approximately 1424.17; direction 19/33.
- FULL7 Equal ANN Ensemble: SigmaAE 1428.86; direction 22/33.
- REDUCED4 Equal ANN Ensemble: SigmaAE 1431.46; direction 24/33.
- SVR frozen parent reference: SigmaAE 1449.187363; direction 19/33.
- CatBoost PRICE: SigmaAE 1460.433935309605; direction 20/33.
- Random Forest comparator: SigmaAE 1491.550693715667; direction 20/33.
- Ridge V1: SigmaAE 1520.9926031249222; direction 21/33.
- Elastic Net V1: SigmaAE 1590.3570524947138; direction 16/33.

Huber V1 will be inserted into this DEV-only ordering after completion. Approximate legacy references remain labeled approximate and are not silently converted into exact values.

## Governance
- Database READ_ONLY.
- No production forecast/decision writes.
- Existing Gold Monthly / Challenger-A path remains unchanged.
- Metal ablation is NOT part of Huber V1.
- 2025/2026 evidence cannot promote, rescue, retune, or alter Huber V1.
