# SESSION MODEL-09B — SAGE A1_PATH_SESSION FEATURE SELECTION — PREREGISTRATION

**Date:** 2026-10-07  
**Status:** BINDING BEFORE 2025 REVIEW

## Baseline

Canonical Model-09:
`S18_A1_PATH_SESSION`

Mandatory:
- fresh `a1_logit`

Selectable:
- canonical hourly PATH/VOL/SHAPE variables
- canonical 14 SAGE SESSION_ALL variables

Final estimator:
- StandardScaler
- LogisticRegression(L2, C=1.0)
- threshold = 0.50

## Objective

Select the most useful PATH and SAGE variables separately by session while preserving the true A1+PATH+SESSION identity.

## Identity constraints

Every selected candidate must contain:
- mandatory `a1_logit`;
- at least one PATH variable;
- at least one SAGE variable.

The selected candidate may not collapse into A1+PATH or A1+SESSION.

## Fair comparator

For every selected candidate, comparator is:

`SELECTED_A1_PATH_MATCHED`

with:
- mandatory `a1_logit`;
- the **exact same selected PATH subset**;
- no SAGE variables.

Therefore Model-09B receives credit only for incremental SAGE value beyond the same A1+PATH representation.

## Clock contract

Unchanged:
- fresh A1 is causal/source-ready;
- hourly PATH is completed before target start;
- SAGE requires `sage_ready_utc < target_start_utc`;
- no target-window information.

## Chronology

- 2022: warm-up/training only
- 2023–2024: nested feature selection + scored development
- 2025: opened only for selected heads passing the frozen paired gate
- 2026: unopened

## Nested selection

For every session and every 5-row outer development block:

1. Training contains only matured same-window rows before the block.
2. Use up to three chronological inner validation folds.
3. Use class-balanced L1 logistic only as selector on `a1_logit + PATH + SAGE`.
4. Selector C grid: 0.03, 0.10, 0.30, 1.00, 3.00.
5. Force `a1_logit`; enforce at least one PATH and one SAGE variable.
6. Evaluate proposed subsets with unchanged final Logistic L2 C=1.0.
7. Select by inner Balanced Accuracy; within 1pp prefer lower Brier, then fewer variables, then smaller selector C.
8. Outer outcomes never select their own variables.

## Frozen representation

After 2023–2024:
- rank PATH and SAGE variables by outer-block selection frequency;
- prefer variables selected in both years;
- freeze 4–8 PATH+SAGE variables per session;
- preserve at least one PATH + one SAGE;
- `a1_logit` remains mandatory;
- no 2025 outcome may alter the representation.

## Pre-2025 paired gate

Selected A1_PATH_SESSION may open 2025 only if:
- combined N >= 80;
- min(UP recall, DOWN recall) >= 0.30;
- candidate BA >= matched selected A1+PATH comparator BA;
- candidate Brier <= comparator Brier + 0.010;
- if both years have N >= 40, candidate BA >= comparator BA in both years.

## 2025

Only pre-eligible selected heads may be transported.

No 2025 feature reselection, threshold tuning, C tuning, clock change or eligibility rescue.
