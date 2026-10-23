# 2026 January–February GOLD daily H=1 actual execution and shock-detection audit

Date: 2026-10-23
GitHub branch: gold-daily-h1-janfeb2026-v1-20261023
Execution: https://github.com/ataullahturgut/sim3-automation/actions/runs/40005502353 (7/7 jobs SUCCESS)
Model: DAILY_H1_4_METAL_ANN_FIXED8_TANH_ALPHA1_RESEARCH
Source: immutable four-metal aligned daily lbruton/StakTrakr Git-pinned retrospective non-firstprint series, with exact monthly view parity. February 27 2026 source price 3516.02 explicitly quarantined due independent Reuters reporting >5230.
Code: tools/gold_daily_h1_2026_jan_feb_event_replay_v1.py
Workflow: .github/workflows/gold-daily-h1-jan-feb-2026-event-replay-v1.yml
Result artifact: gold-daily-h1-janfeb2026-final-all-day-shock-comparison
Source artifact: gold-d1-janfeb-2026-immutable-source
Audit artifact: gold-d1-janfeb-2026-active-future-poison-audit

## The precise forecast experiment

- Next *common trading day's* single daily reference gold price compared to previous common trading day reference quote; **NOT intraday low, daily close, 16:00 NY anchor, intraday max drawdown or news anticipation**.
- Same four Au Ag Pt Pd as monthly/weekly research source, but **new and independent** 1-day model. For each metal input is previous day's log return, trailing 3-day cumulative log return, trailing 5-day cumulative log return and 5-day realized daily squared-return RMS volatility = 16 origin-safe numerical features.
- Fixed nonoptimized one-hidden-layer 8 tanh ANN MLPRegressor, solver lbfgs, alpha 1.0, max_iter 160, random seed 1701, scaler fit on completed past target labels and predictors ONLY. Expanding training since 2010, each day retrained at preceding market observation, no target-day prices, news, post-impact data or threshold tuning allowed.
- Severe-drop early warning if predicted 1-day return <= -3%; crash early warning if <=-5%. Both pre-defined for audit; ordinary negative return **does not** count as severe-drop detection.
- Calendar day Jan 1 missing quote is not imputed; 21 shared-trading-day target labels Jan and 20 Feb of which **Feb27 excluded**. Total **40 valid target days** Jan/Feb 2026.
- 40/40 targeted target-label and 2099 synthetic future poisoning PASS; same input features/training unaffected. Source read-only, no production app and no database writes.
- Data limit: 2026-02-27 **source anomaly** not scored, not used as a training input after it, no artificial price replacement; original evidence preserved.
- Historical first-print/PIT of price source NOT certified, thus retrospective diagnostic only. Not investor-grade production or validated real-time prediction.

## Actual results

| Period | Days | Correct daily direction | ANN quote MAPE | No-change naive quote MAPE | Actual <=-3% down days | Predicted <=-3% down alerts | Severe-down prior-day hits | Actual <=-5% crashes | Crash predicted before day |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026 Jan | 21 | 13 (61.9%) | 1.723183% | 1.761993% | 1 | 0 | 0 | 1 | 0 |
| 2026 Feb (except anomalous Feb27) | 19 | 7 (36.8%) | 2.390626% | **2.043900%** | 2 | 0 | 0 | 1 | 0 |
| Total | 40 | **20 (50%)** | **2.040218%** | **1.895899%** | **3** | **0** | **0** | **2** | **0** |

### Crucial exact chronological predictions

| Issue day | Target | Predicted return | Actual quote-to-quote return | Forecast XAU | Actual XAU | Direction | Predicted severe fall? |
|---|---|---:|---:|---:|---:|---|---|
| 2026-01-28 | 2026-01-29 | +1.28594% | +4.24230% | 5345.6695 | 5501.70 | correct UP | no |
| 2026-01-29 | 2026-01-30 | **-0.41435%** | **-7.96572%** | 5478.9037 | 5063.45 | correct DOWN | **NO** |
| 2026-01-30 | 2026-02-02 | **-0.26017%** | **-7.46527%** | 5050.2764 | 4685.45 | correct DOWN | **NO** |
| 2026-02-02 | 2026-02-03 | -1.46209% | +5.08382% | 4616.9447 | 4923.65 | WRONG DOWN vs UP | no |
| 2026-02-03 | 2026-02-04 | +0.14547% | +2.60173% | 4930.8126 | 5051.75 | correct UP | no |

**Binding conclusion:** While model guessed ordinary DOWN sign on Jan30 and Feb2, it **DID NOT FORECAST THE CRASH** before it happened. Both -7%+ session-to-session quote drops had pred magnitudes below 0.5%, and predefined 3% and 5% fall signals never activated. Across the 40 days there were 3 actual <=-3% down days and 2 <=-5% days; **none were predicted**. The model's full 40-day direction 20/40 (50%) and quote MAPE > unchanged-last-price baseline make it unsuitable for promotion. Do not retrofit thresholds on Jan/Feb shock events and then claim ex-ante success.

Reuters Jan 30 reports contemporaneous intraday spot gold fall 9.5% (not equivalent to StakTrakr single daily reference day-to-day -7.97%); do NOT falsely compare these as same price metric:
https://www.reuters.com/world/india/gold-slips-firmer-dollar-set-best-month-since-1980-2026-01-30/

## Next independent model experiment (not executed)

- Build shock-risk classifier from ONLY matured past daily labels and pre-origin inputs on a pre-Jan2026 training/calibration timeframe, with months 2026 Jan-Feb locked for untouched report of recall, precision, false alarms and magnitude.
- Add origin-known cross-metal divergence, historical multi-day acceleration, realized vol change, CFTC/GVZ/GPR last known releases, regime transitions only with true daily availability/as-of metadata.
- Score event-risk and expected move separately, not merely sign. Avoid evaluating on target intraday prices when source supports just daily close/fixing.
- Do not quietly strip bad Feb27 from historical source; preserve quarantined sample and public-price conflict.
