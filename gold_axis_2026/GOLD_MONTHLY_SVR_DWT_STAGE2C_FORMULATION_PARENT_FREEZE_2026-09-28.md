# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 2C FORMULATION CHECK

Date: 2026-09-28
Status: **COMPLETE / SCIENTIFIC GATE PASS / META_PARENT_SVR FROZEN**

## Frozen comparison protocol
- Kernel: RBF, frozen from Stage 2A.
- Representation: DAILY_SUMMARY12, frozen from Stage 2B.
- Training-only X/Y standardization.
- Common history start: 2010-05.
- epsilon-SVR: C=1, epsilon=0.1, gamma=scale.
- NuSVR: C=1, nu=0.5, gamma=scale.
- DEV only 2022-04..2024-12.
- No hyperparameter tuning.
- 2025 opened: NO. 2026 used: NO. Random split: NONE. DB: READ_ONLY.

## DEV ranking

| Rank | Model | SigmaAE | MAE | RMSE | MAPE | Rel.MAE/RW | Direction | Worst month |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | EPSILON_RBF_DAILY12 | 1449.187363 | 43.914769 | 59.388776 | 2.1700% | 0.824339 | 19/33 | 2024-11 |
| 2 | NU_RBF_DAILY12 | 1525.433400 | 46.225255 | 59.783825 | 2.2774% | 0.867710 | 18/33 | 2024-03 |

## Stage 2 decision / parent freeze
- Frozen META_PARENT_SVR: **EPSILON_RBF_DAILY12**.
- Parent identity is frozen before Stage 3 hyperparameter outcomes.
- Stage 3 may refine only the parent formulation under the predeclared chronological tuning protocol.
- Stage 4 32/32 metaheuristics will use the Stage-3-frozen parent and bounds.

## Kontrol ve Uyum Özeti
- Kernel freeze before formulation outcome: PASS.
- Representation freeze before formulation outcome: PASS.
- DEV-only: PASS.
- Training-only scaling: PASS.
- Determinism: PASS.
- META_PARENT_SVR frozen before Stage 3: PASS.
- 2025 opened: NO.
- 2026 used: NO.
- Random split: NONE.
- DB mutation: NONE / READ_ONLY.
- Payload SHA256: 5a85e126c827740e04914c4eba3cd4afaf45b67e89c0a9bc361b64fef66d9b29
