# GOLD MONTHLY FORECAST — BOOSTING STAGE 6C-A CMA-ES–GBRT REPORT

Date: 2026-09-27
Status: COMPLETE / SCIENTIFIC GATE PASS / NOT PROMOTED

## 1. Purpose
Test the direct monthly-gold literature signal that CMA-ES hyperparameter optimization can improve Gradient Boosting, while preserving the project's origin-safe H=1 chronology.

Authority:
Suan, J. S. P., Anbananthen, K. S. M., & Kanan, R. K. (2026),
"Gold Price Forecasting Using Machine Learning Models with Hyperparameter Optimization for Inflation Hedging",
Emerging Science Journal 10(3), 1473–1490,
DOI 10.28991/ESJ-2026-010-03-016.

This project run is an origin-safe adaptation, not an exact reproduction.

## 2. Frozen protocol
- Model: sklearn GradientBoostingRegressor.
- Representation: DAILY_SUMMARY12.
- Target: next-month Gold log return.
- Price reconstruction: previous completed-month Gold average × exp(predicted return).
- Loss: absolute_error.
- DEV: 2022-04..2024-12, n=33.
- Per outer origin: last 12 pre-target months inner validation; all earlier history inner training.
- CMA-ES: cma 4.5.0; popsize 8; 10 generations; exactly 80 objective calls/origin.
- Total CMA-ES objective calls: 2640.
- Unique decoded candidates: 2640.
- Random split: NONE.
- DB: READ_ONLY.
- 2025: NOT OPENED.
- 2026: QUARANTINED / NOT USED IN DEVELOPMENT.

Pre-outcome freeze:
`GOLD_MONTHLY_BOOSTING_STAGE6C_A_CMAES_GBRT_FREEZE_2026-09-27.md`

Parallel execution changed wall-clock scheduling only. Every target retained the same frozen target-specific seed, search space and 80-call budget.

## 3. Full DEV result

| Model | DEV ΣAE ↓ | MAE | RMSE | MAPE | Direction | Rel MAE vs RW | Worst AE |
|---|---:|---:|---:|---:|---:|---:|---:|
| Frozen GBRT baseline | **1500.4295** | **45.4676** | **58.2166** | **2.2175%** | **22/33 = 66.67%** | **0.8535** | 159.8298 |
| CMA-ES–GBRT | 1650.1985 | 50.0060 | 60.9105 | 2.4382% | 18/33 = 54.55% | 0.9387 | **157.2709** |

CMA-ES minus baseline:
- ΣAE: +149.7690 USD, **9.9817% worse**.
- Direction: -4 correct months.
- Outer-origin AE wins: CMA-ES 15/33; baseline 18/33.
- CMA-ES produced no direction rescue relative to baseline and lost four baseline-correct directions: 2022-10, 2023-09, 2024-01, 2024-08.

## 4. Year-by-year DEV

| Year | Baseline ΣAE | CMA-ES ΣAE | Baseline direction | CMA-ES direction |
|---|---:|---:|---:|---:|
| 2022 Apr-Dec | 415.9404 | **392.7446** | 7/9 | 6/9 |
| 2023 | **428.1815** | 543.0934 | 6/12 | 5/12 |
| 2024 | **656.3076** | 714.3605 | 9/12 | 7/12 |

CMA-ES improves price ΣAE in 2022 but fails to transport that improvement through 2023 and 2024.

## 5. Inner-vs-outer diagnostic
CMA-ES looked very strong on its chronological inner validation:
- mean inner ratio vs frozen GBRT = **0.8722166**;
- median inner ratio = **0.8633923**;
- CMA-ES beat the frozen GBRT inner score in **32/33** outer origins;
- worst inner ratio = 1.0483654.

Despite this, full outer DEV ΣAE deteriorated from 1500.4295 to 1650.1985.

Interpretation:
- the optimizer successfully fits the moving 12-month inner window;
- that gain does not generalize reliably to the next unseen month;
- this is direct evidence of hyperparameter-selection instability / local-regime overfit under the project's small monthly sample.

The result is therefore stronger evidence than a simple full-DEV hyperparameter search: the failure occurs under nested chronological validation, not because of random-split methodology.

## 6. Parameter behavior diagnostic
Selected tree depth counts across 33 origins:
- depth 1: 14
- depth 2: 9
- depth 3: 2
- depth 4: 5
- depth 5: 3

CMA-ES frequently preferred very shallow models, but the selected capacity varied materially across origins. This is retained as a diagnostic only; no post-hoc restricted search is authorized from this observation.

## 7. Reconciliation
The frozen Stage-5 GBRT comparator reproduced exactly:
- expected DEV ΣAE: 1500.42946858865
- replay DEV ΣAE: 1500.42946858865
- expected direction: 22/33
- replay direction: 22/33

Baseline reconciliation: PASS.

## 8. Execution provenance
Canonical parallel run:
- workflow run: **36346760813**
- 11 independent 3-month chunks
- all 11 jobs: SUCCESS
- all chunk scientific gates: PASS
- total outer origins: 33
- total objective calls: 2640

A slower monolithic equivalence run (36346283656) was also launched before parallelization; the parallel run is sufficient canonical evidence because each outer origin is scientifically independent and uses identical deterministic frozen logic.

## 9. Decision
**CMA-ES–GBRT is NOT PROMOTED.**

Reason:
- worse primary DEV ΣAE;
- worse direction;
- improvement only in 2022, not stable across 2023/2024;
- pronounced inner-validation success does not transfer to outer next-month forecasts.

The literature hypothesis was legitimately tested and rejected under this project's chronology/data contract. Do not retune CMA-ES using these outer outcomes.

## 10. Next predeclared Boosting-specific challenger
Next candidate from the authority scan:
**TPE/Optuna–GBRT control**, using the same lane and same nested chronology, before opening decomposition-based challengers.

No TPE outcome has been observed at the time of this report.
