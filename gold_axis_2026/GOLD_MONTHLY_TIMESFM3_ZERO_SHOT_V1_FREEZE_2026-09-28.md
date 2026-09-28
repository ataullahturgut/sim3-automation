# GOLD MONTHLY FORECAST — TIMESFM-3 ZERO-SHOT MULTIVARIATE V1 FREEZE

**Freeze date:** 2026-09-28
**Branch:** `gold-midas-headswap-v1-20260925`
**Status:** PRE-RUN METHOD FREEZE / RESEARCH ONLY

## Authority
Official Google Research TimesFM 3.0:
- checkpoint: `google/timesfm-3.0-pytorch`
- package: `timesfm==3.0.2`
- native multivariate forecasting
- PyTorch backend
- 0.3B parameters
- model weights license: TimesFM Non-Commercial License v1.0

This experiment is research-only and does not authorize production/commercial use of TimesFM-3 weights.

## Purpose
Test TimesFM-3 as a new zero-shot foundation-model challenger for Gold Monthly H=1 forecasting.

## Frozen V1 representation
Target context is a 4-variate monthly price-level matrix:
1. Gold authoritative monthly average XAU/USD
2. Silver monthly average
3. Platinum monthly average
4. Palladium monthly average

For each outer target month M:
- context includes only completed months from 2010-05 through origin M-1;
- no target-month price is present in context;
- input shape = (4, context_length);
- forecast horizon = 1;
- Gold forecast = first variate's point forecast at horizon 1.

No CURRENT8 MR/VW features are used in V1.
No GPR/macro covariates are used in V1.
No external scaling is used.
No fine-tuning is used.
No hyperparameter tuning is used.
No DEV-based parameter selection is used.

## Inference configuration
- backend: PyTorch
- device: CPU
- checkpoint: google/timesfm-3.0-pytorch
- per_core_batch_size: 4
- horizon: 1
- return_quantiles: True
- use_symmetric_averaging: False
- model defaults otherwise unchanged

## Evaluation
- Primary: DEV cumulative absolute Gold price error (SigmaAE)
- Secondary: Gold direction accuracy
- Supporting: MAE, RMSE, MAPE, WAPE, relative MAE vs Random Walk, worst month
- Quantile output is diagnostic only.

## Period roles
- DEV 2022-04..2024-12, n=33: sole scientific comparison authority
- 2025: LOCKED_REPORT_ONLY
- 2026-01..2026-07: QUARANTINED_REPORT_ONLY

Because V1 is strictly zero-shot with no fitting/tuning, DEV is used only for evaluation/comparison, not parameter learning.

## Governance
- DB READ_ONLY
- Random split: NONE
- Target-month leakage: FORBIDDEN
- Existing Challenger-A and Challenger-B models remain unchanged
- If TimesFM-3 fails technically due weight/license/runtime constraints, no substitute TimesFM version may be silently used.
