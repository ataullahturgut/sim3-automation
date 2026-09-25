# GOLD MONTHLY FORECAST — ELMFIS STAGE 1 / BATCH 1.8 REPORT

**Date:** 2026-09-25  
**Repository:** ataullahturgut/sim3-automation  
**Branch:** gold-midas-headswap-v1-20260925  
**Workflow run:** 36175779813 — SUCCESS / OUTPUT_GATE=PASS  
**Status:** STAGE 1.8 COMPLETE — STOP GATE ACTIVE

## 1. Scope

Batch 1.8 executed:

- CPA-ELMFIS
- Krill Herd-ELMFIS
- Crow Search-ELMFIS

Vanilla ELMFIS was re-run as the same-workflow anchor.

No Stage 1.9 method was started.

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

Krill operates in span-normalized parameter space for neighborhood distance and motion. Crow uses bounded memory/flight updates with training-only restart behavior during refit. CPA preserves its exploration/exploitation parity logic.

## 4. DEV results — selection authority

| Model | Sum absolute error (USD) | Direction | MAE | Relative MAE vs RW | RMSE |
|---|---:|---:|---:|---:|---:|
| **Crow Search-ELMFIS** | **1,881.23** | **20/33 = 60.61%** | 57.01 | 1.0701 | 75.81 |
| CPA-ELMFIS | 1,925.03 | **20/33 = 60.61%** | 58.33 | 1.0950 | 72.12 |
| Vanilla ELMFIS | 1,996.29 | **20/33 = 60.61%** | 60.49 | 1.1355 | 72.01 |
| Krill Herd-ELMFIS | 3,043.23 | **20/33 = 60.61%** | 92.22 | 1.7311 | 162.54 |

### DEV interpretation

Within Batch 1.8:
- Crow Search-ELMFIS is the batch leader.
- Crow and CPA both improve cumulative error versus Vanilla while matching Vanilla's 20/33 direction count.
- Krill Herd-ELMFIS is weak on cumulative error and provides no direction improvement.

Across all first 31 Stage-1 entries, the provisional DEV Pareto set remains unchanged:

- **ABC-ELMFIS:** 1,524.89 USD / 21/33 — current price-error side.
- **SMA-ELMFIS:** 1,651.45 USD / 25/33 — current direction/trade-off side.

Crow, CPA and Krill are dominated on the active DEV plane by existing Stage-1 candidates.

No family winner or refinement parent is frozen before the complete Stage-1 broad screen and Stage-2 filtering.

## 5. Reporting-only external periods

These values are recorded only for later transport/stress diagnosis and did not influence selection:

| Model | 2025 sum abs error | 2025 direction | 2026 Jan-Jul sum abs error | 2026 direction |
|---|---:|---:|---:|---:|
| CPA-ELMFIS | 1,308.18 | 7/12 = 58.33% | 2,271.06 | 5/7 = 71.43% |
| Krill Herd-ELMFIS | 1,198.70 | 10/12 = 83.33% | 1,993.48 | 4/7 = 57.14% |
| Crow Search-ELMFIS | 1,199.86 | 11/12 = 91.67% | 2,285.60 | 5/7 = 71.43% |

These reporting-only periods did not alter tuning, Pareto status or model promotion.

## 6. Implementation records

**Script:**  
`gold_axis_2026/tools/vw_midas_elmfis_meta_batch_8_v1.py`

**Workflow:**  
`.github/workflows/gold-midas-elmfis-meta-batch-8-v1.yml`

**Implementation commit:**  
`26422003c1f9ba79edb8cff578479c7b60c68c73`

**Workflow commit:**  
`ed3b998b963bafef947bbc6722be90f6a8bc45c3`

**Run:**  
`36175779813`

All three optimizer branches, Vanilla anchor and combined output gate passed.

## 7. Stage status

- ELMFIS Stage 0: COMPLETE.
- Stage 1 / Batch 1.1: COMPLETE.
- Stage 1 / Batch 1.2: COMPLETE.
- Stage 1 / Batch 1.3: COMPLETE.
- Stage 1 / Batch 1.4: COMPLETE.
- Stage 1 / Batch 1.5: COMPLETE.
- Stage 1 / Batch 1.6: COMPLETE.
- Stage 1 / Batch 1.7: COMPLETE.
- Stage 1 / Batch 1.8: **COMPLETE**.
- Completed Stage-1 entries: **31/33**.
- Remaining Stage-1 entries: **2/33**.
- Next planned batch: **Stage 1.9 — DE-ABC-ELMFIS + Multi-swarm-ELMFIS**.
- **Do not start Stage 1.9 without explicit user confirmation.**

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
