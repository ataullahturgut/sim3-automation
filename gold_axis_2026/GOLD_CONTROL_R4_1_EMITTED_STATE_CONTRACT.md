# GOLD CONTROL — R4.1 EMITTED STATE / PERSISTENCE CONTRACT

**Status date:** 2026-09-01
**Contract status:** `FROZEN_FOR_STAGE3_BRIDGE`
**Canonical branch:** `gold-r4-direction-engine`

## 1. Audit conclusion

A canonical continuously scheduled **live/EOD R4.1 state producer was not found** in the current source-of-truth branch.

What exists:

- `gold_axis_2026/r4_1/scripts/replay_daily.py` — deterministic sequential replay/emission path;
- frozen R4.1 engine package under `gold_axis_2026/r4_1/src/gold_r4/`;
- transitional app dependency on `gold_axis_2026/r4_1/output/latest_signal.json`;
- older R4 workflows/scripts under `projects/gold_h1_r1/`.

What does **not** qualify as the canonical R4.1 live emitter:

- the older R4 investment workflow, because it contains LONG/CASH and AL/SAT execution mapping that is not authorized by the R4.1 `NOT_PROVEN_POSITION_MAPPING` contract;
- the Streamlit live-spot adapter, because monitoring spot is not the frozen EOD decision close;
- `replay_daily.py` by itself, because it is a replay CLI and not a scheduled prospective issuer.

Current live-emitter status:

`NOT_FOUND_CANONICAL_LIVE_R4_1_EMITTER`

This is an explicit production blocker, not permission to reuse an older execution engine.

## 2. Frozen emitted-state fields

The Stage 3 persistence bridge may consume only an **already emitted descriptive R4.1 state**. It must not recompute signals.

Required top-level fields:

- `date`
- `close`
- `target_month`
- `vw_forecast_frozen`
- `monthly_direction_3m`
- `level_emergency`
- `reversal_emergency`
- `fast_state`
- `slow_state`
- `classification`

Optional top-level fields:

- `gvz`
- `gvz_cap`
- `gvz_panic`
- `macro_event_down`
- `bocpd_context`
- `default_execution_session`

The contract intentionally rejects unrecognized top-level fields until separately reviewed. This prevents silent state-shape drift.

## 3. Forbidden action/exposure fields

The emitted-state bridge must reject any payload containing fields such as:

- `action`
- `action_state`
- `position`
- `pos`
- `exposure`
- `target_exposure`
- `trade`

Reason:

`NOT_PROVEN_POSITION_MAPPING`

R4.1 descriptive classifications may not be silently converted into BUY/SELL/HOLD/LONG/CASH/REDUCE instructions.

## 4. Persistence provenance

Persistence adds provenance; it does not reinterpret the state.

Required persistence metadata:

- `decision_as_of` — timezone-aware decision timestamp;
- `generated_at` — timezone-aware generation timestamp;
- `evidence_class` — one of `HISTORICAL_REPLAY`, `PROSPECTIVE_SHADOW`, `LIVE_PRODUCTION`;
- `trigger_type`;
- `close_source_ref`;
- `quality_status`;
- exact Git commit SHA where required;
- frozen R4.1 config version and SHA-256 hash derived from `frozen_r4_1.json`;
- engine version derived from `r4_1/pyproject.toml`.

For `PROSPECTIVE_SHADOW` and `LIVE_PRODUCTION`, the existing Decision Store contract additionally requires:

- `code_sha`;
- `input_snapshot_ref`;
- `forecast_contract_ref`.

No missing prospective reference may be replaced with a guessed identifier.

## 5. Current prospective blockers

The canonical forecast ledger is currently proven empty. Therefore there is not yet a valid issued `forecast_contract_ref` available for a real prospective decision row.

Status:

`BLOCKED_PROSPECTIVE_DECISION_WRITE_FORECAST_LEDGER_EMPTY`

Combined with the missing live emitter:

`BLOCKED_PROSPECTIVE_DECISION_ISSUANCE = LIVE_EMITTER_NOT_FOUND + FORECAST_CONTRACT_NOT_ISSUED`

Stage 3 may verify the bridge transactionally without persisting synthetic rows. It must not create fake prospective lineage merely to make the database non-empty.

## 6. Bridge behavior

Canonical Stage 3 bridge:

`gold_axis_2026/data_pipeline/r4_1_decision_bridge.py`

Required behavior:

1. validate exact emitted-state shape;
2. reject action/exposure fields;
3. derive frozen config version/hash and engine version from GitHub-controlled files;
4. bind explicit evidence/provenance metadata;
5. call `r4_1_decision_adapter.py`;
6. persist only through `decision_store.py`;
7. verify through `decision_store_reader.py`;
8. default to no persistent write;
9. require an explicit environment gate for any persistent production write;
10. keep `LIVE_PRODUCTION` disabled until production graduation/change control explicitly authorizes it.

## 7. Evidence policy

Rollback-only synthetic integration tests are test evidence only. They must never survive the transaction and must never be presented as prospective/live decisions.

A future real `PROSPECTIVE_SHADOW` row is valid only if the state was issued before outcome realization and all required input/forecast provenance existed at issuance time.
