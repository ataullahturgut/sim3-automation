# GOLD DATA R2.7 — Production Data Architecture

Freeze date: 2026-08-31  
Current database schema contract: `GOLD_DATA_R2.6_2026-08-31`  
Current ingestion/data contract: `GOLD_DATA_R2.7_2026-08-31`

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
8. A vendor `1day` bar is not assumed to be a completed EOD bar while the corresponding exchange session may still be open.

## Source hierarchy

- Tier A: official statistical authority, regulated benchmark administrator, exchange/index administrator, or authors' official dataset.
- Tier B: documented licensed/vendor market-data source, private/internal use only unless display rights are explicit.
- Tier C: documented independent operational source. Suitable for monitoring/research, not represented as settlement-grade.
- Tier D: legacy research archive. Pinned for reproducibility and never promoted to authority.

## Current production ingestion — VERIFIED

The following series are automatically collected and persisted to private Neon Postgres. CI performs source checks, persistence, deduplication and point-in-time database audits.

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
| `SP500_FRED` | S&P 500 | FRED API; underlying S&P DJI | A | PASS — private model use; no public raw redistribution |
| `DJIA_FRED` | DJIA | FRED API; underlying S&P DJI | A | PASS — private model use; no public raw redistribution |
| `NASDAQ100_FRED` | Nasdaq-100 | FRED API; underlying Nasdaq | A | PASS — private model use; no public raw redistribution |
| `NEM_TWELVEDATA` | Newmont | Twelve Data `NEM` | B | PASS — vendor identity validated; internal non-display |
| `BARRICK_B_TWELVEDATA` | Barrick current NYSE | Twelve Data `B` | B | PASS — vendor identity validated; internal non-display |
| `GLL_TWELVEDATA` | ProShares UltraShort Gold | Twelve Data `GLL` | B | PASS — vendor identity validated; internal non-display |
| `DZZ_TWELVEDATA` | DB Gold Double Short ETN | Twelve Data `DZZ` | B | PASS — vendor identity validated; internal non-display |
| `HL_PB_TWELVEDATA` | Hecla Series B preferred | Twelve Data `HL.PR.B` | B | PASS — vendor identity validated; internal non-display |

## Direct Fed transport decision

The former production attempt using `fred.stlouisfed.org/graph/fredgraph.csv` timed out systematically from GitHub runners. The production macro path therefore reads directly from primary authorities:

- H.15 DDP for 10-year constant-maturity Treasury yield;
- H.10 DDP for USD/CNY;
- H.10 DDP for the nominal broad dollar index;
- New York Fed Markets Data API for EFFR.

The old FRED identities remain separate lineage records for research continuity; direct-authority series are not presented as exact substitutes for frozen legacy model inputs.

## FRED private index contract

`SP500_FRED`, `DJIA_FRED` and `NASDAQ100_FRED` are obtained via the authenticated FRED API and stored privately. The first production load wrote 750 observations; the immediate repeat wrote 0. A bounded historical seed then populated the research history. Backfilled rows retain first-retrieval availability and therefore do not become retrospectively knowable in old forecast origins.

## Twelve Data R2.7 contract

### Validated identities

Live vendor metadata validation on 2026-08-31 established the following exact identities:

- Newmont: `NEM`, NYSE / XNYS, Common Stock, USD.
- Barrick current NYSE security: `B`, NYSE / XNYS, Common Stock, USD.
- GLL: `GLL`, ARCX, ETF, USD.
- DZZ: `DZZ`, ARCX, ETF, USD.
- Hecla Series B preferred: `HL.PR.B`, NYSE / XNYS, Preferred Stock, USD.

`HL-PB`, `HL-P-B` and `HL-PRB` did not validate as the Twelve Data identity and are not used. Barrick `B` is not silently bridged to the legacy `ABX.TO` proxy.

The validated vendor fields live in `source_contracts_twelve_validated.json`. Persistence only permits field-level validation overrides for already-declared Twelve Data series and forbids changing semantic identity, provider, tier or role through that overlay.

### Completed-session-only rule

Twelve Data can expose an in-progress current-day `1day` bar before the U.S. session is complete. A live test on 2026-08-31 exposed this behavior for some securities while other securities remained on 2026-08-28.

Therefore this EOD lineage accepts only:

```text
observation_date < retrieval_date_in_America/New_York
```

This is intentionally conservative. Even a truly completed same-day bar is admitted on the next scheduled collection rather than risking an incomplete session bar.

Three previously captured same-exchange-day rows were not deleted. They were preserved as raw audit evidence and superseded by `REJECTED` revisions under correction code `TWELVE_INCOMPLETE_DAILY_BAR_R2_7`.

### Rate-limit-safe deduplication

Twelve Data Basic rate limits made a second immediate API fetch unsuitable as a deduplication test. Production therefore:

1. calls the vendor once for the five validated symbols;
2. persists the collected bundle;
3. clones that same bundle with a new retrieval run ID;
4. replays it only through the persistence layer;
5. requires the replay to write zero unchanged observations.

This tests database idempotency without consuming a second set of vendor calls.

### Historical seed

An unbounded 5,000-bar request for NEM timed out on a GitHub runner. The research backfill was therefore explicitly bounded to the audited project window beginning `2016-01-01`.

Verified R2.7 historical seed result:

- 13,395 completed-session observations collected across the five series;
- 12,098 new observations written after the existing daily seed;
- 0 revised observations in the backfill;
- dedupe replay: 13,395 read, 0 written;
- 0 quality errors;
- each series has 2,679 usable daily observations;
- latest eligible observation at verification: 2026-08-28;
- point-in-time rows exposed before each series' first retrieval: 0;
- same-exchange-day eligible rows: 0.

The workflow is frozen back in `daily` mode after the one-time historical seed.

## Point-in-time / leakage contract

Neon contains three conceptually different surfaces.

### Current state

- `canonical_latest`: latest retrieved revision inside the same provider lineage.
- `usable_observations`: current quality-filtered state.

These are for current dashboards/diagnostics and are not historical backtest surfaces by themselves.

### Historical state

`observations_as_of(origin_ts)` is required for historical reconstruction and enforces:

```text
retrieved_at <= origin_ts
AND
available_as_of <= origin_ts
```

It then selects the latest revision that was actually knowable by that origin inside the same lineage. `latest_series_as_of(origin_ts)` returns the latest knowable observation per lineage.

### Immutable model state

Once an actual forecast is issued, every value used by that forecast must also be written to `forecast_input_snapshots`. Later source revisions never rewrite an old forecast snapshot.

## Conservative availability policy

For historical files/current API backfills where exact historical publication timestamps have not been independently reconstructed:

```text
available_as_of = first retrieval by Gold Data Plane
```

Status: `HISTORICAL_RELEASE_TIMESTAMP_RECONSTRUCTION = NOT_PROVEN`.

This may make a backfilled historical series unavailable in a prospective replay before the data plane first collected it. That is intentional: the system must not manufacture historical knowledge.

### Cboe R2 correction

An early R2 collector version incorrectly equated the Cboe observation date with `available_as_of`. Raw rows remain for audit evidence, but current canonical rows use the corrected policy and `observations_as_of()` excludes the invalid-availability records. CI proves zero legacy Cboe rows are exposed in the pre-correction gap.

## Database objects

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
- invalid/incomplete observations are corrected by append-only rejected revisions rather than destructive deletion;
- revision-prone source files such as the GPR workbook are separately archived by content hash.

## Scheduling policy

- XAU monitoring snapshot: hourly at minute 17.
- Daily authority ingestion: 23:45 UTC plus independent 06:25 UTC retry/verification.
- Twelve private market ingestion: Tue–Sat at 01:35 UTC plus 12:45 UTC retry.
- FRED private indices: Tue–Sat after the U.S. session plus independent retry.
- Vendor/source jobs are isolated so one provider outage cannot block unrelated sources.
- Daily Twelve ingestion uses the completed-session-only filter and a single API collection followed by local persistence dedupe replay.

## Data-quality gates

Before a current observation is model-eligible:

- schema check passes;
- numeric/domain check passes;
- source timestamp is parseable;
- source/provider identity matches the frozen contract;
- `available_as_of` is present;
- retrieval-floor availability is never earlier than first retrieval;
- provider substitution is prohibited;
- same-exchange-day Twelve `1day` bars are excluded from EOD lineage;
- latest mandatory ingestion run is successful;
- dedupe replay writes zero unchanged observations;
- point-in-time leak probes pass.

## Data available does NOT mean model migration approved

The presence of NEM/B/GLL/DZZ/HL.PR.B or the new authority/FRED series in Neon does not authorize them as silent replacements inside an archived model. Before migration into a frozen or candidate model:

1. create an overlap/source-bridge sample against the legacy lineage;
2. compare levels and returns;
3. quantify correlation, bias, missing-day alignment and corporate-action treatment;
4. run leakage-safe rolling-origin ablations;
5. accept only if out-of-sample evidence supports the change;
6. freeze a new model/data version if accepted.

## Licensed / blocked inputs

| Input | Status |
|---|---|
| Exact DXY / ICE U.S. Dollar Index | `BLOCKED_LICENSE_OR_AUTHORIZED_VENDOR_ENTITLEMENT_REQUIRED` |
| LBMA Gold/Silver benchmark | optional; appropriate IBA/LBMA data rights required |
| LBMA Platinum/Palladium | `BLOCKED_LICENSE_REQUIRED_FROM_2026-07-01` |
| XPT/USD, XPD/USD via Twelve Data | paid Grow+ required; new model lineage + validation required |
| `GPY` exact identity | `BLOCKED_AMBIGUOUS_IDENTIFIER` |
| `long_term_trend` exact paper definition | `BLOCKED_DEFINITION_NOT_RECOVERED` |
| `volatility` exact paper definition | `BLOCKED_DEFINITION_NOT_RECOVERED` |

## Remaining project-level blockers

- Exact executable VW-MIDAS-SVR Adapt V2 remains `BLOCKED_NOT_PROVEN` independently of this data plane.
- Direct Fed, FRED index and Twelve Data series do not retroactively prove the exact historical feature identities of the archived VW model.
- Exact DXY remains licensed/blocked; `DTWEXBGS_FRB_H10` is a separately named proxy challenger only.
- Platinum/palladium exact benchmark continuity is not solved without appropriate licensing.
- The next research step is source-bridge validation and leakage-safe forecast ablation, not automatic feature promotion.
