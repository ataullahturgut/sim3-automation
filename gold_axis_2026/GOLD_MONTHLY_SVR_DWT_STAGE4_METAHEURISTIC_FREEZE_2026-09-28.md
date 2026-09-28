# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 4 METAHEURISTIC FREEZE

Date: 2026-09-28  
Status: **PRE-OUTCOME FREEZE / BINDING**

## Frozen carried-forward benchmark
Deterministic benchmark after Stage 3:
**EPSILON_RBF_DAILY12**

- formulation: epsilon-SVR
- kernel: RBF
- representation: DAILY_SUMMARY12
- training-only X/Y standardization
- canonical untuned reference C=1.0, epsilon=0.1, gamma=scale
- DEV SigmaAE: 1449.187363
- DEV direction: 19/33

Stage 3A/3B deterministic tuning were not promoted and are CLOSED.

## Stage 4 optimization domain
Every mandatory optimizer uses the same continuous domain:

- log2(C) in [-8, 12]
- log2(gamma) in [-12, 4]
- epsilon in [0.01, 0.50]

Decode:
- C = 2 ** log2(C)
- gamma = 2 ** log2(gamma)
- epsilon used directly

No optimizer may receive a narrower/wider method-specific domain.

## Inner data protocol
For every outer DEV target:
- historical targets must be strictly earlier than current target
- final 20% of pre-target history is chronological validation, minimum 12 rows
- earlier rows are inner training
- X/y scalers fitted on inner training only
- optimizer evolution objective = standardized Gold log-return MAE on inner training
- validation selection restricted to strongest training candidates by the reused governed optimizer implementation
- validation metric = standardized Gold log-return MAE
- winner refit = exact selected SVR hyperparameters fit on all pre-target rows with new all-history train-only scalers
- no target-month actual in optimization

## Fairness budget
Common default:
- population/agents = 24
- update generations = 45
- deterministic repeats = 3
- initialization includes frozen parent anchor plus local/uniform exploration
- repeat winner selected only by prior-only chronological validation
- exact update equations are reused from the already-audited ELMFIS/RBFNN optimizer modules, with only the objective/bounds interface changed

Seed policy:
- reuse each repository optimizer's frozen SEED_BASE
- target-derived deterministic offset
- +1009 per repeat
- record every repeat seed and validation result

No outcome-based budget extension is allowed.

## Mandatory 32 methods / batches

Execution-batch amendment (user directive, 2026-09-28):
- Batch 4.1 had already completed with 4 methods before this amendment and remains valid.
- From Batch 4.2 onward, run at most 5 methods per batch.
- This changes execution packaging only; candidate set, method order, bounds, objective, budget, seed policy and scientific gates are unchanged.

4.1 COMPLETE: PSO, GA, DE, MPA  
4.2: ABC, SSA, GWO, WOA, HHO  
4.3: ACO, BAT, FA, MFO, FPA  
4.4: FA_FPA, CS, SCA, SALP, SMA  
4.5: GOA, ALO, TLBO, JAYA, HGS  
4.6: CHOA, HGSO, AOA, CPA, KRILL  
4.7: CROW, DE_ABC, MULTISWARM

No parent selection before all 32 are complete/audited unless a method is formally BLOCKED by a documented scientific/technical failure.

## Metaheuristic output rule
For each method and outer target record:
- chosen C/gamma/epsilon
- selected repeat
- all repeat validation losses
- forecast
- actual
- AE
- direction
- train/validation chronology
- optimizer source module/function/hash where available
- scientific failure, if any

## Promotion policy
Stage 4 does not automatically replace the parent.

After 32/32:
- primary rank = honest DEV SigmaAE
- direction/stability are complementary
- parent/refinement roles are frozen only after all methods are audited
- 2025/2026 cannot influence ranking or parent selection

## Governance
- DEV: 2022-04..2024-12 only
- 2025 LOCKED
- 2026 QUARANTINED / unused
- random split NONE
- DB READ_ONLY
- no method-specific post-hoc bounds
- no silent failure deletion
- no post-outcome extra optimizer

## Kontrol ve Uyum Özeti
- Stage-3 closure precedes Stage-4 freeze: PASS.
- Common continuous domain frozen: PASS.
- Common inner objective frozen: PASS.
- Population/generation/repeat budget frozen: PASS.
- 32/32 mandatory list frozen: PASS.
- 2025 opened: NO.
- 2026 used: NO.
