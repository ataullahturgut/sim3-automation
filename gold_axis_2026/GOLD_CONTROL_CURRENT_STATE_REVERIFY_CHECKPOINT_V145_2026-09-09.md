# Gold Control V1.45 — Current State Reverify Checkpoint

**Status:** `PASS_WITH_NON_GOVERNED_RESEARCH_REGISTRY_OBSERVATION`  
**Canonical branch:** `gold-r4-direction-engine`  
**Previous HEAD:** `fb8542a526edcd069b8180b9e703ad2f57699da5`  
**Production writes:** `NONE`

## Binding state

- Manifest is `v1.45`; SHA-256 is `c9815fbfa54470264cdf17a229dcedf4d6bbcc5b848eb05b8413229d545f688c`.
- Historical readiness contract SHA-256 is `8e3e0348366da3a8938b56d57d82ada41efc6c7b4ce497cef1f4c63c5da59dcb` and its status remains `FROZEN_BEFORE_HISTORICAL_GAP_COMPLETION_AND_BEFORE_GOLD_PILOT_V1_SCORING`.
- Production exposes exactly 12 governed runtime engines; all 12 are `ACTIVE` and every engine version matches the V1.45 Component Verification inventory.
- `AUTO_SELECTOR=OFF` and `AUTO_ENSEMBLE=OFF` for all 12 current runtime rows.
- All four forecast/decision authority tables contain zero rows.

## Drift review

The source registry contains 81 rows. Research-only Macro Event V3 rows are present with `production_authority=false`, but `MACRO_EVENT_SUCCESSOR_V2` remains the governed runtime identity. This is not treated as a change to the frozen 12-engine pilot.

No NY17/GVZ historical gap-completion writes were found after the earlier pre-write checkpoint. The new governed observations are current-date collection for 2026-09-08, not backdated pilot reconstruction.

## Provisional Component Verification

Workflow run `34343484809` and artifact hash `f860d1c569fdb912cae4f8f20c4edf821dbc660027135d5a203abf358be892c9` confirm:

- `PASS = 1`
- `NOT_PROVEN = 5`
- `BLOCKED = 6`
- `FAIL = 0`

The result remains provisional until NY17 exact adjudication and the reconstruction bundle are complete.

## Test result

- current-surface audit: `PASS`
- V1.45 historical readiness tests: `7/7 PASS`
- Component Verification R1/R2 regression tests: `PASS`
- historical reconstruction bundle tests: `PASS`

Machine-readable evidence: `data_pipeline/audits/current_state_reverify_v145_2026-09-09.json`.
