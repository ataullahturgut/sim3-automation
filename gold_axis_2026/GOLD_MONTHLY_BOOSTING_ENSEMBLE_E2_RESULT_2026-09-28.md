# GOLD MONTHLY FORECAST — BOOSTING ENSEMBLE E2 CONSTRAINED SIMPLEX RESULT

Date: 2026-09-28
Status: COMPLETE / SCIENTIFIC GATE PASS / RAW SIMPLEX NOT PROMOTED

## Protocol
Frozen pools from E1:
- FULL5 = CATBOOST_PRICE + CATBOOST_BALANCED + GBRT + LIGHTGBM + XGB_DIRECTION
- REDUCED4 = CATBOOST_PRICE + GBRT + LIGHTGBM + XGB_DIRECTION

Weights:
- non-negative
- sum to one
- no intercept
- no subset search

Objective:
- minimize cumulative absolute reconstructed-price error (SigmaAE)
- exact linear programming via scipy.optimize.linprog(method="highs")

Honest evaluation:
- DEV 2022-04..2024-12, n=33
- first 6 DEV origins equal-weight fallback
- thereafter weights fit only on strictly prior DEV origins
- current target actual excluded from current weight fitting

Governance:
- 2025 NOT OPENED
- 2026 QUARANTINED / NOT USED
- random split NONE
- DB READ_ONLY

## E1 references
CATBOOST_PRICE:
- SigmaAE 1460.433935309605
- direction 20/33

FULL5 MEDIAN:
- SigmaAE 1484.731330609916
- direction 23/33

REDUCED4 MEDIAN:
- SigmaAE 1490.6522619575326
- direction 22/33

## Honest expanding-prequential E2 results

### FULL5 simplex
- SigmaAE: 1532.4585226357096
- MAE: 46.4381370496
- RMSE: 59.4941555314
- MAPE: 2.2597815607%
- WAPE: 2.2551814990%
- relative MAE vs RW: 0.8717056443
- direction: 19/33 = 57.58%
- worst AE: 140.3461105486 (2024-11)

Yearly:
- 2022: SigmaAE 403.8986024000, direction 6/9
- 2023: SigmaAE 438.3512848455, direction 6/12
- 2024: SigmaAE 690.2086353901, direction 7/12

Versus FULL5 MEDIAN:
- SigmaAE worsened by +47.7271920258
- direction worsened 23/33 -> 19/33

### REDUCED4 simplex
- SigmaAE: 1524.257954917245
- MAE: 46.1896349975
- RMSE: 58.4174647240
- MAPE: 2.2480951860%
- WAPE: 2.2431134604%
- relative MAE vs RW: 0.8670409300
- direction: 18/33 = 54.55%
- worst AE: 136.1295702964 (2024-03)

Yearly:
- 2022: SigmaAE 404.1625866401, direction 6/9
- 2023: SigmaAE 427.6434911703, direction 6/12
- 2024: SigmaAE 692.4518771069, direction 6/12

Versus REDUCED4 MEDIAN:
- SigmaAE worsened by +33.6056929597
- direction worsened 22/33 -> 18/33

## Full-DEV fit diagnostic only

Both pools converge to the same effective solution because excluded components receive zero weight.

Weights:
- CATBOOST_PRICE: 85.3928041885%
- GBRT: 14.6071958115%
- CATBOOST_BALANCED: 0% in FULL5
- LIGHTGBM: 0%
- XGB_DIRECTION: 0%

Same-sample diagnostic:
- SigmaAE: 1458.37666981
- direction: 20/33
- MAE: 44.1932324185
- RMSE: 57.6242217303

This appears to improve CATBOOST_PRICE:
1460.4339353 -> 1458.3766698
improvement = 2.0572655 SigmaAE (~0.14%).

However this is explicitly NOT honest selection evidence because the weights were fitted on the same 33 observations used to score them.

The honest chronological result is materially worse, so the apparent 2.06-point gain is treated as meta-fit/overfit rather than a real frontier improvement.

## Decision
- FULL5 raw simplex: NOT PROMOTED.
- REDUCED4 raw simplex: NOT PROMOTED.
- CATBOOST_PRICE remains provisional PRICE champion: 1460.4339353 / 20/33.
- FULL5 MEDIAN remains provisional BALANCE/DIRECTION ensemble: 1484.7313306 / 23/33.
- No arbitrary subset search.
- No learned stacking.

Per the pre-outcome E2 freeze, the only remaining learned-weight remedy is one controlled shrinkage stage:
- shrink prior-only simplex weights toward equal weights;
- fixed alpha grid frozen before outcome;
- FULL5 and REDUCED4 only;
- median remains a separate frozen comparator;
- no 2025/2026.

If shrinkage also fails, learned ensemble weights are closed and Boosting proceeds to robustness/final freeze.

## Reproducibility
GitHub Actions run: 36385723320
Job: 108810569825
Payload SHA256: a61548f5d0ef46094e942b86ff1ed8422d2dfc5f803bb73396c8848b90cfda10
Scientific gate: BOOSTING_ENSEMBLE_E2_GATE=PASS

## Kontrol ve Uyum Özeti
- E2: PASS / COMPLETE.
- Frozen pools unchanged: PASS.
- Honest expanding-prequential evaluation: PASS.
- Full-DEV fit labeled diagnostic only: PASS.
- 2025 opened: NO.
- 2026 used: NO.
- Random split: NONE.
- Raw simplex promoted: NO.
