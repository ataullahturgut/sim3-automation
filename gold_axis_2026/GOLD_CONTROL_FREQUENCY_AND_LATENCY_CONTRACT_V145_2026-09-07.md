# GOLD CONTROL — FREQUENCY AND LATENCY CONTRACT V1.45

**Issue date:** 2026-09-07  
**Scope:** current Gold Control governed engines and live/event/risk data-plane semantics  
**Status:** CHANGE-CONTROL / PRE-PRODUCTION AUTHORITY CONTRACT

## 1. Principle

Gold Control must not make every engine "real time" by default. Data frequency is part of the model/engine contract and must match the engine objective. Changing an engine from monthly/daily/weekly to intraday without explicit change-control would change its semantics and invalidate comparability with its frozen replay.

Accordingly, V1.45 separates:

- origin-frozen monthly forecast layers;
- completed-session tactical layers;
- completed-week tactical layers;
- release-time event layers;
- intraday emergency/alert layers;
- intraday risk layers;
- display-only live market data.

No layer may consume a faster source merely because that source is available.

## 2. Binding frequency matrix

| Engine / layer | Binding frequency | Live/intraday required? | V1.45 rule |
|---|---|---:|---|
| `VW_MIDAS_MSVR_SUCCESSOR_V1` | monthly H=1 origin | NO | target-month live observations forbidden after origin |
| `CAUSAL_PATCH` | monthly H=1 origin | NO | target-month live observations forbidden after origin |
| `MOMENTUM_3M` | monthly H=1 origin | NO | frozen at month origin |
| `RANDOM_WALK` | monthly H=1 origin | NO | frozen at month origin |
| `MONTHLY_DIRECTION_3M` | month-open strategic context | NO | frozen for target month |
| `FAST` | completed trade-date daily | NO for current identity | keep frozen daily SMA20/2-day rule; do not silently convert to intraday |
| `SLOW` | completed week | NO | keep frozen weekly SMA4/2-week rule |
| `EMERGENCY_LEVEL` | intraday alert + EOD confirmation | YES | real-time/near-real-time XAU required for live alert; NY17 remains confirmation/audit boundary |
| `EMERGENCY_REVERSAL` | intraday alert + EOD confirmation | YES | same as Emergency Level; peak/trough memory must be event-time deterministic |
| `MACRO_EVENT_SUCCESSOR_V2` | scheduled release-time | YES, event-time | update only after official release availability; do not wait for unrelated daily batch |
| `GVZ_RISK` | risk context | YES if used intraday | current daily-close source supports EOD risk only; intraday risk requires approved streaming GVZ source |
| `BOCPD_RETURN_SUCCESSOR_V1` | completed-month regime/break | NO | current identity remains monthly; no intraday reinterpretation |
| live market display | live/indicative | YES for display only | may refresh independently but has no model authority |

## 3. Emergency live-data authority

The current V1.44 daily Emergency recomputation is retained as the deterministic EOD confirmation layer. It is not sufficient by itself for an "immediate emergency" claim.

Preferred live authority candidate:

`XAU_LIVE_TWELVE_WS`

Required contract before activation:

- provider: Twelve Data;
- symbol: `XAU/USD`;
- server-push WebSocket or equivalently governed near-real-time stream;
- event timestamp and receive timestamp both persisted;
- positive finite price validation;
- no interpolation;
- no forward-fill;
- no silent fallback;
- append-only raw-event storage;
- stale-feed detection;
- reconnect/resubscribe audit trail;
- exact source identity and entitlement recorded.

Twelve Data documents real-time WebSocket price delivery for XAU/USD/commodities. WebSocket entitlement depends on subscription plan; entitlement must be proven before this source can become model authority.

`XAU_SPOT_XAUS` remains monitoring/cross-check only unless separately promoted by change-control. `XAU_INTRADAY_XAUS` currently has no production observations and therefore cannot be treated as active authority.

## 4. Emergency live state semantics

Emergency live state must be separate from EOD-confirmed state.

Required states:

- `LIVE_ALERT_LEVEL`
- `LIVE_ALERT_REVERSAL`
- `EOD_CONFIRMED_LEVEL`
- `EOD_CONFIRMED_REVERSAL`

The live alert layer may change intraday as new ticks/bars arrive. The EOD layer is recomputed from canonical `XAU_EOD_TWELVE_NY17` and remains the audit/replay anchor.

Any live alert persistence must include source event IDs/timestamps, first-seen/available timestamps, input fingerprint, contract version and Git SHA. A later EOD confirmation may confirm, clear or supersede the live alert, but may not erase the live alert history.

## 5. FAST and SLOW protection

`FAST` is not renamed or silently converted into an intraday engine. The frozen identity is based on completed daily closes and two completed trade dates. An intraday early-warning challenger, if later desired, must be introduced as a distinct shadow identity with its own replay and acceptance gate.

`SLOW` remains completed-week only. Intraday data must not leak into an incomplete-week SLOW state.

## 6. Macro Event V2 event-time authority

`MACRO_EVENT_SUCCESSOR_V2` is a release-time context, not a daily batch context.

For BLS Employment Situation releases, the official BLS calendar supplies the release date/time; current 2026 Employment Situation releases are scheduled at 08:30 ET. The event pipeline must therefore:

1. know the official scheduled release time in advance;
2. remain pre-release before official availability;
3. ingest actual first-print values only after release;
4. persist first-seen/available time;
5. combine only with the pre-release consensus snapshot that was already available;
6. issue/update event context immediately after both governed inputs are available;
7. never back-insert revisions into the earlier event state.

The current historical first-print/consensus store is valid for research/replay, but future event-time operational readiness is not proven merely by having reconstructed historical rows.

## 7. GVZ risk authority

Current `GVZ_CBOE` is an official Cboe historical/daily-close series and supports EOD risk context.

Cboe documents GVZ dissemination every 15 seconds during regular trading hours and provides streaming values through the Cboe Global Indices Feed. Therefore, if `GVZ_RISK` is intended to constrain intraday risk, daily close is too slow.

Required live authority candidate:

`GVZ_CBOE_LIVE`

Activation requires proof of licensed/authorized access, event-time persistence, freshness monitoring, replayable capture and threshold-equivalence tests against the existing frozen GVZ rule. Until then:

`GVZ_INTRADAY_RISK_READY = FALSE`

and current `GVZ_CBOE` output must be described as EOD risk context only.

## 8. BOCPD and monthly layers

`BOCPD_RETURN_SUCCESSOR_V1` is a completed-month regime/break detector. Its current identity must not be fed intraday returns. If an intraday changepoint detector is later desired, it requires a new shadow identity and separate evidence package.

The H=1 monthly experts and `MONTHLY_DIRECTION_3M` remain origin-frozen. Faster data belongs only to intramonth monitoring layers and must never rewrite the month-open forecast snapshot.

## 9. Live display

`XAU_SPOT_GOLDAPI` / `XAU_SPOT_XAUS` may support indicative live display/monitoring according to their source contracts. Display freshness does not imply model-authority freshness. UI must show separate labels for:

- live indicative market price;
- Emergency live alert;
- EOD-confirmed Emergency state;
- FAST daily state;
- SLOW weekly state;
- event-time Macro context;
- EOD or live GVZ risk context.

## 10. Scheduling/runtime architecture

GitHub Actions hourly scheduling is acceptable for hourly monitoring and EOD reconciliation, but it is not a true real-time transport. A real-time Emergency or intraday GVZ implementation requires an event-driven or continuously connected runtime capable of maintaining the live feed and persisting events promptly.

The required dependency graph is:

`live source event`

→ `source validation + freshness gate`

→ `append-only raw event persist`

→ `engine-specific recompute`

→ `append-only context persist`

→ `strict freshness/provenance audit`

→ `snapshot/UI refresh`

EOD confirmation remains:

`NY17 reconciliation`

→ `daily FAST/SLOW/Emergency confirmation recompute`

→ `audit`

→ `snapshot/UI`.

## 11. Current readiness as of 2026-09-07

Based on production inventory:

- `XAU_SPOT_XAUS`: live monitoring rows exist, but source is indicative and not model authority;
- `XAU_INTRADAY_XAUS`: registered, but zero production observations;
- `XAU_LIVE_TWELVE_WS`: not yet registered/proven;
- `GVZ_CBOE`: daily-close authority exists;
- `GVZ_CBOE_LIVE`: not yet provisioned;
- Macro first-print/consensus historical rows exist at release timestamps, but future prospective event-time ingestion is not yet proven.

Therefore:

- `EMERGENCY_LIVE_DATA_READY = FALSE`
- `MACRO_EVENT_LIVE_DATA_READY = NOT_YET_PROVEN`
- `GVZ_INTRADAY_RISK_READY = FALSE`
- `FAST_DAILY_DATA_READY` remains governed by the existing V1.44/V1.43 audits
- `SLOW_WEEKLY_DATA_READY` remains governed by the existing V1.44/V1.43 audits

## 12. Acceptance gate

No live-data engine may be declared operational until all of the following are proven prospectively:

1. source entitlement/access works in the production runtime;
2. source timestamps and receive/available timestamps are persisted correctly;
3. stale-feed detection blocks context promotion;
4. duplicate/reconnect handling is idempotent;
5. no silent fallback/substitution occurs;
6. raw and derived provenance is replayable;
7. engine output frequency matches this contract;
8. EOD confirmation agrees with the frozen replay semantics where applicable;
9. authority/decision stores remain unchanged unless separately authorized;
10. UI distinguishes live provisional context from EOD-confirmed/frozen context.
