# Gold Control — VW V2 XAU Exact 1-Minute History Entitlement Probe

**Freeze date:** 2026-09-05  
**Identity:** `VW_MIDAS_SVR_XAU_SUCCESSOR_V2`  
**Purpose:** source-entitlement probe only; no bridge metric and no model score.

The V2 materiality bridge compares research lineage `XAU_MONTHLY_AVG_NY17_HOURLY_RESEARCH_V1` to the exact production mapping `XAU_EOD_TWELVE_NY17` (Twelve Data `XAU/USD`, 1-minute, America/New_York, exact 16:59 bar close).

Before attempting a historical exact-lineage bridge, probe whether the existing Twelve Data entitlement can retrieve the exact 16:59 bar on three preselected historical dates:

- `2024-12-16`
- `2025-06-16`
- `2026-08-28`

PASS requires all three requests to return exactly one `16:59:00` bar with positive finite OHLC fields. Raw market values must not be logged or committed.

PASS means only `HISTORICAL_EXACT_1MIN_BRIDGE_SOURCE_ENTITLEMENT_PROVEN_FOR_PROBE_DATES`; it does not prove the materiality bridge.

Any plan/history/access failure or missing exact bar yields `BLOCKED_HISTORICAL_EXACT_1MIN_BRIDGE_SOURCE_NOT_PROVEN`. No fallback or proxy is permitted.
