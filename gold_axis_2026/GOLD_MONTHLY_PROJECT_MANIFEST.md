# GOLD MONTHLY FORECAST — CANONICAL PROJECT MANIFEST

**Manifest version:** 1.0  
**Date:** 2026-09-28  
**Repository:** `ataullahturgut/sim3-automation`  
**Branch:** `gold-midas-headswap-v1-20260925`  
**Canonical path:** `gold_axis_2026/GOLD_MONTHLY_PROJECT_MANIFEST.md`  
**Machine-readable registry:** `gold_axis_2026/GOLD_MONTHLY_MODEL_REGISTRY.json`  
**Status:** **CURRENT / BINDING FOR GOLD MONTHLY MODEL-RESEARCH STATE**

---

## 0. Manifest authority and anti-duplication rule

This file is the single project-state authority for the **GOLD MONTHLY FORECAST** research program.

It consolidates the previously fragmented family ledgers, closure files, Challenger-B manifest, stage reports and handoff documents into one operational registry.

### What this manifest controls
Before any new Gold Monthly model is proposed or run, the researcher must check:
1. whether the model/family has already been executed;
2. its exact representation/target/protocol;
3. its canonical DEV result;
4. whether the line is CLOSED, RETAINED, PAUSED, DEFERRED or NOT_RUN;
5. whether reopening requires a genuinely new mechanism, data representation, untouched validation authority or explicit user instruction.

### What old files become
Older family ledgers and result documents are **evidence/provenance records**, not competing project-state manifests. They are not deleted. If an older "next action" conflicts with this file, this manifest controls the current project state.

### Re-run policy
A completed model must **not** be rerun merely because a later conversation forgot it.

A rerun is authorized only when at least one of the following is explicitly true:
- corrected implementation after a documented bug;
- materially different input representation;
- materially different target or horizon;
- new causal/decomposition mechanism;
- new untouched validation authority;
- independent reproducibility audit;
- explicit user instruction to reopen the line.

Changing only a seed, tiny parameter range or cosmetic naming does not create a new model identity.

---

## 1. Binding forecasting contract

- Target: **H=1 next-calendar-month average XAU/USD price**.
- Forecast origin: previous completed calendar month end.
- Main modeled target for CURRENT8 neural/nonlinear lines: next-month Gold log return, reconstructed to price.
- DEV/model selection authority: **2022-04..2024-12, n=33**.
- 2025: locked external/final transport according to family-specific freeze; never used retroactively for tuning.
- 2026: quarantined/reporting-only; never used for model selection.
- Random split: **FORBIDDEN**.
- Target-month leakage: **FORBIDDEN**.
- DB access for research: **READ_ONLY**.
- Active primary metric: **DEV cumulative absolute price error, SigmaAE**.
- Direction: principal complementary criterion.
- Supporting metrics: MAE, RMSE, MAPE/WAPE, relative MAE vs Random Walk, worst month, yearly stability.
- No post-hoc rescue on 2025/2026.

### Current execution cache
Authorized DEV Snapshot V1:
- schema: `GOLD_MONTHLY_DEV_SNAPSHOT_V1_2026-09-28`
- payload SHA-256: `2111e394f60d131995273789fc014dc339db4e1b7672095c89117c133879a3eb`
- exact offline CNN-LSTM parity: **PASS with zero metric difference**
- 2025 rows: 0
- 2026 rows: 0

Compatible future DEV runs should use this snapshot instead of repeated Neon reads.

---

## 2. Status vocabulary

| Status | Meaning |
|---|---|
| RETAIN_PRIMARY | Completed; current primary role |
| RETAIN_PARETO | Completed; retained nondominated / trade-off role |
| RETAIN_BENCHMARK | Completed; important comparator |
| COMPLETE_CLOSED | Family/model line complete; do not reopen without new rationale |
| NOT_PROMOTED | Valid completed experiment; keep result, do not repeat |
| REJECTED | Valid result clearly unsuitable under frozen design |
| SCIENTIFIC_FAIL | Execution completed but scientific/numerical gate failed; ineligible |
| PAUSED_RESUME_AT | Work intentionally paused; exact resume point recorded |
| DEFERRED_REVISIT_LAST | Not rejected; revisit only under specified new evidence |
| FROZEN_NOT_RUN | Method design frozen but no valid result yet |
| NOT_RUN | Explicitly not executed |
| SUPERSEDED | Earlier implementation/result replaced by corrected authority |

---

## 3. Current cross-family canonical DEV table

This table uses the active DEV SigmaAE + direction contract. It is not a claim of statistical superiority; n=33 remains small.

| Model | Family / path | DEV SigmaAE | Direction | Current role |
|---|---|---:|---:|---|
| **ChHHO-ANFIS** | ANFIS | **1413.0298** | 23/33 | RETAIN_PRIMARY price anchor |
| **DE-ABC-RBFNN** | RBFNN | **1415.8371** | **25/33** | RETAIN_PARETO |
| **PLS1 V1 All-4** | Challenger B | **1420.0291** | 20/33 | RETAIN_PARETO / Challenger-B price leader |
| **LMC2_RBF_M32** | GPR/MOGP | **1424.1711** | 19/33 | RETAIN_BENCHMARK; GPR family not fully closed |
| FULL7 equal-weight ANN | ANN | 1428.8590 | 22/33 | RETAIN_BENCHMARK |
| REDUCED4 equal-weight ANN | ANN | 1431.4587 | 24/33 | RETAIN_PARETO balanced |
| EPSILON_RBF_DAILY12 | SVR | 1449.1874 | 19/33 | PAUSED family leader |
| CATBOOST_PRICE | Boosting | 1460.4339 | 20/33 | COMPLETE_CLOSED family price leader |
| AOA-ELM | ELM | 1474.1021 | 20/33 | COMPLETE_CLOSED benchmark |
| 108-month DMS diagnostic | DMA/DMS/IDMA | 1483.8794 | 20/33 | diagnostic only; family deferred |
| FULL5_MEDIAN | Boosting ensemble | 1484.7313 | 23/33 | COMPLETE_CLOSED direction/balance |
| Canonical DMA | DMA/DMS/IDMA | 1486.2561 | 19/33 | DEFERRED_REVISIT_LAST |
| PLS2 V1 | Challenger B | 1489.3300 | 23/33 | RETAIN_PARETO secondary |
| Canonical DMS | DMA/DMS/IDMA | 1489.8247 | 20/33 | DEFERRED_REVISIT_LAST |
| Random Forest reference | Historical Gold Monthly | 1491.5507 | 20/33 | RETAIN_BENCHMARK; not rerun in Challenger B |
| Ridge V1 | Challenger B | 1520.9926 | 21/33 | NOT_PROMOTED |
| ABC-ELMFIS | ELMFIS | 1524.8900 | 21/33 | COMPLETE_CLOSED price benchmark |
| CNN-LSTM LB6/W32/D0.10 | CNN/LSTM | 1528.5699 | 20/33 | ACTIVE family leader |
| Huber V1 | Challenger B | 1530.1300 | 20/33 | NOT_PROMOTED |
| Extra Trees V1 | Challenger B | 1539.9221 | 20/33 | NOT_PROMOTED |
| Elastic Net V1 | Challenger B | 1590.3571 | 16/33 | NOT_PROMOTED |
| GPReg-Matérn V1 | Challenger B | 1637.9165 | 19/33 | NOT_PROMOTED |
| BiLSTM vanilla | CNN/LSTM structural | 1638.0968 | 19/33 | NOT_PROMOTED |
| SMA-ELMFIS | ELMFIS | 1651.4482 | **25/33** | RETAIN_PARETO direction specialist |
| GPReg-RBF V1 | Challenger B | 1696.3365 | 16/33 | NOT_PROMOTED |
| SARIMA | Challenger B classical | 1751.5242 | 19/33 | NOT_PROMOTED |
| ARIMA | Challenger B classical | 1781.7822 | 15/33 | NOT_PROMOTED |
| HGB V1 | Challenger B | 1840.2678 | 20/33 | NOT_PROMOTED |
| TimesFM-3 zero-shot V1 | Foundation model | 1850.4113 | 19/33 | NOT_PROMOTED / V1 closed |
| Vanilla ANFIS | ANFIS | 1852.0465 | 21/33 | architecture anchor only |
| Vanilla ELMFIS | ELMFIS | 1996.2933 | 20/33 | architecture anchor only |
| TimeMixer++ V1 | Deep time series | 4232.5931 | 13/33 | REJECTED / V1 closed |
| Prophet | Challenger B classical | 7521.1360 | 14/33 | REJECTED |

Notes:
- PLS1 and PLS2 are Challenger-B results and are now part of the same canonical monthly registry.
- The 108-month DMS row is a diagnostic window result, not the canonical family model.
- GPR Stage 3 is complete, but no final Stage-4/5 family closure is present in the repository; do not falsely mark the whole GPR family frozen.
- SVR is intentionally paused before completing the later structural DWT line.
- The current CNN/LSTM structural program is still active.

---

## 4. Common optimizer parity set already explored

The following optimizer identities have been executed repeatedly across ELM/ANN/ELMFIS/ANFIS/RBFNN/GPR, and broadly across SVR. They are **not novel methods** for this project merely because they are attached to another familiar base learner:

1. Vanilla
2. PSO
3. GA
4. DE
5. MPA
6. ABC
7. SSA
8. GWO
9. WOA
10. HHO
11. ACO
12. Bat
13. FA
14. MFO
15. FPA
16. FA-FPA
17. CS (Cuckoo Search)
18. SCA
19. Salp
20. SMA
21. GOA
22. ALO
23. TLBO
24. JAYA
25. HGS
26. ChOA
27. HGSO
28. AOA
29. CPA
30. Krill Herd
31. Crow Search
32. DE-ABC
33. Multi-swarm

This common parity roster is a duplicate-prevention registry. A future use on a genuinely new base architecture may still be valid, but must be justified as a new architecture-specific experiment rather than described as a new optimizer discovery.

---

## 5. Family ledger — ELM

**Status: COMPLETE_CLOSED.**

### Executed scope
- Vanilla ELM.
- Broad parity screen covering the common optimizer set.
- Targeted refinements:
  - Adaptive PSO-ELM
  - TLBO-tuned PSO-ELM
  - DE-tuned PSO-ELM
  - Adaptive/Improved TLBO-ELM
  - Adaptive Crow Search-ELM
  - PSO-TLBO Hybrid ELM

### Active-metric references
- AOA-ELM: **1474.1021 / 20/33** — price benchmark.
- SCA-ELM: **1508.71 / 21/33**.
- PSO-TLBO Hybrid ELM: **1487.55 / 20/33**.
- TLBO-ELM: **1758.75 / 23/33** — direction benchmark within ELM.
- Vanilla ELM: about **1480.08 / 21/33**.

### Decision
- AOA-ELM retained as ELM price benchmark.
- No additional arbitrary ELM optimizer cross-products.
- Reopen only for a structurally different ELM mechanism or new untouched authority.

Detailed evidence:
- `GOLD_MONTHLY_ELM_METAHEURISTIC_LEDGER_ANN_PLAN_2026-09-25.md`
- `GOLD_MONTHLY_CROSS_FAMILY_REAUDIT_SIGMAAE_DIRECTION_2026-09-26.md`

---

## 6. Family ledger — ANN

**Status: COMPLETE / FROZEN.**

### Broad screen
33/33 canonical ANN identities completed:
- Vanilla ANN plus the full common optimizer parity set.

### Mandatory refinements completed
- Adaptive PSO-ANN
- Adaptive TLBO-ANN
- TLBO-tuned PSO-ANN
- DE-tuned PSO-ANN
- Adaptive Crow Search-ANN
- PSO-TLBO Hybrid ANN

### Evidence-driven hybrids completed
- MPA+SCA Hybrid ANN
- MPA+GA Hybrid ANN
- MPA+CPA fallback

### Frozen ensembles
- FULL7 equal-weight ANN: **1428.8590 / 22/33**
- REDUCED4 equal-weight ANN: **1431.4587 / 24/33**

Relevant single-model references:
- MPA-ANN: about **1471.53 / 19/33**
- SCA-ANN: direction specialist in the original ANN screen
- DE-ABC-ANN: retained component
- TLBO-tuned PSO-ANN: strong direction refinement

### Decision
- FULL7 retained benchmark.
- REDUCED4 retained balanced Pareto challenger.
- No post-hoc subset fishing; Stage 4 freeze remains binding.
- Do not repeat the 33-model broad ANN screen.

Evidence:
- `GOLD_MONTHLY_ANN_STAGE4_FINAL_FREEZE_AUDIT_2026-09-25.md`
- `GOLD_MONTHLY_CROSS_FAMILY_REAUDIT_SIGMAAE_DIRECTION_2026-09-26.md`

---

## 7. Family ledger — ELMFIS

**Status: COMPLETE_CLOSED.**

### Executed scope
- Vanilla ELMFIS.
- 33-entry broad parity screen.
- Six mandatory refinements.
- ANN-parity hybrids including MPA+SCA / related admitted hybrids.
- CQCSA-ELMFIS literature-specific experiment.

### Canonical results
- Vanilla ELMFIS: **1996.2933 / 20/33**
- ABC-ELMFIS: **1524.89 / 21/33** — price benchmark.
- SMA-ELMFIS: **1651.4482 / 25/33** — direction specialist.
- CQCSA-ELMFIS: **1731.94 / 20/33** — NOT_PROMOTED.

### Decision
- ABC = internal price benchmark.
- SMA = auxiliary direction / confirmation specialist.
- Hard SMA direction override not promoted.
- CQCSA adds no Pareto point.
- No repeat of the full optimizer parity program.

Evidence:
- `GOLD_MONTHLY_ELMFIS_STAGE3C_CQCSA_2026-09-26.md`
- `GOLD_MONTHLY_CROSS_FAMILY_REAUDIT_SIGMAAE_DIRECTION_2026-09-26.md`

---

## 8. Family ledger — ANFIS

**Status: COMPLETE_CLOSED.**

### Executed
- checked canonical Vanilla ANFIS.
- 32/32 metaheuristic ANFIS broad screen.
- 27/32 passed scientific forecast gate.
- broad-screen scientific rejects: **ABC, WOA, FPA, HGS, AOA** due pathological forecast magnitude.
- Stage-2 benchmarks:
  - MFO-ANFIS: **1630.3325 / 20/33**
  - HHO-ANFIS: **1646.1336 / 23/33**
- Stage-3 parity refinements:
  - MPA-CPA: 1918.5637 / 18
  - PSO-TLBO Hybrid: 3156.9979 / 19
  - TLBO-tuned PSO: 3465.1623 / 20
  - Adaptive PSO, Adaptive TLBO, Adaptive Crow, DE-tuned PSO, MPA-SCA, MPA-GA: scientific-gate fail
- literature-specific:
  - **ChHHO-ANFIS: 1413.0298 / 23/33**
  - MVO-ANFIS: 2057.3973 / 17/33 after implementation bug correction
- controlled ensemble diagnostics completed; learned/prequential blends not promoted.

### Decision
- ChHHO-ANFIS = primary ANFIS champion and current price anchor.
- No further ANFIS optimizer/stacking expansion without explicit reopening.

Evidence:
- `GOLD_MONTHLY_ANFIS_FAMILY_FINAL_CLOSURE_2026-09-26.md`
- `GOLD_MONTHLY_ANFIS_FINAL_CLOSURE_CROSS_FAMILY_2026-09-26.md`

---

## 9. Family ledger — RBFNN

**Status: COMPLETE / FROZEN.**

### Executed
- Vanilla RBFNN.
- Regularized RBFNN benchmark.
- 32/32 broad optimizer screen.
- six mandatory refinements:
  - Adaptive PSO
  - Adaptive TLBO
  - TLBO-tuned PSO
  - DE-tuned PSO
  - Adaptive Crow
  - PSO-TLBO Hybrid
- Stage 3B evidence-driven hybrids: CLOSED_NOT_OPENED by predeclared complementarity gate.
- MOLS-RBFNN literature-specific structural experiment.
- controlled ensembles + shrinkage/prequential audit.

### Canonical results
- **DE-ABC-RBFNN: 1415.8371 / 25/33** — family champion and global Pareto point.
- Adaptive Crow: 1455.8616 / 21.
- PSO-TLBO: 1489.6671 / 21.
- MOLS-RBFNN: 1578.5391 / 18.
- FULL_MEDIAN ensemble: 1444.3008 / 22 — benchmark, not primary.

### Decision
- DE-ABC retained.
- Family frozen.
- Do not repeat broad/meta refinement search.

Evidence:
- `GOLD_MONTHLY_RBFNN_FINAL_FREEZE_2026-09-26.md`

---

## 10. Family ledger — GPR / MOGP

**Status: STAGE 3 COMPLETE / FAMILY FINAL CLOSURE NOT PROVEN.**

### Completed
- Stage 0 audited.
- Stage 1 broad screen: 32 models audited.
- Stage 2 parent freeze.
- Stage 3A six refinements:
  - Adaptive PSO
  - Adaptive TLBO
  - TLBO-tuned PSO
  - DE-tuned PSO
  - Adaptive Crow
  - PSO-TLBO
- Stage 3B MPA-SCA.
- Stage 3C genuine structural model LMC2_RBF_M32.

### Stage-3 canonical results
| Model | DEV SigmaAE | Direction |
|---|---:|---:|
| **LMC2_RBF_M32** | **1424.1711** | 19/33 |
| MPA_SCA | 1709.2943 | 22/33 |
| Adaptive Crow | 1724.2888 | 19/33 |
| Adaptive TLBO | 1740.8877 | 19/33 |
| Adaptive PSO | 1794.2201 | 20/33 |
| PSO_TLBO | 1815.3287 | 21/33 |
| TLBO-tuned PSO | 1863.6677 | 19/33 |
| DE-tuned PSO | 1939.8588 | 16/33 |

### Decision
- LMC2_RBF_M32 retained as eligible GPR benchmark.
- Do **not** rerun Stages 0-3.
- Repository evidence shows Stage-4 pool freeze but no final Stage-4/5 family closure. If GPR is resumed, resume from the frozen Stage-4 state; do not restart broad search.

Evidence:
- `GOLD_MONTHLY_GPR_STAGE3_REPORT_2026-09-26.md`
- `GOLD_MONTHLY_GPR_STAGE3_CLOSURE_2026-09-26.json`
- `GOLD_MONTHLY_GPR_STAGE4_POOL_FREEZE_2026-09-26.json`

---

## 11. Family ledger — Boosting / Trees

**Status: COMPLETE_CLOSED.**

### Completed model lines
- CatBoost PRICE / BALANCED.
- GBRT.
- LightGBM.
- XGBoost direction component.
- CatBoost metaheuristic finalists: DE-ABC, PSO, MFO, HHO, TLBO.
- CMA-ES-GBRT.
- TPE/Optuna-GBRT.
- causal CEEMDAN-XGB.
- causal VMD-XGB.
- controlled median/equal/inverse-MAE ensembles.
- expanding-prequential simplex.
- shrinkage robustness.
- 2025 one-shot final holdout after freeze.

### Canonical DEV results
- CATBOOST_PRICE: **1460.4339 / 20/33**
- FULL5_MEDIAN: **1484.7313 / 23/33**
- frozen GBRT comparator: 1500.4295 / 22
- TPE-GBRT: 1576.9729 / 18
- CMA-ES-GBRT: 1650.1985 / 18
- CEEMDAN-XGB: 1820.4746 / 17
- VMD-XGB: 2019.0624 / 15

### Decision
- PRICE = CATBOOST_PRICE.
- BALANCE/DIRECTION = FULL5_MEDIAN.
- CatBoost optimizer enumeration, same GBRT optimization, decomposition branch, learned weights and arbitrary subset search are CLOSED.

Evidence:
- `GOLD_MONTHLY_BOOSTING_FAMILY_FINAL_CLOSURE_2026-09-28.md`

---

## 12. Family ledger — SVR / DWT-SVR

**Status: PAUSED_RESUME_AT Stage 5A.3.**

### Completed
- canonical Linear/RBF SVR.
- kernel ablation: RBF, Linear, Poly2, Poly3, Sigmoid.
- representation ablation:
  - CURRENT8
  - DAILY_SUMMARY12
  - MIXED20
  - RAW_LEVEL_LAGS8
  - SIMPLE_RETURNS8
- epsilon-SVR vs NuSVR.
- deterministic coarse + local tuning.
- 32/32 metaheuristics technically executed; FA technically completed but user-excluded from authoritative ranking.
- Stage 5A.1 Adaptive PSO.
- Stage 5A.2 TLBO-tuned PSO.

### Key results
- **EPSILON_RBF_DAILY12: 1449.1874 / 19/33** — current family leader.
- RBF CURRENT8: 1524.5006 / 21.
- deterministic coarse: 1580.9011 / 20.
- deterministic local: 1592.5905 / 22.
- best authoritative metaheuristic ALO: 1494.8081 / 20.
- Adaptive PSO: 1748.6557 / 16.
- TLBO-tuned PSO: 1871.8062 / 17.
- FA technical: 1583.8106 / 19, user-excluded.

### Exact resume point
If this family is explicitly reopened:
1. DE-tuned PSO-SVR
2. Adaptive/Improved TLBO-SVR
3. Adaptive Crow Search-SVR
4. PSO-TLBO Hybrid SVR
5. conditional Stage 5B only if evidence justifies
6. causal DWT/MODWT-SVR structural line
7. controlled ensemble
8. robustness
9. family freeze
10. 2025 one-shot

Do not restart Stages 1-4.

Evidence:
- `GOLD_MONTHLY_SVR_DWT_FAMILY_LEDGER_2026-09-28.md`

---

## 13. Family ledger — DMA / DMS / IDMA

**Status: DEFERRED_REVISIT_LAST / NOT REJECTED.**

Canonical corrected results:
- DMA alpha=.99/lambda=.99: **1486.2561 / 19/33**
- DMS: **1489.8247 / 20/33**
- 108-month DMS diagnostic: **1483.8794 / 20/33**
- exploratory IDMA expanding MSFE selector: 1495.6721 / 20
- exploratory IDMA price-AE selector: 1495.5268 / 20

Small market augmentation did not rescue the family.

### Reopen condition
Only revisit with a substantially broader, literature-faithful, origin-safe macro-financial predictor panel or after higher-priority families are complete.

Do not spend compute on small alpha/lambda/window tweaks under CURRENT8.

Evidence:
- `GOLD_MONTHLY_DMA_DMS_IDMA_DEFERRED_CHECKPOINT_2026-09-27.md`

---

## 14. Challenger B — full completed scope

**Status: COMPLETE for user-authorized Challenger-B scope.**

Challenger B is now part of this master registry; its separate manifest is a detailed evidence document, not a separate current-state authority.

### DEV results
| Model | Representation | DEV SigmaAE | Direction | rel.MAE/RW | Decision |
|---|---|---:|---:|---:|---|
| **PLS1 V1** | CURRENT8 | **1420.0291** | 20/33 | 0.8078 | RETAIN |
| PLS2 V1 | CURRENT8 multi-output | 1489.3300 | **23/33** | 0.8472 | RETAIN secondary |
| Ridge V1 | CURRENT8 | 1520.9926 | 21/33 | 0.8652 | NOT_PROMOTED |
| Huber V1 | CURRENT8 | 1530.1300 | 20/33 | 0.8704 | NOT_PROMOTED |
| Extra Trees V1 | CURRENT8 | 1539.9221 | 20/33 | 0.8760 | NOT_PROMOTED |
| Elastic Net V1 | CURRENT8 | 1590.3571 | 16/33 | 0.9046 | NOT_PROMOTED |
| GPReg-Matérn V1 | CURRENT8 | 1637.9165 | 19/33 | 0.9317 | NOT_PROMOTED |
| GPReg-RBF V1 | CURRENT8 | 1696.3365 | 16/33 | 0.9649 | NOT_PROMOTED |
| SARIMA | raw monthly Gold | 1751.5242 | 19/33 | 0.9963 | NOT_PROMOTED |
| ARIMA | raw monthly Gold | 1781.7822 | 15/33 | 1.0135 | NOT_PROMOTED |
| HGB V1 | CURRENT8 | 1840.2678 | 20/33 | 1.0468 | NOT_PROMOTED |
| Prophet | raw monthly Gold | 7521.1360 | 14/33 | 4.2782 | REJECTED |

### PLS1 metal ablation
| Variant | Metals | DEV SigmaAE | Direction |
|---|---|---:|---:|
| ALL4 reference | Au+Ag+Pt+Pd | **1420.0291** | 20/33 |
| No Silver | Au+Pt+Pd | 1454.3225 | **22/33** |
| No Palladium | Au+Ag+Pt | 1461.6772 | 19/33 |
| Gold+Silver | Au+Ag | 1491.2346 | 20/33 |
| Gold only | Au | 1519.4727 | 21/33 |
| No Platinum | Au+Ag+Pd | 1519.6757 | 20/33 |

Binding representation:
- primary PLS1 remains **all four metals**.
- No-Silver retained only as direction-heavy Pareto diagnostic.

### Explicitly not run in Challenger B
- Seasonal Naive
- Drift
- Theta
- Optimized Theta
- SARIMAX_SAFE
- Dynamic Ridge
- exact Grup-ARGE Linear SVR port

These are **NOT_RUN**, not completed experiments.

Evidence:
- `GOLD_MONTHLY_CHALLENGER_B_MANIFEST_2026-09-28.md`

---

## 15. CNN / LSTM structural family

**Status: ACTIVE STRUCTURAL PROGRAM.**

### Stage 0 canonical
- LSTM LB12: 1738.0595 / 15
- CNN LB12: 1906.9426 / 13
- CNN-LSTM LB12: 1554.3082 / 18

### Stage 1A lookback
Winners:
- LSTM LB3: **1589.9827 / 19**
- CNN LB3: **1641.8275 / 21**
- CNN-LSTM LB6: **1528.5699 / 20**

Lookback was the only local tuning dimension that produced a meaningful family-level gain.

### Stage 1B width
- LSTM winner W32: 1589.9827 / 19
- CNN W16 technical price near-tie: 1641.5065 / 20; W32 direction 21
- CNN-LSTM winner W32: 1528.5699 / 20

### Stage 1C dropout
- LSTM D0.10: **1589.9827 / 19**
- CNN-LSTM D0.10: **1528.5699 / 20**
- D0 and D0.20 did not improve the parents.

### Stage 1D learning rate
- LSTM LR0.0003: 1648.5032 / 20 — no meaningful gain
- CNN LR0.0003: 1637.1770 / 21 — only ~0.264% price gain, below pre-frozen meaningful threshold
- CNN-LSTM LR0.0003: 1583.4676 / 18 — worse

Pre-frozen stop rule triggered:
- batch-size sweep skipped
- kernel micro-sweep skipped
- local Cartesian micro-tuning closed

### BiLSTM structural challenger
Vanilla BiLSTM LB3/W32/D0.10:
- **1638.0968 / 19/33**
- scientific gate PASS
- snapshot-only execution
- not promoted
- no rescue tuning authorized

### Current family leader
**CNN-LSTM LB6 / W32 / dropout .10 / Adam .001**
- DEV SigmaAE **1528.569850656**
- direction **20/33**
- rel.MAE/RW **0.869493658**

### Exact next model
**CNN-BiLSTM structural challenger — NOT YET RUN at this manifest version.**

Evidence:
- `GOLD_MONTHLY_CNN_LSTM_STAGE1D_LR_RESULT_2026-09-28.md`
- `GOLD_MONTHLY_BILSTM_STRUCTURAL_RESULT_2026-09-28.md`

---

## 16. Foundation / modern sequence challengers

### TimesFM-3 zero-shot V1
Status: COMPLETE / NOT_PROMOTED.
- raw 4-metal monthly multivariate context
- no fine-tuning
- DEV **1850.4113 / 19/33**
- rel.MAE/RW 1.0526
- V1 closed
- research-only checkpoint licensing noted in result document

### TimeMixer++ V1
Status: COMPLETE / REJECTED V1.
- raw 4-metal levels, 48-month context
- DEV **4232.5931 / 13/33**
- rel.MAE/RW 2.4076
- V1 closed; no architecture fishing

### TimeXer V1
Status: **FROZEN_NOT_RUN**.
- pre-run freeze exists
- seq_len 48, patch_len 6, MS exogenous/endogenous formulation
- no valid result file exists at this manifest version

Do not describe TimeXer as tested until a successful result artifact exists.

---

## 17. Existing references not to duplicate casually

- Random Forest reference: **1491.550694 / 20/33**.
- CatBoost PRICE already completed under Boosting.
- XGBoost CURRENT8 / direction and decomposition variants already covered in Boosting.
- SVR already has a dedicated governed family; do not create a duplicate “new SVR” line outside that ledger.
- PLS/Ridge/ElasticNet/Huber/GPR-style regressors are already covered by Challenger B and/or GPR family.
- ARIMA/SARIMA/Prophet have valid Challenger-B results; do not rerun them under a new label without a materially different frozen representation.

---

## 18. Current open roadmap

### Immediate
1. **CNN-BiLSTM** structural challenger using authorized Snapshot V1.
2. Only if CNN-BiLSTM is promising: small, predeclared structural refinement.

### Later planned distinct families
- ICEEMDAN-LSTM-CNN-CBAM.
- GRU / Attention-GRU / MA-GRUS.
- Transformer / PatchTST / DPformer.
- LSTM-Transformer.
- TimeXer V1 remains frozen-but-unrun and may be executed separately.
- SVR resumes only from Stage 5A.3 if explicitly reopened.
- DMA/DMS/IDMA revisited last with broader literature-faithful predictor panel.

### Closed paths that must not silently reopen
- ANN broad 33-model screen.
- ELM broad/refinement screen.
- ELMFIS broad/refinement screen.
- ANFIS broad/refinement/ensemble line.
- RBFNN broad/refinement/ensemble line.
- Boosting family.
- Challenger-B completed scope.
- BiLSTM rescue tuning.
- CNN/LSTM batch/kernel micro-tuning.
- TimesFM-3 zero-shot V1.
- TimeMixer++ V1.

---

## 19. Corporate experiment-entry standard

Every future model added to this project must append one registry entry with:

- unique model_id;
- family;
- source/authority;
- exact input representation;
- target;
- origin clock;
- train/validation protocol;
- parameters frozen before outcome;
- workflow run/job/artifact/commit;
- DEV SigmaAE;
- DEV direction;
- scientific gate;
- 2025 role;
- 2026 role;
- decision;
- reopen policy;
- predecessor/parent;
- whether snapshot or DB was used.

A model without this entry is not considered properly closed.

---

## 20. Kontrol ve Uyum Özeti

- Challenger B integrated into main monthly manifest: **YES**.
- Fragmented family state replaced by one canonical current-state manifest: **YES**.
- Old detailed ledgers retained as evidence/provenance: **YES**.
- Duplicate-prevention method registry established: **YES**.
- Completed vs not-run methods explicitly separated: **YES**.
- Active metric contract SigmaAE + direction preserved: **YES**.
- Random split: **NONE**.
- 2025/2026 selection contamination: **NONE**.
- Current execution cache: Snapshot V1 authorized.
- Current active next model: **CNN-BiLSTM**.
