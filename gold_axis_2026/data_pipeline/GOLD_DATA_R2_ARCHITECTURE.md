# GOLD DATA R2 — Production Data Architecture

Freeze date: 2026-08-31

## Objective

Build a point-in-time, leakage-safe, auditable data plane for Gold Control and the Gold H=1/R4.1 research stack. No source may be silently replaced by another source with a similar economic meaning.

## Source hierarchy

- Tier A: official statistical authority, regulated benchmark administrator, exchange/index administrator, or authors' official dataset.
- Tier B: documented licensed market-data vendor, private/internal use only unless display rights are explicit.
- Tier C: documented independent operational source. Suitable for monitoring/research, not represented as settlement-grade.
- Tier D: legacy research archive. Pinned for reproducibility and never promoted to a new production authority.

## Approved / blocked production map

| Semantic series | Production source | Tier | Storage cadence | Status |
|---|---|---:|---|---|
| XAU live | XAUS public API | C | 1–5 min app cache; intraday archival separately | APPROVED indicative |
| XAU intraday | XAUS intraday | C | hourly backfill of source 2-min samples | APPROVED indicative |
| GVZ | Cboe official | A | once after Cboe EOD publication + next-day retry | APPROVED |
| VIX | Cboe official | A | once after Cboe EOD publication + next-day retry | APPROVED |
| US 10Y | DGS10, Federal Reserve H.15 via FRED/ALFRED | A | daily + revision check | APPROVED |
| Effective Fed Funds | DFF via FRED/ALFRED | A | daily + revision check | APPROVED |
| USD/CNY | DEXCHUS, Federal Reserve H.10 via FRED/ALFRED | A | daily; enforce actual availability time | APPROVED |
| Broad USD index | DTWEXBGS, Federal Reserve H.10 via FRED/ALFRED | A | daily | APPROVED as challenger/proxy only; never called DXY |
| S&P 500 | SP500 via FRED | A | daily private storage | APPROVED for private model use; raw values not publicly redistributed |
| DJIA | DJIA via FRED | A | daily private storage | APPROVED for private model use; raw values not publicly redistributed |
| Nasdaq-100 | NASDAQ100 via FRED | A | daily private storage | APPROVED for private model use; raw values not publicly redistributed |
| GPR/GPRT/GPRA | Caldara-Iacoviello official workbook | A | monthly vintage archive + daily check around release | APPROVED revision-prone |
| NEM | Twelve Data | B | daily close | PENDING API-key/symbol validation; internal non-display |
| Hecla preferred identity | Twelve Data reference/time series | B | daily close | PENDING exact-symbol validation; internal non-display |
| Barrick current NYSE | Twelve Data, ticker B | B | daily close | PENDING validation; not a silent bridge for ABX.TO legacy |
| GLL | Twelve Data | B | daily close | PENDING validation; internal non-display |
| DZZ | Twelve Data | B | daily close | PENDING validation; internal non-display |
| Exact DXY | ICE Data Indices / authorized vendor | A | daily if licensed | BLOCKED until entitlement/licence |
| LBMA Gold/Silver benchmark | ICE Benchmark Administration / LBMA | A | benchmark times if licensed | OPTIONAL; licence required for use of real-time/historical benchmark data |
| LBMA Platinum/Palladium benchmark | ICE Benchmark Administration / LBMA | A | benchmark times if licensed | BLOCKED licence required from 2026-07-01 |
| XPT/USD, XPD/USD operational alternative | Twelve Data commodities | B | daily if subscribed | PAID Grow+; new model validation required before use |
| StakTrakr metal archive | pinned repository archive | D | no automatic forward extension as authority | KEEP only for historical reproducibility |

## Scheduling policy

1. Live XAU display is not the EOD execution close. Gold Control may refresh it with a 30–60 second cache.
2. XAU intraday archival should run hourly at a non-round minute (for example minute 17) and backfill the latest available 2-minute samples. It must deduplicate by source timestamp.
3. U.S. daily market/index/vendor collectors run only after the relevant market/session has completed. Store the provider date/time and retrieval time separately.
4. Cboe VIX/GVZ collector runs after EOD publication, then retries the next morning. Never infer a missing close from live values.
5. FRED/ALFRED collector runs daily. For model snapshots, available-at timestamps/realtime vintage semantics are enforced; publication/revision lag is not ignored.
6. GPR current workbook is checked daily only near the expected monthly release window and otherwise weekly. Every changed workbook is preserved by content hash as a new source vintage.
7. Monthly forecast-input snapshots are immutable once a forecast is issued. A later data revision creates a new revision record but does not rewrite the historical forecast snapshot.
8. R4.1 EOD signal generation runs only after all required EOD inputs pass freshness and lineage checks. A blocked mandatory input blocks the relevant model path rather than invoking a proxy silently.

## Database policy

Private Neon Postgres stores normalized observations and provenance. Public GitHub stores code/contracts only.

Required logical tables:

- `retrieval_runs`: one row per ingestion attempt.
- `observations`: append-only revisions of series observations.
- `source_vintages`: hashes/metadata of revision-prone source files.
- `quality_events`: schema, freshness, gap, outlier, source or licensing failures.
- `forecast_input_snapshots`: immutable point-in-time feature values used for each model forecast.
- `derived_feature_snapshots`: Fast/Slow/3M/Emergency and transformed forecast features with formula/version lineage.
- `source_registry`: source tier, rights/display policy, semantic identity, expected cadence and freshness SLA.

The canonical view must choose the latest retrieval within one lineage only. It must never choose across different providers/semantic definitions.

## Data-quality gates

Before an observation becomes model-eligible:

- schema check passes;
- numeric/domain check passes;
- source timestamp is parseable;
- freshness SLA passes;
- no impossible calendar duplication;
- semantic/source lineage matches the frozen contract;
- if a value changed for an existing observation date, the old value is retained and the change is recorded as a revision;
- provider substitution is prohibited unless a new model/source version is explicitly validated and frozen.

## Migration / bridge rule

Legacy model series and new authority/vendor series are separate. For any proposed source migration:

1. create an overlap sample;
2. compare levels and returns;
3. quantify correlation, bias, missing-day alignment and corporate-action treatment;
4. replay the model out of sample using the candidate source;
5. accept only with a new model/data version;
6. never backfill the new provider into an old frozen model and call it an exact reproduction.

## Current blockers

- Exact executable VW-MIDAS-SVR Adapt V2 remains BLOCKED_NOT_PROVEN independently of this data plane.
- Exact DXY requires ICE/authorized-vendor rights; DTWEXBGS is only a separately named dollar proxy challenger.
- LBMA platinum/palladium data requires IBA licensing from 2026-07-01; free substitution is prohibited for the frozen Patch lineage.
- Exact `GPY`, `long_term_trend`, and `volatility` paper-feature definitions remain unresolved.
- Twelve Data Basic is internal non-display; external/public dashboard display requires appropriate rights/plan. Raw vendor prices therefore stay server-side/private.
