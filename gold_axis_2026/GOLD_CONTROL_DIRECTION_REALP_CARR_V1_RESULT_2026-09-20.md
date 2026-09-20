# GOLD CONTROL — DIRECTION_REALP_CARR_V1_RESEARCH RESULT

**Date:** 2026-09-20  
**Identity:** `DIRECTION_REALP_CARR_V1_RESEARCH`  
**Status:** `EVALUATED / NO_PROMOTION / PRE2025_VALIDATION_FAILED / REALP_BCARS_FAMILY_CLOSE_CURRENT_SEQUENCE / NOT_RUNTIME`

## Authority boundary

This experiment is NOT represented as CARB. The exact CARB mathematical specification was not proven from an accessible primary source. This experiment uses the source-verifiable Realized Probability construction plus the published CARR-filter / linear-regression predictability mechanism.

## 2024 fixed validation

- n = 53
- accuracy = 0.4716981132
- balanced accuracy = 0.4650997151
- UP sensitivity = 0.8148148148
- DOWN sensitivity = 0.1153846154
- TP/TN/FP/FN = 22/3/23/5
- forecast UP/DOWN = 45/8
- always-UP accuracy = 0.5094339623
- previous-sign accuracy = 0.5094339623
- historical-mean-RealP direction accuracy = 0.5094339623
- previous-RealP direction accuracy = 0.5094339623
- RealP R2_oos vs expanding historical mean = 0.0078420965
- RealP forecast range = 0.4902635953 .. 0.5167846348
- preregistered gate passed = FALSE

Gate components:
- accuracy_gt_always_up = FALSE
- accuracy_gt_previous_sign = FALSE
- balanced_accuracy_gte_0_55 = FALSE
- down_sensitivity_gte_0_40 = FALSE
- r2_oos_realp_gt_0 = TRUE
- up_sensitivity_gte_0_40 = TRUE

## Unchanged 2025 post-diagnostic replay

- n = 52
- accuracy = 0.6153846154
- balanced accuracy = 0.4444444444
- UP sensitivity = 0.8888888889
- DOWN sensitivity = 0.0000000000
- TP/TN/FP/FN = 32/0/16/4
- forecast UP/DOWN = 48/4
- always-UP accuracy = 0.6923076923
- previous-sign accuracy = 0.5576923077
- RealP R2_oos = -0.0559187037
- RealP forecast range = 0.4886575923 .. 0.5155125926

## Binding interpretation

The model failed the frozen 2024 gate. The unchanged 2025 replay cannot rescue the failed pre-2025 validation.

Binding current-sequence decision: close the B-CARS / Realized-Probability direction family unless the user explicitly reopens it. No CARB invention, threshold rescue, alternate CARR order, exogenous augmentation, or 2025-driven tuning is authorized.
