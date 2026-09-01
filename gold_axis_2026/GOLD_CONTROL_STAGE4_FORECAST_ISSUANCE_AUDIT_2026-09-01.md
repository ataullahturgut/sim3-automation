# GOLD CONTROL — STAGE 4 FORECAST / MONTHLY-CONTEXT ISSUANCE AUDIT

**Audit date:** 2026-09-01  
**Manifest:** target v1.8  
**Decision:** `BLOCKED_WITH_EXPLICIT_CURRENT_ISSUER_AND_MONTHLY_CONTEXT_GAPS`

## Executive conclusion

The canonical daily NY17 source is operational, but Stage 4 is not yet ready for a prospective R4.1 decision because the mandatory monthly model/context inputs and the H=1 current issuer are not all executable/issued under proven contracts.

## Evidence

### Live forecast-state schema

GitHub Actions run `33512445624`, job `99871192709`, `SUCCESS`, used a read-only Neon transaction. All three forecast-state tables exist and contain zero rows.

### Patch current issuer

`core5_monthly` ends at `2026-07-01`. Retained Patch operational code is August-2026 specific and contains July cutoffs. Historical Patch closure executability is not evidence of a September issuer.

Status: `PATCH_R1_CURRENT_ISSUER_NOT_PROVEN`.

### VW current R4.1 reference

R4.1 `EngineSnapshot` requires `monthly_vw_forecast`. Canonical-history forensic run `33513175499`, job `99873596626`, did not recover the exact original VW-MIDAS-SVR Adapt V2 runner/source chain. Existing `run_vw_*` files are reconstruction/research artifacts and the retained VW rebuild code itself treats exact replication as blocked.

Status: `VW_EXECUTABLE_REPRODUCTION_BLOCKED_NOT_PROVEN`; `VW_CURRENT_MONTHLY_REFERENCE_NOT_ISSUED`.

### Monthly direction context

R4.1 also requires `monthly_direction`. The frozen role remains 3M Momentum; no prospective monthly-direction issuance row exists.

Status: `MONTHLY_DIRECTION_CONTEXT_NOT_ISSUED`.

### Canonical NY17 history

The single-day canonical daily pipeline passed. For Fast/Slow and 3M direction, longer same-lineage history is required. Sampled Twelve exact NY17 history is available from May-August (run `33513634775`, job `99875100590`, `SUCCESS`). The first atomic July-August backfill run `33512957983`, job `99872871327`, failed before persistence because seven provider/request errors remained. The code did not authorize a partial write.

Status: `CANONICAL_XAU_HISTORY_BACKFILL_NOT_YET_SUCCESS`.

## Governance decision

- do not backdate an issuance timestamp to 2026-08-31 for data first retrieved on 2026-09-01;
- do not label backfilled NY17 observations as historically knowable before their recorded retrieval time;
- do not extend Patch by changing date constants and call it the frozen production model;
- do not promote VW reconstruction scripts as the exact audited VW identity without output/source-chain identity proof;
- do not use RW/Patch/live spot as a silent replacement for `monthly_vw_forecast`;
- do not create forecast-table rows solely to clear readiness gates.

The first legitimate forward decision remains `PROSPECTIVE_SHADOW` only after all required R4.1 snapshot inputs are issued with immutable provenance.
