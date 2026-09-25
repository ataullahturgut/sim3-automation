# GOLD MONTHLY FORECAST — ELM METAHEURISTIC LEDGER & ANN NEXT-PHASE PLAN

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
- [ ] FA-FPA-ANN
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
- [ ] Krill Herd-ANN
- [ ] Crow Search-ANN
- [ ] DE-ABC-ANN
- [ ] Multi-swarm ANN

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
