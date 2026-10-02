# GOLD NEXT-DAY DIRECTION — HOURLY LAG V3 SELECTION AUTHORITY

**Date:** 2026-10-02  
**Status:** FROZEN PRE-RUN  
**Source:** `XAU_USD_TWELVE_1H_RESEARCH_V1`

## Goal

Test the 24 ordered hourly-return lags **one by one**, remove lags that do not add predictive value to the V1 summary-feature Logistic model, and retain only lags that improve a frozen 2023 selection objective. Then freeze the subset and report it on 2024.

This stage is explicitly a feature-selection experiment. 2023 becomes the selection/development year for this V3. 2024 is used only after the lag subset has been frozen. Note that 2024 is not a pristine never-seen holdout for the wider research program because prior V1/V2 diagnostics already reported it; therefore V3-2024 is confirmation evidence, not a new untouched lockbox.

## Target / clock

- forecast issued after the 16:00 America/New_York XAU/USD hourly bar;
- target = sign of next available trading-day 16:00 anchor return;
- only information available by the issue bar may enter features.

## Base model

`V1_LOGIT_L2`:
- original 17 V1 summary features;
- StandardScaler;
- LogisticRegression(C=1.0, L2, lbfgs).

## Candidate lags

Exactly 24 ordered hourly returns:
- `hr_ret_lag0` = most recently completed hourly return;
- ...
- `hr_ret_lag23` = hourly return 23 bars before the issue bar.

No 24-47h blocks, shock variables, MLP or other V2 additions participate in this selection run.

## Stage A — one-at-a-time lag audit

For each candidate lag independently:

- model = V1 17 features + that single lag;
- strict monthly expanding OOS predictions within 2023;
- training uses only targets matured before each test month;
- record delta versus exact V1 baseline on:
  - accuracy
  - balanced accuracy
  - Brier
  - log loss
  - UP recall
  - DOWN recall.

This table is retained even for rejected lags.

## Stage B — greedy forward retention on 2023 only

Start from V1 with no added hourly lag.

At each step:
1. test every remaining lag added to the currently retained set;
2. choose the candidate with the largest increase in **balanced accuracy**;
3. accept it only if:
   - balanced accuracy improves by at least **0.50 percentage point**, and
   - Brier does not worsen by more than **0.002 absolute**, and
   - accuracy does not fall by more than **0.50 percentage point**;
4. repeat until no lag qualifies or a maximum of 6 lags is reached.

All choices are made from 2023 only.

## Stage C — frozen 2024 confirmation

After Stage B:
- freeze the selected lag subset;
- run the same monthly expanding forecasting procedure over 2024;
- no lag may be added/removed from 2024 outcomes;
- compare frozen V3 against V1 on 2024.

## Required outputs

- one-at-a-time 24-lag audit table;
- forward-selection step log;
- selected lag list;
- 2023 selection metrics;
- 2024 frozen confirmation metrics;
- monthly prediction ledger;
- final standardized coefficients.

No 2025/2026 data are involved.
