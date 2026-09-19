# GOLD CONTROL — DIRECTION_BCTX_AR_V1_RESEARCH RESULT

**Date:** 2026-09-19  
**Identity:** `DIRECTION_BCTX_AR_V1_RESEARCH`  
**Status:** `EVALUATED / NO_PROMOTION / PRE2025_VALIDATION_FAILED / BCT_FAMILY_CLOSE_CURRENT_SEQUENCE / NOT_RUNTIME`

## Frozen selected configuration

- m = 3
- D = 10
- beta = 0.75
- p = 1
- c1_z = -0.826725139744
- c2_z = 1.07899191595
- selected development log evidence = -124.952049681
- development scaling mean = 0.000689352355521
- development scaling sd = 0.019718573811

Hyperparameter/quantiser selection used only the development sample through 2023-12-25 and exact GCTW evidence. No 2024 or 2025 direction score entered selection.

## 2024 fixed validation

- n = 53
- accuracy = 0.5660377358
- balanced accuracy = 0.5584045584
- UP sensitivity = 0.9629629630
- DOWN sensitivity = 0.1538461538
- TP/TN/FP/FN = 26/4/22/1
- forecast UP/DOWN = 48/5
- always-UP accuracy = 0.5094339623
- previous-sign accuracy = 0.5094339623
- return RMSE = 0.0204091170
- return MAE = 0.0154812943
- pre-registered gate passed = FALSE

Gate components:
- accuracy_gt_always_up = TRUE
- accuracy_gt_previous_sign = TRUE
- balanced_accuracy_gte_0_55 = TRUE
- down_sensitivity_gte_0_40 = FALSE
- up_sensitivity_gte_0_40 = TRUE

## Unchanged 2025 post-diagnostic replay

- n = 52
- accuracy = 0.6923076923
- balanced accuracy = 0.4864864865
- UP sensitivity = 0.9729729730
- DOWN sensitivity = 0.0000000000
- TP/TN/FP/FN = 36/0/15/1
- forecast UP/DOWN = 51/1
- always-UP accuracy = 0.7115384615
- previous-sign accuracy = 0.5576923077
- return RMSE = 0.0251399789
- return MAE = 0.0203505404

## Binding interpretation

BCT-AR failed the preregistered 2024 direction gate. The unchanged 2025 replay cannot rescue the failed pre-2025 validation.

Binding current-sequence decision: close the BCT direction family after BCT/CTW V1 and this BCT-AR successor. No D/beta/window/threshold/quantiser rescue is authorized unless the user explicitly reopens the family.
