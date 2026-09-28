# GOLD MONTHLY FORECAST — BOOSTING ENSEMBLE E2 CONSTRAINED SIMPLEX FREEZE

Date: 2026-09-28
Status: FROZEN BEFORE E2 OUTCOME

## Purpose
Test whether non-negative learned ensemble weights add honest DEV value beyond the frozen E1 baselines.

## Frozen pools
FULL5:
1. CATBOOST_PRICE
2. CATBOOST_BALANCED
3. GBRT
4. LIGHTGBM
5. XGB_DIRECTION

REDUCED4:
1. CATBOOST_PRICE
2. GBRT
3. LIGHTGBM
4. XGB_DIRECTION

Pools are unchanged from:
GOLD_MONTHLY_BOOSTING_ENSEMBLE_POOL_FREEZE_2026-09-28.md

## Frozen references
- CATBOOST_PRICE: DEV SigmaAE 1460.433935309605, direction 20/33.
- FULL5 MEDIAN E1: DEV SigmaAE 1484.731330609916, direction 23/33.
- REDUCED4 MEDIAN E1: DEV SigmaAE 1490.6522619575326, direction 22/33.

## Weight constraints
For each pool:
- w_j >= 0
- sum_j w_j = 1

No intercept.
No negative weights.
No component subset search.
No stacking/meta-features.

## Optimization objective
Minimize cumulative absolute reconstructed-price error:
SigmaAE = sum_t | forecast_t - actual_t |

Solver:
- exact linear programming via scipy.optimize.linprog(method="highs").

This objective matches the project's primary DEV selection metric.

## Honest expanding-prequential evaluation
For each DEV target index t:
- first 6 DEV origins: equal weights;
- for t >= 6: solve the constrained simplex using DEV origins strictly before t only;
- apply those weights once to target t;
- target-t actual is not available to the optimizer;
- future DEV origins are unavailable.

This expanding-prequential result is the ONLY honest E2 selection evidence.

## Full-DEV fit
A second simplex is solved on all 33 DEV observations only to record the eventual external frozen-weight diagnostic.

Its same-sample DEV score:
- is diagnostic only;
- is NOT honest selection evidence;
- cannot promote a model if expanding-prequential performance is inferior.

## Governance
- DEV: 2022-04..2024-12, n=33.
- 2025: NOT OPENED / NOT EVALUATED.
- 2026: QUARANTINED / NOT USED.
- random split: NONE.
- DB: READ_ONLY.
- base model retraining: allowed only for exact reproduction of already-frozen component predictions; no base hyperparameter changes.
- arbitrary subset search: NONE.

## Decision rule
E2 simplex is promoted only if its honest expanding-prequential DEV SigmaAE is lower than the relevant E1 baseline and competitive with the family price leader without a material stability collapse.

If E2 is worse than E1:
- do NOT promote raw simplex;
- proceed only to the already-planned controlled shrinkage test toward the E1 baseline, with a fixed pre-outcome alpha grid.
