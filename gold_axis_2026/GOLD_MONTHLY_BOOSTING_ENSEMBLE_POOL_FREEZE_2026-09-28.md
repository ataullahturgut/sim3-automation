# GOLD MONTHLY FORECAST — BOOSTING ENSEMBLE POOL FREEZE

Date: 2026-09-28
Status: FROZEN BEFORE ENSEMBLE EVALUATION

## Authority and governance
- DEV selection authority only: 2022-04..2024-12, n=33.
- 2025: NOT OPENED / NOT EVALUATED.
- 2026: QUARANTINED / NOT USED.
- No ensemble forecast was evaluated before this pool freeze.
- Component audit used only individual-model DEV predictions, error correlations, and directional complementarity.
- Random split: NONE.
- DB: READ_ONLY.

## Eligible Boosting-family components

| Component | Frozen role | DEV SumAE | Direction |
|---|---|---:|---:|
| CATBOOST_PRICE | family price leader | 1460.4339353 | 20/33 |
| CATBOOST_BALANCED | CatBoost direction/balance profile | 1481.2619377 | 22/33 |
| GBRT | distinct boosting architecture / balance | 1500.4294686 | 22/33 |
| LIGHTGBM | distinct boosting architecture / balance | 1534.6087211 | 22/33 |
| XGB_DIRECTION | strongest direction specialist | 1679.8371518 | 23/33 |

RF was audited but is NOT a Boosting model and is excluded from the Boosting-family final ensemble pool.

## Signed forecast-error correlation audit

Key correlations:
- CATBOOST_PRICE vs CATBOOST_BALANCED: 0.9891845
- CATBOOST_PRICE vs GBRT: 0.9658567
- CATBOOST_PRICE vs LIGHTGBM: 0.9716127
- CATBOOST_PRICE vs XGB_DIRECTION: 0.9373603
- GBRT vs LIGHTGBM: 0.9547566
- GBRT vs XGB_DIRECTION: 0.9337491
- LIGHTGBM vs XGB_DIRECTION: 0.9343319

Interpretation:
- The two CatBoost variants are extremely redundant.
- XGB_DIRECTION provides the strongest directional complement and the lowest correlation to the price leader among eligible Boosting models.
- GBRT and LightGBM remain correlated but preserve distinct boosting implementations and both carry 22/33 direction performance.

## Direction complementarity versus CATBOOST_PRICE
- CATBOOST_BALANCED: rescues 4 leader misses, loses 2 leader hits.
- GBRT: rescues 3, loses 1.
- LIGHTGBM: rescues 4, loses 2.
- XGB_DIRECTION: rescues 5, loses 2.

## Frozen pools

### FULL5
Role-complete Boosting pool:
1. CATBOOST_PRICE
2. CATBOOST_BALANCED
3. GBRT
4. LIGHTGBM
5. XGB_DIRECTION

Purpose:
Preserve every predeclared Boosting role, including both CatBoost price/balance profiles.

### REDUCED4
Predeclared redundancy-reduced Boosting pool:
1. CATBOOST_PRICE
2. GBRT
3. LIGHTGBM
4. XGB_DIRECTION

CATBOOST_BALANCED is omitted only from REDUCED4 because:
- its signed-error correlation with CATBOOST_PRICE is 0.9892, the highest principal redundancy in the pool;
- its role is partially represented by GBRT/LIGHTGBM 22/33 balance profiles;
- omission is frozen before any ensemble performance is computed.

## Authorized Stage E1 variants
For BOTH frozen pools evaluate only:
1. EQUAL_MEAN
   - fixed equal weights.
2. MEDIAN
   - component forecast median each month.
3. PREQUENTIAL_INVERSE_MAE
   - for DEV target t, use only earlier DEV origins;
   - first 6 DEV origins use equal weights;
   - thereafter weight_j proportional to 1 / prior DEV MAE_j;
   - no target-t outcome enters target-t weight calculation.

Primary selection metric:
- DEV price SumAE.

Secondary:
- direction correct,
- MAE/RMSE/MAPE/WAPE,
- relative MAE vs RW,
- yearly SumAE,
- worst month.

## Not yet authorized
- optimized/simplex weights,
- arbitrary component subset search,
- learned stacking,
- shrinkage,
- 2025 holdout,
- 2026 evaluation.

Stage E2 learned/simplex weights may be opened only after E1 results are reported.

## Control and compliance
- Pool frozen before ensemble evaluation: PASS.
- 2025 excluded: PASS.
- 2026 quarantined: PASS.
- RF excluded from final Boosting family: PASS.
- Arbitrary subset search: NONE.
