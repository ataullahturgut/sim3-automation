# GOLD MONTHLY FORECAST — BOOSTING ENSEMBLE E1 BASELINES RESULT

Date: 2026-09-28
Status: COMPLETE / SCIENTIFIC GATE PASS

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

Pool freeze occurred before any ensemble result was computed.

## Authorized E1 variants
- EQUAL_MEAN
- MEDIAN
- PREQUENTIAL_INVERSE_MAE
- optimized/simplex weights were NOT run.

DEV only: 2022-04..2024-12, n=33.
2025: NOT OPENED.
2026: QUARANTINED / NOT USED.
Random split: NONE.
DB: READ_ONLY.

## Overall E1 ranking

| Rank | Pool | Variant | SumAE | Direction |
|---:|---|---|---:|---:|
| 1 | FULL5 | MEDIAN | 1484.731330609916 | 23/33 |
| 2 | REDUCED4 | MEDIAN | 1490.652261957533 | 22/33 |
| 3 | FULL5 | EQUAL_MEAN | 1503.458115374356 | 21/33 |
| 4 | FULL5 | PREQUENTIAL_INVERSE_MAE | 1503.717374495322 | 21/33 |
| 5 | REDUCED4 | EQUAL_MEAN | 1512.863860829353 | 20/33 |
| 6 | REDUCED4 | PREQUENTIAL_INVERSE_MAE | 1513.307298935892 | 20/33 |

## Best E1: FULL5 MEDIAN

Metrics:
- DEV SumAE: 1484.731330609916
- MAE: 44.9918585033
- RMSE: 58.3000739012
- MAPE: 2.1899869452%
- WAPE: 2.1849456794%
- relative MAE vs RW: 0.8445570709
- direction: 23/33 = 69.70%
- worst AE: 141.1046292520 (2024-11)

Yearly:
- 2022: SumAE 400.8910952267, direction 7/9
- 2023: SumAE 423.4845687955, direction 6/12
- 2024: SumAE 660.3556665877, direction 10/12

## Comparison with individual leaders

CATBOOST_PRICE:
- SumAE 1460.433935309605
- direction 20/33

CATBOOST_BALANCED:
- SumAE 1481.261937710369
- direction 22/33

FULL5 MEDIAN:
- SumAE 1484.731330609916
- direction 23/33

Interpretation:
- FULL5 MEDIAN does NOT beat the family price leader.
- Price gap versus CATBOOST_PRICE = +24.297395300311 SumAE (~1.66% worse).
- It gains +3 correct directions versus CATBOOST_PRICE.
- It gains +1 direction versus CATBOOST_BALANCED while being only +3.469392899547 SumAE worse.
- This is a genuine balance/complementarity signal, not a new price champion.

## Equal vs inverse-MAE result

FULL5:
- Equal: 1503.458115374356 / 21/33
- Prequential inverse-MAE: 1503.717374495322 / 21/33

REDUCED4:
- Equal: 1512.863860829353 / 20/33
- Prequential inverse-MAE: 1513.307298935892 / 20/33

Inverse-MAE weighting does not improve the equal-weight benchmark.

Final all-DEV inverse-MAE weights are close to uniform and are context only:
FULL5:
- CATBOOST_PRICE 0.20919
- CATBOOST_BALANCED 0.20625
- GBRT 0.20361
- LIGHTGBM 0.19908
- XGB_DIRECTION 0.18187

REDUCED4:
- CATBOOST_PRICE 0.26355
- GBRT 0.25652
- LIGHTGBM 0.25081
- XGB_DIRECTION 0.22912

## Decision

1. CATBOOST_PRICE remains the provisional Boosting family PRICE champion.
2. FULL5 MEDIAN is retained as the provisional BALANCE / DIRECTION ensemble challenger.
3. Equal mean is not promoted over the median.
4. Prequential inverse-MAE is not promoted.
5. No arbitrary subset search is authorized.
6. E2 constrained/simplex weighting may now be considered because E1 demonstrated real component complementarity, but it must use chronological expanding meta-evaluation and must not use same-sample fitted weights as honest DEV evidence.
7. 2025 remains closed.

## Reproducibility
GitHub Actions run: 36384759464
Job: 108807711065
Payload SHA256: eab54ad416fa2396e973e273983192c06d4863749334132d72e0db07e21b5ec1
Scientific gate: BOOSTING_ENSEMBLE_E1_GATE=PASS

## Kontrol ve Uyum Özeti
- Pool freeze before ensemble evaluation: PASS.
- Component reconciliation: PASS.
- E1 variants only: PASS.
- Optimized simplex run: NO.
- Subset search: NONE.
- 2025 opened: NO.
- 2026 used: NO.
- Random split: NONE.
- DB writes: NONE.
