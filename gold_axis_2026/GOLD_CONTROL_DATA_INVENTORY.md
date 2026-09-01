# GOLD CONTROL — DATA INVENTORY / HEALTH AUDIT

**Inventory version:** 2.0  
**Generated at (UTC):** `2026-09-01T08:34:15.566079+00:00`  
**Evidence:** direct read-only Neon query executed by protected GitHub Actions; transaction rolled back  
**Stage 1 status:** `PASS_AUDIT_COMPLETE`  

---

## 1. Audit contract

This file is generated from the actual Neon data plane plus the database `source_registry`. It contains metadata only; observation values, provider payloads, secrets and quality-event messages are excluded.

Historical reconstruction remains governed by `observations_as_of(origin_ts)` / immutable snapshots. Current-state views never prove what was knowable at an old forecast origin.

## 2. Current database inventory

| Series | Semantic | Tier | Contract source | Actual latest source | Role | Display | Model/status | First obs | Last obs | First retrieval | Last retrieval | Rows | Pipeline health | PIT / blocker |
|---|---|---:|---|---|---|---|---|---|---|---|---|---:|---|---|

## 3. Operational findings

- Persisted/current series in `usable_observations`: **0**.
- Registered series with no current usable rows: **0**.
- Degraded/stale mapped series: **0**.
- Explicit unresolved lineage/blocker notes: **0**.
- A provider failure is not repaired by silent substitution. A failed latest run remains visible as degraded health while unrelated provider jobs may continue independently.

### Latest source-job states

| Job | Status | Started | Finished | Read | Written |
|---|---|---|---|---:|---:|

## 4. Forecast-state database audit

This section is metadata-only and is included because Stage 2 depends on proving whether immutable forecast-state objects actually contain issued records.

| Object | Exists | Row count | Columns / temporal evidence |
|---|---|---:|---|

## 5. Quality and point-in-time status

- Quality ERROR events recorded in the append-only ledger: **37**.
- Quality WARNING events: **0**.
- Historical backfills retain the first-retrieval floor unless historical publication/vintage timing is independently reconstructed.
- `canonical_latest` and `usable_observations` are current-state surfaces only.
- Licensed/vendor raw display restrictions remain binding even when the series is healthy in Neon.

## 6. Stage 1 closure

**Decision:** `PASS_AUDIT_COMPLETE`

Stage 1 is considered audit-complete because the required current inventory fields are now produced from an actual read-only Neon query. Operational source failures or lineage discrepancies remain explicit blockers; they do not invalidate the inventory itself and are not hidden by proxy substitution.

The next roadmap work is Stage 2 reconciliation of the forecast-state store, followed only then by Stage 3 decision-state persistence.
