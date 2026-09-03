# GOLD CONTROL — DATA EVIDENCE SPINE V1 CONTRACT

**Freeze date:** 2026-09-03  
**Status:** `FROZEN_DATA_EVIDENCE_SPINE_V1`  
**Scope:** Gold Control production data plane, multi-expert forecast ledger, runtime engine observability, and read-only application consumption.

## 1. Purpose

Gold Control must not have separate, loosely connected islands for market observations, model inputs, expert outputs, engine status and final decision state. The production database is the immutable evidence spine that connects those layers without allowing the database to invent model authority.

This contract does **not** authorize an expert selector, ensemble, position mapping or final action. Existing locks remain binding:

- `NOT_PROVEN_EXPERT_SELECTION_RULE`
- `AUTO_SELECTOR=OFF`
- `AUTO_ENSEMBLE=OFF`
- `NOT_PROVEN_POSITION_MAPPING`

## 2. Authority basis

Gold Control adopts the following engineering principles as internal governance analogies, without claiming that banking regulation applies to this project:

1. Federal Reserve/OCC/FDIC SR 26-2 (2026) — maintain comprehensive model inventory, data/model documentation, validation, limitations and ongoing monitoring; shared data and methodology dependencies must be visible.
2. NIST AI RMF Govern 1.6 — maintain an organized inventory of system/model artifacts to support maintenance, governance and incident response.
3. NIST AI 800-4 (2026) — monitor deployed functionality and operational health rather than assuming pre-deployment tests prove continued operation.
4. Point-in-time feature-store practice — historical model inputs must reproduce what was knowable at the relevant timestamp, not what is known today.
5. PostgreSQL referential-integrity practice — cross-table identity must use primary/foreign keys and, where necessary, fail-closed triggers instead of application-only assumptions.

## 3. Canonical evidence chain

```text
retrieval_runs / source_vintages
        ↓
observations
        ↓
observations_as_of(as_of)   ← mandatory PIT surface for historical/forward reconstruction
        ↓
forecast_input_sets
        ↓
forecast_input_snapshots + forecast_input_set_members
        ↓
monthly_expert_forecasts
        ↓
derived_feature_snapshots / governed context outputs
        ↓
engine_execution_runs + normalized output links
        ↓
future governed selector / canonical forecast contract
        ↓
decision_runs / decision_signal_snapshots / decision_events
        ↓
read-only application
```

No layer may silently skip an upstream evidence object when a governed downstream claim requires it.

## 4. Input-set rule

A forecast is bound to **one sealed input set**, identified by `input_set_id`.

Each set records:

- target month;
- forecast origin;
- actual `as_of` timestamp;
- forecast track (`MONTH_END_EXPERT` or `EARLY_INDICATIVE`);
- expert/model/version identity;
- evidence class;
- Git commit;
- immutable input fingerprint.

Every `forecast_input_snapshot` belongs to exactly one set. Membership is normalized through `forecast_input_set_members` and enforced by foreign keys. The legacy `input_snapshot_ids[]` array on `monthly_expert_forecasts` remains for backward audit readability, but it is no longer sufficient authority by itself.

The database must reject an expert row when its:

- target/track/origin/as-of/model identity differs from its input set;
- input fingerprint differs from its input set;
- snapshot ID array differs from normalized membership;
- input set is empty.

## 5. Point-in-time and revision safety

`canonical_latest` and `usable_observations` are current-state convenience surfaces only. Historical or forward-origin model construction must use either:

- `observations_as_of(as_of)`; or
- an immutable previously sealed `forecast_input_set` and its snapshots.

For every persisted input snapshot:

- `available_as_of <= input_set.as_of`;
- `retrieved_at <= input_set.as_of`;
- source/model/target identity must match its set;
- provider/source substitution requires a new versioned contract and may not reuse an old model identity silently.

## 6. Runtime engine ledger

All 12 governed motors have a common append-only runtime ledger: `engine_execution_runs`.

The ledger records status even when no numerical/directional output exists. Valid runtime states are:

- `ACTIVE`
- `ISSUED`
- `WAITING`
- `BLOCKED`
- `NOT_PROVEN`

The exact `status_code`, engine/model version, `as_of`, target context, evidence class and Git commit must be recorded. Outputs are linked through normalized bridge tables:

- `engine_execution_derived_outputs`
- `engine_execution_expert_outputs`
- `engine_execution_decision_outputs`

A status-only run is legitimate and must not fabricate an output row.

## 7. Application boundary

The application is a **read/presentation layer**.

- It must open the production state through a read-only transaction.
- It may read current Decision Store state, expert ledger state, derived component context and runtime status.
- It may not recompute a missing production signal merely to populate the UI.
- It may not turn `HISTORICAL_REPLAY`, `LATE_BOOTSTRAP_SHADOW_CONTEXT`, `WAITING`, `BLOCKED` or `NOT_PROVEN` into a live/canonical claim.

A dedicated least-privilege database reader role is desirable defense-in-depth but is not yet proven/provisioned by this contract. Until then, `SET TRANSACTION READ ONLY` remains mandatory for the UI connection path.

## 8. Decision Store boundary

The current Decision Store V1 schema is retained. It remains empty until its own mapping gates are satisfied.

Because the final expert selector/aggregation rule is still `NOT_PROVEN_EXPERT_SELECTION_RULE`, this contract does **not** retrofit or populate Decision Store rows. A future Decision Store V2 change-control must bind the final decision run to normalized forecast/input evidence with database-enforced references before the first canonical decision write.

Status: `BLOCKED_DECISION_STORE_V2_SELECTION_CONTRACT`.

## 9. Migration safety

Production schema change must use a temporary Neon migration branch first. Acceptance requires:

1. migration applies cleanly on a production clone;
2. existing rows remain unchanged;
3. all new FK/PK/unique/check/immutability guards exist;
4. current 7 component-context rows remain immutable and unchanged;
5. forecast/expert/decision tables remain empty before first legitimate issuance;
6. synthetic transactional tests prove valid writes succeed and invalid/orphan/mismatched writes fail;
7. no production migration is applied until explicit user approval after temporary-branch evidence is shown.

## 10. No-hindsight rule

No migration, status sync, backfill or evidence-linking task may create a forecast or decision at a timestamp after the relevant outcome became known and label it prospective/live.

Historical context already persisted with its true timestamp may be linked to a later governance-audit runtime record, but the original evidence class and original timestamps must remain unchanged.
