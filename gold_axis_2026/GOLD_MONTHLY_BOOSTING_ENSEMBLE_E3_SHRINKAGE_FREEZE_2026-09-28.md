# GOLD MONTHLY FORECAST — BOOSTING ENSEMBLE E3 CONTROLLED SHRINKAGE FREEZE

Date: 2026-09-28
Status: FROZEN BEFORE E3 OUTCOME

## Purpose
E2 raw constrained simplex failed to beat the frozen E1 median baselines under honest expanding-prequential DEV evaluation. E3 tests the only pre-planned learned-weight remedy: shrink each prior-only simplex weight vector toward equal weights.

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

Pools are unchanged from the E1/E2 freezes.

## Frozen references
CATBOOST_PRICE:
- DEV SigmaAE 1460.433935309605
- direction 20/33

FULL5 E1 MEDIAN:
- DEV SigmaAE 1484.731330609916
- direction 23/33

REDUCED4 E1 MEDIAN:
- DEV SigmaAE 1490.6522619575326
- direction 22/33

FULL5 E2 RAW SIMPLEX:
- DEV SigmaAE 1532.4585226357096
- direction 19/33

REDUCED4 E2 RAW SIMPLEX:
- DEV SigmaAE 1524.257954917245
- direction 18/33

## Shrinkage definition
For each DEV origin t, let:
- w_equal = equal-weight vector for the frozen pool
- w_simplex(t) = the E2 non-negative sum-to-one simplex vector fitted strictly on DEV origins before t

Define:
w_alpha(t) = (1-alpha) * w_equal + alpha * w_simplex(t)

Thus:
- alpha=0.00 = frozen equal-weight ensemble
- alpha=1.00 = frozen raw E2 simplex
- intermediate alpha values are controlled shrinkage toward equal weights

No shrinkage toward the median is attempted because a median ensemble is not represented by one linear weight vector. E1 MEDIAN remains a separate frozen comparator.

## Frozen alpha grid
The complete grid is:
- 0.00
- 0.10
- 0.25
- 0.50
- 0.75
- 1.00

No additional alpha may be added after outcomes are observed.

## Honest evaluation
For each fixed alpha candidate:
- DEV targets are 2022-04..2024-12, n=33
- first 6 DEV origins use equal weights because the E2 simplex itself uses equal fallback
- for t >= 6, w_simplex(t) is fitted only on DEV origins strictly before t
- current target actual is never used to create w_simplex(t)
- alpha is globally fixed per candidate and is not re-fit per target

The 33-month score of each pre-frozen alpha candidate is DEV selection evidence. 2025 remains the final locked holdout.

## Selection rule
For each pool:
1. Rank the frozen alpha candidates by primary metric DEV cumulative absolute price error (SigmaAE).
2. Secondary tie-breaks only: higher direction-correct count, then lower RMSE.
3. A learned shrinkage solution is promoted only if an alpha > 0 beats that pool's frozen E1 MEDIAN SigmaAE.
4. If no alpha > 0 beats E1 MEDIAN, learned-weight ensemble optimization is CLOSED for that pool.
5. Alpha=0 is a control baseline and cannot be called a learned-weight promotion.

No arbitrary subset search, stacking, new base-model tuning, or post-outcome alpha refinement is allowed.

## Governance
- DEV: 2022-04..2024-12, n=33
- 2025: NOT OPENED / NOT EVALUATED
- 2026: QUARANTINED / NOT USED
- random split: NONE
- DB: READ_ONLY
- component configs: frozen Stage-5 configs only
- component predictions must exactly reconcile to frozen component metrics
- E2 simplex construction must remain unchanged

## Next step
Implement and run the E3 runner exactly under this freeze. If both pools fail the promotion rule, proceed to final Boosting robustness with CatBoost PRICE and E1 FULL5 MEDIAN as the principal frozen challengers.
