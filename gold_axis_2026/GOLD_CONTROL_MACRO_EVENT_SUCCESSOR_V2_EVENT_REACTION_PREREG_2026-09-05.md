# Gold Control — Macro Event Successor V2 Gold Event-Reaction Validation Preregistration

Date: 2026-09-05
Engine identity: `MACRO_EVENT_SUCCESSOR_V2`
Validation identity: `MACRO_EVENT_SUCCESSOR_V2_EVENT_REACTION_VALIDATION_V1`
Status at preregistration: **reaction source/window/acceptance gates frozen before any V2 shock-event gold reaction values are fetched or inspected**.

## 1. Purpose

`MACRO_EVENT_SUCCESSOR_V2` passed its deterministic macro-surprise replay and produced strong shock states in the VAL/LOCK windows. This document freezes the separate gold event-reaction validation required by the V2 score preregistration before any corresponding intraday gold reaction results are inspected.

This is validation of the new successor only. It does not reconstruct or redefine the archived `MACRO_EVENT` identity.

## 2. Authority boundary

This validation is research-only historical replay reconstruction. It has:
- no direction vote;
- no H=1 price forecast;
- no selector/ensemble authority;
- no action or position mapping;
- no Forecast Store or Decision Store write;
- no runtime promotion by itself;
- no production database write.

Raw vendor payloads are not committed to the public repository. Only derived reaction evidence and payload hashes may be uploaded as workflow artifacts.

## 3. Frozen event sample

Use **all and only** V2 strong-shock events in the already frozen VAL+LOCK windows:
- V2 state `GOLD_ADVERSE_MACRO_SHOCK` or `GOLD_SUPPORTIVE_MACRO_SHOCK`;
- VAL = `2021-01..2023-12`;
- LOCK = `2024-01..2026-08`.

The event set must be derived by recomputing the preregistered V2 score from the frozen Neon source run `6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a`. No event may be added, removed, or reclassified after gold reaction values are seen.

The official release date/time comes from the governed first-print macro source row and must be `08:30 America/New_York` on the recorded release date.

## 4. Frozen gold reaction source

Primary source: **Twelve Data `XAU/USD` Commodity Aggregate**, `/time_series`, interval `1min`, timezone `America/New_York`.

Rationale:
- the project already has an authenticated Twelve Data source lane and secret;
- Twelve Data documents commodity intraday history from 2020-01-09 onward, which covers the full VAL+LOCK shock-event period;
- 1-minute bars permit the reaction to be measured tightly around the 08:30 ET Employment Situation release rather than using a full-day close-to-close proxy.

No silent fallback provider is allowed. If the authenticated plan cannot retrieve the required historical 1-minute bars, validation status is `BLOCKED_TWELVE_HISTORICAL_INTRADAY_ACCESS` and the model is not promoted.

Historical vendor bars retrieved now are classified `HISTORICAL_REPLAY_RECONSTRUCTION`; retrieval time is current truth and is not backdated.

## 5. Bar timestamp semantics and frozen primary window

Project source governance treats Twelve Data 1-minute `datetime` as the **bar-open timestamp**.

Employment Situation release: `08:30:00 America/New_York`.

Primary reaction window:
- pre-release price `P0` = **close of the 08:29 bar**, i.e. the final 1-minute bar ending at 08:30;
- post-release price `P15` = **close of the 08:44 bar**, i.e. the bar ending at 08:45;
- primary return: `R15 = 100 * (P15 / P0 - 1)` percent.

This measures the first 15 completed minutes after release while anchoring immediately before the announcement.

Secondary descriptive windows, not promotion gates:
- `R5`: 08:29-bar close to 08:34-bar close (ends 08:35);
- `R30`: 08:29-bar close to 08:59-bar close (ends 09:00).

No window may be changed after inspecting results under this validation identity.

## 6. Expected direction

For each strong-shock event:
- `GOLD_ADVERSE_MACRO_SHOCK` expects `R15 < 0`;
- `GOLD_SUPPORTIVE_MACRO_SHOCK` expects `R15 > 0`.

Define signed reaction:
- adverse event: `signed_R15 = -R15`;
- supportive event: `signed_R15 = +R15`.

A directional hit occurs when `signed_R15 > 0`. Exactly zero is a miss.

## 7. Frozen acceptance gates

Let `n` be the number of VAL+LOCK V2 strong-shock events.

### Source/engineering gates
All must pass:
1. V2 event set is recomputed from the exact frozen macro source run and exact V2 preregistration identity.
2. Every V2 VAL+LOCK strong-shock event has the exact required 08:29 and 08:44 bars. Coverage must be **n/n**; partial-event dropping is forbidden.
3. All required OHLC values are positive finite numbers and bar timestamps are unique.
4. Response payload hashes are recorded; raw vendor payloads are not committed.
5. Re-running the calculation on the same fetched bars is deterministic.
6. Forecast/Decision authority-store counts are unchanged before/after.
7. No model result or runtime state is persisted to Neon by this validation.

### Reaction evidence gates
V2 may advance to promotion change-control only if **both** are true:
1. directional hits are at least **7 of 8** when the frozen event count is 8; generically, one-sided exact Binomial(0.5) sign-test `p <= 0.10`;
2. median `signed_R15` is strictly greater than 0.

The exact sign-test p-value is computed as `sum(C(n,k) / 2^n, k=hits..n)`.

If the frozen event count differs from the already observed V2 replay due to source/replay drift, validation fails closed before reaction values are interpreted.

No threshold search, event deletion, sign flip, or reaction-window search is permitted after results are viewed.

## 8. Interpretation

A PASS means the preregistered V2 macro shock states show out-of-sample directional consistency with immediate gold reaction over the frozen 15-minute window. It does **not** establish a profitable trading strategy, H=1 monthly forecast skill, or automatic BUY/SELL authority.

A FAIL means V2 is not approved for promotion under this identity. Any revised design requires a separately named successor/validation revision and new preregistration before results.

## 9. Methodological basis

Gold/macro event-study literature finds that U.S. macroeconomic surprises are incorporated quickly into gold prices, that 08:30 U.S. releases such as nonfarm payrolls are especially important, and that unexpectedly stronger U.S. economic news tends to be negative for gold. Earlier event studies also report that much price adjustment occurs within minutes and that elevated volatility can persist for roughly 15 minutes or longer. The primary 15-minute reaction window is frozen on that basis rather than selected from the V2 reaction results.
