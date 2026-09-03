# Gold Control Deployment Display Snapshot Contract V2 — 2026-09-03

**Frozen marker:** `FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V2`

## Purpose

Neon production remains the immutable evidence/state authority. V2 closes one deployment-only gap in V1: a hosting instance without `NEON_DATABASE_URL` could render the seven persisted direction/risk context rows, but could not render already-persisted `HISTORICAL_REPLAY` expert rows because the forecast reader returned an empty list.

## V2 allowed payload

V1 payload remains unchanged: 12 governed runtime rows, seven persisted display-context features, Data Evidence Spine health and lineage fields. V2 additionally permits **display-only historical replay expert rows** that already exist in `monthly_expert_forecasts` and satisfy all of the following:

- `forecast_track = HISTORICAL_REPLAY`
- `evidence_class = HISTORICAL_REPLAY`
- `canonical_authority = false`
- `selector_status = NOT_PROVEN_EXPERT_SELECTION_RULE`
- `auto_selector = OFF`
- `auto_ensemble = OFF`
- `provenance.historical_replay = true`
- `provenance.prospective_claim = false`
- `provenance.canonical_authority = false`
- `provenance.direction_vote_permitted = false`

No replay row may populate `MONTH_END_EXPERT`, `EARLY_INDICATIVE`, canonical forecast, Decision Store, selector/ensemble output, position mapping or action state.

## Source and refresh

The V2 snapshot is exported from production Neon inside `SET TRANSACTION READ ONLY`. The payload is SHA-256 fingerprinted and validated before use. The scheduled refresh workflow must include the latest governed replay target and replay rows whenever such rows exist.

## UI semantics

When direct Neon access is unavailable, `forecast_source.py` may use only the validated V2 snapshot for `HISTORICAL_REPLAY`. Other forecast tracks remain empty unless genuinely issued through their own governed production paths.

The Tahmin page must visibly label fallback replay as:

`EYLÜL 2026 HISTORICAL REPLAY` / `REPLAY · PROSPECTIVE DEĞİL`

The current September replay contains only the experts proven and persisted under the replay contract. It must not create a direction vote or pretend to be the missed 31-August prospective forecast.

## Required acceptance

Release is blocked unless a real 390×844 browser started with `NEON_DATABASE_URL` deliberately absent shows the persisted replay values from the V2 snapshot, while canonical forecast/Decision Store/selector/action authority remain absent or locked.
