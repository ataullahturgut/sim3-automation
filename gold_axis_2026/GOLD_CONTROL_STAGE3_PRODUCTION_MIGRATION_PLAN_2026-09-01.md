# GOLD CONTROL — STAGE 3 PRODUCTION MIGRATION PLAN

**Date:** 2026-09-01  
**Canonical branch:** `gold-r4-direction-engine`  
**Target:** Neon `production` / `neondb`  
**Current state:** isolated rehearsal passed; production not yet changed

## Proven rehearsal evidence

- isolated branch: `gc-stage3-rehearsal-20260901`
- branch id: `br-long-mountain-b2cgwu86`
- parent: `production`
- exact canonical migration executed manually: `data_pipeline/schema_patch_decision_store_v1.sql`
- UI confirmed persisted objects:
  - `decision_runs`
  - `decision_signal_snapshots`
  - `decision_events`
  - `latest_decision_snapshot_by_evidence`
- `stage3_rehearsal_verify.sql` was then executed by the operator and reported successful.

That rehearsal script checks persistent schema presence, synthetic `HISTORICAL_REPLAY` insertability, append-only mutation rejection, unproven action-state rejection, and evidence-scoped latest-state visibility.

## Production migration content

Production must receive the exact same versioned file:

`gold_axis_2026/data_pipeline/schema_patch_decision_store_v1.sql`

No hand-edited SQL variant is authorized.

The migration is additive: it adds the Decision Store tables, indexes, append-only guard function/triggers, evidence-scoped latest-state view, and schema/action-mapping metadata. It does not alter existing observation/forecast tables.

## Safety controls that must remain active

- `action_state` remains unproven and constrained to NULL.
- `HISTORICAL_REPLAY`, `PROSPECTIVE_SHADOW`, and `LIVE_PRODUCTION` remain separate evidence classes.
- no generic cross-evidence latest-decision view is authorized.
- no historical replay may be relabeled as prospective/live.
- app switching and production writer activation are separate later steps; migration alone must not make the app consume the new store.

## Post-migration verification

Immediately after migration, before enabling any production writer:

1. confirm the three Decision Store tables and evidence-scoped view exist;
2. confirm `decision_store_schema_version = GOLD_CONTROL_DECISION_STORE_V1_2026-09-01`;
3. confirm `decision_action_mapping_status = NOT_PROVEN_POSITION_MAPPING`;
4. keep production Decision Store tables empty until the audited writer is explicitly connected;
5. do not run `stage3_rehearsal_verify.sql` on production because it intentionally writes synthetic replay rows.

## Rollback

Emergency rollback file:

`gold_axis_2026/data_pipeline/schema_rollback_decision_store_v1.sql`

Use only before production writer activation, or after preserving any Decision Store rows that must not be lost.

## Approval gate

Production migration is consequential and requires explicit operator approval after reviewing this plan.

Until approval and successful post-migration verification:

`STAGE_3 = ISOLATED_REHEARSAL_PASS / PRODUCTION_MIGRATION_PENDING`
