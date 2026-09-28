# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 4 METAHEURISTIC SCREEN FREEZE

Date: 2026-09-28  
Status: **PRE-OUTCOME BINDING FREEZE**  
Applies to: Stage 4.1 through Stage 4.8

## Frozen model identity
All 32 optimizers tune the **same** SVR identity:

- formulation: epsilon-SVR
- kernel: RBF
- representation: DAILY_SUMMARY12
- target: next-month Gold log return
- price reconstruction: previous completed-month Gold average * exp(predicted return)
- training-only X/Y standardization
- common history start: 2010-05

Frozen deterministic reference:
- EPSILON_RBF_DAILY12_STAGE2_PARENT
- DEV SigmaAE 1449.187363
- direction 19/33

Stage-3 coarse/local tuning was NOT promoted.

## Optimization vector

Each optimizer searches exactly three variables:

1. `log2_C`
2. `log2_gamma`
3. `epsilon`

Decode:
- C = 2^log2_C
- gamma = 2^log2_gamma
- epsilon = epsilon

## Continuous bounds

Frozen for all 32 methods:

- log2_C in **[-8, 12]**
- log2_gamma in **[-12, 4]**
- epsilon in **[0.01, 0.50]**

No optimizer receives wider/narrower bounds based on its result.

Canonical initialization center:
- log2_C = 0
- log2_gamma = log2(1/12) ≈ -3.584962500721156
- epsilon = 0.10

The gamma center approximates canonical `gamma=scale` after 12-feature training standardization. It is an initialization anchor only, not a result claim.

Common initial-population rule:
- candidate 0 = canonical center exactly;
- local half of the remaining population = Gaussian perturbation around the canonical center;
- per-dimension local sigma = **10% of the frozen bound span**;
- remaining candidates = uniform over the full frozen bounds;
- clip every candidate to bounds.

This initialization rule is common across methods wherever the reused repository optimizer implementation accepts the shared initializer.

## Common budget

For every method where population/generation semantics apply:
- population / agents: **24**
- generations / iterations: **45**
- deterministic repeats per outer target: **3**

For methods with different native semantics, use the existing repository implementation and match this budget class as closely as its frozen implementation permits.

No method receives extra generations after seeing results.

## Inner chronology

For each outer DEV target:
- use only pre-target rows;
- final 20% of pre-target history = chronological validation tail;
- minimum validation size = 12;
- earlier rows = inner training;
- X/Y scaler fit only on inner training.

## Optimization and validation discipline

Population evolution:
- objective = standardized Gold log-return MAE on **inner training**.

Validation selection:
- validation never directly drives population evolution;
- at each validation check, only the top quartile of candidates by inner-training loss are eligible;
- among those candidates choose lower standardized Gold log-return MAE on the chronological validation tail.

Across 3 deterministic repeats:
- choose the repeat with lowest inner validation MAE.

Outer refit:
- after hyperparameters are selected, fit X/Y scalers on **all pre-target rows**;
- fit one SVR on all pre-target rows with selected hyperparameters;
- forecast the outer target once;
- no second metaheuristic/refit optimization stage.

## Optimizer source rule

Reuse the repository's already-audited optimizer update equations from the ELMFIS/ANN/RBFNN parity infrastructure.

For every method, record:
- source module;
- optimizer function;
- source SHA256;
- seed base;
- method-specific constants;
- population;
- generations;
- repeats.

Only the objective/bounds/model-fit adapter changes to SVR.

## Seed policy

Per target and repeat:
- deterministic target hash;
- existing method-specific repository seed base;
- repeat offset = 1009 * repeat index.

No random uncontrolled seed.

## Mandatory 32 methods / frozen batches

### 4.1
PSO, GA, DE, MPA

### 4.2
ABC, SSA, GWO, WOA

### 4.3
HHO, ACO, Bat, FA

### 4.4
MFO, FPA, FA-FPA, CS

### 4.5
SCA, Salp, SMA, GOA

### 4.6
ALO, TLBO, JAYA, HGS

### 4.7
ChOA, HGSO, AOA, CPA

### 4.8
Krill Herd, Crow Search, DE-ABC, Multi-swarm

No parent/refinement selection until all 32 are audited or a method is formally BLOCKED for a documented technical reason.

## Outer evaluation
- DEV = 2022-04..2024-12, n=33 only.
- 2025 = LOCKED / not built or evaluated.
- 2026 = QUARANTINED / not built or evaluated.
- primary comparison = DEV SigmaAE.
- direction and stability are complementary.

## Scientific gates
Per method:
- 33/33 outer origins unless formally marked scientific failure;
- selected theta within frozen bounds;
- inner validation strictly pre-target;
- finite validation fitness;
- finite forecast;
- abs predicted monthly log return < 1;
- deterministic seed/repeat records;
- DB invariants unchanged;
- no target-period leakage.

Failures remain recorded and are never silently removed from the 32-method ledger.

## Stage 5 relation
After 32/32:
- only DEV evidence may select a compact refinement/hybrid package;
- no arbitrary optimizer cross-product explosion;
- 2025/2026 may not choose refinement parents.

## Kontrol ve Uyum Özeti
- Model identity common to all methods: FROZEN.
- Bounds common to all methods: FROZEN.
- Budget common to all methods: FROZEN.
- Inner objective/validation rule: FROZEN.
- Seed policy: FROZEN.
- 32/32 candidate list: FROZEN.
- 2025 opened: NO.
- 2026 used: NO.
- Random split: NONE.
- DB writes: NONE.
