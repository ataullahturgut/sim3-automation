# GOLD CONTROL — RAW vs SQRT HAR-DR MULTI-ORIGIN ROBUSTNESS V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_RESEARCH`  
**Parent benchmark:** `DOWNSIDE_HAR_DR_XAU_V1_RESEARCH`  
**Hypothesis-generating observation:** `SQRT_OLS_HAR_DR` showed better 2025 level calibration and high-risk classification than raw HAR-DR inside the separately frozen SQRT-QHAR experiment.  
**Manifest update:** DEFERRED UNTIL USER REVIEWS RESULTS  
**Runtime authority:** NONE  
**Production writes:** NONE

## 1. Scientific question

Does representing downside risk on the **semideviation scale**,

`SD_t = sqrt(DR_t)`,

produce a HAR model whose one-day forecasts are more stable under time variation than the conventional HAR-DR model fitted directly on raw downside realized semivariance?

The intervention is the target/predictor representation only. Both models remain plain OLS HAR models with daily/weekly/monthly heterogeneous components.

## 2. Governance and evidentiary status

This hypothesis was generated after inspecting 2025 HAR-DR behavior. Therefore:

- **2022, 2023, 2024** are the primary retrospective falsification panel;
- **2025** is a discovery/stress year and is NOT treated as pristine confirmation;
- **2026 YTD** is an additional retrospective transport stress period and is also NOT pristine blind evidence;
- no conclusion will describe 2025 or 2026 as an untouched holdout.

No random split. No window search. No hyperparameter search. No threshold tuning.

## 3. Governed data contract

Source:
`public.xau_intraday_research_cache_5m`.

Daily construction:
- timezone `America/New_York`;
- Monday-Friday only;
- retain date only with at least 240 five-minute closes;
- intraday log return uses consecutive closes within the same retained date only;
- no cross-date return enters realized semivariance.

Daily downside realized semivariance:

`DR_t = sum_i r_(t,i)^2 I(r_(t,i)<=0)`.

Daily downside semideviation:

`SD_t = sqrt(DR_t)`.

Daily close-to-close return is retained only for auxiliary DOWN/extreme-return diagnostics.

## 4. Models

### A. RAW_HAR_DR

Predictors:
- `DR_t`;
- mean `DR_{t-4:t}`;
- mean `DR_{t-21:t}`.

Target:
`DR_{t+1}`.

OLS with intercept.

### B. SQRT_HAR_DR

Predictors:
- `SD_t`;
- mean `SD_{t-4:t}`;
- mean `SD_{t-21:t}`.

Target:
`SD_{t+1}`.

OLS with intercept.

The final downside-risk forecast is:

`DRhat_{t+1} = SDhat_{t+1}^2`.

No Jensen/bias correction, clipping, log transform, QLIKE optimization, adaptive scale state, macro variable, realized jump, class weight or nonlinear term is allowed in V1.

Any nonpositive `SDhat` in an evaluation period is a model-domain failure and is reported; it is not repaired by absolute value, squaring a negative prediction, or clipping.

## 5. Expanding-origin evaluation

For each target year Y:

- fit each model using every eligible supervised target dated no later than 31 December Y-1;
- evaluate only targets dated within Y;
- refit exactly once at the annual origin;
- no target-year observation enters coefficient estimation.

Frozen evaluation years:

- 2022;
- 2023;
- 2024;
- 2025;
- 2026 YTD through the last eligible available target.

Minimum formation support per origin: 250 supervised rows.

## 6. Year-specific formation thresholds

For each annual origin, using formation targets only:

- historical-mean DR benchmark = mean formation target DR;
- high-risk threshold = nearest-rank 80th percentile of formation target DR;
- extreme-negative-return threshold = nearest-rank 5th percentile of formation next-day close return.

The same year-specific thresholds are shared by RAW_HAR_DR and SQRT_HAR_DR.

## 7. Mandatory metrics by year and pooled pre-2025 panel

For both models:

- n;
- MSE;
- MAE;
- DR-scale QLIKE;
- OOS R2 versus the year-origin frozen historical-mean DR forecast;
- persistence MSE and QLIKE;
- correlation forecast vs realized DR;
- forecast mean / realized mean;
- Mincer-Zarnowitz-style calibration intercept and slope;
- absolute calibration-slope error `|slope-1|`;
- high-risk ROC AUC;
- high-risk alert coverage, precision, recall, F1;
- DOWN-day rate conditional on high-risk alert versus unconditional;
- extreme-negative-return rate conditional on alert versus unconditional;
- forecast minimum / median / maximum.

For SQRT_HAR_DR additionally:
- minimum SD forecast;
- count of nonpositive SD forecasts.

## 8. Paired-loss and classification diagnostics

For the pooled 2022–2024 annual-origin predictions:

- paired MSE loss difference = RAW squared error minus SQRT squared error;
- paired QLIKE loss difference = RAW QLIKE loss minus SQRT QLIKE loss;
- Newey-West/HAC mean-loss t statistics with lag 5 and lag 10;
- pooled high-risk AUC uses the normalized score `forecast_DR / year-specific formation high-risk threshold`, so annual threshold-level changes do not mechanically dominate the pooled ranking;
- high-risk binary correctness discordance:
  - SQRT-only correct;
  - RAW-only correct;
  - both correct;
  - neither correct;
- exact two-sided binomial/McNemar-style p-value on discordant correctness counts.

Positive paired-loss mean favors SQRT.

## 9. Frozen pre-2025 robustness gate

The semideviation-representation hypothesis is **supported** only if all hold across 2022–2024:

1. SQRT_HAR_DR MSE < RAW_HAR_DR MSE in at least 2 of 3 years;
2. pooled 2022–2024 SQRT MSE < pooled RAW MSE;
3. SQRT absolute calibration-slope error is smaller than RAW in at least 2 of 3 years;
4. SQRT high-risk AUC is not lower than RAW by more than 0.02 in any of the three years;
5. pooled high-risk AUC for SQRT is at least RAW pooled AUC minus 0.01;
6. no nonpositive SQRT SD forecast occurs in 2022–2024.

No QLIKE superiority requirement is imposed because the hypothesis concerns representation/calibration robustness rather than QLIKE optimization. QLIKE remains a mandatory counter-metric and a deterioration must be disclosed.

## 10. Stress-period interpretation

Only if the 2022–2024 gate passes, 2025 and 2026 YTD are assessed as retrospective stress evidence.

A stress year is marked `REPRESENTATION_STRESS_SUPPORT` when:
- SQRT MSE <= RAW MSE;
- SQRT calibration-slope error < RAW calibration-slope error;
- SQRT high-risk AUC >= RAW AUC - 0.02;
- no nonpositive SQRT SD forecast.

These stress labels are descriptive and not equivalent to fresh external validation.

## 11. Interpretation lock

Possible primary conclusions:
- `PRE2025_SEMIDEVIATION_REPRESENTATION_SUPPORTED`
- `PRE2025_SEMIDEVIATION_REPRESENTATION_NOT_SUPPORTED`.

Secondary stress labels:
- `2025_REPRESENTATION_STRESS_SUPPORT / NOT_SUPPORTED`;
- `2026YTD_REPRESENTATION_STRESS_SUPPORT / NOT_SUPPORTED`.

Even if this V1 passes, publication-level confirmation still requires a genuinely independent intraday metal / Gold-futures / GLD dataset or later unseen period.

No manifest change occurs in the workflow.
