# GOLD MONTHLY FORECAST — ELMFIS STAGE 1 / BATCH 1.3 REPORT

**Date:** 2026-09-25  
**Repository:** ataullahturgut/sim3-automation  
**Branch:** gold-midas-headswap-v1-20260925  
**Workflow run:** 36170874292 — SUCCESS / OUTPUT_GATE=PASS  
**Status:** STAGE 1.3 COMPLETE — STOP GATE ACTIVE

## 1. Scope

Batch 1.3 executed:

- WOA-ELMFIS
- HHO-ELMFIS
- ACO-ELMFIS
- Bat-ELMFIS

Vanilla ELMFIS was re-run as the same-workflow anchor.

No Stage 1.4 method was started.

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

The canonical 5-rule ELMFIS and the Stage-1 optimization interface were retained:

- 8 standardized inputs;
- 4 outputs;
- 40 fuzzy-rule center parameters;
- 40 log-spread parameters;
- total optimized antecedent dimension = 80;
- TSK consequents solved analytically by ridge for each candidate antecedent structure.

Common protocol:
- population = 24;
- selection generations = 45;
- refit generations = 15;
- 3 deterministic repeats per target;
- chronological final-20% validation tail;
- validation never uses target-month information;
- final refit uses only pre-target history.

WOA, HHO, ACO and Bat preserve their ANN/ELM parity mechanics while moves/noise are bounded or scaled for the heterogeneous ELMFIS center/log-spread parameter space.

## 4. DEV results — selection authority

| Model | Sum absolute error (USD) | Direction | MAE | Relative MAE vs RW | RMSE |
|---|---:|---:|---:|---:|---:|
| **HHO-ELMFIS** | **1,857.89** | **22/33 = 66.67%** | 56.30 | 1.0568 | 68.24 |
| ACO-ELMFIS | 1,942.87 | 19/33 = 57.58% | 58.87 | 1.1052 | 71.55 |
| Vanilla ELMFIS | 1,996.29 | 20/33 = 60.61% | 60.49 | 1.1355 | 72.01 |
| Bat-ELMFIS | 2,137.83 | 19/33 = 57.58% | 64.78 | 1.2161 | 86.66 |
| WOA-ELMFIS | 2,536.55 | 15/33 = 45.45% | 76.87 | 1.4429 | 124.65 |

### DEV interpretation

Within Batch 1.3:
- HHO-ELMFIS is the clear batch leader on the active two-objective plane.
- ACO-ELMFIS has lower cumulative error than Vanilla but worse direction.
- Bat-ELMFIS and WOA-ELMFIS are weaker than Vanilla on both active objectives.

Across all first 12 Stage-1 entries:
- ABC-ELMFIS remains the provisional price-error side: **1,524.89 USD / 21/33**.
- HHO-ELMFIS becomes the provisional direction-side Pareto point: **1,857.89 USD / 22/33**.
- GWO-ELMFIS is now dominated by HHO because both have 22/33 direction, while HHO has lower cumulative error.

No family winner or refinement parent is frozen before the full Stage-1 broad screen and Stage-2 filtering.

## 5. Reporting-only external periods

These values are recorded for later robustness diagnosis only.

| Model | 2025 sum abs error | 2025 direction | 2026 Jan-Jul sum abs error | 2026 direction |
|---|---:|---:|---:|---:|
| WOA-ELMFIS | 1,875.06 | 10/12 = 83.33% | 2,040.94 | 4/7 = 57.14% |
| HHO-ELMFIS | 1,633.31 | 10/12 = 83.33% | 1,639.09 | 4/7 = 57.14% |
| ACO-ELMFIS | 997.08 | 10/12 = 83.33% | 1,724.82 | 4/7 = 57.14% |
| Bat-ELMFIS | 1,721.99 | 9/12 = 75.00% | 2,438.45 | 4/7 = 57.14% |

These periods did not affect optimizer tuning, model promotion, rejection, or Pareto status.

## 6. Implementation records

**Script:**  
`gold_axis_2026/tools/vw_midas_elmfis_meta_batch_3_v1.py`

**Workflow:**  
`.github/workflows/gold-midas-elmfis-meta-batch-3-v1.yml`

**Implementation commit:**  
`b65db00a2132eabcfa6cba5b17de63ef5a0df0ec`

**Workflow commit:**  
`509327c0546cdf75fbac9949a257483892a062fa`

**Run:**  
`36170874292`

All four optimizer branches, the Vanilla anchor, and the combined output gate passed.

## 7. Stage status

- ELMFIS Stage 0: COMPLETE.
- Stage 1 / Batch 1.1: COMPLETE.
- Stage 1 / Batch 1.2: COMPLETE.
- Stage 1 / Batch 1.3: **COMPLETE**.
- Completed Stage-1 entries: **12/33**.
- Remaining Stage-1 entries: **21/33**.
- Next planned batch: **Stage 1.4 — FA-ELMFIS + MFO-ELMFIS + FPA-ELMFIS + FA-FPA-ELMFIS**.
- **Do not start Stage 1.4 without explicit user confirmation.**

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
