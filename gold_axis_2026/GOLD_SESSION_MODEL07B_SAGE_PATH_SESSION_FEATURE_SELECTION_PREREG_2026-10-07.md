# SESSION MODEL-07B — SAGE PATH_SESSION FEATURE SELECTION — PREREGISTRATION

**Date:** 2026-10-07  
**Status:** BINDING BEFORE 2025 REVIEW

## Baseline

Canonical Model-07:
`S16_PATH_SESSION`

Final estimator:
- StandardScaler
- LogisticRegression(L2, C=1.0)
- threshold = 0.50
- same-window causal replay
- block = 5
- minimum matured training rows = 120

Canonical inputs:
- hourly XAU PATH/VOL/SHAPE block;
- 14 SAGE SESSION_ALL variables.

## Objective

Select the most useful PATH and SAGE variables separately by session while preserving the model's PATH+SESSION identity.

## Candidate universe

PATH candidates:
- exactly the canonical `res1h.feature_names("g1h")` block.

SAGE candidates:
- exactly the canonical 14 `SESSION_ALL` variables.

No A1, 15m challenger, cross-metal, macro, GVZ, COT, model-output, or target-derived feature may enter.

## Identity constraint

Every selected PATH_SESSION model must contain:
- at least one PATH variable;
- at least one SAGE variable.

Therefore the challenger may not collapse into PATH_GLOBAL or SESSION_ONLY.

## Clock contract

Unchanged:
- SAGE complete cycle ready at 16:15 America/New_York;
- require `sage_ready_utc < target_start_utc`;
- hourly PATH must also be completed before target start;
- no target-window information.

## Chronology

- 2022: warm-up/training only
- 2023–2024: nested feature selection + development scoring
- 2025: opened only for selected heads that pass the frozen pre-2025 paired gate
- 2026: unopened

## Nested selection

For every session and every 5-row outer development block:

1. Use only matured same-window rows before the block.
2. Use up to three chronological inner validation folds.
3. Use class-balanced L1 LogisticRegression only as a selector.
4. Selector C grid: 0.03, 0.10, 0.30, 1.00, 3.00.
5. Enforce at least one PATH and one SAGE variable in every candidate subset.
6. Score each candidate subset with the unchanged final Logistic L2 C=1.0 model.
7. Select by inner Balanced Accuracy; within 1pp prefer lower Brier, then fewer variables, then smaller selector C.
8. Outer outcomes never select their own variables.

## Frozen per-session representation

After 2023–2024:
- rank PATH and SAGE variables by outer-block selection frequency;
- prefer cross-year stable variables;
- freeze 3–8 total variables where possible;
- preserve at least one PATH + one SAGE variable;
- no 2025 outcome may modify the frozen representation.

## Fair comparator

For every frozen selected PATH_SESSION head, construct a matched comparator on the exact same rows using:
- the **same selected PATH subset**;
- no SAGE variables.

This comparator is `SELECTED_PATH_MATCHED`.

Thus any Model-07B gain must come from the retained SAGE information, not merely from pruning PATH.

## Pre-2025 paired gate

Selected Model-07B may open 2025 only if:
- combined N >= 80;
- min(UP recall, DOWN recall) >= 0.30;
- candidate BA >= matched selected-PATH comparator BA;
- candidate Brier <= comparator Brier + 0.010;
- if both years have N >= 40, candidate BA >= comparator BA in both 2023 and 2024.

## 2025

Only pre-2025 eligible selected heads may be transported.

No 2025 feature reselection, threshold tuning, C tuning, clock change, or eligibility rescue.
