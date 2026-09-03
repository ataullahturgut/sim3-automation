# GOLD CONTROL — R4.2 EMERGENCY PERSISTENCE RECONCILIATION

**Date:** 2026-09-03  
**Status:** `AUDITED_ACTIVE_BLOCKER_NOT_STALE`  
**Parent manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.22  
**Bridge authority:** `GOLD_CONTROL_R4_2_MONTHLY_REFERENCE_EMERGENCY_BRIDGE_CONTRACT_2026-09-02.md`

## 1. Question reconciled

The canonical manifest states that the R4.2 generic monthly-price-reference → Emergency bridge is validated, while the application reader still exposes:

`BLOCKED_NO_PERSISTED_MONTHLY_PRICE_REFERENCE`

These statements are not contradictory. They refer to two different dependency gates.

## 2. Source-of-truth application

Per manifest v1.22:

- GitHub is authoritative for code, frozen contracts, validation logic, version history and audit documents.
- Neon Postgres is authoritative for mutable/dynamic production state, including immutable forecast input snapshots, derived feature snapshots, forecast contracts and future decision snapshots/events.

Therefore bridge validation cannot prove that a persisted forward monthly reference exists. Production persistence must be verified from Neon.

## 3. Frozen bridge authority

The R4.2 bridge contract validates provenance-safe use of a generic `MonthlyPriceReference` without relabelling a Patch forecast as historical `monthly_vw_forecast`.

The bridge contract explicitly requires:

- unchanged frozen R4.1 Emergency geometry;
- explicit model identity;
- fail-closed behavior when persisted IDs are required but missing;
- no Neon, forecast-ledger or Decision Store write during bridge validation.

Accordingly:

`R4_2_MONTHLY_REFERENCE_EMERGENCY_BRIDGE_PASS`

means the structural/provenance bridge is validated. It does **not** mean a live/prospective monthly reference has been persisted.

## 4. Production Neon audit — 2026-09-03

Read-only production audit found:

- `forecast_input_snapshots` = `0` rows;
- `monthly_forecast_contracts` = `0` rows;
- `monthly_expert_forecasts` = `0` rows;
- `decision_signal_snapshots` = `0` rows.

A second read-only audit of `derived_feature_snapshots` found only the existing `MONTHLY_DIRECTION_3M` monthly-related component context and no persisted monthly price reference or Emergency feature.

Therefore no operational R4.2 `MonthlyPriceReference` can currently satisfy `require_persisted_reference=true`.

## 5. Canonical reconciliation

Current status is frozen as:

- bridge validation: `R4_2_MONTHLY_REFERENCE_EMERGENCY_BRIDGE_PASS`;
- persisted monthly reference: `BLOCKED_NO_PERSISTED_MONTHLY_PRICE_REFERENCE`;
- Emergency Level/Reversal forward context: `BLOCKED` until a valid persisted reference exists;
- blocker stale: `FALSE`;
- no Emergency value may be fabricated from historical replay, a mockup, live spot alone, or an unpersisted forecast candidate.

The existing application blocker must therefore remain active. Removing it now would violate manifest v1.22 source-of-truth and fail-closed rules.

## 6. Exit condition for the persistence blocker

The blocker may be reconsidered only after a real eligible origin produces governed forward state with the required persisted provenance. At minimum, the audit must prove a mutually consistent forward chain containing:

1. immutable forecast input snapshot state;
2. immutable monthly forecast contract state;
3. the corresponding governed monthly forecast/reference identity;
4. target month and forecast origin consistency;
5. the active model identity without relabelling it as `monthly_vw_forecast`;
6. prospective evidence class appropriate to the first forward issuance;
7. IDs/provenance sufficient for `MonthlyPriceReference.validate(require_persisted_ids=True)`;
8. subsequent Emergency calculation under the unchanged frozen R4.1 thresholds.

Persistence alone does not authorize a final Decision Store classification or position/action mapping.

## 7. Temporal constraint

September 2026 remains non-backfillable because the canonical 31-August origin was missed. No September reconstruction may be relabelled prospective.

The first possible contract-compliant target remains October 2026 at the end-September origin, subject to every Stage-4B availability, issuance and persistence gate closing prospectively.

## 8. Non-changes

This reconciliation makes no change to:

- Emergency thresholds;
- Patch geometry or model ranking;
- source/provider mappings;
- H=1 target definition;
- selector or ensemble policy;
- position/action mapping;
- BOCPD or Macro Event blockers.

It only separates a **validated bridge** from a **not-yet-persisted forward monthly reference**.
