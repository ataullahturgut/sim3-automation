# SESSION MODEL-08B — SAGE A1_SESSION FEATURE SELECTION — PREREGISTRATION

**Date:** 2026-10-07  
**Status:** BINDING BEFORE 2025 REVIEW

## Baseline

Canonical Model-08:
`S17_A1_SESSION`

Mandatory structural input:
- `a1_logit`

Selectable block:
- only the canonical 14 SAGE SESSION_ALL variables.

Final estimator:
- StandardScaler
- LogisticRegression(L2, C=1.0)
- threshold = 0.50

Correct comparator:
- direct fresh `p_A1_arcr`
- no downstream refit.

## Objective

Determine whether a smaller, session-specific SAGE subset adds stable directional information on top of fresh A1.

## Candidate universe

Only:
- sess_asia
- sess_europe
- sess_us_am
- sess_us_pm
- sess_us_total
- sess_west_total
- sess_east_west
- sess_us_reversal
- sess_dispersion
- sess_sign_changes
- sess_dominance
- sess_asia_us_interaction
- sess_east_west_conflict
- sess_us_conflict

No PATH, 15m, cross-metal, macro, GVZ, COT or downstream model state may enter.

## Identity constraint

`a1_logit` is mandatory in every selected model.

At least two SAGE variables must be retained so that the challenger remains an A1+SESSION model rather than collapsing to direct A1.

## Clock contract

Unchanged:
- fresh A1 is causal and source-ready;
- SAGE cycle ready at 16:15 America/New_York;
- require `sage_ready_utc < target_start_utc`;
- no target-window information.

## Chronology

- 2022: warm-up/training only
- 2023–2024: nested SAGE-variable selection + scored development
- 2025: opened only for selected heads that pass the frozen paired gate
- 2026: unopened

## Nested selection

For every session and every 5-row outer development block:

1. Training includes only matured same-window rows before the block.
2. Use up to three chronological inner validation folds.
3. Use class-balanced L1 logistic only as a selector on `a1_logit + SESSION_ALL`.
4. Selector C grid: 0.03, 0.10, 0.30, 1.00, 3.00.
5. `a1_logit` is forced into every selected candidate.
6. Keep at least two SAGE variables.
7. Evaluate candidates with the unchanged final Logistic L2 C=1.0 model.
8. Select by inner Balanced Accuracy; within 1pp prefer lower Brier, then fewer SAGE variables, then smaller selector C.
9. Outer outcomes never select their own variables.

## Frozen representation

After 2023–2024:
- rank SAGE variables by outer-block selection frequency;
- prefer variables selected in both development years;
- freeze 2–6 SAGE variables per session;
- `a1_logit` remains mandatory;
- no 2025 outcome may modify the set.

## Pre-2025 paired gate

Selected A1_SESSION may open 2025 only if:
- combined N >= 80;
- min(UP recall, DOWN recall) >= 0.30;
- candidate BA >= direct A1 BA;
- candidate Brier <= direct A1 Brier + 0.010;
- where both years have N >= 40, candidate BA >= direct A1 BA in both 2023 and 2024.

## 2025

Only pre-eligible selected heads may be transported.

No 2025 feature reselection, threshold tuning, C tuning, clock change or eligibility rescue.
