# D1-META V1 — DIRECT NEXT-DAY SELECTIVE STACK PREREGISTRATION

**Date:** 2026-10-05  
**Identity:** `D1_META_V1`  
**Status:** FROZEN BEFORE RESULT RUN

## Purpose

Stop treating H3 systems as equal D1 votes. Use their frozen origin-safe outputs as **sensors/features** in a model trained directly on the next-day D1 target.

This challenger is designed to address both:
1. CIG UNCERTAIN states caused by H3 lineage disagreement; and
2. coherent-but-wrong 4/4 consensus states.

## D1 target

For each H3 origin:
`D1_UP = 1[Gold(forecast_issue_date) > Gold(feature_cutoff_date)]`.

No future H3 endpoint information enters the feature set.

## Frozen sensor families

### F1 EXPERT
- p_aurora
- p_helios_v5_dce
- p_rift
- p_vega
- OPAL reversal probability
- OPAL/RIFT/VEGA override flags
- V5 candidate-reversal flag
- GT flip share
- expert probability mean/std/range
- pairwise V5-RIFT and V5-VEGA probability gaps.

### F2 EXPERT_PATH
F1 plus frozen origin-safe path state:
- h_ret_12
- trend_strength
- opposite_semivar_share
- deceleration_6h
- session_against_trend
- path_consistency
- trend_close_location
- opposite_extreme_recency
- jump_concentration
- trend_to_range
- adverse_excursion.

### F3 EXPERT_PATH_MACRO
F2 plus origin-safe daily cross-market state:
- broad USD r1
- nominal 10Y d1
- real 10Y d1
- 10Y breakeven d1
- VIX r1
- Nasdaq-100 r1
- silver r1
- metal breadth1
- gold-minus-metal-basket1.

The ORBIT daily features remain diagnostic-quality reconstructed daily series where documented; this challenger cannot upgrade their source authority.

## Candidate model families

For each F1/F2/F3 feature family:

1. `LOGIT_L2`
   - StandardScaler
   - median imputation
   - LogisticRegression C=0.5, L2, max_iter=3000.

2. `HGB_SMALL`
   - median imputation
   - HistGradientBoostingClassifier
   - max_depth=2
   - learning_rate=0.05
   - max_iter=150
   - min_samples_leaf=25
   - l2_regularization=1.0.

No hyperparameter search.

## Period protocol

- training base: 2022-11 through 2023-12.
- model/family selection: 2024-H1.
- selective threshold selection: 2024-H2.
- frozen confirmation: 2025.
- 2026 is opened only after the 2025 confirmation gate.

### Model selection
Choose lowest 2024-H1 Brier.
Tie-break:
1. higher balanced accuracy;
2. higher accuracy;
3. simpler order F1 before F2 before F3, LOGIT before HGB.

### Selective threshold
Symmetric probability thresholds tested on 2024-H2 only:
`t in [0.55, 0.60, 0.65, 0.70]`.

Action if:
- p_up >= t => UP
- p_up <= 1-t => DOWN
- otherwise ABSTAIN.

Eligible threshold requires coverage >=50%.
Choose highest selective accuracy; tie by higher coverage, then higher t.
No 2025/2026 result may alter this threshold.

## 2025 confirmation gate

PASS requires:
1. selective accuracy >=70%;
2. selective coverage >=50%;
3. full-sample balanced accuracy >=55%.

If FAIL, 2026 is diagnostic only and no D1-META integration may be promoted.

## 2026 frozen tests

Report standalone selective D1-META and two predeclared CIG integration policies.

### RESOLVE_ONLY
- existing CIG consensus remains unchanged;
- if CIG is UNCERTAIN and D1-META has a selective action, use D1-META.

### VETO_RESOLVE
- if CIG is UNCERTAIN and D1-META acts, use D1-META;
- if CIG has consensus and D1-META confidently gives the opposite direction, change state to UNCERTAIN;
- otherwise preserve CIG.

Promotion requires:
- 2025 confirmation PASS;
- 2026 integrated accuracy >= original CIG accuracy;
- 2026 integrated coverage >=75%;
- August integrated accuracy >=75%;
- August coverage strictly above original 47.62%.

No 2026 tuning is allowed.
