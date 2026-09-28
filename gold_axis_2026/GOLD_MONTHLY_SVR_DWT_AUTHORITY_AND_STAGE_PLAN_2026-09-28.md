# GOLD MONTHLY FORECAST — SVR / DWT-SVR AUTHORITY & STAGE PLAN

Date: 2026-09-28  
Status: **STAGE 0 COMPLETE / PRE-OUTCOME AUTHORITY FREEZE**  
Branch: `gold-midas-headswap-v1-20260925`

## 1. Scope

New family:
**SVR / DWT-SVR**

Objective:
- H=1 next-calendar-month average XAU/USD price.
- Forecast origin = previous completed calendar month-end.
- Primary prediction route = forecast next-month Gold log return, then reconstruct price from previous completed-month Gold average.

This family is distinct from the already-existing historical `VW_MIDAS_MSVR_SUCCESSOR_V1` identity:
- historical MSVR is a joint 4-output custom RBF multi-output support-vector-regression successor;
- this new family is a governed **single-output Gold epsilon-SVR / wavelet-SVR research line**;
- no historical MSVR result may be silently copied into the new SVR family;
- the historical MSVR implementation may be retained as a comparator/reference only if explicitly reconciled under the current DEV contract.

## 2. Binding project governance

- DEV selection/tuning authority: **2022-04..2024-12, n=33**.
- 2025: **FINAL LOCKED HOLDOUT**, unopened for this SVR family until final family freeze.
- 2026: **QUARANTINED / REPORTING ONLY**; must not tune, select, prune, weight, or rescue an SVR-family model.
- Random split: **PROHIBITED**.
- Evaluation: chronological / expanding-origin only.
- Database: **READ_ONLY**.
- Target-month actual: unavailable to feature construction, scaling, fitting, model selection, decomposition, optimizer fitness, and hyperparameter selection at its forecast origin.
- Primary selection metric: DEV cumulative reconstructed-price absolute error, `SigmaAE`.
- Complementary criteria: direction accuracy, MAE, RMSE, MAPE/WAPE, relative MAE vs random walk, yearly stability, worst month.
- No arbitrary composite score unless separately preregistered.
- Every stage must write method, exact parameterization, data/representation, chronology, metrics, scientific gate, decision, run/job/artifact/commit lineage to the family ledger.

## 3. Authority basis

### 3.1 Support Vector Regression authority

Canonical computational authority:
- Chang & Lin, LIBSVM.
- epsilon-SVR is a standard supported regression formulation.
- canonical kernel families include linear, polynomial, RBF and sigmoid.
- principal epsilon-SVR hyperparameters are `C` and `epsilon`; nonlinear kernels additionally depend on kernel parameters such as `gamma`.
- LIBSVM provides a regression parameter-search utility that searches `C`, `gamma`, and `epsilon`.
- scaling and parameter selection are explicitly treated as important in LIBSVM documentation.

Project decision:
- primary SVR formulation = **epsilon-SVR**.
- implementation target = LIBSVM-compatible `sklearn.svm.SVR`.
- canonical baseline kernels = **LINEAR** and **RBF**.
- polynomial/sigmoid kernels are controlled Stage-2 challengers, not broad-screen parents by default.
- target scaling is required because epsilon has target-scale meaning.

### 3.2 Gold-specific DWT-SVR authority

Primary gold-specific source:
- Marian Risse (2019), *Combining wavelet decomposition with machine learning to forecast gold returns*, International Journal of Forecasting 35(2), 601-615.
- DOI: 10.1016/j.ijforecast.2018.11.008.

Relevant mechanism:
- monthly gold-return forecasting;
- discrete/multiresolution wavelet decomposition applied to predictor series;
- decomposed time/frequency information supplied to SVR;
- out-of-sample statistical forecast evaluation;
- paper reports improved forecasting usefulness from frequency-decomposed predictors relative to undecomposed alternatives.

Secondary reconstruction evidence around the Risse setup:
- the Risse-style monthly framework is reported as decomposing predictor series into six wavelet details plus a smooth component;
- MODWT/MRA is repeatedly cited in financial forecasting work following Risse because it avoids dyadic-length restrictions and preserves alignment better than ordinary downsampled DWT.

Project decision:
- DWT-SVR line will be implemented as a **causal prefix-only multiresolution wavelet feature line**.
- global/full-series decomposition is **PROHIBITED**.
- a training row at historical target `t` must be generated from a prefix ending no later than the information available for `t`; future predictor values cannot be used to construct historical wavelet coefficients.
- the target-origin row may use predictor data available at the current completed origin only.
- decomposition must be recomputed moving-front/prefix-by-prefix or with an exactly equivalent causal filter.
- decomposition reconstruction/invariance and future-feature perturbation gates are mandatory.

### 3.3 Wavelet filter / level authority

Predeclared structural baseline:
- literature-style multiresolution decomposition with **up to six detail levels + one smooth component** where sample-length admissibility permits.
- a Haar/MODWT-style causal baseline is preferred for the first structural challenger because Haar is widely used in financial forecasting and supports clean scale interpretation.

Important evidence label:
- the exact original Risse wavelet-filter implementation cannot be fully independently reconstructed from the public text currently available in this repository.
- therefore an assertion that our Stage-5 implementation is an exact byte-for-byte Risse replication would be **NOT_PROVEN**.
- the project will call it a **Risse-motivated causal DWT/MODWT-SVR adaptation**, not an exact replication, unless later source evidence proves exact equivalence.

## 4. Frozen data contract for canonical SVR

Primary input representation entering Stage 1:
**CURRENT8**, already governed in the monthly project.

For each of Gold, Silver, Platinum, Palladium:
1. previous completed-month log return;
2. origin-month GPR-adaptive weighted daily log-return summary.

Total = 8 origin-safe predictors.

GPR:
- official point-in-time origin vintage;
- lagged availability rules retained;
- origin-safe normalization only.

Target:
- next-month **Gold log return** only for the canonical single-output SVR line.

Reconstruction:
`forecast_price(t) = actual_gold_price(t-1) * exp(predicted_gold_log_return(t))`.

Scaling:
- predictor scaler fitted on pre-target training rows only.
- target scaler fitted on pre-target Gold log returns only.
- canonical scaling = standardization using training-only mean/std.
- prediction is inverse-transformed before price reconstruction.
- any zero/near-zero feature standard deviation is guarded deterministically.

## 5. Stage plan — binding order

### Stage 0 — Authority / Protocol Freeze
**COMPLETE with this document.**

No model outcome was used to define this plan.

### Stage 1 — Canonical SVR baseline
Purpose: establish clean plain-SVR anchors before tuning.

Mandatory:
- LINEAR epsilon-SVR
- RBF epsilon-SVR

Canonical starting values on standardized data:
- C = 1.0
- epsilon = 0.1
- RBF gamma = `scale`
- shrinking = TRUE
- tolerance = 1e-3

Report:
- full DEV 33 origins;
- yearly 2022/2023/2024;
- SigmaAE, MAE, RMSE, MAPE, WAPE, relative MAE/RW, direction, worst month;
- scientific / chronology / finite-prediction gates.

No 2025/2026.

### Stage 2 — Controlled SVR ablations

#### Stage 2A — kernel ablation
Using the Stage-1 representation/scaling/target contract:
- LINEAR
- RBF
- POLY degree 2
- POLY degree 3
- SIGMOID

This stage is diagnostic/selection work on DEV only.

#### Stage 2B — representation ablation
Reuse already-governed origin-safe monthly representations from completed families where technically compatible:
- CURRENT8
- DAILY_SUMMARY12
- MIXED20
- RAW_LEVEL_LAGS8

No new post-outcome feature mining.

#### Stage 2C — formulation check
- epsilon-SVR remains primary.
- NuSVR may be tested as a secondary parameterization challenger.
- direct-price target is not opened automatically; LOGRET->price remains the authority target unless a separate pre-outcome authority note justifies a direct-price challenger.

Output:
- freeze one **META_PARENT_SVR** lane before any 32-metaheuristic outcomes.
- parent eligibility prioritizes DEV SigmaAE with direction/stability as complementary evidence.
- parent is expected to be LINEAR or RBF; polynomial/sigmoid are challengers but do not automatically become meta parents if numerically unstable.

### Stage 3 — deterministic hyperparameter refinement

#### Stage 3A — coarse chronological grid
For RBF-type parent:
- search C, epsilon, gamma.
For LINEAR parent:
- search C, epsilon.

Search is nested/chronological inside each outer DEV origin.

Initial broad parameter domains, defined on standardized data:
- `log2(C)`: [-8, 12]
- `log2(gamma)`: [-12, 4] for RBF
- `epsilon`: [0.01, 0.50]

The exact finite grid must be committed before Stage-3 outcomes.

#### Stage 3B — local refinement
- allowed only around the Stage-3A region;
- refinement rule/grid must be committed before Stage-3B outcomes;
- no 2025/2026.

At Stage-3 close:
- freeze the deterministic tuned SVR benchmark;
- freeze the exact continuous optimizer bounds to be used by every Stage-4 metaheuristic.

## 6. Stage 4 — mandatory 32/32 metaheuristic SVR screen

This is a user-directed parity requirement for the SVR family.

The broad screen is **NOT OPTIONAL** and may not be pruned because an early method looks weak or because of any 2025/2026 outcome.

Common rules:
- same frozen META_PARENT_SVR architecture;
- same frozen representation;
- same target/scaling;
- same continuous parameter bounds;
- same inner objective;
- same budget class;
- same deterministic seed policy/repeat count;
- same chronological outer DEV origins;
- no 2025/2026.

Optimization vector:
- if RBF parent: `log2(C), log2(gamma), epsilon`;
- if LINEAR parent: `log2(C), epsilon`.

Primary inner objective:
- mean absolute standardized Gold log-return error on a chronological validation tail using only pre-target rows.

Default fairness budget:
- population / agent count = 24 where applicable;
- generations / iterations = 45;
- 3 deterministic repeats;
- methods without direct population/generation semantics must be matched as closely as practical by objective-evaluation budget and documented.

Mandatory methods, 32/32:

1. PSO
2. GA
3. MPA
4. DE
5. ABC
6. SSA
7. GWO
8. WOA
9. HHO
10. ACO
11. Bat
12. FA
13. MFO
14. FPA
15. FA-FPA
16. CS
17. SCA
18. Salp
19. SMA
20. GOA
21. ALO
22. TLBO
23. JAYA
24. HGS
25. ChOA
26. HGSO
27. AOA
28. CPA
29. Krill Herd
30. Crow Search
31. DE-ABC
32. Multi-swarm

Vanilla/deterministic tuned SVR remains the 33rd reference identity in the broad-screen table.

### Frozen execution batches

Stage 4.1:
- PSO, GA, DE, MPA

Stage 4.2:
- ABC, SSA, GWO, WOA

Stage 4.3:
- HHO, ACO, Bat, FA

Stage 4.4:
- MFO, FPA, FA-FPA, CS

Stage 4.5:
- SCA, Salp, SMA, GOA

Stage 4.6:
- ALO, TLBO, JAYA, HGS

Stage 4.7:
- ChOA, HGSO, AOA, CPA

Stage 4.8:
- Krill Herd, Crow Search, DE-ABC, Multi-swarm

No Stage-4 parent selection until **all 32/32** methods have been executed/audited or a specific method is formally BLOCKED with documented technical reason.

## 7. Stage 5 — targeted refinement / hybrid SVR

Opened only after 32/32 broad-screen completion.

Purpose:
- mirror the controlled refinement logic used in completed ELM/ANN/RBFNN/ANFIS families;
- avoid arbitrary hundreds of optimizer cross-products.

Candidate classes:
- adaptive version of a retained optimizer;
- meta-optimizer tuning a retained optimizer;
- cooperative/hybrid optimizer;
- only a compact predeclared set based on DEV evidence and/or direct methodological authority.

2025/2026 cannot choose the refinements.

## 8. Stage 6 — DWT / MODWT-SVR structural line

### Stage 6A — causal decomposition engineering gate
Before scoring:
- prefix-only/moving-front decomposition;
- no global decomposition;
- exact target-origin information cutoff;
- reconstruction/invariance check;
- future-feature perturbation test;
- deterministic repeat test;
- sample-length admissibility for chosen levels;
- boundary policy documented.

### Stage 6B — wavelet structure ablation
Predeclared candidates:
- Haar/MODWT-style baseline;
- literature-authorized alternative wavelet families only if the authority note is committed before outcomes;
- level count up to six, subject to sample-length admissibility.

No post-outcome wavelet family mining.

### Stage 6C — frozen SVR on wavelet features
Compare:
- raw frozen SVR parent;
- Risse-motivated causal DWT/MODWT-SVR.

### Stage 6D — DWT-SVR refinement
Opened only if Stage 6C earns a predeclared DEV gate.
May include:
- hyperparameter refinement on the wavelet representation;
- a compact metaheuristic DWT-SVR refinement if justified.

The 32/32 broad metaheuristic obligation applies to the **plain SVR parent line**, not automatically to every wavelet configuration; otherwise the search would become an uncontrolled Cartesian explosion.

## 9. Stage 7 — controlled ensemble / complementarity

Open only if multiple retained SVR/DWT-SVR models exhibit genuine complementary errors/directions.

Order:
1. pool freeze before ensemble outcomes;
2. equal mean / median;
3. prequential inverse-error weighting;
4. only if justified: constrained simplex with strictly prior DEV rows;
5. only if justified and pre-frozen: shrinkage;
6. no arbitrary subset search;
7. no same-sample fitted weights promoted as honest evidence.

## 10. Stage 8 — final robustness

Mandatory:
- yearly 2022/2023/2024 metrics;
- month-by-month pairwise AE wins/ties;
- direction rescue/loss;
- worst-month removal;
- common leave-one-origin;
- stability dispersion;
- component leave-one-out for ensembles, diagnostic only;
- parameter stability for tuned/meta models;
- failure/pathological prediction audit.

Robustness is diagnostic unless an integrity gate fails; it must not trigger post-hoc model mining.

## 11. Stage 9 — final SVR-family freeze

Freeze before opening 2025:
- PRICE role;
- BALANCE/DIRECTION role if supported;
- exact model identity;
- representation;
- kernel;
- target/scaling;
- hyperparameters;
- DWT structure if applicable;
- ensemble pool/rule if applicable;
- all closed research lines.

## 12. Stage 10 — 2025 one-shot final holdout

Only after Stage 9 commit.

Report:
- all 12 months;
- actual, forecast, AE, RW, direction;
- SigmaAE, MAE, RMSE, MAPE/WAPE, relative MAE/RW, direction, worst month.

2025 result cannot:
- change model;
- change hyperparameters;
- select optimizer;
- select wavelet;
- change ensemble;
- reopen a rejected method.

After Stage 10:
**SVR / DWT-SVR FAMILY CLOSED.**

## 13. Execution safety / batching policy

The family will not be run as one monolithic workflow.

Default:
- small deterministic SVR stages may run together;
- kernel/representation ablations in modest batches;
- metaheuristics = frozen 4-method batches;
- adaptive/meta-on-meta/hybrid stages use smaller batches;
- DWT engineering is separated from DWT scoring;
- ensemble/freeze/holdout are separate gated stages.

If compute or scientific risk is high, batch size is reduced without changing the frozen candidate set.

## 14. Closed leakage / methodology hazards

Explicitly prohibited:
- random train/test split;
- global standardization;
- target-year feature fitting;
- full-series wavelet decomposition;
- decomposition of historical rows using later predictor observations;
- optimizing on reconstructed target-month actual;
- selecting methods using 2025 or 2026;
- selecting only successful metaheuristics and silently dropping failures;
- changing bounds after seeing an optimizer's outcome;
- same-sample ensemble fit reported as honest DEV;
- post-hoc switching based on 2025/2026.

## 15. Stage-0 decision

Authority evidence is sufficient to open the family.

Stage 0:
**PASS / COMPLETE.**

Authorized next execution:
**Stage 1 — Canonical LINEAR and RBF epsilon-SVR baselines on CURRENT8, DEV only.**

No Stage-1 result exists at the time of this freeze.

## 16. Kontrol ve Uyum Özeti

- Gold-specific SVR/DWT-SVR authority identified: PASS.
- Canonical epsilon-SVR formulation frozen: PASS.
- CURRENT8 primary input contract frozen: PASS.
- Training-only X/Y scaling frozen: PASS.
- LOGRET -> price reconstruction frozen: PASS.
- DEV 2022-04..2024-12 only for selection: PASS.
- 2025 locked until final freeze: PASS.
- 2026 selection/tuning exclusion: PASS.
- Random split: NONE.
- DB: READ_ONLY.
- 32/32 mandatory metaheuristic checklist recorded: PASS.
- 4-method batch plan recorded: PASS.
- Causal prefix-only DWT/MODWT requirement recorded: PASS.
- Full-series decomposition: PROHIBITED.
- Exact original Risse wavelet implementation equivalence: NOT_PROVEN.
- Next stage: Stage 1 canonical SVR baseline.
