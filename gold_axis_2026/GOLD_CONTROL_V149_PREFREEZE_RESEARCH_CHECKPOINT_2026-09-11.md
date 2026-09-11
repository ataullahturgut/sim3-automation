# Gold Control V1.49 pre-outer research checkpoint

This checkpoint was created before any V1.49 final outer replay.

## Monthly same-origin reconstruction

- Target months: `2023-01..2026-07` (`43`)
- Long-form rows: `301` (`7 × 43`)
- VW/Patch/Momentum/RW: `43/43` frozen replay rows each
- DMA/DMS/IDMA: `43/43` diagnostic reconstructions, but `0/43` PIT-admissible rows
- Seven-model common PIT sample: `0`
- Binding status: `BLOCKED_PIT`

The canonical repository contains no executable frozen DMA/DMS/IDMA identity or
forecast artifact. Production identifies all `CORE5_*` snapshots as
`APPROVED_RESEARCH_ONLY_NOT_PIT`. Diagnostic reconstructions are retained to make
the gap observable, but they are excluded from inferential and integration-family
selection. No final-vintage substitution is treated as PIT evidence.

The admissible 2023–2024 development subset contains 24 origins. VW and Patch
have similar point estimates; no pairwise squared-loss HAC test reaches 5%,
conditional predictive-ability tests do not establish predictability, and formal
Hansen MCS is `BLOCKED_INSUFFICIENT_SAMPLE`. Complex integration is therefore
`NOT_PROVEN`; only mandatory RW and `SIMPLE_EQUAL_4` are frozen for the later
outer diagnostic.

## Short-horizon inventory and development-only incremental audit

- Historical reconstruction origins: `400`
- Mature 1D targets: `399`
- Mature 3D targets: `397`
- Block 0: `READY_TO_REPLAY`
- Block 4: `READY_TO_REPLAY` with context semantics preserved
- Blocks 1–3 and 5: `BLOCKED_PIT` and/or `BLOCKED_CONTRACT`
- `TODAY_TO_NY17`: `BLOCKED_CONTRACT`

On the first 240 origins only, adding Block 4 to Block 0 reduced calibrated
Brier by `0.002148` for 1D and `0.006268` for 3D, with non-worse log loss.
Block 4 is therefore retained before outer scoring. This is a development-stage
selection result, not final evidence.

Frozen estimator universe: regularized logistic, deterministic GBRT and
deterministic histogram gradient boosting. Hyperparameter identifiers, prior-only
selection, calibration rules, target maturity, thresholds and seed are recorded
in `v149_research/contracts/limited_candidate_freeze_v149.json`.

`AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`, production authority is false and no
production write occurred.

Status: `PASS_WITH_MONTHLY_BLOCKED_PIT`.
