# GOLD MONTHLY FORECAST — CHALLENGER B / ELASTIC NET V1 RESULT

**Date:** 2026-09-28
**Status:** COMPLETE / SCIENTIFIC GATE PASS / NOT PROMOTED ON DEV
**Workflow run:** 36430681760
**Commit:** 51c64cfcc19b5a522d15e30badeb486ad023b93c
**Freeze:** `GOLD_MONTHLY_CHALLENGER_B_ELASTICNET_FREEZE_2026-09-28.md`

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
- StandardScaler is fitted only inside the relevant training fold.

## Frozen Elastic Net method
- Estimator: sklearn ElasticNet.
- Training history start: 2010-05.
- Alpha grid: 0.0001, 0.001, 0.01, 0.1, 1.0.
- L1-ratio grid: 0.10, 0.25, 0.50, 0.75, 0.90, 0.95.
- max_iter = 200000; tol = 1e-10; selection = cyclic.
- Parameter selection: last 12 eligible pre-target months only.
- Selection objective: cumulative price AE / Random-Walk cumulative price AE.
- Outer fit: all matured pre-target rows.
- Target: next-month Gold log return.
- Price recovery: previous completed-month Gold average × exp(predicted return).

## DEV — selection authority, 2022-04..2024-12
- n = 33
- SigmaAE = **1590.3570524947138**
- MAE = **48.19263795438527**
- RMSE = **59.3877105980463**
- MAPE = **2.3850885041172183%**
- WAPE = **2.340385562584362%**
- Direction = **16/33 = 48.48%**
- Relative MAE vs Random Walk = **0.9046399616010886**
- Random-Walk SigmaAE = **1758.0**
- Worst AE = **130.72359698064497**, 2024-03
- Mean zero coefficients = **4.4545 / 8**

DEV selected alpha counts:
- 0.0001: 4
- 0.001: 9
- 0.01: 18
- 0.1: 2
- 1.0: 0

DEV selected L1-ratio counts:
- 0.10: 16
- 0.25: 4
- 0.50: 2
- 0.75: 2
- 0.90: 2
- 0.95: 7

Zero-coefficient count distribution:
- 0 zeros: 3 origins
- 1 zero: 1 origin
- 3 zeros: 1 origin
- 4 zeros: 11 origins
- 5 zeros: 9 origins
- 6 zeros: 3 origins
- 7 zeros: 4 origins
- 8 zeros: 1 origin

## DEV-only comparison
- CatBoost PRICE: SigmaAE 1460.433935309605; direction 20/33
- CatBoost BALANCED: SigmaAE 1481.261937710369; direction 22/33
- Random Forest comparator: SigmaAE 1491.550693715667; direction 20/33
- Ridge V1: SigmaAE 1520.9926031249222; direction 21/33
- Elastic Net V1: SigmaAE **1590.3570524947138**; direction **16/33**
- XGBoost CURRENT8 reference: SigmaAE 1583.8534958594905; direction 20/33

**Decision:** Elastic Net V1 is scientifically valid and beats Random Walk on cumulative price error, but is NOT PROMOTED. It is worse than Ridge V1 on both DEV SigmaAE and direction accuracy, and worse than the existing CatBoost/RF frontier.

The sparsity diagnostic is informative but not a causal proof: Elastic Net zeroed an average of 4.45 of 8 standardized coefficients, with one DEV origin zeroing all eight. Under this frozen grid and selection rule, the resulting sparse linear representation did not preserve enough directional signal.

## 2025 — LOCKED REPORT ONLY
Not used for model selection, tuning, feature selection, rescue, or promotion.

- n = 12
- SigmaAE = **1078.903948906771**
- MAE = **89.90866240889757**
- RMSE = **120.07656449291316**
- MAPE = **2.566592262036899%**
- Direction = **11/12 = 91.67%**
- Relative MAE vs Random Walk = **0.6395399815689217**
- Random-Walk SigmaAE = **1687.0**
- Worst AE = **248.38451977864088**, 2025-10
- Mean zero coefficients = **5.0833 / 8**

Interpretation: retrospective 2025 direction performance is strong, but the period is locked and cannot rescue the DEV decision.

## 2026 Jan-Jul — QUARANTINED REPORT ONLY
Not used for model selection or tuning.

- n = 7
- SigmaAE = **1401.1089398470785**
- MAE = **200.1584199781541**
- RMSE = **262.1006700093032**
- MAPE = **4.342317612946911%**
- Direction = **5/7 = 71.43%**
- Relative MAE vs Random Walk = **0.8450596742141607**
- Random-Walk SigmaAE = **1658.0**
- Worst AE = **416.21100230680986**, 2026-01
- Mean zero coefficients = **5.2857 / 8**

## Governance decision
Elastic Net V1 is retained as a completed Challenger-B reference and is **NOT PROMOTED**. The existing Gold Monthly path remains unchanged.

Ridge remains the stronger of the two linear Challenger-B models on DEV, but Ridge itself was also not promoted against the existing frontier.

Metal ablation remains a separate later experiment and must not be selected from 2025/2026 evidence.

Result payload SHA256:
`bb506c202621ab00b691ca0de697e14c45a1b165e6e06d659c221f663193e261`
