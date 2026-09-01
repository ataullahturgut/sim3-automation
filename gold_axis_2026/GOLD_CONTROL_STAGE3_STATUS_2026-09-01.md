# GOLD CONTROL — STAGE 3 DECISION STORE STATUS

**Status date:** 2026-09-01  
**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.1  
**Stage:** 3 — Decision State Store  
**Current status:** `ISOLATED_REHEARSAL_SCHEMA_APPLIED; PRODUCTION_MIGRATION_NOT_APPLIED`

## 1. What is now verified

The following Stage 3 artifacts exist on the canonical branch:

- `gold_axis_2026/data_pipeline/schema_patch_decision_store_v1.sql`
- `gold_axis_2026/data_pipeline/decision_store.py`
- `gold_axis_2026/data_pipeline/decision_store_reader.py`
- `gold_axis_2026/data_pipeline/r4_1_decision_adapter.py`
- `gold_axis_2026/data_pipeline/test_decision_store_schema.py`
- `gold_axis_2026/data_pipeline/test_decision_store_writer.py`
- `gold_axis_2026/data_pipeline/test_decision_store_reader.py`
- `gold_axis_2026/data_pipeline/test_r4_1_decision_adapter.py`
- `.github/workflows/gold-control-decision-store-schema-smoke.yml`

Latest protected rollback-only verification against the actual Neon production connection completed successfully on commit:

`cba353cd53ec87ba9b1ca8d1d86b51af3b3d5e98`

Workflow run:

`33493261858`

Job:

`99809509661`

Verified rollback-only results:

- candidate DDL transactional compatibility: `PASS`
- evidence-scoped latest-state database view: `PASS`
- ambiguous cross-evidence `latest_decision_snapshot` view absent: `PASS`
- database action mapping guard (`action_state IS NULL`): `PASS`
- append-only mutation rejection: `PASS`
- fingerprint uniqueness / idempotency: `PASS`
- Python persistence writer: `PASS`
- exact-repeat idempotent write behavior: `PASS`
- previous-classification lineage: `PASS`
- prospective provenance guard: `PASS`
- explicit evidence-class reader isolation: `PASS`
- historical replay not surfaced as live state: `PASS`
- deterministic R4.1 emitted-state → persistence payload mapping: `PASS`
- R4.1 engine/config/code provenance binding in stored row contract: `PASS`
- R4.1 state → store → reader roundtrip: `PASS`
- rollback left no decision-store schema or synthetic decision rows behind: `PASS`

Exact current CI markers:

```text
DECISION_STORE_SCHEMA_SMOKE_PASS transactional_ddl=PASS evidence_scoped_latest_view=PASS action_mapping_guard=PASS append_only=PASS idempotency_fingerprint=PASS rollback=PASS
DECISION_STORE_WRITER_SMOKE_PASS persistence=PASS idempotency=PASS previous_state_lineage=PASS action_mapping_guard=PASS prospective_provenance_guard=PASS append_only=PASS rollback=PASS
DECISION_STORE_READER_SMOKE_PASS evidence_isolation=PASS replay_not_live=PASS action_mapping_guard=PASS rollback=PASS
R4_1_DECISION_ADAPTER_SMOKE_PASS engine_repeatability=PASS state_to_payload=PASS provenance_binding=PASS store_roundtrip=PASS idempotency=PASS action_mapping_guard=PASS rollback=PASS
```

## 2. Isolated Neon rehearsal branch

A real isolated child branch now exists and has been independently identified through the Neon project resource layer:

- branch name: `gc-stage3-rehearsal-20260901`
- branch id: `br-long-mountain-b2cgwu86`
- parent branch: `production`
- parent id: `br-gentle-mouse-b22dzkr1`
- database: `neondb`
- default: `false`
- protected: `false`

The exact canonical file `gold_axis_2026/data_pipeline/schema_patch_decision_store_v1.sql` was manually executed in the Neon SQL Editor while the rehearsal branch was selected.

The Neon UI reported successful execution of the multi-statement script. The initial `DROP ... IF EXISTS` notices for non-existing legacy triggers/view were expected first-install notices, not migration failures.

The user then opened the rehearsal branch Tables view and the following persisted objects were visibly present:

- `decision_runs`
- `decision_signal_snapshots`
- `decision_events`
- the evidence-scoped latest-decision view (`latest_decision_snapshot_by_evidence`, truncated in the UI list)

This closes the earlier statement that no rehearsal branch existed. The rehearsal branch now exists and the candidate schema has been persistently applied there.

Important limitation: the Neon connector's SQL/describe wrappers still exhibit the camelCase/snake_case argument contract mismatch, so full machine-side introspection of the rehearsal branch after manual application remains `BLOCKED_CONNECTOR_SCHEMA_MISMATCH`. Therefore the current proof for persistent rehearsal application is UI-backed plus the prior rollback-only CI contract tests; it is not yet a full connector-side schema diff/row-level verification.

## 3. Important safety properties

### 3.1 Evidence isolation

The reader requires an explicit evidence class. It does not use an implicit "latest of everything" query.

The database candidate schema was also tightened: the earlier ambiguous cross-evidence `latest_decision_snapshot` candidate view was removed before production migration. The only convenience view is now:

`latest_decision_snapshot_by_evidence`

which returns the latest successful state separately for each evidence class.

This prevents:

`HISTORICAL_REPLAY -> CURRENT/LIVE DECISION`

from happening silently at either the reader or convenience-view layer.

### 3.2 No invented position mapping

The current V1 store continues to enforce:

`NOT_PROVEN_POSITION_MAPPING`

Therefore descriptive states such as `ALIGNED_UP`, `CONFLICT`, or `REVERSAL_RISK_DOWN` are not converted into `BUY`, `SELL`, `HOLD_LONG`, `EXIT`, `REDUCE`, or an exposure percentage.

### 3.3 Engine output is preserved, not reinterpreted by persistence

`r4_1_decision_adapter.py` maps the already-emitted R4.1 state into the store contract and deterministic audit reason vocabulary. It does not recompute Fast, Slow, Emergency, GVZ or classification and does not create an action state.

## 4. What has NOT happened

No production decision-store migration has been applied.

No production decision writer/reader has been switched on.

No historical replay has been relabeled as prospective/live.

No app screen has been switched to the decision store yet.

No claim is made that connector-side post-migration schema introspection or schema diff has passed; that path remains blocked by the connector contract mismatch.

## 5. Remaining Stage 3 work

Stage 3 becomes eligible for `PASS` only after:

1. persistent rehearsal branch schema is verified beyond UI object presence, preferably through a working connector or equivalent auditable SQL checks;
2. persistent rehearsal writer/reader roundtrip is exercised without rollback-only limitations;
3. production migration plan is reviewed and explicitly approved;
4. migration is applied to production through an auditable path;
5. production post-migration schema is verified;
6. production decision writer/reader are connected without weakening the evidence-class or action-mapping guards.

Current status:

`STAGE_3 = ISOLATED_REHEARSAL_SCHEMA_APPLIED / PRODUCTION_MIGRATION_NOT_APPLIED`

Stages 4–12 may be prepared non-mutatively where useful, but none may be promoted as complete ahead of Stage 3.
