# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 2A KERNEL ABLATION

Date: 2026-09-28
Status: **COMPLETE / SCIENTIFIC GATE PASS**

## Protocol
- DEV only: 2022-04..2024-12, n=33.
- CURRENT8 unchanged.
- Training-only X/Y standardization.
- epsilon-SVR, fixed C=1.0 and epsilon=0.1.
- Kernels: linear, RBF, polynomial degree 2, polynomial degree 3, sigmoid.
- RBF/poly/sigmoid gamma=scale; poly/sigmoid coef0=0.
- No hyperparameter tuning.
- 2025 opened: NO. 2026 used: NO. Random split: NONE. DB: READ_ONLY.

## DEV ranking

| Rank | Model | SigmaAE | MAE | RMSE | MAPE | Rel.MAE/RW | Direction | Worst month |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | RBF_SVR | 1524.500568 | 46.196987 | 61.849758 | 2.2348% | 0.867179 | 21/33 | 2024-03 |
| 2 | LINEAR_SVR | 1535.115953 | 46.518665 | 60.039956 | 2.2931% | 0.873217 | 19/33 | 2024-03 |
| 3 | POLY2_SVR | 1793.247438 | 54.340831 | 71.241275 | 2.6217% | 1.020050 | 17/33 | 2024-04 |
| 4 | POLY3_SVR | 1810.349586 | 54.859078 | 66.356466 | 2.7121% | 1.029778 | 17/33 | 2023-03 |
| 5 | SIGMOID_SVR | 2784.332441 | 84.373710 | 115.343307 | 4.1869% | 1.583807 | 15/33 | 2023-03 |

## Decision
- Stage 2A kernel leader: **RBF_SVR**.
- This is not yet META_PARENT_SVR; Stage 2B and 2C remain mandatory.
- No kernel is dropped from historical record.

## Kontrol ve Uyum Özeti
- Stage 1 linear/RBF reconciliation: PASS.
- DEV-only: PASS.
- Fixed canonical hyperparameters: PASS.
- Training-only scaling: PASS.
- Determinism: PASS.
- 2025 opened: NO.
- 2026 used: NO.
- Random split: NONE.
- DB mutation: NONE / READ_ONLY.
- Payload SHA256: 009344e607f5e509c33cee79aee3ffc4d8aba31c1434b675490d6b0a11ffdb58
