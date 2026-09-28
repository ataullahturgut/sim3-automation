# GOLD MONTHLY FORECAST — TIMESFM-3 ZERO-SHOT MULTIVARIATE V1 RESULT

**Date:** 2026-09-28  
**Status:** COMPLETE / SCIENTIFIC GATE PASS / NOT PROMOTED  
**Workflow run:** 36444552737  
**Commit:** 63f98687ef1269bfffe1823bfb7fb97e9f26987f  
**Freeze:** `GOLD_MONTHLY_TIMESFM3_ZERO_SHOT_V1_FREEZE_2026-09-28.md`

## Method
- Official checkpoint: `google/timesfm-3.0-pytorch`
- Package: `timesfm==3.0.2`
- Backend: PyTorch CPU
- 4-variate native multivariate context:
  - Gold monthly average
  - Silver monthly average
  - Platinum monthly average
  - Palladium monthly average
- Context starts 2010-05 and ends at the prior completed month for each origin.
- Horizon: 1 month.
- No CURRENT8 engineered features.
- No covariates.
- No external scaling.
- No fine-tuning.
- No hyperparameter tuning.
- Zero-shot only.
- Quantiles returned for diagnostics only.

## License / use status
TimesFM-3 pretrained weights are evaluated here for research only under the TimesFM Non-Commercial License v1.0. This result does not authorize production or commercial deployment of the checkpoint.

## DEV — 2022-04..2024-12
- n = 33
- SigmaAE = **1850.4112841796875**
- MAE = **56.073069217566285**
- RMSE = **67.57812110312065**
- MAPE = **2.7440277134865783%**
- WAPE = **2.723084006540553%**
- Direction = **19/33 = 57.58%**
- Relative MAE vs Random Walk = **1.0525661457222342**
- Random-Walk SigmaAE = **1758.0**
- Worst AE = **142.927490234375**, 2024-03

### DEV decision
**NOT PROMOTED.**

The canonical zero-shot raw-level multivariate TimesFM-3 setup is worse than Random Walk on the primary DEV cumulative absolute error metric and is dominated by the established leading Gold Monthly families.

Within the frozen comparison subset it ranks **11/11** by DEV SigmaAE.

Pareto dominators include:
- ChHHO-ANFIS
- RBFNN DE-ABC
- PLS1 V1
- GPR/MOGP LMC2_RBF_M32
- FULL7 ANN
- REDUCED4 ANN
- SVR frozen parent
- CatBoost PRICE
- PLS2
- Random Forest

## 2025 — LOCKED REPORT ONLY
- SigmaAE = **1467.6059472656248**
- MAE = **122.30049560546873**
- RMSE = **157.28503447079999**
- Direction = **9/12 = 75.00%**
- Relative MAE vs RW = **0.8699501762096176**
- Worst AE = **285.84015625**, 2025-09

Not used for selection or rescue.

## 2026 Jan-Jul — QUARANTINED REPORT ONLY
- SigmaAE = **1182.217041015625**
- MAE = **168.88814871651786**
- RMSE = **222.04168681898076**
- Direction = **6/7 = 85.71%**
- Relative MAE vs RW = **0.7130380223254674**
- Worst AE = **371.69677734375**, 2026-01

This transport result is substantially better than DEV, but 2026 is quarantined and cannot be used to promote or retune the model.

## Interpretation
The result does **not** establish that the TimesFM-3 family is unusable for Gold. It establishes only that the frozen canonical V1:
- raw monthly price levels,
- 4-metal native multivariate context,
- no covariates,
- no fine-tuning,
- zero-shot H=1

is not competitive under the Gold Monthly DEV authority.

A future TimesFM-3 experiment, if separately authorized, should change one design dimension at a time and freeze it before outcome. Plausible research-only directions include:
1. return-space rather than raw-level targets;
2. past-only origin-safe GPR/macro covariates;
3. a controlled Gold-only vs 4-metal multivariate representation comparison.

Those variants are **not run here**.

## Governance
- Scientific gate: PASS
- DB: READ_ONLY
- Random split: NONE
- Target-month leakage: NONE
- DEV remains the selection authority
- 2025 remains locked
- 2026 remains quarantined
- Challenger-A / Challenger-B existing paths unchanged

Result payload SHA256:
`c733cf7533a5bd00c3d77944549398cb4e6aecb47418b8483acf4f681b795e64`
