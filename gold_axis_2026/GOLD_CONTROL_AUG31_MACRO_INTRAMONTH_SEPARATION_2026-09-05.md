# GOLD CONTROL — 31 AUG ORIGIN / MACRO EVENT INTRAMONTH SEPARATION

Date: 2026-09-05

## Binding scope

This change does not alter any model mathematics, threshold, source values, direction vote, selector, ensemble, H=1 forecast, or Decision Store authority. It only freezes the timing boundary between the existing 31-August month-open reconstruction and the later Macro Event update.

## 31-August month-open object

Frozen origin / information boundary:

`2026-08-31T21:00:00Z`

Target context:

`2026-09`

Authoritative reconstruction artifact:

`gold_axis_2026/apps/aug31_replay_expansion_snapshot.json`

The artifact is `HISTORICAL_REPLAY`, not a backdated prospective issuance. Its governed month-open contents are limited to information legitimately available at or before the frozen 31-Aug boundary. The artifact contains Causal Patch, Emergency initialization and BOCPD successor context; it does not contain `MACRO_EVENT_SUCCESSOR_V2`.

## Macro Event timing

The current `MACRO_EVENT_SUCCESSOR_V2` reference uses the August 2026 Employment Situation released on 2026-09-04. Its runtime metadata carries:

- `information_cutoff = 2026-09-04T12:30:00Z`
- `current_state_as_of = 2026-09-04T12:30:00Z`
- state = `MACRO_MIXED_OR_SMALL`

Therefore this Macro Event state is an **intramonth September event update**, not a member of the 31-August month-open origin snapshot.

Frozen machine semantics:

- `timing_scope = INTRAMONTH_EVENT_UPDATE`
- `month_open_snapshot_member = false`
- `month_open_origin_cutoff = 2026-08-31T21:00:00Z`
- `event_information_cutoff = 2026-09-04T12:30:00Z`
- `direction_vote_permitted = false`
- `no_h1_price_forecast = true`
- `no_automatic_action = true`

A September intramonth update may coexist with a September target context, but it must never be represented as evidence available at the 31-August origin.

## Authority stores

This timing correction authorizes no Forecast Store or Decision Store write. Existing `AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`, `NOT_PROVEN_EXPERT_SELECTION_RULE` and `NOT_PROVEN_POSITION_MAPPING` locks remain unchanged.

## Result

`PASS_AUG31_MONTH_OPEN_AND_MACRO_INTRAMONTH_SEPARATION_FROZEN`
