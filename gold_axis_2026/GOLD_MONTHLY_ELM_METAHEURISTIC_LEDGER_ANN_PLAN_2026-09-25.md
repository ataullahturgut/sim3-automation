> **MASTER-MANIFEST NOTICE — 2026-09-28**
>
> This large file remains a chronological family evidence ledger for ELM/ANN/ELMFIS/RBFNN/GPR development. Current project state, duplicate-prevention rules, Challenger-B integration and the active next action are now governed by:
> - `gold_axis_2026/GOLD_MONTHLY_PROJECT_MANIFEST.md`
> - `gold_axis_2026/GOLD_MONTHLY_MODEL_REGISTRY.json`
>
> Historical "next action" lines below must not override the canonical master manifest.

# GOLD MONTHLY FORECAST — ELM METAHEURISTIC LEDGER & ANN NEXT-PHASE PLAN

> **Current checkpoint — 2026-09-26: N2 GPR Stage0–2 COMPLETE; Stage3A COMPLETE, run36266015124; Stage3AB COMPLETE; Stage3 COMPLETE; Stage4 pools frozen before evaluation; frozen price MULTISWARM1606.7414/23, direction FA_FPA1724.6532/25. RBFNN Stage0–5 COMPLETE/FROZEN.** Primary/direction specialist DE-ABC: DEV ΣAE 1415.8371, direction 25/33. ChHHO remains price leader at 1413.0298 / 23. Ensemble benchmark FULL Median 1444.3008 / 22; not promoted. [Final report](GOLD_MONTHLY_RBFNN_FINAL_FREEZE_2026-09-26.md). Historical entries below remain chronological; latest closure supersedes earlier pending/next-action statuses.


**Date:** 2026-09-25  
**Repository:** ataullahturgut/sim3-automation  
**Research branch:** gold-midas-headswap-v1-20260925  
**Scope:** Monthly H=1 XAU/USD average-price forecasting research. Separate from the daily GOLD CONTROL direction engine.

## 1. Frozen monthly forecast contract

- Target: next calendar month's average XAU/USD price, H=1.
- Origin: previous completed month-end.
- Inputs: frozen 8 origin-safe VW-MIDAS features:
  - Gold, Silver, Platinum, Palladium;
  - prior monthly log-return (MR);
  - GPR-adaptive weighted within-origin-month daily log-return (VW).
- GPR source: official Git PIT vintage only; exact origin vintage; publication-lagged p-1 observation; origin-safe normalization only.
- ELM output: 4 returns jointly (Gold/Silver/Platinum/Palladium), Gold primary.
- Standard ELM optimizer target: hidden input weights and biases only; final beta solved analytically with ridge.
- Standard historical ELM architecture baseline: 16 hidden nodes, sigmoid, ridge alpha 0.001, hidden parameter bounds [-2,2].
- Per-origin training-only inner fitness: chronological last 20% of training; objective = 0.7 * Gold standardized MAE + 0.3 * all-output standardized MAE.
- No random split.
- DEV: 2022-04..2024-12, n=33.
- 2025: locked transport, n=12; never used for tuning/selection.
- 2026 Jan-Jul: retrospective stress/external, n=7; never used for tuning/selection.
- DB access: READ_ONLY.
- 2025/2026 outcomes are reported evidence only, not model-selection authority.

## 2. Broad ELM metaheuristic screen — completed

| # | Method | DEV MAPE % | 2025 MAPE % | 2026 MAPE % | 2026 direction % |
|---:|---|---:|---:|---:|---:|
| 1 | DE-ELM | 2.58768 | 2.55964 | 5.30611 | 57.14 |
| 2 | ABC-ELM | 2.48251 | 2.28817 | 4.30223 | 71.43 |
| 3 | SSA-ELM | 2.47446 | 2.42033 | 4.52602 | 57.14 |
| 4 | GWO-ELM | 2.45696 | 2.43499 | 4.70303 | 85.71 |
| 5 | WOA-ELM | 2.23961 | 2.40077 | 4.44498 | 71.43 |
| 6 | HHO-ELM | 2.60822 | 2.36634 | 4.78169 | 71.43 |
| 7 | ACO-ELM | 2.69993 | 2.29219 | 4.38003 | 71.43 |
| 8 | Bat-ELM | 2.79911 | 3.26336 | 4.63720 | 57.14 |
| 9 | FA-ELM | 3.03251 | 2.80230 | 5.14529 | 71.43 |
| 10 | MFO-ELM | 2.77548 | 3.02021 | 4.85106 | 71.43 |
| 11 | FPA-ELM | 2.34201 | 2.44273 | 5.53509 | 71.43 |
| 12 | FA-FPA-ELM | 2.63753 | 2.42164 | 5.08298 | 57.14 |
| 13 | CS-ELM | 2.73091 | 2.56715 | 4.80174 | 85.71 |
| 14 | SCA-ELM | 2.19271 | 2.12562 | 5.15175 | 57.14 |
| 15 | Salp-ELM | 2.45982 | 3.02242 | 5.07340 | 57.14 |
| 16 | SMA-ELM | 2.53462 | 2.45558 | 4.23362 | 71.43 |
| 17 | GOA-ELM | 2.42952 | 2.58766 | 5.03272 | 71.43 |
| 18 | ALO-ELM | 2.47135 | 2.34011 | 5.12196 | 57.14 |
| 19 | TLBO-ELM | 2.55127 | 2.40035 | 4.02284 | 85.71 |
| 20 | JAYA-ELM | 2.49871 | 2.58768 | 4.79077 | 71.43 |
| 21 | HGS-ELM | 2.45196 | 2.77720 | 4.77476 | 85.71 |
| 22 | ChOA-ELM | 2.64419 | 2.46433 | 6.30334 | 28.57 |
| 23 | HGSO-ELM | 2.26442 | 2.84745 | 4.90256 | 71.43 |
| 24 | AOA-ELM | 2.15854 | 2.52849 | 5.13545 | 42.86 |
| 25 | CPA-ELM | 2.69050 | 2.69493 | 5.43951 | 57.14 |
| 26 | Krill Herd-ELM | 2.64209 | 2.96256 | 4.99841 | 71.43 |
| 27 | Crow Search-ELM | 2.61964 | 2.70122 | 4.07178 | 85.71 |
| 28 | DE-ABC-ELM | 2.53226 | 2.32476 | 4.65316 | 71.43 |
| 29 | Multi-swarm ELM | 2.41470 | 2.41099 | 5.01252 | 57.14 |

### Earlier ELM benchmarks retained

| Method | DEV MAPE % | 2025 MAPE % | 2026 MAPE % | 2026 direction % |
|---|---:|---:|---:|---:|
| Vanilla ELM | 2.19286 | 2.55897 | 5.25830 | 71.43 |
| PSO-ELM | 2.73492 | 2.64138 | 4.09964 | 85.71 |
| GA-ELM | 2.55877 | 2.52288 | 4.74921 | 71.43 |
| MPA-ELM | 2.44941 | 1.98523 | 5.08435 | 57.14 |

## 3. ELM refinement / meta-on-meta / hybrid closure — completed

The purpose of this phase was not to enumerate every possible optimizer cross, but to test a compact follow-up package motivated by observed ELM results.

| Step | Method | What was fine-tuned | DEV MAPE % | 2025 MAPE % | 2026 MAPE % | 2026 direction % | Decision |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | Adaptive PSO-ELM | adaptive w/c1/c2 schedule; hidden; alpha | 2.60499 | 3.06712 | 4.69840 | 57.14 | Did not improve standard PSO transport/stress |
| 2 | TLBO-tuned PSO-ELM | w, c1, c2, Vmax, hidden, alpha | 2.32298 | 2.25634 | 4.40809 | 71.43 | Stronger DEV/2025, weaker 2026 transfer |
| 3 | DE-tuned PSO-ELM | w, c1, c2, Vmax, hidden, alpha | 2.56288 | 2.06271 | 4.85916 | 57.14 | Strong 2025, poor 2026 transfer |
| 4 | Adaptive / Improved TLBO-ELM | teacher gain, learner gain, TF2 probability, decay, hidden, alpha | 2.46807 | 2.67691 | 4.42831 | 71.43 | Did not improve standard TLBO |
| 5 | Adaptive Crow Search-ELM | AP0, flight0, AP slope, flight decay, hidden, alpha | 2.35034 | 2.71236 | 4.75913 | 57.14 | Did not improve standard Crow |
| 6 | PSO-TLBO Hybrid ELM | w, c1, c2, Vmax, PSO/TLBO mix, TLBO gain, hidden, alpha | 2.18548 | 2.26698 | 4.93398 | 57.14 | Excellent DEV fit, poor 2026 transfer |

### ELM closure finding

Across the six refinement experiments, extra meta-optimization often improved DEV and/or 2025 retrospective transport, but did not improve 2026 stress transfer. The repeated pattern is consistent with over-optimization risk in the small-sample monthly setting.

Observed retrospective 2026 robustness among standard ELM variants remains strongest for:
- TLBO-ELM: MAPE 4.02284%, direction 85.71%.
- Crow Search-ELM: MAPE 4.07178%, direction 85.71%.
- PSO-ELM: MAPE 4.09964%, direction 85.71%.

These 2026 results are evidence only. They must not be used as model-selection/tuning authority.

### ELM research status

- Broad single-metaheuristic ELM scan: COMPLETE.
- Targeted adaptive/meta-on-meta/hybrid closure: COMPLETE.
- Additional arbitrary ELM cross-products: PARKED / DO NOT EXPAND without a new scientific rationale.
- Next family: ANN.

## 4. ANN next-phase protocol — binding research order

The ANN phase will deliberately mirror the ELM workflow.

### Phase A — ANN baseline

1. Build/freeze one canonical ANN architecture and training protocol under the same monthly H=1 data contract.
2. Use chronological rolling/expanding-origin evaluation only.
3. Define ANN parameter vector and what the metaheuristic is allowed to optimize.
4. Keep output target, features, origin-safe preprocessing, 2025 transport role and 2026 stress role unchanged.
5. Establish a plain ANN baseline before metaheuristic optimization.

### Phase B — single metaheuristic ANN screen

Run individual metaheuristics first, one optimizer at a time. Do not begin hybrid/meta-on-meta methods until the single-method screen is complete.

Planned single-method ANN checklist:

- [x] Vanilla ANN baseline
- [x] PSO-ANN
- [x] GA-ANN
- [x] MPA-ANN
- [x] DE-ANN
- [x] ABC-ANN
- [x] SSA-ANN
- [x] GWO-ANN
- [x] WOA-ANN
- [x] HHO-ANN
- [x] ACO-ANN
- [x] Bat-ANN
- [x] FA-ANN
- [x] MFO-ANN
- [x] FPA-ANN
- [x] FA-FPA-ANN
- [x] CS-ANN
- [x] SCA-ANN
- [x] Salp-ANN
- [x] SMA-ANN
- [x] GOA-ANN
- [x] ALO-ANN
- [x] TLBO-ANN
- [x] JAYA-ANN
- [x] HGS-ANN
- [x] ChOA-ANN
- [x] HGSO-ANN
- [x] AOA-ANN
- [x] CPA-ANN
- [x] Krill Herd-ANN
- [x] Crow Search-ANN
- [x] DE-ABC-ANN
- [x] Multi-swarm ANN

The single-method ANN screen can be pruned only for a documented scientific or implementation reason; it must not be pruned because of 2025/2026 outcomes.

### Phase C — ANN targeted refinement / hybrid

Only after Phase B is complete:
1. Identify a small set of promising parent optimizers using pre-2025 evidence.
2. Build a compact refinement package rather than exhaustive cross-products.
3. Candidate classes may include:
   - adaptive optimizer -> ANN;
   - meta-optimizer tuning another optimizer -> ANN;
   - cooperative/hybrid optimizer -> ANN.
4. Fine-tuning remains training-only / chronological.
5. 2025 and 2026 remain transport/stress evidence only.

## 5. Governance reminder

- No random split.
- No target-month leakage.
- No 2025/2026 tuning or optimizer selection.
- No DB writes.
- Do not silently change the 8-feature VW-MIDAS input contract.
- Do not mix this monthly-price line with the separate daily direction engine.
- Every ANN experiment must log method, parameter bounds, inner objective, seed policy, training window, metrics by period, and accept/reject/next decision.


## 6. ANN Phase A / Batch 1.1 — completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-ann-meta-batch-1-v1.yml`  
**Run:** 36127630549 — SUCCESS  
**Implementation:** `gold_axis_2026/tools/vw_midas_ann_meta_batch_1_v1.py`

Canonical Vanilla ANN was re-run in the same workflow. The pre-2025 selected baseline remained one hidden layer with 4 units, tanh activation, alpha 1.0, LBFGS training.

PSO-ANN / GA-ANN / DE-ANN use the same frozen 8-feature VW-MIDAS data contract and a fixed 8->4(tanh)->4 linear ANN geometry. The metaheuristics optimize all 56 ANN weights/biases directly. For every target origin:
- all data are pre-target and standardized using only available history;
- the chronological final 20% of training history (minimum 6 rows) is the validation tail;
- population evolution is driven by 0.7*Gold standardized MAE + 0.3*all-output standardized MAE on inner-training;
- validation selects only among the top quartile of candidates by training loss;
- 3 deterministic repeats are used;
- the validation-selected solution is warm-start refit on all pre-target history;
- target-month data are never used in fitness;
- DB access remains READ_ONLY and authority invariants were unchanged.

| Method | DEV MAPE % | DEV Direction % | 2025 MAPE % | 2025 Direction % | 2026 MAPE % | 2026 Direction % |
|---|---:|---:|---:|---:|---:|---:|
| Vanilla ANN | 2.18895 | 54.55 | 2.77892 | 83.33 | 4.57914 | 57.14 |
| PSO-ANN | 2.61194 | 54.55 | 2.59392 | 83.33 | 4.31502 | 85.71 |
| GA-ANN | 2.36033 | 63.64 | 2.71883 | 75.00 | 4.62219 | 71.43 |
| DE-ANN | 2.84842 | 51.52 | 2.41362 | 75.00 | 4.31570 | 71.43 |

### Batch 1.1 interpretation

- **DEV-only ordering for this batch:** Vanilla ANN, GA-ANN, PSO-ANN, DE-ANN by MAPE.
- Vanilla ANN currently remains the strongest Batch 1.1 DEV reference.
- GA-ANN is the strongest metaheuristic ANN in Batch 1.1 on DEV evidence.
- PSO-ANN and DE-ANN did not beat Vanilla ANN on DEV.
- 2025 transport and 2026 stress are recorded strictly as external evidence and were not used for tuning, ranking authority, or parent selection.
- No parent optimizer is frozen yet; the full single-method ANN screen must finish first.

### ANN progress after Batch 1.1

- Completed: **4 / 33**
- Remaining: **29 / 33**
- Next: Batch 1.2 single-metaheuristic ANN screen.


## 7. ANN Phase A / Batch 1.2 — completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-ann-meta-batch-2-v1.yml`  
**Run:** 36128225062 — SUCCESS  
**Implementation:** `gold_axis_2026/tools/vw_midas_ann_meta_batch_2_v1.py`

MPA-ANN, ABC-ANN, SSA-ANN and GWO-ANN use the same canonical 8->4(tanh)->4 linear ANN geometry and the same origin-safe VW-MIDAS data contract as Batch 1.1. The optimization/validation contract is unchanged: 3 deterministic repeats per target, chronological last-20% validation tail, Gold-weighted four-output standardized MAE objective, validation selection restricted to top-quartile training candidates, full pre-target-history refit, target-month exclusion from all fitness calculations, READ_ONLY DB access, and unchanged authority invariants.

| Method | DEV MAPE % | DEV Direction % | 2025 MAPE % | 2025 Direction % | 2026 MAPE % | 2026 Direction % |
|---|---:|---:|---:|---:|---:|---:|
| MPA-ANN | 2.19947 | 57.58 | 2.45524 | 83.33 | 4.05739 | 85.71 |
| ABC-ANN | 3.06525 | 51.52 | 2.99919 | 83.33 | 4.76730 | 71.43 |
| SSA-ANN | 2.41896 | 66.67 | 2.71124 | 83.33 | 4.17629 | 85.71 |
| GWO-ANN | 2.53258 | 54.55 | 2.73568 | 66.67 | 4.89698 | 71.43 |

### Batch 1.2 interpretation

- **DEV-only MAPE ordering inside Batch 1.2:** MPA-ANN, SSA-ANN, GWO-ANN, ABC-ANN.
- MPA-ANN is very close to the current Vanilla ANN DEV MAPE reference (2.19947% vs 2.18895%).
- SSA-ANN has the strongest DEV direction accuracy observed so far (66.67%) but does not beat Vanilla/MPA on DEV MAPE.
- ABC-ANN is currently weak on DEV and also worse than the random-walk benchmark on DEV relative MAE.
- 2025 transport and 2026 stress are external evidence only and were not used to alter ranking or optimizer configuration.
- No parent optimizer is frozen yet.

### ANN progress after Batch 1.2

- Completed: **8 / 33**
- Remaining: **25 / 33**
- Current DEV MAPE ordering across completed models:
  1. Vanilla ANN — 2.18895%
  2. MPA-ANN — 2.19947%
  3. GA-ANN — 2.36033%
  4. SSA-ANN — 2.41896%
  5. GWO-ANN — 2.53258%
  6. PSO-ANN — 2.61194%
  7. DE-ANN — 2.84842%
  8. ABC-ANN — 3.06525%
- Next: Batch 1.3 single-metaheuristic ANN screen.


## 8. ANN Phase A / Batch 1.3 — completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-ann-meta-batch-3-v1.yml`  
**Run:** 36128772974 — SUCCESS  
**Implementation:** `gold_axis_2026/tools/vw_midas_ann_meta_batch_3_v1.py`

WOA-ANN, HHO-ANN, ACO-ANN and Bat-ANN use the same canonical 8->4(tanh)->4 linear ANN geometry and the same origin-safe VW-MIDAS data contract as Batches 1.1–1.2. The same 3-repeat chronological inner-validation, top-quartile validation selection, full-history pre-target refit, target-month exclusion, READ_ONLY DB access and authority-invariant checks were retained.

| Method | DEV MAPE % | DEV Direction % | 2025 MAPE % | 2025 Direction % | 2026 MAPE % | 2026 Direction % |
|---|---:|---:|---:|---:|---:|---:|
| WOA-ANN | 2.38669 | 63.64 | 3.25858 | 75.00 | 4.25585 | 85.71 |
| HHO-ANN | 2.49709 | 57.58 | 2.68056 | 91.67 | 3.91070 | 85.71 |
| ACO-ANN | 2.35494 | 63.64 | 2.95467 | 66.67 | 4.35377 | 71.43 |
| Bat-ANN | 2.64871 | 54.55 | 2.45347 | 75.00 | 4.97714 | 85.71 |

### Batch 1.3 interpretation

- **DEV-only MAPE ordering inside Batch 1.3:** ACO-ANN, WOA-ANN, HHO-ANN, Bat-ANN.
- ACO-ANN is the strongest Batch 1.3 model on DEV MAPE and enters the current upper tier of metaheuristic ANN candidates.
- WOA-ANN also beats the DEV random-walk MAPE benchmark and has 63.64% DEV direction accuracy.
- HHO-ANN is mid-pack on DEV; its strong 2025/2026 external results are recorded but not used for selection.
- Bat-ANN is currently weak on DEV and has relative MAE above the random-walk benchmark.
- No optimizer is frozen as a hybrid parent yet.

### ANN progress after Batch 1.3

- Completed: **12 / 33**
- Remaining: **21 / 33**
- Current DEV MAPE ordering across completed models:
  1. Vanilla ANN — 2.18895%
  2. MPA-ANN — 2.19947%
  3. ACO-ANN — 2.35494%
  4. GA-ANN — 2.36033%
  5. WOA-ANN — 2.38669%
  6. SSA-ANN — 2.41896%
  7. HHO-ANN — 2.49709%
  8. GWO-ANN — 2.53258%
  9. PSO-ANN — 2.61194%
  10. Bat-ANN — 2.64871%
  11. DE-ANN — 2.84842%
  12. ABC-ANN — 3.06525%
- Next: Batch 1.4 single-metaheuristic ANN screen.


## 9. ANN Phase A / Batch 1.4 — completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-ann-meta-batch-4-v1.yml`  
**Run:** 36129113648 — SUCCESS  
**Implementation:** `gold_axis_2026/tools/vw_midas_ann_meta_batch_4_v1.py`

FA-ANN, MFO-ANN, FPA-ANN and CS-ANN retain the frozen canonical 8->4(tanh)->4 linear ANN geometry and the same governed 8-feature VW-MIDAS data contract. Optimization fairness and leakage controls remain unchanged: 3 deterministic repeats per target, chronological last-20% inner validation, top-quartile training candidate validation, full pre-target-history warm-start refit, fixed optimizer budget, no target-month fitness, READ_ONLY DB access, and unchanged authority invariants.

| Method | DEV MAPE % | DEV Direction % | 2025 MAPE % | 2025 Direction % | 2026 MAPE % | 2026 Direction % |
|---|---:|---:|---:|---:|---:|---:|
| FA-ANN | 2.39002 | 60.61 | 2.65891 | 75.00 | 4.06486 | 85.71 |
| MFO-ANN | 2.60702 | 57.58 | 3.70485 | 58.33 | 5.29073 | 57.14 |
| FPA-ANN | 2.70125 | 42.42 | 2.86750 | 83.33 | 5.63250 | 57.14 |
| CS-ANN | 2.50128 | 54.55 | 3.06513 | 66.67 | 4.59451 | 71.43 |

### Batch 1.4 interpretation

- **DEV-only MAPE ordering inside Batch 1.4:** FA-ANN, CS-ANN, MFO-ANN, FPA-ANN.
- FA-ANN enters the upper-middle metaheuristic ANN group but does not beat Vanilla ANN or MPA-ANN.
- CS-ANN is modest on DEV; it narrowly beats the random-walk DEV MAPE benchmark.
- MFO-ANN and FPA-ANN are weak on DEV; both have relative MAE above the random-walk benchmark.
- 2025/2026 evidence remains external only and is not used for ranking authority or parent selection.

### ANN progress after Batch 1.4

- Completed: **16 / 33**
- Remaining: **17 / 33**
- Current DEV MAPE ordering across completed models:
  1. Vanilla ANN — 2.18895%
  2. MPA-ANN — 2.19947%
  3. ACO-ANN — 2.35494%
  4. GA-ANN — 2.36033%
  5. WOA-ANN — 2.38669%
  6. FA-ANN — 2.39002%
  7. SSA-ANN — 2.41896%
  8. HHO-ANN — 2.49709%
  9. CS-ANN — 2.50128%
  10. GWO-ANN — 2.53258%
  11. MFO-ANN — 2.60702%
  12. PSO-ANN — 2.61194%
  13. Bat-ANN — 2.64871%
  14. FPA-ANN — 2.70125%
  15. DE-ANN — 2.84842%
  16. ABC-ANN — 3.06525%
- Next: Batch 1.5 single-metaheuristic ANN screen.


## 10. ANN Phase A / Batch 1.5 — completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-ann-meta-batch-5-v1.yml`  
**Run:** 36129458713 — SUCCESS  
**Implementation:** `gold_axis_2026/tools/vw_midas_ann_meta_batch_5_v1.py`

SCA-ANN, Salp-ANN, SMA-ANN and GOA-ANN retain the frozen canonical 8->4(tanh)->4 linear ANN geometry, the same governed 8-feature VW-MIDAS input contract, and the same fair optimization/evaluation protocol: 3 deterministic repeats per target, chronological final-20% inner validation, top-quartile training candidate validation, fixed optimization budget, warm-start refit on all pre-target history, no target-month fitness, READ_ONLY DB, and unchanged authority invariants.

| Method | DEV MAPE % | DEV Direction % | 2025 MAPE % | 2025 Direction % | 2026 MAPE % | 2026 Direction % |
|---|---:|---:|---:|---:|---:|---:|
| SCA-ANN | 2.36197 | 72.73 | 3.03650 | 75.00 | 4.70795 | 57.14 |
| Salp-ANN | 2.43583 | 60.61 | 2.63556 | 75.00 | 4.53777 | 71.43 |
| SMA-ANN | 2.57631 | 51.52 | 3.62164 | 91.67 | 5.51515 | 28.57 |
| GOA-ANN | 3.00269 | 51.52 | 2.80686 | 58.33 | 5.25250 | 57.14 |

### Batch 1.5 interpretation

- **DEV-only MAPE ordering inside Batch 1.5:** SCA-ANN, Salp-ANN, SMA-ANN, GOA-ANN.
- SCA-ANN becomes the strongest DEV direction model so far at **72.73%**, while its DEV MAPE remains behind Vanilla ANN and MPA-ANN.
- Salp-ANN is competitive middle-tier on DEV and beats the random-walk DEV MAPE benchmark.
- SMA-ANN narrowly beats RW MAPE on DEV but has weak external 2026 stress behavior; external results are not used for selection.
- GOA-ANN is weak on DEV and has relative MAE above the random-walk benchmark.
- No parent optimizer is frozen yet.

### ANN progress after Batch 1.5

- Completed: **20 / 33**
- Remaining: **13 / 33**
- Current DEV MAPE ordering across completed models:
  1. Vanilla ANN — 2.18895%
  2. MPA-ANN — 2.19947%
  3. ACO-ANN — 2.35494%
  4. GA-ANN — 2.36033%
  5. SCA-ANN — 2.36197%
  6. WOA-ANN — 2.38669%
  7. FA-ANN — 2.39002%
  8. SSA-ANN — 2.41896%
  9. Salp-ANN — 2.43583%
  10. HHO-ANN — 2.49709%
  11. CS-ANN — 2.50128%
  12. GWO-ANN — 2.53258%
  13. SMA-ANN — 2.57631%
  14. MFO-ANN — 2.60702%
  15. PSO-ANN — 2.61194%
  16. Bat-ANN — 2.64871%
  17. FPA-ANN — 2.70125%
  18. DE-ANN — 2.84842%
  19. GOA-ANN — 3.00269%
  20. ABC-ANN — 3.06525%
- Current DEV direction leader: **SCA-ANN — 72.73%**.
- Next: Batch 1.6 single-metaheuristic ANN screen.


## 11. ANN Phase A / Batch 1.6 — completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-ann-meta-batch-6-v1.yml`  
**Run:** 36129773054 — SUCCESS  
**Implementation:** `gold_axis_2026/tools/vw_midas_ann_meta_batch_6_v1.py`

ALO-ANN, TLBO-ANN, JAYA-ANN and HGS-ANN retain the frozen canonical 8->4(tanh)->4 linear ANN geometry, the same governed 8-feature VW-MIDAS contract, and the same fair optimization/evaluation protocol: 3 deterministic repeats per target, chronological final-20% validation, top-quartile training candidate validation, fixed optimization budget, warm-start refit on all pre-target history, no target-month fitness, READ_ONLY DB access and unchanged authority invariants.

| Method | DEV MAPE % | DEV Direction % | 2025 MAPE % | 2025 Direction % | 2026 MAPE % | 2026 Direction % |
|---|---:|---:|---:|---:|---:|---:|
| ALO-ANN | 2.49827 | 60.61 | 2.43691 | 75.00 | 4.53480 | 71.43 |
| TLBO-ANN | 2.37828 | 60.61 | 2.56347 | 75.00 | 4.35961 | 85.71 |
| JAYA-ANN | 2.53899 | 63.64 | 3.14153 | 75.00 | 4.18073 | 57.14 |
| HGS-ANN | 2.48142 | 51.52 | 3.01738 | 66.67 | 3.94597 | 85.71 |

### Batch 1.6 interpretation

- **DEV-only MAPE ordering inside Batch 1.6:** TLBO-ANN, HGS-ANN, ALO-ANN, JAYA-ANN.
- TLBO-ANN enters the current upper tier of metaheuristic ANN candidates on DEV MAPE.
- HGS-ANN and ALO-ANN beat the DEV random-walk MAPE benchmark, but remain behind the leading ANN methods.
- JAYA-ANN is only slightly better than the random-walk DEV MAPE benchmark and is not currently a leading price-error candidate.
- Strong 2025/2026 external behavior for HGS/TLBO is recorded only as transport/stress evidence; it did not affect selection or tuning.

### ANN progress after Batch 1.6

- Completed: **24 / 33**
- Remaining: **9 / 33**
- Current DEV MAPE ordering across completed models:
  1. Vanilla ANN — 2.18895%
  2. MPA-ANN — 2.19947%
  3. ACO-ANN — 2.35494%
  4. GA-ANN — 2.36033%
  5. SCA-ANN — 2.36197%
  6. TLBO-ANN — 2.37828%
  7. WOA-ANN — 2.38669%
  8. FA-ANN — 2.39002%
  9. SSA-ANN — 2.41896%
  10. Salp-ANN — 2.43583%
  11. HGS-ANN — 2.48142%
  12. HHO-ANN — 2.49709%
  13. ALO-ANN — 2.49827%
  14. CS-ANN — 2.50128%
  15. GWO-ANN — 2.53258%
  16. JAYA-ANN — 2.53899%
  17. SMA-ANN — 2.57631%
  18. MFO-ANN — 2.60702%
  19. PSO-ANN — 2.61194%
  20. Bat-ANN — 2.64871%
  21. FPA-ANN — 2.70125%
  22. DE-ANN — 2.84842%
  23. GOA-ANN — 3.00269%
  24. ABC-ANN — 3.06525%
- Current DEV direction leader remains **SCA-ANN — 72.73%**.
- Next: Batch 1.7 single-metaheuristic ANN screen.


## 12. ANN Phase A / Batch 1.7 — completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-ann-meta-batch-7-v1.yml`  
**Run:** 36130127593 — SUCCESS  
**Implementation:** `gold_axis_2026/tools/vw_midas_ann_meta_batch_7_v1.py`

ChOA-ANN, HGSO-ANN, AOA-ANN and CPA-ANN retain the frozen canonical 8->4(tanh)->4 linear ANN geometry, governed 8-feature VW-MIDAS inputs, and the same fair optimization/evaluation contract used in all prior ANN batches: 3 deterministic repeats per target, chronological final-20% validation, validation selection restricted to top-quartile training candidates, fixed optimization budget, warm-start refit on all pre-target history, no target-month fitness, READ_ONLY DB access, and unchanged authority invariants.

| Method | DEV MAPE % | DEV Direction % | 2025 MAPE % | 2025 Direction % | 2026 MAPE % | 2026 Direction % |
|---|---:|---:|---:|---:|---:|---:|
| ChOA-ANN | 2.46605 | 60.61 | 2.47875 | 91.67 | 4.47334 | 85.71 |
| HGSO-ANN | 2.66180 | 54.55 | 3.15876 | 75.00 | 5.40566 | 85.71 |
| AOA-ANN | 2.51719 | 57.58 | 3.48182 | 83.33 | 4.85791 | 57.14 |
| CPA-ANN | 2.27985 | 60.61 | 2.66751 | 75.00 | 3.88837 | 71.43 |

### Batch 1.7 interpretation

- **DEV-only MAPE ordering inside Batch 1.7:** CPA-ANN, ChOA-ANN, AOA-ANN, HGSO-ANN.
- CPA-ANN is the strongest Batch 1.7 model and becomes the **third-best ANN overall on DEV MAPE**, behind Vanilla ANN and MPA-ANN.
- ChOA-ANN is competitive middle-upper tier but does not challenge the current price-error leaders.
- AOA-ANN is mid-pack.
- HGSO-ANN is weak on DEV and has relative MAE above the random-walk benchmark.
- Strong 2025/2026 external behavior, where present, remains reporting-only and did not affect tuning or rank authority.

### ANN progress after Batch 1.7

- Completed: **28 / 33**
- Remaining: **5 / 33**
- Current DEV MAPE top tier:
  1. Vanilla ANN — 2.18895%
  2. MPA-ANN — 2.19947%
  3. CPA-ANN — 2.27985%
  4. ACO-ANN — 2.35494%
  5. GA-ANN — 2.36033%
  6. SCA-ANN — 2.36197%
  7. TLBO-ANN — 2.37828%
  8. WOA-ANN — 2.38669%
  9. FA-ANN — 2.39002%
  10. SSA-ANN — 2.41896%
- Current DEV direction leader remains **SCA-ANN — 72.73%**.
- Next: final Batch 1.8 — Krill Herd, Crow Search, FA-FPA, DE-ABC, Multi-swarm ANN.


## 13. ANN Phase A / Batch 1.8 — completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-ann-meta-batch-8-v1.yml`  
**Run:** 36130538857 — SUCCESS  
**Implementation:** `gold_axis_2026/tools/vw_midas_ann_meta_batch_8_v1.py`

Final parity batch completed with Krill Herd-ANN, Crow Search-ANN, FA-FPA-ANN, DE-ABC-ANN and Multi-swarm ANN. The same frozen canonical 8->4(tanh)->4 linear ANN, governed 8-feature VW-MIDAS inputs, 3 deterministic repeats per target, chronological final-20% validation, top-quartile candidate validation selection, fixed optimization budget, full pre-target-history warm-start refit, target-month exclusion, READ_ONLY DB access and authority-invariant checks were retained.

**Important naming control:** CS-ANN completed in Batch 1.4 is Cuckoo Search. Crow Search-ANN in this batch is a distinct optimizer.

| Method | DEV MAPE % | DEV Direction % | 2025 MAPE % | 2025 Direction % | 2026 MAPE % | 2026 Direction % |
|---|---:|---:|---:|---:|---:|---:|
| Krill Herd-ANN | 2.37501 | 66.67 | 3.25709 | 66.67 | 4.80715 | 71.43 |
| Crow Search-ANN | 2.50491 | 60.61 | 2.76303 | 91.67 | 5.34593 | 57.14 |
| FA-FPA-ANN | 2.28398 | 60.61 | 2.37024 | 75.00 | 4.92916 | 85.71 |
| DE-ABC-ANN | 2.26109 | 66.67 | 2.81484 | 83.33 | 5.15819 | 71.43 |
| Multi-swarm ANN | 2.59615 | 54.55 | 2.88801 | 66.67 | 4.66934 | 71.43 |

### Batch 1.8 interpretation

- **DEV-only MAPE ordering inside Batch 1.8:** DE-ABC-ANN, FA-FPA-ANN, Krill Herd-ANN, Crow Search-ANN, Multi-swarm ANN.
- DE-ABC-ANN becomes the second-best metaheuristic/hybrid-parity ANN on DEV MAPE after MPA-ANN and the third-best ANN overall after Vanilla and MPA.
- FA-FPA-ANN is also a strong DEV price-error candidate.
- Krill Herd-ANN combines good DEV MAPE with 66.67% DEV direction accuracy.
- Crow Search-ANN is middle tier on DEV despite strong 2025 direction; 2025 is external evidence only.
- Multi-swarm ANN is weak on DEV and has relative MAE slightly worse than the random-walk benchmark.
- FA-FPA, DE-ABC and Multi-swarm are retained in Phase A only for ELM parity; their hybrid nature is recorded so they will not be double-counted as novel Phase C hybrids.

### ANN Phase A final progress

- **Completed: 33 / 33**
- **Remaining: 0 / 33**
- **AŞAMA 1/5: COMPLETE**

### Final DEV MAPE top tier after all 33 entries

1. Vanilla ANN — 2.18895%
2. MPA-ANN — 2.19947%
3. DE-ABC-ANN — 2.26109%
4. CPA-ANN — 2.27985%
5. FA-FPA-ANN — 2.28398%
6. ACO-ANN — 2.35494%
7. GA-ANN — 2.36033%
8. SCA-ANN — 2.36197%
9. Krill Herd-ANN — 2.37501%
10. TLBO-ANN — 2.37828%

Current DEV direction leader remains **SCA-ANN — 72.73%**.

### Next governed phase

**AŞAMA 2/5 — ANN result filtering and parent selection**
- consolidate all 33 DEV results;
- analyze price-error, direction, RW-relative performance and origin/year stability using DEV only;
- use recorded repeat/inner-validation evidence for robustness review where available;
- keep 2025/2026 outside selection authority;
- freeze only a small parent set for adaptive/meta-on-meta/hybrid ANN work;
- explicitly avoid double-counting FA-FPA, DE-ABC and Multi-swarm as new Phase C inventions.


## 14. ANN Stage 2 / Batch 2.1 — DEV-only filtering audit completed 2026-09-25

**Audit source:** GitHub Actions artifacts from ANN Phase A batches 1.1–1.8.  
**Dedicated report:** `gold_axis_2026/GOLD_MONTHLY_ANN_STAGE2_BATCH21_DEV_FILTER_2026-09-25.md`

### Authority and evidence
- Selection authority remained **DEV 2022-04..2024-12 only (n=33)**.
- 2025 transport and 2026 stress were not used in any filter, retention or exclusion decision.
- No random split was introduced.
- Repeat evidence is validation-fitness dispersion only; it is **not** treated as full forecast seed-variance evidence.
- RW DEV benchmark: MAPE 2.5888209463%, MAE 53.2727272727.

### Filtering result
1. RW gate (DEV MAPE < RW and relative MAE < 1): **24/33 pass**.
2. Core price retention: within +10% of Vanilla ANN DEV MAPE while passing RW gate.
3. Direction rescue: DEV direction >= 66.67% while passing RW gate.
4. Stability rescue: yearly-MAPE SD <= 0.13 and median repeat-validation CV <= 0.035 while passing RW gate.
5. Redundancy prune: **WOA-ANN** and **FA-ANN** removed because other retained models dominate them on the principal DEV predictive/stability metrics and they add no unique role.
6. Pareto cross-check: all nine RW-eligible Pareto-nondominated models on MAPE/RMSE/direction/year-stability are preserved.

### Batch 2.1 retained pool — 12/33
- Vanilla ANN — baseline / price
- MPA-ANN — price leader
- DE-ABC-ANN — price + direction / hybrid-parity
- CPA-ANN — price
- FA-FPA-ANN — price / hybrid-parity
- ACO-ANN — balanced price/RMSE/direction
- GA-ANN — year-stable balanced
- SCA-ANN — direction leader
- Krill Herd-ANN — direction + RW win-rate diversity
- TLBO-ANN — repeat-stable balanced
- SSA-ANN — direction + repeat stability
- HHO-ANN — year + repeat stability

### Excluded at Batch 2.1
**Fail RW gate (9):** ABC-ANN, Bat-ANN, DE-ANN, FPA-ANN, GOA-ANN, HGSO-ANN, MFO-ANN, Multi-swarm ANN, PSO-ANN.

**Pass RW but no price/direction/stability retention role (10):** ALO-ANN, AOA-ANN, CS-ANN, ChOA-ANN, Crow Search-ANN, GWO-ANN, HGS-ANN, JAYA-ANN, SMA-ANN, Salp-ANN.

**Redundancy-pruned (2):** FA-ANN, WOA-ANN.

### Stage status
- **AŞAMA 2/5 — Batch 2.1: COMPLETE**
- Candidate pool: **33 -> 12**
- No final Stage 3 parent is frozen yet.
- Next: **Batch 2.2** — prediction-error correlation/redundancy and role-based parent freezing using DEV only.


## 15. ANN Stage 2 / Batch 2.2 — parent freeze completed 2026-09-25

**Dedicated report:** `gold_axis_2026/GOLD_MONTHLY_ANN_STAGE2_BATCH22_PARENT_FREEZE_2026-09-25.md`

### DEV-only complementarity audit
- Pairwise signed-error correlations, direction disagreement, origin-level absolute-error wins, direction-rescue counts and simple 50/50 pair proxies were computed from the 33 DEV origins.
- 2025 transport and 2026 stress remained completely outside selection authority.
- Strongest complementarity signal: Vanilla ANN + DE-ABC-ANN, error correlation 0.7703, 50/50 proxy DEV MAPE 2.08507%, direction 69.70%.
- DE-ABC is not promoted as a new Stage 3 parent because it is already a hybrid carried for ELM parity.

### Frozen Stage 3 entities

**Baseline anchor**
- Vanilla ANN

**Active evidence-driven parents — 5**
- MPA-ANN — primary price parent
- CPA-ANN — complementary price/search-diversity parent
- SCA-ANN — direction-specialist parent
- GA-ANN — year-stability parent
- TLBO-ANN — refinement/meta-tuning parent

**Hybrid-parity benchmarks — benchmark only**
- DE-ABC-ANN
- FA-FPA-ANN

**Reserve challengers**
- SSA-ANN — repeat/direction stability
- Krill Herd-ANN — diversity / RW win-rate
- ACO-ANN — balanced reserve
- HHO-ANN — yearly/repeat stability reserve

### Stage 3 frozen two-track plan

**Track 1 — mandatory ELM-parity refinements**
1. Adaptive PSO-ANN
2. TLBO-tuned PSO-ANN
3. DE-tuned PSO-ANN
4. Adaptive/Improved TLBO-ANN
5. Adaptive Crow Search-ANN
6. PSO-TLBO Hybrid ANN

Base PSO-ANN failed the Batch 2.1 RW gate; this must be disclosed when interpreting PSO-derived refinements.

**Track 2 — evidence-driven ANN-specific additions**
- Priority 1: MPA + SCA
- Priority 2: MPA + GA
- CPA-based alternative only if the first two fail to add DEV value.
- No combinatorial cross-product search.

### Stage status
- **AŞAMA 2/5: COMPLETE**
- Phase A models: 33/33 complete.
- Batch 2.1 filtering: 33 -> 12.
- Batch 2.2 active parent freeze: 5 active parents + Vanilla anchor + 2 fixed hybrid benchmarks + 4 reserves.
- Next: **AŞAMA 3/5 — Adaptive / Meta-on-Meta / Hybrid ANN**, beginning with the mandatory parity track in controlled batches.


## 16. ANN Stage 3 / Batch 3.1 — Adaptive PSO + Adaptive TLBO completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-ann-stage3-batch31-v1.yml`  
**Run:** 36132219383 — SUCCESS  
**Implementation:** `gold_axis_2026/tools/vw_midas_ann_stage3_batch31_v1.py`  
**Dedicated report:** `gold_axis_2026/GOLD_MONTHLY_ANN_STAGE3_BATCH31_ADAPTIVE_REFINEMENTS_2026-09-25.md`

### ANN-specific translation control
ELM ridge alpha was not copied mechanically into ANN. The ANN refinement tunes hidden width and weight decay because all ANN output weights are directly optimized rather than solved by an analytic ridge layer.

### Results
| Model | DEV MAPE % | DEV Direction % | 2025 MAPE % | 2026 MAPE % |
|---|---:|---:|---:|---:|
| Adaptive PSO-ANN | 2.26567 | 57.58 | 3.00291 | 4.69805 |
| Adaptive TLBO-ANN | 2.24090 | 54.55 | 2.64661 | 4.21136 |

### Decisions
- Adaptive PSO-ANN improves base PSO-ANN from 2.61194% to 2.26567% DEV MAPE (~13.26% relative reduction). It successfully rescues a base model that failed the Stage 2 RW gate, but it does not beat Vanilla or MPA.
- Adaptive TLBO-ANN improves base TLBO-ANN from 2.37828% to 2.24090% DEV MAPE (~5.78% relative reduction) and becomes the current third-best DEV MAPE ANN after Vanilla and MPA.
- Adaptive TLBO DEV RMSE 56.305 is effectively level with MPA-ANN 56.292.
- 2025/2026 remain reporting-only.

### Hyperparameter audit
Adaptive PSO DEV hidden selection: h3=17, h4=11, h6=5.  
Adaptive PSO weight decay: 0=12, 1e-4=9, 1e-3=12.

Adaptive TLBO DEV hidden selection: h3=8, h4=14, h6=11.  
Adaptive TLBO weight decay: 0=5, 1e-4=21, 1e-3=7.  
Adaptive TLBO median tuned controls: teach_gain=0.7791, learn_gain=0.9395, TF2 probability=0.4817, decay=1.7299.

### Stage status
- **AŞAMA 3/5 — Batch 3.1: COMPLETE**
- Next mandatory parity batch: **TLBO-tuned PSO-ANN + DE-tuned PSO-ANN**.


## 17. ANN Stage 3 / Batch 3.2 — TLBO-tuned PSO + DE-tuned PSO completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-ann-stage3-batch32-v1.yml`  
**Run:** 36132859342 — SUCCESS  
**Implementation:** `gold_axis_2026/tools/vw_midas_ann_stage3_batch32_v1.py`  
**Dedicated report:** `gold_axis_2026/GOLD_MONTHLY_ANN_STAGE3_BATCH32_TUNED_PSO_2026-09-25.md`

### Results
| Model | DEV MAPE % | DEV Direction % | 2025 MAPE % | 2026 MAPE % |
|---|---:|---:|---:|---:|
| TLBO-tuned PSO-ANN | 2.28920 | 69.70 | 2.82828 | 4.17474 |
| DE-tuned PSO-ANN | 2.30759 | 54.55 | 2.79166 | 4.73900 |

### Base-PSO improvement
- TLBO-tuned PSO-ANN reduces DEV MAPE from base PSO-ANN 2.61194% to 2.28920% (~12.36% relative reduction).
- DE-tuned PSO-ANN reduces DEV MAPE to 2.30759% (~11.65% relative reduction).
- Both therefore confirm that PSO internal parameters materially benefit from external tuning on this problem.

### Hyperparameter audit
TLBO-tuned PSO DEV medians:
- w=0.3364
- c1=1.2770
- c2=1.5465
- Vmax fraction=0.05
- h3 selected 24/33 origins
- weight decay 1e-4 selected 15/33

DE-tuned PSO DEV medians:
- w=0.4934
- c1=1.5489
- c2=1.8489
- Vmax fraction=0.05
- h4 selected 14/33
- weight decay 1e-3 selected 16/33

Boundary finding:
- Vmax lower bound 0.05 selected in 17/33 TLBO-tuned origins and 18/33 DE-tuned origins.
- DE also selects c2 upper bound in 10/33 origins.
- These are documented sensitivity signals, not silently treated as proof that the current bounds are optimal.

### Decisions
- **TLBO-tuned PSO-ANN:** retain as strong Stage 3 price+direction refinement; 69.70% DEV direction is especially notable.
- **DE-tuned PSO-ANN:** successful parity refinement but not a current leading candidate.
- 2025/2026 remain reporting-only and were not used for tuning or decision.
- **AŞAMA 3/5 — Batch 3.2: COMPLETE**
- Next mandatory parity batch: **Adaptive Crow Search-ANN + PSO-TLBO Hybrid ANN**.


## 18. ANN Stage 3 / Batch 3.3 — Adaptive Crow + PSO-TLBO Hybrid completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-ann-stage3-batch33-v1.yml`  
**Run:** 36133726760 — SUCCESS  
**Implementation:** `gold_axis_2026/tools/vw_midas_ann_stage3_batch33_v1.py`  
**Dedicated report:** `gold_axis_2026/GOLD_MONTHLY_ANN_STAGE3_BATCH33_CROW_PSO_TLBO_2026-09-25.md`

### Results
| Model | DEV MAPE % | DEV Direction % | 2025 MAPE % | 2026 MAPE % |
|---|---:|---:|---:|---:|
| Adaptive Crow Search-ANN | 2.49577 | 60.61 | 2.68521 | 4.54980 |
| PSO-TLBO Hybrid ANN | 2.34425 | 60.61 | 2.46744 | 4.42872 |

### Decisions
- Adaptive Crow Search improves base Crow Search-ANN from 2.50491% to 2.49577% DEV MAPE (~0.37% relative); improvement is real but too small for promotion.
- PSO-TLBO Hybrid improves base PSO-ANN by ~10.25% relative DEV MAPE and base TLBO-ANN by ~1.43%; retain as useful hybrid evidence, but it does not beat the leading Stage 3 refinements.
- Hybrid parameter audit shows no collapse to pure PSO or pure TLBO: median mix=0.5095 and median TLBO gain=0.9926.
- Adaptive Crow tuning also does not collapse to one default configuration.

### Mandatory parity-track status
All six pre-agreed ELM-parity ANN refinements are now complete:
1. Adaptive PSO-ANN
2. TLBO-tuned PSO-ANN
3. DE-tuned PSO-ANN
4. Adaptive/Improved TLBO-ANN
5. Adaptive Crow Search-ANN
6. PSO-TLBO Hybrid ANN

Current parity-track DEV MAPE ordering:
1. Adaptive TLBO-ANN — 2.24090%
2. Adaptive PSO-ANN — 2.26567%
3. TLBO-tuned PSO-ANN — 2.28920%
4. DE-tuned PSO-ANN — 2.30759%
5. PSO-TLBO Hybrid ANN — 2.34425%
6. Adaptive Crow Search-ANN — 2.49577%

### Stage status
- **AŞAMA 3/5 mandatory parity track: COMPLETE (6/6)**
- Next evidence-driven ANN-specific hybrid batch:
  - MPA + SCA
  - MPA + GA
- CPA-based alternative only if these fail to add DEV value.
- 2025/2026 remain reporting-only.


## 19. ANN Stage 3 / Batch 3.4 — Evidence-driven MPA hybrids completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-ann-stage3-batch34-v1.yml`  
**Run:** 36134549789 — SUCCESS  
**Implementation:** `gold_axis_2026/tools/vw_midas_ann_stage3_batch34_v1.py`  
**Dedicated report:** `gold_axis_2026/GOLD_MONTHLY_ANN_STAGE3_BATCH34_MPA_SCA_GA_HYBRIDS_2026-09-25.md`

### Results
| Model | DEV MAPE % | DEV Direction % | 2025 MAPE % | 2026 MAPE % |
|---|---:|---:|---:|---:|
| MPA+SCA Hybrid ANN | 2.23957 | 60.61 | 2.70259 | 4.52720 |
| MPA+GA Hybrid ANN | 2.48841 | 51.52 | 2.63731 | 4.71151 |

### Learned operator competition
**MPA+SCA selected-repeat mean survivor shares:** incumbent 44.78%, MPA 45.87%, SCA 9.35%.  
**MPA+GA selected-repeat mean survivor shares:** incumbent 24.53%, MPA 28.22%, GA 47.25%.

### Decisions
- MPA+SCA is a useful trade-off hybrid: it does not beat MPA on aggregate DEV MAPE (2.19947% -> 2.23957%) but improves MPA direction (57.58% -> 60.61%) and sharply improves yearly-MAPE stability (SD ~0.3698 -> 0.1470). Retain as balanced/stability evidence, not as price leader.
- MPA+GA is dominated by both parents on DEV MAPE and direction; reject from leading set.
- The Stage 2 fallback condition is therefore met for exactly one controlled CPA alternative: **MPA+CPA Hybrid ANN**.
- No further combinatorial hybrid expansion is permitted.
- 2025/2026 remain reporting-only.

### Stage status
- **AŞAMA 3/5 — Batch 3.4: COMPLETE**
- Next: **Batch 3.5 — MPA+CPA Hybrid ANN**, one-model controlled fallback.


## 20. ANN Stage 3 / Batch 3.5 — Final MPA+CPA fallback completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-ann-stage3-batch35-v1.yml`  
**Run:** 36135543119 — SUCCESS  
**Implementation:** `gold_axis_2026/tools/vw_midas_ann_stage3_batch35_v1.py`  
**Dedicated report:** `gold_axis_2026/GOLD_MONTHLY_ANN_STAGE3_BATCH35_MPA_CPA_FINAL_2026-09-25.md`

### Result
| Model | DEV MAPE % | DEV Direction % | 2025 MAPE % | 2026 MAPE % |
|---|---:|---:|---:|---:|
| MPA+CPA Hybrid ANN | 2.56713 | 57.58 | 2.48144 | 4.43815 |

### Learned operator survivor shares
Selected-repeat mean:
- CPA: 56.32%
- MPA: 23.02%
- incumbent: 20.66%

Refit mean:
- CPA: 57.83%
- MPA: 21.39%
- incumbent: 20.78%

### Decision
- MPA+CPA is dominated by both MPA and CPA on DEV MAPE and adds no direction benefit.
- DEV yearly-MAPE SD is ~0.37166, essentially no improvement over MPA's ~0.3698 stability weakness.
- Reject MPA+CPA from the leading set.
- No further MPA+X or other combinatorial ANN-specific optimizer hybrid search is permitted.

### Stage 3 final status
**AŞAMA 3/5: COMPLETE**

Mandatory ELM-parity refinements: 6/6 complete.

ANN-specific evidence-driven hybrids:
- MPA+SCA — retain as balance/stability evidence
- MPA+GA — reject
- MPA+CPA — reject

Important current DEV references:
- Vanilla ANN — 2.18895%
- MPA-ANN — 2.19947%
- MPA+SCA Hybrid — 2.23957%
- Adaptive TLBO-ANN — 2.24090%
- DE-ABC-ANN — 2.26109%
- Adaptive PSO-ANN — 2.26567%
- CPA-ANN — 2.27985%
- TLBO-tuned PSO-ANN — 2.28920% / direction 69.70%
- SCA-ANN — direction leader 72.73%

### Next
**AŞAMA 4/5 — ANN Ensemble**

Before implementation:
- recover exact ELM ensemble component set;
- recover exact ELM ensemble weight-learning protocol;
- preserve simple-average benchmark;
- optimized weights must be non-negative, sum to 1, and be learned using pre-2025 chronological evidence only;
- no fixed arbitrary weights except the simple-average benchmark.


## 21. ANN Stage 4 / Batch 4.1 — Ensemble baselines completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-ann-stage4-batch41-v1.yml`  
**Run:** 36136349942 — SUCCESS  
**Implementation:** `gold_axis_2026/tools/vw_midas_ann_stage4_batch41_v1.py`  
**Dedicated report:** `gold_axis_2026/GOLD_MONTHLY_ANN_STAGE4_BATCH41_ENSEMBLE_BASELINES_2026-09-25.md`

### ELM ensemble parity recovery
- Exact prediction-level ELM ensemble component set / learned weights / ensemble result: **NOT_FOUND** in the original ledger commit or current repo.
- No ELM ensemble details were invented.
- Stage 4 is therefore recorded as a new ANN ensemble stage, not exact ELM ensemble parity.

### Frozen 7-model component pool
- Vanilla ANN
- MPA-ANN
- SCA-ANN
- DE-ABC-ANN
- Adaptive TLBO-ANN
- TLBO-tuned PSO-ANN
- MPA+SCA Hybrid ANN

All component predictions were loaded directly from their original successful GitHub Actions artifacts; no base model was retrained.

### Honest DEV meta-evaluation
| Variant | DEV MAPE % | DEV Direction % | 2025 MAPE % | 2026 MAPE % |
|---|---:|---:|---:|---:|
| SIMPLE_AVERAGE | **2.10665** | **66.67** | 2.46790 | 4.35551 |
| PERFORMANCE_WEIGHTED | 2.11411 | 66.67 | 2.46539 | **4.35001** |
| OPTIMIZED_SIMPLEX | 2.33779 | 60.61 | **2.39450** | 4.40192 |

### Main findings
- Simple average is the strongest honest prequential DEV ensemble and improves on Vanilla ANN 2.18895% and MPA-ANN 2.19947%.
- Performance-weighted weights remain close to uniform; this supports diversified error averaging as the main source of gain.
- Unregularized optimized simplex shows clear meta-overfit:
  - full-DEV in-sample fit MAPE = 2.05363% (not valid as honest DEV evaluation);
  - expanding prequential DEV MAPE = 2.33779%.
- Final full-DEV optimized simplex weights collapse onto MPA+SCA 34.14%, Vanilla 25.13%, DE-ABC 21.10%, MPA 19.63%, with near-zero weight on SCA, Adaptive TLBO and TLBO-tuned PSO.
- 2025/2026 were not used for component selection, weighting or variant selection.

### Decisions
- **SIMPLE_AVERAGE: retain as current leading ANN ensemble benchmark.**
- **PERFORMANCE_WEIGHTED: retain as robust challenger.**
- **OPTIMIZED_SIMPLEX: do not promote in unregularized form.**
- Next Stage 4 batch should test only controlled remedies for weight overfit:
  - shrinkage/regularized simplex toward equal weights;
  - optionally one predeclared reduced role-diverse pool.
- No combinatorial subset search or arbitrary post-2025 weight fitting.

### Stage status
- **AŞAMA 4/5 — Batch 4.1: COMPLETE**
- Next: **Batch 4.2 — regularized/shrunk optimized ensemble robustness**.


## 22. ANN Stage 4 / Batch 4.2 — shrinkage and reduced-pool robustness completed 2026-09-25

**Initial run:** 36136794458 — technical failure (SLSQP iteration limit); no scientific result accepted.  
**Corrected run:** 36137025884 — SUCCESS / OUTPUT_GATE=PASS.  
**Implementation:** `gold_axis_2026/tools/vw_midas_ann_stage4_batch42_v1.py`  
**Dedicated report:** `gold_axis_2026/GOLD_MONTHLY_ANN_STAGE4_BATCH42_SHRINKAGE_ROBUSTNESS_2026-09-25.md`

### Numerical correction
- Nonsmooth MAPE simplex optimization was replaced by an exact LP formulation.
- Shrinkage is now explicit:
  `w_alpha = (1-alpha)*equal + alpha*w_optimized`.
- Fixed alpha grid: 0, 0.10, 0.25, 0.50, 0.75, 1.00.
- Alpha selection uses DEV-only expanding prequential MAPE.
- 2025/2026 remain outside all selection.

### FULL7 prequential shrinkage curve
- alpha 0.00 -> DEV MAPE **2.10665%**
- alpha 0.10 -> 2.12971%
- alpha 0.25 -> 2.16431%
- alpha 0.50 -> 2.22197%
- alpha 0.75 -> 2.27963%
- alpha 1.00 -> 2.33729%

**Chosen alpha = 0.00.**

### REDUCED4 prequential shrinkage curve
Pool: Vanilla + MPA + SCA + DE-ABC.
- alpha 0.00 -> DEV MAPE **2.12123%**, direction **72.73%**, RMSE **54.966**
- alpha 0.10 -> 2.13516%
- alpha 0.25 -> 2.15605%
- alpha 0.50 -> 2.19086%
- alpha 0.75 -> 2.22568%
- alpha 1.00 -> 2.26049%

**Chosen alpha = 0.00.**

### Decisions
- Both FULL7 and REDUCED4 reject optimized-weight contribution in favor of pure equal weighting.
- The monotonic deterioration away from alpha=0 is strong evidence that learned simplex weights are not supported by n=33 DEV meta-history.
- **FULL7 simple average remains the primary ANN ensemble candidate:** DEV MAPE 2.10665%, direction 66.67%.
- **REDUCED4 simple average remains a secondary directional/RMSE challenger:** DEV MAPE 2.12123%, direction 72.73%, RMSE 54.966.
- No further weight fine-tuning, arbitrary subset search, or generic stacking/meta-learner is scientifically justified after the optimized-simplex and shrinkage failures.
- 2025/2026 remain reporting-only.

### Stage status
- **AŞAMA 4/5 — Batch 4.2: COMPLETE**
- Stage 4 modeling search is effectively closed.
- If one final Stage 4 step is used, it should be robustness/freeze only, not a new ensemble family.
- Next major phase after freeze: **AŞAMA 5/5 — final ELM vs ANN comparison and family freeze**.


## 23. ANN Stage 4 — final robustness / freeze audit completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-ann-stage4-freeze-audit-v1.yml`  
**Run:** 36137558490 — SUCCESS / OUTPUT_GATE=PASS  
**Implementation:** `gold_axis_2026/tools/vw_midas_ann_stage4_freeze_audit_v1.py`  
**Dedicated report:** `gold_axis_2026/GOLD_MONTHLY_ANN_STAGE4_FINAL_FREEZE_AUDIT_2026-09-25.md`

### Year robustness
FULL7 DEV yearly MAPE:
- 2022: 2.19485%
- 2023: 1.89276%
- 2024: 2.25439%

REDUCED4 DEV yearly MAPE:
- 2022: 2.29902%
- 2023: 1.88397%
- 2024: 2.22516%

Both ensembles beat RW on relative MAE in each DEV year.

### Leave-one-origin sensitivity
FULL7:
- leave-one-origin MAPE range 1.96114%..2.17153%
- no single origin causes collapse.

REDUCED4:
- 1.97434%..2.18489%
- no single-origin collapse.

### Origin-level anchor comparison
FULL7 vs Vanilla:
- FULL7 lower APE in 17/33 origins, worse in 16/33.
- mean APE delta = -0.0823 percentage points.

FULL7 vs MPA:
- FULL7 lower APE in 17/33, worse in 16/33.
- mean APE delta = -0.0928 points.

Interpretation: aggregate gain is driven by error magnitude rather than overwhelming month-by-month win frequency.

### Leave-one-component diagnostic
Diagnostic only; not used to select a new subset.

Removing components from FULL7 yields:
- remove Vanilla -> MAPE 2.11284%
- remove MPA -> 2.11936%
- remove SCA -> **2.09504%**
- remove DE-ABC -> 2.13407%
- remove Adaptive TLBO -> 2.11877%
- remove TLBO-tuned PSO -> **2.08292%**
- remove MPA+SCA -> 2.12927%

This shows mild redundancy / negative MAPE contribution from SCA and TLBO-tuned PSO under the post-hoc removal diagnostic. These results are **not** used to promote a FULL6/FULL5 subset because that would reopen DEV subset search after the anti-overfit freeze.

### Final Stage 4 freeze
**PRIMARY:** FULL7 equal-weight ensemble
- DEV MAPE 2.10665%
- DEV direction 66.67%
- DEV RMSE 55.634

**SECONDARY CHALLENGER:** REDUCED4 equal-weight ensemble
- DEV MAPE 2.12123%
- DEV direction 72.73%
- DEV RMSE 54.966

Closed:
- learned performance weights as primary;
- optimized simplex;
- shrinkage simplex;
- generic stacking/meta-learner;
- arbitrary subset search;
- further optimizer-hybrid expansion.

### Stage status
**AŞAMA 4/5: COMPLETE AND FROZEN.**

Next: **AŞAMA 5/5 — final ELM vs ANN comparison and research-family freeze.**


## 24. FINAL — Stage 5/5 ELM vs ANN comparison and family freeze completed 2026-09-25

**Dedicated final report:** `gold_axis_2026/GOLD_MONTHLY_FINAL_ELM_VS_ANN_FAMILY_FREEZE_2026-09-25.md`

### Final comparison

**Baseline**
- Vanilla ELM DEV MAPE: 2.19286%
- Vanilla ANN DEV MAPE: 2.18895%
- Architecture-only improvement is negligible (~0.18% relative).

**Best single/metaheuristic**
- AOA-ELM: **2.15854%**
- MPA-ANN: 2.19947%
- ELM is stronger at the best-single level (~1.86% relative MAPE advantage).

**Best targeted refinement/hybrid**
- PSO-TLBO Hybrid ELM: **2.18548%**
- MPA+SCA Hybrid ANN: 2.23957%
- ELM is also stronger at the optimizer-hybrid level (~2.47% relative MAPE advantage).

**Final overall**
- AOA-ELM: 2.15854%
- FULL7 ANN equal ensemble: **2.10665%**
- REDUCED4 ANN equal ensemble: 2.12123%

FULL7 improves on the best DEV-selected ELM model by ~2.40% relative MAPE.

### External descriptive comparison against DEV-selected AOA-ELM
| Candidate | DEV MAPE % | 2025 MAPE % | 2026 MAPE % |
|---|---:|---:|---:|
| AOA-ELM | 2.15854 | 2.52849 | 5.13545 |
| FULL7 ANN | **2.10665** | **2.46790** | **4.35551** |
| REDUCED4 ANN | 2.12123 | 2.47331 | 4.46679 |

2025/2026 remain reporting-only and did not drive the freeze.

### Scientific interpretation
- ANN does **not** win because ANN is intrinsically superior: Vanilla ANN ≈ Vanilla ELM.
- Best ELM singles/refinements are stronger than the analogous ANN singles/refinements.
- ANN wins only after controlled role-diverse forecast aggregation.
- Therefore the final gain is attributed primarily to **ensemble diversification**, not architecture superiority.

### Frozen hierarchy
**PRIMARY:** FULL7 equal-weight ANN ensemble  
**SECONDARY:** REDUCED4 equal-weight ANN ensemble  
**ELM benchmark:** AOA-ELM  
**ELM refinement benchmark:** PSO-TLBO Hybrid ELM  
**ANN single benchmark:** MPA-ANN  
**ANN refinement references:** MPA+SCA, Adaptive TLBO, TLBO-tuned PSO, SCA direction specialist.

### Closed
Do not reopen without genuinely new unseen data or a new predeclared scientific hypothesis:
- ELM optimizer cross-products;
- ANN broad optimizer search;
- MPA+X hybrid enumeration;
- arbitrary ensemble subset search;
- optimized/shrunk ensemble weights;
- stacking/meta-learners;
- any post-hoc 2025/2026 model switching.

### Program status
- AŞAMA 1/5: COMPLETE
- AŞAMA 2/5: COMPLETE
- AŞAMA 3/5: COMPLETE
- AŞAMA 4/5: COMPLETE AND FROZEN
- **AŞAMA 5/5: COMPLETE AND FROZEN**

**Final primary model: FULL7 equal-weight ANN ensemble.**


## 25. ACTIVE EVALUATION CONTRACT — cumulative absolute error + direction

**Effective:** 2026-09-25  
**Status:** BINDING. This section supersedes the MAPE-centered selection/freeze interpretation in Section 24.

### 25.1 Forecast objective is unchanged
The scientific task remains:
- forecast next calendar month's average XAU/USD price at H=1;
- origin = previous completed month-end;
- frozen origin-safe VW-MIDAS data contract unless separately reopened by a new research decision.

**The target is NOT changed to return forecasting.**

### 25.2 Why the old evaluation is retired
The former Stage 5 freeze relied too heavily on average percentage price error (MAPE). That can make repeated monthly misses look acceptably small after averaging and does not jointly reward correct monthly direction.

Therefore:
- prior MAPE-centered ranking/freeze is retained only as historical research documentation;
- it is **no longer authoritative for model selection**;
- the former statement "FULL7 is the final primary model" is **UNFROZEN / UNDER RE-AUDIT**.

### 25.3 New binding primary metrics

For each evaluation window:

**Primary cumulative price-error metric**
`SUM_ABS_ERROR = Σ |forecast_t - actual_t|`

This is the cumulative absolute USD forecasting error across all months in the window.

**Primary direction metric**
`DIRECTION_ACCURACY = correct monthly direction forecasts / number of months`

Direction is evaluated from the forecasted next-month price relative to the prior observed monthly price versus the realized next-month direction.

### 25.4 Supporting metrics
- MAE = SUM_ABS_ERROR / n; valid as an average companion metric.
- MAPE, WAPE, RMSE, worst-month error and other metrics may still be reported diagnostically.
- MAPE is **not** the primary ranking authority.
- No arbitrary scalar score combining error and direction is allowed unless explicitly predeclared before looking at evaluation outcomes.
- Default comparison is a **two-objective Pareto / trade-off analysis**: lower cumulative absolute error AND higher direction accuracy.

### 25.5 Authority boundaries remain unchanged
- DEV: 2022-04..2024-12, n=33 — only model-selection/tuning authority.
- 2025: retrospective transport only.
- 2026 Jan-Jul: retrospective stress only.
- 2025/2026 may reveal robustness failures but cannot be used to retroactively tune or select a winner.
- No random split.
- No target-month leakage.
- DB remains READ_ONLY.

### 25.6 Re-audit findings under the new metrics

On DEV, the leading ensemble trade-off remains concentrated in:
- **FULL7 ANN:** cumulative absolute error **1428.86 USD**, direction **22/33 = 66.67%**.
- **REDUCED4 ANN:** cumulative absolute error **1431.46 USD**, direction **24/33 = 72.73%**.

Interpretation:
- FULL7 has only **2.60 USD** less cumulative error over 33 DEV months.
- REDUCED4 gets **2 additional monthly directions correct**.
- Therefore the prior claim that FULL7 is unambiguously the best model is withdrawn.
- Under the active two-objective contract, FULL7 and REDUCED4 form the principal DEV trade-off pair pending the next robustness stage.

Other important DEV references:
- MPA-ANN: cumulative absolute error **1471.53 USD**, direction **19/33 = 57.58%**.
- AOA-ELM: cumulative absolute error **1474.10 USD**, direction **20/33 = 60.61%**.
- Vanilla ELM: cumulative absolute error **1480.08 USD**, direction **21/33 = 63.64%**.
- MSVR predecessor: cumulative absolute error **1518.65 USD**, direction **21/33 = 63.64%**.

### 25.7 Retrospective 2025/2026 diagnostic — NOT selection authority
When all attempted families are inspected retrospectively on 2025 + 2026 Jan-Jul, three models illustrate the price-error / direction frontier:
- TLBO-ELM: total absolute error **2289.07 USD**, direction **14/19 = 73.68%**.
- MPA-ANN: total absolute error **2341.53 USD**, direction **16/19 = 84.21%**.
- HHO-ANN: total absolute error **2386.03 USD**, direction **17/19 = 89.47%**.

These three are **diagnostic retrospective profiles only**. They must not be promoted as final winners because 2025/2026 outcomes are already observed.

The key lesson is robustness instability across regimes: the model with the smallest DEV cumulative error is not necessarily the model with the best external price-error/direction balance.

## 26. NEXT STAGE — dual-objective robustness re-audit before any new model search

**Status:** NEXT.

No ANN/ELM family will be retrained yet.

### Stage 26 objective
Determine whether the existing model universe already contains a robust candidate under the new binding two-objective evaluation, using **DEV-only evidence**.

### Stage 26.1 — Full DEV re-ranking
For every completed model/family:
- compute cumulative absolute error on all 33 DEV origins;
- compute direction accuracy;
- compute yearly cumulative absolute error and direction for 2022, 2023 and 2024 separately;
- identify the DEV Pareto frontier;
- do not use 2025/2026 for ranking.

### Stage 26.2 — Stability / regime robustness
For each DEV Pareto candidate:
- inspect year-to-year cumulative-error dispersion;
- inspect direction stability by year;
- inspect worst monthly absolute error;
- inspect leave-one-origin sensitivity;
- identify whether a model's aggregate result is driven by a small number of unusually favorable months.

### Stage 26.3 — Candidate freeze under the corrected contract
A model can be frozen only if:
- it is Pareto-competitive on cumulative error + direction;
- it is not dependent on one DEV year/origin;
- its trade-off is explicit (price-error leader vs direction leader vs balanced candidate).

No arbitrary weighted score will be used to force a single winner.

### Stage 26.4 — External diagnostic only
After the DEV-only candidate set is frozen:
- report 2025 and 2026 Jan-Jul cumulative error and direction;
- characterize robustness degradation;
- do not switch winner based on those periods.

### Decision gate after Stage 26
Only after this re-audit:
- **If an existing model is robust:** keep it; do not rerun ANN/ELM.
- **If all existing candidates are unstable:** reopen modeling with the corrected objective/selection contract.
- Any reopened modeling must optimize/select with cumulative absolute error + direction considerations on pre-2025 chronological evidence only.



## 27. RESTORED MASTER MODEL-FAMILY CHECKLIST

**Effective:** 2026-09-25  
**Status:** BINDING MASTER ROADMAP.

### Why this section exists
The later 5-stage ANN checklist was a **sub-checklist for the ANN family**, not the complete project roadmap.  
Section 26's proposed robustness re-audit is useful as a diagnostic layer but **must not replace the previously agreed master model-family checklist**.

The project already completed ELM and ANN families, but the earlier roadmap contained additional model families that have not yet been executed.

### Restored master checklist

1. **ELM family**
   - Vanilla ELM
   - PSO-ELM
   - GA-ELM
   - MPA-ELM
   - broader single-metaheuristic ELM variants
   - targeted adaptive/meta-on-meta/hybrid ELM refinements
   - **STATUS: COMPLETE**

2. **ELMFIS**
   - baseline ELMFIS
   - **STATUS: NOT YET RUN**

3. **Optimized ELMFIS**
   - metaheuristic-optimized ELMFIS variants
   - **STATUS: NOT YET RUN**
   - optimizer expansion must be controlled; no blind combinatorial sweep.

4. **ANFIS**
   - baseline ANFIS
   - **STATUS: NOT YET RUN**

5. **Metaheuristic ANFIS**
   - PSO-ANFIS
   - GWO-ANFIS
   - HHO-ANFIS
   - **STATUS: NOT YET RUN**

6. **MLP / ANN family**
   - original roadmap examples included PSO/GA/WOA/HHO-MLP;
   - the project subsequently expanded this into the full ANN broad screen, refinements, hybrids and ensembles.
   - **STATUS: COMPLETE under the expanded ANN program**

7. **RBFNN family**
   - baseline RBFNN
   - planned controlled optimized/metaheuristic RBFNN variants
   - **STATUS: NOT YET RUN**

8. **Multi-output / GOR line**
   - multi-output / GOR
   - PSO-GOR-ELM
   - related controlled multi-output variants
   - **STATUS: NOT YET RUN**

9. **Metaheuristic SVR**
   - baseline/supporting SVR plus controlled metaheuristic optimization
   - **STATUS: NOT YET RUN**

### Active evaluation contract for all remaining families
The target remains next-month average XAU/USD price.  
Every new family must use the same governed chronological/origin-safe data contract unless explicitly changed.

Primary evaluation is now:
- cumulative absolute price error: `Σ|forecast - actual|`
- monthly direction accuracy

Supporting diagnostics:
- MAE
- MAPE/WAPE
- RMSE
- worst-month absolute error
- year-by-year stability

No arbitrary composite score is binding unless predeclared before results are inspected.

### Authority
- DEV 2022-04..2024-12 remains the only tuning/model-selection authority.
- 2025 and 2026 Jan-Jul remain retrospective transport/stress reporting only.
- No post-hoc switching based on 2025/2026.

### Correct next stage
Because ELM and ANN are already complete, the project resumes at the **first uncompleted family in the restored checklist**:

**NEXT: ELMFIS baseline.**

After baseline ELMFIS is verified under the common data/evaluation contract:
1. decide whether optimized ELMFIS is warranted;
2. then ANFIS;
3. then PSO/GWO/HHO-ANFIS;
4. then RBFNN;
5. then multi-output/GOR/PSO-GOR-ELM;
6. then metaheuristic SVR.

### Section 26 status
Section 26 is retained as a useful **diagnostic robustness audit**, but it is **not the project master next-stage roadmap** and must not block the remaining pre-agreed model families.


## 28. ELMFIS FULL PARITY PROGRAM — ACTIVE

**Dedicated checklist:** `gold_axis_2026/GOLD_MONTHLY_ELMFIS_FULL_PARITY_PLAN_2026-09-25.md`

ELMFIS is now treated as a complete model family, not a one-off baseline.

Binding order:
1. Stage 0 — canonical ELMFIS baseline / authority freeze.
2. Stage 1 — full **33-entry** ELM/ANN broad parity screen.
3. Stage 2 — DEV-only Pareto filtering using **cumulative absolute price error + direction**.
4. Stage 3A — six mandatory refinements:
   - Adaptive PSO
   - TLBO-tuned PSO
   - DE-tuned PSO
   - Adaptive TLBO
   - Adaptive Crow
   - PSO-TLBO Hybrid
5. Stage 3B — three ANN parity hybrids:
   - MPA+SCA
   - MPA+GA
   - MPA+CPA
6. Stage 3C — ELMFIS-specific **CQCSA-ELMFIS** authority candidate from published gold-price work.
7. Stage 4 — controlled ensemble / robustness.
8. Stage 5 — ELMFIS vs ELM vs ANN vs predecessor MSVR.

Stage-1 exact 33-entry set:
Vanilla, PSO, GA, MPA, DE, ABC, SSA, GWO, WOA, HHO, ACO, Bat, FA, MFO, FPA, FA-FPA, CS, SCA, Salp, SMA, GOA, ALO, TLBO, JAYA, HGS, ChOA, HGSO, AOA, CPA, Krill Herd, Crow Search/CSA, DE-ABC, Multi-swarm.

The target remains monthly H=1 average price. 2025/2026 remain reporting only. No MAPE-centered selection; active primary evaluation is cumulative absolute price error plus direction accuracy.

**NEXT EXECUTION:** Stage 0 canonical ELMFIS baseline.


## ELMFIS Stage 1 / Batch 1.1 — completed 2026-09-25

**Run:** 36169448338 — SUCCESS / OUTPUT_GATE=PASS  
**Report:** `gold_axis_2026/GOLD_MONTHLY_ELMFIS_STAGE1_BATCH11_REPORT_2026-09-25.md`

Frozen monthly H=1 contract and corrected evaluation authority were retained. Metaheuristics optimized only the 80 ELMFIS antecedent parameters (40 centers + 40 log-spreads); TSK consequents were solved analytically with ridge. DEV 2022-04..2024-12 remained the sole selection authority.

| Model | DEV sum abs error USD | DEV direction |
|---|---:|---:|
| DE-ELMFIS | **1665.4715** | **21/33 = 63.64%** |
| GA-ELMFIS | 1980.8994 | 14/33 = 42.42% |
| Vanilla ELMFIS | 1996.2933 | 20/33 = 60.61% |
| PSO-ELMFIS | 2358.4962 | 20/33 = 60.61% |

**Interpretation:** DE-ELMFIS is the provisional Batch-1.1 leader on both active DEV objectives and reduces Vanilla ELMFIS cumulative absolute error by about 330.82 USD while adding one correct direction month. No family winner or refinement parent is frozen; full Stage-1 broad screening remains mandatory.

**Progress:** ELMFIS Stage 1 = 4/33 complete.  
**Next after explicit user confirmation only:** MPA-ELMFIS + ABC-ELMFIS + SSA-ELMFIS + GWO-ELMFIS.


## ELMFIS Stage 1 / Batch 1.2 — completed 2026-09-25

**Workflow run:** 36170049225 — SUCCESS / OUTPUT_GATE=PASS  
**Report:** `gold_axis_2026/GOLD_MONTHLY_ELMFIS_STAGE1_BATCH12_REPORT_2026-09-25.md`

The frozen monthly H=1 target, governed 8-feature VW-MIDAS input contract, chronological validation, READ_ONLY database policy, and DEV-only selection authority were retained. MPA/ABC/SSA/GWO optimized only the 80 ELMFIS antecedent parameters; TSK consequents remained analytic ridge solutions.

DEV-only active-metric results:

| Model | Sum absolute error USD | Direction |
|---|---:|---:|
| ABC-ELMFIS | **1524.8854** | 21/33 = 63.64% |
| GWO-ELMFIS | 1943.5595 | **22/33 = 66.67%** |
| Vanilla ELMFIS | 1996.2933 | 20/33 = 60.61% |
| SSA-ELMFIS | 2124.4760 | 20/33 = 60.61% |
| MPA-ELMFIS | 3060.5864 | 19/33 = 57.58% |

**Interpretation:** ABC-ELMFIS becomes the provisional Stage-1 price-error leader among the first eight entries. GWO-ELMFIS supplies the current direction-side Pareto point. DE-ELMFIS is dominated by ABC at the same 21/33 direction count. No parent or final winner is frozen before the full 33-entry Stage-1 screen.

**Progress:** ELMFIS Stage 1 = 8/33 complete.  
**STOP GATE:** Stage 1.3 has not started.  
**Next after explicit user confirmation only:** WOA-ELMFIS + HHO-ELMFIS + ACO-ELMFIS + Bat-ELMFIS.


## ELMFIS Stage 1 / Batch 1.3 — completed 2026-09-25

**Workflow run:** 36170874292 — SUCCESS / OUTPUT_GATE=PASS  
**Report:** `gold_axis_2026/GOLD_MONTHLY_ELMFIS_STAGE1_BATCH13_REPORT_2026-09-25.md`

The frozen H=1 monthly target, governed 8-feature VW-MIDAS contract, chronological validation, READ_ONLY DB policy, and DEV-only selection authority were retained. WOA/HHO/ACO/Bat optimized only the 80 ELMFIS antecedent parameters; TSK consequents remained analytic ridge solutions.

DEV-only active-metric results:

| Model | Sum absolute error USD | Direction |
|---|---:|---:|
| HHO-ELMFIS | **1857.8942** | **22/33 = 66.67%** |
| ACO-ELMFIS | 1942.8695 | 19/33 = 57.58% |
| Vanilla ELMFIS | 1996.2933 | 20/33 = 60.61% |
| Bat-ELMFIS | 2137.8294 | 19/33 = 57.58% |
| WOA-ELMFIS | 2536.5468 | 15/33 = 45.45% |

**Interpretation:** HHO-ELMFIS becomes the current direction-side Pareto point and dominates the prior GWO point at the same 22/33 direction count with lower cumulative error. ABC-ELMFIS remains the current price-error side at 1524.8854 USD / 21/33. No parent or final winner is frozen before the full 33-entry Stage-1 screen.

**Progress:** ELMFIS Stage 1 = 12/33 complete.  
**STOP GATE:** Stage 1.4 has not started.  
**Next after explicit user confirmation only:** FA-ELMFIS + MFO-ELMFIS + FPA-ELMFIS + FA-FPA-ELMFIS.


## ELMFIS Stage 1 / Batch 1.4 — completed 2026-09-25

**Workflow run:** 36171748270 — SUCCESS / OUTPUT_GATE=PASS  
**Report:** `gold_axis_2026/GOLD_MONTHLY_ELMFIS_STAGE1_BATCH14_REPORT_2026-09-25.md`

The frozen monthly H=1 target, governed 8-feature VW-MIDAS input contract, chronological validation, READ_ONLY database policy, and DEV-only selection authority were retained. FA/MFO/FPA/FA-FPA optimized only the 80 ELMFIS antecedent parameters; TSK consequents remained analytic ridge solutions.

DEV-only active-metric results:

| Model | Sum absolute error USD | Direction |
|---|---:|---:|
| FA-FPA-ELMFIS | **1820.4499** | **25/33 = 75.76%** |
| Vanilla ELMFIS | 1996.2933 | 20/33 = 60.61% |
| MFO-ELMFIS | 2244.0539 | 19/33 = 57.58% |
| FPA-ELMFIS | 2251.8993 | 22/33 = 66.67% |
| FA-ELMFIS | 2421.4143 | 23/33 = 69.70% |

**Interpretation:** FA-FPA-ELMFIS becomes the current direction-side Pareto point and dominates the former HHO point on both active DEV objectives. ABC-ELMFIS remains the current price-error side at 1524.8854 USD / 21/33. No parent or final winner is frozen before the full 33-entry Stage-1 screen.

**Progress:** ELMFIS Stage 1 = 16/33 complete.  
**STOP GATE:** Stage 1.5 has not started.  
**Next after explicit user confirmation only:** CS-ELMFIS + SCA-ELMFIS + Salp-ELMFIS + SMA-ELMFIS.


## ELMFIS Stage 1 / Batch 1.5 — completed 2026-09-25

**Workflow run:** 36173141852 — SUCCESS / OUTPUT_GATE=PASS  
**Report:** `gold_axis_2026/GOLD_MONTHLY_ELMFIS_STAGE1_BATCH15_REPORT_2026-09-25.md`

The frozen H=1 monthly target, governed 8-feature VW-MIDAS contract, chronological validation, READ_ONLY database policy, and DEV-only selection authority were retained. CS/SCA/Salp/SMA optimized only the 80 ELMFIS antecedent parameters; TSK consequents remained analytic ridge solutions.

DEV-only active-metric results:

| Model | Sum absolute error USD | Direction |
|---|---:|---:|
| SMA-ELMFIS | **1651.4482** | **25/33 = 75.76%** |
| CS-ELMFIS | 1809.3931 | **25/33 = 75.76%** |
| Vanilla ELMFIS | 1996.2933 | 20/33 = 60.61% |
| Salp-ELMFIS | 2273.0187 | 19/33 = 57.58% |
| SCA-ELMFIS | 3177.3119 | 21/33 = 63.64% |

**Interpretation:** SMA-ELMFIS becomes the current direction/trade-off Pareto point and dominates both the former FA-FPA point and CS at the same 25/33 direction count with lower cumulative error. ABC-ELMFIS remains the current price-error side at 1524.8854 USD / 21/33. No parent or final winner is frozen before the full 33-entry Stage-1 screen.

**Progress:** ELMFIS Stage 1 = 20/33 complete.  
**STOP GATE:** Stage 1.6 has not started.  
**Next after explicit user confirmation only:** GOA-ELMFIS + ALO-ELMFIS + TLBO-ELMFIS + JAYA-ELMFIS.


## ELMFIS Stage 1 / Batch 1.6 — completed 2026-09-25

**Workflow run:** 36174033508 — SUCCESS / OUTPUT_GATE=PASS  
**Report:** `gold_axis_2026/GOLD_MONTHLY_ELMFIS_STAGE1_BATCH16_REPORT_2026-09-25.md`

The frozen H=1 monthly target, governed 8-feature VW-MIDAS contract, chronological validation, READ_ONLY database policy, and DEV-only selection authority were retained. GOA/ALO/TLBO/JAYA optimized only the 80 ELMFIS antecedent parameters; TSK consequents remained analytic ridge solutions.

DEV-only active-metric results:

| Model | Sum absolute error USD | Direction |
|---|---:|---:|
| JAYA-ELMFIS | **1810.4656** | **21/33 = 63.64%** |
| Vanilla ELMFIS | 1996.2933 | 20/33 = 60.61% |
| GOA-ELMFIS | 2322.7589 | 21/33 = 63.64% |
| ALO-ELMFIS | 2812.5033 | 18/33 = 54.55% |
| TLBO-ELMFIS | 3240.2851 | 20/33 = 60.61% |

**Interpretation:** JAYA-ELMFIS is the Batch-1.6 DEV leader but does not enter the current Pareto frontier because ABC-ELMFIS has the same 21/33 direction count with lower cumulative error. The provisional frontier remains ABC-ELMFIS (1524.8854 / 21/33) and SMA-ELMFIS (1651.4482 / 25/33). No parent or final winner is frozen before the full 33-entry Stage-1 screen.

**Progress:** ELMFIS Stage 1 = 24/33 complete.  
**STOP GATE:** Stage 1.7 has not started.  
**Next after explicit user confirmation only:** HGS-ELMFIS + ChOA-ELMFIS + HGSO-ELMFIS + AOA-ELMFIS.


## ELMFIS Stage 1 / Batch 1.7 — completed 2026-09-25

**Workflow run:** 36175116272 — SUCCESS / OUTPUT_GATE=PASS  
**Report:** `gold_axis_2026/GOLD_MONTHLY_ELMFIS_STAGE1_BATCH17_REPORT_2026-09-25.md`

The frozen H=1 monthly target, governed 8-feature VW-MIDAS contract, chronological validation, READ_ONLY database policy, and DEV-only selection authority were retained. HGS/ChOA/HGSO/AOA optimized only the 80 ELMFIS antecedent parameters; TSK consequents remained analytic ridge solutions.

DEV-only active-metric results:

| Model | Sum absolute error USD | Direction |
|---|---:|---:|
| HGSO-ELMFIS | **1594.6455** | 18/33 = 54.55% |
| HGS-ELMFIS | 1780.8620 | 20/33 = 60.61% |
| AOA-ELMFIS | 1873.9154 | **22/33 = 66.67%** |
| Vanilla ELMFIS | 1996.2933 | 20/33 = 60.61% |
| ChOA-ELMFIS | 2822.8921 | 20/33 = 60.61% |

**Interpretation:** HGSO is the Batch-1.7 price-error leader but does not enter the Pareto frontier because ABC-ELMFIS has both lower cumulative error and higher direction. AOA is dominated by SMA-ELMFIS. The provisional frontier therefore remains ABC-ELMFIS (1524.8854 / 21/33) and SMA-ELMFIS (1651.4482 / 25/33).

**Progress:** ELMFIS Stage 1 = 28/33 complete.  
**STOP GATE:** Stage 1.8 has not started.  
**Next after explicit user confirmation only:** CPA-ELMFIS + Krill Herd-ELMFIS + Crow Search-ELMFIS.


## ELMFIS Stage 1 / Batch 1.8 — completed 2026-09-25

**Workflow run:** 36175779813 — SUCCESS / OUTPUT_GATE=PASS  
**Report:** `gold_axis_2026/GOLD_MONTHLY_ELMFIS_STAGE1_BATCH18_REPORT_2026-09-25.md`

The frozen H=1 monthly target, governed 8-feature VW-MIDAS contract, chronological validation, READ_ONLY database policy, and DEV-only selection authority were retained. CPA/Krill Herd/Crow Search optimized only the 80 ELMFIS antecedent parameters; TSK consequents remained analytic ridge solutions.

DEV-only active-metric results:

| Model | Sum absolute error USD | Direction |
|---|---:|---:|
| Crow Search-ELMFIS | **1881.2292** | 20/33 = 60.61% |
| CPA-ELMFIS | 1925.0323 | 20/33 = 60.61% |
| Vanilla ELMFIS | 1996.2933 | 20/33 = 60.61% |
| Krill Herd-ELMFIS | 3043.2306 | 20/33 = 60.61% |

**Interpretation:** Crow Search is the Batch-1.8 DEV leader but does not enter the Pareto frontier. The provisional frontier remains ABC-ELMFIS (1524.8854 / 21/33) and SMA-ELMFIS (1651.4482 / 25/33).

**Progress:** ELMFIS Stage 1 = 31/33 complete.  
**STOP GATE:** Stage 1.9 has not started.  
**Next after explicit user confirmation only:** DE-ABC-ELMFIS + Multi-swarm-ELMFIS.


---

## 16. POST-ANFIS ROADMAP REVISION — CURRENT / BINDING (2026-09-26)

### 16.1 Why the roadmap is changed

The prior post-ANFIS sequence:
- RBFNN
- Multi-output / GOR / PSO-GOR-ELM
- Metaheuristic SVR

is now **SUPERSEDED as a mandatory execution order**.

Reason: completed ELM, ANN, ELMFIS and ANFIS experiments show that repeatedly changing only the optimizer often produces:
- small or inconsistent DEV gains;
- severe meta-overfit in learned weights;
- pathological forecasts in some adaptive/meta-on-meta variants;
- weak transport/stress stability despite apparently attractive in-sample or same-DEV results.

The next research phase must therefore prioritize **new model geometry / inductive bias** rather than blind metaheuristic enumeration.

### 16.2 Current reference hierarchy before the next families

Active DEV selection authority remains:
- DEV = 2022-04..2024-12, n=33.
- Primary criteria: cumulative absolute price error (ΣAE) + monthly direction accuracy.
- 2025 and 2026 remain reporting/stress only and must not influence model selection.

Current principal references:
- ChHHO-ANFIS — current price leader.
- REDUCED4 ANN — balanced price/direction challenger.
- SMA-ELMFIS — direction specialist.
- AOA-ELM — single-model ELM benchmark.

### 16.3 New governed roadmap

#### Phase N1 — Compact RBFNN benchmark
Purpose:
- test RBFNN as a genuinely different nonlinear basis model;
- avoid building a large optimizer program around it unless the baseline itself is competitive.

Required experiments:
1. Vanilla RBFNN.
2. Regularized RBFNN.
3. Chronology-safe center / spread / ridge tuning.
4. DEV-only comparison against current reference set.

Decision rule:
- if RBFNN is not competitive on DEV, close the family;
- do not launch large PSO/GA/DE/... RBFNN screens without a new scientific reason.

#### Phase N2 — Gaussian Process family — HIGH PRIORITY
Purpose:
- exploit strong small-sample regularization;
- add uncertainty-aware nonlinear modeling;
- exploit the four related metal outputs where possible.

Required experiments:
1. Single-output GPR benchmark.
2. Kernel comparison: ARD-RBF and Matérn at minimum.
3. 4-output / multi-output Gaussian Process using LMC/coregionalization if computationally feasible.
4. DEV-only hyperparameter selection.
5. Numerical/conditioning and uncertainty calibration diagnostics.

This is a priority family because it provides a new model geometry rather than another optimizer wrapper.

#### Phase N3 — Multi-task RFF-BLR
Purpose:
- test random Fourier feature nonlinear representation plus Bayesian shrinkage/sparsity;
- exploit the 4-output structure;
- target the small-sample multi-task setting directly.

Required experiments:
1. shared RFF feature map;
2. Bayesian linear multi-task output layer;
3. chronology-safe feature-scale/kernel-width selection;
4. sparsity/regularization diagnostics;
5. DEV-only comparison.

#### Phase N4 — Robust Multi-output ELM
Purpose:
- preserve the efficient ELM family while changing the loss/regularization geometry;
- address outlier sensitivity and multi-target coupling.

Required experiments:
1. GOR-ELM baseline.
2. If available and well-specified, improved/regularized GOR variant.
3. Only if the plain robust model is competitive, authorize one controlled tuner/refinement.
4. PSO-GOR-ELM is no longer automatic; it requires evidence from the untuned GOR result.

No broad metaheuristic GOR screen is authorized by default.

#### Phase N5 — Kernel Regression Block — replaces blind metaheuristic SVR
Required candidate set:
1. Kernel Ridge Regression (KRR).
2. RBF-SVR.
3. Least-Squares SVR / LS-SVM regression analogue where implementation is verified.
4. Twin SVR / Twin Support Vector Regression.
5. Kernel ELM / multi-task KELM where technically well-defined.

Governance:
- use one common chronology-safe hyperparameter protocol;
- prefer convex/regularized fitting and small controlled hyperparameter search;
- do not attach a separate metaheuristic optimizer to every kernel model by default.

#### Phase N6 — Tree Boosting challenger
Purpose:
- add a structurally different nonlinear partitioning family.

Candidate set:
1. HistGradientBoosting / regularized GBM.
2. LightGBM if implementation/dependencies are stable.
3. XGBoost if implementation/dependencies are stable.

Governance:
- shallow trees;
- strong regularization;
- compact, predeclared search;
- no broad optimizer-on-optimizer layer initially.

#### Phase N7 — Final cross-family tournament
Only after N1-N6 are completed or explicitly closed.

Minimum comparison set:
- ChHHO-ANFIS.
- REDUCED4 ANN.
- SMA-ELMFIS.
- best GP/MOGP.
- best RFF-BLR.
- best robust multi-output ELM.
- best kernel model.
- best boosting model.

Compare under:
- DEV ΣAE;
- DEV direction;
- MAE;
- RMSE;
- worst-month AE;
- year stability;
- relative MAE vs RW;
- leave-one-origin sensitivity where practical.

Then report 2025/2026 transport/stress without using them to alter the frozen DEV decision.

### 16.4 Explicitly parked / not automatically authorized

Do not automatically reopen:
- broad metaheuristic SVR screens;
- 20+ optimizer RBFNN screens;
- broad PSO/GA/DE/ABC/... GOR enumeration;
- new ANFIS optimizer crosses;
- new ensemble-weight optimization;
- generic stacking after the demonstrated small-sample meta-overfit;
- LSTM/GRU/Transformer as the next primary family.

These may be reopened only with a new, independently justified scientific hypothesis.

### 16.5 Binding next action

The next project action is:
**Phase N1 — Compact RBFNN benchmark**.

The new roadmap must be followed sequentially unless a phase is scientifically blocked or explicitly closed by the user.


### 16.6 N1.1 Vanilla RBFNN — completed 2026-09-26

Status: **COMPLETE / VALID BASELINE / NOT A LEADER**

Canonical specification:
- 8 Gaussian RBF centers;
- deterministic training-only k-means;
- per-cluster RMS width with singleton nearest-center fallback;
- 4-output OLS linear layer with intercept;
- no ridge;
- no metaheuristic;
- no hyperparameter search.

Execution:
- run 36255366631 — SUCCESS
- scientific gate PASS.

DEV:
- ΣAE 1666.0440
- direction 19/33 = 57.58%
- MAE 50.4862
- RMSE 62.1013
- relative MAE vs RW 0.94769.

Decision:
- RBFNN family remains open only for one compact regularized/tuned step.
- Next: N1.2 regularized RBFNN with a small predeclared center-count / width-scale / ridge grid selected chronologically.
- Broad optimizer screens remain unauthorized.


### 16.7 RBFNN roadmap extension — hybrid/refinement parity authorized 2026-09-26

User directive:
RBFNN must not stop at vanilla/regularized baselines. After the compact regularized RBFNN is established, execute a controlled hybrid/refinement package analogous to the successful scientific structure used for ELM/ANN/ANFIS.

This supersedes the earlier wording that RBFNN should be closed immediately after one compact regularized step if it is not a leader.

#### N1.2 — Regularized RBFNN baseline
Required before hybrids:
- compact center-count grid;
- compact global width-scale grid;
- ridge output regularization;
- chronological inner validation;
- no metaheuristic.

Purpose:
freeze a defensible regularized RBFNN reference and parameter bounds before optimizer-driven experiments.

#### N1.3 — RBFNN controlled hybrid/refinement parity track
Authorized methods:
1. Adaptive PSO-RBFNN.
2. TLBO-tuned PSO-RBFNN.
3. DE-tuned PSO-RBFNN.
4. Adaptive/Improved TLBO-RBFNN.
5. Adaptive Crow Search-RBFNN.
6. PSO-TLBO Hybrid RBFNN.

The optimizer may act only on scientifically meaningful RBFNN parameters:
- RBF centers and/or center perturbations;
- positive widths in log-space or bounded width multipliers;
- optional compact structural choice (center count) only if encoded with a predeclared discrete rule;
- ridge/regularization only within the frozen compact bounds.
The 4-output linear consequent layer should remain analytically solved whenever possible rather than being unnecessarily meta-optimized.

#### N1.4 — Evidence-driven RBFNN optimizer hybrids
Only after N1.3:
- identify parent optimizers using DEV only;
- allow at most a small, predeclared hybrid set motivated by observed complementarity;
- candidate parity mechanisms may include MPA+SCA, MPA+GA, MPA+CPA only if corresponding parent evidence exists;
- do not automatically enumerate all optimizer cross-products.

#### N1.5 — Literature-specific RBFNN hybrid challengers
Permitted if directly supported by literature and structurally distinct:
- PSO/adaptive-PSO RBFNN;
- GA+adaptive-PSO / evolutionary-architecture RBFNN;
- hard-ridge + DE/CS RBF-type forecasting;
- adaptive/self-learning TLBO-trained RBFNN.
These are literature-guided challengers, not permission for broad blind optimizer enumeration.

#### N1.6 — RBFNN family freeze
After hybrid/refinement completion:
- DEV Pareto on ΣAE + direction;
- year stability;
- scientific/numerical gate;
- optional ensemble only if component complementarity justifies it;
- 2025/2026 reporting only;
- freeze RBFNN family champion before proceeding to N2 Gaussian Processes.

Governance unchanged:
- DEV 2022-04..2024-12 only for selection;
- 2025/2026 excluded from selection;
- no random split;
- READ_ONLY DB;
- no target-month leakage.


### 16.8 RBFNN governed stage order — CURRENT / BINDING

The RBFNN family must now follow the same stage architecture used for ANN and ANFIS. This section supersedes any earlier ad-hoc RBFNN ordering.

#### STAGE 0 — Canonical baseline
- Vanilla RBFNN.
- Frozen 8-feature VW-MIDAS input contract.
- 4-output Gold/Silver/Platinum/Palladium return target; Gold price primary.
- Gaussian RBF hidden units.
- Training-only center estimation.
- Analytic linear output layer.
- No random split.
- No target-month leakage.
- Scientific/numerical gate.

Status:
- Vanilla RBFNN COMPLETE.
- Regularized RBFNN is retained as an additional Stage-0/benchmark refinement, not a substitute for Stage 1 broad screen.

#### STAGE 1 — Broad single-optimizer screen

Stage 1.1
- PSO-RBFNN
- GA-RBFNN
- DE-RBFNN

Stage 1.2
- MPA-RBFNN
- ABC-RBFNN
- SSA-RBFNN
- GWO-RBFNN

Stage 1.3
- WOA-RBFNN
- HHO-RBFNN
- ACO-RBFNN
- Bat-RBFNN

Stage 1.4
- FA-RBFNN
- MFO-RBFNN
- FPA-RBFNN
- FA-FPA-RBFNN

Stage 1.5
- CS-RBFNN
- SCA-RBFNN
- Salp-RBFNN
- SMA-RBFNN

Stage 1.6
- GOA-RBFNN
- ALO-RBFNN
- TLBO-RBFNN
- JAYA-RBFNN

Stage 1.7
- HGS-RBFNN
- ChOA-RBFNN
- HGSO-RBFNN
- AOA-RBFNN

Stage 1.8
- CPA-RBFNN
- Krill Herd-RBFNN
- Crow Search-RBFNN

Stage 1.9
- DE-ABC-RBFNN
- Multi-swarm RBFNN

Optimizer scope:
- RBF centers and/or center perturbations;
- positive widths in log-space or bounded multipliers;
- optional compact structural choice only under a predeclared discrete rule;
- ridge/regularization only within frozen compact bounds;
- 4-output linear output layer should remain analytically solved whenever possible.

No target-month data may enter optimizer fitness.

#### STAGE 2 — DEV filtering and parent freeze

Stage 2.1 — DEV filtering:
- RW gate;
- DEV ΣAE;
- direction;
- RMSE;
- year stability;
- worst month;
- numerical/scientific gate;
- redundancy prune.

Stage 2.2 — complementarity / parent freeze:
- signed-error correlations;
- direction disagreements;
- rescue/loss counts;
- price leader;
- direction leader;
- stability parent;
- hybrid/complementarity parent;
- freeze a small Stage-3 parent set.

2025/2026 remain excluded from all parent-selection decisions.

#### STAGE 3A — mandatory parity refinements

Run exactly the same mandatory refinement classes used in ANN/ANFIS:
1. Adaptive PSO-RBFNN.
2. Adaptive / Improved TLBO-RBFNN.
3. TLBO-tuned PSO-RBFNN.
4. DE-tuned PSO-RBFNN.
5. Adaptive Crow Search-RBFNN.
6. PSO-TLBO Hybrid RBFNN.

These six are parity experiments, not an invitation to enumerate arbitrary meta-on-meta crosses.

#### STAGE 3B — evidence-driven hybrids

After Stage 3A and only if parent evidence supports them:
- MPA + SCA RBFNN.
- MPA + GA RBFNN.
- MPA + CPA RBFNN if needed as the fallback hybrid.

Do not automatically enumerate all optimizer pairs.

#### STAGE 3C — literature-specific RBFNN hybrids

Search and test a small number of RBFNN-specific literature-backed hybrids that are structurally distinct from the parity set. Examples may include:
- adaptive/evolutionary PSO-RBFNN;
- GA + adaptive-PSO RBFNN;
- self-learning/adaptive TLBO-RBFNN;
- other center-width evolutionary RBF methods with clear methodological authority.

Literature-specific methods require:
- source;
- exact mechanism;
- parameterization;
- data requirements;
- clear distinction from already-tested parity methods.

#### STAGE 4 — ensemble / robustness / freeze

Stage 4.1 — ensemble pool freeze:
- vanilla anchor;
- price leader;
- direction leader;
- stability model;
- hybrid/refinement representative;
- FULL and REDUCED pools frozen before ensemble evaluation.

Stage 4.2 — baseline ensembles:
- simple average;
- median;
- expanding-prequential inverse-prior-MAE weighting.

Stage 4.3 — learned simplex weights:
- nonnegative;
- sum to 1;
- full-DEV fit diagnostic only;
- expanding-prequential DEV is the only honest selection evidence.

Stage 4.4 — shrinkage:
- alpha = 0.00, 0.10, 0.25, 0.50, 0.75, 1.00;
- FULL and REDUCED pools separately.

Stage 4.5 — final robustness/freeze:
- year-by-year;
- leave-one-origin;
- leave-one-component-out diagnostic;
- worst-month/tail stability;
- numerical stability;
- final RBFNN family roles.

#### STAGE 5 — cross-family comparison

Compare at minimum:
- ChHHO-ANFIS;
- REDUCED4 ANN;
- FULL7 ANN where relevant;
- SMA-ELMFIS;
- AOA-ELM;
- best RBFNN single model;
- best RBFNN hybrid/refinement;
- best RBFNN ensemble if any.

Use:
- DEV ΣAE;
- direction;
- MAE;
- RMSE;
- worst AE;
- relative MAE vs RW;
- year stability;
- leave-one-origin sensitivity where practical;
- global Pareto frontier.

2025/2026 remain reporting-only after the DEV decision is frozen.

#### Early Stage-3 artifact handling

Any Adaptive PSO-RBFNN / Adaptive TLBO-RBFNN runs launched before completion of Stage 1 and Stage 2 are classified as:
**EARLY / NON-BINDING STAGE-3 ARTIFACTS**.

They may be retained for implementation debugging and later reproducibility checks, but:
- must not be used for Stage-2 parent selection;
- must not be treated as final Stage-3 evidence unless rerun or formally revalidated after the Stage-2 parent freeze;
- must not alter Stage-1 ordering.

#### Historical binding next action — completed

This architecture-freeze instruction is superseded by the completed RBFNN Stage 0–5 entries below. Its first step was:
**RBFNN Stage 1.1 — PSO-RBFNN + GA-RBFNN + DE-RBFNN**.

Proceed sequentially through Stage 1 batches, then Stage 2, then Stage 3A/3B/3C, then Stage 4, then Stage 5.


### 16.9 RBFNN takeover audit and Stage-1 protocol freeze — 2026-09-26

Repository head verified at takeover: `41b55dac576c1d06e267b85158f9d3beb3c35e8e`.
Current GitHub run/job/artifact metadata and downloaded JSONs supersede conversational checkpoints.

| Baseline | Run | Job | Artifact | Commit | DEV ΣAE | Direction |
|---|---|---|---|---|---:|---:|
| Vanilla | 36255366631 | 108441010234 | 10910331925 | d9cc92142605c759a600a707b24943c56e3d27e0 | 1666.0440165140133 | 19/33 |
| Regularized | 36255648854 | 108441813323 | 10911110410 | b72d09a9d4197840ee1a5448973c5b4111176d87 | 1611.9847106804657 | 20/33 |

Baseline artifact copies: `gold_axis_2026/evidence/rbfnn_stage0/`.
Vanilla maximum DEV design condition 24.3670; Regularized 244.5479.
Existing baseline workflow/output gates passed. These historical gates did not explicitly enforce every requested collapse/conditioning test; full scientific-gate parity is NOT_PROVEN for Regularized cluster occupancy because its artifact lacks those diagnostics. This is a reporting limitation, not evidence requiring baseline rerun.

Early Adaptive PSO/TLBO run **36255801793**, job **108442235467**, artifact **10910572105**, commit `b0271eb15efa0afa0ac17b06f7b451bc221cfb83`: **EARLY / NON-BINDING STAGE-3 ARTIFACT**. Excluded from Stage-1 ranking and Stage-2 parent selection. No final Stage-3 evidence claimed.

#### Predeclared Stage-1 implementation (before any new DEV outcomes)

- Script: `gold_axis_2026/tools/vw_midas_rbfnn_stage1_v1.py`.
- Workflow: `.github/workflows/gold-monthly-rbfnn-stage1-v1.yml`.
- Batch sequence exactly 1.1–1.9 from section 16.8; maximum 4 independent jobs. Each batch depends on successful completion of its predecessor; implementation failures halt progression. Scientific rejection is recorded without disguising it as an implementation failure.
- Frozen geometry: 8 Gaussian radial bases, 8 inputs, 4 analytic outputs, intercept.
- Inner chronological last 20%, minimum 6 validation observations; minimum 30 inner training observations.
- Input/output scaling and deterministic 20-initialization k-means fitted only to inner training. Cluster RMS widths, singleton nearest-center fallback; initial empty clusters rejected.
- Width reference grid [0.5,1,1.5,2]; ridge [0,0.0001,0.001,0.01,0.1], selected on inner validation. No target-year aggregate selection.
- Meta-vector 72 parameters: 64 center perturbations in [-1,1] standardized units and 8 log-width multipliers in [log(.5),log(2)]. No output-weight meta-optimization.
- Population 24, generations 45, 3 deterministic repeats; date SHA256 seed plus recorded optimizer seed and repeat increment 1009.
- Exact repository optimizer implementations reused from `vw_midas_elmfis_meta_batch_{1..9}_v1.py` PHASE functions with RBF objective adapter; filenames/function names and source hashes recorded. These are repository parity implementations, not a claim of independently verified equivalence to every original paper.
- Fitness: .7 Gold standardized MAE + .3 four-output standardized MAE. Training drives evolution; validation selects only top-quartile training candidates and repeat.
- Refit: selected geometry AND inner-training scaler retained; analytic output layer fitted on all pre-target rows. No k-means regeneration or reassignment of learned center perturbations. Augmented least squares for ridge avoids normal-equation condition squaring.
- Candidate gate: finite parameters/beta, positive bounded widths, center separation >=1e-6, design condition <=1e10. Final forecasts finite for ALL four outputs and absolute predicted log-return <1. Initial cluster occupancy enforced; evolved nearest-region emptiness recorded diagnostically because learned bases need not remain a k-means partition.
- Fitness evaluation counts and repeat losses retained; equal generations do not imply equal evaluations for all optimizer algorithms.
- DEV decision/hash persisted BEFORE transport/stress evaluation. Full n=33 required; incomplete scientific results excluded, never ranked on a surviving subset. External scientific failures reported separately and cannot change DEV acceptance.
- DB loader and invariant reads READ_ONLY; unchanged authority invariants required.
- 2025/2026 reporting only; no parent selected before full Stage 1.

Status at protocol freeze: **STAGE 1 IMPLEMENTED / EXECUTION PENDING**. Stage 2–5 pending; no performance improvement claimed.


### 16.10 RBFNN Stage 1.1 — COMPLETE / AUDITED

Run **36256830372**, commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`.
Report: `GOLD_MONTHLY_RBFNN_STAGE1_REPORT_2026-09-26.md` (cumulative, no duplicated batch reports).

| Model | Job | Artifact | DEV ΣAE | DEV direction | 2025 ΣAE / direction | 2026 ΣAE / direction | Decision |
|---|---|---|---:|---:|---|---|---|
| PSO | 108445085805 | 10910357737 | 1598.5085 | 20/33 | 1031.3426 / 11/12 | 1475.5659 / 5/7 | SCIENTIFIC PASS; retain for Stage-2 comparison, no parent selected |
| GA | 108445085897 | 10910513816 | 1523.4710 | 19/33 | 989.9040 / 10/12 | 1560.4409 / 5/7 | SCIENTIFIC PASS; retain for Stage-2 comparison, no parent selected |
| DE | 108445085946 | 10911201564 | 1550.2583 | 18/33 | 1115.9977 / 9/12 | 1665.7461 / 4/7 | SCIENTIFIC PASS; retain for Stage-2 comparison, no parent selected |

GA is the batch price leader (1523.4710); PSO leads batch direction (20/33). None beats ChHHO-ANFIS 1413.0298 / 23/33. No scientific rejection in this batch. Three artifacts independently audited: complete 33/12/7 coverage, metric recomputation, DEV freeze hash, chronological diagnostics, four-output finite return checks and DB invariant equality. External results did not influence acceptance. Next: Stage 1.2 MPA/ABC/SSA/GWO; total completed 3/32.


### RBFNN Stage 1.2 — COMPLETE / AUDITED

Run **36256830372**, commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; shared frozen script/workflow/specification in §16.9.

| Model | Job | Artifact | DEV ΣAE | DEV direction | 2025 ΣAE / direction | 2026 ΣAE / direction | Gate / decision |
|---|---|---|---:|---:|---|---|---|
| MPA | 108445391910 | 10911490096 | 1510.5118 | 20/33 | 1103.2103 / 8/12 | 1490.3723 / 5/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |
| ABC | 108445391970 | 10911316182 | 1558.8168 | 18/33 | 1168.1027 / 8/12 | 1554.4114 / 5/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |
| SSA | 108445391918 | 10911116879 | 1559.8246 | 18/33 | 999.5913 / 9/12 | 1561.0808 / 5/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |
| GWO | 108445392044 | 10911365910 | 1511.6245 | 22/33 | 1203.3243 / 8/12 | 1661.8822 / 5/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |

Independent audit: coverage, recomputed metrics, freeze hash, chronology, numerical diagnostics and DB invariant equality. 2025/2026 reporting only. No Stage-2 parent selection yet. Next: Stage 1.3.


### RBFNN Stage 1.3 — COMPLETE / AUDITED

Run **36256830372**, commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; shared frozen script/workflow/specification in §16.9.

| Model | Job | Artifact | DEV ΣAE | DEV direction | 2025 ΣAE / direction | 2026 ΣAE / direction | Gate / decision |
|---|---|---|---:|---:|---|---|---|
| WOA | 108445827612 | 10910504177 | 1499.2639 | 19/33 | 1157.8414 / 10/12 | 1526.8745 / 5/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |
| HHO | 108445827611 | 10911193159 | 1586.1569 | 20/33 | 1109.8340 / 10/12 | 1404.7751 / 6/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |
| ACO | 108445827582 | 10910439350 | 1481.9468 | 19/33 | 1175.0249 / 9/12 | 1684.5221 / 5/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |
| BAT | 108445827586 | 10911445645 | 1501.6410 | 21/33 | 1037.0801 / 8/12 | 1526.1445 / 5/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |

Independent audit: coverage, recomputed metrics, freeze hash, chronology, numerical diagnostics and DB invariant equality. 2025/2026 reporting only. No Stage-2 parent selection yet. Next: Stage 1.4.


### RBFNN external-exclusion correction — DEV unchanged / external rows SUPERSEDED

Strict reading of the user contract requires no 2025/2026 observations in hyperparameter selection, including tuning at later external origins. Original Stage-1 per-origin tuning used available earlier external months. Although target-month chronology was preserved and external scores never selected a family/parent, **all original Stage-1 2025/2026 rows and the external columns in prior batch entries are SUPERSEDED** under this stricter constraint. DEV rows, rankings and decisions remain valid and unchanged.

Correction: `rbfnn_external_frozen_reporting_v1.py`, workflow `rbfnn-strict-external-v1.yml` freezes all optimizer/width/ridge/geometry/scaling choices using the 2024-12 origin only. At subsequent origins only the analytic output coefficients are refitted on available pre-target history; external observations never enter tuning. The copied DEV section must retain its identical SHA256. New external run/artifact lineage will be recorded separately; do not treat old external figures as final. No optimizer was rescued or chosen based on external performance.


### RBFNN Stage 1.4 — COMPLETE / AUDITED

Run **36256830372**, commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; shared frozen script/workflow/specification in §16.9.

| Model | Job | Artifact | DEV ΣAE | DEV direction | 2025 ΣAE / direction | 2026 ΣAE / direction | Gate / decision |
|---|---|---|---:|---:|---|---|---|
| FA | 108446196895 | 10911491233 | 1530.4171 | 20/33 | 1154.3285 / 8/12 | 1476.4276 / 4/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |
| MFO | 108446196851 | 10911102079 | 1449.1065 | 20/33 | 1145.3883 / 9/12 | 1590.1962 / 5/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |
| FPA | 108446196876 | 10910888723 | 1525.4420 | 21/33 | 1038.6675 / 11/12 | 1626.7086 / 6/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |
| FA_FPA | 108446197620 | 10911386249 | 1524.5325 | 20/33 | 1186.9763 / 8/12 | 1444.4187 / 5/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |

Independent audit: coverage, recomputed metrics, freeze hash, chronology, numerical diagnostics and DB invariant equality. 2025/2026 reporting only. No Stage-2 parent selection yet. Next: Stage 1.5.


### RBFNN Stage 1.5 — COMPLETE / AUDITED

Run **36256830372**, commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; shared frozen script/workflow/specification in §16.9.

| Model | Job | Artifact | DEV ΣAE | DEV direction | 2025 ΣAE / direction | 2026 ΣAE / direction | Gate / decision |
|---|---|---|---:|---:|---|---|---|
| CS | 108447551133 | 10910693139 | 1525.6645 | 20/33 | 1026.6605 / 10/12 | 1597.2074 / 5/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |
| SCA | 108447551125 | 10910383641 | 1541.6271 | 21/33 | 1070.8575 / 8/12 | 1668.9123 / 5/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |
| SALP | 108447551136 | 10911311967 | 1426.6878 | 23/33 | 1048.4474 / 10/12 | 1481.7930 / 6/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |
| SMA | 108447551196 | 10911516015 | 1568.1653 | 19/33 | 1061.1819 / 9/12 | 1741.0975 / 4/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |

Independent audit: coverage, recomputed metrics, freeze hash, chronology, numerical diagnostics and DB invariant equality. 2025/2026 reporting only. No Stage-2 parent selection yet. Next: Stage 1.6.


### RBFNN Stage 1.6 — COMPLETE / AUDITED

Run **36256830372**, commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; shared frozen script/workflow/specification in §16.9.

| Model | Job | Artifact | DEV ΣAE | DEV direction | 2025 ΣAE / direction | 2026 ΣAE / direction | Gate / decision |
|---|---|---|---:|---:|---|---|---|
| GOA | 108447881974 | 10911147860 | 1492.8771 | 20/33 | 1001.7465 / 10/12 | 1509.2009 / 5/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |
| ALO | 108447881981 | 10911590599 | 1597.3649 | 19/33 | 1125.6221 / 9/12 | 1695.0873 / 6/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |
| TLBO | 108447881998 | 10911427101 | 1525.7861 | 19/33 | 1219.1781 / 8/12 | 1849.1663 / 3/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |
| JAYA | 108447881948 | 10910813059 | 1460.7401 | 21/33 | 1189.3143 / 9/12 | 1703.0444 / 5/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |

Independent audit: coverage, recomputed metrics, freeze hash, chronology, numerical diagnostics and DB invariant equality. 2025/2026 reporting only. No Stage-2 parent selection yet. Next: Stage 1.7.


### RBFNN Stage 1.7 — COMPLETE / AUDITED

Run **36256830372**, commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; shared frozen script/workflow/specification in §16.9.

| Model | Job | Artifact | DEV ΣAE | DEV direction | 2025 ΣAE / direction | 2026 ΣAE / direction | Gate / decision |
|---|---|---|---:|---:|---|---|---|
| HGS | 108448226587 | 10911337750 | 1461.9334 | 20/33 | 1068.9775 / 9/12 | 1467.0408 / 5/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |
| CHOA | 108448226537 | 10910809960 | 1571.0927 | 20/33 | 1076.1496 / 10/12 | 1578.1525 / 5/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |
| HGSO | 108448226566 | 10911079556 | 1564.9802 | 20/33 | 1050.0976 / 9/12 | 1427.1983 / 6/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |
| AOA | 108448226604 | 10911427228 | 1501.0998 | 19/33 | 1112.8490 / 10/12 | 1157.9096 / 5/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |

Independent audit: coverage, recomputed metrics, freeze hash, chronology, numerical diagnostics and DB invariant equality. 2025/2026 reporting only. No Stage-2 parent selection yet. Next: Stage 1.8.


### RBFNN Stage 1.8 — COMPLETE / AUDITED

Run **36256830372**, commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; shared frozen script/workflow/specification in §16.9.

| Model | Job | Artifact | DEV ΣAE | DEV direction | 2025 ΣAE / direction | 2026 ΣAE / direction | Gate / decision |
|---|---|---|---:|---:|---|---|---|
| CPA | 108448532745 | 10911516667 | 1608.6437 | 17/33 | 1006.6045 / 10/12 | 1604.2304 / 5/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |
| KRILL | 108448532738 | 10911212904 | 1560.4829 | 17/33 | 1131.2027 / 11/12 | 2052.6335 / 4/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |
| CROW | 108448532720 | 10911875102 | 1538.2158 | 19/33 | 1080.5612 / 8/12 | 1486.2783 / 5/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |

Independent audit: coverage, recomputed metrics, freeze hash, chronology, numerical diagnostics and DB invariant equality. 2025/2026 reporting only. No Stage-2 parent selection yet. Next: Stage 1.9.


### RBFNN Stage 1.9 — COMPLETE / AUDITED

Run **36256830372**, commit `a09559f84075e53f0a38b408bcd6977c99b6e12c`; shared frozen script/workflow/specification in §16.9.

| Model | Job | Artifact | DEV ΣAE | DEV direction | 2025 ΣAE / direction | 2026 ΣAE / direction | Gate / decision |
|---|---|---|---:|---:|---|---|---|
| DE_ABC | 108448841547 | 10911447422 | 1415.8371 | 25/33 | 1145.3733 / 9/12 | 1932.7022 / 4/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |
| MULTISWARM | 108448841513 | 10911840511 | 1525.8563 | 21/33 | 997.9950 / 9/12 | 1550.5971 / 4/7 | PASS; ELIGIBLE_FOR_STAGE2_NOT_PARENT_SELECTED |

Independent audit: coverage, recomputed metrics, freeze hash, chronology, numerical diagnostics and DB invariant equality. 2025/2026 reporting only. No Stage-2 parent selection yet. Next: Stage 2 DEV filtering and parent freeze.


### RBFNN Stage 1 closure and Stage 2 freeze — COMPLETE

Stage 1: **32/32** complete, scientific gates PASS on DEV. Canonical corrected raw artifacts archived in `evidence/rbfnn_stage1/strict_results.json.gz`; original/strict run and job/artifact provenance in the adjacent JSONs. Strict external run **36257615727**, commit `540a138ba1d5f71ed1577be76196c9191f897bb6`. All 32 corrected artifacts preserve the exact original DEV hash. Original external columns remain SUPERSEDED; the cumulative Stage-1 report contains the authoritative corrected external metrics.

Stage-1 champion: **DE-ABC-RBFNN: DEV ΣAE 1415.8371, direction 25/33**, MAE 42.9042, RMSE 57.9188, relative MAE vs RW 0.80537, monthly wins 22/33. Against ChHHO reference 1413.0298 / 23/33: +2.8073 price loss, +2 correct directions. No claim of statistical superiority.

Stage 2 full audit/freeze: `GOLD_MONTHLY_RBFNN_STAGE2_FREEZE_2026-09-26.md` and companion JSON. Price/direction parent DE-ABC, stability parent Salp, architecture anchor Vanilla, conditional optimizer parent MPA. Stage-3 parent set frozen before any Stage-3 production run. No MPA+SCA/GA/CPA candidate clears the frozen complementarity opening rule. 2025/2026 excluded.

Next: Stage 3A mandatory parity, groups of two: Adaptive PSO + Adaptive TLBO; TLBO-tuned PSO + DE-tuned PSO; Adaptive Crow + PSO-TLBO. Implementation `tools/rbfnn_stage3a_v1.py`; workflow `.github/workflows/rbfnn-stage3a-v1.yml`. Reuses repository refinement mechanics with the frozen 72-parameter RBF interface; exact source hashes, learned outer parameters/bounds/trace are logged per origin. Final population 24, generations 45, repeats 3, analytic output refit, strict pre-2025 external tuning freeze. Technical synthetic interface checks passed for all six. No early N1.3 artifact is promoted or used as parent evidence.


### RBFNN Stage 3A.1 — COMPLETE / AUDITED

Run **36258593871**, commit `80acdfeb141b1daaa0eecf893b740143fcac6202`. Adaptive PSO: job 108449967744 / artifact 10911333701, DEV ΣAE 1519.3532 / 18 directions. Adaptive TLBO: job 108449967875 / artifact 10911686683, DEV ΣAE 1552.2502 / 21 directions. Both scientific PASS; neither improves DE-ABC 1415.8371 / 25. Retained as refinement benchmarks, not leaders. Corrected external metrics and lineage in `GOLD_MONTHLY_RBFNN_STAGE3_REPORT_2026-09-26.md`. Parent pool unchanged; 2025/2026 excluded; DB invariants equal. Next: TLBO-tuned PSO + DE-tuned PSO.


### RBFNN Stage 3A.2 — COMPLETE / AUDITED

Run **36258593871**, commit `80acdfeb141b1daaa0eecf893b740143fcac6202`. TLBO-tuned PSO: job 108450632348 / artifact 10911547589, DEV ΣAE 1610.0497 / 19 directions. DE-tuned PSO: job 108450632407 / artifact 10911677231, DEV ΣAE 1524.1595 / 20 directions. Both scientific PASS, dominated by DE-ABC 1415.8371 / 25 and retained as benchmarks. Full specification, bounds and corrected external metrics in Stage-3 report/artifacts. Frozen parents unchanged, DEV-only selection, 2025/2026 excluded, chronology PASS, DB READ_ONLY/invariants equal. Next: Adaptive Crow + PSO-TLBO.


### RBFNN Stage 3A closure / Stage 3B — COMPLETE

Run **36258593871**, commit `80acdfeb141b1daaa0eecf893b740143fcac6202`. Adaptive Crow: job 108451546851 / artifact 10911986536, DEV ΣAE 1455.8616 / 21 directions. PSO-TLBO: job 108451546834 / artifact 10911578130, DEV ΣAE 1489.6671 / 21 directions. Both scientific PASS. All **6/6** mandatory refinements audited; Adaptive Crow leads Stage 3A but is dominated by DE-ABC 1415.8371 / 25. Corrected external reports and full specifications/bounds are in Stage-3 report and compressed raw evidence.

Stage 3B **CLOSED_NOT_OPENED**: no MPA+SCA/GA/CPA clears the predeclared DEV correlation/rescue/price-win rule. No post-result parent edits. Next Stage 3C: **MOLS-RBFNN**, Chen/Grant/Cowan (1991), verified author-hosted primary full text; exact source, adaptations and structural distinction in Stage-3C authority. No generic optimizer relabeled as a new model.

Kontrol ve Uyum Özeti: DEV-only PASS; 2025/2026 exclusion PASS; random split NONE; chronology/leakage checks PASS; DB READ_ONLY/invariants equal; scientific gate PASS; run/job/artifact/commit manifest updated.


### RBFNN Stage 3C closure — COMPLETE

MOLS-RBFNN run **36259649017**, job **108452901591**, artifact **10911678043**, commit `f4561f8eea4c020e8c524910f4c43aff9a2fbb74`; script `tools/rbfnn_mols_literature_v1.py`, workflow `.github/workflows/rbfnn-stage3c-v1.yml`. DEV ΣAE **1578.5391**, direction **18/33**, scientific PASS; benchmark only, dominated by DE-ABC. External reports 2025 **1042.8290 / 8/12**, 2026 **1712.6412 / 4/7**, excluded from decisions. Exact source/method/parameter mapping in Stage-3C authority; raw artifacts archived with Stage-3 provenance. All Stage 3 work closed; Stage-3 leader Adaptive Crow, overall leader DE-ABC unchanged. Next: Stage-4 FULL/REDUCED pool freeze before computing any ensemble performance.

Kontrol ve Uyum Özeti: DEV-only PASS; 2025/2026 exclusion PASS; random split NONE; chronology/leakage checks PASS; DB READ_ONLY/invariants equal; scientific gate PASS; manifest updated.


### RBFNN Stage 4.1 — POOLS FROZEN BEFORE EVALUATION

FULL = Vanilla, DE-ABC, Salp, Adaptive Crow. REDUCED = Vanilla, DE-ABC. Roles: Vanilla anchor, DE-ABC price/direction, Salp worst-year RW-relative stability, Adaptive Crow refinement representative. Redundancy rule: remove unprotected dominated component when signed-error correlation >0.95. Salp/DE-ABC correlation 0.95757, Adaptive Crow/DE-ABC 0.97228. No ensemble outcomes were calculated before this freeze. Source DEV hashes recorded in `GOLD_MONTHLY_RBFNN_STAGE4_POOL_FREEZE_2026-09-26.json`.

Predeclared evaluation: simple average, median, inverse prior-MAE; simplex ΣAE minimization w>=0/sum=1; equal weights for first six DEV months; alpha [0,.1,.25,.5,.75,1] separately for both pools. Full-DEV simplex DIAGNOSTIC ONLY. External weights frozen at DEV end; no external loss updates. Canonical Vanilla retains fixed non-tuned origin-only k-means; Stage1/3 optimized geometries/tuning freeze 2024-12.

Stage-4/5 script and workflow: `tools/rbfnn_stage4_v1.py`, `tools/rbfnn_final_audit_v1.py`, `.github/workflows/rbfnn-stage4-final-v1.yml`. Technical future-forecast/label invariance and simplex fixture PASS. Next: compute honest prequential ensembles, then cross-family final audit.


### RBFNN Stage 4/5 — COMPLETE / FINAL FAMILY FREEZE

Run **36259902967**, job **108453610546**, artifact **10911484644**, commit **77083ec589ce6e8e9626cd20ae72ed4d95543913**. The commit froze FULL/REDUCED pools before any ensemble outcomes. Workflow `.github/workflows/rbfnn-stage4-final-v1.yml`; scripts `tools/rbfnn_stage4_v1.py`, `tools/rbfnn_final_audit_v1.py`; independent verification `tools/rbfnn_independent_final_verification.py`. All 18 ensemble variants evaluated on prequential DEV, plus reporting-only external periods.

- FULL Median leads ensembles: **ΣAE 1444.3008 / 22 directions**; BENCHMARK_NOT_PRIMARY.
- FULL shrinkage alpha **0.75**: **1449.3304 / 21**. REDUCED alpha **1.00**: **1450.6011 / 23**. Both selected only on prequential DEV.
- Full-DEV fitted FULL simplex **1402.2173** is **DIAGNOSTIC ONLY**. Honest prequential FULL simplex is **1450.5469 / 22**; no in-sample promotion.
- RBFNN primary / direction specialist / best hybrid: **DE-ABC**, **1415.8371 / 25**. Balanced challenger: **Salp**, **1426.6878 / 23**, benchmark role. Best mandatory refinement: Adaptive Crow **1455.8616 / 21**.
- ChHHO-ANFIS remains price leader **1413.0298 / 23**. DE-ABC adds two correct directions at +2.80735 cumulative price error. Distinct global Pareto: **ChHHO-ANFIS and DE-ABC-RBFNN**. Other-family references recomputed from their original monthly artifacts with run/job/artifact/commit provenance.
- DE-ABC external reports: 2025 **1145.3733 / 9 of 12**; 2026 Jan–Jul **1932.7022 / 4 of 7**. These never controlled selection. Historical family external protocols differ, so their displayed results are not a controlled external ranking.

Final report: `GOLD_MONTHLY_RBFNN_FINAL_FREEZE_2026-09-26.md` and artifact JSON. Stage-4 JSON retains all monthly forecasts, yearly metrics, fitted/prequential weights, shrinkage alternatives and leave-one-component-out diagnostics. Final verification JSON audits 41 specifications and 54 ensemble-period predictions/metrics, plus source hashes and numerical diagnostics. DE-ABC max DEV condition 312.8473; worst AE 155.5631; leave-one-origin comparison reverses the ChHHO price ranking in 15/33 omissions. Small n=33 and many comparisons do not establish statistical superiority. Independent full-prediction repeat robustness and historical Regularized occupancy proof remain **NOT_PROVEN**.

**KONTROL VE UYUM ÖZETİ:** DEV-only selection PASS; 2025 exclusion PASS; 2026 exclusion PASS; random split NONE; origin/target/future-label leakage checks PASS; DB READ_ONLY and unchanged invariants PASS; scientific gates PASS for all 39 new specifications; historical limitations explicitly NOT_PROVEN; manifest/ledger updated. The Stage-1 external-tuning correction remains explicit: superseded external values are not authoritative, DEV hashes unchanged.

RBFNN Stage 0–5 **COMPLETE/FROZEN**. No automatic expansion to another family. Next monthly roadmap action is governed **N2 Gaussian Processes**, outside this RBFNN task.


### N2 GPR — full parity architecture authorized / authority freeze — 2026-09-26

User explicitly authorized the same Stage0–5 architecture as RBFNN and continued sequential execution without repeated approvals. This supersedes a compact-only GPR interpretation. Binding method/source/parameter/checklist document: **GOLD_MONTHLY_GPR_AUTHORITY_AND_STAGE_PLAN_2026-09-26.md**. Same32 optimizers in batches1.1–1.9; Stage2 DEV parent freeze; six mandatory Stage3A refinements; evidence-gated MPA hybrids; 1–3 genuinely GP-specific literature candidates; frozen pools/prequential ensembles; cross-family final.

Verified authority: GPML chapters2/4/5; Bonilla/Chai/Williams2007 multitask GP; Álvarez/Rosasco/Lawrence2012 vector-valued kernel review. Main model is real four-output ICM, not four independent regressors. Canonical covariance B⊗K+D⊗I, B=LLᵀ, 22 bounded parameters, exact analytic posterior; training objective marginal likelihood (plus explicit parameter prior for MAP), chronological validation Gold-weighted MAE. Noise is distinguished from fixed numerical jitter. Exact parameterization/bounds, validation/refit, gates and external freeze are recorded before outcomes.

Stage0 methods: SO_RBF (explicit auxiliary single-output benchmark), VANILLA_ICM_RBF (joint canonical anchor), ICM_M32 (kernel comparison), REGULARIZED_ICM_RBF (lambda1 MAP prior). L-BFGS-B three deterministic starts; budget/convergence recorded. Stage1 retains common ICM-RBF MAP objective regardless of baseline performance.

Implementation: `tools/gpr_core_v1.py`, `tools/gpr_experiment_v1.py`; workflow `.github/workflows/gpr-stage0-v1.yml`. Dense Kronecker oracle verified mean/variance/NLL, condition upper bound and genuine cross-output transfer. All32 optimizer adapters passed synthetic interface checks. Next: Stage0 production and artifact audit, then Stage1.1. No GP performance result claimed yet.

Kontrol ve Uyum Özeti: DEV-only selection and 2025/2026 exclusion specified; no random split; origin-safe preprocessing/fitness/refit; READ_ONLY loader and invariant equality required; GP scientific gates explicit; ledger/protocol updated. External parameters/scaler freeze at 2024-12; only posterior conditioning expands. Authorization persists across checkpoints.


### GPR Stage 0 — COMPLETE / AUDITED

Run **36263297105**, commit **b28d63cb5dbf5d0f8290b20dfe8152b40a54623d**. Scientific gates PASS for all4; source-level dense oracle and production future-label invariance tests PASS. Full raw archive/provenance `evidence/gpr_stage0/`; report `GOLD_MONTHLY_GPR_STAGE0_REPORT_2026-09-26.md`.

| Model | Job | Artifact | DEV ΣAE / direction | 2025 ΣAE / direction | 2026 ΣAE / direction | Decision |
|---|---|---|---|---|---|---|
| SO_RBF | 108463083454 | 10913008323 | 1519.4443 / 19/33 | 1064.1439 / 10/12 | 1608.0868 / 4/7 | Auxiliary single-output benchmark only |
| VANILLA_ICM_RBF | 108463083386 | 10913335491 | 1726.6205 / 15/33 | 1175.6207 / 9/12 | 1561.4442 / 3/7 | Canonical anchor, not leader |
| ICM_M32 | 108463083203 | 10912764354 | 1640.0091 / 17/33 | 966.7238 / 9/12 | 1566.2865 / 5/7 | Best joint baseline, benchmark |
| REGULARIZED_ICM_RBF | 108463083413 | 10912109099 | 1842.2361 / 16/33 | 1086.4234 / 9/12 | 1548.0149 / 4/7 | Valid but weaker than RW, benchmark |

None improves ChHHO1413.0298/23 or DE-ABC-RBFNN1415.8371/25. No evidence that joint modeling is automatically superior. The already-frozen common Stage1 ICM-RBF MAP contract is unchanged; kernel/regularization are not switched in response to these outcomes. L-BFGS termination and interval coverage are recorded in raw diagnostics.

Next: Stage1.1 PSO/GA/DE, then batches1.2–1.9. Workflow `.github/workflows/gpr-stage1-v1.yml`, common runner `tools/gpr_experiment_v1.py`, population24/generations45/repeats3, lambda1 MAP objective, exact22 bounds in authority. All Stage1 batches share the same frozen protocol. No parents selected yet.

Kontrol ve Uyum Özeti: DEV-only PASS; 2025/2026 exclusion PASS; random split NONE; chronology/hash/invariant checks PASS; DB READ_ONLY; all GP scientific gates PASS; manifest and checkpoint updated.


### GPR Stage 1.1 — COMPLETE / AUDITED

Run **36263592441**, commit **b5885a50dfbc17474b8f22ac2e8b61f43b7b748d**. Shared script `tools/gpr_experiment_v1.py`, workflow `.github/workflows/gpr-stage1-v1.yml`; frozen22 bounds, population24/generations45/repeats3 and objective/refit in GPR authority.

| Method | Job | Artifact | DEV ΣAE / direction | 2025 ΣAE / direction | 2026 ΣAE / direction | Gate / decision |
|---|---|---|---|---|---|---|
| PSO | 108463902930 | 10912874314 | 1780.2169 / 19/33 | 1377.4255 / 8/12 | 1448.8102 / 4/7 | PASS; parent selection deferred |
| GA | 108463903324 | 10913173273 | 1723.5877 / 21/33 | 1232.3520 / 9/12 | 1675.1882 / 4/7 | PASS; parent selection deferred |
| DE | 108463902811 | 10912349208 | 1924.6270 / 21/33 | 1193.9617 / 9/12 | 1500.4802 / 5/7 | PASS; parent selection deferred |

Kontrol ve Uyum Özeti: DEV-only PASS; 2025/2026 excluded; random split NONE; origin/freeze-hash checks PASS; DB READ_ONLY/invariants equal; gate failures retained; manifest updated. Next: Stage1.2.


### GPR Stage 1.2 — COMPLETE / AUDITED

Run **36263592441**, commit **b5885a50dfbc17474b8f22ac2e8b61f43b7b748d**. Shared script `tools/gpr_experiment_v1.py`, workflow `.github/workflows/gpr-stage1-v1.yml`; frozen22 bounds, population24/generations45/repeats3 and objective/refit in GPR authority.

| Method | Job | Artifact | DEV ΣAE / direction | 2025 ΣAE / direction | 2026 ΣAE / direction | Gate / decision |
|---|---|---|---|---|---|---|
| MPA | 108464326830 | 10913356064 | 1701.5802 / 23/33 | 1310.8517 / 10/12 | 1627.5845 / 4/7 | PASS; parent selection deferred |
| ABC | 108464327155 | 10912909413 | 1672.2945 / 22/33 | 1270.7420 / 9/12 | 1733.8828 / 3/7 | PASS; parent selection deferred |
| SSA | 108464326883 | 10913208515 | 1798.1173 / 21/33 | 1073.4934 / 9/12 | 1822.8569 / 4/7 | PASS; parent selection deferred |
| GWO | 108464326989 | 10913365971 | 1650.2596 / 21/33 | 1309.3998 / 7/12 | 1714.9181 / 3/7 | PASS; parent selection deferred |

Kontrol ve Uyum Özeti: DEV-only PASS; 2025/2026 excluded; random split NONE; origin/freeze-hash checks PASS; DB READ_ONLY/invariants equal; gate failures retained; manifest updated. Next: Stage1.3.


### GPR Stage 1.3 — COMPLETE / AUDITED

Run **36263592441**, commit **b5885a50dfbc17474b8f22ac2e8b61f43b7b748d**. Shared script `tools/gpr_experiment_v1.py`, workflow `.github/workflows/gpr-stage1-v1.yml`; frozen22 bounds, population24/generations45/repeats3 and objective/refit in GPR authority.

| Method | Job | Artifact | DEV ΣAE / direction | 2025 ΣAE / direction | 2026 ΣAE / direction | Gate / decision |
|---|---|---|---|---|---|---|
| WOA | 108464925053 | 10913094229 | 1836.8353 / 21/33 | 1074.8662 / 9/12 | 1598.3084 / 5/7 | PASS; parent selection deferred |
| HHO | 108464925071 | 10913411163 | 1823.3648 / 21/33 | 1058.8792 / 10/12 | 1571.7864 / 5/7 | PASS; parent selection deferred |
| ACO | 108464925116 | 10912159858 | 1815.8271 / 19/33 | 1240.0333 / 8/12 | 1785.4657 / 4/7 | PASS; parent selection deferred |
| BAT | 108464925085 | 10913795139 | 1746.6720 / 21/33 | 1144.6360 / 10/12 | 1797.0547 / 4/7 | PASS; parent selection deferred |

Kontrol ve Uyum Özeti: DEV-only PASS; 2025/2026 excluded; random split NONE; origin/freeze-hash checks PASS; DB READ_ONLY/invariants equal; gate failures retained; manifest updated. Next: Stage1.4.


### GPR Stage1 technical score-domain verification — REQUIRED BEFORE STAGE2

Source review identified ABC/ALO/DE-ABC roulette quality `1/(1+loss)`. GP NLL is not universally positive, so interface equivalence must not be assumed solely from synthetic independent outputs. Existing fitted baseline NLLs are positive, but that does not prove every metaheuristic candidate. A technical replay of these three methods records every training score without changing scores, seeds, algorithms or candidate identity. Require strictly positive observed scores and exact original DEV hash/prediction equality before Stage2 freeze. This is an implementation-domain verification, not outcome-driven tuning or an extra candidate. Script `tools/gpr_score_domain_audit_v1.py`; workflow `.github/workflows/gpr-score-domain-audit-v1.yml`. Any failure blocks Stage2 and requires explicit implementation correction/lineage. Main Stage1 batches continue unchanged.


### GPR score-domain technical replay — positivity PASS / original matching in progress

Run **36264658833**, commit **356015a4d03988342bdbb575681ed4a830ef6bc1**. ABC job108466913684/artifact10912689533: 111521 finite training calls, minimum1.1495314. ALO job108466913788/artifact10913337530: 115056 calls, minimum1.1479349. DE-ABC job108466913693/artifact10913840808: 224753 calls, minimum1.1534185. No nonfinite training calls. Thus roulette loss-domain assumption is valid for every observed evaluation in these frozen experiments; no score transform/algorithm change is needed.

ABC replay DEV hash exactly matches the original Stage1 artifact. ALO and DE-ABC original batch results are not yet available; final matching remains **WAITING_FOR_ORIGINALS**, and Stage2 is blocked until all3 match. Replay outputs are technical evidence only and excluded from candidate counts/parent selection. Archive `evidence/gpr_score_domain/results.json.gz`, verification `GOLD_MONTHLY_GPR_SCORE_DOMAIN_AUDIT_2026-09-26.json`; finalize script performs exact hash matching. This domain proof is dataset-specific, not a universal positivity claim about GP NLL.


### GPR Stage 1.4 — COMPLETE / AUDITED

Run **36263592441**, commit **b5885a50dfbc17474b8f22ac2e8b61f43b7b748d**. Shared script `tools/gpr_experiment_v1.py`, workflow `.github/workflows/gpr-stage1-v1.yml`; frozen22 bounds, population24/generations45/repeats3 and objective/refit in GPR authority.

| Method | Job | Artifact | DEV ΣAE / direction | 2025 ΣAE / direction | 2026 ΣAE / direction | Gate / decision |
|---|---|---|---|---|---|---|
| FA | 108465649928 | 10913387613 | 1861.6613 / 19/33 | 1159.5279 / 9/12 | 1648.0344 / 4/7 | PASS; parent selection deferred |
| MFO | 108465650026 | 10913425627 | 1702.0152 / 19/33 | 1327.6499 / 8/12 | 1718.7822 / 4/7 | PASS; parent selection deferred |
| FPA | 108465649974 | 10913039667 | 1711.7090 / 20/33 | 1213.2619 / 8/12 | 1634.7762 / 4/7 | PASS; parent selection deferred |
| FA_FPA | 108465649964 | 10913277531 | 1724.6532 / 25/33 | 1264.0104 / 9/12 | 1711.5714 / 3/7 | PASS; parent selection deferred |

Kontrol ve Uyum Özeti: DEV-only PASS; 2025/2026 excluded; random split NONE; origin/freeze-hash checks PASS; DB READ_ONLY/invariants equal; gate failures retained; manifest updated. Next: Stage1.5.


### GPR Stage 1.5 — COMPLETE / AUDITED

Run **36263592441**, commit **b5885a50dfbc17474b8f22ac2e8b61f43b7b748d**. Shared script `tools/gpr_experiment_v1.py`, workflow `.github/workflows/gpr-stage1-v1.yml`; frozen22 bounds, population24/generations45/repeats3 and objective/refit in GPR authority.

| Method | Job | Artifact | DEV ΣAE / direction | 2025 ΣAE / direction | 2026 ΣAE / direction | Gate / decision |
|---|---|---|---|---|---|---|
| CS | 108467841107 | 10913716533 | 1835.2043 / 22/33 | 1342.7277 / 10/12 | 1698.3633 / 3/7 | PASS; parent selection deferred |
| SCA | 108467841117 | 10913686573 | 1713.8379 / 23/33 | 1020.1019 / 9/12 | 1602.2326 / 4/7 | PASS; parent selection deferred |
| SALP | 108467841122 | 10913816298 | 1841.6043 / 20/33 | 1281.1444 / 10/12 | 1726.2159 / 3/7 | PASS; parent selection deferred |
| SMA | 108467841086 | 10914185898 | 1701.0740 / 22/33 | 1123.6182 / 9/12 | 1650.1670 / 4/7 | PASS; parent selection deferred |

Kontrol ve Uyum Özeti: DEV-only PASS; 2025/2026 excluded; random split NONE; origin/freeze-hash checks PASS; DB READ_ONLY/invariants equal; gate failures retained; manifest updated. Next: Stage1.6.


### GPR Stage 1.6 — COMPLETE / AUDITED

Run **36263592441**, commit **b5885a50dfbc17474b8f22ac2e8b61f43b7b748d**. Shared script `tools/gpr_experiment_v1.py`, workflow `.github/workflows/gpr-stage1-v1.yml`; frozen22 bounds, population24/generations45/repeats3 and objective/refit in GPR authority.

| Method | Job | Artifact | DEV ΣAE / direction | 2025 ΣAE / direction | 2026 ΣAE / direction | Gate / decision |
|---|---|---|---|---|---|---|
| GOA | 108468283985 | 10913288541 | 1850.3608 / 22/33 | 1345.6494 / 9/12 | 1748.7540 / 3/7 | PASS; parent selection deferred |
| ALO | 108468283980 | 10914116270 | 1704.0561 / 21/33 | 1127.1573 / 9/12 | 1617.5643 / 4/7 | PASS; parent selection deferred |
| TLBO | 108468284010 | 10913656152 | 1736.5717 / 19/33 | 1229.3699 / 10/12 | 1817.4760 / 3/7 | PASS; parent selection deferred |
| JAYA | 108468284040 | 10914065648 | 1760.9248 / 22/33 | 1364.4745 / 7/12 | 1814.9369 / 3/7 | PASS; parent selection deferred |

Kontrol ve Uyum Özeti: DEV-only PASS; 2025/2026 excluded; random split NONE; origin/freeze-hash checks PASS; DB READ_ONLY/invariants equal; gate failures retained; manifest updated. Next: Stage1.7.


### GPR Stage 1.7 — COMPLETE / AUDITED

Run **36263592441**, commit **b5885a50dfbc17474b8f22ac2e8b61f43b7b748d**. Shared script `tools/gpr_experiment_v1.py`, workflow `.github/workflows/gpr-stage1-v1.yml`; frozen22 bounds, population24/generations45/repeats3 and objective/refit in GPR authority.

| Method | Job | Artifact | DEV ΣAE / direction | 2025 ΣAE / direction | 2026 ΣAE / direction | Gate / decision |
|---|---|---|---|---|---|---|
| HGS | 108468774112 | 10913941795 | 1814.9260 / 20/33 | 1165.3952 / 9/12 | 1718.6267 / 4/7 | PASS; parent selection deferred |
| CHOA | 108468774107 | 10914291094 | 1822.1087 / 17/33 | 1124.4099 / 10/12 | 1746.6646 / 4/7 | PASS; parent selection deferred |
| HGSO | 108468774044 | 10913466849 | 1677.9024 / 19/33 | 1243.9984 / 10/12 | 1704.9450 / 4/7 | PASS; parent selection deferred |
| AOA | 108468774129 | 10913482813 | 1611.8839 / 22/33 | 1089.9437 / 8/12 | 1492.7431 / 5/7 | PASS; parent selection deferred |

Kontrol ve Uyum Özeti: DEV-only PASS; 2025/2026 excluded; random split NONE; origin/freeze-hash checks PASS; DB READ_ONLY/invariants equal; gate failures retained; manifest updated. Next: Stage1.8.


### GPR Stage 1.8 — COMPLETE / AUDITED

Run **36263592441**, commit **b5885a50dfbc17474b8f22ac2e8b61f43b7b748d**. Shared script `tools/gpr_experiment_v1.py`, workflow `.github/workflows/gpr-stage1-v1.yml`; frozen22 bounds, population24/generations45/repeats3 and objective/refit in GPR authority.

| Method | Job | Artifact | DEV ΣAE / direction | 2025 ΣAE / direction | 2026 ΣAE / direction | Gate / decision |
|---|---|---|---|---|---|---|
| CPA | 108469283872 | 10914186822 | 1778.4226 / 22/33 | 1174.2591 / 8/12 | 1856.1890 / 3/7 | PASS; parent selection deferred |
| KRILL | 108469283903 | 10913299086 | 1769.3329 / 22/33 | 1285.7184 / 9/12 | 1856.1225 / 3/7 | PASS; parent selection deferred |
| CROW | 108469283941 | 10914450763 | 1736.9995 / 22/33 | 1237.0919 / 9/12 | 1777.8806 / 2/7 | PASS; parent selection deferred |

Kontrol ve Uyum Özeti: DEV-only PASS; 2025/2026 excluded; random split NONE; origin/freeze-hash checks PASS; DB READ_ONLY/invariants equal; gate failures retained; manifest updated. Next: Stage1.9.


### GPR technical replay audit amendment — floating-point identity

ALO original and replay have identical discrete decisions, selected repeats, source hashes and call counts, but non-bitwise floating-point arithmetic: maximum price difference DEV4.55e-13, 2025 9.09e-13, 2026 1.82e-12. Exact serialized DEV hash equality therefore failed despite numerical equivalence. The original exact-hash requirement above is superseded transparently: compare every numeric value in DEV/2025/2026 recursively with rtol=1e-10/atol=1e-10, every discrete field exactly; compare actual theta arrays rather than their raw-byte hashes. Original/replay hashes and bitwise status remain separately recorded. This does not change scores, models, seeds, selections or original results. ABC is bitwise identical; ALO passes strict numerical comparison; DE-ABC original pending. Stage2 remains blocked until all3 pass. This is an implementation audit amendment, not a scientific model gate relaxation.


### GPR Stage 1.9 — COMPLETE / AUDITED

Run **36263592441**, commit **b5885a50dfbc17474b8f22ac2e8b61f43b7b748d**. Shared script `tools/gpr_experiment_v1.py`, workflow `.github/workflows/gpr-stage1-v1.yml`; frozen22 bounds, population24/generations45/repeats3 and objective/refit in GPR authority.

| Method | Job | Artifact | DEV ΣAE / direction | 2025 ΣAE / direction | 2026 ΣAE / direction | Gate / decision |
|---|---|---|---|---|---|---|
| DE_ABC | 108469745401 | 10913986440 | 1709.2591 / 23/33 | 1280.3824 / 9/12 | 1762.8199 / 3/7 | PASS; parent selection deferred |
| MULTISWARM | 108469745367 | 10914071210 | 1606.7414 / 23/33 | 1204.7296 / 8/12 | 1677.0049 / 4/7 | PASS; parent selection deferred |

Kontrol ve Uyum Özeti: DEV-only PASS; 2025/2026 excluded; random split NONE; origin/freeze-hash checks PASS; DB READ_ONLY/invariants equal; gate failures retained; manifest updated. Next: Stage2 DEV filtering and parent freeze.


### GPR Stage 1 closure and Stage2 parent freeze — COMPLETE

All32 original Stage1 artifacts are audited; no scientific failures. Technical score-domain verification PASS for ABC/ALO/DE-ABC with original/replay bitwise status and strict numerical comparison separately recorded. Stage1 price leader MULTISWARM: DEV ΣAE1606.741381, direction23/33; direction leader FA_FPA:1724.653242,25/33. No external results used.

Frozen roles: {"architecture_anchor": "VANILLA_ICM_RBF", "direction_leader": "FA_FPA", "optimizer_hybrid_parent": "MPA", "price_leader": "MULTISWARM", "stability_parent": "ICM_M32"}. Pairwise correlations, bidirectional direction rescue, monthly price wins, yearly/leave-one-origin summaries and validation-repeat dispersion in `GOLD_MONTHLY_GPR_STAGE2_FREEZE_2026-09-26.json`. Independent prediction-repeat robustness NOT_PROVEN. Eligible conditional pair MPA+SCA signed-error correlation0.875656578, below predeclared0.90; remaining rescue/win gates also PASS. Stage3B opens only after six Stage3A refinements close. Full freeze is committed before production Stage3A.

Kontrol ve Uyum Özeti: all32 closure PASS; DEV-only filtering PASS; SO_RBF excluded from four-output parents; 2025/2026 excluded; no random split; DB READ_ONLY; no survivor selection before broad screen closure. Next: Stage3A six refinements, batches<=2.


### GPR Stage3A — RUNNING after immutable parent freeze

Parent freeze commit24be35eb14e9d5b1d8cfab7593bd42fc241541bd precedes activation commit47480bf7dc77d5e86437ace1f11bce7490baefe5; run36266015124. Three sequential batches of two refinements. Canonical GP prior initialization is retained; frozen parent roles govern comparison/conditional hybrid admission and do not imply unimplemented theta transfer.


### GPR Stage 3A — ADAPTIVE_PSO / AUDITED

Run 36266015124; job 108470702244; artifact 10913299773; execution commit `47480bf7dc77d5e86437ace1f11bce7490baefe5`. Full per-origin parameters, optimizer bounds/source hashes, termination, exact posterior diagnostics and repeat selection remain in raw archive.

| Period | ΣAE | Direction | Gate |
|---|---:|---:|---|
| dev | 1794.2201 | 20/33 | PASS |
| transport_2025 | 1195.8734 | 9/12 | PASS |
| stress_2026 | 1594.1298 | 5/7 | PASS |

Decision: DEV-only candidate; final role awaits all Stage3 methods. External results reporting only.

Kontrol ve Uyum Özeti: chronology, DEV hash, strict external theta freeze, positive uncertainty and numerical gates PASS for accepted rows; DB READ_ONLY/invariants equal; no random split; incomplete scientific periods not ranked.


### GPR reporting clarification — strict RBFNN external reference

The RBFNN DE_ABC comparison uses `strict_results.json.gz`, whose external_lineage records tuning_last2024-12 and expanding analytic output refit only (run36257615727, commit540a138ba1d5f71ed1577be76196c9191f897bb6). GPR uses the same no-external-hyperparameter-learning cutoff. Earlier blanket protocol-difference wording is narrowed to the older pre-RBF family references. External performance remains reporting only for all families; no selection changes.


### GPR implementation documentation clarification — validation snapshots

Stage1/3B repository mechanisms retain the best chronological validation candidate among top-training-quartile snapshots across generations, not only the last generation. Stage3A validates final training winners plus stated outer q tuning. Frozen code and results unchanged; different validation opportunities/objective call counts explicitly documented in authority and Turkish method report. All target/future and external exclusion gates remain unchanged.


### GPR Stage 3A — ADAPTIVE_TLBO / AUDITED

Run 36266015124; job 108470702038; artifact 10914585546; execution commit `47480bf7dc77d5e86437ace1f11bce7490baefe5`. Full per-origin parameters, optimizer bounds/source hashes, termination, exact posterior diagnostics and repeat selection remain in raw archive.

| Period | ΣAE | Direction | Gate |
|---|---:|---:|---|
| dev | 1740.8877 | 19/33 | PASS |
| transport_2025 | 1171.3549 | 8/12 | PASS |
| stress_2026 | 1599.9542 | 4/7 | PASS |

Decision: DEV-only candidate; final role awaits all Stage3 methods. External results reporting only.

Kontrol ve Uyum Özeti: chronology, DEV hash, strict external theta freeze, positive uncertainty and numerical gates PASS for accepted rows; DB READ_ONLY/invariants equal; no random split; incomplete scientific periods not ranked.


### GPR Stage 3A — DE_TUNED_PSO / AUDITED

Run 36266015124; job 108473163896; artifact 10914288153; execution commit `47480bf7dc77d5e86437ace1f11bce7490baefe5`. Full per-origin parameters, optimizer bounds/source hashes, termination, exact posterior diagnostics and repeat selection remain in raw archive.

| Period | ΣAE | Direction | Gate |
|---|---:|---:|---|
| dev | 1939.8588 | 16/33 | PASS |
| transport_2025 | 1165.2957 | 9/12 | PASS |
| stress_2026 | 1620.3487 | 4/7 | PASS |

Decision: DEV-only candidate; final role awaits all Stage3 methods. External results reporting only.

Kontrol ve Uyum Özeti: chronology, DEV hash, strict external theta freeze, positive uncertainty and numerical gates PASS for accepted rows; DB READ_ONLY/invariants equal; no random split; incomplete scientific periods not ranked.


### GPR Stage 3A — TLBO_TUNED_PSO / AUDITED

Run 36266015124; job 108473163912; artifact 10914384584; execution commit `47480bf7dc77d5e86437ace1f11bce7490baefe5`. Full per-origin parameters, optimizer bounds/source hashes, termination, exact posterior diagnostics and repeat selection remain in raw archive.

| Period | ΣAE | Direction | Gate |
|---|---:|---:|---|
| dev | 1863.6677 | 19/33 | PASS |
| transport_2025 | 1400.8577 | 9/12 | PASS |
| stress_2026 | 1894.1223 | 3/7 | PASS |

Decision: DEV-only candidate; final role awaits all Stage3 methods. External results reporting only.

Kontrol ve Uyum Özeti: chronology, DEV hash, strict external theta freeze, positive uncertainty and numerical gates PASS for accepted rows; DB READ_ONLY/invariants equal; no random split; incomplete scientific periods not ranked.


### GPR Stage 3A — PSO_TLBO / AUDITED

Run 36266015124; job 108475710588; artifact 10914825981; execution commit `47480bf7dc77d5e86437ace1f11bce7490baefe5`. Full per-origin parameters, optimizer bounds/source hashes, termination, exact posterior diagnostics and repeat selection remain in raw archive.

| Period | ΣAE | Direction | Gate |
|---|---:|---:|---|
| dev | 1815.3287 | 21/33 | PASS |
| transport_2025 | 1240.6596 | 9/12 | PASS |
| stress_2026 | 1564.8887 | 5/7 | PASS |

Decision: DEV-only candidate; final role awaits all Stage3 methods. External results reporting only.

Kontrol ve Uyum Özeti: chronology, DEV hash, strict external theta freeze, positive uncertainty and numerical gates PASS for accepted rows; DB READ_ONLY/invariants equal; no random split; incomplete scientific periods not ranked.


### Final reporting identity rule — frozen before ensembles

Numerically identical DEV prediction paths (absolute tolerance1e-8 USD, same target months) are aliases, not independent challengers. Cross-family Pareto output deduplicates aliases while recording their mapping; balanced-challenger role excludes aliases of the primary. This prevents e.g. simple-average and alpha0 names from being presented as two independent models. No scores or candidate predictions are changed.


### GPR Stage 3A — ADAPTIVE_CROW / AUDITED

Run 36266015124; job 108475710574; artifact 10914557870; execution commit `47480bf7dc77d5e86437ace1f11bce7490baefe5`. Full per-origin parameters, optimizer bounds/source hashes, termination, exact posterior diagnostics and repeat selection remain in raw archive.

| Period | ΣAE | Direction | Gate |
|---|---:|---:|---|
| dev | 1724.2888 | 19/33 | PASS |
| transport_2025 | 1223.9506 | 9/12 | PASS |
| stress_2026 | 1613.7839 | 4/7 | PASS |

Decision: DEV-only candidate; final role awaits all Stage3 methods. External results reporting only.

Kontrol ve Uyum Özeti: chronology, DEV hash, strict external theta freeze, positive uncertainty and numerical gates PASS for accepted rows; DB READ_ONLY/invariants equal; no random split; incomplete scientific periods not ranked.


### GPR Stage3A closure — COMPLETE / 6 of6 audited

Run36266015124, execution commit47480bf7dc77d5e86437ace1f11bce7490baefe5; all six jobs succeeded and all DEV/external gates PASS. Lowest refinement DEV ΣAE ADAPTIVE_CROW1724.288839, direction19/33. None beats Stage1 MULTISWARM1606.741381/23. Exact monthly evidence and all job/artifact IDs in evidence/gpr_stage3 and Stage3 report. Closure file checks all6 and original parent-freeze hashes.

Kontrol ve Uyum Özeti: DEV-only PASS; chronological inner tuning and external hyperparameter freeze PASS; DB READ_ONLY/invariants equal; no target/future use; no score-driven rescue. Next: admitted MPA_SCA only, after this closure commit.


### GPR Stage3B MPA_SCA — RUNNING

Run36268484542, activation commit0bee31b199a419059bbab9570e3e07e1d27d7af7 follows Stage3A closure commit111899e4ed9e2a55ebe5a94a7a62b4ecf0ecd0a1. Single eligible pair from Stage2; same22-dimensional ICM objective, pop24, generations45, repeats3. Incumbent/MPA/SCA proposals compete by training NLL; chronological top-quartile validation retention and survivor shares recorded. No new pair selected from external results.


### GPR Stage 3B — MPA_SCA / AUDITED

Run 36268484542; job 108477773189; artifact 10914109472; execution commit `0bee31b199a419059bbab9570e3e07e1d27d7af7`. Full per-origin parameters, optimizer bounds/source hashes, termination, exact posterior diagnostics and repeat selection remain in raw archive.

| Period | ΣAE | Direction | Gate |
|---|---:|---:|---|
| dev | 1709.2943 | 22/33 | PASS |
| transport_2025 | 1211.6084 | 10/12 | PASS |
| stress_2026 | 1749.1495 | 4/7 | PASS |

Decision: DEV-only candidate; final role awaits all Stage3 methods. External results reporting only.

Kontrol ve Uyum Özeti: chronology, DEV hash, strict external theta freeze, positive uncertainty and numerical gates PASS for accepted rows; DB READ_ONLY/invariants equal; no random split; incomplete scientific periods not ranked.


### GPR Stage3AB closure — COMPLETE / AUDITED

MPA_SCA run36268484542, job108477773189, artifact10914109472, commit0bee31b199a419059bbab9570e3e07e1d27d7af7: DEV ΣAE1709.294302,22/33. All52 monthly scientific gates PASS. No Stage1 leader improvement. All6 mandatory methods plus admitted hybrid are now closed. `GOLD_MONTHLY_GPR_STAGE3AB_CLOSURE_2026-09-26.json` checks Stage3A closure, exact parent hashes, and hybrid opening evidence.

Kontrol ve Uyum Özeti: DEV-only PASS; external tuning exclusion PASS; READ_ONLY/invariant equality PASS; no random split; full provenance retained. Next: primary-source verification and pre-outcome authority freeze for one genuine GP-specific LMC candidate.


### GPR Stage3C LMC2_RBF_M32 — AUTHORITY FROZEN / RUNNING

Primary sources rechecked after Stage3AB: Alvarez/Rosasco/Lawrence2012 sections4.2 and6.2, equations10/19–21/31–33; GPML2006 section5.4.1 equations5.8/5.9. One structural LMC candidate, two distinct ARD kernels and full-rank task matrices,40 parameters, exact dense posterior and analytic likelihood gradient. Full bounds/prior/seeds/budget/gates in `GOLD_MONTHLY_GPR_STAGE3C_AUTHORITY_2026-09-26.md`. Synthetic independent covariance, all40 finite-difference derivative checks and future-label invariance PASS; rechecked by workflow.

Authority commitf38cfaa13604f7284c3de13b785d3b663729d910 precedes activation commit3168be9cfc74ff3e6cbbc1ef76fb0c588422fe01; run36269000173. No production outcome used to choose this specification. Next: audit LMC, closeStage3, commit pools before ensemble outcomes.


### GPR Stage 3C — LMC2_RBF_M32 / AUDITED

Run 36269000173; job 108479223144; artifact 10915270480; execution commit `3168be9cfc74ff3e6cbbc1ef76fb0c588422fe01`. Full per-origin parameters, optimizer bounds/source hashes, termination, exact posterior diagnostics and repeat selection remain in raw archive.

| Period | ΣAE | Direction | Gate |
|---|---:|---:|---|
| dev | 1424.1711 | 19/33 | PASS |
| transport_2025 | 1022.6730 | 10/12 | PASS |
| stress_2026 | 1625.2864 | 5/7 | PASS |

Decision: DEV-only candidate; final role awaits all Stage3 methods. External results reporting only.

Kontrol ve Uyum Özeti: chronology, DEV hash, strict external theta freeze, positive uncertainty and numerical gates PASS for accepted rows; DB READ_ONLY/invariants equal; no random split; incomplete scientific periods not ranked.


### GPR Stage3C / all Stage3 closure — COMPLETE

LMC2_RBF_M32 run36269000173, job108479223144, artifact10915270480, commit3168be9cfc74ff3e6cbbc1ef76fb0c588422fe01. DEV ΣAE1424.171081,19/33;2025 ΣAE1022.673030,10/12;2026 ΣAE1625.286417,5/7. All scientific/chronology/freeze gates PASS. LMC is the new four-output price and worst-year-relative stability leader; FA_FPA remains direction leader. RBFNN reference1415.837129/25 still dominates LMC on DEV point estimates. No new kernel/prior variant opened after this outcome.

Kontrol ve Uyum Özeti: Stage3A6 + admittedStage3B1 + genuineStage3C1 all COMPLETE/AUDITED; source/closure hashes match; READ_ONLY invariants equal; no external selection. `GOLD_MONTHLY_GPR_STAGE3_CLOSURE_2026-09-26.json` is terminal Stage3 evidence.

### GPR Stage4 pool freeze — BEFORE ANY ENSEMBLE OUTCOMES

FULL roles: Vanilla ICM architecture, LMC2 price/stability, FA_FPA direction, MPA_SCA mandatory-refinement/hybrid representative. Deduplicated FULL=[VANILLA_ICM_RBF,LMC2_RBF_M32,FA_FPA,MPA_SCA]. No unprotected component satisfies the predefined domination/correlation removal rule within this pool, so REDUCED is the same4 models. This is a valid no-removal outcome, not an omitted reduced-pool stage. Both names will be evaluated; their identical configurations are not independent experiments. No pool changed after ensemble outcomes.

Pool hashes, fixed alpha grid0/.1/.25/.5/.75/1, minimum history6 and frozen external-weight rule in `GOLD_MONTHLY_GPR_STAGE4_POOL_FREEZE_2026-09-26.json`. Next: commit this freeze, activate ensemble/final workflow.


## 17. NEW MODEL DISCOVERY POLICY — GOLD-SPECIFIC AUTHORITY FIRST

Status: BINDING after GPR family closure.

The project will no longer advance automatically through a preselected generic sequence such as RFF-BLR -> GOR-ELM -> generic SVR. New model families must first pass a gold-forecasting authority screen.

### 17.1 Selection criteria

A new family is prioritized using four dimensions:

1. Gold-specific out-of-sample forecasting evidence.
2. Reported superiority versus meaningful benchmarks, preferably with statistical comparison where available.
3. Literature maturity / citation evidence, interpreted with publication age.
4. Compatibility with this project's governed setting:
   - H=1 next-calendar-month average XAU/USD;
   - small DEV sample;
   - origin-safe expanding/rolling evaluation;
   - frozen 8-feature VW-MIDAS contract unless an approved extension is explicitly opened;
   - joint Gold/Silver/Platinum/Palladium structure where method supports it;
   - no random split;
   - 2025 and 2026 reporting-only.

Citation count is evidence of maturity, not a substitute for forecasting quality. Very recent high-performing methods may enter as FRONTIER candidates even with low citation counts.

### 17.2 New prioritized family queue

Tier 1 / MUST TEST:
1. DMA / DMS / IDMA family.
2. Gradient boosting family: GBRT, XGBoost, CatBoost, LightGBM, HistGradientBoosting and controlled regularized/shallow variants.
3. Wavelet-SVR family: linear/RBF SVR anchor, DWT-SVR and causal rolling wavelet variants.
4. CNN-BiLSTM family: LSTM/CNN/BiLSTM/CNN-LSTM/ConvLSTM/CNN-BiLSTM with small-sample architecture control.

Tier 2 / HIGH-VALUE FRONTIER:
5. Attention-GRU / MA-GRUS family.
6. Transformer family: Transformer, PatchTST, LSTM-Transformer and DPformer subject to sample-size gate.

Tier 3 / DECOMPOSITION-HYBRID, CAUSAL IMPLEMENTATION REQUIRED:
7. ICEEMDAN-LSTM-CNN-CBAM family.
8. VMD + BiLSTM/BiGRU + Bayesian-optimization family.

Existing or already-covered families are not to be restarted blindly. ANN/ELM/ANFIS/RBFNN/GPR variants are reopened only for exact literature-specific replication when the prior implementation is materially different from the authoritative mechanism.

RFF-BLR, GOR-ELM, KRR/KELM/Twin-SVR and other cross-domain candidates remain in the reserve research pool; they are no longer the automatic next families.

### 17.3 Family-specific experimentation rule

Do NOT automatically run a 30+ metaheuristic screen for every new family.

For each family:
Stage 0 — canonical baseline / authoritative reproduction target.
Stage 1 — the family's own literature-supported variants / ablations.
Stage 2 — DEV-only filtering and role/parent freeze.
Stage 3 — literature-specific hybrid/refinement only when supported by authority or Stage-2 evidence.
Stage 4 — ensemble only if multiple retained models are demonstrably complementary.
Stage 5 — global cross-family comparison.

Metaheuristic optimization is opened only when the authoritative literature uses it for that family or when a predeclared scientific rationale exists.

### 17.4 Current next family

The next family is:
**DMA / DMS / IDMA for monthly gold forecasting.**

Before production execution, a dedicated authority document must freeze:
- original DMA/DMS mechanism;
- gold-specific forecasting evidence;
- IDMA mechanism;
- forgetting-factor design;
- model-space definition;
- predictor subset policy;
- prior/initial probability policy;
- predictive-density/weight update equations;
- chronology-safe implementation;
- exact Stage 0–5 plan;
- treatment of the project's 4-metal target structure;
- 2025/2026 exclusion.

No DMA/DMS/IDMA production result may be used before that authority specification is committed.


### 17.5 DMA/DMS/IDMA authority freeze and execution order

Authority document committed:
`gold_axis_2026/GOLD_MONTHLY_DMA_DMS_IDMA_AUTHORITY_AND_STAGE_PLAN_2026-09-27.md`

Authority commit:
`9af2868f5390e5778f096531f32ac3f7cf5a276e`

Binding execution order:
- Stage 0: RW + static anchor + BMA + TVP + canonical DMA + canonical DMS.
- Stage 1: authority-supported forgetting-factor variants with nested/prequential selection only.
- Stage 2: DOW-DMA / DOW-DMS.
- Stage 3: IDMA (log-PL objective, forecast-error objective, predictor-selection ablation, forgetting-factor-calibration ablation).
- Stage 4: DEV-only family freeze.
- Stage 5: 2025/2026 reporting-only and global cross-family comparison.

Canonical gold-DMA settings:
- alpha=0.99;
- lambda=0.99;
- equal/non-informative initial model probabilities;
- diffuse initial state;
- 256 subset models from the frozen 8 origin-safe predictors;
- Gold-only canonical target in the first pass.

No production DMA-family result is authoritative before Stage 0 chronology/probability/scientific gates pass.


---

## 18. ChHHO HIGH-ERROR ALARM RESEARCH — FROZEN CHECKPOINT 2026-09-30

**Status:** ALARM-DETECTION RESEARCH ACTIVE / ROUTING NOT AUTHORIZED  
**Primary model:** ChHHO-ANFIS  
**Selection authority:** DEV 2022-04..2024-12 (33 target months)  
**Transport/reporting only:** 2025 and 2026  
**Alarm target for current audit:** HIGH ERROR = ChHHO AE > frozen DEV Q3 = **63.06 USD**

### 18.1 Scope and governance

This work answers only:

> Can an origin-visible warning state identify a month in which ChHHO has elevated error risk before the target month begins?

It does **not** authorize:
- switching to another model;
- fallback selection;
- routing/blending;
- retuning A/C/D on 2025/2026;
- moving thresholds merely to catch a known miss;
- claiming post-hoc discovery rules as validated out-of-sample alarms.

A/C/D below remain the DEV-derived frozen mechanisms.  
B remains warning-only because it produced extra DEV alarms.  
E/G were discovered after inspecting later misses and are therefore **candidate characterization layers frozen only for historical validation**, not production alarms.

### 18.2 Frozen / candidate alarm definitions

#### A — CROSS_METAL_FRAGILITY — FROZEN STRONG MODEL-INTERACTION ALARM
At origin:
- ChHHO forecast direction = current Gold monthly direction;
- |Gold monthly log return| < 2%;
- at least 2 of Silver / Platinum / Palladium move opposite to Gold.

DEV exact flags:
- 2022-11 — AE 102.20
- 2023-08 — AE 77.53

Transport:
- 2025-09 — HIT, AE 288.42
- 2025-12 — HIT, AE 93.32
- 2026-05 — FALSE ALARM, AE 55.10

Current reading: strong ChHHO-specific relationship alarm; not a universal market-stress alarm.

#### B — SUPPORTED_MOMENTUM_UNDERREACTION — WARNING ONLY
At origin:
- Gold monthly log return > +3%;
- at least 2 other precious metals positive;
- Broad USD monthly mean log change < 0;
- nominal 10Y monthly-mean change < 0;
- real 10Y monthly-mean change < 0;
- ChHHO predicted Gold move <= +1%.

DEV:
- intended hit 2023-01 — AE 100.74
- extra flags 2023-02 — AE 29.06
- 2023-05 — AE 19.38

Transport:
- 2025-03 — HIT, AE 119.06

Status: confidence reduction / yellow warning only; not a hard alarm.

#### C — DELAYED_RATES_CATCHUP — FROZEN STRONG BUT LOW-EVENT ALARM
At origin:
- Gold monthly log return < 0;
- nominal 10Y monthly-mean change < 0;
- real 10Y monthly-mean change < 0;
- |ChHHO predicted Gold move| < 1%.

DEV exact flag:
- 2024-07 — AE 71.01

No 2025/2026 transport event yet.

#### D — MACRO_GOLD_CONFLICT — FROZEN STRONG BUT RARE ALARM
At origin:
- Gold monthly log return > +3%;
- Broad USD monthly mean log change > 0;
- nominal 10Y monthly-mean change > 0;
- real 10Y monthly-mean change > 0;
- ChHHO predicts UP.

DEV exact flag:
- 2024-11 — AE 119.13

No 2025/2026 transport event yet.

#### E — EXTREME_LEVEL_MODEL_DISAGREEMENT — CANDIDATE / DISCOVERY-FROZEN
For the historical-validation exercise only, freeze:
- Gold monthly-average price > 20% above trailing 12-month average; and
- |ChHHO predicted return − current Gold 1m return| > 5 percentage points.

Observed later high-error flags:
- 2025-05 — AE 90.25
- 2025-11 — AE 163.94
- 2026-01 — AE 458.50
- 2026-03 — AE 145.62

All four observed flags are high-error, but this **is not validated precision** because the rule was discovered after inspecting later misses.

Independent market-state history, 2011-2021:
- extreme-level >20% events: 3
- next-month high-severity market states: 3/3
- interpretation: direction is not fixed; magnitude/extrapolation risk is elevated.

#### G — POST_LIQUIDATION_HIGH_UNCERTAINTY — CANDIDATE / DISCOVERY-FROZEN
For historical validation only, freeze:
- trailing 3-month Gold monthly-average log return <= -10%.

Observed ChHHO-period flags:
- 2022-08 — AE 35.85 — FALSE ALARM
- 2026-07 — AE 82.68 — HIT
- 2026-08 — AE 347.99 — HIT

Independent market-state history, 2011-2021:
- 3m <= -10% events: 5
- next-month high-severity states: 4/5
- mean next-month absolute Gold move about 4.53% vs about 2.63% baseline.

**Do not relax to -8% merely to catch 2026-06.** Historical selectivity deteriorates materially when the drawdown threshold is loosened.

### 18.3 Current five-alarm audit, 2022-04..2026-08

Hard/current research set = A OR C OR D OR E OR G.  
B is excluded from hard-alarm counts and retained as warning-only.

Alarm months:

| Target | Mechanism | ChHHO AE USD | Frozen high-error? | Result |
|---|---|---:|---|---|
| 2022-08 | G | 35.85 | NO | FALSE ALARM |
| 2022-11 | A | 102.20 | YES | HIT |
| 2023-08 | A | 77.53 | YES | HIT |
| 2024-07 | C | 71.01 | YES | HIT |
| 2024-11 | D | 119.13 | YES | HIT |
| 2025-05 | E | 90.25 | YES | HIT |
| 2025-09 | A | 288.42 | YES | HIT |
| 2025-11 | E | 163.94 | YES | HIT |
| 2025-12 | A | 93.32 | YES | HIT |
| 2026-01 | E | 458.50 | YES | HIT |
| 2026-03 | E | 145.62 | YES | HIT |
| 2026-05 | A | 55.10 | NO | FALSE ALARM |
| 2026-07 | G | 82.68 | YES | HIT |
| 2026-08 | G | 347.99 | YES | HIT |

Period summary:

| Period | High-error months | Hard alarms | Hits | False alarms | High-error recall |
|---|---:|---:|---:|---:|---:|
| DEV 2022-04..2024-12 | 8 | 5 | 4 | 1 | 4/8 = 50% |
| 2025 | 8 | 4 | 4 | 0 | 4/8 = 50% |
| 2026 Jan-Aug | 5 | 5 | 4 | 1 | 4/5 = 80% |

**Governance note:** the 2025/2026 result above is descriptive research evidence only. E and G were discovered after observing later misses; therefore the combined 4/5 2026 recall must **not** be described as an out-of-sample validated alarm-system performance.

### 18.4 Negative / closed alarm branches

Gold-specific ETF flows, CFTC Managed Money positioning and GVZ were already researched.

Broad F-style screens were not selective enough to promote as a general ChHHO high-error alarm:
- loose OR combinations produced too many alerts;
- stricter 2-of-3 / 3-of-3 combinations lost recall;
- historical tests showed general stress/regime information, not a clean ChHHO-specific failure detector.

Status:
- **ETF/CFTC/GVZ = COMPLETED SECONDARY DESCRIPTORS / NOT PROMOTED AS GENERAL ALARM**
- do not restart this branch without a new scientific question.

### 18.5 Unresolved case

**2026-06 — ChHHO AE 362.17 USD**

Origin 2026-05:
- Gold about -2.82% 1m;
- about -8.88% 3m;
- ChHHO near flat;
- not E;
- not G at the frozen -10% threshold;
- not A/C/D.

This case remains intentionally unresolved. Existing alarm thresholds must not be distorted to force a hit.

### 18.6 Current alarm hierarchy

**Primary strong/current research alarms**
1. A — Cross-metal fragility
2. E — Extreme level + ChHHO disagreement
3. G — Post-liquidation high uncertainty

**Strong but low-event support alarms**
4. C — Delayed rates catch-up
5. D — Macro-Gold conflict

**Warning-only**
6. B — Supported momentum underreaction

### 18.7 Next binding experiment — historical ChHHO backcast

Before any routing/fallback experiment:

1. Reconstruct ChHHO forecasts for the earliest scientifically feasible pre-DEV history, target **2018-01..2021-12** if minimum training-history constraints permit.
2. Every historical origin must use only information available by that origin; no future labels, no 2022+ fitting, and no target-month leakage.
3. Keep A/C/D unchanged.
4. Keep E/G thresholds exactly at the discovery-frozen values above; no threshold search on backcast results.
5. Report per mechanism:
   - alarms,
   - high-error hits,
   - false alarms,
   - misses,
   - conditional AE / APE,
   - year-by-year stability.
6. Compare 2018-2021 backcast vs DEV 2022-2024 vs 2025 vs 2026 without pooling selection authority.
7. If the original ChHHO algorithm cannot be reconstructed for a pre-DEV origin because the required minimum training history is unavailable, report the earliest feasible origin and **do not fabricate a backcast**.
8. No router/model-switching stage opens until this alarm-validation checkpoint is closed.

**Next action:** execute the 2018-2021 origin-safe ChHHO backcast and frozen-alarm false-alarm/hit audit.


### 18.8 Historical ChHHO backcast feasibility gate — BLOCKED BY PIT SOURCE COVERAGE

Attempted next experiment: origin-safe ChHHO backcast for 2018-01..2021-12 using the exact production/research feature contract.

Result: **BLOCKED / DO NOT FABRICATE BACKCAST.**

Evidence:
- Neon series `GPR_OFFICIAL_GIT_PIT` has first exact origin vintage **2022-03** and continuous proven coverage from 2022-03 onward.
- Canonical source contract `source_contract_gpr_pit_v2.json` explicitly freezes `continuous_proven_origin_start = 2022-03`.
- Older archive files such as 2021-10/11/12 and 2022-01 were only added to the official Git archive on **2022-03-01**, i.e. after their own forecast origins, so they cannot be treated as point-in-time evidence for those months.
- The official monthly Git archive does not provide a proven exact-origin vintage path for 2018-2021 under the current approved source policy.
- Current/final-vintage GPR substitution remains forbidden.

Scientific consequence:
- The earliest exact-origin ChHHO target buildable under the frozen GPR PIT contract is **2022-04** (origin 2022-03), which is already the start of the existing DEV period.
- Therefore there is no independent pre-DEV ChHHO backcast sample available under the current canonical data authority.
- A/C/D cannot receive a genuine pre-2022 ChHHO-specific false-alarm test without opening and separately validating a new historical PIT GPR authority.
- E/G retain independent **market-state** historical evidence from 2011-2021, but this is not equivalent to ChHHO-specific error validation.

Binding rule:
- Do not use final-vintage GPR, retrospectively backfilled current GPR, or any unproven historical GPR series merely to obtain 2018-2021 ChHHO predictions.
- Any future attempt to extend ChHHO before 2022-04 requires a separately committed historical-GPR source authority with exact origin-time availability proof before model execution.

Current alarm-validation evidence stack therefore remains:
1. 2011-2021 model-free market-state history for E/G and supporting mechanism context.
2. 2022-2024 DEV mechanism diagnostics for A/C/D and ChHHO error behavior.
3. Frozen 2025 transport evidence for A/B.
4. 2026 stress evidence plus discovery-only E/G characterization.
5. 2026-06 remains unresolved.

**Backcast experiment status:** BLOCKED_VALIDLY_BY_SOURCE_COVERAGE, not failed scientifically and not replaced by a leaky approximation.


### 18.9 Pre-DEV ChHHO backcast result — COMPLETED 2026-09-30

Authority:
- `gold_axis_2026/GOLD_MONTHLY_CHHHO_PREDEV_GPR_WEB_LATEST_AUTHORITY_2026-09-30.md`
- authority commit: `4c607f78d37291fd0c4685efffd03ef060c187a0`

Execution:
- workflow: `Gold Monthly ChHHO PreDEV Backcast V1`
- successful run: **36684719608**
- code commit: `b31e181487c016cad15b7d4c7ce7e9ef80b13633`
- artifact: **11083172327**
- result report: `gold_axis_2026/GOLD_MONTHLY_CHHHO_PREDEV_ALARM_BACKCAST_RESULT_2026-09-30.md`
- result report commit: `2842f80d0afae76c6fcce47568a200c6f5ace13c`
- scientific gate: **PASS**

Historical PIT source:
- official repo `iacoviel/iacoviel.github.io`
- path `gpr_files/gpr_web_latest.xlsx`
- latest Git commit <= each origin cutoff
- no current/final-vintage GPR substitution

Coverage:
- requested origins: 27 (2019-12..2022-02)
- buildable origins: **21**
- first buildable: 2019-12
- last buildable: 2021-10
- blocked p-1-missing origins: 2020-10, 2021-05, 2021-11, 2021-12, 2022-01, 2022-02

ChHHO backcast on 21 buildable origins:
- cumulative AE: **922.53 USD**
- MAE: **43.93 USD**
- mean APE: **2.518%**

Frozen AE-Q3 high-error definition (AE > 63.06 USD):
- high-error months: **6**
- hard alarms A/C/D/E/G: **2**
- hits: **0**
- false alarms: **2**
- misses: **6**
- precision: **0%**
- recall: **0%**

High-error targets missed by all hard alarms:
- 2020-03 — AE 81.87, APE 5.14%
- 2020-04 — AE 113.65, APE 6.75%
- 2020-07 — AE 70.42, APE 3.81%
- 2021-03 — AE 93.31, APE 5.43%
- 2021-04 — AE 66.64, APE 3.79%
- 2021-08 — AE 74.79, APE 4.19%

Alarm events:
- A: 0 events
- C: 2021-09 — AE 14.32, APE 0.81% — **FALSE ALARM**
- D: 0 events
- E: 2020-09 — AE 23.68, APE 1.23% — **FALSE ALARM**
- G: 0 events

Scale-robustness check:
- DEV APE Q3 = **2.96117%**
- DEV absolute log-return-error Q3 = **3.00590 pp**
- pre-DEV high APE months = **8**
- pre-DEV high return-error months = **8**
- for both definitions: **0 hits, 2 false alarms, 8 misses**
- therefore the negative pre-DEV result is not an artifact of the nominal USD threshold.

#### Binding revision to alarm hierarchy

The prior 18.6 hierarchy is superseded by this evidence.

**A — Cross-metal fragility**
- retains strong/selective 2022+ descriptive evidence;
- pre-DEV had no A events;
- status: **PROMISING / NOT INDEPENDENTLY VALIDATED**.

**C — Delayed rates catch-up**
- DEV exact hit exists (2024-07);
- only pre-DEV event was false (2021-09);
- status: **MIXED / LOW-EVENT / NOT STRONG-FROZEN FOR PRODUCTION**.

**D — Macro-Gold conflict**
- DEV exact hit exists (2024-11);
- no pre-DEV event;
- status: **RARE / UNCONFIRMED OUTSIDE DEV**.

**E — Extreme level + ChHHO disagreement**
- later discovery-period hits exist;
- pre-DEV event 2020-09 was a clear false alarm despite extreme state;
- status downgraded to **MARKET-STATE / MODEL-DISAGREEMENT WARNING CANDIDATE**, not a strong ChHHO error alarm.

**G — Post-liquidation**
- retains independent market-state evidence for elevated movement/uncertainty;
- no ChHHO-specific pre-DEV event in the 21 buildable origins;
- status: **UNCERTAINTY-REGIME WARNING CANDIDATE**, not independently validated ChHHO error alarm.

**Combined A/C/D/E/G hard engine**
- status: **NOT VALIDATED / NOT PRODUCTION-READY / ROUTING PROHIBITED**.
- Do not quote 2026 discovery-period 4/5 recall as validated performance.
- Do not retune thresholds using this backcast to rescue the missed months.

#### Next binding research task

Characterize the six pre-DEV missed high-error months (2020-03, 2020-04, 2020-07, 2021-03, 2021-04, 2021-08) using origin-visible market states, then compare them with:
- DEV worst/high-error months;
- 2025 high-error months;
- 2026 high-error months, especially unresolved 2026-06.

Goal: identify a repeated natural mechanism, not fit a rule to known misses.


### 18.10 Audit correction — pre-DEV backcast INVALIDATED by GPR methodology mismatch

A post-run source-equivalence audit invalidates the interpretation recorded in 18.9.

#### Critical finding

The pre-DEV backcast used:

- official repository: `iacoviel/iacoviel.github.io`
- historical file: `gpr_files/gpr_web_latest.xlsx`

However, the official repository documents this file under the **older GPR methodology** (`gpr2019.htm`). The current canonical project source is the later GPR methodology documented in `gpr.Rmd` and distributed through `data_gpr_export.xls`.

The official current page states that the index search terms were changed in 2021 and that the current methodology differs from the old GPR index. Therefore `gpr_web_latest.xlsx` is not source-equivalent to the frozen 2022+ ChHHO GPR authority.

Observed numerical non-equivalence is material:
- old historical snapshot 2020-01 GPR ≈ **333.03**
- canonical `CORE5_GPR_ROUNDED_RESEARCH_R1` 2020-01 = **138.42**

This is not a normal small vintage revision; it indicates a different data-definition regime.

#### Consequence

The 21-origin pre-DEV run remains a technically reproducible experiment, but it **violates the frozen feature-definition contract**. It must not be used as evidence for alarm precision/recall or to downgrade/promote A/C/D/E/G.

Therefore the following conclusions from 18.9 are **withdrawn**:
- combined A/C/D/E/G = 0 hits / 2 false alarms as scientific alarm evidence;
- downgrade of E based on 2020-09;
- downgrade of C based on 2021-09;
- any claim that the frozen alarm family failed pre-DEV.

Status of run 36684719608 / artifact 11083172327:
**INVALIDATED_GPR_METHODOLOGY_MISMATCH — AUDIT TRAIL ONLY**

#### Backcast-code reconciliation

A separate reconciliation test was run to distinguish source error from implementation error.

Workflow:
- `Gold Monthly ChHHO Backcast Reconcile V1`
- run: **36687542392**
- artifact: **11084196490**

Targets checked:
- 2022-04
- 2023-08
- 2024-11

For each target:
- canonical sample keys = helper sample keys;
- max sample-array absolute difference = **0.0**;
- helper ChHHO prediction = canonical ChHHO prediction to floating-point tolerance;
- forecast = canonical stored forecast;
- train-row count = exact match;
- diagnostics = exact match.

Result: **PASS**.

Interpretation:
- the backcast helper/model implementation is correct;
- the invalidation is caused by **non-equivalent pre-DEV GPR source methodology**, not by ChHHO code or alarm calculation mechanics.

#### Restored alarm-status governance

Until a **same-methodology, origin-proven pre-2022 GPR source** is found:

- A/C/D retain their existing 2022-2024 DEV evidence only;
- E remains a discovery-period candidate with independent market-state support, not a validated production alarm;
- G remains a post-liquidation uncertainty candidate with independent market-state support, not a validated production alarm;
- no pre-DEV ChHHO-specific validation claim is allowed;
- no routing/model switching is authorized;
- thresholds remain frozen and must not be retuned from the invalid backcast.

#### Correct next question

Search only for **same-methodology pre-2022 current-GPR vintages**. If none can be proven, pre-DEV ChHHO backcast is scientifically unavailable and the project must proceed with:
1. independent model-free historical market-state evidence before 2022;
2. real ChHHO evidence from 2022 onward;
3. explicit separation between discovery and validation periods.



### 18.11 Valid same-methodology pre-DEV backcast V2 — COMPLETE

This section supersedes the invalid V1 pre-DEV alarm interpretation.

Authority:
- `gold_axis_2026/GOLD_MONTHLY_CHHHO_PREDEV_CURRENT_GPR_AUTHORITY_2026-09-30.md`
- authority commit: `ae009acc67cbf22c3cd6edaa7e934067823db260`

Execution:
- workflow: `Gold Monthly ChHHO PreDEV CurrentGPR V2`
- run: **36688284811**
- artifact: **11084467079**
- workflow/code commit: `574f82130fe8b8518b2285c1d7798cabf629c836`
- result report: `gold_axis_2026/GOLD_MONTHLY_CHHHO_PREDEV_CURRENTGPR_V2_RESULT_2026-09-30.md`
- report commit: `6eb19d91e0a8868cd62bd33495823b62dec3c571`
- scientific gate: **PASS**

#### Source

Same methodology family as canonical 2022+ project:
- official repository: `iacoviel/iacoviel.github.io`
- file: `gpr_files/data_gpr_export.xls`
- earliest proven Git history: 2021-10-18
- origin rule: latest commit <= origin month-end cutoff
- required GPR month = origin p-1
- no future/current substitution
- old-method `gpr_web_latest.xlsx` forbidden

Buildable origins:
- 2021-10
- 2021-11
- 2021-12
- 2022-01
- 2022-02

Targets:
- 2021-11
- 2021-12
- 2022-01
- 2022-02
- 2022-03

#### Results

| Target | AE USD | APE | A | C | D | E | G |
|---|---:|---:|---|---|---|---|---|
| 2021-11 | 8.41 | 0.46% | 0 | 0 | 0 | 0 | 0 |
| 2021-12 | **85.62** | **4.78%** | 0 | 0 | 0 | 0 | 0 |
| 2022-01 | 52.16 | 2.87% | 0 | 0 | 0 | 0 | 0 |
| 2022-02 | 49.67 | 2.68% | 0 | 0 | 0 | 0 | 0 |
| 2022-03 | 12.46 | 0.64% | 0 | 0 | 0 | 0 | 0 |

Frozen HIGH ERROR = AE > 63.06 USD.

Summary:
- n = **5**
- high-error months = **1**
- alarms = **0**
- hits = **0**
- false alarms = **0**
- misses = **1**

Interpretation:
- the only high-error target, **2021-12**, is not covered by A/C/D/E/G;
- this proves the current alarm family is **not exhaustive**;
- the five-origin sample is too small to estimate reliable precision/recall;
- it does **not** falsify A/C/D/E/G because none of those mechanisms fired in this window.

#### Backcast implementation audit

Reconciliation run **36687542392** / artifact **11084196490**:
- targets checked: 2022-04, 2023-08, 2024-11;
- canonical sample arrays vs backcast-helper arrays: exact match;
- ChHHO predictions: exact to floating-point tolerance;
- forecast values: canonical match;
- train-row counts: exact;
- diagnostics: exact;
- result: **PASS**.

Therefore:
- backcast implementation is correct;
- V1 was invalid because of source-methodology mismatch;
- V2 is scientifically admissible but very small.

#### Current alarm status after audit

- **A Cross-metal:** promising/selective from 2022+ evidence; no pre-DEV event in valid V2.
- **C Delayed rates:** DEV evidence only; no pre-DEV event in valid V2.
- **D Macro conflict:** rare DEV evidence only; no pre-DEV event in valid V2.
- **E Extreme-level/model disagreement:** discovery candidate + model-free historical market-state support; no pre-DEV event in valid V2.
- **G Post-liquidation:** uncertainty-regime candidate + model-free historical support; no pre-DEV event in valid V2.
- **Combined A/C/D/E/G:** not production-validated; no routing/model switching authorized.

The invalid 21-origin V1 results must never be used in future alarm summaries except as a documented source-audit failure.


### 18.12 Canonical alarm audit V3 — COMPLETE / SUPERSEDES V2 ALARM BOOLEANS

Authority:
- `gold_axis_2026/GOLD_MONTHLY_CHHHO_ALARM_AUDIT_V3_AUTHORITY_2026-09-30.md`
- authority commit: `194e436855d7eb4a9d78ba5e843d5886693de760`

Execution:
- workflow: `Gold Monthly ChHHO Alarm Audit V3`
- run: **36692016381**
- artifact: **11086181973**
- audit code commit: `6169f54414fc4da966e793726185fe64a2d31418`
- workflow commit: `523b19140eab4d9d0a58d984d5cc349e0666705f`
- result report: `gold_axis_2026/GOLD_MONTHLY_CHHHO_ALARM_AUDIT_V3_RESULT_2026-09-30.md`
- result report commit: `d5fbbe4c77b361586c60f930551bc9a5451f0f1d`
- scientific gate: **PASS**

#### Binding correction

V2's same-methodology GPR reconstruction and ChHHO forecasts remain admissible.

However, V2 alarm booleans are superseded because V2 built Gold alarm states from the common-daily four-metal reconstruction instead of the canonical monthly Gold authority.

V3 uses:
- DEV Gold: frozen snapshot `core_gold`;
- later Gold: public World Bank monthly Gold extension;
- Silver/Platinum/Palladium: governed common-daily monthly means;
- B/C/D macro: External Authority V2 H.10/H.15;
- frozen ChHHO forecast artifacts; no model rerun;
- unchanged alarm thresholds.

#### Replay gate

V3 reproduces frozen DEV A/B/C/D event sets exactly:
- A: 2022-11, 2023-08
- B warning-only: 2023-01, 2023-02, 2023-05
- C: 2024-07
- D: 2024-11

All replay gates passed before pre-DEV interpretation.

#### Gold-source discrepancy

Across 2022-04..2026-08, exactly one A/B/C/D/E/G event changes because of the canonical Gold correction:

**2026-05 / origin 2026-04**
- legacy common-daily Gold 1m = -0.6383%
- canonical monthly Gold 1m = -2.8194%
- ChHHO prediction = -1.6853%
- A requires |Gold 1m| < 2%
- legacy A = TRUE
- corrected A = FALSE

Therefore the previously reported **2026-05 A false alarm is withdrawn** as a source-construction artifact.

No threshold was changed.

#### Corrected 2022-04..2026-08 event lists

- A: 2022-11, 2023-08, 2025-09, 2025-12
- B warning-only: 2023-01, 2023-02, 2023-05, 2025-03
- C: 2024-07
- D: 2024-11
- E discovery-frozen: 2025-05, 2025-11, 2026-01, 2026-03
- G discovery-frozen: 2022-08, 2026-07, 2026-08

Hard research alarm remains A OR C OR D OR E OR G.

#### Pre-DEV macro equivalence

For all five valid same-methodology pre-DEV origins, V2 macro reconstruction equals External Authority V2 exactly:
- Broad USD max absolute difference = **0.0**
- nominal 10Y max absolute difference = **0.0**
- real 10Y max absolute difference = **0.0**

Thus the C/D macro-source concern does not create a numerical discrepancy in this window.

#### Corrected valid pre-DEV result

| Target | AE USD | APE | Return-error pp | Hard alarm | Result |
|---|---:|---:|---:|---|---|
| 2021-11 | 8.41 | 0.462% | 0.463 | **A** | **FALSE ALARM** |
| 2021-12 | **85.62** | **4.783%** | **4.672** | none | **MISS** |
| 2022-01 | 52.16 | 2.872% | 2.914 | none | normal |
| 2022-02 | 49.67 | 2.676% | 2.713 | none | normal |
| 2022-03 | 12.46 | 0.639% | 0.642 | none | normal |

The newly visible A event is 2021-11 because canonical Gold at origin 2021-10 is +0.1126%, ChHHO predicts +2.0382%, and two other precious metals move opposite to Gold.

#### Three-label robustness

Frozen labels:
- AE > 63.06 USD
- APE > 2.96117%
- absolute log-return error > 3.00590 pp

All three produce the same five-origin pre-DEV classification:
- high-error target: 2021-12
- hard alarm target: 2021-11
- hits: 0
- false alarms: 1
- misses: 1

This sample is too small for stable precision/recall estimation.

#### Corrected HIGH_AE descriptive summaries

- Pre-DEV valid window: 1 high-error / 1 alarm / 0 hit / 1 false alarm / 1 miss.
- DEV 2022-04..2024-12: 8 high-error / 5 alarms / 4 hits / 1 false alarm / 4 misses.
- 2025: 8 high-error / 4 alarms / 4 hits / 0 false alarms / 4 misses.
- 2026 Jan-Aug: 5 high-error / 4 alarms / 4 hits / 0 false alarms / 1 miss (2026-06).

The 2025/2026 counts include discovery-frozen E/G and therefore remain descriptive, not out-of-sample validation.

#### Current binding mechanism status

- **A Cross-metal fragility:** real/selective signature, but the only valid pre-DEV A event (2021-11) is false. Not independently validated as universally reliable.
- **C Delayed rates:** DEV low-event evidence only; no valid pre-DEV event.
- **D Macro conflict:** rare DEV evidence only; no valid pre-DEV event.
- **E Extreme-level/model disagreement:** later discovery-frozen candidate; no valid pre-DEV event.
- **G Post-liquidation:** uncertainty-regime candidate; no valid pre-DEV event.
- **Combined hard engine:** not production-validated; routing/model switching remains prohibited.

Binding governance:
1. V1 21-origin old-method GPR run remains invalid.
2. V2 ChHHO/GPR forecasts remain valid.
3. **V2 alarm booleans and its 0-alarm pre-DEV summary are superseded by V3.**
4. Remove 2026-05 from A false-alarm lists.
5. Add 2021-11 as the valid pre-DEV A false alarm.
6. 2021-12 remains a robust uncovered ChHHO high-error month under AE, APE and return-error definitions.
7. No threshold retuning.
8. No routing/model switching.


### 18.13 E/G historical validation V2 — COMPLETE / PRE-DISCOVERY CHECK

Authority:
- `gold_axis_2026/GOLD_MONTHLY_CHHHO_EG_HISTORICAL_VALIDATION_V2_AUTHORITY_2026-09-30.md`
- authority commit: `f569785f9247c87e0d4fbec5808614ca81ed7a35`

Execution:
- workflow: `Gold Monthly ChHHO E/G Historical Validation V2`
- run: **36697319930**
- artifact: **11087809958**
- code commit: `31cd6f975a97a5ef62dd9e9d60ec50c0a02346a6`
- workflow commit: `94d9fc3af6704f9afd42830d2e3db4eb94adac4c`
- result report: `gold_axis_2026/GOLD_MONTHLY_CHHHO_EG_HISTORICAL_VALIDATION_V2_RESULT_2026-09-30.md`
- result report commit: `593be754a1489b1e104e332a35e2f21d80a0f373`
- scientific gate: **PASS**

#### Independent market-state test, 2010-2024

Baseline across 180 monthly origins:
- mean next-month absolute Gold log return: **2.639%**
- median: **2.211%**
- Q3: **3.998%**

**E-level precursor (>20% above prior MA12)**
- events: **4** — 2011-08, 2011-09, 2020-08, 2024-10
- next-month absolute-return mean: **2.695%**
- uplift vs baseline: **1.02x**
- above baseline Q3: **1/4 = 25%**

Binding interpretation:
- E's extreme-price-level condition alone is **not** a strong historical next-month risk signal.

**G (Gold 3m log return <= -10%)**
- events: **6** — 2013-04, 2013-05, 2013-06, 2013-07, 2016-12, 2022-07
- next-month absolute-return mean: **4.067%**
- uplift vs baseline: **1.54x**
- above baseline Q3: **4/6 = 66.7%**

Binding interpretation:
- G is supported as a recurring **high-movement / uncertainty market-state signal**.
- G is not directional.

#### ChHHO-specific pre-discovery test

2022-2024 uses the frozen canonical ChHHO artifact directly; no model rerun.
Pre-2022 uses an unchanged ChHHO counterfactual stress replay with the earliest current-method 2021-10 GPR snapshot, truncated by historical origin. This is **not PIT validation**.

**G buildable pre-discovery model events**
- 2017-01 counterfactual: AE 33.75, APE 2.83%, return error 2.87pp — NOT high error.
- 2022-08 canonical: AE 35.85, APE 2.03%, return error 2.05pp — NOT high error.
- high AE / APE / return-error: **0/2**.

The four 2013 G events are unbuildable under the unchanged ChHHO internal minimum-history gate and are not replaced with another model.

Binding interpretation:
- G is **historically supported as a market-risk regime signal**.
- G is **not validated as a ChHHO high-error alarm**; available pre-discovery model-specific evidence is 0/2 high-error.

**E buildable pre-discovery evidence**
- 2020-09 counterfactual: E-level TRUE and full E TRUE; AE 26.68, APE 1.39%, return error 1.38pp — NOT high error.
- 2024-11 canonical: E-level TRUE but full E FALSE; ChHHO AE 119.13. This failure is captured by D, not E.
- two 2011 E-level events are unbuildable under the unchanged main-model history gate.

Full E pre-discovery:
- buildable events: **1**
- high AE / APE / return-error: **0/1**.

Binding interpretation:
- E is **not historically validated as a ChHHO error alarm**.
- Later 2025/2026 E hits remain discovery-period evidence.

#### Revised E/G governance

- **E:** DISCOVERY-PERIOD CHHHO DISAGREEMENT PATTERN / UNVALIDATED ERROR ALARM.
- **G:** HISTORICALLY SUPPORTED HIGH-MOVEMENT / UNCERTAINTY REGIME WARNING; NOT A VALIDATED CHHHO ERROR ALARM.
- E and G must not be counted as independently validated hard alarms when quoting alarm-system performance.
- No threshold retuning.
- No routing/model switching from E/G.


### 18.14 Historical ChHHO performance audit — COMPLETE / H1 MODEL-SPECIFIC ALARM EVIDENCE DOWNGRADED

Authority:
- `gold_axis_2026/GOLD_MONTHLY_CHHHO_HISTORICAL_PERFORMANCE_AUDIT_AUTHORITY_2026-09-30.md`
- authority commit: `9e260efc73b421b79ecea8f0f8217e1f5bf00e81`

Execution:
- workflow: `Gold Monthly ChHHO Historical Performance Audit V1`
- run: **36698427012**
- artifact: **11088508878**
- code commit: `1ac65d66871f5edacdac4dd108395958bd17e434`
- workflow commit: `ed43d05a7ae9ff41c50c2eebd0639088d048ce08`
- result report: `gold_axis_2026/GOLD_MONTHLY_CHHHO_HISTORICAL_PERFORMANCE_AUDIT_RESULT_2026-09-30.md`
- report commit: `7eef51f8b5f90bfcccc41bc0550b824bbfed8991`
- scientific gate: **PASS**

#### H1 counterfactual 2013-09..2021-10

The unchanged ChHHO was run for every feasible historical target using the current-method GPR snapshot as a truncated counterfactual history.

Performance:
- n = **98**
- ΣAE = **6141.85 USD**
- MAE = **62.67 USD**
- MAPE = **4.65%**
- RMSE = **155.06 USD**
- direction = **54/98 = 55.1%**
- relative MAE vs RW = **1.90**
- HIGH_AE = **25/98**
- worst target = **2019-03**, AE **1290.22 USD**, APE **99.17%**

Binding interpretation:
- H1 is **not an effective historical forecast baseline**.
- H1 is materially worse than random walk and contains catastrophic extrapolation/numerical-instability cases.
- H1 must not be used as strong ChHHO-specific alarm validation evidence.

Worst-path numerical examples:
- 2019-03 forecast 10.78 vs actual 1301, predicted log return -4.8077, design condition ≈ 2.32e24.
- 2015-03 design condition ≈ 5.55e33.
- 2020-04 design condition ≈ 1.65e18.
- 2014-02 condition ≈ 5.10e6.

#### H2 valid same-method pre-DEV 2021-11..2022-03

- n = 5
- ΣAE = **208.32 USD**
- MAE = **41.66 USD**
- MAPE = **2.29%**
- direction = **2/5 = 40%**
- relative MAE vs RW = **0.886**
- HIGH_AE = **1/5**
- worst = 2021-12, AE 85.62

Small sample but not globally pathological.

#### H3 frozen canonical DEV 2022-04..2024-12

- n = 33
- ΣAE = **1413.03 USD**
- MAE = **42.82 USD**
- MAPE = **2.11%**
- RMSE = **54.83 USD**
- direction = **23/33 = 69.7%**
- relative MAE vs RW = **0.804**
- HIGH_AE = **8/33**

This is the effective/governed model block.

#### H1 HIGH_AE targets

2013-09, 2013-10, 2013-11,
2014-01, 2014-02, 2014-03, 2014-09,
2015-01, 2015-03,
2016-02, 2016-03, 2016-10,
2019-03, 2019-06, 2019-08, 2019-10, 2019-11,
2020-03, 2020-04, 2020-07, 2020-12,
2021-03, 2021-04, 2021-06, 2021-08.

#### H2/H3 HIGH_AE targets

H2:
- 2021-12.

H3:
- 2022-05
- 2022-07
- 2022-11
- 2023-01
- 2023-08
- 2024-03
- 2024-07
- 2024-11

#### E/G model-specific occurrences in usable historical blocks

**E**
- 2020-09: E-level TRUE, full E TRUE; AE 26.68 — NOT high error.
- 2024-11: E-level TRUE, full E FALSE; AE 119.13 — high error via D mechanism.
- 2011-09 and 2011-10 E-level targets are model-unbuildable under unchanged ChHHO.

**G**
- 2017-01: G TRUE; AE 33.75 — NOT high error.
- 2022-08: G TRUE; AE 35.85 — NOT high error.
- 2013-05/06/07/08 G targets are model-unbuildable under unchanged ChHHO.

Later discovery-period full-E targets:
- 2025-05, 2025-11, 2026-01, 2026-03 — high error.

Later discovery-period G targets:
- 2026-07, 2026-08 — high error.

#### Revised governance

- H1 counterfactual model-specific E/G results = exploratory diagnostics only.
- G's independent market-state history remains valid and supports G as a high-movement/uncertainty regime warning.
- E remains an unvalidated ChHHO-error alarm.
- G remains unvalidated as a ChHHO-error alarm.
- H2/H3 and frozen later transport remain the legitimate model-performance reference blocks.
- No threshold retuning.
- No routing/model switching.


### 18.15 Miss mechanism screen V2 — COMPLETE / H CANDIDATE ADDED

Authority:
- `gold_axis_2026/GOLD_MONTHLY_CHHHO_MISS_MECHANISM_SCREEN_V2_AUTHORITY_2026-09-30.md`
- authority commit: `69ea7d54308573928a1761ae56c246b5fd70266c`

Execution:
- workflow: `Gold Monthly ChHHO Miss Mechanism Screen V2`
- run: **36700638160**
- artifact: **11089099005**
- code commit: `297202a174940883a06d84b76c70595665742afc`
- workflow commit: `ec5159fe926123426de3b1ca36709c72670df89f`
- result report: `gold_axis_2026/GOLD_MONTHLY_CHHHO_MISS_MECHANISM_SCREEN_V2_RESULT_2026-09-30.md`
- report commit: `35befa9ec6b9185b4be5ebc4873215902488c188`
- scientific gate: **PASS**

#### Scope correction

The unstable H1 2013-2021 counterfactual ChHHO block is excluded from model-error validation.

Usable model evidence:
- H2 valid same-method pre-DEV 2021-11..2022-03
- H3 frozen canonical DEV 2022-04..2024-12
- frozen 2025 transport
- frozen 2026 Jan-Aug

For this screen, an already-explained high-error month is any HIGH_AE target with A OR B OR C OR D.

#### Independent calibration

All candidate GVZ/CFTC quantile thresholds were calibrated on **2010-01..2020-12 only**, before the usable evaluation period.

Key frozen thresholds:
- abs monthly Managed-Money net/OI change Q90 = **0.1499821**
- abs monthly OI pct change Q90 = **14.9766%**
- OI / prior-12m median Q10 = **0.865006**
- Managed-Money net/OI Q10/Q90 = **0.0293005 / 0.363831**
- GVZ max Q80/Q90 = **24.468 / 28.321**
- GVZ dynamic ratio Q90 = **1.404916**
- Gold realized-vol ratio Q95 = **1.861729**

No 2021+ model error was used to select these quantile thresholds.

#### New repeated mechanism candidate H — CFTC POSITIONING SHIFT

Frozen definition:
- abs monthly change in Managed-Money net position / OI >= 0.1499821
  OR
- abs monthly open-interest change >= 14.9766%.

Pre-discovery 2021-11..2024-12:
- events 6
- high-error hits 2
- false alarms 4
- hits: 2021-12 and 2024-07
- 2021-12 is the previously unexplained hit; 2024-07 is already C.

Later:
- 2025: 2025-02 and 2025-10, both HIGH_AE, no false alarms.
- 2026 Jan-Aug: 2026-03 HIGH_AE, no false alarms.

All usable:
- events 9
- high-error hits 5
- false alarms 4
- precision 55.6%
- all-HIGH_AE recall 22.7%
- previously unexplained hits 4/14 = 28.6%:
  - 2021-12
  - 2025-02
  - 2025-10
  - 2026-03

Status:
**H = PROMISING POSITIONING-REPRICING WARNING / NOT HARD ALARM.**

This is the only candidate in the screen with a pre-discovery unexplained high-error hit and repeated later unexplained hits without threshold retuning.

#### Other candidate families

- POSITION_EXTREME: later 2025-01/02 descriptor; no pre-discovery unexplained hit.
- OI_COMPRESSION: 2026-heavy; no pre-discovery unexplained hit.
- FLOW_2OF4: later-regime flow warning; no pre-discovery unexplained hit.
- GVZ Q80/Q90/dynamic: later-regime gold-volatility warnings; no pre-discovery unexplained hit.
- E frozen: later discovery-period only; no pre-discovery unexplained hit.
- G frozen: later post-liquidation hits; pre-discovery 2022-08 is false.

No candidate above is promoted to a hard ChHHO error alarm.

#### Remaining no-signal HIGH_AE targets

Exactly three A/B/C/D-unexplained high-error targets have none of the fixed E/G/GVZ/CFTC/volatility candidate states:

- 2022-05 — AE 79.94
- 2022-07 — AE 64.95
- 2024-03 — AE 131.58

Cross-model overlap authority:
- 2024-03: 16/16 competitive models top-8; best alternative improves only 5.47 USD -> **SHARED-HARD**.
- 2022-07: 14/16; best alternative improves only 1.76 USD -> **SHARED-HARD**.
- 2022-05: 11/16; best alternative improves 17.77 USD -> **BROADLY HARD / LIMITED RESCUE**.

Binding implication:
Do not force a ChHHO-specific alarm to catch these three months. They belong primarily to a global hard-month/shock-risk class.

#### Revised alarm/research map

- A — cross-metal fragility
- B — supported momentum underreaction, warning-only
- C — delayed rates catch-up
- D — macro-Gold conflict
- **H — CFTC positioning shift, new warning-only candidate**
- E — discovery-period disagreement descriptor, unvalidated
- G — historical high-movement regime warning, not a validated ChHHO error alarm
- GVZ/OI/FLOW — later-regime flow/volatility descriptors, not promoted

No routing/model switching authorized.


### 18.16 Alarm error-label revision V1 — PRIMARY LABEL MOVED FROM AE TO RETURN SPACE

Authority:
- `gold_axis_2026/GOLD_MONTHLY_CHHHO_ERROR_LABEL_REVISION_V1_AUTHORITY_2026-09-30.md`
- authority commit: `b539f41999656a995b4885d8cbb8d28714e18784`

Execution:
- workflow: `Gold Monthly ChHHO Error Label Revision V1`
- successful exact-Q3 run: **36701753769**
- artifact: **11089679811**
- exact-Q3 code commit: `b1de501398940701ff3c89dbdb6e45eafc780472`
- result report: `gold_axis_2026/GOLD_MONTHLY_CHHHO_ERROR_LABEL_REVISION_V1_RESULT_2026-09-30.md`
- report commit: `39aff1bfd701bae572b40a62c69282e5536e5796`
- scientific gate: **PASS**

#### Binding correction

A fixed USD AE threshold is no longer the primary model-failure label for alarm research because it is not scale invariant as Gold's nominal price changes.

Project model selection/economic evaluation is **unchanged**:
- cumulative absolute USD error ΣAE remains primary;
- direction remains co-primary;
- MAE/MAPE/WAPE/RMSE remain supporting.

Alarm research primary target is now:

**HIGH_RETURN_ERROR = absolute Gold log-return forecast error > exact DEV Q3.**

Exact authoritative DEV Q3 thresholds:
- AE Q3 = **63.0550184580 USD**
- APE Q3 = **2.9611704846%**
- return-error Q3 = **3.0058983302 percentage points**

HIGH_APE is mandatory robustness.
HIGH_AE is reporting/economic impact only, not primary alarm classification.

#### Robustness result

Across 58 scientifically usable ChHHO targets:
- HIGH_AE = **22**
- HIGH_APE = **18**
- HIGH_RETURN_ERROR = **18**

HIGH_APE and HIGH_RETURN_ERROR select **exactly the same 18 targets**.

Therefore the normalized error definition is robust across two independent normalizations.

#### AE classification bias

AE-only high-error targets that are NOT high under normalized metrics:
- 2024-07
- 2025-01
- 2025-05
- 2025-12
- 2026-07

Normalized-only target missed by fixed AE:
- **2022-09** — AE 58.98 USD, APE 3.5093%, return error 3.4492pp.

This is binding evidence that fixed-dollar AE distorts alarm classification across changing Gold price levels.

#### New canonical normalized high-error target set

Valid pre-DEV:
- 2021-12

DEV:
- 2022-05
- 2022-07
- **2022-09**
- 2022-11
- 2023-01
- 2023-08
- 2024-03
- 2024-11

2025:
- 2025-02
- 2025-03
- 2025-09
- 2025-10
- 2025-11

2026 Jan-Aug:
- 2026-01
- 2026-03
- 2026-06
- 2026-08

#### Revised alarm interpretations

**A**
- normalized hits: 2022-11, 2023-08, 2025-09
- false alarms: 2021-11, 2025-12
- remains selective/promising, not universally validated.

**B**
- normalized hits: 2023-01, 2025-03
- remains warning-only.

**C**
- only event 2024-07 lies exactly at normalized DEV Q3 boundary and is not above Q3.
- previous AE-based hit status is withdrawn.
- status: **MECHANISM DESCRIPTOR / UNVALIDATED WARNING**.

**D**
- 2024-11 remains a normalized high-error hit.
- status unchanged: rare/low-event but real normalized hit.

**H — CFTC POSITIONING SHIFT**
- normalized hits: 2021-12, 2025-02, 2025-10, 2026-03
- events 9 / hits 4 / false alarms 5
- precision 44.4%
- previous AE-based 2024-07 H hit is withdrawn.
- remains promising repeated warning candidate, not hard alarm.

**E**
- events: 2025-05, 2025-11, 2026-01, 2026-03
- normalized hits: 2025-11, 2026-01, 2026-03
- 2025-05 is not normalized high error.
- still discovery-period / unvalidated.

**G**
- events: 2022-08, 2026-07, 2026-08
- normalized hit only 2026-08.
- reinforces G as high-movement/uncertainty regime warning, not ChHHO error alarm.

#### A/B/C/D/H normalized coverage

DEV:
- high errors 8
- hits 4
- recall 50%
- hits: 2022-11, 2023-01, 2023-08, 2024-11
- misses: 2022-05, 2022-07, **2022-09**, 2024-03

2025:
- high errors 5
- hits 4
- descriptive recall 80%
- miss: 2025-11

2026 Jan-Aug:
- high errors 4
- hit 1
- descriptive recall 25%
- misses: 2026-01, 2026-06, 2026-08

All usable:
- 18 normalized high-error months
- A/B/C/D/H hits 10
- misses 8
- precision 52.6%
- recall 55.6%
These are descriptive mechanism-coverage figures, not production alarm performance.

#### Remaining primary normalized-error misses after A/B/C/D/H

- 2022-05
- 2022-07
- **2022-09**
- 2024-03
- 2025-11
- 2026-01
- 2026-06
- 2026-08

Descriptor coverage:
- 2025-11: E + GVZ
- 2026-01: E + GVZ
- 2026-06: GVZ + OI compression + FLOW_2OF4
- 2026-08: G + GVZ + OI compression + FLOW_2OF4

No fixed candidate signal:
- 2022-05
- 2022-07
- **2022-09**
- 2024-03

2022-09 is a newly exposed normalized-error miss and requires separate cross-model/mechanism audit.

#### Supersession rule

Any prior alarm hit/false-alarm statement that depended solely on HIGH_AE is superseded by this section when AE and normalized labels disagree.

No alarm thresholds were retuned.
No routing/model switching is authorized.


### 18.17 Error severity V2 — FIXED 2.5% / 3.0% NORMALIZED BANDS

Authority:
- `gold_axis_2026/GOLD_MONTHLY_CHHHO_ERROR_SEVERITY_V2_AUTHORITY_2026-09-30.md`
- authority commit: `e08c0cf26d26ab8b47b38d7dc4fb93dc83cbbc37`

Execution:
- workflow: `Gold Monthly ChHHO Error Severity V2`
- run: **36702363530**
- artifact: **11090178105**
- code commit: `db7c60786c872d965be21e5f0c215226334dd8f0`
- workflow commit: `872f816e057e9ffed13a6e6920e87bd339b6860a`
- result report: `gold_axis_2026/GOLD_MONTHLY_CHHHO_ERROR_SEVERITY_V2_RESULT_2026-09-30.md`
- report commit: `d3a710705a236ab250d046b98fdfc895cf0d7f0b`
- scientific gate: **PASS**

#### Binding severity definition

Alarm research uses absolute Gold log-return forecast error:

- **NORMAL:** < 2.50 percentage points
- **MEDIUM:** 2.50 <= error < 3.00 percentage points
- **HIGH:** error >= 3.00 percentage points

This supersedes the previous exact DEV-Q3 return-error cutoff (3.0058983302pp) as the primary human-readable severity classification.

Project model evaluation is unchanged:
- ΣAE remains primary economic/model-selection metric;
- direction remains co-primary;
- MAE/MAPE/WAPE/RMSE remain supporting.

AE is not the alarm severity label.

#### Severity counts — 58 usable ChHHO targets

- NORMAL: **34**
- MEDIUM: **5**
- HIGH: **19**

MEDIUM targets:
- 2022-01
- 2022-02
- 2024-04
- 2025-01
- 2025-05

HIGH targets:
- 2021-12
- 2022-05
- 2022-07
- 2022-09
- 2022-11
- 2023-01
- 2023-08
- 2024-03
- **2024-07**
- 2024-11
- 2025-02
- 2025-03
- 2025-09
- 2025-10
- 2025-11
- 2026-01
- 2026-03
- 2026-06
- 2026-08

Difference from superseded DEV-Q3 rule:
- only **2024-07** changes;
- return error 3.00589833pp is >=3.0, therefore HIGH under V2.

#### A/B/C/D/H HIGH-error coverage

DEV:
- HIGH 9
- hits 5
- recall 55.6%
- hits: 2022-11, 2023-01, 2023-08, 2024-07, 2024-11
- misses: 2022-05, 2022-07, 2022-09, 2024-03

2025:
- HIGH 5
- hits 4
- descriptive recall 80%
- miss: 2025-11

2026 Jan-Aug:
- HIGH 4
- hit 1
- descriptive recall 25%
- hit: 2026-03
- misses: 2026-01, 2026-06, 2026-08

All usable:
- HIGH 19
- A/B/C/D/H hits 11
- false alarms relative to HIGH 8
- precision 57.9%
- recall 57.9%

These are descriptive mechanism-coverage figures, not production performance.

#### Mechanism updates

- **A:** HIGH hits 2022-11, 2023-08, 2025-09; false relative to HIGH 2021-11, 2025-12.
- **B:** HIGH hits 2023-01, 2025-03; warning-only.
- **C:** 2024-07 = 3.005898pp and therefore HIGH under fixed 3.0pp rule. C regains its single low-event HIGH hit.
- **D:** 2024-11 remains HIGH hit.
- **H:** HIGH hits 2021-12, 2024-07, 2025-02, 2025-10, 2026-03; 9 events total, 5 HIGH hits, 4 false relative to HIGH, precision 55.6%. Warning-only candidate.

#### MEDIUM errors

Five targets:
- 2022-01
- 2022-02
- 2024-04
- 2025-01
- 2025-05

A/B/C/D/H identifies only 2024-04 among these, via H.

MEDIUM+HIGH elevated error:
- total 24
- A/B/C/D/H hits 12
- recall 50%
- precision 63.2%

#### Remaining HIGH misses after A/B/C/D/H

- 2022-05
- 2022-07
- 2022-09
- 2024-03
- 2025-11
- 2026-01
- 2026-06
- 2026-08

Descriptor coverage:
- 2025-11: E + GVZ
- 2026-01: E + GVZ
- 2026-06: GVZ + OI compression + FLOW_2OF4
- 2026-08: G + GVZ + OI compression + FLOW_2OF4

No fixed candidate descriptor:
- 2022-05
- 2022-07
- 2022-09
- 2024-03

No routing/model switching authorized.


### 18.18 Error severity V3 — APE 2.5% / 3.0% BANDS BINDING

Authority:
- `gold_axis_2026/GOLD_MONTHLY_CHHHO_ERROR_SEVERITY_V3_AUTHORITY_2026-09-30.md`
- authority commit: `4b005a86c1dbfdae5f3e6979d097b1a7ffdc650d`

Execution:
- workflow: `Gold Monthly ChHHO Error Severity V3`
- run: **36702767607**
- artifact: **11090497943**
- code commit: `bcbcc59eedd5f5583dd482916c5c87b600c01a1f`
- workflow commit: `9f9e7dd903cf1ae0635bec6f6e8e8e09a95162e8`
- result report: `gold_axis_2026/GOLD_MONTHLY_CHHHO_ERROR_SEVERITY_V3_RESULT_2026-09-30.md`
- report commit: `e7fd49fe522049232d1f96882bb3199c85b9ec18`
- scientific gate: **PASS**

#### Binding primary severity metric

Because the requested concept is percentage error, the alarm-severity metric is **APE**:

- NORMAL: APE < **2.50%**
- MEDIUM: **2.50% <= APE < 3.00%**
- HIGH: APE >= **3.00%**

Absolute log-return error is retained as a robustness check only.

Project model evaluation is unchanged:
- ΣAE remains the primary economic/model-selection metric;
- direction remains co-primary;
- alarm severity is separate.

#### Severity counts — 58 usable targets

- NORMAL: **34**
- MEDIUM: **7**
- HIGH: **17**

HIGH:
- 2021-12
- 2022-05
- 2022-07
- 2022-09
- 2022-11
- 2023-01
- 2023-08
- 2024-03
- 2024-11
- 2025-02
- 2025-03
- 2025-09
- 2025-10
- 2025-11
- 2026-01
- 2026-06
- 2026-08

MEDIUM:
- 2022-01
- 2022-02
- 2024-04
- 2024-07
- 2025-01
- 2025-05
- 2026-03

#### APE vs return-error band disagreements

Only two:
- 2024-07: APE 2.96117% = MEDIUM; return error 3.00590pp = HIGH.
- 2026-03: APE 2.99874% = MEDIUM; return error 3.04462pp = HIGH.

APE classification is binding.

#### A/B/C/D/H HIGH-error coverage

DEV:
- HIGH 8
- hits 4
- recall 50%
- hits: 2022-11, 2023-01, 2023-08, 2024-11
- misses: 2022-05, 2022-07, 2022-09, 2024-03

2025:
- HIGH 5
- hits 4
- descriptive recall 80%
- miss: 2025-11

2026 Jan-Aug:
- HIGH 3
- hits 0
- descriptive recall 0%
- misses: 2026-01, 2026-06, 2026-08

All usable:
- HIGH 17
- A/B/C/D/H hits 9
- misses 8
- false alarms relative to HIGH 10
- precision 47.4%
- recall 52.9%

These remain descriptive mechanism-coverage figures, not production alarm performance.

#### Mechanism updates under APE HIGH

- **A:** HIGH hits 2022-11, 2023-08, 2025-09.
- **B:** HIGH hits 2023-01, 2025-03.
- **C:** 2024-07 APE 2.96117% -> MEDIUM, therefore C is not a HIGH-error hit.
- **D:** 2024-11 remains HIGH.
- **H:** HIGH hits 2021-12, 2025-02, 2025-10. 2024-07 and 2026-03 are MEDIUM under APE. H remains warning-only.

#### MEDIUM coverage

MEDIUM targets:
- 2022-01
- 2022-02
- 2024-04
- 2024-07
- 2025-01
- 2025-05
- 2026-03

A/B/C/D/H identifies:
- 2024-04
- 2024-07
- 2026-03

MEDIUM misses:
- 2022-01
- 2022-02
- 2025-01
- 2025-05

#### MEDIUM+HIGH elevated error

All usable:
- elevated 24
- A/B/C/D/H hits 12
- recall 50%
- precision 63.2%

#### Remaining HIGH misses after A/B/C/D/H

- 2022-05
- 2022-07
- 2022-09
- 2024-03
- 2025-11
- 2026-01
- 2026-06
- 2026-08

Descriptor coverage:
- 2025-11: E + GVZ
- 2026-01: E + GVZ
- 2026-06: GVZ + OI compression + FLOW_2OF4
- 2026-08: G + GVZ + OI compression + FLOW_2OF4

No fixed candidate descriptor:
- 2022-05
- 2022-07
- 2022-09
- 2024-03

No routing/model switching authorized.


### 18.19 ETF anomaly/dynamic regime audit — STATIC REJECTED / DYNAMIC SIGNAL FOUND

Official daily sources:
- GLD: SPDR Gold Shares Historical Archive (daily Tonnes of Gold + Daily Share Volume)
- IAU: iShares Gold Trust Historical data (daily Shares Outstanding)

Source-inspection workflow:
- `Gold Monthly ETF Daily Source Inspect V1`
- successful source-format run: **36703826210**
- GLD archive coverage: 2004-11..2026-09
- IAU historical coverage: 2005-01..2026-09
- official daily fund data are eligible as origin-known inputs.

#### V1 single-month anomaly screen

Authority:
- `GOLD_MONTHLY_CHHHO_ETF_ANOMALY_SCREEN_V1_AUTHORITY_2026-09-30.md`
- authority commit: `c1e440496b60444bbdb3dcf7ddbd86a1cba55388`

Execution:
- workflow: `Gold Monthly ChHHO ETF Anomaly Screen V1`
- run: **36704096595**
- artifact: **11091336563**
- head: `48098a09a74bfaee22caa93097cb714e390bdf2d`
- scientific gate: **PASS**

Calibration: 2010-01..2020-12 only.

Single-month Q10/Q90 result:
- 2022-05 / origin 2022-04: 0 static ETF anomalies
- 2022-07 / origin 2022-06: 0
- 2022-09 / origin 2022-08: 0
- 2024-03 / origin 2024-02: 0

ETF_STRESS_2PLUS across 58 usable targets:
- events 3
- HIGH APE hits 0
- false alarms 3

Binding interpretation:
**single-month ETF extremity is rejected as the explanation for the four core HIGH-error misses.**

#### V2 dynamic ETF regime screen

Authority:
- `GOLD_MONTHLY_CHHHO_ETF_DYNAMIC_REGIME_V2_AUTHORITY_2026-09-30.md`
- authority commit: `e85f36caf84130da833904d18864875e144520fb`

Execution:
- workflow: `Gold Monthly ChHHO ETF Dynamic Regime V2`
- run: **36704354365**
- artifact: **11090919621**
- code commit: `f7072974ea99f4113d77522aaa33011fcf6ab414`
- workflow commit: `0bf83b9129674d1db4c991b2220ebf757bf31510`
- result report: `GOLD_MONTHLY_CHHHO_ETF_ANOMALY_DYNAMIC_RESULT_2026-09-30.md`
- result commit: `742c9769295511ce63e0b6999e09c45f664bb18b`
- scientific gate: **PASS**

Frozen 2010-2020 dynamic thresholds:
- combined-flow month-to-month deterioration Q10 = **-4.2816pp**
- 3m cumulative combined flow Q10 = **-6.1704%**
- 6m cumulative combined flow Q10 = **-10.3011%**
- combined outflow-streak Q90 = **3.9 months** (operationally 4)
- simultaneous GLD+IAU outflow-streak Q90 = **2 months**

Core HIGH-error findings:

**2022-05 / origin 2022-04**
- GLD +0.285%, IAU +0.744%, combined +0.514%.
- FLOW_DELTA1 = -4.3673pp, below historical Q10.
- **I1 ETF FLOW DETERIORATION = TRUE.**
- WGC later reported April global inflows +43t, 77% below March's exceptional inflow.

**2022-07 / origin 2022-06**
- GLD -1.690%, IAU -1.674%.
- simultaneous outflow streak = 2 months.
- **I2 ETF REDEMPTION PERSISTENCE = TRUE.**
- WGC later described June as second consecutive global outflow month.

**2022-09 / origin 2022-08**
- GLD -3.231%, IAU -1.008%, combined -2.120%.
- simultaneous GLD+IAU outflow streak = 4 months.
- combined outflow streak = 4 months.
- 3m cumulative flow = -6.794%.
- flags: **I2 TRUE + outflow-streak Q90 + 3m-flow Q10**.
- WGC later described August as fourth consecutive global outflow month.
- cross-model authority: only 1/16 competitive models put 2022-09 in own worst-8; 8/15 alternatives beat ChHHO; best alternative AE 41.32 vs ChHHO 58.98. This is not a shared-hard month under the prior rank test.

**2024-03 / origin 2024-02**
- GLD -3.318%, IAU -1.564%.
- simultaneous outflow streak = 2 months.
- **I2 ETF REDEMPTION PERSISTENCE = TRUE.**
- WGC later described February as ninth consecutive global outflow month.
- cross-model authority classifies 2024-03 SHARED-HARD (16/16).

Dynamic candidate statistics:

**I1 ETF FLOW DETERIORATION**
- frozen rule: FLOW_DELTA1 <= 2010-2020 Q10.
- events 2
- HIGH APE hits 1 (2022-05)
- false alarms 1 (2026-04)
- status: rare candidate warning.

**I2 ETF REDEMPTION PERSISTENCE**
- frozen rule: GLD and IAU both contract for at least historical Q90 persistence length = 2 months.
- events 12
- HIGH APE hits 5
- false alarms 7
- precision 41.7%
- HIGH recall 29.4%
- HIGH hits: 2022-07, 2022-09, 2022-11, 2023-08, 2024-03.
- status: promising regime warning, not hard alarm.

Other dynamic ETF signals:
- 3m combined-flow Q10: events 6, HIGH hits 2 (2022-09, 2022-11), precision 33.3%.
- 4m combined-outflow streak: events 7, HIGH hits 2 (2022-09, 2022-11), precision 28.6%.

Binding interpretation:
- Static ETF anomaly hypothesis = rejected.
- Dynamic ETF transition/persistence hypothesis = **supported as exploratory mechanism**.
- Descriptively, all four previously unexplained core HIGH-error targets fall into one of two independently frozen dynamic states:
  - 2022-05 -> I1 deterioration
  - 2022-07 / 2022-09 / 2024-03 -> I2 redemption persistence.
- Do **not** combine I1 OR I2 into a post-hoc hard alarm without untouched validation.
- I1/I2 remain warning candidates.
- No target-month ETF data.
- WGC monthly reports are corroboration only, not predictor inputs.
- No routing/model switching authorized.


### 18.20 ETF I1/I2 historical recurrence — I2 HISTORICALLY SUPPORTED / REGIME-DEPENDENT

Historical recurrence authority:
- `GOLD_MONTHLY_CHHHO_ETF_I1_I2_HISTORICAL_RECURRENCE_V1_AUTHORITY_2026-09-30.md`
- authority commit: `4119c164e763680da65b8b6ca477b5eafa7fc89d`

Execution:
- workflow: `Gold Monthly ETF I1 I2 Historical Recurrence V1`
- run: **36705282325**
- artifact: **11091154474**
- code commit: `e9268fac4d823fbbaf9ad44f0e0c582f7fe6a9f8`
- workflow commit: `001b329935018456bb566c85df8715876daed61c`
- scientific gate: **PASS**

#### I1 historical recurrence

2010-2020:
- events 14
- next-month mean absolute GLD move 4.03pp vs 3.62pp non-event
- ratio 1.11x; bootstrap ratio CI 0.75x..1.57x
- MOVE_3 64.3% vs 50.0%, RR 1.29x, Fisher p 0.234
- MOVE_5 28.6% vs 29.7%, RR 0.96x, Fisher p 0.641

Binding interpretation:
**I1 is not historically robust as a general storm/high-movement signal.**
Keep only as a candidate ETF-demand-transition warning; it specifically explains the 2022-05 origin state.

#### I2 raw historical recurrence

Frozen state:
- GLD and IAU both contract for >=2 consecutive months.

2010-2020 raw active months:
- events 21
- next-month mean absolute GLD move 4.94pp vs 3.43pp non-event
- ratio 1.44x; bootstrap ratio CI 1.08x..1.88x
- MOVE_3 76.2% vs 46.8%, RR 1.63x, Fisher p 0.0118
- MOVE_5 57.1% vs 24.3%, RR 2.35x, Fisher p 0.00383

Because long redemption runs create serial dependence, this raw-month result required a de-clustered episode audit before interpretation.

#### I2 episode-entry robustness

Authority:
- `GOLD_MONTHLY_ETF_I2_EPISODE_ROBUSTNESS_V1_AUTHORITY_2026-09-30.md`
- authority commit: `6d432dc1e373697bca3142630346c7b4724164d8`

Execution:
- workflow: `Gold Monthly ETF I2 Episode Robustness V1`
- run: **36705483191**
- artifact: **11091313948**
- code commit: `7f2b4093812f016a7aa46592276aecc74ae9bafc`
- workflow commit: `dcd2bb9e3d98d47e37b7eac9da83975c9f8f5fca`
- scientific gate: **PASS**

2010-2020 independent I2 entries:
- 8 episodes: 2012-04, 2013-03, 2014-05, 2014-09, 2015-12, 2016-12, 2018-06, 2019-05
- mean next-month absolute GLD move: **5.52pp**
- non-entry mean: **3.55pp**
- mean uplift: **+1.97pp**
- mean ratio: **1.56x**
- bootstrap ratio CI: **1.14x..2.01x**

MOVE_3:
- I2 entry: **7/8 = 87.5%**
- non-entry: 49.2%
- RR **1.78x**
- Fisher p **0.0377**

MOVE_5:
- I2 entry: **6/8 = 75.0%**
- non-entry: 26.6%
- RR **2.82x**
- Fisher p **0.00839**

Therefore the historical I2 effect survives and strengthens after eliminating pseudo-replication from long streaks.

#### Transport stability

2021-2024 episode entries:
- 2021-03, 2021-08, 2022-06, 2023-07, 2024-02
- mean next-month absolute GLD move 3.80pp vs 3.27pp
- ratio 1.16x; bootstrap CI 0.62x..1.99x
- MOVE_3 60% vs 39.5%
- MOVE_5 20% vs 25.6%
- no stable large-move enrichment.

Thus the very strong 2010-2020 market-magnitude effect is **not stationary**.

However, the three episode entries inside canonical DEV all precede HIGH-APE ChHHO targets:
- origin 2022-06 -> target 2022-07 HIGH
- origin 2023-07 -> target 2023-08 HIGH
- origin 2024-02 -> target 2024-03 HIGH

2025-2026 Aug:
- only new I2 entry = origin 2026-06
- next-month GLD move +0.85pp
- target 2026-07 not HIGH APE
- explicit counterexample to universal alarm interpretation.

#### Core four relation

- 2022-05 / origin 2022-04 -> I1 deterioration; next GLD move -3.32pp; I1 historical support weak.
- 2022-07 / origin 2022-06 -> I2 episode entry; ChHHO HIGH APE.
- 2022-09 / origin 2022-08 -> inside persistent I2 episode, 4-month simultaneous redemption + 3m Q10 flow stress; ChHHO HIGH APE.
- 2024-03 / origin 2024-02 -> I2 episode entry; next GLD move +8.31pp; ChHHO HIGH APE.

Binding status:
- **I1 = candidate transition warning only.**
- **I2 = HISTORICALLY SUPPORTED, REGIME-DEPENDENT ETF RISK WARNING.**
- I2 is stronger than a purely post-hoc descriptor but is not a universal hard ChHHO-error alarm.
- No I1 OR I2 composite rule authorized.
- No routing/model switching authorized.

Full result:
- `GOLD_MONTHLY_ETF_I1_I2_HISTORICAL_RECURRENCE_RESULT_2026-09-30.md`
- report commit: `00bc2389b36743113689409ee58164eaaa8f91df`


### 18.21 WGC T1 early-month ETF alarm backtest — V4 BINDING / PASS

Objective:
- Keep the month-end ChHHO forecast unchanged.
- Test whether the official WGC monthly gold-ETF report, published during the first days of the target month, adds an **alarm-only T1 warning channel**.

Authority:
- `gold_axis_2026/GOLD_MONTHLY_WGC_T1_ETF_ALARM_BACKTEST_V4_AUTHORITY_2026-09-30.md`
- authority commit: `b57e602f2717143dd633fdb0300c98d64024eb8a`

Execution:
- workflow: `Gold Monthly WGC T1 ETF Alarm Backtest V4`
- run: **36708826992**
- artifact: **11093192454**
- code commit: `32489decb6f33bff14b33fd0d9770617da9a0bf5`
- workflow commit: `75f31ba6cfc1814a80376bb1924ba7c68ec8fa72`
- artifact digest: `sha256:58f418f5dbb60202810f1da19f9fc79aea31c2db892d566fb9a01dbdb8f1d984`
- result report: `gold_axis_2026/GOLD_MONTHLY_WGC_T1_ETF_ALARM_BACKTEST_V4_RESULT_2026-09-30.md`
- result commit: `61e207159a8e2bf5e6856f2d3feb28cff8f28742`
- scientific gate: **PASS**

#### Supersession / parser governance

- WGC T1 V1-V3 numerical/parser performance claims are **non-binding** because their completeness gates failed.
- V4 is the first binding T1 performance result.
- Binding evaluation window: 2021-11..2026-08, **58/58 rows complete**.
- No missing evaluation month.
- No publication-month mismatch.
- No report-data-month mismatch.
- Exactly one pre-authorized manual official-source override:
  - target 2021-12 / data month 2021-11
  - WGC report published 7 Dec 2021
  - global direction INFLOW
  - previous Oct 2021 report direction OUTFLOW
  - therefore R2_WGC FALSE.

#### Standardized T1 rule

**R2_WGC = current WGC monthly report says GLOBAL OUTFLOW AND immediately previous WGC monthly report also says GLOBAL OUTFLOW.**

- No numeric tonnage threshold.
- No forecast modification.
- No target-month market data other than the arriving official report itself.
- No routing/model switching.

TIMELY_T1:
- publication occurs in target month on calendar day <=10.

All R2_WGC events in the evaluation are timely.

#### R2_WGC standalone performance

Across 58 usable ChHHO targets:
- R2 events: **23**
- HIGH APE months: **17**
- HIGH hits: **6**
- HIGH precision: **26.1%**
- HIGH recall: **35.3%**

HIGH hit targets:
- 2022-07
- 2022-09
- 2022-11
- 2023-01
- 2023-08
- 2024-03

MEDIUM hits:
- 2022-02
- 2024-04

MEDIUM+HIGH:
- elevated months 24
- hits 8
- precision 34.8%
- recall 33.3%

Normal false-alarm targets:
- 2021-11
- 2022-08
- 2022-10
- 2022-12
- 2023-02
- 2023-03
- 2023-04
- 2023-09
- 2023-10
- 2023-11
- 2023-12
- 2024-01
- 2024-02
- 2024-05
- 2026-07

Binding interpretation:
R2_WGC is **too noisy to be a hard alarm alone**, but it has meaningful incremental T0-miss coverage.

#### T0 + T1 HIGH-error coverage

T0 A/B/C/D/H:
- HIGH hits **9/17**
- recall **52.9%**

T1 R2_WGC:
- HIGH hits 6
- overlaps with T0: 2022-11, 2023-01, 2023-08
- **incremental T1 hits over T0: 3**
  - 2022-07
  - 2022-09
  - 2024-03

T0 + T1 union:
- HIGH hits **12/17**
- recall **70.6%**

Remaining standardized HIGH misses:
- 2022-05
- 2025-11
- 2026-01
- 2026-06
- 2026-08

#### Four-core audit

**2022-05**
- report published 6 May 2022
- April direction INFLOW; prior March INFLOW
- R2_WGC FALSE
- T0 A/B/C/D/H FALSE
- official report explicitly says April inflows were **77% lower than the previous month**
- this is visible T1 deterioration information but is **not** counted as a standardized R2 hit.

**2022-07**
- report 7 Jul 2022
- June OUTFLOW + May OUTFLOW
- R2_WGC TRUE
- T0 false
- standardized incremental T1 HIGH hit.

**2022-09**
- report 7 Sep 2022
- August OUTFLOW + July OUTFLOW
- R2_WGC TRUE
- T0 false
- standardized incremental T1 HIGH hit.

**2024-03**
- report 7 Mar 2024
- February OUTFLOW + January OUTFLOW
- R2_WGC TRUE
- T0 false
- standardized incremental T1 HIGH hit.

#### Binding decision

- Maintain **T0 month-end alarm channel** and separate **T1 early-month WGC report warning channel**.
- R2_WGC role = **warning**, not hard alarm.
- T1 improves descriptive HIGH-error coverage from 52.9% to 70.6% without modifying the forecast.
- 2022-05 requires a separately preregistered deterioration/slowdown rule before it can count as a standardized T1 alarm.
- No forecast correction authorized.
- No routing/model switching authorized.


### 18.22 Unified Alarm Matrix V1 — 58-MONTH CONSOLIDATION COMPLETE

Authority:
- `gold_axis_2026/GOLD_MONTHLY_UNIFIED_ALARM_MATRIX_V1_AUTHORITY_2026-09-30.md`
- authority commit: `195a9e13ae8144ad839c58660b23a22f981a7fce`

Execution:
- workflow: `Gold Monthly Unified Alarm Matrix V1`
- run: **36710435526**
- artifact: **11094306282**
- code commit: `e09338ba31b68a55f7509dbef920963678cfac07`
- workflow commit: `e6208e2039080ad36de1350361e3855ed0517265`
- artifact digest: `sha256:58fe779f3a564073697c109717949170c23ce772342f32ae20f9aff8eea6dac8`
- result report: `gold_axis_2026/GOLD_MONTHLY_UNIFIED_ALARM_MATRIX_V1_RESULT_2026-09-30.md`
- result commit: `fa867c84cc5fc07404a6b406e0f8c5288cc7e130`
- scientific gate: **PASS**

Frozen inputs:
- APE severity V3 artifact 11090497943
- ETF dynamic regime V2 artifact 11090919621
- WGC T1 V4 artifact 11093192454

Outputs:
- JSON complete matrix
- CSV complete matrix
- Markdown complete matrix

#### Binding matrix columns

58 targets 2021-11..2026-08:
- APE + NORMAL/MEDIUM/HIGH
- A
- B
- C
- D
- E
- G
- H
- I1
- I2
- T1_WGC
- T1 publication date/timeliness
- active signal list

Signal statuses remain distinct:
- A selective T0 alarm candidate
- B warning-only
- C medium-error/low-event warning
- D rare HIGH hit
- E discovery-period/unvalidated
- G high-movement regime warning
- H CFTC positioning warning
- I1 ETF transition warning candidate
- I2 historically supported regime warning
- T1_WGC early-month report warning

No signal is deleted merely because it is not a hard alarm.

#### HIGH-error signal map

17 HIGH APE targets:

- 2021-12 — H
- 2022-05 — I1
- 2022-07 — I2 + T1_WGC
- 2022-09 — I2 + T1_WGC
- 2022-11 — A + I2 + T1_WGC
- 2023-01 — B + T1_WGC
- 2023-08 — A + I2 + T1_WGC
- 2024-03 — I2 + T1_WGC
- 2024-11 — D
- 2025-02 — H
- 2025-03 — B
- 2025-09 — A
- 2025-10 — H
- 2025-11 — E
- 2026-01 — E
- **2026-06 — NO CURRENT SIGNAL**
- 2026-08 — G

#### Blind spots by evidence layer

Standard T0 A/B/C/D/H misses:
- 2022-05
- 2022-07
- 2022-09
- 2024-03
- 2025-11
- 2026-01
- 2026-06
- 2026-08

Standard T0 HIGH coverage:
- 9/17 = **52.9%**

All visible T0 A/B/C/D/E/G/H/I1/I2:
- only HIGH month with no signal = **2026-06**
- descriptive visibility = **16/17 = 94.1%**

This 94.1% is NOT hard-alarm validation because E/G/I have different evidence statuses and include discovery-period/regime warnings.

All visible T0 + T1:
- still only blind HIGH = **2026-06**
- T1 confirms/duplicates several I2 regimes and provides official early-month timing evidence.

#### Signal statistics vs HIGH APE

- A: events 5 / HIGH 3 / MEDIUM 0 / normal false 2 / HIGH precision 60.0%
- B: 4 / 2 / 0 / 2 / 50.0%
- C: 1 / 0 / 1 / 0 / HIGH precision 0%; medium-warning role
- D: 1 / 1 / 0 / 0 / 100% single-event
- E: 4 / 2 / 2 / 0 / 50.0%; discovery-period/unvalidated
- G: 3 / 1 / 0 / 2 / 33.3%; regime-warning role
- H: 9 / 3 / 3 / 3 / 33.3%; CFTC positioning warning
- I1: 2 / 1 / 0 / 1 / 50.0%; transition warning candidate
- I2: 12 / 5 / 0 / 7 / 41.7%; historically supported regime warning
- T1_WGC: 23 / 6 / 2 / 15 / 26.1%; noisy standalone, early-month confirmation

#### MEDIUM rows

- 2022-01 — no signal
- 2022-02 — T1_WGC
- 2024-04 — H + T1_WGC
- 2024-07 — C + H
- 2025-01 — no signal
- 2025-05 — E
- 2026-03 — E + H

#### Binding next research priority

**2026-06** is the only HIGH APE month with no currently frozen A/B/C/D/E/G/H/I1/I2/T1_WGC signal.

Do not loosen thresholds merely to catch 2026-06.

No forecast correction authorized.
No routing/model switching authorized.


### 18.23 Unified Alarm Matrix V2 — FALSE-CALL ACCOUNTING BINDING

Authority:
- `gold_axis_2026/GOLD_MONTHLY_UNIFIED_ALARM_MATRIX_V2_FALSE_CALL_AUTHORITY_2026-09-30.md`
- authority commit: `76beeaaeec3d833e78f8a0df6431ed9369eba66a`

Execution:
- workflow: `Gold Monthly Unified Alarm Matrix V2 False Call`
- run: **36711349670**
- artifact: **11093903747**
- code commit: `37994b3f08676c6bc20e5d9fd81ac07a16051132`
- workflow commit: `028ddbd75bf5c19f321d54b4ad9d2bc09d1b1a14`
- artifact digest: `sha256:995f216b3a44d4903b214cfcb7f64335dda70f73e2f6e56f67e7a821744eb949`
- result report: `gold_axis_2026/GOLD_MONTHLY_UNIFIED_ALARM_MATRIX_V2_FALSE_CALL_RESULT_2026-09-30.md`
- result commit: `54bcb9a60dd1f74113fec636a84c545d27d60f87`
- scientific gate: **PASS**

#### Binding outcome accounting

APE severity remains:
- NORMAL <2.5%
- MEDIUM 2.5%..<3.0%
- HIGH >=3.0%

For any active signal:
- HIGH -> HIGH HIT
- MEDIUM -> MEDIUM HIT
- NORMAL -> FALSE CALL

MEDIUM is not a false call.

From this checkpoint onward, every alarm-performance report must show:
- HIGH hits
- MEDIUM hits
- NORMAL false calls
- useful-call rate
- false-call rate
- HIGH recall

Recall alone is insufficient.

#### Individual false-call burden

- A: 5 events / 3 HIGH / 0 MEDIUM / **2 false** / false-call rate **40.0%**
  - false: 2021-11, 2025-12
- B: 4 / 2 / 0 / **2 false** / **50.0%**
  - false: 2023-02, 2023-05
- C: 1 / 0 / 1 / **0 false**
- D: 1 / 1 / 0 / **0 false**
- E: 4 / 2 / 2 / **0 false observed**
  - caution: discovery-period/unvalidated; zero observed false does not equal independent validation
- G: 3 / 1 / 0 / **2 false** / **66.7%**
  - false: 2022-08, 2026-07
- H: 9 / 3 / 3 / **3 false** / **33.3%**
  - false: 2023-03, 2023-09, 2024-08
- I1: 2 / 1 / 0 / **1 false** / **50.0%**
  - false: 2026-04
- I2: 12 / 5 / 0 / **7 false** / **58.3%**
  - false: 2022-08, 2022-10, 2022-12, 2023-09, 2023-10, 2023-11, 2026-07
- T1_WGC: 23 / 6 / 2 / **15 false** / **65.2%**
  - false: 2021-11, 2022-08, 2022-10, 2022-12, 2023-02, 2023-03, 2023-04, 2023-09, 2023-10, 2023-11, 2023-12, 2024-01, 2024-02, 2024-05, 2026-07

#### Union quality

**T0_STANDARD = A OR B OR C OR D OR H**
- events 19
- HIGH 9
- MEDIUM 3
- NORMAL false 7
- useful-call rate **63.2%**
- false-call rate **36.8%**
- HIGH recall **52.9%**

False:
- 2021-11
- 2023-02
- 2023-03
- 2023-05
- 2023-09
- 2024-08
- 2025-12

**T0_ALL_VISIBLE = A/B/C/D/E/G/H/I1/I2**
- events 34
- HIGH 16
- MEDIUM 4
- NORMAL false 14
- useful-call rate **58.8%**
- false-call rate **41.2%**
- HIGH recall **94.1%**

The high visibility is not acceptable as a single production alarm because it produces 14 normal-month false calls.

**T0_PLUS_T1_STANDARD**
- events 34
- HIGH 12
- MEDIUM 4
- NORMAL false 18
- useful-call rate **47.1%**
- false-call rate **52.9%**
- HIGH recall **70.6%**

T1 improves coverage but sharply increases false-call burden when treated as an equal hard alarm.

**ANY_VISIBLE**
- events 40
- HIGH 16
- MEDIUM 5
- NORMAL false **19**
- useful-call rate **52.5%**
- false-call rate **47.5%**
- HIGH recall **94.1%**

Binding interpretation:
**ANY_VISIBLE is a research visibility map, not a production alarm.**

#### Multi-signal false calls

Even multiple simultaneous warnings can be false:

- 2021-11 — A + T1_WGC — APE 0.462%
- 2022-08 — G + I2 + T1_WGC — 2.031%
- 2022-10 — I2 + T1_WGC — 0.193%
- 2022-12 — I2 + T1_WGC — 1.755%
- 2023-02 — B + T1_WGC — 1.566%
- 2023-03 — H + T1_WGC — 2.199%
- 2023-09 — H + I2 + T1_WGC — 0.281%
- 2023-10 — I2 + T1_WGC — 1.853%
- 2023-11 — I2 + T1_WGC — 0.624%
- 2026-07 — G + I2 + T1_WGC — 2.030%

Therefore signal-count voting cannot be assumed to improve precision.

No new Boolean selection rule was optimized.
No thresholds were retuned.
No forecast correction or routing/model switching authorized.


### 18.24 False-call suppressor screen — CROSS-MODEL SAFE VETO CANDIDATE

Authority:
- `gold_axis_2026/GOLD_MONTHLY_ALARM_FALSE_CALL_SUPPRESSOR_SCREEN_V1_AUTHORITY_2026-09-30.md`
- authority commit: `fc4375f3ff2efef48c7a686c21dfbae57d7d3016`

Execution:
- workflow: `Gold Monthly Alarm False Call Suppressor Screen V1`
- run: **36712803237**
- code commit: `3290b8eb95a3f90277573d614bdd7e2dcd8b5750`
- workflow commit: `1fbd3cda23e2dcc6233e421d4a7d3c958e6c9ca4`
- result report: `gold_axis_2026/GOLD_MONTHLY_ALARM_FALSE_CALL_SUPPRESSOR_SCREEN_V1_RESULT_2026-09-30.md`
- result commit: `95519c954bddbe74fff31d3d6e51c8c242626930`
- scientific gate: **PASS**

Scope:
- DEV 2022-04..2024-12 only.
- frozen 16-model competitive cross-model pool.
- suppressor features are origin-known forecasts only.
- no actual target price enters veto features.
- expanding prior-only feature thresholds, minimum prior history 6 origins.

#### Existing risk alarms cannot act as opposite alarms

A/B/C/D/E/G/H/I1/I2/T1 are all risk-oriented.
No current channel is a principled SAFE / anti-alarm.

Simple cross-family or signal-count confirmation is not a reliable suppressor:
- 2022-08: G + I2 + T1, APE 2.031% NORMAL
- 2023-09: H + I2 + T1, APE 0.281% NORMAL
- 2026-07: G + I2 + T1, APE 2.030% NORMAL

Therefore veto research moved to origin-known cross-model forecast consensus.

#### Consensus feature separation

Among veto-eligible ANY_VISIBLE alarm rows:

HIGH:
- median forecast dispersion 1.241%
- median ChHHO deviation from competitive median 0.999%
- median direction agreement 75.0%

MEDIUM:
- dispersion 1.147%
- ChHHO deviation 0.786%
- direction agreement 81.25%

NORMAL false calls:
- dispersion **0.951%**
- ChHHO deviation **0.537%**
- direction agreement **81.25%**

False calls tend to occur with tighter forecast clustering and a more consensus-central ChHHO forecast, although distributions overlap.

#### Candidate veto decisions

**V1_TIGHT_CENTRAL**
- rejected.
- suppresses true HIGH 2024-03 (APE 6.098%) while removing no false call in ANY_VISIBLE comparison.

**V2_STRONG_DIRECTION_CONSENSUS**
Frozen exploratory definition:
- >=80% competitive models agree with ChHHO direction vs RW; AND
- forecast dispersion <= expanding prior-history median.

ANY_VISIBLE DEV:
- before: 25 events / 8 HIGH / 2 MEDIUM / 15 false
- V2 suppresses three NORMAL false calls:
  - 2022-12, APE 1.755%, I2 + T1
  - 2024-02, APE 1.546%, T1
  - 2024-08, APE 1.796%, H
- incorrectly suppressed HIGH: **0**
- incorrectly suppressed MEDIUM: **0**
- after: 22 events / 8 HIGH / 2 MEDIUM / 12 false
- false-call rate 60.0% -> **54.5%**

T0_ALL_VISIBLE:
- suppresses 2022-12 and 2024-08, both NORMAL
- HIGH lost 0 / MEDIUM lost 0
- false-call rate 50.0% -> **44.4%**

T0_STANDARD:
- suppresses 2024-08 only
- HIGH lost 0 / MEDIUM lost 0
- false-call rate 45.5% -> **40.0%**

Status:
**PROMISING EXPLORATORY SAFE-VETO CANDIDATE.**
Not production-authorized.

**V3_CENTRAL_ONLY**
- rejected.
- suppresses true HIGH 2024-11 (APE 4.494%) and MEDIUM 2024-07 (APE 2.961%).

#### Binding next requirement

Validate V2 unchanged on 2025/2026 using only models with frozen transport predictions.
Do not retune:
- 80% direction agreement;
- expanding-median dispersion condition.

No production veto authorized.
No forecast correction.
No routing/model switching.
