# Gold Data R1 — storage and provenance contract

This directory is the persistent data layer for Gold Control and future R4.x forecast/execution runs.

## Storage layers

- `snapshots/`: append-only retrieval snapshots. One row per provider observation/retrieval. Never silently rewrite history.
- `canonical/`: deduplicated normalized series used by the application/model. Rebuilt deterministically from snapshots/source archives.
- `vintages/`: revision-prone source snapshots, especially GPR/GPRT/GPRA. A newly downloaded vintage is stored separately before canonicalization.
- `manifests/`: machine-readable run metadata, source status and quality checks.

## Mandatory observation fields

Canonical long-format records use:

`series_id,date,value,source,source_symbol,provider_as_of,retrieved_at,frequency,unit,transform,quality_status,lineage_id`

A row must not be labeled `OK` when the provider timestamp/source identity is missing where the source normally supplies one. Third-party operational proxies are explicitly labeled; they are not promoted to authoritative references.

## Provider substitution rule

Provider substitution is prohibited unless a new versioned source contract is committed first. A provider switch starts a new `lineage_id`; series from different lineages are never silently concatenated as if homogeneous.

## Revision policy

Revision-prone macro series are not overwritten in-place. Each retrieval is retained in `vintages/` and the canonical file records the retrieval timestamp. This allows later point-in-time reconstruction where the provider's publication/vintage history supports it.

## Live vs EOD

Indicative XAU spot snapshots are display/monitoring data. They are not automatically treated as the R4.1 EOD execution close. EOD promotion requires an explicit, tested session-close contract.

## Current blockers

- Exact executable VW-MIDAS-SVR Adapt V2 training/replay chain remains `BLOCKED_NOT_PROVEN`.
- GPY identity is `BLOCKED_AMBIGUOUS_IDENTIFIER`.
- Exact definitions of the paper's `long_term_trend` and `volatility` fields remain `BLOCKED_DEFINITION_NOT_RECOVERED`.
- Scheduled GitHub Actions run on the repository default branch. The Gold project currently lives on `gold-r4-direction-engine`; automatic scheduling must not be claimed until the workflow is installed on the default branch or the Gold branch becomes default/merged by an explicit repository decision.
