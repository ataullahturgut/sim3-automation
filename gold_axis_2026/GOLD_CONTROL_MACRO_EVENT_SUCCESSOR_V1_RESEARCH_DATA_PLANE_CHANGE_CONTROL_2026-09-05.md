# Gold Control — Macro Event Successor V1 Research Data-Plane Change Control

Date: 2026-09-05
Branch: `gold-control-macro-event-successor-v1-source-contract`
Engine identity: `MACRO_EVENT_SUCCESSOR_V1`

## Scope

This change control authorizes **research-source ingestion only** for the Macro Event successor. It does not recover, repair, rename, or activate the archived `MACRO_EVENT` identity. It does not authorize a macro score, direction vote, selector/ensemble participation, position mapping, Forecast Store write, Decision Store write, or runtime promotion.

The user explicitly selected Investing.com consensus data for internal doctoral research on 2026-09-05. The project therefore records Investing.com as a research-only provider under `USER_ACCEPTED_LICENSE_RISK`; this is a governance label, not a legal conclusion or a claim of commercial redistribution rights.

## Frozen source lanes

Actual first-print reconstruction:
- NFP: BLS Employment Situation semantics reconstructed with ALFRED as-of the official release date.
- Unemployment rate: same release-date ALFRED reconstruction.
- Average Hourly Earnings MoM: derived from release-date ALFRED AHE levels and rounded to the BLS-published one-decimal MoM convention.

Consensus:
- Investing.com Economic Calendar preserved `Forecast` field only.
- `Actual` from Investing.com is never the authority actual.
- No other provider may fill missing Investing.com consensus after model results are viewed.

Availability:
- Official event timestamp is 08:30 `America/New_York` on the release date.
- Because Investing.com does not prove the exact historical last forecast-update timestamp in this research lane, its preserved Forecast is eligible **no earlier than the official release timestamp**.
- `retrieved_at` and `first_seen_at` must remain the true current reconstruction/ingestion time and must never be backdated.

## Coverage evidence and missing-data rule

Frozen coverage audit window: reference months `2016-01..2026-08`, 128 months.

Investing.com coverage after provider-rate-limit-respecting retrieval:
- NFP: 128/128 event rows; 127/128 Forecast values; coverage 0.992188.
- Unemployment: 127/128 event rows; 127/128 Forecast values; coverage 0.992188.
- AHE MoM: 128/128 event rows; 126/128 Forecast values; coverage 0.984375.

The predeclared minimum coverage gate was 0.98 and all three series pass.

The complete-case rule is now frozen before model scoring:
- all three consensus inputs must be present for an event;
- no imputation, carry-forward, provider substitution, or model forecast replacement is permitted;
- incomplete reference months are excluded from Macro Event scoring.

Known incomplete reference months from the source audit:
- `2020-08` — AHE consensus missing;
- `2025-10` — NFP/AHE consensus missing and unemployment event row missing.

Therefore the governed complete-case research panel is expected to contain **126 reference months** before actual-data quality checks. Any additional actual-data failure must reduce the panel and must be reported; it may not be silently repaired.

## Authorized Neon writes

Authorized tables:
- `source_registry`
- `retrieval_runs`
- `observations`

Writes must be append-only/deduplicated at observation level. Existing source-registry rows may only be upserted for the six Macro Event successor source IDs defined in the frozen source contract.

Forbidden tables under this authorization:
- `monthly_forecast_contracts`
- `decision_signal_snapshots`
- `decision_runs`
- `decision_events`
- `engine_execution_runs`

The ingestion transaction must assert the four Forecast/Decision authority stores are unchanged before and after the source-data write. No engine runtime state may be written.

## Evidence classification

All backfilled rows are `HISTORICAL_REPLAY_RECONSTRUCTION` / doctoral-research source data. They are not evidence that the data were originally retrieved by Gold Control at the historical event timestamp.

## Stop point after ingestion

Successful ingestion only makes the six source series available for research replay. The next phase must separately preregister the successor macro-score formula, normalization, DEV/VAL/LOCK windows, event-response confirmation semantics, and validation gates **before** looking at model-performance results.
