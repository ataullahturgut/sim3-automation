# GOLD MONTHLY FORECAST — CHALLENGER B / GPREG-RBF V1 RESULT

**Date:** 2026-09-28  
**Status:** COMPLETE / SCIENTIFIC GATE PASS / NOT PROMOTED  
**Workflow run:** 36434174432  
**Commit:** b97f2a9a894923d09493378d25305ce59ad699b1  
**Freeze:** `GOLD_MONTHLY_CHALLENGER_B_GPREG_RBF_FREEZE_2026-09-28.md`

## Provenance
This run preserves the prior Grup-ARGE GPR-RBF implementation pattern:
- StandardScaler on X only, fitted on training data.
- Kernel = ConstantKernel(signal_scale, fixed) * RBF(length_scale, fixed).
- GaussianProcessRegressor(normalize_y=True, optimizer=None, random_state=42).
- Grid: length_scale [0.5,1,2,5] × signal_scale [0.5,1,2] × alpha [1e-4,1e-3,1e-2,1e-1].

## B0 / governance
PASS.
- CURRENT8 frozen predictors.
- Exact-origin GPR PIT chronology.
- Random split: NONE.
- DB: READ_ONLY.
- Authority invariants unchanged.
- 2025 locked report-only.
- 2026 quarantined report-only.

## DEV — 2022-04..2024-12
- n = 33
- SigmaAE = **1696.3365035638303**
- MAE = **51.40413647163122**
- RMSE = **62.251096447265134**
- MAPE = **2.514479649976976%**
- WAPE = **2.496345997270208%**
- Direction = **16/33 = 48.48%**
- Relative MAE vs Random Walk = **0.9649240634606543**
- Random-Walk SigmaAE = **1758.0**
- Worst AE = **140.99548743519904**, 2024-03
- Mean predictive std in Gold log-return space = **0.01159556711697004**

## Cross-family DEV comparison
GPReg-RBF V1 is price-error rank **14/14** in the frozen comparison pool.

It is Pareto-dominated by every other model in the pool, including:
- ChHHO-ANFIS
- RBFNN DE-ABC
- PLS1
- GPR/MOGP LMC2
- ANN ensembles
- SVR
- CatBoost
- PLS2
- Random Forest
- Ridge
- Huber
- Elastic Net

Therefore it does not enter the active Challenger-A / Challenger-B frontier.

## 2025 — LOCKED REPORT ONLY
- SigmaAE = **1069.249363481822**
- MAE = **89.10411362348516**
- RMSE = **117.5764163337166**
- Direction = **10/12 = 83.33%**
- Relative MAE vs RW = **0.6338170500781399**

This cannot rescue or promote the model.

## 2026 Jan-Jul — QUARANTINED REPORT ONLY
- SigmaAE = **1726.5319270555556**
- MAE = **246.64741815079364**
- RMSE = **290.53441319636**
- Direction = **3/7 = 42.86%**
- Relative MAE vs RW = **1.0413340935196354**

In this quarantined period the model is worse than Random Walk on cumulative absolute error.

## Decision
**NOT PROMOTED.**

The RBF Gaussian Process formulation, as faithfully transferred from the prior Grup-ARGE implementation and evaluated under the frozen Gold CURRENT8 protocol, does not provide competitive DEV performance.

Proceed to the separately frozen GPReg-Matérn challenger next; do not tune Matérn using GPReg-RBF 2025/2026 evidence.

Result payload SHA256:
`435a1ae7bc95789afa16ef0a00ef14327e2cd4627715eae9f84f81356d1b9381`
