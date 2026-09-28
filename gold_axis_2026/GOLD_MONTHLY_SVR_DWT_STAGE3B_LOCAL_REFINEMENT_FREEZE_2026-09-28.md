# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 3B LOCAL REFINEMENT FREEZE

Date: 2026-09-28  
Status: **PRE-OUTCOME FREEZE / BINDING**  
Branch: `gold-midas-headswap-v1-20260925`

## Frozen parent and Stage-3A context

META_PARENT_SVR remains:
- epsilon-SVR
- RBF kernel
- DAILY_SUMMARY12
- training-only X/Y standardization

Frozen parent DEV:
- SigmaAE 1449.187363
- direction 19/33

Stage-3A coarse nested tuning:
- SigmaAE 1580.901050
- direction 20/33
- not promoted over the frozen parent.

Stage-3A most frequently selected coarse neighborhoods:
1. log2(C)=0, log2(gamma)=-4, epsilon around 0.01–0.10
2. log2(C)=4, log2(gamma)=-12, epsilon around 0.01–0.20
3. log2(C)=8, log2(gamma)=-8, epsilon around 0.05–0.10

Stage 3B is allowed to refine only these preidentified Stage-3A selection regions.

## Local candidate regions

### Region A — moderate C / moderate gamma
- log2(C): -2, 0, 2
- log2(gamma): -6, -4, -2
- epsilon: 0.01, 0.03, 0.05, 0.075, 0.10

Candidates: 3 x 3 x 5 = 45

### Region B — higher C / very small gamma
- log2(C): 2, 4, 6
- log2(gamma): -12, -10, -8
- epsilon: 0.01, 0.03, 0.05, 0.10, 0.15, 0.20

Candidates: 3 x 3 x 6 = 54

### Region C — high C / small gamma
- log2(C): 6, 8, 10
- log2(gamma): -10, -8, -6
- epsilon: 0.03, 0.05, 0.075, 0.10, 0.15

Candidates: 3 x 3 x 5 = 45

The union is deduplicated before execution.

No point outside these regions may be added after Stage-3B outcomes.

## Chronological selection protocol

Exactly the same nested chronology as Stage 3A:
1. For each outer DEV target, use only rows with target < outer target.
2. Final 20% chronological pre-target rows are inner validation, minimum 12.
3. Earlier rows are inner training.
4. X/y scalers are fit on inner training only.
5. Candidate objective = mean absolute standardized Gold log-return error on inner validation.
6. Deterministic tie-break:
   - lower inner MAE
   - lower C
   - lower epsilon
   - lower gamma
7. Selected candidate is refit on all pre-target rows.
8. Outer target is forecast once.
9. Current outer-target actual is never used in selection.

## Promotion logic

Stage-3B is a controlled refinement test, not an automatic replacement.

The family keeps the lower honest DEV SigmaAE among:
- frozen Stage-2 parent
- Stage-3A coarse tuned
- Stage-3B local tuned

Direction remains complementary evidence.

If Stage 3B does not beat the frozen Stage-2 parent on DEV SigmaAE:
- deterministic tuning line is CLOSED_NOT_PROMOTED;
- Stage 4 metaheuristic bounds are still frozen from the original authority domain, not from a post-hoc rescue grid;
- no further deterministic rescue tuning is opened.

If Stage 3B beats the parent:
- Stage-3B becomes the deterministic tuned benchmark;
- Stage-4 bounds still require a separate pre-outcome freeze.

## Scientific gates

Mandatory:
- union candidate list frozen before run
- 33/33 DEV outer forecasts
- all selected points belong to frozen union
- inner validation precedes outer target
- inner scaling train-only
- outer refit pre-target only
- finite predictions
- deterministic replay
- DB invariants unchanged
- 2025 unopened
- 2026 unused
- random split none

## Kontrol ve Uyum Özeti
- Stage-3A result used only to identify modal regions allowed by the prior plan: PASS.
- Outer residuals not used to place local points: PASS.
- Exact local grids frozen before Stage-3B outcomes: PASS.
- 2025 opened: NO.
- 2026 used: NO.
- Random split: NONE.
- DB writes: NONE.
