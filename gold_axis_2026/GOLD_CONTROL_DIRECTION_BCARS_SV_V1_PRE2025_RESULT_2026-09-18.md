# GOLD CONTROL — DIRECTION_BCARS_SV_V1_RESEARCH PRE-2025 CHECKPOINT

**Date:** 2026-09-18  
**Identity:** `DIRECTION_BCARS_SV_V1_RESEARCH`  
**Status:** `PRE2025_CHECKPOINT_COMPLETE / FROZEN_BEFORE_2025_REPLAY`  
**Parent B-CARS V1:** `BLOCKED_PRE2025_BOUNDARY_SUPPORT`  
**Weekly input SHA-256:** `e7048cb9e478495e8832486cac4f763260dbcca6ab329ef7f4fc5e8216a41d9b`

## Frozen method

B-CARS(1,1) is fit by expanding-window MLE. Exact 0/1 up-ratios are handled with the preregistered Smithson-Verkuilen transformation
`y*=(y(n-1)+0.5)/n`.
The first 52 modeled weekly up-ratios are the initial estimation window. Direction is UP iff the forecast transformed mean exceeds 0.5.

No 2025 outcome is used in this checkpoint.

## 2023 development/audit

- n = 43
- accuracy = 0.4418604651
- balanced accuracy = 0.5000000000
- actual UP / DOWN = 24 / 19
- forecast UP / DOWN = 0 / 43
- UP sensitivity = 0.0000000000
- DOWN sensitivity = 1.0000000000
- TP / TN / FP / FN = 0 / 19 / 0 / 24
- always-UP accuracy = 0.5581395349
- previous-week-sign accuracy = 0.5348837209
- up-ratio MSE B-CARS = 0.0692390464
- up-ratio MSE historical mean = 0.0690128297
- source-style up-ratio R2_oos = -0.0032778941
- derived P(UP) Brier = 0.2574601328
- derived P(UP) log loss = 0.7081198025
- raw-scale forecast mean range = 0.4552182593 .. 0.4899385584

2023 collapses to 43/43 DOWN forecasts.

## 2024 fixed validation

- n = 53
- accuracy = 0.4716981132
- balanced accuracy = 0.4729344729
- actual UP / DOWN = 27 / 26
- forecast UP / DOWN = 23 / 30
- UP sensitivity = 0.4074074074
- DOWN sensitivity = 0.5384615385
- TP / TN / FP / FN = 11 / 14 / 12 / 16
- always-UP accuracy = 0.5094339623
- previous-week-sign accuracy = 0.5094339623
- up-ratio MSE B-CARS = 0.0868412660
- up-ratio MSE historical mean = 0.0841024767
- source-style up-ratio R2_oos = -0.0325649068
- derived P(UP) Brier = 0.2552594222
- derived P(UP) log loss = 0.7040374427
- raw-scale forecast mean range = 0.4690625945 .. 0.6051034528

## Combined pre-2025

- n = 96
- accuracy = 0.4583333333
- balanced accuracy = 0.4745098039
- actual UP / DOWN = 51 / 45
- forecast UP / DOWN = 23 / 73
- UP sensitivity = 0.2156862745
- DOWN sensitivity = 0.7333333333
- source-style up-ratio R2_oos = -0.0208597319
- derived P(UP) Brier = 0.2562451572
- derived P(UP) log loss = 0.7058659997

## Pre-2025 interpretation and lock

This boundary-safe B-CARS successor does **not** establish a standalone Gold weekly direction edge before 2025.

2024 validation is below 0.50 on both accuracy and balanced accuracy; continuous up-ratio forecasting also underperforms the expanding historical-mean benchmark.

No model order, boundary transform, threshold, optimizer rule, feature, frequency or window may be changed under this identity before the locked 2025 replay.
