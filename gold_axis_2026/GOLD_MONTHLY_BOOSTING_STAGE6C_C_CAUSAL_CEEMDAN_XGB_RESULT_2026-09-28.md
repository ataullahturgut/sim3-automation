# GOLD MONTHLY FORECAST — BOOSTING STAGE 6C-C CAUSAL CEEMDAN–XGBOOST RESULT

Date: 2026-09-28
Status: COMPLETE / SCIENTIFIC GATE PASS / NOT PROMOTED

## Method
Gold-specific CEEMDAN-XGBoost structural challenger adapted to the project's strict origin-safe H=1 monthly protocol.

Authority:
- Xin Xie (2025), "Research on Gold Price Prediction Model Based on CEEMDAN-XGBoost",
  Academic Journal of Science and Technology, 18(2), 88–95.
  DOI: 10.54097/27p05m50.
- CEEMDAN implementation: PyEMD / EMD-signal 1.10.0.
- Moving-front causal decomposition used to eliminate full-series decomposition leakage.

Project adaptation:
- monthly authoritative Gold average levels
- each feature generated from a prefix ending at target t-1
- four endpoint IMF features
- residual excluded
- XGBoost Stage-5 CURRENT8 X_R4_COMBO learner frozen unchanged
- training target = next-month Gold log return
- DEV only = 2022-04..2024-12, n=33
- 2025 = NOT OPENED
- 2026 = QUARANTINED / NOT USED IN DEVELOPMENT
- random split = NONE
- DB = READ_ONLY
- no CEEMDAN tuning
- no XGBoost tuning

## Scientific gates
- CEEMDAN smoke/determinism gate: PASS
- output gate: PASS
- scientific gate: PASS
- database authority invariants unchanged: PASS
- maximum reconstruction relative error: 1.7687567128995104e-16
- feature payload SHA256: 36a5d40e9d156f2e96ba28f9322496d43366def8aa75aadbb04e936ebb944356

PyEMD returned between 3 and 5 IMF arrays across prefixes even with max_imf=4; the frozen representation always used only the first four IMF endpoint slots and zero-padded when fewer than four were available. Residual was never used as a feature.

## Frozen XGBoost CURRENT8 comparator
- DEV SigmaAE: 1583.8534958594905
- MAE: 47.9955604806
- RMSE: 61.0528338569
- MAPE: 2.3212903741%
- WAPE: 2.3308148627%
- relative MAE vs RW: 0.9009405551
- direction: 20/33 = 60.61%
- worst AE: 139.8069155695

Yearly:
- 2022: SigmaAE 383.0717717760, direction 5/9
- 2023: SigmaAE 471.8753196693, direction 7/12
- 2024: SigmaAE 728.9064044142, direction 8/12

## Causal CEEMDAN-XGBoost
- DEV SigmaAE: 1820.4745552856104
- MAE: 55.1658956147
- RMSE: 67.1097192094
- MAPE: 2.7019593006%
- WAPE: 2.6790288128%
- relative MAE vs RW: 1.0355372897
- direction: 17/33 = 51.52%
- worst AE: 147.8638051983 (2024-04)

Yearly:
- 2022: SigmaAE 515.1830933810, direction 4/9
- 2023: SigmaAE 563.5167863522, direction 6/12
- 2024: SigmaAE 741.7746755524, direction 7/12

## Delta versus frozen XGBoost CURRENT8
- SigmaAE worsened by +236.6210594261
- direction worsened by -3 correct months
- relative MAE vs RW crossed above 1.0, meaning the causal CEEMDAN challenger was worse than random walk on aggregate DEV price MAE.

## Interpretation
The source paper reports a large gain from CEEMDAN-XGBoost under its own daily/global-decomposition setup, but that gain did not transport to this project when the decomposition was made strictly causal and evaluated on monthly H=1 DEV.

The result is consistent with the known concern that globally decomposed time-series features can look substantially stronger than genuinely point-in-time decompositions. This run does not prove the source paper is invalid; it shows that the canonical causal adaptation is not competitive under this project's data/target/governance.

## Decision
CAUSAL CEEMDAN-XGBOOST is NOT PROMOTED.
It does not improve the Stage-5 XGBoost frontier and is materially worse than the current Boosting family leader Vanilla CatBoost (SigmaAE 1460.433935309605).

Per the pre-outcome plan, Stage 6C-D VMD -> residual CEEMDAN -> WOA-XGBoost should only be opened if Stage 6C-C showed a meaningful signal. Stage 6C-C did not. Therefore Stage 6C-D is NOT automatically justified by this result and requires a fresh authority/decision review before execution.

## Reproducibility
GitHub Actions run: 36382346934
Job: 108800529082
Result payload SHA256: b11f70c2490e7a1d13d797e0e01325e4ba29c1e44406f1d5491da109f29cd13a
Scientific gate: BOOSTING_STAGE6C_C_GATE=PASS
