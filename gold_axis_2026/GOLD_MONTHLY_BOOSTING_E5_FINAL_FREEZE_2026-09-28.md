# GOLD MONTHLY FORECAST — BOOSTING E5 FINAL FREEZE

Date: 2026-09-28
Status: FINAL BOOSTING ARCHITECTURE FROZEN BEFORE 2025 HOLDOUT

## Scope
This freeze closes Boosting model development, tuning, structural challengers, learned-weight ensembles, shrinkage, and DEV robustness.

No Boosting model, feature set, target, representation, hyperparameter, component pool, ensemble rule, or role may change after this point based on 2025 outcomes.

## Frozen governance
- DEV: 2022-04..2024-12, n=33
- 2025: FINAL LOCKED HOLDOUT, still unopened at freeze time
- 2026: QUARANTINED / report-only, not usable for model development
- random split: NONE
- evaluation chronology: expanding / origin-safe
- database: READ_ONLY
- primary DEV selection metric: cumulative absolute reconstructed-price error (SigmaAE)

## Frozen PRICE role

Model: CATBOOST_PRICE

Frozen Stage-5 identity:
- lane: CATBOOST_PRICE
- profile: CB_R0_BASELINE
- representation: CURRENT8
- target: next-month Gold log-return
- CatBoost Ordered
- iterations: 100
- depth: 6
- learning_rate: 0.03
- l2_leaf_reg: 3
- random_strength: 1
- seed: 1701

DEV evidence:
- SigmaAE: 1460.433935309605
- direction: 20/33
- MAE: 44.255574
- RMSE: 57.8094
- relative MAE vs RW: 0.830736

E4 robustness:
- monthly AE wins vs FULL5 MEDIAN: 14
- losses: 7
- ties: 12
- common leave-one-origin remaining-32-month SigmaAE comparison:
  - CATBOOST_PRICE preferred: 33/33
  - FULL5_MEDIAN preferred: 0/33
  - ties: 0

Final role:
PRICE = CATBOOST_PRICE

## Frozen BALANCE / DIRECTION role

Model: FULL5 MEDIAN

Frozen components:
1. CATBOOST_PRICE
2. CATBOOST_BALANCED
3. GBRT
4. LIGHTGBM
5. XGB_DIRECTION

Combination rule:
- row-wise median of the five reconstructed-price forecasts
- no learned weights
- no tuning
- no subset selection
- no post-hoc component deletion

DEV evidence:
- SigmaAE: 1484.731330609916
- direction: 23/33
- MAE: 44.991859
- relative MAE vs RW: 0.84456

E4 direction relation versus CATBOOST_PRICE:
- rescues: 3
- losses: 0
- both correct: 20
- both wrong: 10

Final role:
BALANCE_DIRECTION = FULL5_MEDIAN

## Closed alternatives
The following are closed and cannot be resurrected from 2025 outcomes:
- CatBoost metaheuristic tuning finalists
- CMA-ES–GBRT
- TPE/Optuna–GBRT
- causal CEEMDAN–XGBoost
- causal VMD–XGBoost
- VMD + residual CEEMDAN continuation
- WOA continuation
- E2 constrained simplex
- E3 controlled shrinkage
- arbitrary component subset search
- learned stacking

## 2025 one-shot holdout protocol
After this freeze, 2025 may be opened exactly once as final transport evidence.

For each 2025 target month:
- forecast origin is the end of the previous completed calendar month
- only data available at that origin may be used
- frozen component configurations are reproduced exactly
- CATBOOST_PRICE is evaluated as frozen PRICE role
- FULL5 MEDIAN is evaluated as frozen BALANCE_DIRECTION role
- no target-month actual enters fitting or feature construction

Report for each frozen role:
- monthly actual
- monthly forecast
- absolute error
- direction correctness versus random walk
- yearly SigmaAE
- MAE
- RMSE
- MAPE / WAPE
- relative MAE vs RW
- direction count / 12
- worst month / worst AE

## Holdout non-intervention rule
2025 results may NOT:
- alter a base model
- change a hyperparameter
- change a feature/representation
- change a component pool
- change the median rule
- create a rescue model
- reopen learned weights
- trigger shrinkage tuning
- reopen structural challengers
- change PRICE or BALANCE_DIRECTION role definitions

2025 is transport evidence only.

## E5 decision
Boosting architecture is FINAL FROZEN.

Frozen roles entering 2025:
- PRICE: CATBOOST_PRICE
- BALANCE_DIRECTION: FULL5_MEDIAN

Next and only remaining Boosting step:
- E6 2025 FINAL HOLDOUT, one-shot evaluation.

## Kontrol ve Uyum Özeti
- E4 robustness: PASS
- PRICE final role frozen: CATBOOST_PRICE
- BALANCE_DIRECTION final role frozen: FULL5_MEDIAN
- learned-weight optimization: CLOSED
- structural challenger search: CLOSED
- arbitrary subset search: CLOSED
- 2025 opened before freeze: NO
- 2026 used for selection/tuning: NO
- random split: NONE
- DB: READ_ONLY
