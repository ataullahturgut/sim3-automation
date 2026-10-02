# GOLD NEXT-DAY DIRECTION — HOURLY XAU AUTHORITY

**Date:** 2026-10-02  
**Status:** FROZEN PRE-RUN  
**Source:** `XAU_USD_TWELVE_1H_RESEARCH_V1`  
**Purpose:** predict whether the next available trading day's 16:00 America/New_York XAU/USD anchor is UP or DOWN versus today's 16:00 anchor.

## Timeline

For each issue day:
- use hourly XAU/USD observations only through the exact **16:00 America/New_York** hourly bar;
- issue the forecast immediately after that bar;
- target = sign of log(next available day's 16:00 anchor / current day's 16:00 anchor).

No next-day hourly observation is permitted in the features.

## Data

Existing raw source:
- Twelve Data XAU/USD
- interval: 1h
- registered series: `XAU_USD_TWELVE_1H_RESEARCH_V1`
- available research history: 2022-01-02 .. 2024-12-31
- approximately 17,644 hourly rows.

This is a historical research backfill and is not claimed to be the canonical live NY17 series.

## Fixed hourly features

All features are computed only from hourly closes available by the issue bar:

- log return over 1h, 3h, 6h, 12h, 24h
- realized hourly-return volatility over 6h, 12h, 24h
- up-hour fraction over 6h, 12h, 24h
- log close-range over 12h and 24h
- linear log-price slope over 6h, 12h, 24h
- local-day first-bar-to-16:00 log return.

No feature search is allowed in this first run.

## Models

Two fixed baselines:

1. Logistic Regression L2
   - StandardScaler
   - C=1
   - max_iter=2000

2. HistGradientBoostingClassifier
   - max_depth=3
   - learning_rate=0.05
   - max_iter=150
   - l2_regularization=1.0
   - min_samples_leaf=20

No hyperparameter tuning.

## Evaluation

- 2022: initial training history.
- 2023-2024: strict expanding one-step daily out-of-sample evaluation.
- model refit at the start of each calendar month using only matured earlier targets.
- report:
  - accuracy
  - balanced accuracy
  - Brier
  - log loss
  - UP recall
  - DOWN recall
  - 2023 and 2024 separately
  - confusion counts
  - monthly ledger.

Reference baselines:
- always-majority probability from training history
- naive momentum direction = today's first-bar-to-16:00 return sign.

This run is a feasibility screen for hourly XAU next-day direction. It does not authorize trading or live deployment.
