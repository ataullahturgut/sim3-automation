# GOLD MONTHLY FORECAST — BOOSTING STAGE 6C-A CMA-ES–GBRT PRE-OUTCOME FREEZE

Date: 2026-09-27
Status: FROZEN BEFORE OUTCOME

## Authority
Primary direct gold-specific source:
Suan, J. S. P., Anbananthen, K. S. M., & Kanan, R. K. (2026).
"Gold Price Forecasting Using Machine Learning Models with Hyperparameter Optimization for Inflation Hedging."
Emerging Science Journal 10(3), 1473–1490.
DOI: 10.28991/ESJ-2026-010-03-016.

The source compares Grid Search, TPE and CMA-ES and reports CMA-ES-optimized Gradient Boosting as its best model on monthly gold forecasting. The present experiment is an origin-safe adaptation to this project's frozen H=1 protocol; it is NOT claimed as an exact reproduction because the data, target and validation protocol differ.

## Frozen project lane
- Estimator: sklearn GradientBoostingRegressor.
- Representation: DAILY_SUMMARY12.
- Training target: next-month Gold log return.
- Price reconstruction: previous completed month Gold average * exp(predicted log return).
- Loss: absolute_error.
- Training-history start: 2010-03.
- DEV authority: 2022-04..2024-12, n=33.
- 2025: BLOCKED / NOT OPENED BY THIS STAGE.
- 2026: BLOCKED FROM DEVELOPMENT. Previously viewed CatBoost 2026 stress evidence is quarantined and cannot affect this experiment.
- Random split: NONE.
- Database: READ_ONLY.

## Nested chronology
For each outer DEV target t:
1. Build features and labels using only information available before t.
2. Inner validation = last 12 buildable pre-t months.
3. Inner training = all earlier buildable history.
4. CMA-ES sees only inner-training/inner-validation data.
5. Primary fitness = reconstructed-price inner-validation SigmaAE / Random-Walk inner-validation SigmaAE.
6. After hyperparameter selection, refit GBRT on all pre-t history and forecast t exactly once.
7. Outer target actual is never used by CMA-ES.

## CMA-ES budget
Implementation package: cma 4.5.0.
- latent search cube: six dimensions in [0,1].
- x0: [0.5]*6.
- sigma0: 0.25.
- population size: 8.
- generations: 10.
- maximum objective calls: 80 per outer origin.
- one deterministic seed per outer target derived from fixed base seed 1701.
- decoded duplicates count toward the 80-call budget; cache may only avoid redundant computation.
- no rescue/restart based on outer outcomes.

## Frozen hyperparameter search space
1. max_depth: integer 1..5.
2. n_estimators: integer 50..500.
3. learning_rate: log-uniform 0.01..0.20.
4. min_samples_leaf: integer 1..10.
5. subsample: continuous 0.60..1.00.
6. max_features: continuous 0.60..1.00.

All other GradientBoostingRegressor parameters remain at the frozen project/default values, including random_state=1701 and loss=absolute_error.

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

## Decision rule
Primary: full 33-month DEV SigmaAE.
Secondary: direction correct, RMSE, yearly SumAE stability, worst month, relative MAE vs RW.
No 2025/2026 evidence may change the decision.

## Stop rule
This run evaluates CMA-ES–GBRT only. It does not authorize TPE, CEEMDAN, VMD, ensembles or any later challenger.
