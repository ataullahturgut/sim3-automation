# GOLD MONTHLY FORECAST — SVR / DWT-SVR FAMILY LEDGER

Date: 2026-09-28  
Status: **ACTIVE — STAGE 4.1 COMPLETE / STAGE 4.2 NEXT**  
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
**COMPLETE / SCIENTIFIC GATES PASS / META_PARENT_SVR FROZEN**

#### Stage 2A — kernel ablation
Fixed CURRENT8, C=1, epsilon=0.1, training-only scaling.

| Model | DEV SigmaAE | Direction | Decision |
|---|---:|---:|---|
| RBF_SVR | **1524.500568** | **21/33** | kernel leader |
| LINEAR_SVR | 1535.115953 | 19/33 | retained comparator |
| POLY2_SVR | 1793.247438 | 17/33 | not promoted |
| POLY3_SVR | 1810.349586 | 17/33 | not promoted |
| SIGMOID_SVR | 2784.332441 | 15/33 | not promoted |

Run: 36394248901.  
Payload: `009344e607f5e509c33cee79aee3ffc4d8aba31c1434b675490d6b0a11ffdb58`.

#### Stage 2B — representation ablation
Frozen RBF epsilon-SVR; common training-history start 2010-05.

| Representation | DEV SigmaAE | Direction |
|---|---:|---:|
| DAILY_SUMMARY12 | **1449.187363** | 19/33 |
| CURRENT8 | 1518.897044 | **21/33** |
| MIXED20 | 1579.308304 | 17/33 |
| RAW_LEVEL_LAGS8 | 1800.428613 | 18/33 |
| SIMPLE_RETURNS8 | 1850.543554 | 17/33 |

Decision: **DAILY_SUMMARY12** frozen as Stage-2 representation leader.

Run: 36394425649.  
Payload: `4430712c7284e2978b496429528116f61e1fda4f217ca2f399dbf68bc049303b`.

#### Stage 2C — formulation check / parent freeze
Frozen RBF + DAILY_SUMMARY12.

| Formulation | DEV SigmaAE | Direction |
|---|---:|---:|
| epsilon-SVR | **1449.187363** | **19/33** |
| NuSVR | 1525.433400 | 18/33 |

**META_PARENT_SVR = EPSILON_RBF_DAILY12**

Frozen parent identity:
- formulation: epsilon-SVR
- kernel: RBF
- representation: DAILY_SUMMARY12
- feature dimension: 12
- canonical C=1.0
- canonical epsilon=0.1
- canonical gamma=scale
- training-only X/Y standardization
- common training-history start: 2010-05

Run: 36394635849.  
Payload: `5a85e126c827740e04914c4eba3cd4afaf45b67e89c0a9bc361b64fef66d9b29`.

No Stage-2 result used 2025 or 2026.

### Stage 3 — deterministic hyperparameter refinement
**COMPLETE / SCIENTIFIC GATES PASS / TUNING NOT PROMOTED**

Stage 3A coarse nested grid:
- 150 frozen combinations.
- Stage-2 parent: **1449.187363 / 19/33**.
- Stage-3A coarse tuned: **1580.901050 / 20/33**.
- Delta vs parent: +131.713687 SigmaAE.
- Decision: not promoted.

Stage 3B local refinement:
- local neighborhoods frozen around Stage-3A per-origin centers before execution.
- Stage-3B local tuned: **1615.913256 / 22/33**.
- promotion threshold: SigmaAE < 1449.187363.
- Decision: **NOT PROMOTED**.

Final deterministic SVR reference remains:
**EPSILON_RBF_DAILY12_STAGE2_PARENT**
- DEV SigmaAE 1449.187363
- direction 19/33

Stage-3A run: 36395013531; payload `289535fc26a3e12f8b2a2e4da8c86c0dd4c1a565aee30965239432bd6010bfc2`.  
Stage-3B run: 36395363215; payload `8ae88568da68a451d667ef53110888cd0ffe76bbf029003b71cfe37c9e938c9e`.

Deterministic hyperparameter tuning line is CLOSED / NOT PROMOTED.

### Stage 4 execution observability rule — BINDING

Effective 2026-09-28 after Batch 4.2 observability failure:

- A batch of 5 methods means **5 separate GitHub jobs in one workflow**, not 5 background processes inside one shell step.
- Each optimizer must expose its own `queued / in_progress / completed / failure` job status.
- Per-model logs must be directly fetchable while that model is running.
- Aggregation must be a separate downstream job with explicit `needs` on all optimizer jobs.
- Scientific gate and report commit occur only after all optimizer jobs complete.
- Shell background execution using `&` for multiple optimizers in one job is **PROHIBITED**.
- If a model fails, the workflow must preserve the statuses of the other methods; no silent batch-level masking.
- This is an observability/execution rule only; it does not alter model definitions, optimizer budgets, bounds, seeds, or scientific evaluation.

Current Batch 4.2 run was launched before this binding rule and may be used for its final scientific results if it completes cleanly, but it is **NOT an acceptable template for later batches**.

### Stage 4 — 32/32 metaheuristic SVR broad screen
**MANDATORY / ACTIVE / 4 OF 32 COMPLETE**

Batching amendment:
- Batch 4.1 was already completed as a 4-method batch.
- User directive: all subsequent batches run **5 methods at a time**, except the final remainder.
- Scientific method set and order are unchanged.

Batch 4.1 COMPLETE:
- [x] PSO
- [x] GA
- [x] DE
- [x] MPA

Batch 4.1 DEV ranking:
1. DE — 1590.781952 / 19/33
2. GA — 1611.632502 / 19/33
3. MPA — 1696.206317 / 15/33
4. PSO — 1719.949306 / 17/33
Frozen Stage-2 parent remains better: 1449.187363 / 19/33.
Run: 36396937495.

#### Batch 4.2 — ABC / SSA / GWO / WOA
**COMPLETE / SCIENTIFIC GATE PASS**

| Method | DEV SigmaAE | Direction |
|---|---:|---:|
| ABC | **1563.258913** | 16/33 |
| GWO | 1590.104631 | 18/33 |
| WOA | 1635.345256 | 17/33 |
| SSA | 1659.670617 | **19/33** |

None beats frozen parent 1449.187363 / 19/33.
Run: 36398195330.
Artifact: 10959831017.
Final workflow conclusion failure was push-conflict only; compute/scientific gate passed and report was recovered manually.

Batch 4.2 NEXT:
- [ ] ABC
- [ ] SSA
- [ ] GWO
- [ ] WOA
- [ ] HHO

Batch 4.3:
- [ ] ACO
- [ ] BAT
- [ ] FA
- [ ] MFO
- [ ] FPA

Batch 4.4:
- [ ] FA_FPA
- [ ] CS
- [ ] SCA
- [ ] SALP
- [ ] SMA

Batch 4.5:
- [ ] GOA
- [ ] ALO
- [ ] TLBO
- [ ] JAYA
- [ ] HGS

Batch 4.6:
- [ ] CHOA
- [ ] HGSO
- [ ] AOA
- [ ] CPA
- [ ] KRILL

Batch 4.7 FINAL REMAINDER:
- [ ] CROW
- [ ] DE_ABC
- [ ] MULTISWARM

Progress: **8/32**
No Stage-4 parent selection until all 32 are complete/audited.
Vanilla/deterministic parent remains reference identity #33.

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
**Execute Batch 4.2 as a 5-method batch: ABC, SSA, GWO, WOA, HHO.**

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
