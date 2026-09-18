# GOLD CONTROL — DIRECTION_RSM_V1_RESEARCH PRE-2025 CHECKPOINT

**Date:** 2026-09-18  
**Identity:** `DIRECTION_RSM_V1_RESEARCH`  
**Status:** FROZEN RSM-52 BEFORE 2025 PRICE/RETURN TEST  
**Evidence:** PRE2025_RETROSPECTIVE_TIME_ORDERED_RESEARCH

## Frozen specification

- Source: `XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`
- Monday-Friday New York-local observations only
- Weekly close: last actual governed weekday observation in each calendar week
- No fill / no source substitution
- Weekly log-return sign
- Rolling window: 52 weekly signs
- UP iff `p_up >= 0.5`, else DOWN
- Target: next represented calendar-week return sign
- No FAST/GVZ/BOCPD/Macro/Emergency inputs

## Data audit before 2025

Pre-2025 source interval used: 2022-03-01 through 2024-12-31.

- governed weekday rows: 668
- distinct local dates: 668
- represented calendar weeks: 149
- missing calendar weeks inside range: 0
- non-approved rows: 0
- only one represented week had fewer than 3 daily observations
- first weekly close: 2022-03-04
- last pre-2025 weekly close: 2024-12-31

The canonical exact-16:59 `XAU_EOD_TWELVE_NY17` series was not used because its 2022-2024 historical coverage is too sparse for a faithful rolling-52 weekly RSM test. No alternate provider was spliced into the selected research series.

## Pre-2025 results

### 2023 target weeks
- n = 43
- accuracy = 0.5581395349
- balanced accuracy = 0.5822368421
- Brier = 0.2511868722
- log loss = 0.6955470390
- actual UP/DOWN = 24 / 19
- forecast UP/DOWN = 13 / 30
- exact p=0.5 origins = 7
- always-UP accuracy = 0.5581395349
- previous-week-sign accuracy = 0.5348837209

### 2024 target weeks
- n = 53
- accuracy = 0.5094339623
- balanced accuracy = 0.5007122507
- Brier = 0.2533563135
- log loss = 0.6999508385
- actual UP/DOWN = 27 / 26
- forecast UP/DOWN = 51 / 2
- exact p=0.5 origins = 5
- always-UP accuracy = 0.5094339623
- previous-week-sign accuracy = 0.5094339623

### Combined pre-2025
- n = 96
- accuracy = 0.53125
- balanced accuracy = 0.5209150327
- Brier = 0.2523845846
- log loss = 0.6979783033
- actual UP/DOWN = 51 / 45
- forecast UP/DOWN = 64 / 32
- exact p=0.5 origins = 12
- always-UP accuracy = 0.53125
- previous-week-sign accuracy = 0.5208333333

## Verification

The pre-2025 forecasts/metrics were independently reconstructed in two implementations:
1. raw Neon observation rows -> independent JavaScript calculation;
2. independent PostgreSQL weekly/window-function calculation.

The 2023 and 2024 metrics match exactly.

## Interpretation before opening 2025 outcomes

RSM-52 does **not** demonstrate a strong standalone Gold edge in the pre-2025 checkpoint. In 2024 its raw accuracy equals the always-UP baseline and its balanced accuracy is approximately 0.50. No parameter is changed in response.

The exact frozen model is nevertheless carried forward to the locked 2025 historical test to avoid post-validation rescue/tuning.
