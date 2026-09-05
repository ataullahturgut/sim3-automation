# Gold Control — Broad Research Data Spine R1 Neon Ingestion Change Control

**Freeze date:** 2026-09-05  
**Engineering branch:** `gold-control-broad-research-data-spine-r1`  
**Status at freeze:** `ENGINEERING_READY / PRODUCTION_PERSISTENCE_BLOCKED_PENDING_CANONICAL_MANIFEST_AUTHORITY`  
**Scope:** append-safe research/source-data persistence only. No model scoring, forecast issuance, decision write, engine-runtime change, selector, ensemble or position/action mapping.

## 1. Binding predecessor evidence

This ingestion step exists only because the separate Broad Research Data Spine R1 source-only preflight completed successfully.

Frozen successful preflight evidence:

- feature commit: `a0a06bbce8249f8e7ac4cc0f482f1f68c711657b`
- GitHub Actions run: `33989608218` (`Gold Control Broad Research Data Spine R1 Preflight`, run #6)
- conclusion: `success`
- evidence artifact: `broad-research-data-spine-r1-preflight-a0a06bbce8249f8e7ac4cc0f482f1f68c711657b`
- artifact digest: `sha256:ba4300d3501211ce7deaeea61627042f066ec45e679f672deb1741e26e102f1a`
- CORE5: PASS, exactly 390 months, `1994-02..2026-07`
- StakTrakr pinned four-metal panel: PASS
- Twelve Data hourly-derived XAU research line: PASS, 54/54 months
- GPRT/GPRA exact-vintage companion coverage: PASS, 54/54 origins
- preflight database writes: `NONE`
- preflight model scores: `NONE`
- preflight forecast writes: `NONE`
- preflight decision writes: `NONE`

No ingestion gate may be weakened after this result.

## 2. Authority boundary

The canonical project manifest remains the sole project decision authority.

Existing manifest v1.36 explicitly authorizes production source-data/audit-plane writes for the separately governed `GPR_OFFICIAL_GIT_PIT` data plane, but it does **not** yet contain a Broad Research Data Spine R1 production-persistence authorization.

Therefore this feature-branch change-control may freeze and test the ingestion implementation, but it may not itself grant production-write authority.

Reserved future authorization token:

`MANIFEST_V1_37_BROAD_RESEARCH_DATA_SPINE_R1`

The writer MUST reject `--persist` unless all of the following are simultaneously true:

1. `BROAD_RESEARCH_PRODUCTION_WRITE_AUTHORIZED=MANIFEST_V1_37_BROAD_RESEARCH_DATA_SPINE_R1`;
2. `GITHUB_REF_NAME=gold-r4-direction-engine`;
3. `GOLD_CONTROL_MANIFEST_VERSION=1.37`;
4. the frozen successful source-preflight head is exactly `a0a06bbce8249f8e7ac4cc0f482f1f68c711657b`;
5. the frozen successful preflight artifact digest is exactly `sha256:ba4300d3501211ce7deaeea61627042f066ec45e679f672deb1741e26e102f1a`.

Until a canonical manifest explicitly activates that token, production persistence is:

`BLOCKED_CANONICAL_WRITE_AUTHORITY_NOT_YET_FROZEN`

No feature-branch workflow may bypass this rule.

## 3. Exact production target

Production Neon identity remains:

- project: `winter-art-94880101`
- branch: `br-gentle-mouse-b22dzkr1`
- database: `neondb`

No new table or schema migration is authorized or required.

Allowed write tables only:

- `source_registry`
- `retrieval_runs`
- `observations`
- `source_vintages`
- `quality_events` only if a separately accepted successful bundle contains governed quality evidence; the R1 successful persistence path requires zero ERROR quality events.

Forbidden writes include, without limitation:

- `monthly_forecast_contracts`
- `decision_signal_snapshots`
- `decision_runs`
- `decision_events`
- engine runtime/state tables
- model validation/promotion tables
- selector/ensemble state
- position/action mappings.

The four forecast/decision authority stores must be exactly zero before and after persistence.

The current governed 12-motor runtime distribution must remain exactly:

- `ACTIVE = 6`
- `WAITING = 5`
- `BLOCKED = 1`

Any mismatch stops the transaction.

## 4. Frozen Tier-A persistence identities

### 4.1 CORE5 locked monthly research snapshot

Separate Neon series:

- `CORE5_GOLD_USD_OZ_RESEARCH_R1`
- `CORE5_FEDFUNDS_RESEARCH_R1`
- `CORE5_NASDAQ_AVG_RESEARCH_R1`
- `CORE5_USDCNY_AVG_RESEARCH_R1`
- `CORE5_GPR_ROUNDED_RESEARCH_R1`

Source artifact:

`gold_axis_2026/core5_monthly.csv.gz.b64`

Required shape remains exactly 390 months, `1994-02..2026-07`.

Evidence class:

`LOCKED_LOCAL_RESEARCH_SNAPSHOT_NOT_HISTORICAL_PIT`

Timestamp rule:

- `observation_ts` = represented calendar month;
- `retrieved_at` = true ingestion/reconstruction time;
- `first_seen_at` = true ingestion/reconstruction time on first insert;
- `provider_as_of = NULL`;
- `available_as_of = retrieved_at`.

The last rule is deliberate: this locked local snapshot is not granted retroactive historical PIT availability. Its old observation dates do not imply the file was available to Gold Control at those old origins.

### 4.2 StakTrakr four-metal daily research panel

Pinned upstream:

`lbruton/StakTrakr@ed2e549f82ba0d1cd3ca32842b82d3888d301e01`

Series:

- `XAU_STAKTRAKR_RESEARCH_DAILY_R1`
- `XAG_STAKTRAKR_RESEARCH_DAILY_R1`
- `XPT_STAKTRAKR_RESEARCH_DAILY_R1`
- `XPD_STAKTRAKR_RESEARCH_DAILY_R1`

Range is limited through `2026-07-31`.

Evidence class:

`HISTORICAL_RECONSTRUCTION_NO_ORIGIN_PIT_CLAIM`

Timestamp rule:

- historical record date is preserved as `observation_ts`;
- `retrieved_at` and first `first_seen_at` are current reconstruction time;
- `provider_as_of = NULL`;
- `available_as_of = retrieved_at`;
- no historical PIT claim is made.

The source payload does not encode a formal unit field. The persisted unit is therefore left NULL rather than inferred and the metadata records `unit_not_encoded_in_source_payload=true`.

Any conflicting duplicate for the same research series/day is a hard failure; the writer may not silently choose one.

### 4.3 Twelve Data hourly-derived XAU research line

Series:

`XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`

Frozen retrieval:

- provider: Twelve Data
- symbol: `XAU/USD`
- interval: `1h`
- timezone: `America/New_York`
- selected hourly bar timestamp: `16:00:00`
- required months: `2022-03..2026-08`
- minimum selected days: 15 per month.

Evidence class:

`HISTORICAL_RESEARCH_RETRIEVAL_NOT_CANONICAL_NY17`

This series is not equivalent to:

`XAU_EOD_TWELVE_NY17`

Timestamp rule:

- `observation_ts` = selected 16:00 America/New_York bar timestamp converted to UTC;
- `retrieved_at` and first `first_seen_at` = true current retrieval time;
- `provider_as_of = NULL`;
- `available_as_of = retrieved_at`.

The ingestion code must not print raw vendor values to CI logs or evidence summaries.

### 4.4 Official GPR companion PIT reconstructions

Series:

- `GPRT_OFFICIAL_GIT_PIT`
- `GPRA_OFFICIAL_GIT_PIT`

Required origins:

`2022-03..2026-08` = 54 origins.

Each origin uses the same exact official Caldara-Iacoviello archive workbook identity already proven by the GPR PIT audit.

Evidence class:

`HISTORICAL_REPLAY_RECONSTRUCTION`

Timestamp semantics:

- `provider_as_of` / `available_as_of` = earliest official Git archive-add commit floor for that exact workbook;
- `retrieved_at` / first `first_seen_at` = true current reconstruction time;
- the Git commit timestamp is availability evidence, not a false historical Gold Control retrieval timestamp;
- current/final-vintage substitution is forbidden.

Every origin must contain the required `p-1` companion observation.

## 5. Source registry behavior

This ingestion is append-safe.

For each reserved R1 series ID:

- if no registry row exists, the writer may insert it;
- if the series ID already exists with matching immutable identity fields, the writer leaves the existing row unchanged;
- if an existing row conflicts on semantic/provider/symbol/frequency identity, persistence hard-fails.

The writer must not use an upsert that silently rewrites an existing series identity.

## 6. Observation idempotency and revision rule

For an exact `(series_id, observation_ts, lineage_id)` already represented in `canonical_latest`:

- if value and quality status are unchanged, skip the duplicate;
- if value or quality status genuinely changed under the same lineage, append a new observation while preserving the original `first_seen_at`.

A new payload hash alone is not sufficient reason to manufacture a data revision.

No observation row is UPDATEd or DELETEd.

`source_vintages` uses its existing `(source_id, content_sha256)` uniqueness and `ON CONFLICT DO NOTHING`.

`retrieval_runs` is one immutable run identity except for closing that same run record with final row counts/status.

## 7. Ingestion engineering preflight

Before any canonical production execution, the ingestion builder itself must complete in no-write mode and prove:

- 12 reserved Tier-A series are built;
- CORE5 contributes exactly `5 × 390 = 1950` observation rows;
- all four StakTrakr metal series have non-zero governed rows;
- Twelve Data has exactly 54 required months and every month has at least 15 selected days;
- GPRT and GPRA each have 54 proven vintage origins;
- zero ERROR quality events;
- production Neon forecast/decision authority counts remain zero;
- production runtime distribution remains 6/5/1;
- `database_writes = NONE`;
- `model_scores = NONE`;
- `forecast_writes = NONE`;
- `decision_writes = NONE`;
- `engine_runtime_writes = NONE`;
- `raw_market_values_logged = false`.

Only metadata, counts and hashes may be uploaded as CI evidence.

## 8. Stop rules

Stop and do not persist if any of the following occurs:

- canonical manifest authorization is absent;
- execution is not on the canonical branch;
- the frozen preflight evidence identity differs;
- any Tier-A source gate fails;
- a source identity conflicts with an existing Neon registry row;
- a forecast/decision authority table is non-zero;
- the current 12-motor runtime distribution differs from 6 ACTIVE / 5 WAITING / 1 BLOCKED;
- a provider/source substitution would be required;
- a historical timestamp would need to be backdated;
- vendor raw values would be exposed in CI evidence.

No model may be scored and no selector/ensemble work may start merely because this ingestion engineering step exists.
