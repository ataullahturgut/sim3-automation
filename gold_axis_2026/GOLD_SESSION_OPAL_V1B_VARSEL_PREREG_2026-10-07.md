# SESSION OPAL V1B — VARIABLE-SELECTION CHALLENGER — PREREGISTRATION

**Date:** 2026-10-07  
**Status:** BINDING FOR POST-BASELINE DIAGNOSTIC

## Purpose

Test whether SESSION OPAL can be simplified to a stable session-specific subset of its original 18 variables without changing:
- upstream AURORA;
- corrected COT timing;
- 12h pre-target momentum definition;
- estimator family;
- reversal threshold 0.70;
- causal monthly replay.

The baseline OPAL V1 remains the canonical specification.

## Candidate universe

Only the original 18 OPAL variables:

- opt_mm_net
- opt_prod_net
- opt_swap_net
- opt_other_net
- d_opt_mm_net
- d_opt_prod_net
- opt_mm_z52
- opt_prod_z52
- opt_swap_z52
- opt_other_z52
- spec_hedger_gap
- spec_swap_gap
- fut_mm_net
- fut_prod_net
- trend_x_opt_mm
- trend_x_opt_prod
- trend_x_spec_hedger_gap
- trend_strength

No new feature may enter.

## Chronology

- 2023–2024 only: variable selection and development gate
- 2025: transport only after the selected representation is frozen
- 2026: unopened

The already-observed OPAL V1 2025 baseline result is not used in variable ranking, subset choice, threshold choice or eligibility.

## Selector

Within each partition/window, for each development-month training history with:
- at least 80 matured same-window rows;
- both reversal classes present;

fit:
- StandardScaler
- LogisticRegression(penalty=L1, solver=liblinear, class_weight=balanced)

C grid:
- 0.03
- 0.10
- 0.30
- 1.00
- 3.00

Choose C by chronological inner validation Balanced Accuracy; within 1 pp prefer:
1. lower Brier;
2. fewer variables;
3. smaller C.

## Frozen session subset

After all 2023–2024 selection events:

- rank features by selection frequency;
- prefer features selected in both 2023 and 2024;
- retain 3–8 features per session;
- ensure at least one direct COT-positioning feature;
- ensure at least one trend/context feature from:
  - trend_x_opt_mm
  - trend_x_opt_prod
  - trend_x_spec_hedger_gap
  - trend_strength

No 2025 result may alter the frozen subset.

## Final challenger model

Use the same final estimator as OPAL V1:
- StandardScaler
- LogisticRegression(C=1.0, class_weight=balanced)
- reversal threshold = 0.70

Only the feature subset changes.

## Gate

The selected OPAL head must pass the same frozen pre-2025 gate against fresh AURORA:

- annual accuracy tolerance <= 1 pp;
- annual Brier tolerance <= 0.003;
- combined BA >= AURORA BA;
- min class recall >= 30%;
- net rescue > 0;
- at least one override.

Only passing selected heads may open 2025.

This is a diagnostic challenger, not an automatic replacement for canonical OPAL V1.
