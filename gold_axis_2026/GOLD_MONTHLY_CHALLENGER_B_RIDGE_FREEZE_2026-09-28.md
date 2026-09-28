# GOLD MONTHLY FORECAST — CHALLENGER B / RIDGE V1 FREEZE

**Freeze date:** 2026-09-28  
**Branch:** `gold-midas-headswap-v1-20260925`  
**Status:** PRE-RUN METHOD FREEZE

## Purpose
Test Ridge Regression as the first Grup-ARGE-style advanced challenger without modifying or replacing the existing Gold Monthly forecast path.

## Binding evaluation contract
- Target: H=1 next-calendar-month average XAU/USD price.
- Model target: next-month Gold log return.
- Price reconstruction: previous completed-month Gold average × exp(predicted Gold log return).
- Representation: `CURRENT8` only.
- Features: Gold, Silver, Platinum, Palladium; for each metal:
  1. prior-month log return (MR),
  2. GPR-adaptive weighted within-origin-month daily log return (VW).
- GPR: `GPR_OFFICIAL_GIT_PIT`; exact origin vintage; p-1 observation; causal normalization.
- Daily metals: frozen StakTrakr research series already governed by the existing pipeline.
- Common training start: 2010-05.
- Random split: NONE.
- Outer evaluation: chronological expanding origin.
- Scaling: StandardScaler fitted only on the corresponding training fold.
- Estimator: sklearn Ridge, fit_intercept=True.
- Alpha grid frozen before results: [0.01, 0.1, 1.0, 10.0, 100.0].
- Per-origin alpha selection: last 12 eligible pre-target months only; objective is cumulative absolute price error divided by Random-Walk cumulative absolute price error. Tie-break: lower alpha.
- Outer fit: all eligible completed pre-target rows after alpha selection.
- Outer CURRENT8 feature construction does not reference target-month metal values.
- Actual target price is used only for post-forecast scoring.
- Primary metric: cumulative absolute price error (SigmaAE).
- Secondary: direction accuracy, MAE, RMSE, MAPE, WAPE, relative MAE vs Random Walk, worst month, yearly stability.

## Period roles
- DEV: 2022-04..2024-12 (n=33). Development/selection evidence.
- 2025: LOCKED_REPORT_ONLY. No tuning, feature/model selection or rescue.
- 2026-01..2026-07: QUARANTINED_REPORT_ONLY. No tuning, feature/model selection or rescue.

## Governance
- Database READ_ONLY.
- No production forecast/decision writes.
- Existing main Gold Monthly models remain unchanged.
- XGBoost/ARIMA are not rerun in this challenger.
- Metal ablation is NOT part of Ridge V1; it is a separate later stage and must not be chosen from 2025/2026 results.
