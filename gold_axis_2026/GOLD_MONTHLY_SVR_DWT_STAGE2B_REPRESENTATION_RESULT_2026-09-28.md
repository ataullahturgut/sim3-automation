# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 2B REPRESENTATION ABLATION

Date: 2026-09-28
Status: **COMPLETE / SCIENTIFIC GATE PASS**

## Protocol
- RBF epsilon-SVR frozen from Stage 2A.
- C=1.0, epsilon=0.1, gamma=scale.
- Training-only X/Y standardization.
- Common training-history start: 2010-05 for representation fairness.
- DEV only 2022-04..2024-12.
- Representations: CURRENT8, RAW_LEVEL_LAGS8, SIMPLE_RETURNS8, DAILY_SUMMARY12, MIXED20.
- No hyperparameter tuning.
- 2025 opened: NO. 2026 used: NO. Random split: NONE. DB: READ_ONLY.

## DEV ranking

| Rank | Representation | Dim | SigmaAE | MAE | RMSE | MAPE | Rel.MAE/RW | Direction | Worst month |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | DAILY_SUMMARY12 | 12 | 1449.187363 | 43.914769 | 59.388776 | 2.1700% | 0.824339 | 19/33 | 2024-11 |
| 2 | CURRENT8 | 8 | 1518.897044 | 46.027183 | 61.854269 | 2.2276% | 0.863991 | 21/33 | 2024-03 |
| 3 | MIXED20 | 20 | 1579.308304 | 47.857827 | 61.076928 | 2.3442% | 0.898355 | 17/33 | 2024-03 |
| 4 | RAW_LEVEL_LAGS8 | 8 | 1800.428613 | 54.558443 | 68.657168 | 2.6388% | 1.024135 | 18/33 | 2024-04 |
| 5 | SIMPLE_RETURNS8 | 8 | 1850.543554 | 56.077077 | 66.933570 | 2.7373% | 1.052641 | 17/33 | 2022-07 |

## Decision
- Stage 2B representation leader under frozen RBF baseline: **DAILY_SUMMARY12**.
- No META_PARENT_SVR is frozen yet; Stage 2C formulation remains mandatory.
- All representation outcomes remain in the ledger even if weak.

## Kontrol ve Uyum Özeti
- Kernel frozen before representation outcomes: PASS.
- Common training history: PASS.
- Training-only scaling: PASS.
- DEV-only: PASS.
- Determinism: PASS.
- 2025 opened: NO.
- 2026 used: NO.
- Random split: NONE.
- DB mutation: NONE / READ_ONLY.
- Payload SHA256: 4430712c7284e2978b496429528116f61e1fda4f217ca2f399dbf68bc049303b
