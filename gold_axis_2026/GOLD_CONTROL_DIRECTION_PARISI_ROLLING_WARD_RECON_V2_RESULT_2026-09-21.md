# GOLD CONTROL — DIRECTION_PARISI_ROLLING_WARD_RECON_V2_RESEARCH RESULT

**Date:** 2026-09-21
**Identity:** DIRECTION_PARISI_ROLLING_WARD_RECON_V2_RESEARCH
**Evidence class:** SOURCE_CONSTRAINED_RECONSTRUCTION / NOT_EXACT_PROPRIETARY_REPLICATION

## Source boundary

This V2 corrects the removed first adaptation by using the published 4+4 first-difference signal, a genuine two-slab Ward-1 reconstruction, long Gold/DJIA history and period-by-period fixed-window rolling retraining. Exact Parisi-2008 proprietary neuron allocation, activation/scaling selection, rolling-size grid and training internals remain unproven; no exact-replication claim is made.

## Pre-2025 frozen selection

- selected rolling window = 100 weeks, selected on 2023 only
- 2023 selected PPS/accuracy = 0.5769230769
- 2023 selected balanced accuracy = 0.5703703704

## Unchanged 2024 validation

- n = 52
- accuracy/PPS = 0.5576923077
- balanced accuracy = 0.5179910045
- UP sensitivity = 0.8620689655
- DOWN sensitivity = 0.1739130435
- TP/TN/FP/FN = 25/4/19/4
- always-UP = 0.5576923077
- previous-sign = 0.4230769231
- PT statistic = 0.3571730355831603
- PT p = 0.7209622708130391
- ARIMA(4,1,2) n = 52
- ARIMA(4,1,2) accuracy = 0.5

No retuning was performed after this 2024 checkpoint.

## Locked 2025 retrospective challenge

- n = 52
- actual UP/DOWN = 35/17
- forecast UP/DOWN = 46/6
- accuracy/PPS = 0.6346153846
- balanced accuracy = 0.5016806723
- UP sensitivity = 0.8857142857
- DOWN sensitivity = 0.1176470588
- TP/TN/FP/FN = 31/2/15/4
- always-UP = 0.6730769231
- always-DOWN = 0.3269230769
- previous-sign = 0.6153846154
- DeltaGold RMSE = 100.8277393279
- DeltaGold MAE = 72.6732479276
- PT statistic = 0.0355892342423808
- PT p = 0.9716098927150164
- block-bootstrap mean accuracy = 0.6132692308
- block-bootstrap sd accuracy = 0.0813661628
- bootstrap 5-95% = 0.4807692308 .. 0.7500000000
- ARIMA(4,1,2) n = 52
- ARIMA(4,1,2) accuracy = 0.5384615384615384

## Governance

- rolling-window selection used 2023 only;
- 2024 was replayed unchanged and frozen before 2025 scoring;
- 2025 did not select/tune any parameter;
- database writes NONE;
- forecast-ledger writes NONE;
- decision-store writes NONE;
- no runtime promotion and no PR merge are authorized by this result.
