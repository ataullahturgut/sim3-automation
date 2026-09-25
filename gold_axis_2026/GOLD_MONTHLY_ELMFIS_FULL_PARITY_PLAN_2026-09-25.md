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
- [ ] Vanilla ELMFIS
- [ ] PSO-ELMFIS
- [ ] GA-ELMFIS
- [ ] MPA-ELMFIS
- [ ] DE-ELMFIS
- [ ] ABC-ELMFIS
- [ ] SSA-ELMFIS
- [ ] GWO-ELMFIS
- [ ] WOA-ELMFIS
- [ ] HHO-ELMFIS
- [ ] ACO-ELMFIS
- [ ] Bat-ELMFIS
- [ ] FA-ELMFIS
- [ ] MFO-ELMFIS
- [ ] FPA-ELMFIS
- [ ] CS-ELMFIS
- [ ] SCA-ELMFIS
- [ ] Salp-ELMFIS
- [ ] SMA-ELMFIS
- [ ] GOA-ELMFIS
- [ ] ALO-ELMFIS
- [ ] TLBO-ELMFIS
- [ ] JAYA-ELMFIS
- [ ] HGS-ELMFIS
- [ ] ChOA-ELMFIS
- [ ] HGSO-ELMFIS
- [ ] AOA-ELMFIS
- [ ] CPA-ELMFIS
- [ ] Krill Herd-ELMFIS
- [ ] Crow Search / CSA-ELMFIS

### Broad-screen hybrid/parity entries
- [ ] FA-FPA-ELMFIS
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
