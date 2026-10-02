# GOLD NEXT-DAY DIRECTION — HOURLY XAU MANIFEST

**Date:** 2026-10-02  
**Status:** ACTIVE RESEARCH / V1 COMPLETE  
**Source:** `XAU_USD_TWELVE_1H_RESEARCH_V1`

## Objective

Predict whether the next available trading day's 16:00 America/New_York XAU/USD anchor will be UP or DOWN versus the current day's 16:00 anchor.

Forecast issue: immediately after current-day 16:00 NY hourly bar.

## Data

- raw XAU/USD hourly observations: **17,644**
- source coverage: 2022-01-02 .. 2024-12-31
- usable daily issue rows after feature/target maturity: **705**
- 2022 = initial training history
- 2023-2024 = strict expanding out-of-sample scoring

## Features

Past-only hourly transforms:
- 1h / 3h / 6h / 12h / 24h log returns
- 6h / 12h / 24h realized hourly-return volatility
- 6h / 12h / 24h up-hour fraction
- 12h / 24h log close range
- 6h / 12h / 24h log-price slope
- local-day first-bar-to-16:00 session return

## V1 models

### Logistic L2

2023-2024:
- N **468**
- accuracy **54.91%**
- balanced accuracy **54.41%**
- Brier **0.2598**
- log loss **0.7178**
- UP recall **64.23%**
- DOWN recall **44.59%**

2023:
- accuracy **56.25%**
- balanced accuracy **56.35%**

2024:
- accuracy **53.69%**
- balanced accuracy **52.76%**

### HistGradientBoosting

2023-2024:
- accuracy **48.29%**
- balanced accuracy **47.98%**
- Brier **0.2807**
- log loss **0.7625**

### Baselines

Expanding majority-probability:
- 2023-2024 accuracy **52.56%**
- balanced accuracy **50.00%**
- Brier **0.2497**
- log loss **0.6925**

Same-day session-momentum direction:
- accuracy **47.86%**
- balanced accuracy **47.81%**

## Initial interpretation

- The simple Logistic model extracts a directional signal from hourly XAU structure and exceeds majority-direction accuracy by about 2.35 percentage points.
- The probability stream is not yet well calibrated: Brier/log-loss remain worse than the majority-probability baseline.
- The nonlinear HGB V1 does not improve the result.
- The signal persists in both 2023 and 2024, but is weaker in 2024.
- Current asymmetry: UP recall materially exceeds DOWN recall.

Largest standardized Logistic coefficients:
1. ret_12h +0.740
2. upfrac_12h -0.529
3. upfrac_24h +0.440
4. session_ret -0.328
5. range_24h -0.244
6. upfrac_6h +0.226
7. rv_24h +0.221
8. slope_6h -0.203

## Provenance

- authority: `GOLD_NEXTDAY_DIRECTION_HOURLY_AUTHORITY_2026-10-02.md`
- result: `GOLD_NEXTDAY_DIRECTION_HOURLY_RESULT_2026-10-02.md`
- workflow run: **37002176253**

## Next research

Before adding external data, inspect:
- monthly/market-state variability,
- DOWN misses,
- coefficient stability,
- simple calibration,
- whether a compact subset can improve 2024 stability.

2025/2026 hourly scoring requires extending the same 1h raw source beyond 2024 under an explicit source/clock refresh; it is not available in the current registered 1h research backfill.
