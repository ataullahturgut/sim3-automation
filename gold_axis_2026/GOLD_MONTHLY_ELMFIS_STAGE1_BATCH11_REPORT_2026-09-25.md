# GOLD MONTHLY FORECAST — ELMFIS STAGE 1 / BATCH 1.1 REPORT

**Date:** 2026-09-25  
**Repository:** ataullahturgut/sim3-automation  
**Branch:** gold-midas-headswap-v1-20260925  
**Workflow run:** 36169448338 — SUCCESS / OUTPUT_GATE=PASS  
**Status:** STAGE 1.1 COMPLETE — STOP GATE ACTIVE

## 1. Scope

Batch 1.1 executed the first three optimized ELMFIS variants under the frozen monthly H=1 contract:

- PSO-ELMFIS
- GA-ELMFIS
- DE-ELMFIS

Vanilla ELMFIS was re-run in the same workflow as the baseline anchor.

No later ELMFIS batch was started.

## 2. Frozen authority

Unchanged throughout the batch:

- Target: next calendar month's average XAU/USD price, H=1.
- Origin: previous completed month-end.
- Inputs: governed 8 origin-safe VW-MIDAS features.
- DEV selection authority: 2022-04..2024-12, n=33.
- 2025: retrospective transport reporting only.
- 2026 Jan-Jul: retrospective stress reporting only.
- Random split: none.
- Target-month leakage: prohibited.
- DB access: READ_ONLY.
- Primary evaluation plane: cumulative absolute price error + direction accuracy.
- MAPE and related statistics: supporting metrics only.

## 3. Canonical optimized ELMFIS contract

The canonical Stage-0 ELMFIS structure was retained:

- 8 standardized inputs;
- 5 fuzzy rules;
- 4 outputs;
- Gaussian/bell antecedent membership;
- product AND with normalized firing strength;
- first-order TSK consequent;
- analytic ridge consequent fitting.

Metaheuristics optimize antecedent parameters only:

- 40 rule-center parameters;
- 40 log-spread parameters;
- total optimized antecedent dimension = 80.

TSK consequent coefficients are never searched by the metaheuristic. They are solved analytically by ridge for every candidate antecedent configuration.

Optimization/selection protocol:

- population = 24;
- selection generations = 45;
- refit generations = 15;
- deterministic repeats = 3;
- chronological final 20% validation tail, minimum 6 rows;
- population evolution objective = 0.7 × Gold standardized MAE + 0.3 × all-output standardized MAE on inner training;
- validation selects only among the top quartile by inner-training loss;
- validation consequents are fit on inner training only;
- full-history refit uses all pre-target history only.

## 4. DEV results — selection authority

| Model | Sum absolute error (USD) | Direction | MAE | Relative MAE vs RW | RMSE |
|---|---:|---:|---:|---:|---:|
| DE-ELMFIS | **1,665.47** | **21/33 = 63.64%** | 50.47 | 0.9474 | 65.40 |
| GA-ELMFIS | 1,980.90 | 14/33 = 42.42% | 60.03 | 1.1268 | 76.03 |
| Vanilla ELMFIS | 1,996.29 | 20/33 = 60.61% | 60.49 | 1.1355 | 72.01 |
| PSO-ELMFIS | 2,358.50 | 20/33 = 60.61% | 71.47 | 1.3416 | 92.36 |

### DEV interpretation

Within Batch 1.1, DE-ELMFIS dominates the other three models on the active primary plane:

- lowest cumulative absolute price error;
- highest direction accuracy in the batch;
- relative MAE below 1.0 versus the random-walk benchmark.

Relative to Vanilla ELMFIS, DE-ELMFIS reduces DEV cumulative absolute error by approximately **330.82 USD** and improves direction by **1 month**.

GA-ELMFIS is close to Vanilla on cumulative price error but loses substantial direction performance.

PSO-ELMFIS is worse than Vanilla on cumulative error and does not improve direction.

These observations are provisional Batch-1.1 findings only. No ELMFIS family winner or refinement parent is frozen before the full Stage-1 broad screen and Stage-2 DEV filtering.

## 5. Reporting-only external periods

These values are recorded for later transport/stress diagnosis and did not affect selection or interpretation authority.

| Model | 2025 sum abs error | 2025 direction | 2026 Jan-Jul sum abs error | 2026 direction |
|---|---:|---:|---:|---:|
| DE-ELMFIS | 1,293.64 | 10/12 = 83.33% | 1,909.59 | 5/7 = 71.43% |
| GA-ELMFIS | 1,294.63 | 8/12 = 66.67% | 2,696.49 | 4/7 = 57.14% |
| PSO-ELMFIS | 1,785.48 | 10/12 = 83.33% | 4,401.27 | 2/7 = 28.57% |
| Vanilla ELMFIS | 1,032.73 | 9/12 = 75.00% | 1,997.74 | 3/7 = 42.86% |

No model was promoted, rejected, tuned or reweighted using these 2025/2026 outcomes.

## 6. Implementation records

**Script:**  
`gold_axis_2026/tools/vw_midas_elmfis_meta_batch_1_v1.py`

**Workflow:**  
`.github/workflows/gold-midas-elmfis-meta-batch-1-v1.yml`

**Implementation commit:**  
`832f493ab379a53e6efcb9b91ee9b02df64f2871`

**Workflow commit:**  
`56b9529222339d7281df1e59e02532bb750baee7`

**Run:**  
`36169448338`

All four execution branches passed their individual gates and the combined batch gate passed.

## 7. Stage status

- ELMFIS Stage 0: COMPLETE.
- ELMFIS Stage 1 / Batch 1.1: **COMPLETE**.
- Completed Stage-1 entries: Vanilla, PSO, GA, DE = 4/33.
- Remaining Stage-1 entries: 29/33.
- Next planned batch: **Stage 1.2 — MPA-ELMFIS + ABC-ELMFIS + SSA-ELMFIS + GWO-ELMFIS**.
- **Do not start Stage 1.2 without explicit user confirmation.**

## 8. Control and compliance summary

- Forecast target unchanged: PASS.
- 8-feature origin-safe contract unchanged: PASS.
- DEV-only model-selection authority: PASS.
- 2025 reporting-only role: PASS.
- 2026 reporting-only role: PASS.
- READ_ONLY DB: PASS.
- No random validation: PASS.
- No target-month fitness/leakage: PASS.
- Primary metrics = cumulative absolute error + direction: PASS.
- Batch output gate: PASS.
