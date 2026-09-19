# GOLD CONTROL — DIRECTION_BCTX_AR_V1_RESEARCH PREREGISTRATION

**Date:** 2026-09-19  
**Identity:** `DIRECTION_BCTX_AR_V1_RESEARCH`  
**Parent:** `DIRECTION_BCT_CTW_V1_RESEARCH`  
**Status:** `FROZEN_BEFORE_BCTX_AR_REPLAY`  
**Evidence class:** historical research only; no runtime or production authority

## 1. Objective

Test one final, literature-grounded successor to the binary BCT/CTW direction motor before closing the BCT family.

The successor is BCT-AR, a specific BCT-X model for real-valued time series. Instead of discarding weekly-return magnitude and modelling only a binary UP/DOWN sequence, BCT-AR:
- quantises recent real-valued returns into observable context states;
- learns the context-tree structure by Bayesian evidence/MAP inference;
- associates a separate AR model with each selected state;
- issues a real-valued one-week return forecast whose sign is mapped to UP/DOWN.

Primary source:
Papageorgiou & Kontoyiannis, *The Bayesian Context Trees State Space Model for time series modelling and forecasting*, International Journal of Forecasting / arXiv:2308.00913v3.

Pinned public replication repository:
- `IoannisPapageorgiou/Replication_BCTX`
- reference commit `8e34c5fe74797bfaad7583dae1aa46c5d01bf21d`.

## 2. Gold input and target

Input:
`gold_axis_2026/research_inputs/XAU_WEEKLY_SIGN_SOURCE_METHOD_V2_2022_2025.csv`.

The continuous target is the governed `weekly_return` already used by the corrected VLMC source-method V2:
- daily simple XAU percentage returns are summed inside each Monday-start calendar week;
- no alternate provider;
- no interpolation;
- no 2025-based source modification.

Direction evaluation:
- UP iff realized `weekly_return > 0`;
- DOWN otherwise;
- model forecast direction is UP iff predicted weekly return > 0.

This successor therefore preserves the corrected Gold weekly-return surface instead of the older BCT V1 weekly-close log-return construction.

## 3. Chronology

Hyperparameter-selection / development sample:
- all available target weeks from 2022-03-07 through 2023-12-25.

Fixed pre-2025 validation:
- all represented 2024 target weeks.

Post-diagnostic replay:
- all represented 2025 target weeks, executed unchanged after the 2024 forecast/result table is frozen.

2025 may not choose or change:
- alphabet size;
- context depth;
- beta;
- priors;
- scaling;
- quantiser grid;
- selected quantiser thresholds;
- AR order;
- direction threshold;
- promotion/closure gate.

No random split.

## 4. Frozen BCT-AR structure

Alphabet size:
- `m=3`, interpreted as lower / middle / upper return states.

Maximum context depth:
- `D=10`.

BCT prior:
- `beta = 1 - 2^(-m+1) = 0.75`;
- `alpha = (1-beta)^(1/(m-1))`.

AR base model:
- state-specific Gaussian AR(p) with intercept;
- candidate AR order `p in {1,2,3,4,5}`.

Parameter priors, following the source defaults:
- `mu0 = 0`;
- `Sigma0 = I`;
- `tau = 1`;
- `lambda = 1`.

Tree inference:
- exact GCTW evidence for model selection;
- GBCT MAP context tree for forecasting;
- MAP AR coefficients at each selected state.

## 5. Frozen scale handling

Because Gold weekly returns are decimal-valued and the BCT-AR prior is defined on the numeric scale of the input, the continuous return series is standardised once using only the 2022-03-07..2023-12-25 development sample:

`z_t = (r_t - mu_train) / sd_train`.

- `mu_train` and sample `sd_train` are frozen before 2024;
- the same transformation is used for 2024 and 2025;
- predicted z-return is transformed back to the original weekly-return scale before direction scoring.

No rolling or post-2023 rescaling is permitted under V1.

## 6. Quantiser and AR-order selection

The source paper selects quantiser thresholds and AR order by maximising Bayesian evidence at the end of training.

For this Gold V1, the candidate threshold values are frozen as the development-sample standardised-return quantiles:
`{q10,q20,q30,q40,q50,q60,q70,q80,q90}`.

All ordered threshold pairs `c1 < c2` from those nine values are evaluated, giving at most 36 ternary quantisers.

For each threshold pair, each `p in {1,2,3,4,5}` is evaluated.

Selection rule:
1. maximise exact log GCTW evidence on the development sample;
2. ties within `1e-10`: choose lower p;
3. remaining ties: choose the lexicographically smaller `(c1,c2)`.

No direction accuracy, balanced accuracy, Brier score, 2024 outcome or 2025 outcome enters this selection.

The selected `(c1,c2,p)` is frozen before any 2024 forecast is scored.

## 7. Forecasting rule

For each target week:
1. use all prior weekly returns available at that origin;
2. keep the frozen development scaling, quantiser thresholds, p, D and beta;
3. recompute the exact MAP context tree from all data available through the origin;
4. find the current state from the last D quantised returns;
5. use that state's MAP AR coefficients to predict next standardised weekly return;
6. invert the frozen scaling;
7. forecast UP iff predicted original-scale weekly return > 0, else DOWN.

The model is therefore updated sequentially with newly observed past returns, but its model-class choices and hyperparameters remain frozen.

## 8. Required outputs

Persist:
- complete evidence grid over threshold pairs and p;
- frozen selected configuration;
- 2024 complete forecast table before 2025 execution;
- 2024 metrics;
- unchanged 2025 forecast table;
- 2025 metrics;
- tree-size/depth diagnostics;
- native return RMSE/MAE;
- direction accuracy;
- balanced accuracy;
- UP sensitivity;
- DOWN sensitivity;
- confusion counts;
- always-UP baseline;
- previous-week-sign baseline.

## 9. Pre-registered decision gate

The BCT-AR successor passes the 2024 direction gate only if all are true on the fixed 2024 validation support:

1. balanced accuracy >= 0.55;
2. UP sensitivity >= 0.40;
3. DOWN sensitivity >= 0.40;
4. raw accuracy is strictly greater than both the always-UP and previous-week-sign baselines.

If any condition fails:
- `NO_PROMOTION / PRE2025_VALIDATION_FAILED`;
- 2025 is retained only as unchanged post-diagnostic evidence and cannot rescue the model;
- the BCT direction family closes for the current research sequence unless explicitly reopened by the user.

If all conditions pass, the unchanged 2025 replay is interpreted as generalisation evidence, not as a tuning surface.

## 10. Forbidden

- alternative m after results;
- D or beta grid search;
- 2024/2025 threshold tuning;
- alternative direction cutoff;
- NO_SIGNAL band;
- FAST/GVZ/BOCPD/Macro/Emergency augmentation;
- exogenous covariates;
- rolling-window search;
- target relabelling after results;
- random split;
- event-conditioned training;
- post-result quantiser-grid expansion under this identity.
