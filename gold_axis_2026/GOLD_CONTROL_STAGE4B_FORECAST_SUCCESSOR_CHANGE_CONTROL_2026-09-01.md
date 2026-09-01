# GOLD CONTROL — STAGE 4B FORECAST SUCCESSOR CHANGE CONTROL

**Date:** 2026-09-01  
**Scope:** H=1 monthly forecast / monthly price-reference production identity  
**Decision:** `LEGACY_VW_PATCH_EXECUTABLE_RECOVERY_REJECTED; GOVERNED_SUCCESSOR_REQUIRED`

## 1. Problem statement

R4.1 requires a monthly price forecast/reference, historically named and frozen as `VW-MIDAS-SVR Adapt V2`, while the production-closure package also preserved `Causal PatchTST Gold R1` as a temporary executable point-forecast path.

The project can no longer prove that either archived model identity has a current executable implementation that reproduces the canonical production-closure outputs. Continuing by editing dates, using similarly named legacy files, or inserting another model into the existing `monthly_vw_forecast` field would create false provenance.

## 2. Canonical evidence

### 2.1 VW identity recovery is not proven

Canonical production closure:

- `gold_axis_2026/production_closure/PROVENANCE.json`
- audited analytical reference: `VW-MIDAS-MSVR Adapt V2`
- executable reproduction status: `BLOCKED_NOT_PROVEN`

The two retained VW rebuild paths explicitly declare that they are reconstructions rather than exact identity recovery:

- `gold_axis_2026/run_vw_full_rebuild.py`
- `gold_axis_2026/run_vw_full_rebuild_v2.py`

Known unresolved identity gaps include missing authors' processed data, ambiguous/missing feature identities/definitions, source differences and weighting ambiguity. Therefore neither rebuild may inherit the canonical VW production identity.

### 2.2 Legacy output files are not canonical production identities

Read-only identity audit:

- workflow run: `33522033593`
- job: `99903431886`
- result: `SUCCESS`
- common months: 43 (`2023-01` through `2026-07`)

Results:

- legacy VW vs canonical production VW: exact equality `0/43`; max absolute difference `218.864231338107`; median absolute difference `17.498979817271`; correlation `0.998827030778`;
- legacy Patch vs canonical production Patch: exact equality `0/43`; max absolute difference `123.790855593923`; median absolute difference `24.259256262629`; correlation `0.999412536963`;
- RW: exact equality `43/43`;
- 3M momentum: formula-level identity apart from negligible floating representation differences.

High correlation is not identity evidence. `monthly_predictions_2023_2026.csv` may not be promoted to the production-closure VW/Patch identities.

### 2.3 Retained August Patch runner does not reproduce the canonical August Patch issuance artifact

Audit:

- workflow run: `33522158937`
- job: `99903852563`
- result: `SUCCESS`
- expected and reproduced forecast values were not logged;
- database writes: none.

Comparison against `production_closure/PROVENANCE.json`:

- absolute difference: `33.825192815012 USD`;
- relative difference: `0.008218696900873` (~`0.8219%`);
- exact float equality: `FALSE`;
- within `1e-6`: `FALSE`.

The retained input package itself ends at:

- core month: `2026-07-01`;
- daily history: `2026-07-31`.

The retained runner is hard-coded for the August target. It therefore cannot be treated as the canonical Patch identity and cannot be extended to later months merely by changing date constants.

Canonical status is refined from:

`PATCH_R1_CURRENT_ISSUER_NOT_PROVEN`

to:

`PATCH_R1_EXECUTABLE_IDENTITY_NOT_PROVEN`

## 3. Current model-risk authority

The project adopts the principles, not the regulatory applicability claim, of the current 2026 U.S. interagency model-risk guidance as an external governance authority.

Official sources:

- Federal Reserve SR 26-2: https://www.federalreserve.gov/supervisionreg/srletters/SR2602.pdf
- SR 26-2 attachment, Supervisory Guidance on Model Risk Management: https://www.federalreserve.gov/supervisionreg/srletters/SR2602a1.pdf
- OCC Bulletin 2026-13: https://www.occ.treas.gov/news-issuances/bulletins/2026/bulletin-2026-13.html

Relevant principles applied here:

- model development/use, validation/monitoring, governance and controls are distinct but connected responsibilities;
- conceptual soundness, outcomes analysis, data, assumptions and limitations should be understood and documented;
- third-party/proprietary limitations do not remove the need to validate use of the model;
- model risk controls should be commensurate with the use and consequence of the model;
- material model changes or redevelopment require their own validation rather than inheritance of the predecessor's identity.

This project is not asserting that the guidance legally governs Gold Control. It is used as an authoritative model-governance reference.

## 4. Frozen decision

### 4.1 Historical R4.1 remains immutable

`R4.1-challenger` and its historical `VW-MIDAS-SVR Adapt V2` field remain preserved for historical replay/audit only.

Do not rewrite the R4.1 frozen config to pretend that a different model is VW.

### 4.2 Legacy executable recovery route is rejected

Statuses:

- `VW_EXECUTABLE_IDENTITY_RECOVERY = REJECTED_BLOCKED_NOT_PROVEN`
- `PATCH_R1_EXECUTABLE_IDENTITY = BLOCKED_NOT_PROVEN`

Archived VW/Patch outputs remain `HISTORICAL_REPLAY` / analytical reference artifacts only.

### 4.3 A new successor identity is required

Reserved research identity:

`GOLD_H1_SUCCESSOR_R1`

Reserved engine lane:

`R4.2-SHADOW-CANDIDATE`

Current status:

`VALIDATION_ONLY_NOT_APPROVED`

These names reserve a clean lineage only. They do not approve a model or forecast.

### 4.4 R4.2 must use a generic price-reference contract

If a successor is approved, it must not be inserted into an R4.1 field named `monthly_vw_forecast`.

The future R4.2 snapshot contract should instead bind at minimum:

- `monthly_price_reference`;
- `monthly_price_reference_model_id`;
- forecast origin;
- target month and target definition;
- input snapshot id/hash;
- code/config SHA;
- evidence class;
- issued-at timestamp.

Any R4.1 emergency rule that depends on distance from the monthly VW reference must be revalidated for R4.2 against the successor reference before it is allowed to influence a prospective decision.

## 5. What is explicitly prohibited

- no silent RW fallback as primary;
- no silent 3M Momentum promotion to primary price forecast;
- no promotion of `Repro SVR` merely because it is executable;
- no promotion of VW rebuild v1/v2 under the old VW identity;
- no Patch date extension under `PATCH_R1` identity;
- no model selection based solely on 2026 fit;
- no retuning of tactical/emergency thresholds to make a new reference look better;
- no September 2026 H=1 backfill labeled prospective;
- no Decision Store forward row until a complete successor/engine input contract is valid.

## 6. Prospective boundary

The 2026-08-31 origin for September 2026 has passed.

Earliest fully contract-compliant H=1 prospective target remains:

- origin: end of `2026-09-30`;
- target: October 2026 monthly-average XAU/USD;
- evidence class at first issuance: `PROSPECTIVE_SHADOW` only.

If the successor validation/data contract is not ready at that real origin, the system remains blocked. It must not manufacture an issuance after the fact.

## 7. Required next gate

Before any successor historical score is used for selection, freeze and execute:

`gold_axis_2026/GOLD_CONTROL_H1_SUCCESSOR_VALIDATION_CONTRACT_R1.md`

The first technical gate is source/input readiness, especially a sufficiently deep, source-consistent historical XAU/USD target construction compatible with the future operational target. No model family is promoted until that gate passes.
