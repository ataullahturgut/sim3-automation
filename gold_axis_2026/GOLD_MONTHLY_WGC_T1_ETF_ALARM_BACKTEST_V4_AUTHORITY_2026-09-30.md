# GOLD MONTHLY — WGC T1 Early-Month ETF Alarm Backtest V4 Authority

**Date:** 2026-09-30
**Status:** PRE-REGISTERED / BINDING / SUPERSEDES V1-V3 PERFORMANCE CLAIMS
**Scope:** alarm detection only. No forecast correction, routing, or model switching.

## 1. Binding question

After the month-end ChHHO forecast is made, can the official WGC monthly gold-ETF report published in the first days of the target month provide a timely warning that the forecast month is in a risky regime?

T1 does not alter the forecast.

## 2. Evaluation window

Binding model-error evaluation:
- targets 2021-11..2026-08
- exactly 58 usable ChHHO rows under APE severity V3.

Every one of these 58 targets must have an authoritative WGC global ETF direction for the immediately preceding report month.

The parser may use automatic extraction. If a page is unambiguous in the official WGC article but the parser misses it, an explicit manual-authority override is allowed only when all of the following are stored:
- official WGC URL;
- publication date;
- report/data month;
- global direction;
- supporting snippet;
- reason for override.

No inferred or third-party override is allowed.

## 3. Standardized T1 alarm

For the WGC report published during target month T:

- GLOBAL_OUTFLOW = official report explicitly says global gold ETFs had net outflows / global holdings declined in data month T-1.
- GLOBAL_INFLOW = official report explicitly says global net inflows / global holdings increased in data month T-1.

**R2_WGC = current report GLOBAL_OUTFLOW AND immediately previous monthly report GLOBAL_OUTFLOW.**

This is fixed before performance evaluation.

No tonnage threshold is used.

## 4. Supplemental non-scored warning

Store a qualitative SLOWDOWN_NOTE when the official report explicitly states a sharp deterioration from the prior month.

It is not combined with R2_WGC and does not count in standardized precision/recall.

The manually verified April-2022 report published 6 May 2022 explicitly states that April inflows were 77% lower than March; this remains a descriptive warning for target 2022-05, not an R2 hit.

## 5. Manual authority override frozen before run

Exactly one required evaluation override is pre-authorized:

### Target 2021-12 / data month 2021-11
Official WGC page:
https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/2021/12

Publication:
- 7 December 2021

Global direction:
- INFLOW (+1)

Supporting statement:
- November global gold ETFs experienced net inflows of 13.6t, first positive month since July.

Previous report authority:
https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/2021/11
- published 5 November 2021
- October global ETFs experienced net outflows of 25.5t.

Therefore R2_WGC for target 2021-12 is FALSE.

No other manual evaluation override is permitted without a new authority revision.

## 6. Timeliness

TIMELY_T1:
- report publication month equals target month;
- publication calendar day <=10.

Report standardized R2 results both all-events and timely-events.

## 7. Outcome authority

APE severity:
- NORMAL <2.5%
- MEDIUM 2.5%..<3.0%
- HIGH >=3.0%.

## 8. Required metrics

R2_WGC:
- event count / event targets / publication dates;
- HIGH hits, false alarms, precision, recall;
- MEDIUM+HIGH hits, precision, recall;
- timely metrics.

Also report:
- T0 A/B/C/D/H HIGH coverage;
- incremental HIGH hits added by T1 R2;
- T0+T1 union coverage;
- remaining HIGH misses.

Explicit core audit:
- 2022-05
- 2022-07
- 2022-09
- 2024-03.

## 9. Scientific gates

- evaluation authority coverage = 58/58;
- manual overrides exactly match the frozen override registry;
- publication month = target month for every row;
- report data month = target minus one month;
- no target-month market data other than the report content itself;
- no forecast modification;
- no threshold fitting.

## 10. Interpretation

R2_WGC is a warning channel, not a hard production alarm, unless its false-alarm burden and independent transport justify later promotion.

The 2022-05 slowdown note may be described as information visible at T1, but it must not be counted as a standardized R2 hit.
