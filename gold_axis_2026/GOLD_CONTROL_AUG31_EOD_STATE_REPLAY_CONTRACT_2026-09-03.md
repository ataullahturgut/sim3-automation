# Gold Control — 31 August 2026 EOD State Historical Replay Contract

**Issue date:** 2026-09-03  
**Status:** `FROZEN_AUG31_EOD_STATE_REPLAY_V1`  
**Target context:** `2026-09`  
**Replay state boundary:** `2026-08-31T21:00:00Z`  
**Evidence class:** `HISTORICAL_REPLAY`

## 1. Purpose

The September 2026 official H=1 prospective origin was missed and must remain `NOT_ISSUED_MISSED_2026_08_31_ORIGIN`. This contract does not backdate or relabel a prospective forecast.

It closes a different presentation/evidence gap: reconstruct the governed **state that the frozen component rules produce at the 31-August EOD boundary** using only source observations whose economic/observation period is at or before that boundary, while preserving the fact that some source rows were retrieved after the origin.

This state replay is displayed alongside, but remains semantically distinct from, the already governed September H=1 expert replay.

## 2. Non-negotiable evidence semantics

Every state replay row must carry:

- `evidence_class=HISTORICAL_REPLAY`;
- `prospective_h1_claim=false`;
- `current_runtime_authority=false`;
- `canonical_authority=false` where applicable;
- `decision_store_write=NONE`;
- `canonical_forecast_write=NONE`;
- true calculation/write timestamp; never a backdated calculation timestamp;
- `state_as_of=2026-08-31T21:00:00Z`;
- source observation/retrieval lineage and explicit `retrieved_post_origin` status.

The existing `latest_engine_runtime_state` production view excludes `HISTORICAL_REPLAY`; replay executions may therefore be persisted without replacing current ACTIVE/WAITING/BLOCKED operational states.

## 3. Authorized replay components

### 3.1 Monthly Direction 3M

Frozen feature version: `R4_1_3M_SIMPLE_RETURN_V1`.

Rule: use the last four completed canonical `XAU_EOD_TWELVE_NY17` month-end closes ending no later than 31-August-2026, compute the three consecutive simple close-to-close monthly returns, and apply the frozen `three_month_direction` rule to their arithmetic mean.

The result is a **strategic direction context**, not an H=1 price forecast.

### 3.2 FAST

Frozen feature version: `R4_1_SMA20_2_MARKET_DAY_PERSISTENCE_V1`.

Source: canonical `XAU_EOD_TWELVE_NY17` observations ending no later than the state boundary.

Rule: daily close versus own SMA20 with two-market-day persistence, using the frozen `gold_r4.tactical.fast_state` implementation.

### 3.3 SLOW

Frozen feature version: `R4_1_COMPLETED_WEEKLY_SMA4_2_WEEK_PERSISTENCE_V1`.

Source: the same canonical XAU EOD lineage.

Rule: completed weekly closes only; weekly close versus SMA4 with two-completed-week persistence, using the frozen `completed_weekly_closes` and `slow_state` implementations. Because 31-August-2026 is a Monday, the week containing 31 August is incomplete and must not enter the SLOW state.

### 3.4 GVZ risk state

Frozen feature version: `R4_1_GVZ_RISK_CAP_CONTEXT_V1`.

Source: official persisted `GVZ_CBOE` observation dated no later than 31-August-2026.

Frozen thresholds/caps:

- `full_cap_max=25.9795` → cap `1.0`;
- `half_cap_max=30.5238` → cap `0.5`;
- above `30.5238` → cap `0.25`, panic true.

GVZ remains **risk-only** and may never cast a gold direction vote.

## 4. Explicitly blocked state-replay components

The following must remain blocked unless their exact missing dependency is independently recovered under change control:

- `CAUSAL_PATCH`: `BLOCKED_REPLAY_INPUT_SET_NOT_REPRODUCIBLE_FOR_2026_08_31` for the September H=1 replay lane;
- `VW_MIDAS_MSVR`: `BLOCKED_NOT_PROVEN_EXECUTABLE`;
- `MACRO_EVENT`: `BLOCKED_NOT_FULLY_RECOVERED` because the full timestamp-safe consensus/vintage construction is not reproducible;
- `EMERGENCY_LEVEL`: `BLOCKED_NO_AUTHORIZED_REPLAY_MONTHLY_REFERENCE`;
- `EMERGENCY_REVERSAL`: `BLOCKED_NO_AUTHORIZED_REPLAY_MONTHLY_REFERENCE`;
- `BOCPD`: `BLOCKED_EXACT_FORWARD_BOCPD_RULE_NOT_RECOVERED`.

Emergency geometry is implemented and R4.2 accepts an explicitly identified generic monthly reference, but there is no governed selector/reference contract authorizing either the Random Walk or Momentum replay forecast to become **the** Emergency monthly reference. No implicit selection is allowed.

Macro Event and BOCPD must not be reconstructed from partial configuration or placeholder/precomputed replay columns.

## 5. Persistence contract

Authorized replay state features must use replay-specific feature identities so current-state readers cannot accidentally select them as the latest live/shadow context:

- `AUG31_REPLAY_MONTHLY_DIRECTION_3M`
- `AUG31_REPLAY_FAST_STATE`
- `AUG31_REPLAY_SLOW_STATE`
- `AUG31_REPLAY_GVZ_VALUE`
- `AUG31_REPLAY_GVZ_CAP`
- `AUG31_REPLAY_GVZ_PANIC`
- `AUG31_REPLAY_GVZ_REGIME`

Each is append-only in `derived_feature_snapshots` and must be linked to an `engine_execution_runs` row with `evidence_class=HISTORICAL_REPLAY` through `engine_execution_derived_outputs`.

The writer must be idempotent: an exact existing replay set is a no-op/pass; a conflicting existing replay row is a hard failure. It must not update/delete prior evidence.

## 6. UI contract

The `Tahmin` replay surface must expose a clearly separate section:

`31 AĞUSTOS 2026 EOD STATE REPLAY`

with badge:

`HISTORICAL REPLAY · PROSPECTIVE DEĞİL`

It must distinguish:

- **H=1 expert replay**: Momentum and Random Walk price-level forecasts for September;
- **EOD state replay**: Monthly Direction, FAST, SLOW and GVZ state at the August boundary;
- **blocked components**: exact blockers listed above.

FAST/SLOW/GVZ are not H=1 price forecasts. Historical state replay may not populate current operational cards, current Decision Store, prospective performance metrics, selector/ensemble inputs, or action mappings.

## 7. Locks retained

- `NOT_PROVEN_EXPERT_SELECTION_RULE`
- `AUTO_SELECTOR=OFF`
- `AUTO_ENSEMBLE=OFF`
- `NOT_PROVEN_POSITION_MAPPING`
- September official H=1 state remains `NOT_ISSUED_MISSED_2026_08_31_ORIGIN`.

No BUY/SELL/HOLD/EXIT/REDUCE or exposure instruction is authorized by this contract.