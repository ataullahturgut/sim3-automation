# GOLD MONTHLY FORECAST — SVR / DWT-SVR FAMILY LEDGER

Date: 2026-09-28  
Status: **ACTIVE — STAGE 0 COMPLETE / STAGE 1 NEXT**  
Branch: `gold-midas-headswap-v1-20260925`

Canonical authority:
`GOLD_MONTHLY_SVR_DWT_AUTHORITY_AND_STAGE_PLAN_2026-09-28.md`

Authority commit:
`70453bd6693a4878bb45021cb9c2ffd02becdf8f`

## Frozen contract
- H=1 next-calendar-month average XAU/USD.
- Origin: previous completed month-end.
- Primary target: next-month Gold log return -> reconstructed price.
- Primary representation entering Stage 1: CURRENT8.
- DEV: 2022-04..2024-12, n=33.
- 2025: LOCKED one-shot final holdout.
- 2026: QUARANTINED / report-only.
- No random split.
- DB READ_ONLY.
- Primary metric: DEV SigmaAE.
- Direction: complementary principal criterion.

## Family distinction
This family is not the historical multi-output `VW_MIDAS_MSVR_SUCCESSOR_V1`.
The new line is single-output Gold epsilon-SVR / causal wavelet-SVR research.

## Stage status

### Stage 0 — Authority / protocol freeze
**COMPLETE / PASS**
- SVR authority checked.
- Gold-specific DWT-SVR authority checked.
- leakage-safe wavelet rule frozen.
- 32/32 metaheuristic parity requirement frozen.
- staged batch order frozen.
- no model result used in plan design.

### Stage 1 — Canonical SVR baseline
**NEXT / NOT YET RUN**
Mandatory:
- LINEAR epsilon-SVR
- RBF epsilon-SVR
- CURRENT8
- standardized X/Y from pre-target training only
- C=1, epsilon=0.1
- RBF gamma=scale
- DEV only

### Stage 2 — Controlled ablations
**PLANNED / NOT YET RUN**
- 2A kernel
- 2B representation
- 2C formulation
- output: frozen META_PARENT_SVR

### Stage 3 — deterministic hyperparameter refinement
**PLANNED / NOT YET RUN**
- coarse nested grid
- local refinement
- freeze continuous metaheuristic bounds

### Stage 4 — 32/32 metaheuristic SVR broad screen
**MANDATORY / NOT YET RUN**

Batch 4.1:
- [ ] PSO
- [ ] GA
- [ ] DE
- [ ] MPA

Batch 4.2:
- [ ] ABC
- [ ] SSA
- [ ] GWO
- [ ] WOA

Batch 4.3:
- [ ] HHO
- [ ] ACO
- [ ] Bat
- [ ] FA

Batch 4.4:
- [ ] MFO
- [ ] FPA
- [ ] FA-FPA
- [ ] CS

Batch 4.5:
- [ ] SCA
- [ ] Salp
- [ ] SMA
- [ ] GOA

Batch 4.6:
- [ ] ALO
- [ ] TLBO
- [ ] JAYA
- [ ] HGS

Batch 4.7:
- [ ] ChOA
- [ ] HGSO
- [ ] AOA
- [ ] CPA

Batch 4.8:
- [ ] Krill Herd
- [ ] Crow Search
- [ ] DE-ABC
- [ ] Multi-swarm

Progress: **0/32**
Vanilla/deterministic tuned SVR will remain reference identity #33.

### Stage 5 — targeted refinement / hybrids
**PLANNED / NOT YET RUN**
Open after all 32 methods audited.

### Stage 6 — causal DWT/MODWT-SVR
**PLANNED / NOT YET RUN**
- causal decomposition engineering gate
- wavelet structure ablation
- frozen SVR on wavelet features
- conditional refinement

### Stage 7 — controlled ensemble
**PLANNED / NOT YET RUN**

### Stage 8 — robustness
**PLANNED / NOT YET RUN**

### Stage 9 — final family freeze
**PLANNED / NOT YET RUN**

### Stage 10 — 2025 one-shot holdout
**LOCKED / NOT YET OPENED**

## Current next authorized action
**Stage 1 — canonical LINEAR + RBF epsilon-SVR baselines.**

## Kontrol ve Uyum Özeti
- Stage 0 authority freeze committed: PASS.
- 32/32 metaheuristic methods recorded: PASS.
- 2025 opened: NO.
- 2026 used: NO.
- Random split: NONE.
- DB writes: NONE.
