# Gold Control — VW V2 XAU Research-to-Production Bridge Execution Contract

**Freeze date:** 2026-09-05  
**Identity:** `VW_MIDAS_SVR_XAU_SUCCESSOR_V2`  
**Status:** `FROZEN_BEFORE_BRIDGE_METRICS`  
**Parent V2 contract:** `GOLD_CONTROL_VW_MIDAS_SVR_XAU_SUCCESSOR_V2_CHANGE_CONTROL_2026-09-05.md`

## 1. Purpose

Execute the already-frozen materiality bridge between:

- research lineage `XAU_MONTHLY_AVG_NY17_HOURLY_RESEARCH_V1` = Twelve Data `XAU/USD`, `1h`, `America/New_York`, `16:00` bar close;
- production mapping `XAU_EOD_TWELVE_NY17` = Twelve Data `XAU/USD`, `1min`, `America/New_York`, exact `16:59` bar close.

This is source/lineage validation only. It is not model tuning and cannot change V2 features, grid, windows, benchmark, or validation gates.

## 2. Source-driven bridge window

A pre-metric entitlement probe on frozen dates established:

- exact historical 1-minute bar present on `2025-06-16` and `2026-08-28`;
- exact historical 1-minute bar not returned on `2024-12-16`.

No bridge metric was computed in that probe.

Before any bridge metric is observed, freeze the bridge sample as twelve consecutive fully completed months:

`2025-07` through `2026-06` = 12 months.

The start is after the earliest successful historical exact-1m probe month and the end is the last month needed to form a 12-month consecutive source comparison without using the current partial month. This window may not move after bridge metrics are seen.

## 3. Daily construction

For every month in the frozen bridge window:

1. fetch research `1h` bars and select exact `16:00:00` bar timestamp;
2. fetch exact production-mapping `1min` bars in bounded <=3-calendar-day chunks and select exact `16:59:00` bar timestamp;
3. require at least 15 positive finite daily references in each lineage;
4. require the daily date sets to match exactly within each month;
5. compute the arithmetic monthly mean separately for the two lineages.

No raw vendor value may be printed, committed, or uploaded as evidence.

## 4. Frozen bridge gates

PASS requires all of:

- 12/12 frozen months complete;
- level correlation >= `0.995`;
- median absolute level gap <= `50 bps`;
- p95 absolute level gap <= `100 bps`;
- monthly return correlation >= `0.95`;
- monthly return sign agreement >= `0.80`.

No threshold relaxation is permitted.

## 5. Outcomes

All gates pass:

`XAU_RESEARCH_TO_PRODUCTION_LINEAGE_BRIDGE_PASS`

Any source/coverage failure:

`BLOCKED_XAU_RESEARCH_TO_PRODUCTION_LINEAGE_BRIDGE_SOURCE_OR_COVERAGE_NOT_PROVEN`

All source coverage complete but any materiality gate fails:

`BLOCKED_XAU_RESEARCH_TO_PRODUCTION_LINEAGE_BRIDGE_MATERIALITY_FAIL`

A PASS removes only the V2 XAU lineage bridge blocker. It does not by itself grant prospective issuance, selector/ensemble authority, production forecast writes, or position/action authority.
