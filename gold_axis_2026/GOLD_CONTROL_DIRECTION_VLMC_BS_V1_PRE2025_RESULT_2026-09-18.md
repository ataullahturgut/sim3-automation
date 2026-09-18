# GOLD CONTROL — DIRECTION_VLMC_BS_V1_RESEARCH PRE-2025 CHECKPOINT

**Date:** 2026-09-18  
**Identity:** `DIRECTION_VLMC_BS_V1_RESEARCH`  
**Status:** `PRE2025_CHECKPOINT_COMPLETE / FROZEN_BEFORE_2025_TEST`  
**Evidence:** `PRE2025_RETROSPECTIVE_TIME_ORDERED_RESEARCH`  
**Preregistration:** `gold_axis_2026/GOLD_CONTROL_DIRECTION_VLMC_BS_V1_PREREG_2026-09-18.md`  
**Reference implementation:** `gold_axis_2026/tools/direction_vlmc_bs_v1_research.py`

## 1. Frozen model actually evaluated

The model uses the prior 52 weekly return signs only.

For weekly close `C_w`:

`r_w = ln(C_w/C_(w-1))`

`x_w = 1[r_w > 0]`.

At every real forecast origin:

1. build the maximal context tree from the 52 observed binary symbols, with terminal contexts required to occur at least twice;
2. fit a large initial VLMC using `K0=0.30`;
3. generate `B=1000` bootstrap sequences of length 53 after a 10,000-step burn-in;
4. for every `K=0.40,0.42,...,2.50`, fit/prune the context tree on bootstrap symbols 1..52 and classify symbol 53;
5. choose the smallest K among exact ties at the minimum bootstrap mean zero-one loss;
6. refit the real 52-symbol window using that `K_star`;
7. use the longest active context matched by the real past;
8. output its empirical `P(UP)`;
9. forecast UP iff `P(UP)>=0.5`, otherwise DOWN.

The pruning statistic is the classical context-algorithm quantity

`Delta(wu)=N(wu)*sum_a P_hat(a|wu)*log(P_hat(a|wu)/P_hat(a|w))`

and a terminal branch is pruned when `Delta(wu)<K`.

The bootstrap RNG is explicitly frozen to MT19937, seed 1521, with `u=(uint32+0.5)/2^32`, reset independently at each real origin.

## 2. Data and chronology

Source:
`XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`.

Weekly construction is identical to RSM V1:
- Monday-Friday New York-local observations;
- weekly close = last actually observed governed weekday in each Monday-start calendar week;
- no interpolation;
- no forward-fill;
- no provider substitution.

Chronology:
- 2022-03 onward: warm-up/history;
- 2023: implementation/development audit;
- 2024: fixed pre-2025 validation;
- 2025: not used for any parameter, K-grid, threshold, RNG, lookback or model-selection decision at this checkpoint.

## 3. 2023 development/audit result

- n = 43
- accuracy = 0.5116279070
- balanced accuracy = 0.5186403509
- Brier score = 0.4530911065
- log loss = 11.0847833303
- actual UP / DOWN = 24 / 19
- forecast UP / DOWN = 19 / 24
- UP sensitivity = 0.4583333333
- DOWN sensitivity = 0.5789473684
- TP / TN / FP / FN = 11 / 11 / 8 / 13
- always-UP accuracy = 0.5581395349
- previous-week-sign accuracy = 0.5348837209
- mean P(UP) = 0.4424947146
- P(UP)=0 origins = 19
- P(UP)=1 origins = 15
- mean K_star = 0.5651162791
- K_star range = 0.40 .. 1.00
- median K_star = 0.44
- mean bootstrap minimum loss = 0.2516046512
- final-order mean/range = 5.90698 / 5..8
- mean final context count = 19.3721
- mean active-context transition support = 3.4884

## 4. 2024 fixed validation result

- n = 53
- accuracy = 0.4528301887
- balanced accuracy = 0.4501424501
- Brier score = 0.4429450425
- log loss = 10.1376102740
- actual UP / DOWN = 27 / 26
- forecast UP / DOWN = 34 / 19
- UP sensitivity = 0.5925925926
- DOWN sensitivity = 0.3076923077
- TP / TN / FP / FN = 16 / 8 / 18 / 11
- always-UP accuracy = 0.5094339623
- previous-week-sign accuracy = 0.5094339623
- mean P(UP) = 0.5698355104
- P(UP)=0 origins = 16
- P(UP)=1 origins = 20
- mean K_star = 0.7400000000
- K_star range = 0.40 .. 1.40
- median K_star = 0.76
- mean bootstrap minimum loss = 0.2764528302
- final-order mean/range = 5.52830 / 0..9
- mean final context count = 13.5472
- mean active-context transition support = 5.8113

## 5. Combined pre-2025 result

- n = 96
- accuracy = 0.4791666667
- balanced accuracy = 0.4758169935
- Brier score = 0.4474896337
- log loss = 10.5618648721
- actual UP / DOWN = 51 / 45
- forecast UP / DOWN = 53 / 43
- UP sensitivity = 0.5294117647
- DOWN sensitivity = 0.4222222222
- TP / TN / FP / FN = 27 / 19 / 26 / 24
- always-UP accuracy = 0.5312500000
- previous-week-sign accuracy = 0.5208333333
- mean P(UP) = 0.5127974456
- P(UP)=0 origins = 35
- P(UP)=1 origins = 35
- mean K_star = 0.6616666667
- K_star range = 0.40 .. 1.40
- median K_star = 0.58
- mean final order = 5.6979166667
- final order range = 0..9
- mean final context count = 16.15625
- mean active-context transition support = 4.77083

## 6. Probability/calibration warning

The empirical transition-probability construction is highly discrete in a 52-week sample. Of 96 pre-2025 origins, 70 produce exactly `P(UP)=0` or `P(UP)=1`.

Descriptive calibration bins over 2023-2024:
- P(UP) in [0.0,0.2): 37 origins, mean forecast 0.0090, realized UP rate 0.5405
- [0.2,0.4): 3 origins, mean forecast 0.2879, realized UP rate 0.6667
- [0.4,0.6): 12 origins, mean forecast 0.5084, realized UP rate 0.4167
- [0.6,0.8): 6 origins, mean forecast 0.7323, realized UP rate 0.6667
- [0.8,1.0]: 38 origins, mean forecast 0.9878, realized UP rate 0.5263

This explains the very poor Brier/log-loss behavior and is retained as a model limitation rather than repaired after validation.

## 7. Reproducibility verification

The reference Python implementation and an independently optimized implementation were cross-checked at separated forecast origins.

At the final 2024 origin targeting week 2024-12-30, both implementations independently produced exactly:
- K_star = 0.54
- bootstrap loss = 0.207
- K ties = 3
- P(UP) = 1.0
- forecast = UP
- final order = 6
- context count = 16
- active context depth = 4
- transition support = 2 with 0 DOWN / 2 UP.

The first eligible origin was also checked under the same frozen MT19937 stream and matched across implementations.

## 8. Pre-2025 interpretation and lock

The VLMC-BS-52 challenger does **not** establish a standalone Gold direction edge before 2025.

2024 validation is below both the always-UP and previous-week-sign baselines on raw accuracy and below 0.50 on balanced accuracy. Probability calibration is also poor because low-support active contexts frequently yield empirical probabilities of exactly zero or one.

No rescue action is permitted before the locked 2025 test:
- K0 unchanged;
- K grid unchanged;
- B unchanged;
- burn-in unchanged;
- RNG unchanged;
- 52-week lookback unchanged;
- 0.5 direction threshold unchanged;
- no probability smoothing added;
- no minimum-support filter added;
- no NO_SIGNAL band added;
- no Gold Control context motors added.

The exact frozen V1 is carried unchanged into the 2025 historical test.
