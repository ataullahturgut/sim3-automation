# SESSION MODEL-04B — PATH_GLOBAL FEATURE-SELECTION CHALLENGER — PREREGISTRATION

**Date:** 2026-10-07  
**Status:** BINDING BEFORE 2025 REVIEW

## Baseline

SESSION Model-04 baseline is the accepted IRIS HOURLY_ONLY / PATH_GLOBAL model:

- StandardScaler
- LogisticRegression(L2, C=1.0)
- threshold = 0.50
- five-row causal replay
- minimum 180 matured same-window training rows
- same 25 hourly PATH/VOL/SHAPE variables

## Objective

Test whether PATH_GLOBAL improves when its own hourly variables are selected separately for each market window.

This is a **within-lineage variable analysis**. It does not add 15-minute, daily cross-metal, macro, GVZ, COT, or model-output features.

## Candidate universe

Only the original 25 hourly variables:

- h_ret_1
- h_ret_3
- h_ret_6
- h_ret_12
- h_ret_24
- h_ret_48
- h_lag2
- h_session_ret
- h_rv_6
- h_rv_12
- h_rv_24
- h_rv_48
- h_up_semivol_24
- h_down_semivol_24
- h_down_up_semivol_ratio_24
- h_jump_concentration_24
- h_range_24
- h_upfrac_24
- h_slope_6
- h_slope_24
- h_max_drawdown_24
- h_recovery_24
- h_close_location_24
- h_age_max_pos_24
- h_age_max_neg_24

## Clock rule

The hourly timestamp is bar-open; the stored value is bar-close.

A bar opened at T is usable at T+1h. The latest completed hourly bar with:

`available_at <= target_start`

is eligible. Equality is valid because that hourly bar is completed exactly at session start.

No hourly close after target start may enter the predictor set.

## Chronology

- 2022: warm-up/training support only
- 2023–2024: development and variable selection
- 2025: one-time frozen-specification transport
- 2026: unopened

Only matured same-window outcomes may enter training.

## Nested variable selection

For each session and each 5-row outer development block:

1. Outer training contains only matured same-window outcomes before the outer block.
2. Use up to three chronological inner validation folds.
3. Use StandardScaler + L1 LogisticRegression as selector only.
4. Selector C grid: 0.03, 0.10, 0.30, 1.00, 3.00.
5. Candidate subsets are evaluated with the unchanged final PATH_GLOBAL estimator:
   - StandardScaler
   - LogisticRegression(L2, C=1.0)
   - threshold 0.50
6. Select by inner Balanced Accuracy; within 1pp prefer lower Brier, then fewer features, then smaller C.
7. Outer outcomes never select their own variables.

## Frozen session-specific set

After all 2023–2024 development blocks:
- rank variables by outer-block selection frequency;
- prefer variables selected in both development years;
- freeze 3–8 variables per session;
- no 2025 outcome may modify the frozen set.

## Exact comparator

On identical rows compare:
- BASELINE_PATH_GLOBAL — all 25 hourly features
- SELECTED_PATH_GLOBAL — session-specific frozen subset

Report:
- N
- Accuracy
- Balanced Accuracy
- UP recall
- DOWN recall
- Brier
- log loss

## 2025

Replay baseline and selected challenger through the same continuous causal chronology and report only 2025 rows.

No 2025 retuning, threshold adjustment, feature reselection, or session-window change is permitted.
