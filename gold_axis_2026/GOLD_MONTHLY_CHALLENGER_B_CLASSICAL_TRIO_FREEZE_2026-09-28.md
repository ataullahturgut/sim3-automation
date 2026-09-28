# GOLD MONTHLY FORECAST — CHALLENGER B / ARIMA + SARIMA + PROPHET FREEZE

**Freeze date:** 2026-09-28
**Branch:** `gold-midas-headswap-v1-20260925`
**Status:** PRE-RUN METHOD FREEZE

## Scope
Run only the three user-requested missing Grup-ARGE families:
1. ARIMA
2. SARIMA
3. Prophet

No Theta, Dynamic Ridge, Linear SVR, SARIMAX_SAFE or other omitted Grup-ARGE models are run.

## Input contract
These are classical univariate time-series models. They do **not** consume CURRENT8 MR/VW predictors.
- Input series: authoritative completed monthly average XAU/USD Gold price from the same governed Gold Monthly data bundle.
- Training start: 2010-05.
- Business target: H=1 next-calendar-month average XAU/USD price.
- Forecast origin: previous completed calendar month.
- No target-month values in fit or tuning.
- No scaling.
- Random split: NONE.

## Inner candidate-selection design
For each outer target month:
- reserve the latest 12 matured pre-target months as the inner validation block;
- fit each candidate once using history ending immediately before that 12-month validation block;
- produce a 12-step monthly forecast path;
- score cumulative absolute Gold price error over those 12 pre-target months;
- choose the lowest-SigmaAE candidate; deterministic candidate-order tie-break;
- refit the selected candidate on **all** matured months through the current outer origin;
- make the H=1 outer forecast.

This preserves chronology and prevents target leakage. The 12-step inner block is a hyperparameter-selection device only; the outer scientific target remains H=1.

## ARIMA candidate grid — preserved from Grup-ARGE live run
- ARIMA_A: order=(1,0,0), trend='c'
- ARIMA_B: order=(1,1,1), trend='t'
- ARIMA_C: order=(0,1,1), trend='t'

Implementation: statsmodels.tsa.arima.model.ARIMA.

## SARIMA candidate grid — preserved from Grup-ARGE live run
- SARIMA_A: order=(1,0,0), seasonal_order=(1,0,0,12), trend='n'
- SARIMA_B: order=(0,1,1), seasonal_order=(0,1,1,12), trend='n'

Implementation: statsmodels.tsa.statespace.sarimax.SARIMAX.
Binding: enforce_stationarity=False, enforce_invertibility=False.

## Prophet candidate grid — preserved from Grup-ARGE live run
- PROPHET_A:
  - changepoint_prior_scale=0.01
  - seasonality_prior_scale=1.0
  - seasonality_mode='additive'
- PROPHET_B:
  - changepoint_prior_scale=0.1
  - seasonality_prior_scale=1.0
  - seasonality_mode='multiplicative'

Implementation: Prophet with defaults otherwise preserved.
- yearly_seasonality='auto'
- weekly_seasonality='auto' (automatically disabled for monthly spacing)
- daily_seasonality='auto' (automatically disabled for monthly spacing)
- no external regressors
- interval output is diagnostic only.

## Evaluation
Primary: DEV cumulative absolute price error (SigmaAE).
Secondary: direction accuracy, MAE, RMSE, MAPE, WAPE, relative MAE vs Random Walk, worst month, yearly stability.

Direction is sign(forecast - previous completed-month Gold average) vs sign(actual - previous completed-month Gold average).

## Period roles
- DEV: 2022-04..2024-12, n=33 — sole model-selection/comparison authority.
- 2025: LOCKED_REPORT_ONLY.
- 2026-01..2026-07: QUARANTINED_REPORT_ONLY.

## Governance
- DB READ_ONLY.
- Existing Challenger-A/main Gold path unchanged.
- 2025/2026 cannot rescue, tune or promote any of the three models.
- After all three complete, Challenger-B results are consolidated into a single manifest.
