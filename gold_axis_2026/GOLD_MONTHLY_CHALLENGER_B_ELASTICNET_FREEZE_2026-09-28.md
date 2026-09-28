# GOLD MONTHLY FORECAST — CHALLENGER B / ELASTIC NET V1 FREEZE

**Freeze date:** 2026-09-28
**Branch:** `gold-midas-headswap-v1-20260925`
**Status:** PRE-RUN METHOD FREEZE

## Purpose
Test Elastic Net as the second Challenger-B model under the same governed CURRENT8 monthly H=1 protocol used by Ridge V1.

## Binding evaluation contract
- Target: H=1 next-calendar-month average XAU/USD price.
- Model target: next-month Gold log return.
- Price reconstruction: previous completed-month Gold average × exp(predicted Gold log return).
- Representation: `CURRENT8` only.
- Features: Gold, Silver, Platinum, Palladium; per metal:
  1. prior-month log return (MR),
  2. GPR-adaptive weighted within-origin-month daily log return (VW).
- GPR: `GPR_OFFICIAL_GIT_PIT`; exact origin vintage; p-1 observation; causal normalization.
- Common training start: 2010-05.
- Random split: NONE.
- Outer evaluation: chronological expanding origin.
- Scaling: StandardScaler fitted only on the corresponding training fold.
- Estimator: sklearn ElasticNet, fit_intercept=True, max_iter=200000, tol=1e-10, selection=cyclic.
- Alpha grid frozen before results: [0.0001, 0.001, 0.01, 0.1, 1.0].
- L1-ratio grid frozen before results: [0.10, 0.25, 0.50, 0.75, 0.90, 0.95].
- Per-origin parameter selection: last 12 eligible pre-target months only.
- Inner objective: cumulative absolute price error divided by Random-Walk cumulative absolute price error.
- Deterministic tie-break: lower objective, then lower alpha, then lower l1_ratio.
- Outer fit: all eligible completed pre-target rows after parameter selection.
- Outer CURRENT8 feature construction does not dereference target-month metal values.
- Actual target price is used only for post-forecast scoring.
- Primary metric: cumulative absolute price error (SigmaAE).
- Secondary: direction accuracy, MAE, RMSE, MAPE, WAPE, relative MAE vs Random Walk, worst month, yearly stability.
- Additional diagnostic only: number of zero / near-zero coefficients in each outer fit. This diagnostic does not change the forecast or selection objective.

## Period roles
- DEV: 2022-04..2024-12 (n=33). Development/selection evidence.
- 2025: LOCKED_REPORT_ONLY. No tuning, feature/model selection or rescue.
- 2026-01..2026-07: QUARANTINED_REPORT_ONLY. No tuning, feature/model selection or rescue.

## Governance
- Database READ_ONLY.
- No production forecast/decision writes.
- Existing Gold Monthly models remain unchanged.
- Metal ablation is NOT part of Elastic Net V1.
- 2025/2026 evidence cannot be used to promote, rescue, retune, or alter Elastic Net V1.
