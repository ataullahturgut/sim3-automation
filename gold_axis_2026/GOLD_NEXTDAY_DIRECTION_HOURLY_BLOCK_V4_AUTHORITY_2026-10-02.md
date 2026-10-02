# GOLD NEXT-DAY DIRECTION — HOURLY SMALL-BLOCK V4 AUTHORITY

**Date:** 2026-10-02  
**Status:** FROZEN PRE-RUN  
**Source:** `XAU_USD_TWELVE_1H_RESEARCH_V1`

## Goal

Test whether **contiguous 2-hour and 3-hour return blocks** contain next-day direction information that is stronger and more stable than single hourly lags.

The prior V3 result is frozen:
- base = V1 summary-feature Logistic;
- retained single lag = `hr_ret_lag2`.

V4 asks whether small contiguous blocks add value beyond that frozen V3 structure.

## Target / clock

- forecast issued after the 16:00 America/New_York XAU/USD hourly bar;
- target = sign of next available trading-day 16:00 anchor return;
- no future hourly observation enters features.

## Base features

V1 17 summary features:
- ret 1h / 3h / 6h / 12h / 24h
- realized volatility 6h / 12h / 24h
- up-hour fraction 6h / 12h / 24h
- range 12h / 24h
- slope 6h / 12h / 24h
- local-day session return.

Frozen V3 addition:
- `hr_ret_lag2`.

## Candidate block definitions

From the same 24 ordered hourly returns:

### 2-hour blocks
For start position s = 0..22:
- `blk2_s_s+1` = sum(`hr_ret_lag{s}`, `hr_ret_lag{s+1}`)

Total: **23 candidates**.

### 3-hour blocks
For start position s = 0..21:
- `blk3_s_s+2` = sum of three consecutive hourly return lags.

Total: **22 candidates**.

Grand total: **45 fixed candidate blocks**.

No post-run candidate invention.

## Stage A — standalone block audit

Each of the 45 blocks is added individually to the original V1 model and scored by strict monthly expanding OOS predictions in **2023**.

Record deltas versus V1:
- accuracy
- balanced accuracy
- Brier
- log loss
- UP recall
- DOWN recall.

## Stage B — incremental audit beyond V3

Each block is added individually to the frozen V3 base:
- V1 + `hr_ret_lag2` + candidate block.

This determines whether a block adds information beyond the already-retained lag2.

## Stage C — greedy block retention on 2023 only

Starting from V3:
- test every remaining block;
- choose the candidate with largest balanced-accuracy increase;
- accept only if:
  - balanced accuracy improves by >= **0.50 percentage point**;
  - Brier worsens by no more than **0.002**;
  - accuracy falls by no more than **0.50 percentage point**;
- repeat until no candidate qualifies or **4 blocks** have been accepted.

All choices use **2023 only**.

## Stage D — frozen 2024 confirmation

Freeze the selected block subset and report 2024 performance versus:
- V1
- V3 (V1 + lag2)
- V4 selected structure.

No 2024 outcome may change the selected block set.

## Interpretation

2024 is confirmation inside an already-opened wider research history, not a pristine untouched lockbox.

No 2025/2026 data are used.
