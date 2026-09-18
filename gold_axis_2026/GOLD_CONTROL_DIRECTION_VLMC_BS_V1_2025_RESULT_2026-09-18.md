# GOLD CONTROL — DIRECTION_VLMC_BS_V1_RESEARCH LOCKED 2025 TEST

**Date:** 2026-09-18  
**Identity:** `DIRECTION_VLMC_BS_V1_RESEARCH`  
**Status:** `LOCKED_2025_HISTORICAL_TEST_COMPLETE / EVENT_OVERLAY_NOT_YET_APPLIED`  
**Pre-2025 frozen checkpoint:** `73e4b7f5d784f319930f3e64c11e97b79d5a747b`  
**Frozen weekly forecast table:** `gold_axis_2026/GOLD_CONTROL_DIRECTION_VLMC_BS_V1_2025_WEEKLY_FORECASTS_2026-09-18.csv`  
**Forecast-table commit:** `71693991617aa54d0739b4433958021eaf5823b4`

## 1. Frozen model used in 2025

No parameter, pruning rule, source rule or probability threshold was changed after the pre-2025 checkpoint.

For weekly close `C_w`:

`r_w = ln(C_w/C_(w-1))`

`x_w = 1[r_w > 0]`.

At each forecast origin, exactly the prior 52 weekly return signs are used.

The frozen bootstrap VLMC procedure is:
- maximal context tree with terminal contexts observed at least twice;
- initial pruning cutoff `K0=0.30`;
- candidate `K=0.40,0.42,...,2.50`;
- `B=1000` bootstrap replications;
- burn-in `n_start=10000`;
- exact reproducibility stream: MT19937, seed 1521, `u=(uint32+0.5)/2^32`, reset independently at every origin;
- bootstrap objective: minimum one-step zero-one classification loss;
- exact K ties: choose the smallest K on the ascending grid;
- final probability = empirical UP transition probability from the longest active context;
- direction = UP iff `P(UP)>=0.5`, else DOWN.

No probability smoothing, NO_SIGNAL band, FAST/GVZ/BOCPD/Macro/Emergency input, provider substitution or post-validation rescue is present.

## 2. 2025 source and chronology

Source:
`XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`.

Weekly construction:
- Monday-Friday New York-local observations only;
- weekly close = last actually observed governed weekday of the Monday-start calendar week;
- no interpolation;
- no forward-fill;
- no alternate-provider splice.

2025 contains 52 represented target weeks.

The complete 52-row weekly forecast table was produced and frozen before the 19-event volatility overlay was opened.

## 3. Locked 2025 next-week direction result

Metrics recomputed directly from the frozen 52-row CSV:

- n = 52
- accuracy = 0.6730769231
- balanced accuracy = 0.5902777778
- Brier score = 0.3118972835
- log loss = 6.1264976436
- actual UP / DOWN = 36 / 16
- forecast UP / DOWN = 39 / 13
- UP sensitivity = 0.8055555556
- DOWN sensitivity = 0.3750000000
- TP / TN / FP / FN = 29 / 6 / 10 / 7
- always-UP accuracy = 0.6923076923
- previous-week-sign accuracy = 0.5576923077
- mean P(UP) = 0.5968402106
- minimum / maximum P(UP) = 0 / 1
- exact P(UP)=0 origins = 13
- exact P(UP)=1 origins = 18

Bootstrap/tree diagnostics:
- mean K_star = 0.9580769231
- K_star range = 0.40 .. 2.40
- median K_star = 0.82
- mean minimum bootstrap loss = 0.2503076923
- mean final order = 5.0576923077
- final-order range = 0 .. 8
- mean final context count = 10.9615384615
- mean active-context transition support = 12.0192307692

## 4. Comparison with simple baselines and RSM-52

The 67.31% raw VLMC-BS accuracy is below the 2025 always-UP baseline of 69.23%.

However, unlike frozen RSM-52, VLMC-BS does not collapse to one class:
- RSM-52 forecast UP in 52/52 weeks, balanced accuracy 50.00%, DOWN sensitivity 0%;
- VLMC-BS forecast UP in 39 weeks and DOWN in 13 weeks, balanced accuracy 59.03%, DOWN sensitivity 37.50%.

This is evidence of greater two-sided directional discrimination in the 2025 historical replay, but it is not sufficient for promotion because the pre-2025 validation was weak:
- 2024 VLMC-BS accuracy = 45.28%;
- 2024 balanced accuracy = 45.01%;
- both were below the simple 2024 baselines.

## 5. Probability-quality limitation

The categorical direction result is more two-sided than RSM, but probability quality remains poor.

Of 52 locked 2025 origins:
- 13 have P(UP)=0;
- 18 have P(UP)=1.

Thus 31/52 forecasts are at a probability boundary. This produces weak Brier/log-loss behavior and reflects the low-support empirical-transition structure of a 52-symbol VLMC.

No smoothing is added after seeing this result. Any smoothed/probabilistic successor requires a separately named preregistration and cannot reuse 2025 as untouched validation.

## 6. Evidentiary interpretation

The 2025 result is a locked historical test under a specification frozen from pre-2025 work. It shows a potentially useful qualitative property relative to RSM — the model produces both UP and DOWN forecasts and captures 6 of 16 DOWN weeks — but it does not overturn the negative 2024 validation.

Accordingly, 2025 is retained as diagnostic evidence of possible context-dependent two-sided behavior, not as a basis for tuning or promotion.

The frozen 19-event volatility inventory has not been used in this result. Event overlay is a separate subsequent diagnostic.
