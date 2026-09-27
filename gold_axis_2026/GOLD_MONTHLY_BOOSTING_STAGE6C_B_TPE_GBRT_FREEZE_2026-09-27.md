# GOLD MONTHLY FORECAST — BOOSTING STAGE 6C-B TPE/OPTUNA–GBRT PRE-OUTCOME FREEZE

Date: 2026-09-27
Status: FROZEN BEFORE OUTCOME

## Authority
Primary direct gold-specific source:
Suan, J. S. P., Anbananthen, K. S. M., & Kanan, R. K. (2026).
"Gold Price Forecasting Using Machine Learning Models with Hyperparameter Optimization for Inflation Hedging."
Emerging Science Journal 10(3), 1473–1490.
DOI: 10.28991/ESJ-2026-010-03-016.

The source compares Grid Search, TPE and CMA-ES for monthly gold forecasting. This project run is an origin-safe adaptation, not an exact source-code reproduction.

## Frozen project lane
- Estimator: sklearn GradientBoostingRegressor.
- Representation: DAILY_SUMMARY12.
- Training target: next-month Gold log return.
- Price reconstruction: previous completed month Gold average * exp(predicted log return).
- Loss: absolute_error.
- Training-history start: 2010-03.
- DEV authority: 2022-04..2024-12, n=33.
- 2025: BLOCKED / NOT OPENED.
- 2026: QUARANTINED / NOT USED IN DEVELOPMENT.
- Random split: NONE.
- Database: READ_ONLY.

## Nested chronology
For each outer DEV target t:
1. Build inputs and labels only from data available before t.
2. Inner validation = last 12 buildable pre-target months.
3. Inner training = all earlier buildable history.
4. TPE sees only inner train/validation information.
5. Fitness = reconstructed-price inner-validation SigmaAE / RW inner-validation SigmaAE.
6. After hyperparameter selection, refit on all pre-target history and forecast t once.
7. Outer target actual is read only after the forecast is generated.

## TPE budget and sampler
Implementation: Optuna TPESampler.
- trials: 80 per outer origin.
- sampler seed: deterministic per origin, fixed base seed 1701.
- n_startup_trials: 10.
- multivariate: False.
- group: False.
- constant_liar: False.
- pruner: NONE.
- no rescue/restart based on outer outcomes.

## Frozen hyperparameter search space
Exactly the same scientific dimensions as Stage 6C-A CMA-ES:
1. max_depth: integer 1..5.
2. n_estimators: integer 50..500.
3. learning_rate: log-uniform 0.01..0.20.
4. min_samples_leaf: integer 1..10.
5. subsample: continuous 0.60..1.00.
6. max_features: continuous 0.60..1.00.

All other GradientBoostingRegressor parameters remain fixed, including random_state=1701 and loss=absolute_error.

## Comparator
Frozen Stage-5 GBRT:
- DAILY_SUMMARY12
- max_depth=2
- n_estimators=100
- learning_rate=0.10
- min_samples_leaf=2
- subsample=1.0
- max_features=None/full
- DEV SigmaAE reference = 1500.42946858865
- direction = 22/33

Stage 6C-A CMA-ES reference is retained for post-run comparison only:
- DEV SigmaAE = 1650.1984960673
- direction = 18/33

## Decision rule
Primary: full 33-month DEV SigmaAE.
Secondary: direction correct, RMSE, yearly SumAE stability, worst month, relative MAE vs RW.
No 2025/2026 evidence may affect the decision.

## Stop rule
This run evaluates TPE/Optuna–GBRT only. It does not authorize CEEMDAN, VMD, ensembles or later challengers.
