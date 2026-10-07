# SESSION MODEL-06B — SAGE SESSION_ONLY FEATURE SELECTION — PREREGISTRATION

**Date:** 2026-10-07  
**Status:** BINDING BEFORE SELECTED-SAGE 2025 REVIEW

## Baseline

Canonical Model-06:
`S15_SESSION_ONLY`

Estimator:
- StandardScaler
- LogisticRegression(L2, C=1.0)
- threshold = 0.50
- same-window causal replay
- outer block = 5
- minimum training rows = 120

## Objective

Test whether SAGE SESSION_ONLY becomes more stable when the canonical 14 phase variables are reduced separately by session.

No non-SAGE variable may enter Model-06B.

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

## Clock identity

Unchanged from canonical SAGE:

- exact 15m OPEN at NY-local 18:00 / 03:00 / 08:00 / 12:00 / 16:00 boundaries;
- completed SAGE cycle source-ready at 16:15 America/New_York;
- eligible only when `sage_ready_utc < target_start_utc`;
- equality rejected;
- no nearest-bar substitution;
- no target-window information.

## Chronology

- 2022: warm-up/training only
- 2023–2024: nested feature selection + development scoring
- 2025: opened only for heads that pass the frozen selected-SAGE development gate
- 2026: unopened

## Nested feature selection

For each session and each 5-row outer development block:

1. Training contains only matured same-window outcomes before the block.
2. Create up to three chronological inner validation folds.
3. Use StandardScaler + class-balanced L1 LogisticRegression as selector only.
4. Selector C grid: 0.03, 0.10, 0.30, 1.00, 3.00.
5. Evaluate each proposed subset with the unchanged final estimator:
   - StandardScaler
   - LogisticRegression(L2, C=1.0)
   - class_weight=None
   - threshold 0.50
6. Select by inner Balanced Accuracy; within 1 percentage point prefer lower Brier, then fewer variables, then smaller selector C.
7. Outer outcomes never select their own variables.

## Frozen session feature set

After all 2023–2024 outer predictions:
- rank variables by outer-block selection frequency;
- prefer variables selected in both 2023 and 2024;
- freeze 3–8 variables per session;
- no 2025 outcome may change the subset.

## Development comparison and eligibility

Report baseline and selected-SAGE on exact common development rows.

Selected-SAGE may open 2025 for a session only if it satisfies the same preregistered SESSION_ONLY gate:

- combined 2023–2024 N >= 80;
- min(UP recall, DOWN recall) >= 0.30;
- combined BA >= 0.52;
- each development year with N >= 40 has BA >= 0.50.

This eligibility decision is frozen before any selected-SAGE 2025 outcome is read.

## 2025

Only development-eligible selected-SAGE heads are transported through the continuous original five-row block chronology.

Required metrics:
- N
- Accuracy
- Balanced Accuracy
- UP recall
- DOWN recall
- Brier
- log loss

No 2025 feature reselection, threshold tuning, clock change or eligibility rescue is permitted.
