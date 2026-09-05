# Gold Control — Macro Event Successor V2 Event-Reaction Validation Change Control

Date: 2026-09-05
Engine: `MACRO_EVENT_SUCCESSOR_V2`
Validation: `MACRO_EVENT_SUCCESSOR_V2_EVENT_REACTION_VALIDATION_V1`

## Authorized scope

This change control authorizes one read-only historical event-reaction validation under the already frozen reaction preregistration.

Authorized reads:
- governed Neon Macro Event research source run `6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a`;
- Twelve Data authenticated `XAU/USD` Commodity Aggregate 1-minute history for the exact V2 VAL+LOCK strong-shock release dates and frozen 08:29/08:34/08:44/08:59 ET bars.

Authorized outputs:
- derived percentage reaction returns;
- event states/reference months;
- response payload hashes;
- aggregate validation metrics and PASS/FAIL/BLOCKED status;
- GitHub Actions artifact containing derived evidence only.

## Forbidden actions

- no Neon source-data write;
- no model result persistence to Neon;
- no `engine_execution_runs` write;
- no Forecast Store or Decision Store write;
- no direction vote;
- no selector/ensemble participation;
- no runtime promotion;
- no raw Twelve Data payload committed to the repository;
- no provider fallback;
- no reaction-window, sign, threshold, event-set, or acceptance-gate change after reaction results are inspected.

## Fail-closed behavior

If the authenticated Twelve Data plan cannot retrieve historical 1-minute XAU/USD bars for every frozen shock event, the validation records `BLOCKED_TWELVE_HISTORICAL_INTRADAY_ACCESS` or a more specific source-coverage blocker. No alternate provider may be substituted under this validation identity.

A reproducible scientific FAIL is not an engineering failure: CI may complete successfully while the model validation status is FAIL. Promotion remains prohibited unless the preregistered reaction evidence gates pass.
