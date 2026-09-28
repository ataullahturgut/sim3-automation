# GOLD MONTHLY FORECAST — SVR STAGE 5A.1 ADAPTIVE PSO IMPLEMENTATION FREEZE

Date: 2026-09-28
Status: **FROZEN BEFORE OUTCOME**

## Purpose
First targeted-refinement model after the Stage-4 broad metaheuristic screen:
**Adaptive PSO-SVR**.

## Parent / data / target
- Parent identity: `EPSILON_RBF_DAILY12`
- Representation: `DAILY_SUMMARY12`
- Kernel: RBF epsilon-SVR
- Target: next-month Gold log return, reconstructed to next-month average XAU/USD price
- DEV authority: 2022-04..2024-12, n=33
- 2025: LOCKED / NOT OPENED
- 2026: QUARANTINED / NOT USED
- Random split: NONE
- Database: READ_ONLY

## Optimization vector and bounds
`theta = [log2(C), log2(gamma), epsilon]`

- log2(C): [-8, 12]
- log2(gamma): [-12, 4]
- epsilon: [0.01, 0.50]

Parent anchor:
- log2(C)=0
- log2(gamma)=log2(1/12)
- epsilon=0.10

## Adaptive PSO parity rule
Reuses the audited refinement schedule from the completed ANN/ELMFIS/RBFNN line:
- population = 24
- generations = 45
- repeats = 3
- inertia w: 0.90 -> 0.40
- cognitive c1: 2.50 -> 0.50
- social c2: 0.50 -> 2.50
- velocity cap = 0.18 * parameter span
- parent/local/uniform initialization retained from frozen SVR Stage-4 optimizer interface
- chronological inner validation tail only
- validation selects the repeat
- selected hyperparameters are then fit once on all pre-target history
- no target-month actual in optimization or fitting
- no optimizer refit on the outer target history

## Decision gate
Primary comparison:
- Frozen Stage-2 parent: SigmaAE **1449.187363**, direction **19/33**
- Adaptive PSO is promotable only if DEV evidence improves the governed frontier; otherwise it is recorded as benchmark evidence.

## Kontrol ve Uyum Özeti
- Pre-outcome method freeze: PASS
- 2025 opened: NO
- 2026 used: NO
- Random split: NONE
- DB mutation: NONE / READ_ONLY
