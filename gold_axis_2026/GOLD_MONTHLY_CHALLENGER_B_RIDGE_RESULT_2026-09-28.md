# GOLD MONTHLY FORECAST — CHALLENGER B / RIDGE V1 RESULT

**Date:** 2026-09-28  
**Status:** COMPLETE / SCIENTIFIC GATE PASS / NOT PROMOTED ON DEV  
**Workflow run:** 36429982904  
**Commit:** 331cf3dfd1afbcbfb158ad63393e1132ae2ade8c  
**Freeze:** `GOLD_MONTHLY_CHALLENGER_B_RIDGE_FREEZE_2026-09-28.md`

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

## Frozen Ridge method
- Estimator: sklearn Ridge.
- Training history start: 2010-05.
- Alpha grid: 0.01, 0.1, 1, 10, 100.
- Alpha selection: last 12 eligible pre-target months only.
- Selection objective: cumulative price AE / Random-Walk cumulative price AE.
- Outer fit: all matured pre-target rows.
- Target: next-month Gold log return.
- Price recovery: previous completed-month Gold average × exp(predicted return).

## DEV — selection authority, 2022-04..2024-12
- n = 33
- SigmaAE = **1520.9926031249222**
- MAE = **46.09068494317946**
- RMSE = **57.01753212190153**
- MAPE = **2.269407405029311%**
- WAPE = **2.2383081356273022%**
- Direction = **21/33 = 63.64%**
- Relative MAE vs Random Walk = **0.8651835057593414**
- Random-Walk SigmaAE = **1758.0**
- Worst AE = **131.38824466760002**, 2024-03

Selected alpha counts on DEV:
- alpha 100: 16 origins
- alpha 10: 15 origins
- alpha 1: 1 origin
- alpha 0.01: 1 origin
- alpha 0.1: 0 origins

### DEV-only comparison
- CatBoost PRICE: SigmaAE 1460.433935309605; direction 20/33
- Random Forest comparator: SigmaAE 1491.550693715667; direction 20/33
- Ridge V1: SigmaAE 1520.9926031249222; direction 21/33
- XGBoost CURRENT8 reference: SigmaAE 1583.8534958594905; direction 20/33

**Decision:** Ridge V1 is scientifically valid and beats Random Walk, but it does not improve the existing DEV price-error frontier. Therefore **NOT PROMOTED**. Its one additional correct direction versus CatBoost PRICE / RF does not offset the higher cumulative price error under the project's two-objective interpretation.

## 2025 — LOCKED REPORT ONLY
These results are not used for model selection, tuning, feature selection, rescue, or promotion.

- n = 12
- SigmaAE = **1060.2068814934664**
- MAE = **88.35057345778887**
- RMSE = **117.0147985716252**
- MAPE = **2.5372481203295214%**
- Direction = **10/12 = 83.33%**
- Relative MAE vs Random Walk = **0.6284569540565894**
- Random-Walk SigmaAE = **1687.0**
- Worst AE = **243.23381959390053**, 2025-10

Interpretation: strong retrospective transport signal, but it cannot rescue the DEV decision.

## 2026 Jan-Jul — QUARANTINED REPORT ONLY
These results are not used for model selection or tuning.

- n = 7
- SigmaAE = **1382.5045291944834**
- MAE = **197.50064702778334**
- RMSE = **269.0528657599838**
- MAPE = **4.292779048209562%**
- Direction = **5/7 = 71.43%**
- Relative MAE vs Random Walk = **0.8338386786456474**
- Random-Walk SigmaAE = **1658.0**
- Worst AE = **434.24701038402054**, 2026-03

## Governance decision
Ridge V1 is retained as a completed Challenger-B reference, not as a promoted main-model replacement. Existing Gold Monthly path remains unchanged.

The next Challenger-B method should be evaluated under the same frozen data/evaluation contract. Metal ablation remains a separate later experiment and must not be selected using 2025/2026 evidence.

Result payload SHA256:
`5e1511cd5d2d78888914cb4c6a91f2515e957b5907dbb25acdfbb8a4cde6770f`
