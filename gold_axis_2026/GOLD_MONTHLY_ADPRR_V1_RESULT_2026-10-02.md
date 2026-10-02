# GOLD MONTHLY — ADPRR-v1 RESULT

Asymmetric Direction-Preserving Reliability Router. Technical source-contract correction applied before any scientific result existed.

## DEV 2022-04..2024-12

| Model | ΣAE USD | Direction | Balanced acc | UP recall | DOWN recall | Min-side recall | Overrides |
|---|---:|---:|---:|---:|---:|---:|---:|
| PLS1 anchor replay | 1420.03 | 21/33 (63.64%) | 63.24% | 76.47% | 50.00% | 50.00% | 0 |
| ADPRR-v1 | 1407.38 | 22/33 (66.67%) | 66.36% | 76.47% | 56.25% | 56.25% | 1 |

Direction rescues / damages: **1 / 0**.
AE-beneficial / AE-harmful overrides: **1 / 0**.
Threshold counts: \`{"0.02": 1, "0.05": 5, "0.08": 12, "0.12": 7, "0.25": 8}\`.

## Reporting only

| Period | Model | ΣAE USD | Direction | Balanced acc | UP recall | DOWN recall | Overrides |
|---|---|---:|---:|---:|---:|---:|---:|
| 2025 | PLS1 | 1058.90 | 10/12 | 90.91% | 81.82% | 100.00% | 0 |
| 2025 | ADPRR-v1 | 1108.67 | 9/12 | 86.36% | 72.73% | 100.00% | 1 |
| 2026 Jan-Jul | PLS1 | 1392.69 | 6/7 | 90.00% | 100.00% | 80.00% | 0 |
| 2026 Jan-Jul | ADPRR-v1 | 1392.69 | 6/7 | 90.00% | 100.00% | 80.00% | 0 |

## Frozen reference frontier

| Model | DEV ΣAE | Direction |
|---|---:|---:|
| ADPRR_V1 | 1407.38 | 22/33 |
| ChHHO_ANFIS | 1413.03 | 23/33 |
| DE_ABC_RBFNN | 1415.84 | 25/33 |
| PLS1_ANCHOR_REPLAY | 1420.03 | 21/33 |
| FULL7_ANN | 1428.86 | 22/33 |
| REDUCED4_ANN | 1431.46 | 24/33 |

2025/2026 were report-only and did not alter ADPRR-v1.
