# GOLD MONTHLY FORECAST — BOOSTING STAGE 6C-B TPE/OPTUNA–GBRT RESULT

Date: 2026-09-28
Status: COMPLETE / SCIENTIFIC GATE PASS / NOT PROMOTED

## Method
Optuna TPE hyperparameter optimization of GradientBoostingRegressor under the frozen project protocol.

Authority:
Suan, J. S. P., Anbananthen, K. S. M., & Kanan, R. K. (2026).
Gold Price Forecasting Using Machine Learning Models with Hyperparameter Optimization for Inflation Hedging.
Emerging Science Journal 10(3), 1473–1490.
DOI: 10.28991/ESJ-2026-010-03-016.

Project adaptation:
- DAILY_SUMMARY12
- next-month Gold log return
- price reconstruction from previous completed-month Gold average
- loss = absolute_error
- DEV only: 2022-04..2024-12, n=33
- nested chronological inner validation = last 12 pre-target months
- Optuna TPESampler
- 80 trials per origin; 2640 total trials
- random split = NONE
- DB = READ_ONLY
- 2025 = NOT OPENED
- 2026 = QUARANTINED / NOT USED IN DEVELOPMENT

## Baseline GBRT
- DEV SigmaAE: 1500.42946858865
- MAE: 45.4675596542
- RMSE: 58.2166488228
- MAPE: 2.2174631895%
- relative MAE vs RW: 0.8534866147
- direction: 22/33 = 66.67%

## TPE/Optuna–GBRT
- DEV SigmaAE: 1576.972863072526
- MAE: 47.7870564567
- RMSE: 61.5268842775
- MAPE: 2.3084871664%
- WAPE: 2.3206892537%
- relative MAE vs RW: 0.8970266570
- direction: 18/33 = 54.55%
- worst AE: 171.3645836568 (2024-11)

Yearly:
- 2022: SigmaAE 374.3058341253, direction 6/9
- 2023: SigmaAE 459.8566076582, direction 5/12
- 2024: SigmaAE 742.8104212890, direction 7/12

## Inner-vs-outer finding
TPE improved the inner-validation objective in 31/33 origins:
- mean inner ratio vs baseline = 0.8539245072
- median = 0.8399977790
- worst = 1.0322073276

But outer DEV transport failed:
- baseline 1500.4295 / 22 directions
- TPE 1576.9729 / 18 directions
- CMA-ES reference 1650.1985 / 18 directions

Thus TPE is better than CMA-ES but still worse than frozen Stage-5 GBRT.

## Decision
TPE/Optuna–GBRT is scientifically valid but NOT PROMOTED.
It does not improve the frozen GBRT frontier and does not challenge Vanilla CatBoost (1460.4339353).
No 2025 or quarantined 2026 evidence is used in this decision.

Next planned literature challenger:
Stage 6C-C — causal CEEMDAN–XGBoost, if authorized.

## Reproducibility
GitHub Actions run: 36348652770
Job: 108702856918
Result payload SHA256: b4ed6cf64f731f0f39ba935afb1b3e0fc0189f4c301f0dabf93c0c06d1330f1c
Scientific gate: BOOSTING_STAGE6C_B_GATE=PASS
