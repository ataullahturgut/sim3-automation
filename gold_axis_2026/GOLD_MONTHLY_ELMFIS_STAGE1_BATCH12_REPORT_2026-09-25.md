# GOLD MONTHLY FORECAST — ELMFIS STAGE 1 / BATCH 1.2 REPORT

**Date:** 2026-09-25  
**Repository:** ataullahturgut/sim3-automation  
**Branch:** gold-midas-headswap-v1-20260925  
**Workflow run:** 36170049225 — SUCCESS / OUTPUT_GATE=PASS  
**Status:** STAGE 1.2 COMPLETE — STOP GATE ACTIVE

## 1. Scope

Batch 1.2 executed the next four optimized ELMFIS variants under the frozen monthly H=1 contract:

- MPA-ELMFIS
- ABC-ELMFIS
- SSA-ELMFIS
- GWO-ELMFIS

Vanilla ELMFIS was re-run in the same workflow as the baseline anchor.

No Stage 1.3 method was started.

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

## 3. Optimized ELMFIS contract

The Stage-0 canonical ELMFIS structure and Stage-1.1 optimization interface were retained:

- 8 standardized inputs;
- 5 fuzzy rules;
- 4 outputs;
- Gaussian/bell antecedent membership;
- product AND with normalized firing strength;
- first-order TSK consequent;
- analytic ridge consequent fitting;
- 40 rule-center parameters + 40 log-spread parameters = 80 optimized antecedent parameters.

TSK consequent coefficients were not searched by the metaheuristics.

Common optimization protocol:

- population reference = 24;
- selection generations = 45;
- full-history refit generations = 15;
- deterministic repeats = 3;
- chronological final 20% validation tail, minimum 6 rows;
- population evolution objective = 0.7 × Gold standardized MAE + 0.3 × all-output standardized MAE on inner training;
- validation selects only among candidates already strong on inner-training loss;
- full-history refit uses only pre-target history.

Batch-specific methods preserve their established ANN/ELM parity logic while respecting heterogeneous ELMFIS center/log-spread bounds.

## 4. DEV results — selection authority

| Model | Sum absolute error (USD) | Direction | MAE | Relative MAE vs RW | RMSE |
|---|---:|---:|---:|---:|---:|
| **ABC-ELMFIS** | **1,524.89** | **21/33 = 63.64%** | 46.21 | 0.8674 | 58.61 |
| GWO-ELMFIS | 1,943.56 | **22/33 = 66.67%** | 58.90 | 1.1056 | 75.64 |
| Vanilla ELMFIS | 1,996.29 | 20/33 = 60.61% | 60.49 | 1.1355 | 72.01 |
| SSA-ELMFIS | 2,124.48 | 20/33 = 60.61% | 64.38 | 1.2085 | 85.34 |
| MPA-ELMFIS | 3,060.59 | 19/33 = 57.58% | 92.75 | 1.7409 | 168.00 |

### DEV interpretation

Within Batch 1.2:

- ABC-ELMFIS is the clear price-error leader and also improves direction over Vanilla.
- GWO-ELMFIS has the strongest direction result in the batch (22/33) but materially higher cumulative error than ABC.
- SSA-ELMFIS is weaker than Vanilla on cumulative error and does not improve direction.
- MPA-ELMFIS is weak on DEV under the active selection authority.

Across all Stage-1 entries completed so far (Vanilla, PSO, GA, DE, MPA, ABC, SSA, GWO), the current provisional DEV Pareto set is:

- **ABC-ELMFIS:** 1,524.89 USD / 21/33 direction;
- **GWO-ELMFIS:** 1,943.56 USD / 22/33 direction.

DE-ELMFIS is no longer on the provisional frontier because ABC has lower error at the same 21/33 direction.

This is not a family winner or parent freeze. The full Stage-1 broad screen remains mandatory.

## 5. Reporting-only external periods

These values are recorded only for later transport/stress diagnosis and did not influence model promotion, rejection, tuning, or weighting.

| Model | 2025 sum abs error | 2025 direction | 2026 Jan-Jul sum abs error | 2026 direction |
|---|---:|---:|---:|---:|
| ABC-ELMFIS | 1,318.39 | 7/12 = 58.33% | 2,520.68 | 2/7 = 28.57% |
| GWO-ELMFIS | 1,069.99 | 9/12 = 75.00% | 4,417.64 | 5/7 = 71.43% |
| SSA-ELMFIS | 1,612.85 | 9/12 = 75.00% | 1,899.22 | 4/7 = 57.14% |
| MPA-ELMFIS | 1,634.43 | 8/12 = 66.67% | 1,263.95 | 6/7 = 85.71% |

The strong-looking 2026 MPA direction/error behavior does not change its weak DEV status because 2026 is reporting-only.

## 6. Implementation records

**Script:**  
`gold_axis_2026/tools/vw_midas_elmfis_meta_batch_2_v1.py`

**Workflow:**  
`.github/workflows/gold-midas-elmfis-meta-batch-2-v1.yml`

**Implementation commit:**  
`c7c5682d47f2204d73ce7d252d019a3799dd1bae`

**Workflow commit:**  
`45ce007276fca56f4ad8a16f9933087d2d2271f3`

**Run:**  
`36170049225`

All four optimizer branches, the Vanilla anchor, and the combined batch gate passed.

## 7. Stage status

- ELMFIS Stage 0: COMPLETE.
- ELMFIS Stage 1 / Batch 1.1: COMPLETE.
- ELMFIS Stage 1 / Batch 1.2: **COMPLETE**.
- Completed Stage-1 entries: Vanilla, PSO, GA, DE, MPA, ABC, SSA, GWO = **8/33**.
- Remaining Stage-1 entries: **25/33**.
- Next planned batch: **Stage 1.3 — WOA-ELMFIS + HHO-ELMFIS + ACO-ELMFIS + Bat-ELMFIS**.
- **Do not start Stage 1.3 without explicit user confirmation.**

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
