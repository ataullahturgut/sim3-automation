# GOLD MONTHLY FORECAST — ELMFIS STAGE 3A MANDATORY REFINEMENTS

**Date:** 2026-09-26  
**Status:** STAGE 3A COMPLETE — STOP GATE ACTIVE

## 1. Authority

Selection authority remained DEV 2022-04..2024-12 (n=33) only.

Frozen contract:
- H=1 next-calendar-month average XAU/USD.
- governed 8 origin-safe VW-MIDAS inputs.
- canonical 5-rule ELMFIS.
- antecedent centers + log-spreads are the nonlinear search space.
- TSK consequents solved analytically by ridge.
- chronological inner validation only.
- no random split.
- DB READ_ONLY.
- target month excluded from all fitness/tuning.
- 2025 transport and 2026 Jan-Jul stress are reporting-only.

## 2. Executed Stage 3A methods

All six predeclared mandatory refinement/parity methods were executed:

1. Adaptive PSO-ELMFIS
2. TLBO-tuned PSO-ELMFIS
3. DE-tuned PSO-ELMFIS
4. Adaptive / Improved TLBO-ELMFIS
5. Adaptive Crow Search-ELMFIS
6. PSO-TLBO Hybrid ELMFIS

No additional optimizer was introduced after seeing results.

## 3. DEV results

| Model | DEV ΣAE USD | Direction | MAE | RMSE | Rel MAE vs RW | Worst APE |
|---|---:|---:|---:|---:|---:|---:|
| **TLBO-tuned PSO-ELMFIS** | **1,574.26** | 19/33 = 57.58% | 47.70 | 62.66 | **0.8955** | **6.71%** |
| Adaptive Crow Search-ELMFIS | 1,765.35 | 19/33 = 57.58% | 53.50 | 73.08 | 1.0042 | 8.38% |
| DE-tuned PSO-ELMFIS | 1,814.60 | 20/33 = 60.61% | 54.99 | 70.44 | 1.0322 | 8.44% |
| PSO-TLBO Hybrid ELMFIS | 1,920.75 | 21/33 = 63.64% | 58.20 | 72.48 | 1.0926 | 8.18% |
| Adaptive / Improved TLBO-ELMFIS | 2,224.53 | 21/33 = 63.64% | 67.41 | 96.85 | 1.2654 | 16.04% |
| Adaptive PSO-ELMFIS | 2,861.50 | **22/33 = 66.67%** | 86.71 | 200.95 | 1.6277 | 57.93% |

Reference Stage-1 frontier:
- **ABC-ELMFIS:** 1,524.89 USD / 21/33 = 63.64%.
- **SMA-ELMFIS:** 1,651.45 USD / 25/33 = 75.76%.

## 4. DEV interpretation

No Stage-3A method improves the active Stage-1 Pareto frontier.

- TLBO-tuned PSO is the Stage-3A price leader at 1,574.26 USD, but ABC has both lower ΣAE (1,524.89) and higher direction (21/33 vs 19/33), so TLBO-tuned PSO is dominated.
- Adaptive PSO reaches 22/33 direction but its ΣAE explodes to 2,861.50 USD; SMA has substantially lower ΣAE and higher direction, so it is dominated.
- PSO-TLBO Hybrid matches ABC's 21/33 direction but has 395.87 USD more DEV cumulative absolute error.
- Adaptive Crow, DE-tuned PSO and Adaptive TLBO are also dominated by the existing ABC/SMA frontier.

**Stage-3A frontier contribution: NONE.**

The Stage-2 frozen parent roles therefore remain unchanged:
- ABC-ELMFIS — primary price parent.
- SMA-ELMFIS — direction/complementarity parent.
- HHO-ELMFIS — year/tail-stability parent.

## 5. Reporting-only external periods

These values did not participate in model selection:

| Model | 2025 ΣAE | 2025 Direction | 2026 Jan-Jul ΣAE | 2026 Direction |
|---|---:|---:|---:|---:|
| Adaptive PSO | 2,083.97 | 10/12 | 1,618.32 | 4/7 |
| Adaptive TLBO | 1,352.21 | 9/12 | 36,419.21 | 4/7 |
| TLBO-tuned PSO | 1,087.91 | 10/12 | 2,211.53 | 3/7 |
| DE-tuned PSO | **992.90** | **11/12** | 1,657.69 | 3/7 |
| Adaptive Crow | 3,973.48 | 8/12 | 2,714.80 | 3/7 |
| PSO-TLBO Hybrid | 1,608.37 | 10/12 | 1,777.98 | 3/7 |

Adaptive TLBO shows a severe 2026 stress instability. This is recorded as a robustness warning only and did not affect DEV selection.

## 6. Runs and artifacts

### Batch 3.1
Workflow run: **36191026571 — SUCCESS**
- Adaptive PSO artifact: 10887873045
- Adaptive TLBO artifact: 10887878980

### Batch 3.2
Workflow run: **36190917448 — SUCCESS**
- TLBO-tuned PSO artifact: 10887704625
- DE-tuned PSO artifact: 10887968942

### Batch 3.3
Workflow run: **36190990837 — SUCCESS**
- Adaptive Crow artifact: 10888685967
- PSO-TLBO Hybrid artifact: 10888043130

## 7. Stage status

- Stage 0: COMPLETE.
- Stage 1: COMPLETE — 33/33.
- Stage 2: COMPLETE — parent freeze.
- Stage 3A: **COMPLETE — 6/6**.
- Stage 3A new Pareto point: **NO**.
- Stage 3B: NOT STARTED.
- Stage 3C: NOT STARTED.

Next binding stage after user approval:
**Stage 3B — MPA+SCA, MPA+GA, MPA+CPA Hybrid ELMFIS.**

## 8. Control and compliance summary

- DB READ_ONLY: PASS.
- Random split absent: PASS.
- Chronological inner validation: PASS.
- Target-month leakage absent: PASS.
- Frozen 8-feature contract: PASS.
- DEV-only selection/tuning: PASS.
- 2025 selection exclusion: PASS.
- 2026 selection exclusion: PASS.
- Canonical ELMFIS unchanged: PASS.
- TSK consequents analytic ridge: PASS.
- Predeclared six methods completed: PASS.
- Post-hoc method expansion: NO.
- Stage 3A: COMPLETE.
- Next authorized stage: Stage 3B after explicit user approval.
