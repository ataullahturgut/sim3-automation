# GOLD CONTROL — STAGE 3 DECISION STORE STATUS

**Status date:** 2026-09-01  
**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.3  
**Stage:** 3 — Decision State Store  
**Current status:** `PASS_DECISION_STORE_AND_READ_PATH`

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

Production Decision Store V1 schema migration **has been applied and verified**.

No production decision writer/reader has been switched on.

No historical replay has been relabeled as prospective/live.

No app screen has been switched to the decision store yet.

No claim is made that connector-side post-migration schema introspection or schema diff has passed; that path remains blocked by the connector contract mismatch.

## 5. Stage 3 closure

Stage 3 is complete.

Closure evidence:

- production schema migration: run `33496843121`, job `99820886297`, `SUCCESS`;
- production schema independently visible in Neon resource tree;
- guarded R4.1 emitted-state bridge: run `33498177345`, job `99825081623`, `R4_1_DECISION_BRIDGE_SMOKE_PASS`;
- bridge verification covered state-shape guard, forbidden action guard, drift guard, frozen engine/config identity, store-reader roundtrip, idempotency and rollback;
- app Decision Store reader integration: canonical commit `50ab446b2b97634a2a812a3b6de655c358f9829b`;
- app smoke: run `33498603322`, job `99826433286`, `GOLD_CONTROL_DECISION_STORE_APP_READER_PASS`;
- app no longer depends on `latest_signal.json` for current decision state;
- reader excludes `HISTORICAL_REPLAY` and refuses non-null action mapping;
- no synthetic decision row survived rollback tests;
- production Decision Store remains empty because prospective issuance prerequisites are not yet satisfied.

Final Stage 3 status:

`PASS_DECISION_STORE_AND_READ_PATH`

The absence of a real prospective row is now a Stage 4/11 issuance prerequisite, not unfinished Decision Store infrastructure.
