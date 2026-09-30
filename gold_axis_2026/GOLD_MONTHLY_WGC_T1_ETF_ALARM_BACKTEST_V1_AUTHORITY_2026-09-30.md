# GOLD MONTHLY — WGC T1 Early-Month ETF Alarm Backtest V1 Authority

**Date:** 2026-09-30
**Status:** PRE-REGISTERED / BINDING T1 ALARM TEST
**Scope:** alarm detection only. No forecast correction, no routing, no model switching.

## 1. Timing

T0 = month-end ChHHO forecast.

T1 = first official World Gold Council monthly gold-ETF report published during the target month, describing the immediately preceding month.

Example:
- target 2022-07
- T0 forecast made at end-June
- WGC June ETF report published 7 July 2022
- T1 alarm may be emitted on 7 July 2022, without changing the forecast.

Publication date is part of the audit. No report information is backdated to T0.

## 2. Source

Official monthly World Gold Council pages:
`https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/YYYY/MM`

For each page store:
- page URL
- report/data month
- publication date
- as-published global monthly ETF net flow in tonnes
- extraction snippet
- parser confidence.

The test uses the historical article text as published, not a later revised monthly dataset.

## 3. T1 signals

### R1 — WGC FLOW DETERIORATION
Let FLOW_t be the as-published global monthly ETF net flow in tonnes in the T1 report.
Let DELTA_t = FLOW_t - FLOW_(t-1).

At each report publication, compute Q10 of **prior** DELTA observations only, requiring at least 24 prior valid deltas.

R1 = DELTA_t <= prior-history Q10.

This is a rolling PIT threshold; future reports are never used to calibrate an earlier T1 alarm.

### R2 — WGC REDEMPTION PERSISTENCE
R2 = FLOW_t < 0 and FLOW_(t-1) < 0.

This is the report analogue of the independently discovered ETF redemption-persistence mechanism.

### T1_ANY
T1_ANY = R1 OR R2.

This OR is frozen before outcome evaluation and is used only for alarm-coverage reporting.

## 4. Timeliness

Record calendar days after target-month start:
`publish_day = publication day-of-month`.

Operational early-month alarm:
- **TIMELY_T1 = publication date within the first 10 calendar days of the target month.**

Report both:
- all T1 alarms;
- timely T1 alarms.

Do not silently discard late reports.

## 5. Error severity authority

Use the binding APE bands:
- NORMAL <2.5%
- MEDIUM 2.5%..<3.0%
- HIGH >=3.0%

Evaluation rows:
- 2021-11..2026-08 ChHHO usable targets.

## 6. Required outputs

For R1, R2, and T1_ANY:
- events
- publication dates
- HIGH hits
- MEDIUM hits
- false alarms
- HIGH precision / recall
- MEDIUM+HIGH precision / recall
- timely-event metrics.

Explicitly report these four previously unexplained core HIGH targets:
- 2022-05
- 2022-07
- 2022-09
- 2024-03.

Also report all HIGH targets that remain undetected after A/B/C/D/H at T0 and T1_ANY at T1.

## 7. Parser/scientific gates

- At least 90% of monthly report pages needed for 2019-01..2026-08 must yield a valid publication date and signed global flow.
- Every evaluated 2021-11..2026-08 target must have either a parsed T1 report or an explicit documented missing-source status.
- Publication month must equal target month.
- Report data month must equal target month minus one month.
- No target-month market data other than the publication event itself is used.
- No thresholds retuned from ChHHO errors.

If parser coverage is insufficient, the test is incomplete and no alarm-performance claim may be made.
