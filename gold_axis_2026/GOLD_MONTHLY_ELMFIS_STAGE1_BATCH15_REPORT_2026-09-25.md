# GOLD MONTHLY FORECAST — ELMFIS STAGE 1 / BATCH 1.5 REPORT

**Date:** 2026-09-25  
**Repository:** ataullahturgut/sim3-automation  
**Branch:** gold-midas-headswap-v1-20260925  
**Workflow run:** 36173141852 — SUCCESS / OUTPUT_GATE=PASS  
**Status:** STAGE 1.5 COMPLETE — STOP GATE ACTIVE

## 1. Scope

Batch 1.5 executed:

- CS-ELMFIS
- SCA-ELMFIS
- Salp-ELMFIS
- SMA-ELMFIS

Vanilla ELMFIS was re-run as the same-workflow anchor.

No Stage 1.6 method was started.

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
| **SMA-ELMFIS** | **1,651.45** | **25/33 = 75.76%** | 50.04 | 0.9394 | 64.66 |
| CS-ELMFIS | 1,809.39 | **25/33 = 75.76%** | 54.83 | 1.0292 | 77.75 |
| Vanilla ELMFIS | 1,996.29 | 20/33 = 60.61% | 60.49 | 1.1355 | 72.01 |
| Salp-ELMFIS | 2,273.02 | 19/33 = 57.58% | 68.88 | 1.2930 | 111.80 |
| SCA-ELMFIS | 3,177.31 | 21/33 = 63.64% | 96.28 | 1.8073 | 180.57 |

### DEV interpretation

Within Batch 1.5:
- SMA-ELMFIS is the clear batch leader.
- CS-ELMFIS matches SMA's 25/33 direction but has about 157.94 USD higher cumulative error.
- Salp-ELMFIS and SCA-ELMFIS are weak on the active DEV plane.

Across all first 20 Stage-1 entries:
- **ABC-ELMFIS:** 1,524.89 USD / 21/33 — current price-error side.
- **SMA-ELMFIS:** 1,651.45 USD / 25/33 — current direction/trade-off side.

SMA-ELMFIS dominates the former FA-FPA point because both achieve 25/33 direction while SMA lowers cumulative error from 1,820.45 USD to 1,651.45 USD, an improvement of about 169.00 USD.

CS-ELMFIS is also dominated by SMA at the same direction count.

No family winner or refinement parent is frozen before the complete Stage-1 broad screen and Stage-2 filtering.

## 5. Reporting-only external periods

These values are recorded only for later transport/stress diagnosis and did not influence selection:

| Model | 2025 sum abs error | 2025 direction | 2026 Jan-Jul sum abs error | 2026 direction |
|---|---:|---:|---:|---:|
| CS-ELMFIS | 1,520.72 | 10/12 = 83.33% | 3,137.89 | 3/7 = 42.86% |
| SCA-ELMFIS | 2,029.02 | 8/12 = 66.67% | 2,760.24 | 3/7 = 42.86% |
| Salp-ELMFIS | 1,635.15 | 9/12 = 75.00% | 4,628.46 | 4/7 = 57.14% |
| SMA-ELMFIS | 1,583.98 | 10/12 = 83.33% | 2,410.76 | 3/7 = 42.86% |

2025/2026 did not alter tuning, Pareto status, or model promotion.

## 6. Implementation records

**Script:**  
`gold_axis_2026/tools/vw_midas_elmfis_meta_batch_5_v1.py`

**Workflow:**  
`.github/workflows/gold-midas-elmfis-meta-batch-5-v1.yml`

**Implementation commit:**  
`c9beb2c6aa7f7bdae679e6242a2afabf1c750c2d`

**Workflow commit:**  
`76cb6e745844246a6a11041554c05679abfaa005`

**Run:**  
`36173141852`

All optimizer branches, Vanilla anchor and combined output gate passed.

## 7. Stage status

- ELMFIS Stage 0: COMPLETE.
- Stage 1 / Batch 1.1: COMPLETE.
- Stage 1 / Batch 1.2: COMPLETE.
- Stage 1 / Batch 1.3: COMPLETE.
- Stage 1 / Batch 1.4: COMPLETE.
- Stage 1 / Batch 1.5: **COMPLETE**.
- Completed Stage-1 entries: **20/33**.
- Remaining Stage-1 entries: **13/33**.
- Next planned batch: **Stage 1.6 — GOA-ELMFIS + ALO-ELMFIS + TLBO-ELMFIS + JAYA-ELMFIS**.
- **Do not start Stage 1.6 without explicit user confirmation.**

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
