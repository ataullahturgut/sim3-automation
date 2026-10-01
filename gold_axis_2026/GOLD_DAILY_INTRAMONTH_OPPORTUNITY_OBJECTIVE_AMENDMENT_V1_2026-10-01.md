# GOLD DAILY / INTRAMONTH OPPORTUNITY — Objective Amendment V1

**Date:** 2026-10-01  
**Status:** FROZEN / SUPERSEDES DAILY PRICE-ONLY OBJECTIVE  
**Parent manifest:** `GOLD_DAILY_FORECAST_PROJECT_MANIFEST.md`

## 1. Research objective

The project is redefined from a pure next-day point-price task into an **intramonth upside-opportunity forecasting system**.

Business question:

> Even when the monthly Gold forecast is DOWN / weak, can we identify days from which a meaningful short-horizon upward excursion is likely before the month path resumes or reverses?

The daily point-price forecast remains optional/supporting. It is no longer the primary research objective.

## 2. Primary horizon

Primary opportunity horizon:
- **H = 5 future Borsa İstanbul Gold Metal Price observations**

Supporting horizons:
- H=1
- H=3
- H=10.

The 5-day horizon is primary because it is long enough to capture a tactical intramonth swing while remaining materially shorter than the monthly forecast horizon.

## 3. Origin and future path

At each signal origin:
- issue time remains **00:30 Europe/Istanbul** on a Borsa İstanbul business date D;
- the latest known official Borsa İstanbul Gold Metal Price is the prior published business-date price `P0`;
- future path consists only of official Borsa İstanbul Gold Metal Prices published after the signal:
  `P1 ... Ph`.

No same-day future Gold price may enter the predictors.

## 4. Continuous opportunity targets

For horizon h:

**Maximum Favorable Excursion**
`MFE_h = max_{k=1..h} log(Pk / P0)`

**Maximum Adverse Excursion**
`MAE_h = min_{k=1..h} log(Pk / P0)`

MAE_h is normally <=0.

Primary continuous targets:
- `MFE_5`
- `MAE_5`.

Supporting:
- MFE/MAE at 1, 3 and 10 days.

## 5. Opportunity event labels

Do not freeze a post-hoc fixed percentage after viewing 2026.

Stage 2 will pre-register a small set of **origin-scaled opportunity thresholds** using only pre-2026 development history.

Candidate threshold family:
- threshold based on origin-known recent Gold volatility / absolute-return scale;
- no threshold may use future-window volatility;
- final event threshold selected only on pre-2026 chronology.

Example conceptual label:
`UP_OPPORTUNITY_5 = 1{MFE_5 >= frozen_origin_scaled_threshold}`.

Risk quality is evaluated separately through MAE_5 rather than hidden inside the event label.

## 6. Main model outputs

The research system should eventually produce:

- `P_UP_1D`
- `P_UP_3D`
- `P_UP_5D` — primary
- `P_UP_10D`
- expected `MFE_5`
- expected `MAE_5`
- optional risk-adjusted opportunity score after DEV-only freeze.

No risk-adjusted score formula is binding yet.

## 7. Monthly forecast integration

Monthly ChHHO information is **context, not a veto**.

Allowed monthly context after chronology audit:
- monthly predicted return;
- monthly UP/DOWN sign;
- distance of monthly forecast from prior-month level;
- frozen monthly reliability probability / alarm status;
- monthly market regime / state known at the daily origin.

Forbidden:
- target-month realized monthly average;
- future monthly regime;
- any monthly outcome not known by the daily origin.

Critical comparison:
1. daily opportunity model without monthly context;
2. same model family with origin-known monthly context.

Monthly context is promoted only if it improves pre-2026 chronological opportunity prediction.

## 8. Core evaluation population

Primary business diagnostic:
- days lying inside months for which the frozen monthly model forecast was **DOWN**.

Supporting:
- all eligible daily origins;
- monthly-UP subset;
- monthly-HIGH-alarm vs no-alarm subsets where chronology permits.

The model itself need not be trained only on DOWN months. Restricting training to DOWN months is a separate hypothesis and requires enough pre-2026 sample.

## 9. Evaluation metrics

For event probability:
- Brier score
- log loss
- precision / recall
- PR-AUC where sample size supports it
- false-opportunity rate
- opportunity capture rate.

For continuous path targets:
- MFE MAE/RMSE
- MAE-risk MAE/RMSE
- calibration by predicted opportunity bucket.

Business diagnostics:
- captured realized upside
- missed large upside events
- downside experienced after positive signals
- results specifically inside monthly-DOWN months.

Do not report trading profit as a primary metric before a separate execution/cost contract exists.

## 10. Relationship to prior Daily V1/V2

Daily V1 remains INVALID.

Daily V2 remains valid retrospective evidence that direct monthly-family transfer does not beat daily persistence for next-day point price.

Neither V1 nor V2 answers the new opportunity question because they did not target future-path MFE/MAE.

Therefore they are prior evidence, not duplicate opportunity experiments.

## 11. Stage impact

Stage 1 Data Authority remains valid:
- same Borsa İstanbul Gold/four-metal authority;
- same PIT and publication rules;
- same cross-market source restrictions.

Stage 2 is redefined as:

**Opportunity Label, Baseline & Feature Contract**

It must construct MFE/MAE labels, freeze threshold candidates, define baselines and monthly-context joins before model screening.
