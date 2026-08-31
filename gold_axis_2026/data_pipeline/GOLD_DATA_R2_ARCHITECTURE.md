# GOLD DATA R2.6 — Production Data Architecture

Freeze date: 2026-08-31  
Current schema contract: `GOLD_DATA_R2.6_2026-08-31`

## Objective

Build a point-in-time, leakage-safe, auditable data plane for Gold Control and the Gold H=1/R4.1 research stack. No source may be silently replaced by another source with a similar economic meaning.

## Non-negotiable rules

1. Provider lineage is part of series identity. Two providers for the same economic concept remain separate series IDs.
2. `observation_ts` is not automatically an availability timestamp.
3. If historical release/publication timestamps are not independently reconstructed, `available_as_of` uses the first retrieval time recorded by this data plane.
4. Historical model code must use `observations_as_of(origin_ts)` or an immutable `forecast_input_snapshots` record. `canonical_latest` and `usable_observations` are CURRENT-state views and are not historical backtest surfaces.
5. A source-file hash change alone is not a numerical revision. A new observation revision is stored only when value or quality classification changes.
6. Blocked or licensed data is never silently replaced by a convenient proxy.
7. Live/indicative XAU is not the frozen R4.1 EOD execution close.

## Source hierarchy

- Tier A: official statistical authority, regulated benchmark administrator, exchange/index administrator, or authors' official dataset.
- Tier B: documented licensed market-data vendor, private/internal use only unless display rights are explicit.
- Tier C: documented independent operational source. Suitable for monitoring/research, not represented as settlement-grade.
- Tier D: legacy research archive. Pinned for reproducibility and never promoted to a new production authority.

## Current production ingestion — VERIFIED

The following series are automatically collected and persisted to private Neon Postgres. CI performs source checks, schema migration, persistence, deduplication and an end-to-end database audit.

| Series ID | Semantic | Production source | Tier | Current status |
|---|---|---|---:|---|
| `XAU_SPOT_XAUS` | XAU live | XAUS public API | C | PASS — indicative monitoring only |
| `XAU_DAILY_XAUS` | XAU daily cross-check | XAUS history | C | PASS — candidate, not benchmark |
| `GVZ_CBOE` | GVZ | Cboe official daily history | A | PASS |
| `VIX_CBOE` | VIX | Cboe official daily history | A | PASS |
| `DGS10_FRB_H15` | US 10Y | Federal Reserve Board H.15 DDP | A | PASS — direct authority |
| `DEXCHUS_FRB_H10` | USD/CNY | Federal Reserve Board H.10 DDP | A | PASS — direct authority |
| `DTWEXBGS_FRB_H10` | broad USD index | Federal Reserve Board H.10 DDP | A | PASS — proxy challenger only, never DXY |
| `EFFR_NYFED` | effective Fed Funds | New York Fed Markets Data API | A | PASS — direct authority |
| `GPR_OFFICIAL` | GPR | Caldara-Iacoviello official workbook | A | PASS — revision-prone |
| `GPRT_OFFICIAL` | GPRT | Caldara-Iacoviello official workbook | A | PASS — revision-prone |
| `GPRA_OFFICIAL` | GPRA | Caldara-Iacoviello official workbook | A | PASS — revision-prone |

### Direct Fed transport decision

The former production attempt using `fred.stlouisfed.org/graph/fredgraph.csv` timed out systematically from GitHub runners. It is therefore not the production transport for the four macro series above.

The production macro path now reads directly from the primary authorities:

- H.15 DDP for 10-year constant maturity Treasury yield;
- H.10 DDP for USD/CNY;
- H.10 DDP for the nominal broad dollar index;
- New York Fed Markets Data API for EFFR.

The old FRED series IDs remain separate lineage records for research continuity; the direct-authority series are not presented as exact substitutes for any frozen legacy model input.

## Point-in-time / leakage contract

Neon contains three conceptually different surfaces:

### Current state

- `canonical_latest`: latest retrieved revision inside the same provider lineage.
- `usable_observations`: current quality-filtered state.

These views are useful for live dashboards and current-state diagnostics. They are **not safe for historical backtests by themselves** because a provider may revise an old observation after a historical forecast origin.

### Historical state

`observations_as_of(origin_ts)` is the required database function for historical reconstruction. It applies both:

```text
retrieved_at <= origin_ts
AND
available_as_of <= origin_ts
```

and then selects the latest revision that was actually knowable by that origin within each provider lineage.

`latest_series_as_of(origin_ts)` returns the latest knowable observation per lineage at that same origin.

### Immutable model state

Once an actual forecast is issued, all values used by the model must also be written to `forecast_input_snapshots`. Later source revisions never rewrite an old forecast snapshot.

## Conservative availability policy

For the direct Fed, Cboe historical files, GPR current workbook and XAUS historical cross-check, exact historical publication timestamps have not yet been fully reconstructed. Therefore historical rows use:

```text
available_as_of = first retrieval by Gold Data Plane
```

until a separately audited historical-vintage/release-time reconstruction exists.

Status: `HISTORICAL_RELEASE_TIMESTAMP_RECONSTRUCTION = NOT_PROVEN`.

This is intentionally conservative: it may make old history unavailable to a prospective replay, but it does not manufacture knowledge that was not proven to be available at the time.

### Cboe R2 correction

An early R2 collector version incorrectly equated the Cboe observation date with `available_as_of`. Those raw rows remain in `observations` for audit evidence, but:

- the production collector now uses first-retrieval availability;
- current canonical Cboe rows carry the corrected availability policy;
- `observations_as_of()` explicitly excludes the early invalid-availability Cboe records.

The CI point-in-time test proves that zero legacy Cboe rows are exposed in the pre-correction gap.

## Database objects

Private Neon Postgres stores data and provenance. Public GitHub stores code/contracts only.

Primary tables:

- `source_registry`
- `retrieval_runs`
- `observations`
- `source_vintages`
- `quality_events`
- `forecast_input_snapshots`
- `derived_feature_snapshots`
- `monthly_forecast_contracts`
- `system_metadata`

Current-state views:

- `canonical_latest`
- `latest_series`
- `usable_observations`

Point-in-time functions:

- `observations_as_of(timestamptz)`
- `latest_series_as_of(timestamptz)`

## Persistence semantics

For the same `(series_id, observation_ts, lineage_id)`:

- unchanged value + unchanged quality classification → no new observation row;
- changed value or changed quality classification → append a new revision;
- old revisions are retained;
- revision-prone source files such as the GPR workbook are separately archived by content hash in `source_vintages`.

The first direct-Fed production load persisted 853 observations. A repeat load of the same 853 observations wrote 0 new rows and 0 revisions, proving the deduplication contract.

## Scheduling policy

- XAU monitoring snapshot: hourly at minute 17, away from GitHub Actions' crowded top-of-hour boundary.
- Daily authority ingestion: 23:45 UTC.
- Independent retry/verification pass: 06:25 UTC.
- Every daily run is source-isolated (`xau`, `cboe`, `fed`, `gpr`), so one provider outage cannot block the other sources.
- A schema guard runs before daily ingestion and applies the idempotent point-in-time database contract.
- The final `verify-neon` gate checks required series, source registry, latest retrieval runs, availability timestamps and explicit no-leakage probes.

## Data-quality gates

Before a current observation is considered model-eligible:

- schema check passes;
- numeric/domain check passes;
- source timestamp is parseable;
- source/provider identity matches the frozen contract;
- `available_as_of` is present;
- for retrieval-floor series, `available_as_of` is never earlier than `first_seen_at`;
- provider substitution is prohibited;
- current Cboe rows must carry the corrected availability policy;
- latest ingestion run for each mandatory production source must be `SUCCESS`;
- end-to-end point-in-time leak tests must pass.

## Approved but not yet production-ingested

These are not silently reported as complete:

| Series | Planned source | Status / requirement |
|---|---|---|
| S&P 500 | `SP500` via FRED API | `PENDING_FRED_API_KEY`; private model use, no public raw redistribution |
| DJIA | `DJIA` via FRED API | `PENDING_FRED_API_KEY`; private model use, no public raw redistribution |
| Nasdaq-100 | `NASDAQ100` via FRED API | `PENDING_FRED_API_KEY`; private model use, no public raw redistribution |
| NEM | Twelve Data | PENDING API key + symbol validation; internal non-display |
| Hecla preferred identity | Twelve Data reference/time series | PENDING exact symbol validation |
| Barrick current NYSE | Twelve Data ticker `B` | PENDING API key + validation; not a silent bridge for legacy `ABX.TO` |
| GLL | Twelve Data | PENDING API key + validation |
| DZZ | Twelve Data | PENDING API key + validation |

## Licensed / blocked inputs

| Input | Status |
|---|---|
| Exact DXY / ICE U.S. Dollar Index | `BLOCKED_LICENSE_OR_AUTHORIZED_VENDOR_ENTITLEMENT_REQUIRED` |
| LBMA Gold/Silver benchmark | optional; appropriate IBA/LBMA data rights required |
| LBMA Platinum/Palladium | `BLOCKED_LICENSE_REQUIRED_FROM_2026-07-01` |
| XPT/USD, XPD/USD via Twelve Data | paid Grow+ required; would create a new model lineage and require validation |
| `GPY` exact identity | `BLOCKED_AMBIGUOUS_IDENTIFIER` |
| `long_term_trend` exact paper definition | `BLOCKED_DEFINITION_NOT_RECOVERED` |
| `volatility` exact paper definition | `BLOCKED_DEFINITION_NOT_RECOVERED` |

## Legacy / model migration rule

Legacy model series and new authority/vendor series are separate. For any proposed source migration:

1. create an overlap sample;
2. compare levels and returns;
3. quantify correlation, bias, missing-day alignment and corporate-action treatment;
4. replay the model out of sample using the candidate source;
5. accept only with a new model/data version;
6. never backfill the new provider into an old frozen model and call it an exact reproduction.

## Remaining project-level blockers

- Exact executable VW-MIDAS-SVR Adapt V2 remains `BLOCKED_NOT_PROVEN` independently of this data plane.
- Direct Fed and broad-dollar authority series do not retroactively prove the exact historical feature identities of the archived VW model.
- Exact DXY remains licensed/blocked; `DTWEXBGS_FRB_H10` is a separately named proxy challenger only.
- Platinum/palladium exact benchmark continuity is not solved without appropriate licensing.
- S&P 500, DJIA and Nasdaq-100 production ingestion is waiting for a FRED API key.
- Twelve Data market instruments are waiting for API access and symbol/entitlement validation.
