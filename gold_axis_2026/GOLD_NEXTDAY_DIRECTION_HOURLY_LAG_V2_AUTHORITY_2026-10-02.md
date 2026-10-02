# GOLD NEXT-DAY DIRECTION — HOURLY LAG V2 AUTHORITY

**Date:** 2026-10-02  
**Status:** FROZEN PRE-RUN  
**Source:** `XAU_USD_TWELVE_1H_RESEARCH_V1`  
**Target:** next available trading-day 16:00 America/New_York XAU/USD direction versus current-day 16:00 anchor.

## Purpose

Test whether preserving the **ordering of hourly XAU returns** improves next-day UP/DOWN prediction relative to the V1 summary-feature Logistic model.

## Data and clock

- raw source: Twelve Data XAU/USD 1h research backfill
- available registered history: 2022-01-02 .. 2024-12-31
- forecast issue: immediately after current-day 16:00 America/New_York hourly bar
- target: sign of next available trading-day 16:00 anchor return
- no next-day hourly observation may enter features.

## Fixed V2 lag representation

### A. Ordered recent-hour returns
- current completed hour return and previous 23 hourly returns: 24 ordered values.

### B. Prior-day coarse return blocks
- hours 24-29 before issue
- hours 30-35
- hours 36-41
- hours 42-47

Each block is the sum of its six hourly log returns.

### C. Path-shape / shock state
- rolling realized volatility: 6h, 12h, 24h
- prior-anchor realized volatility: 6h, 12h, 24h
- up-hour fraction: 6h, 12h, 24h
- maximum positive hourly return in last 24h
- maximum negative hourly return in last 24h
- hours since the largest positive shock
- hours since the largest negative shock
- current same-sign hourly streak length capped at 24
- current local-day first-bar-to-16:00 return
- previous trading-day session return
- 12h and 24h price ranges.

No feature search is permitted after outcomes are seen.

## Models

All fixed pre-run.

1. **V1_LOGIT_L2**
   - original V1 17 summary features
   - StandardScaler + LogisticRegression(C=1.0, L2)

2. **LAG_LOGIT_L2**
   - full V2 lag representation
   - StandardScaler + LogisticRegression(C=1.0, L2)

3. **LAG_ELASTIC_LOGIT**
   - full V2 lag representation
   - StandardScaler + LogisticRegression
   - penalty=elasticnet
   - solver=saga
   - C=0.20
   - l1_ratio=0.50
   - max_iter=5000

4. **LAG_MLP_16**
   - full V2 lag representation
   - StandardScaler
   - one hidden layer, 16 tanh units
   - solver=lbfgs
   - alpha=0.01
   - max_iter=1500
   - random_state=20261001
   - no random validation / no early stopping.

Reference:
- expanding majority probability.

## Evaluation

- 2022 = initial training history
- 2023-2024 = strict expanding out-of-sample scoring
- refit at start of each calendar month
- only labels with target timestamp before that month start are usable
- no hyperparameter tuning on 2023/2024
- report 2023, 2024, and combined:
  - accuracy
  - balanced accuracy
  - Brier
  - log loss
  - UP recall
  - DOWN recall
  - confusion counts
- preserve monthly ledger, fit log, Elastic-Net nonzero coefficients, and V2 Logistic coefficients.

This is a research feasibility test only.
