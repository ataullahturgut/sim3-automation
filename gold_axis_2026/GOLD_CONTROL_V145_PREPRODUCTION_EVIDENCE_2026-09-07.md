# GOLD CONTROL — V1.45 LIVE-DATA PREPRODUCTION EVIDENCE

**Evidence date:** 2026-09-07  
**Branch:** `gold-control-live-frequency-v145`  
**Status:** PRE-PRODUCTION / NOT YET CANONICAL

## 1. Purpose

This evidence package records the source-access and frequency tests required before any Gold Control layer is promoted from EOD/batch context to live/event-time context. It does not authorize forecast, decision, selector, ensemble or position writes.

## 2. Engine-frequency conclusions

The existing engine identities are not all converted to intraday operation.

- H=1 experts (`VW_MIDAS_MSVR_SUCCESSOR_V1`, `CAUSAL_PATCH`, `MOMENTUM_3M`, `RANDOM_WALK`): month-origin frozen.
- `MONTHLY_DIRECTION_3M`: month-open frozen.
- `FAST`: completed trade-date daily; unchanged.
- `SLOW`: completed week; unchanged.
- `BOCPD_RETURN_SUCCESSOR_V1`: completed month; unchanged.
- `EMERGENCY_LEVEL` / `EMERGENCY_REVERSAL`: existing V1.44 path remains EOD confirmation; separate V1.45 live-provisional features are introduced for intraday alerting.
- `MACRO_EVENT_SUCCESSOR_V2`: official release-time architecture is required.
- `GVZ_RISK`: current `GVZ_CBOE` remains EOD risk context until a separately authorized intraday source is proven.

## 3. Twelve Data XAU/USD WebSocket — PROVEN

GitHub Actions preflight:

- workflow run: `34118583040`
- job: `101731085759`
- result: `SUCCESS`
- provider: Twelve Data WebSocket
- symbol: `XAU/USD`
- endpoint: `wss://ws.twelvedata.com/v1/quotes/price`
- preflight classification: `PROVEN`
- observed valid price event: `4391.55066`
- provider event timestamp: `1788781740`
- receive timestamp: `2026-09-07T11:49:26.932618Z`
- observed provider events in probe: `2`

This proves that the currently configured Twelve Data credential can receive XAU/USD WebSocket price events in the GitHub Actions runtime. It does not by itself prove 24/7 continuous production operation.

## 4. Emergency live dry-run — PASS

Preproduction workflow run `34122117326` executed the V1.45 Emergency live worker for 75 seconds in read-only/dry-run mode.

Observed result:

- self-test: `PASS`
- completed live minute processed: `1`
- minute: `2026-09-07T12:29:00Z`
- completed-minute close: `4394.25232`
- provider events aggregated into that minute: `14`
- monthly reference expert: `CAUSAL_PATCH`
- monthly reference value: `4452.046728838838`
- reference evidence: `HISTORICAL_REPLAY`
- live provisional level state: `NEUTRAL`
- live reversal state: `NOT_READY_INTRAMONTH_BOOTSTRAP_REQUIRED`
- DB writes: `NONE`
- decision-store writes: `NONE`
- forecast-authority writes: `NONE`

The reversal state intentionally remains blocked until historical intraday bootstrap data are persisted. This is fail-closed behavior, not an implementation failure.

## 5. XAU intraday REST bootstrap — ACCESS PROVEN / NOT YET PERSISTED

The same preproduction run queried Twelve Data XAU/USD 1-minute REST history for 2026-09-07.

Result:

- valid 1-minute rows retrieved: `750`
- database write requested: `false`
- source role: historical intramonth reversal bootstrap only
- prospective claim: `false`

The bootstrap source must not be treated as live authority. Its purpose is deterministic reconstruction of current-month peak/trough state before the live WebSocket worker starts.

## 6. BLS Employment Situation actual data — SOURCE ACCESS PROVEN

Official BLS Public Data API v2 preflight passed in workflow run `34122117326`.

Series checked:

- total nonfarm payroll level: `CES0000000001`
- unemployment rate: `LNS14000000`
- average hourly earnings level: `CES0500000003`

Latest period for all three: `2026-M08`.

Derived values from the official source:

- NFP monthly change: `162.0` thousand
- unemployment rate: `4.1%`
- AHE MoM: `0.3%` after the frozen one-decimal convention

Therefore the official actual-value source path is technically accessible for future release-time polling.

However:

`MACRO_EVENT_LIVE_DATA_READY = FALSE`

because no approved prospective pre-release consensus provider has yet been proven. Historical/research Investing.com consensus rows are not automatically promoted to live production authority.

## 7. GVZ intraday — NOT PROVEN

Twelve Data WebSocket probe for symbol `GVZ` did not produce a valid price event.

Observed provider response:

- `subscribe-status`
- `status = error`
- `fails = [{"symbol":"GVZ"}]`
- classification: `NOT_PROVEN`

Cboe's public delayed-quote website is not used as an automated fallback because Cboe explicitly prohibits automated extraction from that delayed-quote site. No silent substitute is permitted.

Therefore:

`GVZ_INTRADAY_RISK_READY = FALSE`

and `GVZ_CBOE` remains the governed EOD risk-context source.

## 8. Source-registry migrations

Two source-contract migrations were prepared and successfully tested on temporary Neon branches:

1. `XAU_LIVE_TWELVE_WS_1M`
   - live provisional Emergency input
   - WebSocket entitlement preflight proven
   - EOD authority remains `XAU_EOD_TWELVE_NY17`

2. `XAU_INTRADAY_TWELVE_REST_1M`
   - historical bootstrap only
   - not live authority
   - no prospective claim

Neither migration has been applied to production at the time of this evidence document. Production application requires explicit database-change approval.

## 9. Remaining activation gates

Before V1.45 can be canonical/live:

1. apply the two tested source-registry migrations to production;
2. persist the current-month REST bootstrap as historical catch-up;
3. run a bounded WebSocket live-shadow persistence smoke and verify append-only observation/feature lineage;
4. prove authority stores remain unchanged;
5. update the V1.45 readiness audit from the persisted evidence;
6. keep `GVZ_RISK` EOD-only until a licensed/authorized intraday GVZ source is proven;
7. keep Macro Event V2 live promotion blocked until a legitimate prospective consensus source is proven;
8. provision a persistent/event-driven worker runtime before claiming continuous 24/7 Emergency monitoring;
9. only after those gates update the canonical manifest and merge V1.45.

## 10. Governance locks

Throughout V1.45 preproduction:

- `AUTO_SELECTOR = OFF`
- `AUTO_ENSEMBLE = OFF`
- no BUY/SELL/HOLD/EXIT/REDUCE generation
- no monthly H=1 forecast mutation
- no decision-store writes
- no silent source substitution
- no forward-fill or interpolation of live source gaps
- live provisional alerts remain distinct from EOD-confirmed Emergency state.
