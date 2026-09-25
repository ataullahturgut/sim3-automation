# GOLD MONTHLY FORECAST — ELMFIS STAGE 1 / BATCH 1.9 REPORT

**Date:** 2026-09-25  
**Repository:** ataullahturgut/sim3-automation  
**Branch:** gold-midas-headswap-v1-20260925  
**Workflow run:** 36177121360 — SUCCESS / OUTPUT_GATE=PASS  
**Status:** STAGE 1.9 COMPLETE — STAGE 1 BROAD SCREEN CLOSED 33/33

## 1. Scope

Batch 1.9 executed:

- DE-ABC-ELMFIS
- Multi-swarm-ELMFIS

Vanilla ELMFIS was re-run as the same-workflow anchor.

All four jobs in run 36177121360 completed successfully:
- optimize (DE_ABC): SUCCESS
- optimize (MULTISWARM): SUCCESS
- baseline-anchor: SUCCESS
- batch-gate: SUCCESS

The combined artifact gate passed. Existing Stage-1 models were not re-run outside the workflow anchor.

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
- population reference = 24;
- selection generations = 45;
- refit generations = 15;
- 3 deterministic repeats per target;
- chronological final-20% validation tail;
- validation does not use target-month information;
- final refit uses only pre-target history.

DE-ABC parameters:
- F = 0.7
- CR = 0.9
- scout_limit = 10

Multi-swarm parameters:
- 3 swarms
- 8 particles per swarm
- elite exchange every 10 generations

## 4. DEV results — selection authority

| Model | Sum absolute error (USD) | Direction | MAE | RMSE | Worst APE |
|---|---:|---:|---:|---:|---:|
| **Multi-swarm-ELMFIS** | **1,848.10** | **18/33 = 54.55%** | 56.00 | 77.24 | 11.14% |
| Vanilla ELMFIS | 1,996.29 | 20/33 = 60.61% | 60.49 | 72.01 | 6.80% |
| DE-ABC-ELMFIS | 2,317.34 | 17/33 = 51.52% | 70.22 | 110.49 | 25.38% |

### DEV interpretation

Within Batch 1.9:
- Multi-swarm-ELMFIS is the batch leader on cumulative error.
- It improves cumulative error versus Vanilla but loses direction accuracy.
- DE-ABC-ELMFIS is weak on both active objectives relative to the strongest Stage-1 candidates.

Across all 33 Stage-1 entries, the DEV Pareto frontier remains:
- **ABC-ELMFIS:** 1,524.8854 USD / 21/33 = 63.64% — price-error side.
- **SMA-ELMFIS:** 1,651.4482 USD / 25/33 = 75.76% — direction/trade-off side.

Neither Batch-1.9 model changes the frontier.

No family winner or Stage-3 refinement parent is frozen here. That belongs to Stage 2 DEV-only filtering.

## 5. Reporting-only external periods

These values are recorded only for later transport/stress diagnosis and did not influence selection:

| Model | 2025 sum abs error | 2025 direction | 2026 Jan-Jul sum abs error | 2026 direction |
|---|---:|---:|---:|---:|
| DE-ABC-ELMFIS | 2,395.12 | 9/12 = 75.00% | 1,957.17 | 4/7 = 57.14% |
| Multi-swarm-ELMFIS | 1,697.95 | 10/12 = 83.33% | 1,922.98 | 4/7 = 57.14% |

These reporting-only periods did not alter tuning, Pareto status or promotion.

## 6. Implementation records

**Script:**  
`gold_axis_2026/tools/vw_midas_elmfis_meta_batch_9_v1.py`

**Workflow:**  
`.github/workflows/gold-midas-elmfis-meta-batch-9-v1.yml`

**Workflow head commit:**  
`32aac8127dbcbcba7579907cc69c3607c72ae80d`

**Run:**  
`36177121360`

**Artifacts:**
- combined: `10883225174`
- DE-ABC: `10882144818`
- Multi-swarm: `10882588061`
- Vanilla anchor: `10882389025`

All artifacts were valid and unexpired at verification time.

## 7. Stage status

- ELMFIS Stage 0: COMPLETE.
- Stage 1 / Batch 1.1: COMPLETE.
- Stage 1 / Batch 1.2: COMPLETE.
- Stage 1 / Batch 1.3: COMPLETE.
- Stage 1 / Batch 1.4: COMPLETE.
- Stage 1 / Batch 1.5: COMPLETE.
- Stage 1 / Batch 1.6: COMPLETE.
- Stage 1 / Batch 1.7: COMPLETE.
- Stage 1 / Batch 1.8: COMPLETE.
- Stage 1 / Batch 1.9: **COMPLETE**.
- Completed Stage-1 entries: **33/33**.
- Remaining Stage-1 entries: **0/33**.
- Stage 1 broad screen: **CLOSED**.
- Next planned stage: **Stage 2 — DEV-only filtering and parent freeze**.
- **Do not start Stage 2 without explicit user confirmation.**

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
- Completed Stage-1 methods re-run for selection: NO.
- Stage 1 complete: YES.

**KULLANICI ONAYI BEKLENİYOR — STAGE 2 BAŞLATILMADI.**
