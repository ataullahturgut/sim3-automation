# GOLD MONTHLY — WGC T1 Early-Month ETF Alarm Backtest V3 Authority

**Date:** 2026-09-30
**Status:** PRE-REGISTERED / BINDING / SUPERSEDES V1-V2 PERFORMANCE CLAIMS
**Scope:** alarm detection only. No forecast correction, routing, or model switching.

## 1. Reason for V3

Historical WGC article templates do not expose a single homogeneous numeric tonnes field in prose across all years. V1 and V2 parser gates therefore correctly rejected performance claims.

V3 tests only a field that is explicit and stable in the monthly reports:
**the direction of global monthly ETF demand: NET INFLOW vs NET OUTFLOW.**

No tonnage magnitude is required for the binding alarm.

## 2. T1 timing

For target month T:
- month-end ChHHO forecast T0 remains unchanged;
- WGC report published in T describes month T-1;
- T1 may issue a warning on the actual report publication date.

TIMELY_T1 = publication day <=10 and publication month = target month.

## 3. Binding standardized report alarm R2-WGC

For each report determine:
- GLOBAL_OUTFLOW = report explicitly states global gold ETFs had net outflows / holdings declined for the report month.
- GLOBAL_INFLOW = report explicitly states global net inflows / holdings increased for the report month.

**R2_WGC = GLOBAL_OUTFLOW in the current report AND GLOBAL_OUTFLOW in the immediately preceding monthly report.**

This is the WGC-report analogue of redemption persistence.

No numeric threshold and no future calibration are used.

## 4. Supplemental qualitative flag, not scored as standardized alarm

If a report explicitly states a sharp deterioration versus the prior month (for example a quantified large slowdown), store:
- SLOWDOWN_NOTE = TRUE
- supporting snippet.

This is descriptive only and is NOT combined with R2_WGC for precision/recall, because no historically frozen magnitude threshold exists.

## 5. Outcome authority

APE:
- NORMAL <2.5%
- MEDIUM 2.5%..<3.0%
- HIGH >=3.0%.

Evaluation: 2021-11..2026-08.

## 6. Required outputs

For R2_WGC:
- all alarm targets;
- publication dates;
- HIGH hit/false alarm/precision/recall;
- MEDIUM+HIGH hit/precision/recall;
- timely metrics.

Explicit core audit:
- 2022-05
- 2022-07
- 2022-09
- 2024-03.

Also show T0 A/B/C/D/H HIGH misses and which are detected by R2_WGC.

## 7. Parser gate

- >=95% of 2019-01..2026-08 report pages must yield publication date + unambiguous global direction.
- every 2021-11..2026-08 evaluated target must have a parsed direction or explicit manual-authority override tied to an official WGC page/snippet;
- no regional or individual-fund direction may substitute for global direction.

## 8. Governance

- Forecast unchanged.
- No target-month market data other than report arrival/content.
- No threshold optimization.
- No R1 OR R2 composite.
- No production hard-alarm claim from this backtest alone.
