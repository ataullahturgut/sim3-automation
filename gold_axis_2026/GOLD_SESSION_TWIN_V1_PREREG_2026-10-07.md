# SESSION TWIN V1 — PREREGISTRATION / IDENTITY CONTRACT

**Date:** 2026-10-07
**Status:** BINDING BEFORE SESSION RUN

## Role

TWIN is a local path-analogue rescue specialist layered on fresh SESSION AURORA.

It is not a stand-alone direction engine.

## Frozen path representations

### SHAPE24
- latest 24 active completed hourly XAU log returns before session start;
- normalize by L2 norm;
- cumulative normalized path;
- PAA into 8 blocks.

### SHAPE48
- latest 48 active completed hourly XAU log returns;
- same normalization;
- cumulative normalized path;
- PAA into 12 blocks.

### SHAPE_MULTI
- concatenate SHAPE24 and SHAPE48.

No amplitude variable is added.

## Local analogue probability

For every session origin:
- memory contains only prior same-window rows satisfying `end_utc <= current start_utc`;
- standardize embedding dimensions using matured memory only;
- Euclidean distance;
- nearest k = 25;
- similarity weight = exp(-distance / median(neighbour distances));
- local UP probability = weighted mean of matured outcomes.

Minimum matured memory = 40.

## Frozen override rule

AURORA remains default.

Override only when:
- AURORA = DOWN and p_local >= 0.70 -> use p_local;
- AURORA = UP and p_local <= 0.30 -> use p_local.

Otherwise keep p_AURORA.

No threshold or k search is allowed.

## Session development selection

Historical H3 TWIN selected representation on 2022-H2. Fresh session AURORA has no 2022 ledger, so representation selection is restricted to 2023–2024 development.

For each partition/window and each representation:
- replay causally using same-window matured memory only;
- eligible if:
  - at least 3 actual overrides;
  - net rescue > 0;
  - TWIN BA >= matched AURORA BA;
  - TWIN accuracy >= AURORA accuracy - 0.5 pp;
  - TWIN Brier <= AURORA Brier + 0.0025.

Rank eligible representations by:
1. higher BA;
2. higher accuracy;
3. lower Brier;
4. lower log loss;
5. simpler representation in tie order SHAPE24 -> SHAPE48 -> SHAPE_MULTI.

## Frozen 2025 transport

Only development-eligible session heads may open 2025.

Representation, k and thresholds are frozen.

## Timing

All XAU hourly bars must satisfy:
`available_at_utc < session_start`.

No current or overlapping target outcome may enter analogue memory.

## Governance

- 30% minimum-class-recall floor does not apply; TWIN is a conditional correction specialist.
- 2025 may validate or fail a frozen role but cannot change it.
- 2026 remains unopened.
- Historical H3 TWIN predictions are QA-only.
