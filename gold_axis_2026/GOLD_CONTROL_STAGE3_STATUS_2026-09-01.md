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
- `gold_axis_2026/data_pipeline/test_decision_store_schema.py`
- `gold_axis_2026/data_pipeline/test_decision_store_writer.py`
- `gold_axis_2026/data_pipeline/test_decision_store_reader.py`
- `.github/workflows/gold-control-decision-store-schema-smoke.yml`

The protected GitHub Actions rollback-only test against the actual Neon production connection completed successfully on commit:

`3c01c6d5381097278d245a2f74736ef2c8f11172`

Workflow run:

`33492175141`

Job:

`99805954267`

Verified results:

- candidate DDL transactional compatibility: `PASS`
- database action mapping guard (`action_state IS NULL`): `PASS`
- append-only mutation rejection: `PASS`
- fingerprint uniqueness / idempotency: `PASS`
- Python persistence writer: `PASS`
- exact-repeat idempotent write behavior: `PASS`
- previous-classification lineage: `PASS`
- prospective provenance guard: `PASS`
- explicit evidence-class reader isolation: `PASS`
- historical replay not surfaced as live state: `PASS`
- rollback left no decision-store schema or synthetic decision rows behind: `PASS`

Exact CI markers:

```text
DECISION_STORE_SCHEMA_SMOKE_PASS transactional_ddl=PASS action_mapping_guard=PASS append_only=PASS idempotency_fingerprint=PASS rollback=PASS
DECISION_STORE_WRITER_SMOKE_PASS persistence=PASS idempotency=PASS previous_state_lineage=PASS action_mapping_guard=PASS prospective_provenance_guard=PASS append_only=PASS rollback=PASS
DECISION_STORE_READER_SMOKE_PASS evidence_isolation=PASS replay_not_live=PASS action_mapping_guard=PASS rollback=PASS
```

## 2. Important safety property

The reader requires an explicit evidence class. It does not use an implicit "latest of everything" query.

This prevents:

`HISTORICAL_REPLAY -> CURRENT/LIVE DECISION`

from happening silently.

The current V1 store also continues to enforce:

`NOT_PROVEN_POSITION_MAPPING`

Therefore descriptive states such as `ALIGNED_UP`, `CONFLICT`, or `REVERSAL_RISK_DOWN` are not converted into `BUY`, `SELL`, `HOLD_LONG`, `EXIT`, `REDUCE`, or an exposure percentage.

## 3. What has NOT happened

No production decision-store migration has been applied.

No synthetic smoke-test decision remains in Neon.

No historical replay has been relabeled as prospective/live.

No app screen has been switched to the decision store yet.

## 4. Remaining Stage 3 blocker

The required isolated Neon branch rehearsal is still blocked by the Neon management connector contract mismatch.

On 2026-09-01 the exposed tool schema required camelCase arguments (`projectId`, `branchName`) while the underlying MCP implementation rejected those and requested snake_case (`project_id`). A retry with snake_case was rejected by the exposed wrapper itself.

Status:

`BLOCKED_CONNECTOR_SCHEMA_MISMATCH`

This is now independently reconfirmed. Do not claim an isolated branch exists.

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
