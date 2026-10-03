# RTE-H3 V2B — SLOW-BURN TRANSITION PERIOD-CORRECTED PREREGISTRATION

**Date:** 2026-10-03  
**Identity:** `RTE_SB_H3_V2B`  
**Branch:** `gold-h3-rte-v2-20261003`  
**Status:** **PERIOD ALLOCATION CORRECTION BEFORE 2025/2026 OPENING**

## Why V2B exists

RTE V2 attempted to use 2023 as a standalone design period. Because the origin-safe V1 estimator requires 100 matured V5-continuation rows and V5 history begins late in 2022, only **12 eligible V1 predictions** existed in 2023.

That is inadequate for a six-rule design family.

This is a sample-availability correction, not a rule redesign.

No V2 slow-burn constant or rule family changes:
- previous pRTE floor = 0.60
- dpRTE ceiling = 0.05
- base thresholds = [0.70, 0.75, 0.80]
- options modes = NONE / EITHER

## Corrected chronology

- 2023-2024: DEVELOPMENT / rule selection
- 2025: untouched external confirmation
- 2026: final holdout only after 2025 PASS

This matches the original RTE V1 period contract and preserves 2025/2026 as unseen for V2B rule selection.

## DEV selection

Use the same six frozen rules over the full 2023-2024 eligible V1 prediction universe.

Eligibility:
- candidate count >= 10
- net rescue > 0
- rescue precision >= 0.55
- candidate rate <= 0.25

Selection:
1. maximum net rescue
2. higher rescue precision
3. more rescued
4. lower candidate rate
5. higher base threshold
6. EITHER as final tie-break

No eligible rule => `NO_ELIGIBLE_RTE_V2B_RULE`.

## 2025 confirmation

Only the selected DEV rule may be used.

PASS requires:
- net rescue >= +2
- rescue precision >= 0.55
- candidate rate <= 0.25
- assisted accuracy > V5 accuracy on the same eligible universe

FAIL => 2026 remains unopened.

## 2026

Only after 2025 PASS. No post-holdout tuning.

## Governance

V2B is still a DEV-developed successor because the slow-burn hypothesis came from V1 2023-2024 diagnostics. Its independent evidence begins in 2025.
