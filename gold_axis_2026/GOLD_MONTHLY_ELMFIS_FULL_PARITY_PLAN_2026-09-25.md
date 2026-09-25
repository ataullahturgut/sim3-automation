# GOLD MONTHLY FORECAST — ELMFIS FULL PARITY PROGRAM

**Date:** 2026-09-25  
**Repository:** ataullahturgut/sim3-automation  
**Branch:** gold-midas-headswap-v1-20260925  
**Status:** BINDING CHECKLIST

## 1. Objective and common authority

The forecasting target remains unchanged:
- H=1 next-calendar-month average XAU/USD price.
- Origin = previous completed month-end.
- Inputs = governed 8 origin-safe VW-MIDAS features.
- Multi-output learning = Gold/Silver/Platinum/Palladium returns jointly; Gold price is primary forecast.
- DEV = 2022-04..2024-12, n=33 and is the only tuning/model-selection authority.
- 2025 = retrospective transport reporting only.
- 2026 Jan-Jul = retrospective stress reporting only.
- No random train/test split.
- No target-month leakage.
- Database access = READ_ONLY.

### Active evaluation contract
Primary criteria:
1. cumulative absolute price error: `SUM_ABS_ERROR = Σ |forecast - actual|`;
2. monthly direction accuracy.

Supporting:
- MAE,
- MAPE/WAPE,
- RMSE,
- worst monthly absolute error,
- year-by-year stability,
- leave-one-origin sensitivity.

No arbitrary error+direction scalar score unless predeclared before results. Use Pareto/trade-off interpretation.

## 2. Canonical ELMFIS definition to freeze before optimization

The ELMFIS family is implemented as a first-order Takagi-Sugeno fuzzy inference system with ELM-style analytic consequent fitting.

Canonical baseline:
- inputs: 8 standardized VW-MIDAS features;
- fuzzy rules: 5;
- antecedent membership: bell/Gaussian form;
- rule firing: product AND across inputs, numerically normalized;
- consequent: first-order TSK linear consequent per rule;
- four outputs jointly;
- consequent coefficients solved analytically with ridge regularization;
- rule centers/spreads estimated from pre-target training history only;
- deterministic k-means rule initialization;
- target month excluded from all training/configuration.

This is a project adaptation of published ELM/FIS structures; it is not claimed as an exact code reproduction of any external paper.

## 3. ELMFIS Stage 0 — baseline / implementation authority

- [x] Implement canonical 5-rule ELMFIS baseline.
- [x] Determinism / compile / READ_ONLY / authority invariant checks.
- [x] Report DEV, 2025, 2026 rows and metrics.
- [x] Record SUM_ABS_ERROR + direction as primary metrics.
- [x] Freeze parameterization interface for metaheuristic parity.

**Gate:** no metaheuristic run before baseline/parameter vector is proven valid.

## 4. ELMFIS Stage 1 — full broad single/metaheuristic parity screen

The full 33-entry ELM/ANN broad screen is repeated for ELMFIS.

### Baseline + primitive/single optimizers
- [x] Vanilla ELMFIS
- [x] PSO-ELMFIS
- [x] GA-ELMFIS
- [x] MPA-ELMFIS
- [x] DE-ELMFIS
- [x] ABC-ELMFIS
- [x] SSA-ELMFIS
- [x] GWO-ELMFIS
- [x] WOA-ELMFIS
- [x] HHO-ELMFIS
- [x] ACO-ELMFIS
- [x] Bat-ELMFIS
- [x] FA-ELMFIS
- [x] MFO-ELMFIS
- [x] FPA-ELMFIS
- [x] CS-ELMFIS
- [x] SCA-ELMFIS
- [x] Salp-ELMFIS
- [x] SMA-ELMFIS
- [x] GOA-ELMFIS
- [x] ALO-ELMFIS
- [x] TLBO-ELMFIS
- [x] JAYA-ELMFIS
- [x] HGS-ELMFIS
- [x] ChOA-ELMFIS
- [x] HGSO-ELMFIS
- [x] AOA-ELMFIS
- [x] CPA-ELMFIS
- [x] Krill Herd-ELMFIS
- [ ] Crow Search / CSA-ELMFIS

### Broad-screen hybrid/parity entries
- [x] FA-FPA-ELMFIS
- [ ] DE-ABC-ELMFIS
- [ ] Multi-swarm ELMFIS

Total Stage-1 parity entries: **33 including Vanilla**.

### Optimization scope
For parity optimization, metaheuristics optimize ELMFIS antecedent parameters only:
- rule centers;
- positive rule spreads, represented in unconstrained/log form.

TSK consequent parameters are solved analytically on the relevant training history. This mirrors the ELM principle of searching nonlinear/hidden parameters while solving output parameters analytically.

## 5. ELMFIS Stage 2 — DEV-only filtering and parent freeze

All 33 Stage-1 candidates are evaluated on DEV only.

Primary selection plane:
- SUM_ABS_ERROR lower is better;
- direction accuracy higher is better.

Additional diagnostics:
- yearly 2022/2023/2024 SUM_ABS_ERROR;
- yearly direction;
- worst-month absolute error;
- relative error vs RW;
- repeat validation stability;
- signed-error correlation / complementarity.

Output:
- DEV Pareto frontier;
- price-error leader;
- direction leader;
- year-stability parent;
- refinement/meta-tuning parent;
- complementarity parent(s);
- reserve challengers.

No 2025/2026 result can promote or remove a parent.

## 6. ELMFIS Stage 3 — full refinement / hybrid parity

### 3A. Mandatory six refinements previously run in both ELM/ANN
- [ ] Adaptive PSO-ELMFIS
- [ ] TLBO-tuned PSO-ELMFIS
- [ ] DE-tuned PSO-ELMFIS
- [ ] Adaptive / Improved TLBO-ELMFIS
- [ ] Adaptive Crow Search-ELMFIS
- [ ] PSO-TLBO Hybrid ELMFIS

### 3B. ANN evidence-driven hybrids — run for family parity
- [ ] MPA+SCA Hybrid ELMFIS
- [ ] MPA+GA Hybrid ELMFIS
- [ ] MPA+CPA Hybrid ELMFIS

These are run even if the exact same parents are not Stage-2 winners, because the user requires direct method parity across ELM, ANN and ELMFIS. Their interpretation will still be DEV-only.

### 3C. ELMFIS-specific authority track
- [ ] CQCSA-ELMFIS

Rationale: Cluster-based quasi-oppositional Crow Search optimized ELMFIS has been published specifically for oil/gold price prediction. Crow Search/CSA parity is already in Stage 1; CQCSA is the family-specific optimized extension.

No further arbitrary optimizer cross-products after these predeclared methods.

## 7. ELMFIS Stage 4 — ensemble and robustness

Using only Stage-2/3 DEV evidence:
- [ ] role-diverse ELMFIS component pool freeze;
- [ ] simple equal-weight forecast ensemble;
- [ ] performance-weighted ensemble;
- [ ] constrained simplex / shrinkage audit;
- [ ] no arbitrary subset search;
- [ ] leave-one-origin sensitivity;
- [ ] year-by-year cumulative error + direction;
- [ ] component-removal diagnostic only, not post-hoc subset promotion.

Ensemble evaluation remains two-objective:
- cumulative absolute error;
- direction accuracy.

## 8. ELMFIS Stage 5 — family freeze and cross-family comparison

Compare, under the corrected active metrics:
- predecessor MSVR;
- ELM family;
- ANN family;
- ELMFIS family.

DEV is the selection authority.

2025/2026 are displayed only after DEV candidate/family status is frozen and cannot retroactively change the selection.

## 9. Execution order

1. Stage 0 baseline.
2. Stage 1 broad 33-entry parity screen in controlled batches.
3. Stage 2 DEV filter / parent freeze.
4. Stage 3A six mandatory refinements.
5. Stage 3B three parity hybrids.
6. Stage 3C CQCSA-ELMFIS.
7. Stage 4 ensemble/robustness.
8. Stage 5 ELMFIS vs ELM vs ANN vs MSVR family comparison.

## 10. Research stop rule

Do not expand ELMFIS into hundreds of arbitrary hybrids.
The predeclared coverage is already broad:
- 33 Stage-1 entries,
- 6 mandatory refinements,
- 3 additional parity hybrids,
- 1 ELMFIS-specific CQCSA extension,
- controlled ensemble layer.

Any additional method requires a new scientific rationale declared before seeing its DEV result.


## 11. Stage 0 result

Workflow run: **36161681793 — SUCCESS / OUTPUT_GATE=PASS**.

| Period | Sum absolute error USD | Direction |
|---|---:|---:|
| DEV | 1996.2933 | 20/33 = 60.61% |
| 2025 | 1032.7313 | 9/12 = 75.00% |
| 2026 Jan-Jul | 1997.7390 | 3/7 = 42.86% |

Baseline is technically valid but weak on DEV. The predeclared Stage-1 broad optimizer screen remains mandatory and is not cancelled by the baseline result.

**NEXT:** Stage 1 Batch 1.1 — PSO-ELMFIS, GA-ELMFIS, DE-ELMFIS; Vanilla baseline retained as anchor.


## 12. Stage 1 / Batch 1.1 result — completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-elmfis-meta-batch-1-v1.yml`  
**Run:** **36169448338 — SUCCESS / OUTPUT_GATE=PASS**  
**Implementation:** `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_1_v1.py`  
**Dedicated report:** `gold_axis_2026/GOLD_MONTHLY_ELMFIS_STAGE1_BATCH11_REPORT_2026-09-25.md`

DEV-only active-metric results:

| Model | Sum absolute error USD | Direction |
|---|---:|---:|
| DE-ELMFIS | **1665.4715** | **21/33 = 63.64%** |
| GA-ELMFIS | 1980.8994 | 14/33 = 42.42% |
| Vanilla ELMFIS | 1996.2933 | 20/33 = 60.61% |
| PSO-ELMFIS | 2358.4962 | 20/33 = 60.61% |

Batch 1.1 finding: DE-ELMFIS is the current batch leader on both active DEV objectives and beats the RW MAE benchmark. This is **not** a family freeze or Stage-2 parent decision; the full Stage-1 screen remains mandatory.

**Progress:** 4/33 Stage-1 entries complete, 29/33 remaining.

**STOP GATE:** Stage 1.2 must not start without explicit user confirmation.

**Next planned batch after confirmation:** MPA-ELMFIS + ABC-ELMFIS + SSA-ELMFIS + GWO-ELMFIS.


## 13. Stage 1 / Batch 1.2 result — completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-elmfis-meta-batch-2-v1.yml`  
**Run:** **36170049225 — SUCCESS / OUTPUT_GATE=PASS**  
**Implementation:** `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_2_v1.py`  
**Dedicated report:** `gold_axis_2026/GOLD_MONTHLY_ELMFIS_STAGE1_BATCH12_REPORT_2026-09-25.md`

DEV-only active-metric results:

| Model | Sum absolute error USD | Direction |
|---|---:|---:|
| ABC-ELMFIS | **1524.8854** | 21/33 = 63.64% |
| GWO-ELMFIS | 1943.5595 | **22/33 = 66.67%** |
| Vanilla ELMFIS | 1996.2933 | 20/33 = 60.61% |
| SSA-ELMFIS | 2124.4760 | 20/33 = 60.61% |
| MPA-ELMFIS | 3060.5864 | 19/33 = 57.58% |

Current provisional Stage-1 DEV Pareto set after 8/33 entries:
- ABC-ELMFIS — price-error side;
- GWO-ELMFIS — direction side.

No parent or family winner is frozen before the full Stage-1 screen and Stage-2 filtering.

**Progress:** 8/33 Stage-1 entries complete, 25/33 remaining.

**STOP GATE:** Stage 1.3 must not start without explicit user confirmation.

**Next planned batch after confirmation:** WOA-ELMFIS + HHO-ELMFIS + ACO-ELMFIS + Bat-ELMFIS.


## 14. Stage 1 / Batch 1.3 result — completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-elmfis-meta-batch-3-v1.yml`  
**Run:** **36170874292 — SUCCESS / OUTPUT_GATE=PASS**  
**Implementation:** `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_3_v1.py`  
**Dedicated report:** `gold_axis_2026/GOLD_MONTHLY_ELMFIS_STAGE1_BATCH13_REPORT_2026-09-25.md`

DEV-only active-metric results:

| Model | Sum absolute error USD | Direction |
|---|---:|---:|
| HHO-ELMFIS | **1857.8942** | **22/33 = 66.67%** |
| ACO-ELMFIS | 1942.8695 | 19/33 = 57.58% |
| Vanilla ELMFIS | 1996.2933 | 20/33 = 60.61% |
| Bat-ELMFIS | 2137.8294 | 19/33 = 57.58% |
| WOA-ELMFIS | 2536.5468 | 15/33 = 45.45% |

Current provisional Stage-1 DEV Pareto set after 12/33 entries:
- ABC-ELMFIS — price-error side: 1524.8854 / 21/33;
- HHO-ELMFIS — direction side: 1857.8942 / 22/33.

HHO dominates the previous GWO direction-side point at the same direction count with lower cumulative error. No parent or family winner is frozen.

**Progress:** 12/33 Stage-1 entries complete, 21/33 remaining.

**STOP GATE:** Stage 1.4 must not start without explicit user confirmation.

**Next planned batch after confirmation:** FA-ELMFIS + MFO-ELMFIS + FPA-ELMFIS + FA-FPA-ELMFIS.


## 15. Stage 1 / Batch 1.4 result — completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-elmfis-meta-batch-4-v1.yml`  
**Run:** **36171748270 — SUCCESS / OUTPUT_GATE=PASS**  
**Implementation:** `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_4_v1.py`  
**Dedicated report:** `gold_axis_2026/GOLD_MONTHLY_ELMFIS_STAGE1_BATCH14_REPORT_2026-09-25.md`

DEV-only active-metric results:

| Model | Sum absolute error USD | Direction |
|---|---:|---:|
| FA-FPA-ELMFIS | **1820.4499** | **25/33 = 75.76%** |
| Vanilla ELMFIS | 1996.2933 | 20/33 = 60.61% |
| MFO-ELMFIS | 2244.0539 | 19/33 = 57.58% |
| FPA-ELMFIS | 2251.8993 | 22/33 = 66.67% |
| FA-ELMFIS | 2421.4143 | 23/33 = 69.70% |

Current provisional Stage-1 DEV Pareto set after 16/33 entries:
- ABC-ELMFIS — price-error side: 1524.8854 / 21/33;
- FA-FPA-ELMFIS — direction side: 1820.4499 / 25/33.

FA-FPA dominates the former HHO direction-side Pareto point on both active objectives. No parent or family winner is frozen.

**Progress:** 16/33 Stage-1 entries complete, 17/33 remaining.

**STOP GATE:** Stage 1.5 must not start without explicit user confirmation.

**Next planned batch after confirmation:** CS-ELMFIS + SCA-ELMFIS + Salp-ELMFIS + SMA-ELMFIS.


## 16. Stage 1 / Batch 1.5 result — completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-elmfis-meta-batch-5-v1.yml`  
**Run:** **36173141852 — SUCCESS / OUTPUT_GATE=PASS**  
**Implementation:** `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_5_v1.py`  
**Dedicated report:** `gold_axis_2026/GOLD_MONTHLY_ELMFIS_STAGE1_BATCH15_REPORT_2026-09-25.md`

DEV-only active-metric results:

| Model | Sum absolute error USD | Direction |
|---|---:|---:|
| SMA-ELMFIS | **1651.4482** | **25/33 = 75.76%** |
| CS-ELMFIS | 1809.3931 | **25/33 = 75.76%** |
| Vanilla ELMFIS | 1996.2933 | 20/33 = 60.61% |
| Salp-ELMFIS | 2273.0187 | 19/33 = 57.58% |
| SCA-ELMFIS | 3177.3119 | 21/33 = 63.64% |

Current provisional Stage-1 DEV Pareto set after 20/33 entries:
- ABC-ELMFIS — price-error side: 1524.8854 / 21/33;
- SMA-ELMFIS — direction/trade-off side: 1651.4482 / 25/33.

SMA dominates both FA-FPA and CS at the same 25/33 direction count with lower cumulative error. No parent or family winner is frozen.

**Progress:** 20/33 Stage-1 entries complete, 13/33 remaining.

**STOP GATE:** Stage 1.6 must not start without explicit user confirmation.

**Next planned batch after confirmation:** GOA-ELMFIS + ALO-ELMFIS + TLBO-ELMFIS + JAYA-ELMFIS.


## 17. Stage 1 / Batch 1.6 result — completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-elmfis-meta-batch-6-v1.yml`  
**Run:** **36174033508 — SUCCESS / OUTPUT_GATE=PASS**  
**Implementation:** `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_6_v1.py`  
**Dedicated report:** `gold_axis_2026/GOLD_MONTHLY_ELMFIS_STAGE1_BATCH16_REPORT_2026-09-25.md`

DEV-only active-metric results:

| Model | Sum absolute error USD | Direction |
|---|---:|---:|
| JAYA-ELMFIS | **1810.4656** | **21/33 = 63.64%** |
| Vanilla ELMFIS | 1996.2933 | 20/33 = 60.61% |
| GOA-ELMFIS | 2322.7589 | 21/33 = 63.64% |
| ALO-ELMFIS | 2812.5033 | 18/33 = 54.55% |
| TLBO-ELMFIS | 3240.2851 | 20/33 = 60.61% |

Current provisional Stage-1 DEV Pareto set after 24/33 entries remains:
- ABC-ELMFIS — price-error side: 1524.8854 / 21/33;
- SMA-ELMFIS — direction/trade-off side: 1651.4482 / 25/33.

JAYA is the Batch-1.6 leader but is dominated by ABC at the same direction count. No parent or family winner is frozen.

**Progress:** 24/33 Stage-1 entries complete, 9/33 remaining.

**STOP GATE:** Stage 1.7 must not start without explicit user confirmation.

**Next planned batch after confirmation:** HGS-ELMFIS + ChOA-ELMFIS + HGSO-ELMFIS + AOA-ELMFIS.


## 18. Stage 1 / Batch 1.7 result — completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-elmfis-meta-batch-7-v1.yml`  
**Run:** **36175116272 — SUCCESS / OUTPUT_GATE=PASS**  
**Implementation:** `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_7_v1.py`  
**Dedicated report:** `gold_axis_2026/GOLD_MONTHLY_ELMFIS_STAGE1_BATCH17_REPORT_2026-09-25.md`

DEV-only active-metric results:

| Model | Sum absolute error USD | Direction |
|---|---:|---:|
| HGSO-ELMFIS | **1594.6455** | 18/33 = 54.55% |
| HGS-ELMFIS | 1780.8620 | 20/33 = 60.61% |
| AOA-ELMFIS | 1873.9154 | **22/33 = 66.67%** |
| Vanilla ELMFIS | 1996.2933 | 20/33 = 60.61% |
| ChOA-ELMFIS | 2822.8921 | 20/33 = 60.61% |

Current provisional Stage-1 DEV Pareto set after 28/33 entries remains:
- ABC-ELMFIS — price-error side: 1524.8854 / 21/33;
- SMA-ELMFIS — direction/trade-off side: 1651.4482 / 25/33.

HGSO has strong price error but is dominated by ABC; AOA is dominated by SMA. No parent or family winner is frozen.

**Progress:** 28/33 Stage-1 entries complete, 5/33 remaining.

**STOP GATE:** Stage 1.8 must not start without explicit user confirmation.

**Next planned batch after confirmation:** CPA-ELMFIS + Krill Herd-ELMFIS + Crow Search-ELMFIS.


## 19. Stage 1 / Batch 1.8 result — completed 2026-09-25

**Workflow:** `.github/workflows/gold-midas-elmfis-meta-batch-8-v1.yml`  
**Run:** **36175779813 — SUCCESS / OUTPUT_GATE=PASS**  
**Implementation:** `gold_axis_2026/tools/vw_midas_elmfis_meta_batch_8_v1.py`  
**Dedicated report:** `gold_axis_2026/GOLD_MONTHLY_ELMFIS_STAGE1_BATCH18_REPORT_2026-09-25.md`

DEV-only active-metric results:

| Model | Sum absolute error USD | Direction |
|---|---:|---:|
| Crow Search-ELMFIS | **1881.2292** | 20/33 = 60.61% |
| CPA-ELMFIS | 1925.0323 | 20/33 = 60.61% |
| Vanilla ELMFIS | 1996.2933 | 20/33 = 60.61% |
| Krill Herd-ELMFIS | 3043.2306 | 20/33 = 60.61% |

Current provisional Stage-1 DEV Pareto set after 31/33 entries remains:
- ABC-ELMFIS — price-error side: 1524.8854 / 21/33;
- SMA-ELMFIS — direction/trade-off side: 1651.4482 / 25/33.

No Stage-1.8 model changes the frontier. No parent or family winner is frozen.

**Progress:** 31/33 Stage-1 entries complete, 2/33 remaining.

**STOP GATE:** Stage 1.9 must not start without explicit user confirmation.

**Next planned batch after confirmation:** DE-ABC-ELMFIS + Multi-swarm-ELMFIS.
