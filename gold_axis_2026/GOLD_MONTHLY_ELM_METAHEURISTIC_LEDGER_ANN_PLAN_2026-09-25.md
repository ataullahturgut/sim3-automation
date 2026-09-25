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

- [ ] Vanilla ANN baseline
- [ ] PSO-ANN
- [ ] GA-ANN
- [ ] DE-ANN
- [ ] ABC-ANN
- [ ] SSA-ANN
- [ ] GWO-ANN
- [ ] WOA-ANN
- [ ] HHO-ANN
- [ ] ACO-ANN
- [ ] Bat-ANN
- [ ] FA-ANN
- [ ] MFO-ANN
- [ ] FPA-ANN
- [ ] CS-ANN
- [ ] SCA-ANN
- [ ] Salp-ANN
- [ ] SMA-ANN
- [ ] GOA-ANN
- [ ] ALO-ANN
- [ ] TLBO-ANN
- [ ] JAYA-ANN
- [ ] HGS-ANN
- [ ] ChOA-ANN
- [ ] HGSO-ANN
- [ ] AOA-ANN
- [ ] CPA-ANN
- [ ] Krill Herd-ANN
- [ ] Crow Search-ANN

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
