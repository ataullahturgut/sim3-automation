# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 1 CANONICAL BASELINE

Date: 2026-09-28
Status: **COMPLETE / SCIENTIFIC GATE PASS**

## Frozen protocol
- DEV only: 2022-04..2024-12, n=33.
- CURRENT8 origin-safe predictors.
- Single-output next-month Gold log return.
- Training-only X and y standardization.
- Price reconstruction from previous completed-month Gold average.
- epsilon-SVR; C=1.0; epsilon=0.1.
- Linear kernel and RBF kernel (gamma=scale).
- Random split: NONE.
- 2025 opened: NO.
- 2026 used: NO.
- DB: READ_ONLY.

## DEV results

| Rank | Model | SigmaAE | MAE | RMSE | MAPE | WAPE | Rel.MAE/RW | Direction | Worst month | Worst AE |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|---:|
| 1 | RBF_SVR | 1524.500568 | 46.196987 | 61.849758 | 2.2348% | 2.2435% | 0.867179 | 21/33 | 2024-03 | 158.334694 |
| 2 | LINEAR_SVR | 1535.115953 | 46.518665 | 60.039956 | 2.2931% | 2.2591% | 0.873217 | 19/33 | 2024-03 | 132.219546 |

## LINEAR_SVR yearly

| Year | SigmaAE | MAE | Direction |
|---|---:|---:|---:|
| 2022 | 435.948275 | 48.438697 | 6/9 |
| 2023 | 473.710626 | 39.475886 | 5/12 |
| 2024 | 625.457051 | 52.121421 | 8/12 |

## RBF_SVR yearly

| Year | SigmaAE | MAE | Direction |
|---|---:|---:|---:|
| 2022 | 398.120567 | 44.235619 | 7/9 |
| 2023 | 385.317157 | 32.109763 | 7/12 |
| 2024 | 741.062844 | 61.755237 | 7/12 |

## Stage 1 decision
- Canonical Stage-1 price leader: **RBF_SVR**.
- This is a baseline result only; no META_PARENT_SVR is frozen yet.
- Stage 2 kernel / representation / formulation ablations remain mandatory.
- 2025 remains locked.

## Reproducibility
- Payload SHA256: 8178e76be47d2e5c3151a1f39c6061082b0a8fdce862d53f1e9b869dd3c3d3a2
- Python: 3.12.14
- NumPy: 2.4.6
- scikit-learn: 1.9.1

## Kontrol ve Uyum Özeti
- Stage-0 authority freeze respected: PASS.
- DEV scope 2022-04..2024-12, n=33: PASS.
- Target feature construction reads t-1/t-2 only: PASS.
- Target actual read only after forecast creation: PASS.
- Training-only X/Y scaling: PASS.
- Deterministic replay: PASS.
- Finite/pathological-prediction gate: PASS.
- 2025 opened: NO.
- 2026 used: NO.
- Random split: NONE.
- DB mutation: NONE / READ_ONLY.
