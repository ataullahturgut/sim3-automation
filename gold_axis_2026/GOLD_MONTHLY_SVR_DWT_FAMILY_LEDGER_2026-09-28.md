# GOLD MONTHLY FORECAST — SVR / DWT-SVR FAMILY LEDGER

Date: 2026-09-28  
Status: **STAGE 5A ACTIVE — 1/6 REFINEMENTS COMPLETE; STAGE 4 CLOSED AT 31/32 SCORED, FA UNSCORED**  
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
- frozen 136-point local union around Stage-3A modal selection regions.
- Stage-3B local tuned: **1592.590456 / 22/33**.
- Delta vs parent: **+143.403093 SigmaAE**.
- promotion threshold: SigmaAE < 1449.187363.
- Decision: **NOT PROMOTED**.

Final deterministic SVR reference remains:
**EPSILON_RBF_DAILY12_STAGE2_PARENT**
- DEV SigmaAE 1449.187363
- direction 19/33

Stage-3A run: 36395013531; payload `289535fc26a3e12f8b2a2e4da8c86c0dd4c1a565aee30965239432bd6010bfc2`.  
Stage-3B authoritative run: **36396414897**; payload `798f16bf175d010007529ffa0b1c47000fe9e36c66a7739ef33debc93fc3c4ab`.  
Earlier Stage-3B artifacts are superseded by this later frozen-union run.

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
**CLOSED BY USER AMENDMENT / 31 OF 32 SCORED; FA UNSCORED**

Batching amendment:
- Batch 4.1 completed as a 4-method batch before the user batching amendment.
- Batch 4.2 completed as a 5-method batch.
- Batch 4.3 was launched as a 5-method batch; FA was deferred by user after four methods completed.
- Effective 2026-09-28 09:33Z, **all remaining metaheuristics are run one-by-one**.
- FA remains deferred and will be revisited last.
- Candidate set, order, bounds, budget, objective, seeds and scientific gates are unchanged.

Batch 4.1 COMPLETE:
- [x] PSO — 1719.949306 / 17/33
- [x] GA — 1611.632502 / 19/33
- [x] DE — **1590.781952 / 19/33**
- [x] MPA — 1696.206317 / 15/33
Run: 36396937495.

Batch 4.2 COMPLETE — authoritative five-method run:
- [x] ABC — 1563.258913 / 16/33
- [x] SSA — 1659.670617 / 19/33
- [x] GWO — 1590.104631 / 18/33
- [x] WOA — 1635.345256 / 17/33
- [x] HHO — **1549.539823 / 18/33**
Run: **36399323779**.
Job: 108853166239.
Artifact: 10959784334.
Scientific gate: PASS.
Overall workflow failure = final non-fast-forward report push only; compute, aggregate, gate and artifact upload all succeeded.
Earlier four-method Batch-4.2 run 36398195330 is **SUPERSEDED** by this five-method result.

Frozen Stage-2 parent remains better than every completed metaheuristic:
**EPSILON_RBF_DAILY12 = 1449.187363 / 19/33.**

Batch 4.3 PARTIAL — user requested FA deferment:
- [x] ACO — 1600.397350 / 18/33
- [x] BAT — **1540.482107 / 14/33**
- [!] FA — UNSCORED / STOPPED BY USER; do not rank as pass/fail on performance
- [x] MFO — 1690.484321 / **20/33**
- [x] FPA — 1605.813991 / 15/33

Current four-model partial price ranking:
1. BAT — 1540.482107
2. ACO — 1600.397350
3. FPA — 1605.813991
4. MFO — 1690.484321

Frozen Stage-2 parent remains better on primary DEV SigmaAE:
EPSILON_RBF_DAILY12 = **1449.187363 / 19/33**.

Run: **36401901203**.
User instruction at 2026-09-28 09:30Z: defer FA and evaluate completed models now.
FA is not counted as complete until explicitly resumed/accepted.

Remaining single-method order (effective 09:33Z):
- [x] FA_FPA — 1572.041237 / 20/33 — run 36404444819 — gate PASS
- [x] CS — 1564.515299 / 19/33
- [x] SCA — 1843.705276 / 14/33
- [x] SALP — 1543.355326 / 19/33
- [x] SMA — 1517.362987 / 18/33


CS single-method run:
- Run: **36406075410**
- Job: **108875011525**
- Scientific gate: **PASS**
- DEV SigmaAE: **1564.515299**
- Direction: **19/33**
- Payload SHA256: `17d33e6a929dd4cad55bf62b5b768bc681e582da8767e46079351ac2fd029d31`
- Frozen Stage-2 parent remains better on primary DEV SigmaAE: 1449.187363 vs 1564.515299.
- Decision: recorded; not promoted while Stage 4 broad screen remains incomplete.


SCA single-method run:
- Run: **36407501882**
- Job: **108879646812**
- Scientific gate: **PASS**
- DEV SigmaAE: **1843.705276**
- Direction: **14/33**
- Relative MAE vs RW: **1.048752**
- Payload SHA256: `a83b7bce58d0fd6869330897f18a578ddf34a465d299cf095da1014ecd2bfeaa`
- Frozen Stage-2 parent is materially better on primary DEV SigmaAE: 1449.187363 vs 1843.705276.
- SCA is also worse than random-walk reference on relative MAE (>1.0).
- Decision: recorded; not promoted.

Batch 4.5:
- [x] GOA — 1617.200714 / 17/33
- [x] ALO — **1494.808085 / 20/33**
- [x] TLBO — 1574.826138 / 20/33
- [ ] JAYA
- [ ] HGS


FA_FPA single-method result:
- Run: **36404444819**
- Job: **108869684865**
- Scientific gate: **PASS**
- DEV SigmaAE: **1572.041237**
- Direction: **20/33**
- Decision: recorded; not promoted.

Sequential five-method run:
- Run: **36409153139**
- Execution order: **SALP -> SMA -> GOA -> ALO -> TLBO**
- All five jobs: **SUCCESS**
- All five scientific gates: **PASS**
- SALP — SigmaAE **1543.355326**, direction **19/33**
- SMA — SigmaAE **1517.362987**, direction **18/33**
- GOA — SigmaAE **1617.200714**, direction **17/33**
- ALO — SigmaAE **1494.808085**, direction **20/33**
- TLBO — SigmaAE **1574.826138**, direction **20/33**
- Best of this five = **ALO**, but frozen Stage-2 parent remains better: **1449.187363 / 19/33**.
- No method promoted yet; Stage-4 broad screen remains incomplete.

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

Progress: **31/32 scored; FA unscored by explicit user stop.**
No Stage-4 parent selection until all 32 are complete/audited.
Vanilla/deterministic parent remains reference identity #33.


### Stage 4 late parallel completion — reconciled 2026-09-28

Parallel5A run **36414795465** — all jobs + aggregate SUCCESS:
- JAYA — 1529.754239 / 18/33
- HGS — 1664.428496 / 18/33
- CHOA — 1560.301510 / 17/33
- HGSO — 1508.944115 / 18/33
- AOA — 1508.677155 / 20/33

Parallel5B run **36415649045** — all jobs + aggregate SUCCESS:
- CPA — 1737.873104 / 16/33
- KRILL — 1770.446584 / 15/33
- CROW — 1541.791658 / 18/33
- DE_ABC — 1514.213571 / 19/33
- MULTISWARM — 1697.478100 / 13/33

Best scored Stage-4 meta remains **ALO = 1494.808085 / 20/33**.
Frozen Stage-2 parent remains better on primary DEV SigmaAE:
**EPSILON_RBF_DAILY12 = 1449.187363 / 19/33**.

FA final run **36416459911** was still running when the user explicitly instructed to leave FA.
FA result is therefore **UNSCORED / NOT ACCEPTED / NOT PERFORMANCE-REJECTED**.
This is a user governance amendment, not an optimizer performance conclusion.

### Stage 5 opening rule after user amendment

ANN/ELMFIS/RBFNN parity review confirms the next governed phase is targeted refinement before ensembles.
Predeclared parity refinement set:
1. Adaptive PSO-SVR
2. TLBO-tuned PSO-SVR
3. DE-tuned PSO-SVR
4. Adaptive / Improved TLBO-SVR
5. Adaptive Crow Search-SVR
6. PSO-TLBO Hybrid SVR

After those six, evidence-driven optimizer hybrids are CONDITIONAL only; they may be closed without opening if no complementarity gate is met, as in RBFNN.

After Stage 5:
- Stage 6 causal DWT/MODWT-SVR structural line
- Stage 7 controlled ensemble
- Stage 8 final robustness
- Stage 9 family freeze
- Stage 10 2025 one-shot holdout

### Stage 5 — targeted refinement / hybrids
**ACTIVE — STAGE 5A 1/6 COMPLETE**

Stage 5A parity refinement set:
- [x] Adaptive PSO-SVR — **1748.655741 / 16/33**
- [ ] TLBO-tuned PSO-SVR
- [ ] DE-tuned PSO-SVR
- [ ] Adaptive / Improved TLBO-SVR
- [ ] Adaptive Crow Search-SVR
- [ ] PSO-TLBO Hybrid SVR

Adaptive PSO-SVR:
- Freeze commit: `ad4b0e2660dd753dcc85a05db1ead8f9dbf2382a`
- Runner commit: `ea6d9f5964e20d7a704441ffa359cd23355dc5ff`
- Workflow commit: `cc38159b03202de2946d976db3c479958056534d`
- Run: **36421221191**
- Job: **108924144043**
- Scientific gate: **PASS**
- DEV SigmaAE: **1748.655741**
- Direction: **16/33**
- MAE: **52.989568**
- RMSE: **65.091441**
- MAPE: **2.5830%**
- Relative MAE vs RW: **0.994685**
- Worst month: **2024-11**
- Payload SHA256: `49b6f5bd6d0f5537b8a59abca529de46376cbf58ce5f5a449720616ef51dafac`
- Frozen Stage-2 parent remains clearly better: **1449.187363 / 19/33**.
- Decision: **NOT PROMOTED**; retain as refinement benchmark evidence.

Stage 5B optimizer hybrids remain CONDITIONAL after all six Stage 5A refinements.

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
**Stage 5A is active. Adaptive PSO-SVR is complete and not promoted. Next authorized refinement: TLBO-tuned PSO-SVR.**

## Kontrol ve Uyum Özeti
- Stage 0 authority freeze: PASS.
- Stage 1 canonical run: PASS.
- Stage 1 determinism: PASS.
- Stage 1 scientific gate: PASS.
- Stage 1 result recorded: PASS.
- Stage 4 scored methods: 31/32; FA unscored by user stop.
- 2025 opened: NO.
- 2026 used: NO.
- Random split: NONE.
- DB writes: NONE / READ_ONLY.
