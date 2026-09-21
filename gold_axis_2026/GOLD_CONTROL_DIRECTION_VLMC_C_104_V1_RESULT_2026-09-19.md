# GOLD CONTROL — VLMC-C 104 V1 RESULT

**Date:** 2026-09-19  
**Identity:** `DIRECTION_VLMC_C_104_V1_RESEARCH`  
**Parent:** `DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH`  
**Status:** `EVALUATED / NO_PROMOTION / PRE2025_VALIDATION_FAILED / 2025_COLLAPSE_TO_ALWAYS_UP / NOT_RUNTIME`

## Frozen method

The experiment uses the previously frozen VLMC-C 104 preregistration without model-parameter changes:

- rolling window = 104 weekly signs;
- `alpha0=0.05`;
- branch-specific mixed-chi-square pruning following the pinned An et al. reference semantics;
- external branch-test reference commit `8195ee16dedbb3a89c288869ee9c0b856ea2ed4f`;
- 100000 Gaussian Monte Carlo draws per branch test;
- reference seed 1 independently per branch;
- next-week UP iff `P(UP)>=0.5`;
- no smoothing, exogenous covariates, threshold rescue, event-conditioned tuning or 2025 tuning.

A workflow implementation defect in the comparison-only previous-sign column reference (`par$previous_up` after a suffixed merge) caused the earlier run to fail after predictions had been computed. Commit `787cb291b660980f41a1e29d59ae08c655832ec1` changed only that comparison-column reference to `par$previous_up_vlmc104`. No model rule, parameter, input, prediction logic or preregistered decision threshold changed.

The corrected governed workflow run `35453387137` completed successfully on 2026-09-19.

## Pre-2025 primary validation — 2024 identical VLMC-104 support

n = 44.

VLMC-C 104:
- accuracy = 0.4772727;
- balanced accuracy = 0.4416667;
- UP sensitivity = 0.8333333;
- DOWN sensitivity = 0.0500000;
- TP/TN/FP/FN = 20/1/19/4;
- forecast UP/DOWN = 39/5;
- Brier = 0.2707773;
- log loss = 1.3128546.

Parent corrected VLMC-BS-104 on identical support:
- accuracy = 0.5681818;
- balanced accuracy = 0.5583333;
- UP sensitivity = 0.6666667;
- DOWN sensitivity = 0.4500000;
- TP/TN/FP/FN = 16/9/11/8;
- forecast UP/DOWN = 27/17;
- Brier = 0.3376922;
- log loss = 6.0234395.

Delta VLMC-C minus VLMC-BS-104:
- accuracy = -0.0909091;
- balanced accuracy = -0.1166667;
- Brier = -0.0669149;
- log loss = -4.7105849.

Interpretation: VLMC-C materially reduces extreme-probability loss, but it worsens the primary direction-discrimination metrics and almost eliminates DOWN detection. It therefore fails the preregistered pre-2025 successor test.

## Unchanged 2025 post-diagnostic replay

n = 52.

VLMC-C 104:
- accuracy = 0.7115385;
- balanced accuracy = 0.5000000;
- UP sensitivity = 1.0000000;
- DOWN sensitivity = 0.0000000;
- TP/TN/FP/FN = 37/0/15/0;
- forecast UP/DOWN = 52/0;
- Brier = 0.2284667;
- log loss = 1.1276896.

Parent corrected VLMC-BS-104:
- accuracy = 0.6153846;
- balanced accuracy = 0.5513514;
- UP sensitivity = 0.7027027;
- DOWN sensitivity = 0.4000000;
- forecast UP/DOWN = 35/17;
- Brier = 0.3134873;
- log loss = 4.6907954.

The VLMC-C raw 2025 accuracy exactly equals the always-UP baseline because it forecast UP in all 52 weeks. The improved Brier/log-loss values do not constitute a direction edge.

## Decision

VLMC-C 104 does not rescue the VLMC direction family.

The decisive evidence is pre-2025: balanced accuracy falls from 0.5583 to 0.4417 and DOWN sensitivity from 0.45 to 0.05 versus the parent VLMC-BS-104 on identical support.

The unchanged 2025 replay reinforces the same failure mode by collapsing to 52/52 UP forecasts and zero DOWN sensitivity.

Binding decision for the current direction-research sequence:

`DIRECTION_VLMC_C_104_V1_RESEARCH = EVALUATED / NO_PROMOTION / PRE2025_VALIDATION_FAILED / 2025_COLLAPSE_TO_ALWAYS_UP / NOT_RUNTIME / NOT_PRODUCTION_AUTHORITY`.

The broader VLMC direction family is closed for the current research sequence after:
- source-faithful VLMC-BS 26/52/104 evaluation;
- Fixed-Share adaptive-window attempt;
- COVLMC-X3 exogenous-covariate attempt;
- VLMC-C 104 consistent-pruning successor.

No further VLMC retuning, alternate fixed-window search, Fixed-Share rescue, COVLMC rescue, discounted/forgetting successor or VLMC-specific smoothing successor is authorized unless the user explicitly reopens the family.

No 2025 outcome may be used to retune or rescue this closed family.
