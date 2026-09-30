# GOLD MONTHLY — WGC T1 Early-Month ETF Alarm Backtest V2 Authority

**Date:** 2026-09-30
**Status:** PRE-REGISTERED / SUPERSEDES V1 FLOW-TEXT PARSER
**Scope:** alarm detection only. No forecast correction, no routing, no model switching.

## 1. Why V2

V1 attempted to extract the article's prose description of monthly global fund-flow tonnes directly. Historical WGC article formats mix:
- monthly flow,
- YTD/quarter totals,
- regional flows,
- individual-fund flows.

The V1 parser gate correctly rejected the backtest because full reliable coverage was not achieved.

V2 uses the WGC's **global total gold-ETF holdings level in tonnes** from each monthly report and derives monthly demand mechanically from consecutive published holdings levels.

WGC defines gold ETF demand as the change in gold holdings during a period. This creates a homogeneous, auditable T1 state and avoids selecting the wrong prose number.

## 2. Timing

For target month T:
- T0 ChHHO forecast remains the month-end forecast.
- T1 is the official WGC monthly ETF report published during T, describing T-1.
- The forecast is NOT changed.
- T1 only issues or does not issue an alarm.

Publication date is binding and stored.

## 3. Source

Official WGC monthly archive:
`https://www.gold.org/goldhub/research/gold-etfs-holdings-and-flows/YYYY/MM`

Extract only:
- publication date;
- report/data month;
- global/collective total ETF holdings in tonnes at the end of the report month;
- exact supporting text snippet.

Derived series:
- DEMAND_t = HOLDINGS_t - HOLDINGS_(t-1)
- DELTA_DEMAND_t = DEMAND_t - DEMAND_(t-1)

No regional or individual-fund number is allowed as the global holdings level.

## 4. T1 signals

### R1 — WGC DEMAND DETERIORATION
At publication of report t:
- calculate Q10 of all previously published valid DELTA_DEMAND observations;
- minimum 24 prior observations;
- R1 = DELTA_DEMAND_t <= prior-history Q10.

This is rolling PIT calibration. Future reports are never used.

### R2 — WGC REDEMPTION PERSISTENCE
R2 = DEMAND_t < 0 AND DEMAND_(t-1) < 0.

### T1_ANY
T1_ANY = R1 OR R2.

The OR is frozen before outcome evaluation.

## 5. Timeliness

TIMELY_T1 if the report is published in the target month and on calendar day <=10.

Report all alarms and timely alarms separately.

## 6. Outcome authority

APE severity V3:
- NORMAL <2.5%
- MEDIUM 2.5%..<3.0%
- HIGH >=3.0%.

Evaluation: 2021-11..2026-08.

## 7. Required outputs

For R1, R2 and T1_ANY:
- event targets and report publication dates;
- HIGH hits / precision / recall;
- MEDIUM+HIGH hits / precision / recall;
- normal false alarms;
- timely metrics.

Explicitly audit:
- 2022-05
- 2022-07
- 2022-09
- 2024-03.

Also show:
- HIGH misses after T0 A/B/C/D/H;
- which of those T1 detects;
- final HIGH misses after T0+T1.

## 8. Parser gates

For 2019-01..2026-08:
- >=90% pages must yield publication date + valid global holdings level;
- global holdings level must be within 1,000t..6,000t;
- evaluation period may have no undocumented missing month;
- publication month must match target month;
- data month is target-1.

If these gates fail, no performance claim is allowed.

## 9. Governance

- No target-month market data other than the arrival of the WGC report.
- No forecast modification.
- No threshold tuning against ChHHO errors.
- No router/fallback test.
