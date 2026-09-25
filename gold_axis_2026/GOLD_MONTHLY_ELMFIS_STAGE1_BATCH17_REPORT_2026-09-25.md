# GOLD MONTHLY FORECAST — ELMFIS STAGE 1 / BATCH 1.7 REPORT

**Date:** 2026-09-25  
**Repository:** ataullahturgut/sim3-automation  
**Branch:** gold-midas-headswap-v1-20260925  
**Workflow run:** 36175116272 — SUCCESS / OUTPUT_GATE=PASS  
**Status:** STAGE 1.7 COMPLETE — STOP GATE ACTIVE

## 1. Scope

Batch 1.7 executed:

- HGS-ELMFIS
- ChOA-ELMFIS
- HGSO-ELMFIS
- AOA-ELMFIS

Vanilla ELMFIS was re-run as the same-workflow anchor.

No Stage 1.8 method was started.

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

HGS/ChOA/HGSO parity mechanics were retained with perturbations scaled to heterogeneous ELMFIS parameter spans. AOA arithmetic operations were applied in normalized parameter space to prevent center/log-spread bound heterogeneity from creating an artificial scale bias.

## 4. DEV results — selection authority

| Model | Sum absolute error (USD) | Direction | MAE | Relative MAE vs RW | RMSE |
|---|---:|---:|---:|---:|---:|
| **HGSO-ELMFIS** | **1,594.65** | 18/33 = 54.55% | 48.32 | 0.9071 | 65.93 |
| HGS-ELMFIS | 1,780.86 | 20/33 = 60.61% | 53.97 | 1.0130 | 66.21 |
| AOA-ELMFIS | 1,873.92 | **22/33 = 66.67%** | 56.79 | 1.0659 | 72.88 |
| Vanilla ELMFIS | 1,996.29 | 20/33 = 60.61% | 60.49 | 1.1355 | 72.01 |
| ChOA-ELMFIS | 2,822.89 | 20/33 = 60.61% | 85.54 | 1.6057 | 193.64 |

### DEV interpretation

Within Batch 1.7:
- HGSO-ELMFIS is the batch price-error leader and beats RW on DEV MAE, but its direction score is only 18/33.
- AOA-ELMFIS has the best direction count in this batch at 22/33 but higher cumulative error.
- HGS-ELMFIS improves cumulative error versus Vanilla without improving direction.
- ChOA-ELMFIS is weak on the active DEV plane.

Across all first 28 Stage-1 entries, the provisional DEV Pareto set remains unchanged:

- **ABC-ELMFIS:** 1,524.89 USD / 21/33 — current price-error side.
- **SMA-ELMFIS:** 1,651.45 USD / 25/33 — current direction/trade-off side.

HGSO does not enter the frontier because ABC has both lower cumulative error and higher direction. AOA is dominated by SMA, which has lower error and higher direction.

No family winner or refinement parent is frozen before the complete Stage-1 broad screen and Stage-2 filtering.

## 5. Reporting-only external periods

These values are recorded only for later transport/stress diagnosis and did not influence selection:

| Model | 2025 sum abs error | 2025 direction | 2026 Jan-Jul sum abs error | 2026 direction |
|---|---:|---:|---:|---:|
| HGS-ELMFIS | 1,199.53 | 9/12 = 75.00% | 3,066.07 | 6/7 = 85.71% |
| ChOA-ELMFIS | 1,087.80 | 11/12 = 91.67% | 2,149.12 | 3/7 = 42.86% |
| HGSO-ELMFIS | 1,244.66 | 9/12 = 75.00% | 1,880.22 | 5/7 = 71.43% |
| AOA-ELMFIS | 848.38 | 11/12 = 91.67% | 3,341.17 | 2/7 = 28.57% |

The strong-looking 2025 AOA/ChOA values and 2026 HGS direction are reporting-only and do not affect DEV selection status.

## 6. Implementation records

**Script:**  
`gold_axis_2026/tools/vw_midas_elmfis_meta_batch_7_v1.py`

**Workflow:**  
`.github/workflows/gold-midas-elmfis-meta-batch-7-v1.yml`

**Implementation commit:**  
`24fde2b26d03c8d89ab3c6eca64410bbbde53134`

**Workflow commit:**  
`8d8aac8cf13de3cbb9064535563403a03a595762`

**Run:**  
`36175116272`

All optimizer branches, Vanilla anchor and combined output gate passed.

## 7. Stage status

- ELMFIS Stage 0: COMPLETE.
- Stage 1 / Batch 1.1: COMPLETE.
- Stage 1 / Batch 1.2: COMPLETE.
- Stage 1 / Batch 1.3: COMPLETE.
- Stage 1 / Batch 1.4: COMPLETE.
- Stage 1 / Batch 1.5: COMPLETE.
- Stage 1 / Batch 1.6: COMPLETE.
- Stage 1 / Batch 1.7: **COMPLETE**.
- Completed Stage-1 entries: **28/33**.
- Remaining Stage-1 entries: **5/33**.
- Next planned batch: **Stage 1.8 — CPA-ELMFIS + Krill Herd-ELMFIS + Crow Search-ELMFIS**.
- **Do not start Stage 1.8 without explicit user confirmation.**

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
