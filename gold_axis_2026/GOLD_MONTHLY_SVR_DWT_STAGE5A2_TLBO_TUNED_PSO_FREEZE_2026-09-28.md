# GOLD MONTHLY FORECAST — SVR STAGE 5A.2 TLBO-TUNED PSO FREEZE

Date: 2026-09-28
Status: **FROZEN BEFORE OUTCOME**

## Method
**TLBO-tuned PSO-SVR**

Outer TLBO tunes the PSO control vector:
- inertia `w`
- cognitive coefficient `c1`
- social coefficient `c2`
- velocity cap fraction `vmax_frac`

Frozen bounds copied from the completed ANN/ELMFIS/RBFNN refinement parity implementation:
- w: [0.20, 0.95]
- c1: [0.20, 3.00]
- c2: [0.20, 3.00]
- vmax_frac: [0.05, 0.80]

Outer tuner:
- TLBO population = 6
- TLBO iterations = 5
- nested PSO population = 12
- nested PSO iterations = 20
- outer score = mean chronological validation loss over 2 deterministic nested PSO repeats

Final SVR hyperparameter optimizer:
- PSO population = 24
- generations = 45
- repeats = 3
- optimization vector = [log2(C), log2(gamma), epsilon]
- SVR bounds remain frozen from Stage 4
- repeat selection uses chronological pre-target validation only
- selected hyperparameters fit once on all pre-target history
- no optimizer refit against the outer target

Authority:
- DEV: 2022-04..2024-12, n=33
- 2025 LOCKED / NOT OPENED
- 2026 QUARANTINED / NOT USED
- random split NONE
- DB READ_ONLY

Reference:
- EPSILON_RBF_DAILY12 = SigmaAE 1449.187363 / 19/33

## Kontrol ve Uyum Özeti
Pre-outcome freeze PASS; chronology preserved; 2025/2026 excluded; DB read-only.
