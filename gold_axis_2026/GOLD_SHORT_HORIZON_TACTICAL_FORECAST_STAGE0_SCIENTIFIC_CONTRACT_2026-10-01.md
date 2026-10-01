# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 0 Scientific Contract

**Date:** 2026-10-01  
**Status:** FROZEN / BINDING  
**Canonical manifest:** `gold_axis_2026/GOLD_SHORT_HORIZON_TACTICAL_FORECAST_PROJECT_MANIFEST.md`

## 1. Mission

Build a short-horizon Gold forecasting system that answers:

> If capital is available now, what is the expected direction, return and downside/upside distribution over the next 1, 3 and 5 Borsa İstanbul Gold observations?

This project is independent from the monthly Gold forecast and from the K100 intramonth-opportunity project.

## 2. Targets

For governed Borsa İstanbul Gold MTL/USD/OZ price P[t]:

- H1 return = log(P[t+1] / P[t])
- H3 return = log(P[t+3] / P[t])
- H5 return = log(P[t+5] / P[t])

Direction target:
- UP_h = 1 iff return_h > 0.

Quantile targets:
- Q10_h
- Q50_h
- Q90_h.

No target-price level model is primary.

## 3. Forecast origin

Signal origin:
- after Gold price P[t] is known;
- before P[t+1] is published;
- operational convention: 00:30 Europe/Istanbul on the next eligible Borsa date.

All features must be available by that origin.

## 4. Chronology

- background/training history: 2011-2021
- DEV selection authority: 2022-2024
- 2025: frozen transport only
- 2026: opened / no selection.

No random split.

## 5. Horizon fairness

H1, H3 and H5 are compared under the same:
- feature families;
- chronology;
- model families;
- scoring rules.

No horizon is declared primary before DEV results.

## 6. First feature blocks

### GOLD_ONLY
Gold:
- r1/r3/r5/r10/r21
- sigma20.

### CORE3
GOLD_ONLY plus:
- Silver r1/r5/r21
- Platinum r1/r5/r21
- causal age/staleness.

### CORE3_SAFE_EXTERNAL
CORE3 plus:
- nominal 10Y
- real 10Y
- breakeven proxy
- Broad USD
- EUR/GBP/JPY/CHF/CNY
- VIX
- Nasdaq-100.

Palladium is not mandatory in the first batch because strict complete history reduces pre-DEV observations from 2722 to 1965. It remains a later CORE4 challenger.

WTI/Brent and daily GPR are excluded from the first batch pending their short-horizon PIT contracts.

## 7. Label-maturity rule

At any prediction origin, a training row for horizon h may enter only if its full h-observation forward return is already known.

This rule is mandatory for H1/H3/H5.

## 8. Evaluation protocol

First screen:
- chronological prequential evaluation;
- refit every 5 Gold origins;
- training expands through matured prior labels only;
- no DEV target leakage.

## 9. Forecast metrics

### Direction probability
Primary:
- Brier score
- log loss.

Supporting:
- ROC-AUC
- PR-AUC
- direction accuracy
- balanced accuracy
- UP precision / recall
- prediction dispersion.

### Return point forecast
Primary:
- MAE
- RMSE.

Supporting:
- sign accuracy
- Spearman correlation
- forecast dispersion.

### Quantiles
Primary:
- pinball loss Q10/Q50/Q90.

Supporting:
- empirical coverage
- interval width
- interval crossing check.

## 10. Baselines

Direction:
- expanding historical UP prevalence
- rolling-252 UP prevalence.

Return:
- zero-return
- expanding historical mean
- rolling-252 mean.

Quantiles:
- expanding historical empirical Q10/Q50/Q90
- rolling-252 empirical quantiles.

## 11. First fixed model batch

No hyperparameter tuning in Stage 1.

### Direction
- Logistic L2
- LightGBM classifier
- XGBoost classifier.

### Return
- Elastic Net
- LightGBM regressor
- XGBoost regressor.

### Quantile return
- LightGBM quantile regression at 0.10 / 0.50 / 0.90.

If LightGBM/XGBoost is unavailable in the execution environment, the run fails rather than silently substituting another family.

## 12. First-screen promotion gate

A horizon/model combination is a forecast PASS only if it beats the strongest frozen baseline on the relevant primary metric.

Direction PASS:
- Brier improves >=1% relative
- log loss not worse.

Return PASS:
- MAE improves >=1% relative to best non-future baseline
- RMSE not worse.

Quantile PASS:
- mean pinball loss across Q10/Q50/Q90 improves >=1% relative to best empirical quantile baseline.

The first screen may identify:
- different winners for direction, point return and quantile distribution;
- different winners by horizon.

No single tactical champion is declared until the three forecast heads are reconciled.

## 13. Economic layer boundary

Stage 1 is a forecasting screen, not a trading backtest.

No:
- entry/exit optimization
- stop/take-profit
- transaction cost
- position sizing
- Sharpe selection

until forecast heads are frozen.

## 14. Data authority

Readiness authority:
- `GOLD_SHORT_HORIZON_DATA_READINESS_AUDIT_RESULT_2026-10-01.md`
- run 36870048143
- artifact 11166972412
- status PASS.

## 15. Exact next action

Run Stage 1:
- H1/H3/H5
- GOLD_ONLY / CORE3 / CORE3_SAFE_EXTERNAL
- frozen first model batch
- DEV 2022-2024 only.
