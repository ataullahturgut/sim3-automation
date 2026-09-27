# GOLD MONTHLY FORECAST — BOOSTING STAGE 6C-A CMA-ES–GBRT RESULT

Date: 2026-09-27
Status: COMPLETE / SCIENTIFIC GATE PASS / NOT PROMOTED

## Method
Literature-motivated CMA-ES hyperparameter optimization of GradientBoostingRegressor under the frozen project protocol.

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
- CMA-ES = popsize 8 × 10 generations = 80 objective calls/origin
- total objective calls = 2640
- random split = NONE
- DB = READ_ONLY
- 2025 = NOT OPENED
- 2026 = QUARANTINED / NOT USED IN DEVELOPMENT

## Baseline GBRT
- DEV SigmaAE: 1500.42946858865
- MAE: 45.4675596542
- RMSE: 58.2166488228
- MAPE: 2.2174631895%
- WAPE: 2.2080472184%
- relative MAE vs RW: 0.8534866147
- direction: 22/33 = 66.67%
- worst AE: 159.8297934157 (2024-11)

Yearly:
- 2022: SigmaAE 415.9404386040, direction 7/9
- 2023: SigmaAE 428.1814630599, direction 6/12
- 2024: SigmaAE 656.3075669247, direction 9/12

## CMA-ES–GBRT
- DEV SigmaAE: 1650.1984960673
- MAE: 50.0060150323
- RMSE: 60.9104931763
- MAPE: 2.4382132236%
- WAPE: 2.4284488377%
- relative MAE vs RW: 0.9386794631
- direction: 18/33 = 54.55%
- worst AE: 157.2708550039 (2024-11)

Yearly:
- 2022: SigmaAE 392.7445904098, direction 6/9
- 2023: SigmaAE 543.0934363295, direction 5/12
- 2024: SigmaAE 714.3604693280, direction 7/12

## Inner-vs-outer finding
CMA-ES improved the nested inner-validation objective in 32/33 outer origins:
- mean inner ratio vs baseline = 0.8722166120
- median = 0.8633923209
- worst = 1.0483653690

Despite this, full outer DEV SigmaAE worsened from 1500.4295 to 1650.1985 and direction fell from 22/33 to 18/33.

This is direct evidence of poor transport from the 12-month inner tuning window to the next outer month under this sample size.

## Decision
CMA-ES–GBRT is scientifically valid but NOT PROMOTED.
It does not improve the frozen GBRT frontier and does not challenge Vanilla CatBoost (1460.4339353).
No 2025 or quarantined 2026 evidence is used in this decision.

Next literature challenger:
Stage 6C-B — TPE/Optuna–GBRT control under the same nested chronological contract, if authorized.

## Reproducibility
GitHub Actions run: 36346283656
Job: 108695961872
Result payload SHA256: 1f1aa49014736eed437798e6aebaca3bcb9fd78c9bd925364f54a931e7fd4e94
Scientific gate: BOOSTING_STAGE6C_A_GATE=PASS
