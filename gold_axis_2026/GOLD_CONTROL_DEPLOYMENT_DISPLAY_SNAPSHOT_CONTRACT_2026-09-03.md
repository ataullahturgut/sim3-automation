# Gold Control Deployment Display Snapshot Contract — 2026-09-03

**Contract marker:** `FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V1`

## Purpose

The production Neon database remains the authoritative immutable state/evidence store. This contract defines a display-only repository snapshot so a deployed read-only UI can still render already-persisted governed state when its hosting environment has no usable `NEON_DATABASE_URL`.

This snapshot is a **read replica artifact**, not a model, calculation, forecast, selector, ensemble, decision or position-mapping authority.

## Authority order

1. When a healthy Neon connection is available, the application reads Neon with `SET TRANSACTION READ ONLY` and Neon is the presentation source.
2. When `NEON_DATABASE_URL` is absent or the database is operationally unreachable, the application may read `apps/production_display_snapshot.json`.
3. A snapshot fallback must be explicitly identified as `PRODUCTION_SNAPSHOT_FALLBACK`; it must never be represented as a direct database read.
4. A schema/governance violation is **not** an availability failure and must fail closed rather than silently falling back.

## Allowed snapshot content

Only the following production display state may be exported:

- the latest 12 governed engine runtime rows;
- the seven persisted context features: `MONTHLY_DIRECTION_3M`, `FAST_STATE`, `SLOW_STATE`, `GVZ_VALUE`, `GVZ_CAP`, `GVZ_PANIC`, `GVZ_REGIME`;
- Data Evidence Spine integrity/count health fields;
- source timestamps, governed version identifiers, evidence classes, git lineage and target context required to explain the display state;
- a deterministic SHA-256 payload fingerprint.

The snapshot must not contain database credentials, connection strings, raw observation history, hidden selector weights, fabricated expert forecasts, canonical forecast values, final classifications, `action_state`, BUY/SELL/HOLD/EXIT/REDUCE mappings, or other non-display-authorized state.

## Export rules

- Export is performed from the production Neon branch by trusted automation using a read-only transaction.
- The exporter validates exactly 12 runtime engines and exactly seven required current context features before writing the artifact.
- Integrity counters `orphan_input_snapshots`, `expert_rows_without_input_set`, and `expert_input_fingerprint_mismatches` must all be zero.
- The artifact is deterministic for unchanged source state; no raw secret or raw market payload is logged.
- The application validates the payload fingerprint and required cardinalities before use.

## UI semantics

A connection/configuration error must never be rendered as `Henüz kayıt yok`, `YAYIMLANMADI` or `NO_CURRENT_EVIDENCE` when a valid production snapshot exists.

When snapshot fallback is active, persisted context remains context-only:

- Monthly Direction, FAST and SLOW retain their governed stored values and direction-vote permissions.
- GVZ remains risk-only and never becomes a gold-direction vote.
- WAITING and BLOCKED engine states retain their production runtime status.
- `classification=None`, `action_state=None`, `canonical_authority=False` remain mandatory unless a separately governed future contract proves otherwise.

## Fail-closed rules

The fallback is rejected if its fingerprint is invalid, required engines/features are missing or duplicated, integrity health is non-zero, forbidden final-decision/action fields appear, or the contract marker does not match.

If both Neon and the validated snapshot are unavailable, the UI must present an explicit production-evidence-unavailable/blocking state. It must not claim that production has no records.

## Locks retained

- `NOT_PROVEN_EXPERT_SELECTION_RULE`
- `AUTO_SELECTOR=OFF`
- `AUTO_ENSEMBLE=OFF`
- `NOT_PROVEN_POSITION_MAPPING`

This contract does not relax or supersede any forecast-origin, PIT, evidence, Decision Store, selector, ensemble, or position-mapping rule.