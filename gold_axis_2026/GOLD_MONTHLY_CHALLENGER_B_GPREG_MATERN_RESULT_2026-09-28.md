# GOLD MONTHLY FORECAST — CHALLENGER B / GPREG-MATERN V1 RESULT

**Date:** 2026-09-28  
**Status:** COMPLETE / SCIENTIFIC GATE PASS / NOT PROMOTED  
**Workflow run:** 36434603455  
**Commit:** d2d058b54ab8c36256d5d76ad2d4382430f43f42  
**Freeze:** `GOLD_MONTHLY_CHALLENGER_B_GPREG_MATERN_FREEZE_2026-09-28.md`

## Provenance
Faithful transfer of the prior Grup-ARGE / GA111 GPR-Matérn structure:
- StandardScaler on X only, fitted inside training fold.
- ConstantKernel × Matérn.
- normalize_y=True.
- optimizer=None.
- random_state=42.
- Exact prior grid:
  - length_scale [0.5, 1.0, 2.0, 5.0]
  - signal_scale [1.0]
  - alpha [0.001, 0.01, 0.1]
  - nu [0.5, 1.5, 2.5]

## B0 / governance
PASS.
- CURRENT8 frozen representation.
- Exact-origin GPR PIT chronology.
- Random split: NONE.
- DB READ_ONLY.
- Authority invariants unchanged.
- 2025 LOCKED_REPORT_ONLY.
- 2026 QUARANTINED_REPORT_ONLY.

## DEV — selection authority, 2022-04..2024-12
- n = 33
- SigmaAE = **1637.916541466211**
- MAE = **49.633834589885176**
- RMSE = **60.95866299590596**
- MAPE = **2.4206191498178216%**
- WAPE = **2.4103745887456127%**
- Direction = **19/33 = 57.58%**
- Relative MAE vs Random Walk = **0.9316931407657627**
- Random-Walk SigmaAE = **1758.0**
- Worst AE = **158.59865379528765**, 2024-11
- Mean predictive std in Gold log-return space = **0.020253120183946663**

### Kernel selection finding
Every DEV origin selected **nu = 2.5**. Under the frozen prior Grup-ARGE grid, the smoother Matérn kernel was consistently preferred to nu=0.5 and nu=1.5.

This is a descriptive DEV result only; it does not authorize post-hoc narrowing or tuning from 2025/2026.

## RBF vs Matérn
| Model | DEV SigmaAE | Direction |
|---|---:|---:|
| GPReg-Matérn V1 | **1637.916541** | **19/33** |
| GPReg-RBF V1 | 1696.336504 | 16/33 |

Matérn improves on RBF by approximately **58.42 SigmaAE** and **3 correct directions**, but both remain noncompetitive versus the current leading families.

## Cross-family placement
GPReg-Matérn is price-error rank **14/15** in the frozen comparison pool. GPReg-RBF is below it.

GPReg-Matérn is Pareto-dominated by:
- ChHHO-ANFIS
- RBFNN DE-ABC
- PLS1 V1
- GPR/MOGP LMC2_RBF_M32
- FULL7 Equal ANN Ensemble
- REDUCED4 Equal ANN Ensemble
- SVR frozen parent
- CatBoost PRICE
- PLS2 V1
- Random Forest
- Ridge V1
- Huber V1

Therefore it does not enter the active two-objective frontier.

## Challenger-B internal price-error ordering
1. PLS1 V1 — 1420.03 / 20
2. PLS2 V1 — 1489.33 / 23
3. Ridge V1 — 1520.99 / 21
4. Huber V1 — 1530.13 / 20
5. Elastic Net V1 — 1590.36 / 16
6. GPReg-Matérn V1 — **1637.92 / 19**
7. GPReg-RBF V1 — 1696.34 / 16

## 2025 — LOCKED REPORT ONLY
- SigmaAE = **1084.1128318717142**
- MAE = **90.34273598930952**
- RMSE = **119.5225483876634**
- Direction = **9/12 = 75.00%**
- Relative MAE vs RW = **0.6426276418919468**

Not used for selection/tuning/promotion.

## 2026 Jan-Jul — QUARANTINED REPORT ONLY
- SigmaAE = **1766.2056264067915**
- MAE = **252.31508948668449**
- RMSE = **304.9624942518192**
- Direction = **3/7 = 42.86%**
- Relative MAE vs RW = **1.0652627421030105**

In this quarantined period it is worse than Random Walk on cumulative absolute error.

## Decision
**NOT PROMOTED.**

Matérn is clearly better than the faithfully transferred RBF Gaussian Process, but neither single-output GP formulation is competitive with the current Challenger-A leaders or with PLS1/PLS2 under CURRENT8.

Existing Gold Monthly / Challenger-A path remains unchanged.

Result payload SHA256:
`a073924f1754c57c28c25979e2210bf0cdad56196fb0b92b91a0acc1a38a93a1`
