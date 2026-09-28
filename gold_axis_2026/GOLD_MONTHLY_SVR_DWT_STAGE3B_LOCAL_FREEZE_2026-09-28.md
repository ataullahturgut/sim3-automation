# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 3B LOCAL REFINEMENT FREEZE

Date: 2026-09-28  
Status: **PRE-OUTCOME FREEZE / BINDING**

## Inputs already known before this freeze
Frozen Stage-2 parent:
- EPSILON_RBF_DAILY12
- DEV SigmaAE 1449.187363
- direction 19/33

Stage-3A coarse nested result:
- DEV SigmaAE 1580.901050
- direction 20/33
- worse than parent by +131.713687

Stage-3A selected coarse regions concentrated mainly around:
- log2(C): 0, 4, 8
- log2(gamma): -12, -8, -4
- epsilon: 0.01, 0.05, 0.10, 0.20

These observations may define the center of Stage-3B, but Stage-3B outcomes themselves may not alter the rules below.

## Stage-3B rule

For each outer DEV target:
1. Reproduce the frozen Stage-3A coarse search using only pre-target data.
2. Take that outer target's selected coarse point as the local center.
3. Build a deterministic local neighborhood around that point.
4. Use the **same inner chronological split, scaling discipline, objective and tie-break** as Stage 3A.
5. Select the best local candidate using only inner validation.
6. Refit on all pre-target rows and forecast the outer target once.

## Local C neighborhood
If Stage-3A selects log2(C)=c:

Use unique clipped values:
- c-2
- c
- c+2

Clip to the original authority range:
- [-8, 12]

## Local gamma neighborhood
If Stage-3A selects log2(gamma)=g:

Use unique clipped values:
- g-2
- g
- g+2

Clip to:
- [-12, 4]

## Local epsilon neighborhood

Frozen mapping:

- coarse 0.01 -> [0.01, 0.025, 0.05]
- coarse 0.05 -> [0.025, 0.05, 0.075]
- coarse 0.10 -> [0.075, 0.10, 0.15]
- coarse 0.20 -> [0.15, 0.20, 0.35]
- coarse 0.50 -> [0.35, 0.50]

No other epsilon values are authorized.

## Inner protocol
Same as Stage 3A:
- final 20% chronological pre-target validation tail;
- minimum 12 validation rows;
- scalers fitted only on inner training;
- objective = MAE of standardized Gold log return on validation;
- deterministic tie-break: inner MAE, lower C, lower epsilon, lower gamma.

## Promotion rule
Stage-3B local tuned benchmark is promoted over the frozen Stage-2 parent **only if**:
- Stage-3B DEV SigmaAE < 1449.187363.

Direction is reported as complementary evidence but cannot rescue a worse primary SigmaAE in this deterministic tuning stage.

If the rule fails:
- deterministic grid/local tuning = **CLOSED / NOT PROMOTED**;
- the frozen Stage-2 parent remains the deterministic SVR reference.

## Stage-4 bounds after Stage 3B
Regardless of Stage-3B promotion outcome, the mandatory 32/32 metaheuristic screen remains authorized.

Unless an integrity failure requires reopening governance, the Stage-4 continuous search domain will remain the original authority domain:
- log2(C) in [-8,12]
- log2(gamma) in [-12,4]
- epsilon in [0.01,0.50]

Exact continuous-bound freeze will be committed after Stage-3B closes and before Stage-4.1.

## Governance
- 2025 remains locked.
- 2026 unused.
- random split none.
- DB read-only.
- no kernel/representation/formulation change.
- no post-outcome rescue points.

## Kontrol ve Uyum Özeti
- Stage-3A result known before local freeze: disclosed.
- Local-neighborhood rule frozen before Stage-3B outcomes: PASS.
- Promotion threshold frozen: PASS.
- Stage-4 obligation preserved: 32/32.
- 2025 opened: NO.
- 2026 used: NO.
