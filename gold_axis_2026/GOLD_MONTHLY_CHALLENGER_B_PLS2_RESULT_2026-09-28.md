# GOLD MONTHLY FORECAST — CHALLENGER B / PLS2 V1 RESULT

**Date:** 2026-09-28  
**Status:** COMPLETE / SCIENTIFIC GATE PASS / RETAIN AS DIRECTION-IMPROVED PLS CHALLENGER  
**Workflow run:** 36433293277  
**Commit:** bff8a3f35f25671efd8e4274cecc9508a76592de  
**Freeze:** `GOLD_MONTHLY_CHALLENGER_B_PLS2_FREEZE_2026-09-28.md`

## B0 audit
PASS.

- Database remained READ_ONLY.
- Authority invariants unchanged.
- Random split: NONE.
- Representation: CURRENT8.
- Inputs: 8 predictors = MR + VW for Gold, Silver, Platinum, Palladium.
- Training outputs: 4 next-month metal log returns.
- Evaluation target: Gold price only.
- Exact-origin GPR PIT chronology preserved.
- PLS internal X/Y scaling fitted only inside each training fold.
- Outer feature builder does not dereference target-month metal values.
- Outer warnings: 0.

## Frozen PLS2 method
- Estimator: sklearn PLSRegression(scale=True).
- Multi-output targets: Gold, Silver, Platinum, Palladium next-month log returns.
- n_components grid: 1..8.
- Component selection: last 12 eligible pre-target months.
- Selection objective: Gold cumulative absolute price error / Gold RW cumulative absolute price error.
- Tie-break: fewer components.
- Training start: 2010-05.

## DEV — selection authority, 2022-04..2024-12
- n = 33
- SigmaAE = **1489.3300296660234**
- MAE = **45.13121302018253**
- RMSE = **55.86250072232989**
- MAPE = **2.2195929527107787%**
- WAPE = **2.1917131715082494%**
- Direction = **23/33 = 69.70%**
- Relative MAE vs Random Walk = **0.8471729406518904**
- Random-Walk SigmaAE = **1758.0**
- Worst AE = **128.5421926610568**, 2024-03
- Outer warning count = **0**

Selected component counts:
- 1 component: 10 origins
- 2 components: 2 origins
- 3 components: 8 origins
- 4 components: 11 origins
- 6 components: 2 origins
- 5,7,8 components: 0 origins

## PLS1 vs PLS2
| Model | DEV SigmaAE | Direction |
|---|---:|---:|
| PLS1 V1 | **1420.029131** | 20/33 |
| PLS2 V1 | 1489.330030 | **23/33** |

Interpretation:
- PLS1 is clearly stronger for the primary price-error objective.
- PLS2 improves DEV direction by 3 months.
- The joint 4-metal output therefore trades price accuracy for direction accuracy under this frozen protocol.
- This is a genuine DEV trade-off, not inferred from 2025/2026.

## Cross-family DEV context
Price-error ordering around PLS2:
1. ChHHO-ANFIS — 1413.029779 / 23
2. RBFNN DE-ABC — ~1415.8371 / 25
3. PLS1 V1 — 1420.029131 / 20
4. GPR/MOGP LMC2 — ~1424.17 / 19
5. FULL7 Equal ANN — 1428.86 / 22
6. REDUCED4 Equal ANN — 1431.46 / 24
7. SVR parent — 1449.187363 / 19
8. CatBoost PRICE — 1460.433935 / 20
9. **PLS2 V1 — 1489.330030 / 23**
10. Random Forest — 1491.550694 / 20
11. Ridge V1 — 1520.992603 / 21
12. Huber V1 — 1530.129962 / 20
13. Elastic Net V1 — 1590.357052 / 16

PLS2 is price-error rank **9/13** in this frozen comparison pool.

### Pareto check
PLS2 is dominated by:
- ChHHO-ANFIS
- RBFNN DE-ABC
- REDUCED4 Equal ANN Ensemble

Therefore PLS2 does not enter the active two-objective Pareto frontier.

However, PLS2 **dominates Random Forest** within this pool:
- lower SigmaAE: 1489.33 vs 1491.55
- higher direction: 23/33 vs 20/33

## Challenger-B internal ranking by DEV SigmaAE
1. PLS1 V1 — **1420.03 / 20/33**
2. PLS2 V1 — **1489.33 / 23/33**
3. Ridge V1 — 1520.99 / 21/33
4. Huber V1 — 1530.13 / 20/33
5. Elastic Net V1 — 1590.36 / 16/33

## 2025 — LOCKED REPORT ONLY
- n = 12
- SigmaAE = **1067.915363391668**
- MAE = **88.99294694930568**
- RMSE = **114.75691736525324**
- MAPE = **2.564089563532326%**
- Direction = **10/12 = 83.33%**
- Relative MAE vs RW = **0.6330262972090505**
- Worst AE = **231.07684245274186**, 2025-10

Not used for selection/tuning/promotion.

## 2026 Jan-Jul — QUARANTINED REPORT ONLY
- n = 7
- SigmaAE = **1361.8721049867768**
- MAE = **194.55315785525383**
- RMSE = **269.78522381624913**
- MAPE = **4.21514970053917%**
- Direction = **5/7 = 71.43%**
- Relative MAE vs RW = **0.821394514467296**
- Worst AE = **447.6893956784079**, 2026-03

Not used for selection/tuning/promotion.

## Decision
**RETAIN as a secondary PLS challenger, not as the primary PLS model.**

PLS1 remains the stronger PLS candidate for the primary price-error objective. PLS2 demonstrates that multi-output joint learning can improve DEV direction, but not enough to enter the current cross-family Pareto frontier.

Existing Gold Monthly / Challenger-A path remains unchanged.

Result payload SHA256:
`5dd9f8c5f05b611dd03f6e7e93ac77426bb8450c21cfe3e0b3ce8883ed9a241d`
