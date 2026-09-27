# GOLD MONTHLY FORECAST — BOOSTING FAMILY LEDGER / MANIFEST

Date: 2026-09-27
Status: ACTIVE — family-specific literature challengers in progress

## Frozen project contract
- H=1 next calendar month average XAU/USD.
- Development authority: 2022-04..2024-12, n=33.
- No random split.
- DB READ_ONLY.
- Primary selection metric: DEV price SigmaAE.
- 2025 locked holdout remains unopened.
- 2026 evidence already viewed for one frozen CatBoost stress run is QUARANTINED and may not be used for any further development, tuning or selection.

## Stage ledger

### Stage 0 — Authority / protocol freeze
COMPLETE.

### Stage 1 — Canonical baselines
COMPLETE.
- CatBoost Ordered CURRENT8: SigmaAE 1460.4339353 / 20 of 33 directions.
- RF anchor: 1614.4908 / 20.
- XGBoost: 1778.0649 / 21.
- GBRT: 1801.8648 / 19.
- LightGBM: 1832.5777 / 20.

### Stage 2 — Feature-representation ablation
COMPLETE.
Promoted lanes:
- CatBoost -> CURRENT8.
- GBRT -> DAILY_SUMMARY12.
- XGBoost -> RAW_LEVEL_LAGS8 price lane; CURRENT8 direction challenger.
- LightGBM -> MIXED20 balanced lane.
- RF -> DAILY_SUMMARY12.

### Stage 3 — Target/loss ablation
COMPLETE.
- LOGRET -> price reconstruction retained.
- DIRECT_PRICE closed.
- CatBoost -> RMSE.
- GBRT -> absolute_error.
- XGBoost -> squared-error primary variants.
- LightGBM -> L1.

### Stage 4 — Capacity scan
COMPLETE.
Key price results:
- CatBoost 1460.4339 / 20.
- GBRT shallow 1500.4295 / 22.
- LightGBM 1534.6087 / 22.
- XGBoost lanes remained weaker on price.

### Stage 5 — Regularization/subsampling
COMPLETE.
- CatBoost frozen price center remains 1460.4339 / 20.
- GBRT remains 1500.4295 / 22.
- XGBoost CURRENT8 regularized price challenger 1583.8535 / 20.
- LightGBM remains 1534.6087 / 22.
- RF comparator 1491.5507 / 20.

### Stage 6A — Broad metaheuristic screen
COMPLETE.
- 33 optimizer methods plus Vanilla screened.
- CatBoost primary inner leader PSO.
- CatBoost best 6-anchor outer diagnostic DE_ABC.
- Six finalists frozen for full DEV.

### Stage 6B — CatBoost finalist full nested DEV
COMPLETE.
| Candidate | DEV SigmaAE | Direction |
|---|---:|---:|
| Vanilla CatBoost | **1460.4339** | 20/33 |
| DE_ABC | 1594.2708 | 21/33 |
| PSO | 1612.0424 | 18/33 |
| MFO | 1649.1963 | 18/33 |
| HHO | 1673.8990 | 19/33 |
| TLBO | 1714.3877 | 16/33 |

Decision:
- no CatBoost metaheuristic finalist beats Vanilla on primary DEV SigmaAE.

### Stage 6C — Boosting-specific literature challengers

#### 6C-A CMA-ES–GBRT
COMPLETE / NOT PROMOTED.

Authority:
Suan et al. (2026), DOI 10.28991/ESJ-2026-010-03-016.

Frozen nested run:
- GBRT DAILY_SUMMARY12 LOGRET absolute_error.
- CMA-ES popsize 8 × 10 generations.
- 80 calls/origin, 2640 total.
- 33 full DEV outer origins.

Results:
- frozen GBRT baseline: **1500.4294686 / 22/33**.
- CMA-ES–GBRT: **1650.1984961 / 18/33**.
- CMA-ES is +9.9817% worse in SigmaAE.
- inner validation improved in 32/33 origins, but next-month outer generalization deteriorated.

Decision:
- NOT PROMOTED.
- no post-hoc CMA rescue.
- do not repeat same CMA-ES search under current data/protocol.

Exact report:
`GOLD_MONTHLY_BOOSTING_STAGE6C_A_CMAES_GBRT_REPORT_2026-09-27.md`

#### 6C-B TPE/Optuna–GBRT
NEXT / NOT YET RUN.
Purpose: optimizer-family control under the same GBRT lane and nested chronology.

#### 6C-C Causal CEEMDAN–XGBoost
PLANNED / NOT YET RUN.
Requires origin-by-origin decomposition to avoid look-ahead.

#### 6C-D Causal VMD–Residual–CEEMDAN–WOA–XGBoost
CONDITIONAL / NOT YET RUN.
Open only after simpler decomposition challenger evidence.

#### 6C-E Boosting ensemble/complementarity
PLANNED / NOT YET RUN.
Pool must be frozen before ensemble outcomes.

### Stage 7 — Stability / feature audit
NOT YET RUN.

### Stage 8 — DEV-only family final selection
NOT YET RUN.

### Stage 9 — external transport
NOT YET VALIDLY OPENED AS FAMILY-FINAL.
- 2025: LOCKED / CLEAN.
- 2026: one CatBoost stress result exists but is quarantined from development.

## Current family status
Boosting family is **NOT COMPLETE**.
Current raw/base family price leader remains Vanilla CatBoost at DEV SigmaAE 1460.4339, but family-specific challenger and ensemble stages are still open.

## Next authorized candidate
Stage 6C-B — TPE/Optuna–GBRT, only after user authorization.
