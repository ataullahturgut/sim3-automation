# GOLD MONTHLY FORECAST — CHALLENGER B / HUBER V1 RESULT

**Date:** 2026-09-28  
**Status:** COMPLETE / SCIENTIFIC GATE PASS / NOT PROMOTED ON DEV  
**Workflow run:** 36431662688  
**Commit:** 24cb6aec7b96e1ad4ba1819261201cb3c35b2d7d  
**Freeze:** `GOLD_MONTHLY_CHALLENGER_B_HUBER_FREEZE_2026-09-28.md`

## B0 audit
PASS.

- Database remained READ_ONLY.
- Authority invariants were unchanged.
- Random split: NONE.
- Representation: CURRENT8, 8 features.
- Metals: Gold, Silver, Platinum, Palladium.
- Per metal: MR monthly log return + GPR-adaptive VW daily-log-return summary.
- GPR: exact-origin official Git PIT vintage with p-1 observation and causal normalization.
- Outer feature path does not dereference target-month metal values.
- StandardScaler fitted only inside the relevant training fold.
- Outer convergence warnings: 0.

## Frozen Huber method
- Estimator: sklearn HuberRegressor.
- Training history start: 2010-05.
- Alpha grid: 0, 0.0001, 0.001, 0.01, 0.1.
- Epsilon grid: 1.10, 1.20, 1.35, 1.50, 1.75, 2.00.
- max_iter = 5000; tol = 1e-8.
- Parameter selection: last 12 eligible pre-target months only.
- Selection objective: cumulative price AE / Random-Walk cumulative price AE.
- Target: next-month Gold log return.
- Price recovery: previous completed-month Gold average × exp(predicted return).

## DEV — selection authority, 2022-04..2024-12
- n = 33
- SigmaAE = **1530.1299616481554**
- MAE = **46.36757459539865**
- RMSE = **59.07571351747936**
- MAPE = **2.291119390839182%**
- WAPE = **2.2517547650709147%**
- Direction = **20/33 = 60.61%**
- Relative MAE vs Random Walk = **0.870381093087688**
- Random-Walk SigmaAE = **1758.0**
- Worst AE = **131.8773831794333**, 2024-03
- Mean training outlier fraction = **18.24%**
- Outer convergence warnings = **0**

Selected alpha counts on DEV:
- 0.1: 26 origins
- 0.01: 4 origins
- 0.001: 1 origin
- 0.0001: 1 origin
- 0.0: 1 origin

Selected epsilon counts on DEV:
- 2.00: 16 origins
- 1.50: 7 origins
- 1.35: 6 origins
- 1.75: 2 origins
- 1.20: 2 origins
- 1.10: 0 origins

## Challenger-A + Challenger-B DEV comparison
Primary ordering below is by SigmaAE only. Project interpretation remains two-objective: SigmaAE + direction.

| Price-error rank | Model | Family | DEV SigmaAE | Direction |
|---:|---|---|---:|---:|
| 1 | ChHHO-ANFIS | ANFIS | 1413.029779 | 23/33 |
| 2 | RBFNN DE-ABC | RBFNN | ~1415.8371 | 25/33 |
| 3 | GPR/MOGP LMC2_RBF_M32 | GPR/MOGP | ~1424.17 | 19/33 |
| 4 | FULL7 Equal ANN Ensemble | ANN | 1428.86 | 22/33 |
| 5 | REDUCED4 Equal ANN Ensemble | ANN | 1431.46 | 24/33 |
| 6 | SVR frozen parent | SVR | 1449.187363 | 19/33 |
| 7 | CatBoost PRICE | Boosting | 1460.433935 | 20/33 |
| 8 | Random Forest comparator | RF | 1491.550694 | 20/33 |
| 9 | Ridge V1 | Challenger-B | 1520.992603 | 21/33 |
| **10** | **Huber V1** | **Challenger-B** | **1530.129962** | **20/33** |
| 11 | Elastic Net V1 | Challenger-B | 1590.357052 | 16/33 |

The RBFNN and GPR/MOGP values remain explicitly approximate because that is how the current cross-family handoff records them; no false precision was introduced.

### Pareto check within this comparison pool
Huber V1 is dominated by:
- ChHHO-ANFIS
- RBFNN DE-ABC
- FULL7 Equal ANN Ensemble
- REDUCED4 Equal ANN Ensemble
- CatBoost PRICE
- Random Forest comparator
- Ridge V1

Therefore Huber does **not** enter the active Challenger-A price/direction frontier.

## 2025 — LOCKED REPORT ONLY
Not used for model selection, tuning, feature selection, rescue, or promotion.

- n = 12
- SigmaAE = **1051.8150202960865**
- MAE = **87.65125169134053**
- RMSE = **116.7104898895018**
- MAPE = **2.5210834710430037%**
- Direction = **10/12 = 83.33%**
- Relative MAE vs Random Walk = **0.6234825253681603**
- Random-Walk SigmaAE = **1687.0**
- Worst AE = **243.83223782492314**, 2025-10

## 2026 Jan-Jul — QUARANTINED REPORT ONLY
Not used for model selection or tuning.

- n = 7
- SigmaAE = **1412.0079048298553**
- MAE = **201.71541497569362**
- RMSE = **274.90264312328765**
- MAPE = **4.373964519304883%**
- Direction = **5/7 = 71.43%**
- Relative MAE vs Random Walk = **0.8516332357236763**
- Random-Walk SigmaAE = **1658.0**
- Worst AE = **450.62782754427917**, 2026-03

## Decision
Huber V1 is scientifically valid, beats Random Walk on DEV cumulative error, and runs cleanly without convergence warnings. However, it is worse than Ridge V1 on both primary SigmaAE and direction, and it is Pareto-dominated by multiple Challenger-A leaders.

**Decision: NOT PROMOTED.**

The existing Gold Monthly / Challenger-A path remains unchanged.

Result payload SHA256:
`78c36d12332e608665da903665ff85b18b98a8a5aeaa4dfcd3ca0851eaf02109`
