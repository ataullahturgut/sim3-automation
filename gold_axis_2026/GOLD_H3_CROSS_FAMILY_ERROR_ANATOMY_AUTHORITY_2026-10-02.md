# GOLD H3 — CROSS-FAMILY ERROR ANATOMY AUTHORITY

**Date:** 2026-10-02  
**Status:** FROZEN DIAGNOSTIC BEFORE ROUTER DESIGN  
**Target:** Global XAU H3 UP/DOWN direction

## Purpose

Diagnose the near-term forecasting problem before designing a new hybrid/router.

This stage does **not** optimize a new model. It asks:

1. Which model families are relatively stronger on UP vs DOWN?
2. When models agree, is consensus materially more reliable?
3. When models disagree, does one family repeatedly rescue another?
4. Are there common-failure states in which all families fail together?
5. Which origin-known state variables are most shifted in common failures and specialist-rescue cases?
6. Does the 2025/2026 deterioration reflect a side bias, a regime shift, or both?

## Data identity

- `GLOBAL_XAU_PUBLIC_STAKTRAKR_R2`
- target: H3 direction
- DEV anatomy: 2022-2024
- transport diagnostics: 2025 and 2026 available matured targets
- 2025/2026 are diagnostic only and cannot alter any DEV-derived conclusion.

## Model panel

Five fixed H3 direction streams:

1. `LOGIT_L2_CORE3`
2. `LGBM_CORE3`
3. `XGB_CORE3`
4. `VANILLA_ANFIS`
5. `CHHHO_ANFIS`

Classical models use the same CORE3 feature block so model-family behavior is not confounded by feature-block changes.

DEV:
- chronological expanding 5-origin blocks
- only matured target labels available at each forecast block.

2025/2026:
- one strict pre-2025 fit for each model family;
- no 2025/2026 label updates.

ANFIS DEV predictions are read from their original successful workflow artifacts:
- Vanilla artifact id: `11218958789`
- ChHHO artifact id: `11219164514`.

## Required diagnostics

### Side-specific performance
For each model and period:
- accuracy
- balanced accuracy
- UP recall
- DOWN recall
- false-call rate
- Brier/log loss where probabilities exist.

### Consensus structure
For each observation:
- number of UP votes
- vote fraction
- unanimous flag
- majority direction
- majority correctness
- probability spread.

Report:
- majority-vote performance
- unanimous coverage and accuracy
- 4/5-or-stronger agreement coverage/accuracy
- disagreement performance.

### Rescue matrix
For each ordered pair A -> B:
- rows where A is wrong
- fraction B is correct
- split by actual UP and actual DOWN.

### Common failures
Identify:
- all-five-wrong observations
- exactly-one-correct observations
- exactly-one-wrong observations.

### Origin-state anatomy
Using only origin-known CORE3 variables, compare:
- common failures vs all other rows
- model-specific rescues vs ordinary rows.

Report standardized mean shifts for:
- gold_r1, gold_r3, gold_r5, gold_r10, gold_r21, sigma20
- silver_r1, silver_r5, silver_r21
- platinum_r1, platinum_r5, platinum_r21.

Age fields are retained in raw output but not ranked as market-state signals.

## Output role

The result should determine the architecture of the next model.

No new router threshold, model family, or feature subset may be chosen until this diagnostic is complete.
