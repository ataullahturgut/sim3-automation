# GOLD H1 R1 — Data Gate Audit R1

Date: 2026-08-29

## Purpose
Before any weekly event-level reversal model is built, audit whether the monthly and tactical source chains are sufficiently trustworthy for 2010–2022 research.

## Monthly canonical chain
Status: PASS_PROJECT_CANONICAL

Evidence from the locked canonical workbook:
- monthly master has 390 rows, 1994-02 through 2026-07;
- 43 evaluation origins;
- 43/43 target reconciliation;
- 3M Momentum formula reproduced exactly from canonical monthly prices;
- random split = none;
- 2026 tuning = none.

Important caveat:
- the canonical source manifest contains an old note implying the pinned precious-metals daily rows are all LBMA. This is not true for later raw history; 2026 inspection shows provider/source transitions and calendar/weekend rows. Therefore raw StakTrakr daily history is NOT treated as a homogeneous official-LBMA tactical source.

## XAUUSD tactical source
Pinned repository:
- simom1/XAUUSD-history
- commit f09a4dea9de06fc1b9f58ff95f7cffaa193b70c0
- D1: Gold-Cash/XAUUSD/XAUUSD_D1.csv
- W1: Gold-Cash/XAUUSD/XAUUSD_W1.csv

Repository documentation states the OHLCV files are exported from MetaTrader 5 and timestamps are UTC. This is an independent broker/MT5 market-history source, not an official LBMA fixing series.

## D1 -> W1 aggregation spot checks at the pinned commit
A full raw-file byte-level automatic reaggregation could not be executed in the current local runtime because the connector exposes the source by ranged reads rather than mounting the entire public file. Therefore this audit does NOT claim an exhaustive row-for-row D1->W1 proof.

However, direct pinned-commit aggregation checks were performed across widely separated historical periods:

### Week labelled 2010-01-03
D1 2010-01-04..2010-01-08:
- open 1096.7
- max high 1140.3
- min low 1093.05
- Friday close 1136.0
- summed tick volume 13720

Pinned W1 2010-01-03:
- 1096.7, 1140.3, 1093.05, 1136.0, 13720

Result: EXACT.

### Week labelled 2014-08-10
D1 2014-08-11..2014-08-15 aggregates to:
- open 1308.49
- high 1319.29
- low 1292.03
- close 1304.51
- tick volume 11085

Pinned W1 2014-08-10:
- 1308.49, 1319.29, 1292.03, 1304.51, 11085

Result: EXACT.

### Week labelled 2020-08-30
D1 2020-08-31..2020-09-04 aggregates to:
- open 1965.41
- high 1992.28
- low 1916.44
- close 1933.70
- tick volume 860699

Pinned W1 2020-08-30 matches exactly.

Result: EXACT.

### Week labelled 2022-09-04
D1 2022-09-05..2022-09-09 aggregates to:
- open 1712.04
- high 1729.44
- low 1691.35
- close 1717.37
- tick volume 450802

Pinned W1 2022-09-04:
- 1712.04, 1729.44, 1691.35, 1717.37, 450802

Result: EXACT.

## Time-axis interpretation
The W1 timestamp is the Sunday/week-open label for the following Monday-Friday trading week. Therefore a month-end Tactical origin must use only a weekly bar whose nominal Friday has completed by the forecast origin. An incomplete current week must not be used.

This convention is consistent with the previously reconstructed 2023 Tactical states and prevents look-ahead from a partial target-month/week bar.

## Existing long-history Tactical reconciliation
The archived Tactical R1 audit reports:
- DEV 2010-2020: CONFIRM N=53, CONFLICT N=36, NEUTRAL N=40;
- VAL 2021-2023: CONFIRM N=14, CONFLICT N=14, NEUTRAL N=7;
- frozen Slow rule: sign(completed weekly close - SMA4), with 2 consecutive completed weeks required for UP/DOWN persistence.

These historical audit counts remain the current full-history reconciliation evidence. The new source checks above independently confirm the D1/W1 aggregation semantics at several separated points, but do not replace a complete raw-file reaggregation.

## Data-gate decision
- CANONICAL_MONTHLY_GOLD = PASS
- 3M_REPRODUCIBILITY = PASS
- XAUUSD_PINNED_SOURCE_IDENTITY = PASS
- D1_W1_AGGREGATION_SEMANTICS = PASS_SPOTCHECKS
- FULL_2010_2022_D1_W1_ROW_RECONCILIATION = NOT_YET_EXHAUSTIVELY_PROVEN
- STAKTRAKR_AS_HOMOGENEOUS_LBMA_DAILY_SOURCE = REJECT
- XAUUSD_W1_AFTER_SPRING_2026 = FAIL / DO_NOT_USE_RAW
- WEEKLY_EVENT_LEVEL_RESEARCH_2010_2022 = ALLOWED_WITH_PINNED_XAUUSD_SOURCE_AND_FROZEN_TIME_AXIS, but any production approval must retain the source caveat until full-file automated reconciliation is archived.

## Next modeling rule
For the 2010-2022 reversal-strength study, use only:
1. canonical monthly GOLD for monthly prior/target,
2. pinned XAUUSD-history commit for completed weekly/daily Tactical features,
3. frozen completed-week cutoff and persistence definitions,
4. DEV 2010-2020 and validation 2021-2022,
5. no 2023+ tuning.

Do not use raw StakTrakr daily history as the Tactical primary source.
