# GOLD CONTROL — AUG31 REPLAY EXPANSION V2 CHANGE CONTROL

**Status:** `FROZEN_BEFORE_AUG31_EXPANSION_RESULT`  
**Freeze date:** 2026-09-04  
**Manifest authority:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.31  
**Target context:** `2026-09`  
**Information/state boundary:** `2026-08-31T21:00:00Z`  
**Evidence lane:** `HISTORICAL_REPLAY` / successor context only

## Purpose

Extend the governed 31-Aug-2026 historical replay so September does not leave now-recoverable engines blank. This is not a backdated prospective issuance. It reconstructs the governed state at the frozen 31-Aug information boundary while preserving actual retrieval/calculation timestamps and late-retrieval provenance.

## Causal Patch replay

Identity: `CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE`.
Target September 2026; replay origin 2026-08-31T21:00:00Z. Frozen geometry remains L=252, P=21, D=32. Daily XAU return inputs must be strictly before 2026-08-31. Completed August macro/anchor inputs must preserve source/vintage/retrieval lineage. Any input retrieved after the historical origin remains explicitly marked `retrieved_post_origin=true`.

The result is historical expert reference only: `prospective_claim=false`, `canonical_authority=false`, `current_runtime_authority=false`, `direction_vote_permitted=false`, selector OFF, ensemble OFF, no Decision Store or canonical forecast write.

## Emergency month-open replay

Use frozen R4.1 thresholds: level displacement +/-4%, reversal 4%. The replay-only monthly reference is the Patch September historical replay; the forward Patch-to-Emergency bridge must not be weakened.

At 31-Aug month-open there is no September EOD observation. Therefore the only authorized initial September state is:
- `EMERGENCY_LEVEL = NEUTRAL`
- `EMERGENCY_REVERSAL = OFF`
- reason `MONTH_OPEN_INITIALIZED_NO_SEPTEMBER_EOD_OBSERVATION`

The 31-Aug close must never be treated as a September close.

## BOCPD successor replay context

Archived `BOCPD` remains BLOCKED. Separate identity `BOCPD_RETURN_SUCCESSOR_V1` may be extended through completed August 2026 using the frozen development prior, expected run length 36, Normal-Inverse-Gamma observation model and MAP-reset state rule unchanged. August is an out-of-lock historical context only, not validation or production evidence. Evidence must be explicitly successor historical replay context, direction vote false, no selector/ensemble/action/position authority, and actual source/retrieval lineage retained.

## Out of scope

VW-MIDAS-MSVR, Macro Event, prospective September issuance, canonical forecast, Decision Store action, model selection/ensemble, post-result threshold or feature retuning, destructive Neon mutations.

## Required sequence

1. Freeze this file before new replay outputs are viewed.
2. Implement deterministic replay-only construction on a feature branch.
3. Run dry-run CI with production credentials for read/source access only.
4. Require PIT, determinism, provenance and authority-isolation gates.
5. Freeze evidence with exact SHA/run and observed outputs.
6. Only after PASS allow append-only persistence into historical replay/display lanes.
7. Verify production runtime remains 4 ACTIVE / 5 WAITING / 3 BLOCKED and decision-authority tables remain unchanged.
8. Extend September UI only after persisted replay evidence passes read-only regression.

## Acceptance gates

PASS requires: Patch geometry 252/21/32 unchanged; no Patch daily feature on/after 31-Aug origin; deterministic Patch replay; historical-not-prospective evidence; Emergency month-open exactly NEUTRAL/OFF; archived BOCPD remains BLOCKED; successor V1 frozen rule unchanged; August clearly out-of-lock replay context; no new direction vote; no canonical forecast/Decision Store write; operational runtime unchanged; late-retrieved inputs preserve actual timestamps.

## Failure rule

Any failed availability, provenance, source identity, determinism, model-contract or authority-isolation gate yields FAIL/BLOCKED for that component. Results may not be used to relax this frozen rule after inspection.
