# GOLD MONTHLY FORECAST — ELMFIS STAGE 1 / BATCH 1.4 REPORT

**Date:** 2026-09-25  
**Repository:** ataullahturgut/sim3-automation  
**Branch:** gold-midas-headswap-v1-20260925  
**Workflow run:** 36171748270 — SUCCESS / OUTPUT_GATE=PASS  
**Status:** STAGE 1.4 COMPLETE — STOP GATE ACTIVE

## 1. Scope

Batch 1.4 executed:

- FA-ELMFIS
- MFO-ELMFIS
- FPA-ELMFIS
- FA-FPA-ELMFIS

Vanilla ELMFIS was re-run as the same-workflow anchor.

FA-FPA is a true hybrid parity implementation: each iteration applies a Firefly intensification step followed by Flower Pollination diversification, adapted from the historical ELM FA-FPA implementation while preserving the ELMFIS antecedent-only optimization contract.

No Stage 1.5 method was started.

## 2. Frozen authority

Unchanged:
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

## 3. Optimization contract

Canonical 5-rule ELMFIS retained:
- 8 standardized inputs;
- 4 outputs;
- 40 rule-center parameters;
- 40 log-spread parameters;
- total optimized antecedent dimension = 80;
- TSK consequents solved analytically by ridge for every candidate antecedent structure.

Common protocol:
- population = 24;
- selection generations = 45;
- refit generations = 15;
- 3 deterministic repeats per target;
- chronological final-20% validation tail;
- validation does not use target-month information;
- final refit uses only pre-target history.

## 4. DEV results — selection authority

| Model | Sum absolute error (USD) | Direction | MAE | Relative MAE vs RW | RMSE |
|---|---:|---:|---:|---:|---:|
| **FA-FPA-ELMFIS** | **1,820.45** | **25/33 = 75.76%** | 55.17 | 1.0355 | 67.30 |
| Vanilla ELMFIS | 1,996.29 | 20/33 = 60.61% | 60.49 | 1.1355 | 72.01 |
| MFO-ELMFIS | 2,244.05 | 19/33 = 57.58% | 68.00 | 1.2765 | 94.29 |
| FPA-ELMFIS | 2,251.90 | 22/33 = 66.67% | 68.24 | 1.2809 | 125.55 |
| FA-ELMFIS | 2,421.41 | 23/33 = 69.70% | 73.38 | 1.3774 | 101.83 |

### DEV interpretation

Within Batch 1.4:
- FA-FPA-ELMFIS is the clear batch leader.
- FA-FPA reaches 25/33 correct directions, materially above all earlier Stage-1 ELMFIS entries.
- Its cumulative error is also lower than the previous direction-side leader HHO-ELMFIS.

Across all first 16 Stage-1 entries, the provisional DEV Pareto set becomes:

- **ABC-ELMFIS:** 1,524.89 USD / 21/33 — current price-error side.
- **FA-FPA-ELMFIS:** 1,820.45 USD / 25/33 — current direction side.

HHO-ELMFIS is no longer on the provisional Pareto frontier because FA-FPA has both lower cumulative error (1,820.45 vs 1,857.89 USD) and higher direction accuracy (25/33 vs 22/33).

No family winner or refinement parent is frozen before the complete Stage-1 broad screen and Stage-2 filtering.

## 5. Reporting-only external periods

These values are recorded only for later transport/stress diagnosis and did not influence selection:

| Model | 2025 sum abs error | 2025 direction | 2026 Jan-Jul sum abs error | 2026 direction |
|---|---:|---:|---:|---:|
| FA-ELMFIS | 1,312.84 | 8/12 = 66.67% | 2,079.69 | 3/7 = 42.86% |
| MFO-ELMFIS | 1,433.13 | 9/12 = 75.00% | 3,021.61 | 4/7 = 57.14% |
| FPA-ELMFIS | 1,649.25 | 8/12 = 66.67% | 1,520.56 | 4/7 = 57.14% |
| FA-FPA-ELMFIS | 1,239.26 | 10/12 = 83.33% | 2,330.96 | 3/7 = 42.86% |

2025/2026 did not alter tuning, Pareto status, or model promotion.

## 6. Implementation records

**Script:**  
`gold_axis_2026/tools/vw_midas_elmfis_meta_batch_4_v1.py`

**Workflow:**  
`.github/workflows/gold-midas-elmfis-meta-batch-4-v1.yml`

**Implementation commit:**  
`398643477558c6c4cf421707f36418c8e155b86f`

**Workflow commit:**  
`e716821e99fc643e7abb42e87519ff52e258fbea`

**Run:**  
`36171748270`

All optimizer branches, Vanilla anchor and combined output gate passed.

## 7. Stage status

- ELMFIS Stage 0: COMPLETE.
- Stage 1 / Batch 1.1: COMPLETE.
- Stage 1 / Batch 1.2: COMPLETE.
- Stage 1 / Batch 1.3: COMPLETE.
- Stage 1 / Batch 1.4: **COMPLETE**.
- Completed Stage-1 entries: **16/33**.
- Remaining Stage-1 entries: **17/33**.
- Next planned batch: **Stage 1.5 — CS-ELMFIS + SCA-ELMFIS + Salp-ELMFIS + SMA-ELMFIS**.
- **Do not start Stage 1.5 without explicit user confirmation.**

## 8. Control and compliance summary

- Forecast target unchanged: PASS.
- 8-feature origin-safe contract unchanged: PASS.
- DEV-only model-selection authority: PASS.
- 2025 reporting-only role: PASS.
- 2026 reporting-only role: PASS.
- READ_ONLY DB: PASS.
- No random validation: PASS.
- No target-month fitness/leakage: PASS.
- Optimizer scope = centers + log-spreads only: PASS.
- TSK consequent = analytic ridge: PASS.
- Primary metrics = cumulative absolute error + direction: PASS.
- Batch output gate: PASS.
