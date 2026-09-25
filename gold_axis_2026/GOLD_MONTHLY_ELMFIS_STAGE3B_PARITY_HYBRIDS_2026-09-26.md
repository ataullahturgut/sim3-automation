# GOLD MONTHLY FORECAST — ELMFIS STAGE 3B PARITY HYBRIDS

**Date:** 2026-09-26  
**Status:** STAGE 3B COMPLETE — STOP GATE ACTIVE

## 1. Authority

Selection/tuning authority remained DEV 2022-04..2024-12 (n=33) only.

Frozen contract:
- H=1 next-calendar-month average XAU/USD.
- governed 8 origin-safe VW-MIDAS inputs.
- canonical 5-rule ELMFIS.
- antecedent centers + log-spreads as nonlinear search space.
- TSK consequents solved analytically by ridge.
- no random split.
- chronological inner validation.
- DB READ_ONLY.
- target month excluded from fitness/tuning.
- 2025 and 2026 reporting-only.

## 2. Executed Stage 3B hybrids

All three predeclared ANN-parity hybrids were executed:

1. MPA+SCA Hybrid ELMFIS
2. MPA+GA Hybrid ELMFIS
3. MPA+CPA Hybrid ELMFIS

Hybrid mechanism:
- one shared population;
- each generation creates MPA proposals and second-optimizer proposals;
- incumbent + MPA + second-optimizer pool compete by inner-training weighted MAE;
- best 24 survive;
- validation does not drive population evolution;
- 3 deterministic repeats per target;
- full-history refit after DEV-safe repeat selection.

## 3. DEV results

| Model | DEV ΣAE USD | Direction | MAE | RMSE | Rel MAE vs RW | Worst APE |
|---|---:|---:|---:|---:|---:|---:|
| **MPA+GA Hybrid ELMFIS** | **1,675.89** | **21/33 = 63.64%** | 50.78 | 65.95 | **0.9533** | 9.32% |
| MPA+SCA Hybrid ELMFIS | 2,549.81 | **21/33 = 63.64%** | 77.27 | 109.20 | 1.4504 | 21.87% |
| MPA+CPA Hybrid ELMFIS | 3,546.16 | 17/33 = 51.52% | 107.46 | 255.16 | 2.0172 | 69.34% |

Reference frontier:
- **ABC-ELMFIS:** 1,524.89 USD / 21/33 = 63.64%.
- **SMA-ELMFIS:** 1,651.45 USD / 25/33 = 75.76%.

## 4. DEV interpretation

No Stage-3B hybrid improves the existing Pareto frontier.

- MPA+GA is the best Stage-3B result. It matches ABC at 21/33 direction but has higher cumulative error: 1,675.89 vs 1,524.89 USD. It is therefore dominated by ABC. It is also dominated by SMA because SMA has both lower ΣAE (1,651.45) and higher direction (25/33).
- MPA+SCA is materially worse on price error and provides no direction gain over ABC.
- MPA+CPA is weak on both active objectives.

**Stage-3B frontier contribution: NONE.**

The Stage-2 frozen parent roles remain unchanged:
- ABC-ELMFIS — primary price parent.
- SMA-ELMFIS — direction/complementarity parent.
- HHO-ELMFIS — year/tail-stability parent.

## 5. Reporting-only external periods

These values did not participate in selection:

| Model | 2025 ΣAE | 2025 Direction | 2026 Jan-Jul ΣAE | 2026 Direction |
|---|---:|---:|---:|---:|
| MPA+SCA | 1,415.60 | 10/12 | 15,155.86 | 4/7 |
| MPA+GA | 1,748.46 | 9/12 | 11,217.29 | 4/7 |
| MPA+CPA | **1,149.63** | 9/12 | 2,859.43 | 3/7 |

MPA+SCA and MPA+GA show severe 2026 stress instability. This is recorded only as robustness evidence and did not affect DEV selection.

## 6. Run and artifacts

Workflow run: **36192286854 — SUCCESS**

Artifacts:
- MPA+SCA: **10888702749**
- MPA+GA: **10888502699**
- MPA+CPA: **10888955934**

Workflow commit:
`bfa2f600ab9069b8f88d33ff74a59f397481cbb6`

Implementation:
`gold_axis_2026/tools/vw_midas_elmfis_stage3b_v1.py`

Workflow:
`.github/workflows/gold-midas-elmfis-stage3b-v1.yml`

## 7. Stage status

- Stage 0: COMPLETE.
- Stage 1: COMPLETE — 33/33.
- Stage 2: COMPLETE.
- Stage 3A: COMPLETE — 6/6.
- Stage 3B: **COMPLETE — 3/3**.
- Stage 3B new Pareto point: **NO**.
- Stage 3C: NOT STARTED.

Next binding stage after user approval:
**Stage 3C — CQCSA-ELMFIS.**

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
- Predeclared three Stage-3B hybrids completed: PASS.
- Post-hoc method expansion: NO.
- Stage 3B: COMPLETE.
- Next authorized stage: Stage 3C after explicit user approval.
