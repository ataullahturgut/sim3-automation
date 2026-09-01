-- GOLD CONTROL DECISION STORE V1 — EMERGENCY ROLLBACK
-- Use only if the V1 production migration must be reverted before the
-- production decision writer is activated, or after any required decision
-- rows have been exported/preserved.
--
-- This script removes only objects introduced by
-- schema_patch_decision_store_v1.sql plus its two metadata keys.

DROP VIEW IF EXISTS latest_decision_snapshot_by_evidence;
DROP VIEW IF EXISTS latest_decision_snapshot;

DROP TRIGGER IF EXISTS decision_events_append_only ON decision_events;
DROP TRIGGER IF EXISTS decision_snapshots_append_only ON decision_signal_snapshots;
DROP TRIGGER IF EXISTS decision_runs_append_only ON decision_runs;

DROP TABLE IF EXISTS decision_events;
DROP TABLE IF EXISTS decision_signal_snapshots;
DROP TABLE IF EXISTS decision_runs;

DROP FUNCTION IF EXISTS reject_gold_control_decision_mutation();

DELETE FROM system_metadata
WHERE key IN (
    'decision_store_schema_version',
    'decision_action_mapping_status'
);
