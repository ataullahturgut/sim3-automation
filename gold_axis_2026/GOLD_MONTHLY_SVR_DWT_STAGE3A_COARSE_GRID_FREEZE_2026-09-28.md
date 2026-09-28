# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 3A COARSE GRID FREEZE

Date: 2026-09-28  
Status: **PRE-OUTCOME FREEZE / BINDING**  
Branch: `gold-midas-headswap-v1-20260925`

## Frozen parent
From Stage 2C:

**META_PARENT_SVR = EPSILON_RBF_DAILY12**

Identity:
- formulation: epsilon-SVR
- kernel: RBF
- representation: DAILY_SUMMARY12
- feature dimension: 12
- target: next-month Gold log return
- price reconstruction: previous completed-month Gold average * exp(predicted log return)
- training-only X/Y standardization
- common training-history start: 2010-05

Canonical parent reference:
- C = 1.0
- epsilon = 0.1
- gamma = scale
- DEV SigmaAE = 1449.187363
- direction = 19/33

## Stage 3A purpose
Perform a deterministic, chronology-safe coarse hyperparameter search for the frozen parent formulation.

No kernel, representation, target, scaling, or formulation changes are allowed in Stage 3A.

## Outer DEV
- 2022-04..2024-12
- n=33
- each target month is an untouched outer evaluation origin
- 2025 remains locked
- 2026 remains unused

## Inner chronology
For each outer target:
1. Build only rows whose target month is strictly earlier than the outer target.
2. Order them chronologically.
3. The final 20% of available pre-target rows is the inner validation tail.
4. Inner validation size is rounded up and must be at least 12 rows.
5. Remaining earlier rows form inner training.
6. X and y scalers are fit **only on inner-training rows**.
7. Each candidate is fit on inner training and scored on the chronological validation tail.
8. Objective = mean absolute error of standardized Gold log return on the inner validation tail.
9. Current outer-target actual is never used in inner search.
10. After candidate selection, X/y scalers and SVR are refit on all pre-target rows and the outer target is forecast once.

## Frozen coarse grid

### C
Use:
- log2(C) = -8, -4, 0, 4, 8, 12

Equivalent C:
- 0.00390625
- 0.0625
- 1
- 16
- 256
- 4096

### gamma
Use:
- log2(gamma) = -12, -8, -4, 0, 4

Equivalent gamma:
- 0.000244140625
- 0.00390625
- 0.0625
- 1
- 16

### epsilon
Use:
- 0.01
- 0.05
- 0.10
- 0.20
- 0.50

Total coarse candidates:
**6 × 5 × 5 = 150**

No new point may be added after Stage-3A outcomes.

## Deterministic selection rule
Rank candidates by:
1. lower inner standardized-log-return MAE;
2. lower C;
3. lower epsilon;
4. lower gamma.

This is a deterministic tie-break only.

## Canonical parent comparator
The frozen Stage-2 parent with `gamma=scale` remains an external Stage-3A comparator.

It is **not** silently converted into a numeric grid point and does not alter the 150-candidate search.

Stage-3A promotion requires interpretation against the frozen parent on honest outer DEV, not same-inner-sample fit.

## Scientific gates
Mandatory:
- 33/33 outer DEV forecasts.
- selected parameters come only from the frozen 150-point grid.
- inner validation strictly precedes outer target.
- scalers fitted only on inner train during selection.
- outer refit uses only rows before outer target.
- finite prediction.
- abs predicted monthly log return < 1.
- deterministic full rerun.
- DB authority invariants unchanged.
- 2025 not built/evaluated.
- 2026 not built/evaluated.
- no random split.

## Stage 3B relation
Stage 3A does **not** define Stage-3B local points in advance.

After Stage 3A closes:
- only the observed Stage-3A selected regions may anchor Stage-3B;
- the exact Stage-3B local grid/rule must be committed in a new pre-outcome freeze before Stage-3B execution;
- Stage-3B cannot add arbitrary rescue points after seeing its own outcomes.

## Stage 4 relation
No Stage-4 metaheuristic may start yet.

After Stage 3B:
- final continuous bounds and inner objective will be frozen;
- the same bounds/objective will apply to all mandatory 32 metaheuristics.

## Kontrol ve Uyum Özeti
- Stage-2 parent frozen before Stage-3 outcomes: PASS.
- Exact Stage-3A grid frozen: PASS.
- Candidate count: 150.
- Chronological inner validation frozen: PASS.
- Scaling discipline frozen: PASS.
- Tie-break frozen: PASS.
- 2025 opened: NO.
- 2026 used: NO.
- Random split: NONE.
- DB writes: NONE.
