# GOLD MONTHLY FORECAST — BOOSTING E4 FINAL ROBUSTNESS FREEZE

Date: 2026-09-28
Status: FROZEN BEFORE E4 ROBUSTNESS OUTPUT

## Purpose
Run the pre-planned final DEV robustness diagnostics after closure of learned-weight ensemble optimization.

## Frozen principal candidates

### PRICE candidate
CATBOOST_PRICE
- DEV SigmaAE: 1460.433935309605
- Direction: 20/33

### BALANCE / DIRECTION candidate
FULL5 MEDIAN
- DEV SigmaAE: 1484.731330609916
- Direction: 23/33

FULL5 components remain frozen:
1. CATBOOST_PRICE
2. CATBOOST_BALANCED
3. GBRT
4. LIGHTGBM
5. XGB_DIRECTION

No new model, subset, weight, alpha, hyperparameter, feature, target, or representation may be selected during E4.

## Frozen robustness diagnostics

1. Year-by-year performance
- 2022
- 2023
- 2024
For both principal candidates report SigmaAE, MAE, direction correct and direction accuracy.

2. Pairwise month-by-month comparison
For each of the 33 DEV targets:
- actual
- random-walk reference
- CATBOOST_PRICE forecast / AE / direction correctness
- FULL5 MEDIAN forecast / AE / direction correctness
- lower-AE winner or tie

Aggregate:
- CATBOOST_PRICE monthly AE wins
- FULL5 MEDIAN monthly AE wins
- ties

3. Direction rescue/loss audit
Relative to CATBOOST_PRICE:
- rescue = CATBOOST_PRICE direction wrong and FULL5 MEDIAN direction correct
- loss = CATBOOST_PRICE direction correct and FULL5 MEDIAN direction wrong
- both correct
- both wrong

4. Worst-month sensitivity
For each principal candidate:
- identify its worst-AE DEV month
- remove only that month
- report remaining n=32 SigmaAE and MAE

Also perform common leave-one-origin sensitivity across all 33 origins:
- remove the same one target from both candidate score vectors
- compare remaining 32-month SigmaAE
- report how many omissions favor CATBOOST_PRICE, favor FULL5 MEDIAN, or tie
- this is diagnostic only; no refitting and no candidate reselection

5. FULL5 leave-one-component-out diagnostic
For each frozen FULL5 component, remove exactly that one component and recompute the row-wise median on the remaining four components.

Report:
- SigmaAE
- direction
- delta SigmaAE vs frozen FULL5 MEDIAN

This is DIAGNOSTIC ONLY.
It cannot create a new REDUCED4/alternate subset or change the final ensemble pool.

6. Stability summary
For both principal candidates report:
- monthly AE standard deviation
- median AE
- worst AE / month
- yearly MAE values
- yearly MAE range
- yearly MAE population standard deviation

## Final-freeze rule after E4
E4 is a descriptive robustness stage, not a new tuning stage.

If:
- all frozen predictions reconcile exactly,
- DEV scope remains 2022-04..2024-12 n=33,
- authority invariants remain unchanged,
- 2025 remains unopened,
- 2026 remains unused,
- and all diagnostics are internally consistent,

then E4 passes and Boosting proceeds to E5 final freeze.

The roles entering E5 remain:
- PRICE = CATBOOST_PRICE
- BALANCE / DIRECTION = FULL5 MEDIAN

E4 may block the freeze only for a scientific/integrity failure. It may not perform post-hoc model reselection from robustness diagnostics.

## Governance
- 2025: NOT OPENED / NOT EVALUATED
- 2026: QUARANTINED / NOT USED
- random split: NONE
- DB: READ_ONLY
- base configs: frozen
- learned weights: CLOSED
- arbitrary subset search: NONE
