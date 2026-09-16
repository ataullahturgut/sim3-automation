# Gold Control — BOCPD Hourly Research Data Backfill Result

Date: 2026-09-16

## Scope

Research-only historical data preparation for a possible future intraday BOCPD challenger. No BOCPD hourly model was fit or scored in this operation.

## Source identity

- Series: `XAU_USD_TWELVE_1H_RESEARCH_V1`
- Provider: Twelve Data
- Symbol: `XAU/USD`
- Interval: `1h`
- Retrieval request timezone: `UTC`
- Role: `BOCPD intraday research input only`
- Status: `APPROVED_HISTORICAL_RESEARCH_ONLY_NOT_RUNTIME`
- Evidence class: `HISTORICAL_RESEARCH_BACKFILL`
- Historical publication timestamp reconstruction: `NOT_PROVEN`
- Availability policy: `first_retrieval_floor`
- Raw vendor values are private internal research data and are not to be publicly redistributed.

The hourly research series is explicitly not equivalent to the canonical `XAU_EOD_TWELVE_NY17` series.

## Retrieval lineage

- Git SHA: `7f10b4ae546b7e6af7f3e9440b1501e302cdc891`
- Workflow run: `35094406962`
- Retrieval run: `a4e54ea9-6e0c-4458-852d-505cc09f8d12`
- Pipeline: `XAU_1H_RESEARCH_BACKFILL_V1_2026-09-16`
- Trigger: `manual_authorized_historical_backfill`
- Run status: `SUCCESS`
- Rows read: `11751`
- Rows written: `11751`
- Deduped existing rows: `0`
- Lineage: `b9a3d21b5b43a9e7537e`

## Coverage

| Year | Rows | Distinct timestamps | First timestamp UTC | Last timestamp UTC | Invalid/nonpositive values |
|---|---:|---:|---|---|---:|
| 2023 | 5,841 | 5,841 | 2023-01-02 23:00 | 2023-12-29 19:00 | 0 |
| 2024 | 5,910 | 5,910 | 2024-01-01 23:00 | 2024-12-31 21:00 | 0 |
| Total | 11,751 | 11,751 | 2023-01-02 23:00 | 2024-12-31 21:00 | 0 |

Provider market-hours gaps are preserved; no interpolation or forward-fill was performed.

## Cross-check against existing daily research series

Existing authority used for the cross-check:

`XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`

For 2023-2024, the existing daily research series has 469 observations selected from the 16:00 America/New_York hourly close.

Exact timestamp join against the new hourly store:

- daily rows: `469`
- exact hourly timestamp overlaps: `469 / 469`
- exact value matches: `469 / 469`
- value mismatches: `0`
- missing hourly matches: `0`
- maximum absolute value difference: `0`

Result: `PASS`.

## Point-in-time truthfulness

All 11,751 backfilled observations have:

- `available_as_of = 2026-09-16T12:12:10.039Z`
- `retrieved_at = 2026-09-16T12:12:10.039Z`
- no backdated `available_as_of` rows
- no backdated `first_seen_at` rows

Therefore the historical bars may support retrospective research reconstruction, but they are not evidence that Gold Control possessed or issued those observations prospectively in 2023-2024.

## Storage check

Neon project branch logical-size limit: `512 MiB`.

The project branch reported logical size `381,755,392` bytes in the capacity check. Post-write PostgreSQL `pg_database_size(neondb)` was approximately `356 MiB` (a different accounting measure), while the new series' row-tuple payload was approximately `7.9 MiB` before shared-table/index overhead.

Conclusion: both 2023 and 2024 hourly histories can remain stored together. Deleting 2023 is not required under the present capacity state.

## Governance

- No production/runtime model identity was changed.
- No canonical NY17 history was altered.
- No source substitution was performed.
- No interpolation or forward-fill was performed.
- No 2025 outcome was used.
- No hourly BOCPD model was run yet.
- A future Candidate B must be separately preregistered/frozen on pre-2025 data before 2025 outcome overlay.
