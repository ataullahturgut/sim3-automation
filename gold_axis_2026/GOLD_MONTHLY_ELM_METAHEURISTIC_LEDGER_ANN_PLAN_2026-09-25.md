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
