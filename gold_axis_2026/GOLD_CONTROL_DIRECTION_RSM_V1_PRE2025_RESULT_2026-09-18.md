# GOLD CONTROL — DIRECTION_RSM_V1_RESEARCH PRE-2025 CHECKPOINT

**Date:** 2026-09-18  
**Identity:** `DIRECTION_RSM_V1_RESEARCH`  
**Status:** `PRE2025_CHECKPOINT_COMPLETE / FROZEN_BEFORE_2025_TEST`  
**Evidence:** `PRE2025_RETROSPECTIVE_TIME_ORDERED_RESEARCH`  
**Implementation:** `gold_axis_2026/tools/direction_rsm_v1_research.py`  
**Preregistration:** `gold_axis_2026/GOLD_CONTROL_DIRECTION_RSM_V1_PREREG_2026-09-18.md`

## 1. Model construction

This implementation reproduces the 52-week Return Signal Momentum direction method used as a source-replication benchmark in Liu, Papailias & Quinn (2021), *International Review of Financial Analysis*, 74, 101677, DOI `10.1016/j.irfa.2021.101677`.

For weekly close `C_w`:

`r_w = ln(C_w / C_(w-1))`

and the binary direction state is

`x_w = 1[r_w > 0]`.

Zero or negative return maps to `0/DOWN`.

For each forecast origin after 52 observed weekly signs:

`p_up(w) = (1/52) * sum(x_(w-51), ..., x_w)`.

The next represented week's direction is forecast as:

- `UP` if `p_up >= 0.5`;
- `DOWN` otherwise.

RSM-52 has no fitted regression coefficients and no hidden optimizer. Its only adaptive quantity is the rolling fraction of positive weekly return signs. Return magnitudes are discarded after the sign transformation.

The 52-week window and `0.5` decision boundary are source-replication settings frozen before 2025 price/return inspection. They were not selected from Gold 2025 outcomes.

## 2. Data construction

Selected series:

`XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`

Source semantics:
- provider: Twelve Data;
- symbol: XAU/USD;
- research-only New York-local 16:00 hourly-derived daily close;
- Monday-Friday New York-local observations only;
- no interpolation;
- no forward-fill;
- no alternate-provider substitution.

Weekly close rule:
1. assign every eligible daily observation to its Monday-start calendar week;
2. choose the last actually observed governed weekday in that week;
3. normally this is Friday;
4. if Friday is absent, retain the last actually observed weekday rather than fabricating a Friday close.

The canonical exact-16:59 `XAU_EOD_TWELVE_NY17` was inspected but not selected for this replication because its pre-2025 historical coverage was too sparse for a faithful rolling-52 weekly test: 138 observations in 2022, 89 in 2023 and 124 in 2024. No second provider was spliced in to repair those gaps.

Selected-series pre-2025 audit:
- interval: 2022-03-01 through 2024-12-31;
- governed weekday rows: 668;
- distinct New York-local dates: 668;
- represented calendar weeks: 149;
- missing calendar weeks inside the represented range: 0;
- non-approved selected rows: 0;
- weeks with fewer than three observed weekdays: 1;
- first weekly close: 2022-03-04;
- last pre-2025 weekly close: 2024-12-31.

The first valid next-week RSM forecast appears only after the 52-sign warm-up, with first 2023 target week beginning 2023-03-06.

## 3. Chronology and validation design

The chronology was fixed as:
- 2022-03 onward: warm-up/history;
- 2023: implementation/development audit after warm-up;
- 2024: fixed-rule pre-2025 validation;
- 2025: locked historical test, inaccessible for model rescue/tuning until the preregistration, code and pre-2025 checkpoint were frozen.

There is no random split.

No FAST, GVZ_RISK, BOCPD, Macro Event, Emergency or other Gold Control motor output enters this V1 model.

## 4. Pre-2025 results

### 2023 target weeks
- n = 43
- accuracy = 0.5581395349
- balanced accuracy = 0.5822368421
- Brier score = 0.2511868722
- log loss = 0.6955470390
- actual UP / DOWN = 24 / 19
- forecast UP / DOWN = 13 / 30
- exact `p_up=0.5` origins = 7
- always-UP accuracy = 0.5581395349
- previous-week-sign accuracy = 0.5348837209

The raw accuracy equals the always-UP baseline, although balanced accuracy is higher because the RSM classifier did issue both UP and DOWN forecasts in 2023.

### 2024 target weeks
- n = 53
- accuracy = 0.5094339623
- balanced accuracy = 0.5007122507
- Brier score = 0.2533563135
- log loss = 0.6999508385
- actual UP / DOWN = 27 / 26
- forecast UP / DOWN = 51 / 2
- exact `p_up=0.5` origins = 5
- always-UP accuracy = 0.5094339623
- previous-week-sign accuracy = 0.5094339623

The 2024 validation is effectively non-discriminative: raw accuracy equals the always-UP baseline and balanced accuracy is approximately 0.50.

### Combined pre-2025
- n = 96
- accuracy = 0.5312500000
- balanced accuracy = 0.5209150327
- Brier score = 0.2523845846
- log loss = 0.6979783033
- actual UP / DOWN = 51 / 45
- forecast UP / DOWN = 64 / 32
- exact `p_up=0.5` origins = 12
- always-UP accuracy = 0.5312500000
- previous-week-sign accuracy = 0.5208333333

## 5. Independent verification

The complete pre-2025 calculation was independently reconstructed in two ways:

1. raw Neon observation rows -> independent JavaScript weekly aggregation and RSM calculation;
2. independent PostgreSQL calculation using weekly selection and window functions.

The 2023 and 2024 counts and all reported metrics matched exactly.

This cross-check was completed before the 2025 price/return test.

## 6. Pre-2025 decision

The fixed RSM-52 specification did not establish a robust standalone Gold direction edge before 2025. In particular, 2024 validation is approximately chance-level on balanced accuracy and equals the always-UP baseline on raw accuracy.

No window, threshold, source, weekly-close rule or feature was changed in response. The exact frozen model was carried unchanged into the locked 2025 historical test to avoid post-validation rescue/tuning.
