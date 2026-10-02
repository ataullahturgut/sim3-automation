# GOLD H3 — CROSS-FAMILY ERROR ANATOMY V1

Diagnostic only. No router was fit in this stage.

## DEV side-specific anatomy (2022-2024)

| Model | Accuracy | Balanced acc | UP recall | DOWN recall | Brier |
|---|---:|---:|---:|---:|---:|
| LOGIT_L2_CORE3 | 54.97% | 54.48% | 65.06% | 43.89% | 0.2466 |
| XGB_CORE3 | 53.51% | 52.95% | 65.06% | 40.83% | 0.2511 |
| VANILLA_ANFIS | 52.05% | 51.64% | 60.51% | 42.78% | 0.2511 |
| LGBM_CORE3 | 50.99% | 50.48% | 61.52% | 39.44% | 0.2528 |
| CHHHO_ANFIS | 50.20% | 49.94% | 55.44% | 44.44% | 0.2559 |

UP specialist: **LOGIT_L2_CORE3** (65.06% UP recall).
DOWN specialist: **CHHHO_ANFIS** (44.44% DOWN recall).

## Consensus

| Scope | Coverage | Accuracy | Balanced acc |
|---|---:|---:|---:|
| MAJORITY | 100.00% | 52.32% | 51.77% |
| STRONG_4_OF_5 | 70.60% | 53.28% | 52.50% |
| UNANIMOUS | 43.44% | 55.49% | 54.26% |
| DISAGREEMENT | 56.56% | 49.88% | 49.68% |

DEV all-five-wrong rows: **146**.
DEV exactly-one-correct rows: **103**.
Unique rescuer counts: \`{"CHHHO_ANFIS": 19, "LGBM_CORE3": 10, "LOGIT_L2_CORE3": 44, "VANILLA_ANFIS": 21, "XGB_CORE3": 9}\`.

## Transport headline

| Period | Model | Accuracy | Balanced acc | UP recall | DOWN recall |
|---|---|---:|---:|---:|---:|
| 2025 | LGBM_CORE3 | 56.92% | 54.93% | 63.46% | 46.39% |
| 2025 | XGB_CORE3 | 57.31% | 54.86% | 65.38% | 44.33% |
| 2025 | CHHHO_ANFIS | 53.75% | 53.53% | 54.49% | 52.58% |
| 2025 | VANILLA_ANFIS | 51.38% | 50.83% | 53.21% | 48.45% |
| 2025 | LOGIT_L2_CORE3 | 50.20% | 50.06% | 50.64% | 49.48% |
| 2026 | CHHHO_ANFIS | 50.26% | 51.21% | 71.43% | 31.00% |
| 2026 | LGBM_CORE3 | 47.64% | 48.57% | 68.13% | 29.00% |
| 2026 | XGB_CORE3 | 45.55% | 46.62% | 69.23% | 24.00% |
| 2026 | VANILLA_ANFIS | 45.03% | 45.87% | 63.74% | 28.00% |
| 2026 | LOGIT_L2_CORE3 | 43.98% | 45.21% | 71.43% | 19.00% |

State-shift, rescue-matrix and exact special-case ledgers are written to separate CSV files.
No model architecture is changed by this diagnostic.
