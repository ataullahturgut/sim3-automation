# GOLD MONTHLY FORECAST — CHALLENGER B / PLS1 V1 RESULT

**Date:** 2026-09-28  
**Status:** COMPLETE / SCIENTIFIC GATE PASS / HIGH-RANKING CHALLENGER / NOT PARETO-FRONTIER LEADER  
**Workflow run:** 36432505865  
**Commit:** 1390a094a96ca3eabf886fde65e85ee212886700  
**Freeze:** `GOLD_MONTHLY_CHALLENGER_B_PLS1_FREEZE_2026-09-28.md`

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
- Scaling is internal to PLSRegression(scale=True), fitted only on each training fold.
- Outer warnings: 0.

## Frozen PLS1 method
- Estimator: sklearn PLSRegression.
- Single target: next-month Gold log return.
- Training history start: 2010-05.
- n_components grid: 1..8.
- max_iter = 2000; tol = 1e-8.
- Component selection: last 12 eligible pre-target months only.
- Selection objective: cumulative price AE / Random-Walk cumulative price AE.
- Tie-break: fewer components.
- Price recovery: previous completed-month Gold average × exp(predicted return).

## DEV — selection authority, 2022-04..2024-12
- n = 33
- SigmaAE = **1420.0291314697745**
- MAE = **43.03118580211438**
- RMSE = **54.86549848149596**
- MAPE = **2.117516847404153%**
- WAPE = **2.0897292671025003%**
- Direction = **20/33 = 60.61%**
- Relative MAE vs Random Walk = **0.8077526345106795**
- Random-Walk SigmaAE = **1758.0**
- Worst AE = **130.29130828962343**, 2024-03
- Outer warning count = **0**

Selected component counts on DEV:
- 1 component: 12 origins
- 2 components: 11 origins
- 3 components: 10 origins
- 4..8 components: 0 origins

Important structural finding: although the grid allowed 1..8 latent components, every DEV origin selected only 1, 2, or 3 components. The CURRENT8 predictor space therefore appears compressible under this frozen PLS1 objective; this is a descriptive model finding, not a reason to retune from 2025/2026.

## Challenger-A + Challenger-B DEV comparison
Primary ordering below is by SigmaAE only. Project interpretation remains two-objective: SigmaAE + direction.

| Price-error rank | Model | Family | DEV SigmaAE | Direction |
|---:|---|---|---:|---:|
| 1 | ChHHO-ANFIS | ANFIS | 1413.029779 | 23/33 |
| 2 | RBFNN DE-ABC | RBFNN | ~1415.8371 | 25/33 |
| **3** | **PLS1 V1** | **Challenger-B** | **1420.029131** | **20/33** |
| 4 | GPR/MOGP LMC2_RBF_M32 | GPR/MOGP | ~1424.17 | 19/33 |
| 5 | FULL7 Equal ANN Ensemble | ANN | 1428.86 | 22/33 |
| 6 | REDUCED4 Equal ANN Ensemble | ANN | 1431.46 | 24/33 |
| 7 | SVR frozen parent | SVR | 1449.187363 | 19/33 |
| 8 | CatBoost PRICE | Boosting | 1460.433935 | 20/33 |
| 9 | Random Forest comparator | RF | 1491.550694 | 20/33 |
| 10 | Ridge V1 | Challenger-B | 1520.992603 | 21/33 |
| 11 | Huber V1 | Challenger-B | 1530.129962 | 20/33 |
| 12 | Elastic Net V1 | Challenger-B | 1590.357052 | 16/33 |

The RBFNN and GPR/MOGP values remain explicitly approximate because that is how the current cross-family records represent them.

### Pareto check
PLS1 V1 is dominated by:
- ChHHO-ANFIS
- RBFNN DE-ABC

Both have lower DEV SigmaAE and higher DEV direction count.

Therefore:
- **PLS1 enters the top cross-family price-error group.**
- **PLS1 is not on the active two-objective Pareto frontier.**
- It is nevertheless the strongest Challenger-B model tested so far by a wide margin.

## Challenger-B internal ranking
1. PLS1 V1 — **1420.03 / 20/33**
2. Ridge V1 — 1520.99 / 21/33
3. Huber V1 — 1530.13 / 20/33
4. Elastic Net V1 — 1590.36 / 16/33

## 2025 — LOCKED REPORT ONLY
Not used for model selection, tuning, feature selection, rescue, or promotion.

- n = 12
- SigmaAE = **1058.8965697409094**
- MAE = **88.24138081174245**
- RMSE = **116.38503915126061**
- MAPE = **2.536839587824273%**
- Direction = **10/12 = 83.33%**
- Relative MAE vs Random Walk = **0.6276802428813927**
- Random-Walk SigmaAE = **1687.0**
- Worst AE = **241.31368183821905**, 2025-10

## 2026 Jan-Jul — QUARANTINED REPORT ONLY
Not used for model selection or tuning.

- n = 7
- SigmaAE = **1392.6946381132939**
- MAE = **198.95637687332768**
- RMSE = **271.8739102202465**
- MAPE = **4.312377708712171%**
- Direction = **6/7 = 85.71%**
- Relative MAE vs Random Walk = **0.8399847033252678**
- Random-Walk SigmaAE = **1658.0**
- Worst AE = **445.96167029150547**, 2026-03

The strong 2026 direction result is report-only and cannot change the DEV decision.

## Decision
PLS1 V1 is scientifically valid and materially stronger than Ridge, Huber and Elastic Net on DEV price error.

**Decision: RETAIN AS STRONG CHALLENGER-B CANDIDATE.**

It does not replace the existing Challenger-A frontier because ChHHO-ANFIS and RBFNN DE-ABC dominate it on both DEV SigmaAE and DEV direction. However, its top-3 cross-family price-error result justifies continuing to the pre-planned PLS2 multi-output experiment under a separately frozen DEV-only protocol.

Existing Gold Monthly / Challenger-A path remains unchanged.

Result payload SHA256:
`56d354a09d9e7b7da50eef03309c7e6a5827ba5b4eba9ee8e608f314074eb0c7`
