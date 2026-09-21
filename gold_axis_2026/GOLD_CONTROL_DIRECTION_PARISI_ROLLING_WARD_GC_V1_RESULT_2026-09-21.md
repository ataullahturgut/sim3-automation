# GOLD CONTROL — DIRECTION_PARISI_ROLLING_WARD_GC_V1_RESEARCH RESULT

**Date:** 2026-09-21  
**Identity:** `DIRECTION_PARISI_ROLLING_WARD_GC_V1_RESEARCH`  
**Status:** `EVALUATED / LOCKED_2025_RETROSPECTIVE_COMPLETE / SOURCE_GROUNDED_ADAPTATION / NOT_EXACT_REPLICATION / NOT_RUNTIME`

## Method identity

This is the preregistered Gold-Control adaptation of Parisi, Parisi & Díaz (2008), not an exact reproduction of the proprietary 2008 Ward implementation. The source-proven eight-lag first-difference signal and rolling period-by-period retraining are preserved; unrecovered Ward implementation details are explicitly resolved by the frozen GC_V1 adaptation contract.

## Frozen pre-2025 selection

- selected rolling window = 75 weeks
- common 2024 selection n = 43
- 2024 accuracy = 0.4651162791
- 2024 balanced accuracy = 0.4543478261
- 2024 UP sensitivity = 0.6086956522
- 2024 DOWN sensitivity = 0.3000000000
- 2024 TP/TN/FP/FN = 14/6/14/9
- 2024 previous-sign accuracy = 0.5116279070

The rolling-window choice was frozen from common 2024 support before any 2025 model score was computed.

## Locked 2025 retrospective challenge

- n = 52
- accuracy = 0.5192307692
- balanced accuracy = 0.5036036036
- UP sensitivity = 0.5405405405
- DOWN sensitivity = 0.4666666667
- TP/TN/FP/FN = 20/7/8/17
- forecasts UP/DOWN = 28/24
- actual UP/DOWN = 37/15
- always-UP accuracy = 0.7115384615
- always-DOWN accuracy = 0.2884615385
- previous-sign accuracy = 0.5576923077
- ΔGold RMSE = 127.6635733176
- ΔGold MAE = 96.3592790651
- Pesaran-Timmermann statistic = 0.04723136913961158
- Pesaran-Timmermann two-sided p = 0.9623288264546985

## Governance

- 2025 was not used for feature, architecture, rolling-window, seed, scaling or sign-threshold selection.
- no post-result retuning was performed.
- no database, forecast-ledger or decision-store writes were performed.
- no automatic runtime promotion is authorized by this retrospective result.
