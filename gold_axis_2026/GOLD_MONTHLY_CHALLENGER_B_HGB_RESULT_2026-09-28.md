# GOLD MONTHLY FORECAST — CHALLENGER B / HISTGRADIENTBOOSTING V1 RESULT

**Date:** 2026-09-28
**Status:** COMPLETE / SCIENTIFIC GATE PASS / NOT PROMOTED
**Workflow run:** 36436125036
**Commit:** a295ace0d8eea030f049b3273e2eb20b7982f9e1
**Freeze:** `GOLD_MONTHLY_CHALLENGER_B_HGB_FREEZE_2026-09-28.md`

## Provenance
This run ports the actually executed Grup-ARGE HistGradientBoosting candidates:
- HGB_A: learning_rate=0.05, max_iter=250, max_leaf_nodes=7, min_samples_leaf=12, l2_regularization=5.0
- HGB_B: learning_rate=0.10, max_iter=150, max_leaf_nodes=7, min_samples_leaf=15, l2_regularization=10.0

Gold adaptation binds `early_stopping=False` so sklearn does not create an internal holdout; all model selection remains in the explicit chronological pre-target inner validation.

## Data / governance
- CURRENT8 frozen representation.
- No scaling; tree-native engineered inputs.
- Random split: NONE.
- Exact-origin GPR PIT chronology preserved.
- DB READ_ONLY.
- Authority invariants unchanged.
- 2025 LOCKED_REPORT_ONLY.
- 2026 QUARANTINED_REPORT_ONLY.

## DEV — selection authority, 2022-04..2024-12
- n = 33
- SigmaAE = **1840.2678387980486**
- MAE = **55.76569208478935**
- RMSE = **71.01649783022977**
- MAPE = **2.6918798411185443%**
- WAPE = **2.7081568094757107%**
- Direction = **20/33 = 60.61%**
- Relative MAE vs Random Walk = **1.046796267803213**
- Random-Walk SigmaAE = **1758.0**
- Worst AE = **162.927972083648**, 2024-11

Candidate counts:
- HGB_A: 21 origins
- HGB_B: 12 origins

Under the frozen DEV protocol, HGB is worse than Random Walk on cumulative absolute price error.

## Cross-family placement
HGB V1 is price-error rank **17/17** in the frozen comparison pool.

It is Pareto-dominated by:
- ChHHO-ANFIS
- RBFNN DE-ABC
- PLS1 V1
- FULL7 Equal ANN Ensemble
- REDUCED4 Equal ANN Ensemble
- CatBoost PRICE
- PLS2 V1
- Random Forest
- Ridge V1
- Huber V1
- Extra Trees V1

It therefore does not enter the active Challenger-A / Challenger-B frontier.

## Challenger-B internal DEV ordering by SigmaAE
1. PLS1 V1 — 1420.03 / 20
2. PLS2 V1 — 1489.33 / 23
3. Ridge V1 — 1520.99 / 21
4. Huber V1 — 1530.13 / 20
5. Extra Trees V1 — 1539.92 / 20
6. Elastic Net V1 — 1590.36 / 16
7. GPReg-Matérn V1 — 1637.92 / 19
8. GPReg-RBF V1 — 1696.34 / 16
9. HGB V1 — **1840.27 / 20**

## 2025 — LOCKED REPORT ONLY
- SigmaAE = **849.6698237369146**
- MAE = **70.80581864474289**
- RMSE = **93.99498562396346**
- MAPE = **2.049491773402984%**
- Direction = **10/12 = 83.33%**
- Relative MAE vs RW = **0.5036572754812771**
- Worst AE = **208.29956102699225**, 2025-10

This is strong retrospective transport evidence but cannot rescue or promote the model because 2025 is locked.

## 2026 Jan-Jul — QUARANTINED REPORT ONLY
- SigmaAE = **1751.6230852713234**
- MAE = **250.23186932447476**
- RMSE = **308.3018329704267**
- Direction = **4/7 = 57.14%**
- Relative MAE vs RW = **1.0564674820695557**
- Worst AE = **502.22442079752454**, 2026-01

In this quarantined period HGB is again worse than Random Walk on cumulative absolute price error.

## Decision
**NOT PROMOTED.**

The faithfully transferred Grup-ARGE HGB challenger fails the DEV selection authority and is worse than Random Walk on the primary DEV error metric. Its strong 2025 retrospective result is retained as report-only evidence and is not used to alter the decision.

Existing Gold Monthly / Challenger-A path remains unchanged.

Result payload SHA256:
`2761fb4c254bc9224dd56ccd054445fade3518f92ef85cfab83dcd5825853e7c`
