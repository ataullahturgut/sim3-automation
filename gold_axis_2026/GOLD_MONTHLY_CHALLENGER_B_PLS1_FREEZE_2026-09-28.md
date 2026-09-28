# GOLD MONTHLY FORECAST — CHALLENGER B / PLS1 V1 FREEZE

**Freeze date:** 2026-09-28
**Branch:** `gold-midas-headswap-v1-20260925`
**Status:** PRE-RUN METHOD FREEZE

## Purpose
Test PLS1 (single-target Partial Least Squares regression) as Challenger-B method #4 under the same governed CURRENT8 monthly H=1 protocol.

## Provenance
PLS1 is a previously used Grup-ARGE challenger family (including GA110, GA111, GA121, GA2101, GA4211 and other products). This run adapts that family to the frozen Gold Monthly CURRENT8 representation; it does not alter the existing Gold model path.

## Binding evaluation contract
- Target: H=1 next-calendar-month average XAU/USD price.
- Model target: next-month Gold log return only (PLS1).
- Price reconstruction: previous completed-month Gold average × exp(predicted Gold log return).
- Representation: CURRENT8 only.
- Features: Gold, Silver, Platinum, Palladium; per metal:
  1. prior-month log return (MR),
  2. GPR-adaptive weighted within-origin-month daily log return (VW).
- GPR: GPR_OFFICIAL_GIT_PIT; exact origin vintage; publication-lagged p-1 observation; causal normalization.
- Common training start: 2010-05.
- Random split: NONE.
- Outer evaluation: chronological expanding origin.
- Scaling: handled internally by sklearn PLSRegression(scale=True); scaling is fitted only on each training fold. No external StandardScaler.
- Estimator: sklearn.cross_decomposition.PLSRegression.
- n_components grid frozen before results: [1,2,3,4,5,6,7,8].
- max_iter = 2000; tol = 1e-08.
- Per-origin component selection: last 12 eligible pre-target months only.
- Inner objective: cumulative absolute price error divided by Random-Walk cumulative absolute price error.
- Deterministic tie-break: lower objective, then fewer components.
- Outer fit: all eligible completed pre-target rows after component selection.
- Outer CURRENT8 feature construction does not dereference target-month metal values.
- Actual target price is used only for post-forecast scoring.
- Primary metric: cumulative absolute price error (SigmaAE).
- Secondary: direction accuracy, MAE, RMSE, MAPE, WAPE, relative MAE vs Random Walk, worst month, yearly stability.
- Diagnostics only: selected component count, coefficient L2 norm, NIPALS iteration count. Diagnostics cannot change selection.

## Period roles
- DEV: 2022-04..2024-12 (n=33), sole development/selection authority.
- 2025: LOCKED_REPORT_ONLY.
- 2026-01..2026-07: QUARANTINED_REPORT_ONLY.

## Challenger-A comparison frontier (context only; never used to tune PLS1)
- ChHHO-ANFIS: SigmaAE 1413.029779; direction 23/33.
- RBFNN DE-ABC: SigmaAE approximately 1415.8371; direction 25/33.
- GPR/MOGP LMC2_RBF_M32: SigmaAE approximately 1424.17; direction 19/33.
- FULL7 Equal ANN Ensemble: SigmaAE 1428.86; direction 22/33.
- REDUCED4 Equal ANN Ensemble: SigmaAE 1431.46; direction 24/33.
- SVR frozen parent: SigmaAE 1449.187363; direction 19/33.
- CatBoost PRICE: SigmaAE 1460.433935309605; direction 20/33.
- Random Forest comparator: SigmaAE 1491.550693715667; direction 20/33.
- Ridge V1: SigmaAE 1520.9926031249222; direction 21/33.
- Huber V1: SigmaAE 1530.1299616481554; direction 20/33.
- Elastic Net V1: SigmaAE 1590.3570524947138; direction 16/33.

PLS1 V1 will be inserted into this DEV-only ordering after completion. Approximate legacy references remain labeled approximate.

## Governance
- Database READ_ONLY.
- No production forecast/decision writes.
- Existing Gold Monthly / Challenger-A path remains unchanged.
- Metal ablation is NOT part of PLS1 V1.
- 2025/2026 evidence cannot promote, rescue, retune, or alter PLS1 V1.
- PLS2 is a separate later experiment and cannot be chosen based on PLS1 2025/2026 results.
