# GOLD MONTHLY FORECAST — BOOSTING E4 FINAL ROBUSTNESS RESULT

Date: 2026-09-28
Status: COMPLETE / SCIENTIFIC GATE PASS

## Principal candidates

| Role | Candidate | SigmaAE | Direction | MAE | Worst month | Worst AE |
|---|---|---:|---:|---:|---|---:|
| PRICE | CATBOOST_PRICE | 1460.433935 | 20/33 | 44.255574 | 2024-03 | 137.162760 |
| BALANCE / DIRECTION | FULL5_MEDIAN | 1484.731331 | 23/33 | 44.991859 | 2024-11 | 141.104629 |

## Year-by-year

### CATBOOST_PRICE

| Year | SigmaAE | MAE | Direction |
|---|---:|---:|---:|
| 2022 | 381.562198 | 42.395800 | 7/9 |
| 2023 | 419.833524 | 34.986127 | 6/12 |
| 2024 | 659.038214 | 54.919851 | 7/12 |

### FULL5_MEDIAN

| Year | SigmaAE | MAE | Direction |
|---|---:|---:|---:|
| 2022 | 400.891095 | 44.543455 | 7/9 |
| 2023 | 423.484569 | 35.290381 | 6/12 |
| 2024 | 660.355667 | 55.029639 | 10/12 |

## Pairwise monthly AE
- CATBOOST_PRICE wins: **14**
- FULL5_MEDIAN wins: **7**
- Ties: **12**

## Direction rescue / loss relative to CATBOOST_PRICE
- Median rescues: **3**
- Median losses: **0**
- Both correct: **20**
- Both wrong: **10**

## Worst-month sensitivity

### CATBOOST_PRICE
- Removed month: **2024-03**
- Removed AE: **137.162760**
- Remaining n=32 SigmaAE: **1323.271175**
- Remaining n=32 MAE: **41.352224**

### FULL5_MEDIAN
- Removed month: **2024-11**
- Removed AE: **141.104629**
- Remaining n=32 SigmaAE: **1343.626701**
- Remaining n=32 MAE: **41.988334**

## Common leave-one-origin sensitivity
- CATBOOST_PRICE preferred: **33 / 33 omissions**
- FULL5_MEDIAN preferred: **0 / 33 omissions**
- Ties: **0**

## FULL5 leave-one-component-out diagnostic only

| Omitted component | SigmaAE | Direction | Delta vs FULL5 Median |
|---|---:|---:|---:|
| CATBOOST_PRICE | 1498.541391 | 22/33 | +13.810060 |
| CATBOOST_BALANCED | 1490.652262 | 22/33 | +5.920931 |
| GBRT | 1492.031436 | 22/33 | +7.300106 |
| LIGHTGBM | 1470.028613 | 22/33 | -14.702718 |
| XGB_DIRECTION | 1471.504805 | 21/33 | -13.226525 |

## Stability summary

| Candidate | Monthly AE std | Median AE | Yearly MAE range | Yearly MAE std |
|---|---:|---:|---:|---:|
| CATBOOST_PRICE | 37.193759 | 35.094403 | 19.933724 | 8.226708 |
| FULL5_MEDIAN | 37.076020 | 36.563137 | 19.739258 | 8.063758 |

## E4 decision
Robustness is diagnostic only and does not perform post-hoc model reselection.

- E4 scientific/integrity gate: **PASS**
- Proceed to E5 final Boosting freeze.
- PRICE role remains **CATBOOST_PRICE**.
- BALANCE / DIRECTION role remains **FULL5_MEDIAN**.

## Reproducibility
- Payload SHA256: 68d6179d97442831da5b83573c67c43c44997a7cc1805e7999bc5a5a83b19bce

## Kontrol ve Uyum Özeti
- Frozen predictions exact reconciliation: PASS.
- DEV scope 2022-04..2024-12, n=33: PASS.
- Robustness-only diagnostics: PASS.
- Leave-one-component-out used for reselection: NO.
- 2025 opened: NO.
- 2026 used: NO.
- Random split: NONE.
- DB mutation: NONE / READ_ONLY.
