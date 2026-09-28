# GOLD MONTHLY FORECAST — CHALLENGER B / ARIMA + SARIMA + PROPHET RESULT

**Date:** 2026-09-28  
**Status:** COMPLETE / SCIENTIFIC GATE PASS  
**Workflow run:** 36438580750  
**Commit:** 311960f1a024971e36fa2810e4f18422a2743fb1  
**Freeze:** `GOLD_MONTHLY_CHALLENGER_B_CLASSICAL_TRIO_FREEZE_2026-09-28.md`

## Scope
Only the user-requested classical families were run:
- ARIMA
- SARIMA
- Prophet

Theta, Optimized Theta, Dynamic Ridge, Linear SVR, SARIMAX_SAFE and other missing Grup-ARGE families were intentionally not run.

## Input path
These three models are univariate time-series models and therefore do not consume CURRENT8 MR/VW predictors.

Input:
- authoritative completed monthly average XAU/USD Gold price level
- training start: 2010-05
- no scaling
- no external regressors
- no target-month leakage

Inner selection:
- latest 12 matured pre-target months
- fit each candidate through the month before the 12-month validation block
- forecast the 12-month validation block
- select by cumulative absolute price error
- refit selected candidate through current outer origin
- make H=1 next-month forecast

## ARIMA
Candidate grid preserved from Grup-ARGE:
- ARIMA_A: (1,0,0), trend='c'
- ARIMA_B: (1,1,1), trend='t'
- ARIMA_C: (0,1,1), trend='t'

### DEV 2022-04..2024-12
- n = 33
- SigmaAE = **1781.7822051610337**
- MAE = **53.99340015639496**
- RMSE = **67.00336486974027**
- MAPE = **2.659360961911125%**
- Direction = **15/33 = 45.45%**
- Relative MAE vs Random Walk = **1.0135279892838644**
- Random-Walk SigmaAE = **1758.0**
- Worst AE = **144.54378093856394**, 2024-03

DEV candidate counts:
- ARIMA_A: 7
- ARIMA_B: 13
- ARIMA_C: 13

**Decision: NOT PROMOTED.** ARIMA is worse than Random Walk on the primary DEV cumulative absolute error metric.

### 2025 — LOCKED REPORT ONLY
- SigmaAE = 1320.1102792504253
- Direction = 11/12
- Relative MAE vs RW = 0.7825194304981774

### 2026 Jan-Jul — QUARANTINED REPORT ONLY
- SigmaAE = 1954.6802568679968
- Direction = 2/7
- Relative MAE vs RW = 1.1789386350229172

## SARIMA
Candidate grid preserved from Grup-ARGE:
- SARIMA_A: order=(1,0,0), seasonal_order=(1,0,0,12), trend='n'
- SARIMA_B: order=(0,1,1), seasonal_order=(0,1,1,12), trend='n'

### DEV 2022-04..2024-12
- n = 33
- SigmaAE = **1751.5241620312304**
- MAE = **53.076489758522136**
- RMSE = **63.4162481227134**
- MAPE = **2.597563209546728%**
- Direction = **19/33 = 57.58%**
- Relative MAE vs Random Walk = **0.9963163606548523**
- Random-Walk SigmaAE = **1758.0**
- Worst AE = **128.26666742624707**, 2024-03

DEV candidate counts:
- SARIMA_A: 18
- SARIMA_B: 15

**Decision: NOT PROMOTED.** SARIMA is only marginally better than Random Walk on DEV price error and remains far behind the active Challenger-A / Challenger-B frontier.

### 2025 — LOCKED REPORT ONLY
- SigmaAE = 1374.5672802758231
- Direction = 11/12
- Relative MAE vs RW = 0.8147998104776664

### 2026 Jan-Jul — QUARANTINED REPORT ONLY
- SigmaAE = 1849.4114083452878
- Direction = 2/7
- Relative MAE vs RW = 1.1154471702926947

## Prophet
Candidate grid preserved from Grup-ARGE:
- PROPHET_A: changepoint_prior_scale=0.01, seasonality_prior_scale=1.0, seasonality_mode='additive'
- PROPHET_B: changepoint_prior_scale=0.1, seasonality_prior_scale=1.0, seasonality_mode='multiplicative'

The first V1 workflow encountered a technical Prophet/CmdStanPy backend compatibility failure before Prophet could produce scientific results. It is superseded by V2, which pinned cmdstanpy=1.2.5 and explicitly used CMDSTANPY. ARIMA/SARIMA were rerun in V2 so all three final results share one clean successful workflow.

### DEV 2022-04..2024-12
- n = 33
- SigmaAE = **7521.135958997547**
- MAE = **227.91321087871356**
- RMSE = **271.66929852659484**
- MAPE = **10.63118095213465%**
- Direction = **14/33 = 42.42%**
- Relative MAE vs Random Walk = **4.278234333900766**
- Random-Walk SigmaAE = **1758.0**
- Worst AE = **548.8403746651152**, 2024-10

DEV candidate counts:
- PROPHET_A: 8
- PROPHET_B: 25

**Decision: REJECT / NOT PROMOTED.** Prophet is dramatically worse than Random Walk and the active model frontier in this frozen raw-monthly-price implementation.

### 2025 — LOCKED REPORT ONLY
- SigmaAE = 8109.539516607124
- Direction = 1/12
- Relative MAE vs RW = 4.8070773660978805

### 2026 Jan-Jul — QUARANTINED REPORT ONLY
- SigmaAE = 5233.697016950674
- Direction = 5/7
- Relative MAE vs RW = 3.156632700211504

## Classical trio DEV ordering
1. SARIMA — **1751.52 / 19**
2. ARIMA — **1781.78 / 15**
3. Prophet — **7521.14 / 14**

None enters the active Challenger-B frontier.

## Governance
- Scientific gate PASS.
- DB READ_ONLY.
- Random split NONE.
- DEV is sole selection authority.
- 2025 locked.
- 2026 quarantined.
- Main Challenger-A / Gold Monthly path unchanged.

Result payload SHA256:
`83cd79f5feaeac140c127a15c5019d6a66d426c3df5c5e9dccb1853f1e1af30f`
