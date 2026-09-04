# Gold Control — Dual-State Engine Observability Change Control

**Issue date:** 2026-09-04  
**Status:** `FROZEN_DUAL_STATE_OBSERVABILITY_V1`  
**Scope:** Presentation / observability only  
**Model authority:** unchanged  
**Decision authority:** unchanged

## 1. Problem closed

The governed `latest_engine_runtime_state` view intentionally excludes `HISTORICAL_REPLAY`. As a result, a monthly expert can have a valid current-target historical replay while its operational runtime row correctly remains `WAITING_ELIGIBLE_MONTH_END_ORIGIN`. The previous engine inventory surfaced only the operational state, which made an issued current-month replay appear absent.

For September 2026 this affected `MOMENTUM_3M` and `RANDOM_WALK`: both have governed `HISTORICAL_REPLAY` H=1 outputs for target `2026-09`, while both remain operationally waiting for the next eligible month-end origin.

## 2. Frozen semantic correction

The application must expose two distinct states where both exist:

1. **Current-month reference evidence** — a governed `HISTORICAL_REPLAY` row for the current target month; and
2. **Operational runtime state** — the unchanged row from `latest_engine_runtime_state`.

For the September 2026 expert replay the display semantics are therefore:

- `ISSUED_HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE` for the September reference output;
- `WAITING_ELIGIBLE_MONTH_END_ORIGIN` for the next prospective/runtime opportunity.

`ISSUED` in this display contract never means `ACTIVE_PROSPECTIVE`, `LIVE_PRODUCTION`, or canonical decision authority.

## 3. Fail-closed reference eligibility

A historical expert row may be attached as current-month reference only when all are true:

- `forecast_track = HISTORICAL_REPLAY`;
- target month equals current runtime target context;
- `evidence_class = HISTORICAL_REPLAY`;
- `canonical_authority = false`;
- `auto_selector = OFF`;
- `auto_ensemble = OFF`;
- a persisted forecast value exists.

The reader is read-only and performs no recomputation or persistence.

## 4. Authority locks retained

This change does **not**:

- create a canonical forecast;
- promote a replay to prospective evidence;
- enable a selector or ensemble;
- authorize an expert winner;
- authorize a direction vote for monthly price experts;
- populate Decision Store;
- authorize position mapping or action states.

Locks remain:

- `AUTO_SELECTOR=OFF`;
- `AUTO_ENSEMBLE=OFF`;
- `NOT_PROVEN_EXPERT_SELECTION_RULE`;
- `NOT_PROVEN_POSITION_MAPPING`.

## 5. September 2026 expected display

Current-month expert reference:

- `MOMENTUM_3M`: persisted September replay value, evidence `HISTORICAL_REPLAY`;
- `RANDOM_WALK`: persisted September replay value, evidence `HISTORICAL_REPLAY`.

Their operational next-run state remains `WAITING_ELIGIBLE_MONTH_END_ORIGIN`.

Separately, Monthly Direction, FAST, SLOW and GVZ retain their governed persisted/current-context roles and their Aug-31 historical state replay remains a distinct evidence layer.

## 6. Validation gate

Promotion requires a production read-only regression proving:

- exactly 12 governed engines remain visible;
- the current runtime health contract still passes;
- exactly the governed September Momentum and Random Walk replay rows attach as current-month expert references;
- both retain `canonical_authority=false`, selector OFF, ensemble OFF;
- their operational runtime status remains WAITING;
- no direction-vote permission is created by the replay attachment.
