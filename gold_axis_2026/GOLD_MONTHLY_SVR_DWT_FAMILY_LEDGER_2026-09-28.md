# GOLD MONTHLY FORECAST — SVR / DWT-SVR FAMILY LEDGER

Date: 2026-09-28  
Status: **ACTIVE — STAGE 1 COMPLETE / STAGE 2 NEXT**  
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
**COMPLETE / SCIENTIFIC GATE PASS**

Frozen Stage-1 protocol:
- LINEAR epsilon-SVR
- RBF epsilon-SVR
- CURRENT8
- training-only X/Y standardization
- C=1.0
- epsilon=0.1
- RBF gamma=scale
- DEV only 2022-04..2024-12
- target actual read only after forecast construction

DEV results:

| Rank | Model | SigmaAE | MAE | RMSE | MAPE | Rel.MAE/RW | Direction |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | RBF_SVR | **1524.500568** | 46.196987 | 61.849758 | 2.2348% | 0.867179 | **21/33** |
| 2 | LINEAR_SVR | 1535.115953 | 46.518665 | **60.039956** | 2.2931% | 0.873217 | 19/33 |

Year blocks — RBF_SVR:
- 2022 Apr-Dec: 398.120567 / 7 of 9 directions.
- 2023: 385.317157 / 7 of 12.
- 2024: 741.062844 / 7 of 12.

Year blocks — LINEAR_SVR:
- 2022 Apr-Dec: 435.948275 / 6 of 9.
- 2023: 473.710626 / 5 of 12.
- 2024: 625.457051 / 8 of 12.

Decision:
- Stage-1 canonical price leader = **RBF_SVR**.
- No META_PARENT_SVR frozen yet.
- Stage 2 remains mandatory before any parent freeze.
- 2025 remains locked.

Provenance:
- workflow run: **36393188008**
- job: **108833417796**
- artifact: **10957126183**
- runner commit: `d05717d6e7d525c7ea4c001646e2623b18488168`
- workflow commit: `3b99e57d70f9cac6a3265b97a886f286c4bc8c60`
- payload SHA256: `8178e76be47d2e5c3151a1f39c6061082b0a8fdce862d53f1e9b869dd3c3d3a2`

### Stage 2 — Controlled ablations
**NEXT / NOT YET RUN**
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
**Stage 2 — controlled SVR ablations (kernel -> representation -> formulation), then META_PARENT_SVR freeze.**

## Kontrol ve Uyum Özeti
- Stage 0 authority freeze: PASS.
- Stage 1 canonical run: PASS.
- Stage 1 determinism: PASS.
- Stage 1 scientific gate: PASS.
- Stage 1 result recorded: PASS.
- 32/32 metaheuristic methods recorded: PASS.
- 2025 opened: NO.
- 2026 used: NO.
- Random split: NONE.
- DB writes: NONE / READ_ONLY.
