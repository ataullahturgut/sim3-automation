# GOLD CONTROL — VLMC ADAPTIVE META V1 RESULT

**Date:** 2026-09-19  
**Identity:** `DIRECTION_VLMC_ADAPTIVE_META_V1_RESEARCH`  
**Status:** `EVALUATED / NO_PROMOTION / ADAPTIVE_META_LAYER_FAILED_TO_IMPROVE_GENERALIZATION`  
**Evidence class:** `RETROSPECTIVE_TIME_ORDERED_NOT_PRISTINE`

## 1. Parent reference

Corrected native VLMC-BS V2 remains the comparison authority:

- 2024 common-support k=52: accuracy 0.6364, balanced accuracy 0.6292;
- 2025 k=104: accuracy 0.6154, balanced accuracy 0.5514, DOWN sensitivity 0.4000.

The development question is whether adaptive expert tracking across k=26/52/104 can make the family more stable when the best memory length changes over time.

## 2. Fixed-Share

2023 development, using k=26/52:
- selected eta = 1;
- selected alpha = 0.05;
- n = 43;
- accuracy = 0.6047;
- balanced accuracy = 0.6184;
- UP sensitivity = 0.5000;
- DOWN sensitivity = 0.7368.

2024 fair validation, k=26/52/104, target weeks from 2024-03-04:
- n = 44;
- accuracy = 0.5682;
- balanced accuracy = 0.5667;
- UP sensitivity = 0.5833;
- DOWN sensitivity = 0.5500;
- Brier = 0.2852.

Locked-rule 2025 retrospective replay:
- n = 52;
- accuracy = 0.5000;
- balanced accuracy = 0.4108;
- UP sensitivity = 0.6216;
- DOWN sensitivity = 0.2000;
- TP/TN/FP/FN = 23/3/12/14;
- always-UP raw baseline = 0.7115.

Frozen 19-event diagnostic:
- raw direction agreement = 12/19 = 0.6316;
- balanced event-direction accuracy = 0.4929;
- UP events = 11/14;
- DOWN events = 1/5.

Conclusion: Fixed-Share does not improve the native VLMC family. It degrades both pre-2025 validation and 2025 replay.

## 3. Fading recent-best expert

2023 development:
- selected rho = 0.90;
- n = 43;
- accuracy = 0.6047;
- balanced accuracy = 0.6184;
- DOWN sensitivity = 0.7368.

2024 validation:
- n = 53;
- accuracy = 0.5660;
- balanced accuracy = 0.5634;
- UP sensitivity = 0.7037;
- DOWN sensitivity = 0.4231.

Locked-rule 2025 retrospective replay:
- n = 52;
- accuracy = 0.5192;
- balanced accuracy = 0.4243;
- UP sensitivity = 0.6486;
- DOWN sensitivity = 0.2000;
- TP/TN/FP/FN = 24/3/12/13.

Frozen 19-event diagnostic:
- raw direction agreement = 11/19 = 0.5789;
- balanced event-direction accuracy = 0.4571;
- UP events = 10/14;
- DOWN events = 1/5.

Conclusion: recent-performance fading does not stabilize VLMC across 2024->2025 and is inferior to the native k=104 2025 result.

## 4. Scientific interpretation

The hypothesis that the VLMC problem can be fixed merely by dynamically switching among 26/52/104 windows is not supported.

The evidence suggests the generalization problem is deeper than window choice:
- k=52 has real pre-2025 signal;
- k=104 is more balanced in 2025;
- adaptive expert tracking fails to transfer that complementarity into a stronger combined predictor.

Therefore no adaptive meta-layer is promoted.

The literature search also identified direct non-stationary context-tree methods such as Adaptive Context Tree Weighting (ACTW), which discounts older observations inside the context estimator itself rather than merely switching among fixed-window experts. That is a structurally different successor and overlaps the separate BCT/CTW research family; it is not silently introduced under this VLMC identity.

## 5. Binding status

`DIRECTION_VLMC_ADAPTIVE_META_V1_RESEARCH = EVALUATED / NO_PROMOTION / ADAPTIVE_META_LAYER_FAILED_TO_IMPROVE_GENERALIZATION / NOT_RUNTIME / NOT_PRODUCTION_AUTHORITY`.

Parent `DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH` remains `NO_PROMOTION / 2025_GENERALIZATION_WEAK`.
