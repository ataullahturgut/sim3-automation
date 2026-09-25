# GOLD MONTHLY FORECAST — ELMFIS STAGE 1 / BATCH 1.6 REPORT

**Date:** 2026-09-25  
**Repository:** ataullahturgut/sim3-automation  
**Branch:** gold-midas-headswap-v1-20260925  
**Workflow run:** 36174033508 — SUCCESS / OUTPUT_GATE=PASS  
**Status:** STAGE 1.6 COMPLETE — STOP GATE ACTIVE

## 1. Scope

Batch 1.6 executed:

- GOA-ELMFIS
- ALO-ELMFIS
- TLBO-ELMFIS
- JAYA-ELMFIS

Vanilla ELMFIS was re-run as the same-workflow anchor.

No Stage 1.7 method was started.

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

GOA pairwise distances were normalized by heterogeneous ELMFIS parameter spans. ALO radius shrinkage likewise used component-wise parameter spans. TLBO and JAYA retained parity logic with bounded antecedent updates.

## 4. DEV results — selection authority

| Model | Sum absolute error (USD) | Direction | MAE | Relative MAE vs RW | RMSE |
|---|---:|---:|---:|---:|---:|
| **JAYA-ELMFIS** | **1,810.47** | **21/33 = 63.64%** | 54.86 | 1.0298 | 72.17 |
| Vanilla ELMFIS | 1,996.29 | 20/33 = 60.61% | 60.49 | 1.1355 | 72.01 |
| GOA-ELMFIS | 2,322.76 | 21/33 = 63.64% | 70.39 | 1.3213 | 129.53 |
| ALO-ELMFIS | 2,812.50 | 18/33 = 54.55% | 85.23 | 1.5998 | 126.42 |
| TLBO-ELMFIS | 3,240.29 | 20/33 = 60.61% | 98.19 | 1.8432 | 203.42 |

### DEV interpretation

Within Batch 1.6:
- JAYA-ELMFIS is the batch leader.
- JAYA improves both cumulative error and direction versus Vanilla.
- GOA improves direction versus Vanilla but carries materially higher cumulative error.
- ALO and TLBO are weak on the active DEV plane.

Across all first 24 Stage-1 entries, the provisional DEV Pareto set remains unchanged:

- **ABC-ELMFIS:** 1,524.89 USD / 21/33 — current price-error side.
- **SMA-ELMFIS:** 1,651.45 USD / 25/33 — current direction/trade-off side.

JAYA does not enter the Pareto frontier because ABC has the same 21/33 direction count with materially lower cumulative error.

No family winner or refinement parent is frozen before the complete Stage-1 broad screen and Stage-2 filtering.

## 5. Reporting-only external periods

These values are recorded only for later transport/stress diagnosis and did not influence selection:

| Model | 2025 sum abs error | 2025 direction | 2026 Jan-Jul sum abs error | 2026 direction |
|---|---:|---:|---:|---:|
| GOA-ELMFIS | 1,726.36 | 8/12 = 66.67% | 2,025.20 | 3/7 = 42.86% |
| ALO-ELMFIS | 1,658.37 | 10/12 = 83.33% | 1,805.81 | 4/7 = 57.14% |
| TLBO-ELMFIS | 955.32 | 9/12 = 75.00% | 1,416.73 | 5/7 = 71.43% |
| JAYA-ELMFIS | 944.01 | 10/12 = 83.33% | 1,760.67 | 4/7 = 57.14% |

The comparatively strong 2025 TLBO/JAYA values and 2026 TLBO values remain reporting-only and do not override their DEV status.

## 6. Implementation records

**Script:**  
`gold_axis_2026/tools/vw_midas_elmfis_meta_batch_6_v1.py`

**Workflow:**  
`.github/workflows/gold-midas-elmfis-meta-batch-6-v1.yml`

**Implementation commit:**  
`97638e9cfab6c927f46ab270d8667e8bec792321`

**Workflow commit:**  
`a64b610eca325dbbda1e2a41faceeaa9c3e044cc`

**Run:**  
`36174033508`

All optimizer branches, Vanilla anchor and combined output gate passed.

## 7. Stage status

- ELMFIS Stage 0: COMPLETE.
- Stage 1 / Batch 1.1: COMPLETE.
- Stage 1 / Batch 1.2: COMPLETE.
- Stage 1 / Batch 1.3: COMPLETE.
- Stage 1 / Batch 1.4: COMPLETE.
- Stage 1 / Batch 1.5: COMPLETE.
- Stage 1 / Batch 1.6: **COMPLETE**.
- Completed Stage-1 entries: **24/33**.
- Remaining Stage-1 entries: **9/33**.
- Next planned batch: **Stage 1.7 — HGS-ELMFIS + ChOA-ELMFIS + HGSO-ELMFIS + AOA-ELMFIS**.
- **Do not start Stage 1.7 without explicit user confirmation.**

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
