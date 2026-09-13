# GC-BREAK Neon Data Spine Audit — 2026-09-13

Status: `READ_ONLY_AUDIT_NO_DATABASE_MUTATION`

Authority: current canonical `gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md`.

## Purpose

Classify Neon data needed for the current governed Gold Control architecture into:

- `KEEP_CORE`: required for current governed runtime / formal formation work;
- `KEEP_DERIVED_OR_NATIVE_CLOCK`: derived or native-clock context required by current governed architecture;
- `PARTIAL_EXTENSION_NOT_CORE_BLOCKER`: optional/partial evidence that must not shrink the core study window;
- `ARCHIVE_CANDIDATE_AFTER_LINEAGE_EXPORT`: research data not required by the current governed 12-identity core and suitable for external archival after dependency/lineage preservation;
- `MISSING_BLOCKER`: required data absent for formal WP progression.

No database rows were changed or deleted by this audit.

## Current Neon capacity

- Project: `winter-art-94880101` (`Gold Control`)
- Plan: `free_v3`
- Branch logical size limit: `536,870,912 bytes` = 512 MiB
- Current production branch logical size: `380,108,800 bytes` ≈ 362.5 MiB
- Approximate remaining logical headroom: ≈149.5 MiB
- PostgreSQL database size observed: ≈340 MB

Largest physical tables observed:

- `observations`: 119 MB
- `xau_intraday_research_cache_1m`: 56 MB
- `xau_intraday_research_cache_5m`: 20 MB

## Binding current 12 governed identities

Monthly H=1:

- `CAUSAL_PATCH`
- `VW_MIDAS_MSVR_SUCCESSOR_V1`
- `MOMENTUM_3M`
- `RANDOM_WALK`

Strategic/trend/event/regime/emergency/risk:

- `MONTHLY_DIRECTION_3M`
- `FAST`
- `SLOW`
- `MACRO_EVENT_SUCCESSOR_V2`
- `BOCPD_RETURN_SUCCESSOR_V1`
- `EMERGENCY_LEVEL`
- `EMERGENCY_REVERSAL`
- `GVZ_RISK`

No research-only channel becomes a governed identity without later manifest change control.

## Core coverage findings

### 1. Canonical XAU / NY17 — `MISSING_BLOCKER`

Required series: `XAU_EOD_TWELVE_NY17`.

Manifest formation window: `2022-01-01 .. 2024-12-31`.

Observed Neon rows for that exact series in the formation window: **0**.

Current stored canonical rows begin only in 2026. Therefore the formal FAST/SLOW/daily GC-BREAK formation spine cannot yet be considered complete.

### 2. FAST / SLOW — `KEEP_DERIVED_OR_NATIVE_CLOCK`

No separate historical raw source is required beyond canonical daily XAU. FAST is a daily tactical state; SLOW is a completed-week state. Their formal formation replay remains downstream of canonical NY17 completion.

### 3. Monthly H=1 PIT inputs — `KEEP_CORE`

For `2022-01 .. 2024-12`, the following PIT monthly series each have **36/36 months**:

- `DGS10_ALFRED_PIT_ME`
- `DFF_ALFRED_PIT_ME`
- `DEXCHUS_ALFRED_PIT_ME`
- `NASDAQ100_ALFRED_PIT_ME`

Historical target/benchmark `XAU_MONTHLY_WB_PINKSHEET` also has **36/36 months** for 2022-2024.

These monthly-frequency sources are correctly aligned with the strategic/monthly clock and should remain in Neon.

### 4. Macro Event Successor V2 inputs — `KEEP_CORE`

For reference months `2022-01 .. 2024-12`, each required employment-event input has **36/36 reference months**:

- `MACRO_NFP_ACTUAL_FIRST_PRINT`
- `MACRO_NFP_CONSENSUS_PIT`
- `MACRO_UNEMP_ACTUAL_FIRST_PRINT`
- `MACRO_UNEMP_CONSENSUS_PIT`
- `MACRO_AHE_ACTUAL_FIRST_PRINT`
- `MACRO_AHE_CONSENSUS_PIT`

Their `event_monthly` frequency is appropriate. They should not be resampled into a false daily signal.

### 5. BOCPD / Monthly Direction — `KEEP_DERIVED_OR_NATIVE_CLOCK`

BOCPD remains completed-month context; Monthly Direction remains strategic monthly prior. Neither should be expanded into a flat daily voting stream. Their values may be carried forward only with state age / availability semantics.

### 6. GVZ / optional VIX — `PARTIAL_EXTENSION_NOT_CORE_BLOCKER`

- `GVZ_CBOE` currently starts 2026-03-10.
- `VIX_CBOE` currently starts 2026-03-13.
- No 2022-2024 observations are stored for either series.

Under the manifest, GVZ historical extension is partial and VIX is optional chronology-safe context. Their absence must **not** reduce the 2022-2024 core formation window. Use same-origin extension tests only where supported, unless full PIT history is later proven.

## Intraday frequency findings

### 1-minute research cache

- Table: `xau_intraday_research_cache_1m`
- Rows observed: 1,330,943
- Coverage: 2023-01-02 through 2026-06-30
- Physical table size: ~56 MB
- Batch lineage: Twelve Data `XAU/USD`, `HISTORICAL_RESEARCH_RETRIEVAL`, `ACADEMIC_RESEARCH_PRIVATE_CACHE`

This is **not itself canonical NY17 evidence**. The table stores only `observation_ts` and `close`; the canonical contract requires exact 16:59 New York source bar plus positive/range-valid OHLC checks and no fallback/interpolation. The cache therefore cannot silently replace the exact canonical retrieval pipeline.

For 2023-2024, the cache contains only 213 dates with a unique exact 16:59 New York row; coverage is incomplete and evidence class remains research retrieval.

Classification: `ARCHIVE_CANDIDATE_AFTER_LINEAGE_EXPORT`, but only after required exact-bar cross-checks and any still-needed event/reversal slices are extracted.

### 5-minute research cache

- Table: `xau_intraday_research_cache_5m`
- Rows observed: 482,734
- Coverage: 2020-04-06 through 2026-08-31
- Physical table size: ~20 MB
- Purpose: academic research private cache

Current governed architecture does not require continuous full-history 5-minute XAU for its daily core. Event/Market-Shock research requires only event-specific intraday windows, and `MARKET_SHOCK_V3` is research-only rather than a governed runtime identity.

Classification: `ARCHIVE_CANDIDATE_AFTER_LINEAGE_EXPORT`; retain only required event-window extracts in the active modeling spine.

### `XAU_INTRADAY_TWELVE_REST_1M`

- 9,403 rows
- Approximate observation payload ~7.3 MB
- Role: Emergency live reversal bootstrap only

Frequency is correct for its operational role, but it is not formal daily formation authority. Historical retention should be bounded to what Emergency replay / live bootstrap actually needs, after reproducibility evidence is preserved.

## Major non-core storage candidates

### GPR PIT research vintages

Three series hold approximately 76,545 observation rows:

- `GPR_OFFICIAL_GIT_PIT` — ~23 MB row payload
- `GPRT_OFFICIAL_GIT_PIT` — ~21 MB row payload
- `GPRA_OFFICIAL_GIT_PIT` — ~21 MB row payload

Combined row payload ≈65 MB before index/TOAST overhead.

`GPR_OFFICIAL_GIT_PIT` is registered for `VW_MIDAS_SVR_XAU_SUCCESSOR_V2` historical PIT research. The current governed monthly identity is `VW_MIDAS_MSVR_SUCCESSOR_V1`, not that research successor V2. `GPRT`/`GPRA` are explicitly research-only.

Classification: `ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CHECK`. Preserve externally before any deletion; do not remove if a current governed H=1 implementation is found to depend on them.

### StakTrakr metals research series

`XAU/XAG/XPT/XPD_STAKTRAKR_RESEARCH_DAILY_R1` are `RESEARCH_INPUT_ONLY` and `NOT_PIT` for formal use. They are not current core formation authority.

Classification: `ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CHECK`.

## Frequency policy for the lean modeling spine

Keep active in Neon at native clock only:

- canonical XAU: one exact governed daily NY17 observation per eligible trade date;
- FAST: derived daily state;
- SLOW: completed-week state;
- BOCPD: completed-month state;
- Monthly H=1 and Monthly Direction: monthly context;
- Macro Event V2: event-time rows only;
- GVZ: daily where supported;
- Emergency: only the intraday/live buffer or replay slices required by its role;
- Market Shock research: event-window slices only, not continuous full-history intraday cache;
- lineage, `available_at`, evidence age, missing reason, source fingerprint and audit metadata.

Do **not** upsample monthly/event evidence into artificial daily raw observations. Carry state/context forward only under native-clock age semantics.

## Recommended execution order

1. Complete canonical exact-NY17 formation data for 2022-2024 under the frozen contract.
2. Materialize the lean formation panel and verify chronology/lineage fields.
3. Run a code-level dependency audit before removing any historical research source.
4. Export/archive non-core bulky research datasets with hashes and lineage.
5. Retain only role-required intraday slices / bounded live buffers in active Neon tables.
6. Only after archive verification, request explicit approval for destructive Neon cleanup.
7. Re-measure logical size and proceed with manifest WP2/WP3/WP4 order.

## Decision

`NEON_DATA_SPINE_OPTIMIZATION_REQUIRED_BEFORE_SCALE_UP = TRUE`

`DESTRUCTIVE_CLEANUP_AUTHORIZED_BY_THIS_AUDIT = FALSE`

`PRIMARY_MISSING_BLOCKER = XAU_EOD_TWELVE_NY17 formation 2022-2024`
