# GOLD CONTROL — STAGE 3 DECISION STORE STATUS

**Status date:** 2026-09-01  
**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.1  
**Stage:** 3 — Decision State Store  
**Current status:** `IMPLEMENTATION_VERIFIED_ROLLBACK_ONLY; PRODUCTION_MIGRATION_BLOCKED`

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

Verified results:

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

## 2. Important safety properties

### 2.1 Evidence isolation

The reader requires an explicit evidence class. It does not use an implicit "latest of everything" query.

The database candidate schema was also tightened: the earlier ambiguous cross-evidence `latest_decision_snapshot` candidate view was removed before production migration. The only convenience view is now:

`latest_decision_snapshot_by_evidence`

which returns the latest successful state separately for each evidence class.

This prevents:

`HISTORICAL_REPLAY -> CURRENT/LIVE DECISION`

from happening silently at either the reader or convenience-view layer.

### 2.2 No invented position mapping

The current V1 store continues to enforce:

`NOT_PROVEN_POSITION_MAPPING`

Therefore descriptive states such as `ALIGNED_UP`, `CONFLICT`, or `REVERSAL_RISK_DOWN` are not converted into `BUY`, `SELL`, `HOLD_LONG`, `EXIT`, `REDUCE`, or an exposure percentage.

### 2.3 Engine output is preserved, not reinterpreted by persistence

`r4_1_decision_adapter.py` maps the already-emitted R4.1 state into the store contract and deterministic audit reason vocabulary. It does not recompute Fast, Slow, Emergency, GVZ or classification and does not create an action state.

## 3. What has NOT happened

No production decision-store migration has been applied.

No synthetic smoke-test decision remains in Neon.

No historical replay has been relabeled as prospective/live.

No app screen has been switched to the decision store yet.

No isolated Neon rehearsal branch is claimed to exist.

## 4. Remaining Stage 3 blocker

The required isolated Neon branch rehearsal is still blocked by the Neon management connector contract mismatch.

On 2026-09-01:

1. the exposed branch-management schema required camelCase arguments (`projectId`, `branchName`), while the underlying MCP implementation rejected those and requested snake_case (`project_id`);
2. a snake_case retry was rejected by the exposed wrapper itself;
3. the higher-level database-migration preparation path was also attempted and exhibited the same mismatch: the wrapper accepted camelCase but the underlying MCP required `project_id` / `migration_sql`.

Status:

`BLOCKED_CONNECTOR_SCHEMA_MISMATCH`

This blocker is independently reconfirmed across both branch-creation and migration-preparation paths. Do not bypass it by claiming a temporary branch was created or by applying the candidate schema directly to production.

## 5. Exit path

Stage 3 becomes eligible for `PASS` only after:

1. working isolated Neon branch lifecycle is available;
2. the exact versioned DDL is applied on the isolated branch;
3. schema and persistence tests pass there without rollback-only limitations;
4. migration is applied to production through an auditable migration path;
5. production post-migration schema is verified;
6. production decision writer/reader are connected without weakening the evidence-class or action-mapping guards.

Until then:

`STAGE_3 = IN_PROGRESS / PRODUCTION_MIGRATION_BLOCKED`

Stages 4–12 may be prepared non-mutatively where useful, but none may be promoted as complete ahead of Stage 3.
