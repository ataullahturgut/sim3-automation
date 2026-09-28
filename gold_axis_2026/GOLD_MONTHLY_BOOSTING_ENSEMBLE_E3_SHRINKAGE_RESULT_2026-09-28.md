# GOLD MONTHLY FORECAST — BOOSTING ENSEMBLE E3 CONTROLLED SHRINKAGE RESULT

Date: 2026-09-28
Status: COMPLETE / SCIENTIFIC GATE PASS

## Frozen protocol
- Pools: FULL5 and REDUCED4 only.
- Shrinkage: w_alpha(t) = (1-alpha) * w_equal + alpha * w_simplex(t).
- Alpha grid: 0.00, 0.10, 0.25, 0.50, 0.75, 1.00.
- E2 simplex weights remain expanding-prequential and prior-only.
- E1 MEDIAN remains a separate frozen comparator.
- 2025 NOT OPENED.
- 2026 QUARANTINED / NOT USED.
- DB READ_ONLY.

## Results

### FULL5

| Alpha | SigmaAE | Direction | Delta vs E1 Median | Beats Median |
|---:|---:|---:|---:|---|
| 0.00 | 1503.458115 | 21/33 | +18.726785 | NO |
| 0.10 | 1506.358156 | 21/33 | +21.626825 | NO |
| 0.25 | 1510.708217 | 21/33 | +25.976887 | NO |
| 0.50 | 1517.958319 | 21/33 | +33.226988 | NO |
| 0.75 | 1525.208421 | 20/33 | +40.477090 | NO |
| 1.00 | 1532.458523 | 19/33 | +47.727192 | NO |

- Best learned alpha: **0.10**
- Best learned SigmaAE: **1506.358156**
- Best learned direction: **21/33**
- Decision: **LEARNED_WEIGHTS_CLOSED_NOT_PROMOTED**

### REDUCED4

| Alpha | SigmaAE | Direction | Delta vs E1 Median | Beats Median |
|---:|---:|---:|---:|---|
| 0.00 | 1512.863861 | 20/33 | +22.211599 | NO |
| 0.10 | 1514.003270 | 20/33 | +23.351008 | NO |
| 0.25 | 1515.712384 | 20/33 | +25.060122 | NO |
| 0.50 | 1518.560908 | 20/33 | +27.908646 | NO |
| 0.75 | 1521.409431 | 19/33 | +30.757169 | NO |
| 1.00 | 1524.257955 | 18/33 | +33.605693 | NO |

- Best learned alpha: **0.10**
- Best learned SigmaAE: **1514.003270**
- Best learned direction: **20/33**
- Decision: **LEARNED_WEIGHTS_CLOSED_NOT_PROMOTED**

## Family status after E3

- CATBOOST_PRICE reference: 1460.433935 / 20/33.
- FULL5 MEDIAN reference: 1484.731331 / 23/33.

No learned shrinkage candidate beats its frozen E1 median comparator on DEV SigmaAE. Learned-weight ensemble optimization is therefore closed. Proceed to final Boosting robustness with CATBOOST_PRICE and E1 FULL5 MEDIAN as the principal challengers.

## Reproducibility
- Payload SHA256: 563201ef6ec459c61e36d0c17f244112aaab256b80b794714b9305efbdeae0fb

## Kontrol ve Uyum Özeti
- E3 freeze respected: PASS.
- Frozen alpha grid unchanged: PASS.
- Alpha=0 identity to E1 equal: PASS.
- Alpha=1 identity to E2 raw simplex: PASS.
- Component metrics exact reconciliation: PASS.
- 2025 opened: NO.
- 2026 used: NO.
- Random split: NONE.
- DB mutation: NONE / READ_ONLY.
