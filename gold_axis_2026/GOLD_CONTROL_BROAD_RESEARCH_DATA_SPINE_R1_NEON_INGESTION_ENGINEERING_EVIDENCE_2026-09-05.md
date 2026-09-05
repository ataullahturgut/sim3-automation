# Gold Control — Broad Research Data Spine R1 Neon Ingestion Engineering Evidence

**Evidence date:** 2026-09-05  
**Engineering branch:** `gold-control-broad-research-data-spine-r1`  
**Tested writer commit:** `671ca6ef84dcc4ffbbf6a6f216b8352897a1ff95`  
**Binding result:** `ENGINEERING_PREFLIGHT_PASS / PRODUCTION_PERSISTENCE_BLOCKED_CANONICAL_WRITE_AUTHORITY_NOT_YET_FROZEN`

## 1. Predecessor source-only preflight

The ingestion engineering work consumes the already-successful Broad Research Data Spine R1 source-only preflight:

- source-preflight commit: `a0a06bbce8249f8e7ac4cc0f482f1f68c711657b`
- source-preflight run: `33989608218`
- source-preflight conclusion: `success`
- source-preflight artifact digest: `sha256:ba4300d3501211ce7deaeea61627042f066ec45e679f672deb1741e26e102f1a`

No source gate was relaxed.

## 2. Ingestion engineering implementation

Frozen implementation files on the feature branch:

- `GOLD_CONTROL_BROAD_RESEARCH_DATA_SPINE_R1_NEON_INGESTION_CHANGE_CONTROL_2026-09-05.md`
- `data_pipeline/broad_research_data_spine_r1_ingest.py`
- `.github/workflows/gold-control-broad-research-r1-ingestion-preflight.yml`

Production persistence is hard-blocked unless a future canonical manifest explicitly authorizes token:

`MANIFEST_V1_37_BROAD_RESEARCH_DATA_SPINE_R1`

and the execution is on canonical branch `gold-r4-direction-engine` with manifest version `1.37` plus the exact frozen source-preflight evidence identity.

## 3. First engineering run — expected debugging evidence

Run `33991460625` failed in the bundle-build step because the writer incorrectly treated CSV column order as part of the CORE5 schema contract.

Observed actual columns:

`date, gold_monthly, gpr, fedfunds, nasdaq, usdcny`

The already-governed CORE5 contract requires the exact required column identities, row count, date range and valid values; it does not require an arbitrary CSV column order.

The writer was corrected without weakening any data gate:

- still exactly six columns total;
- still exactly the required names;
- still exactly 390 rows;
- still `1994-02-01..2026-07-01`;
- still unique dates;
- still all five required fields numeric/non-null.

Fix commit:

`671ca6ef84dcc4ffbbf6a6f216b8352897a1ff95`

## 4. Successful ingestion engineering preflight

GitHub Actions:

- workflow: `Gold Control Broad Research R1 Ingestion Engineering Preflight`
- run: `33991644883`
- run number: `2`
- tested head: `671ca6ef84dcc4ffbbf6a6f216b8352897a1ff95`
- conclusion: `success`
- evidence artifact: `broad-research-r1-ingestion-preflight-671ca6ef84dcc4ffbbf6a6f216b8352897a1ff95`
- artifact digest: `sha256:b1ae7a83d321372061d950c5f1cc8fad8262b570215f9a09ae22a4452fa355b5`

All workflow steps passed, including:

- exact feature checkout and protected read credentials;
- writer compilation;
- proof that production authority is not active on feature;
- full official Caldara-Iacoviello Git-history clone;
- 54-origin base GPR PIT coverage reconstruction;
- complete Tier-A ingestion bundle build in no-write mode;
- all build-only ingestion assertions;
- explicit proof that `--persist` is rejected on the feature branch;
- non-vendor evidence upload.

## 5. Built Tier-A bundle counts

Overall:

- series count: `12`
- total observation rows built: `71,075`
- source-vintage rows built: `126`
- quality events: `0`

CORE5:

- `CORE5_GOLD_USD_OZ_RESEARCH_R1`: `390`
- `CORE5_FEDFUNDS_RESEARCH_R1`: `390`
- `CORE5_NASDAQ_AVG_RESEARCH_R1`: `390`
- `CORE5_USDCNY_AVG_RESEARCH_R1`: `390`
- `CORE5_GPR_ROUNDED_RESEARCH_R1`: `390`
- total CORE5 observation rows: `1,950`
- CORE5 monthly range: `390` months

StakTrakr pinned four-metal panel:

- annual pinned payload files: `17`
- `XAU_STAKTRAKR_RESEARCH_DAILY_R1`: `4,230`
- `XAG_STAKTRAKR_RESEARCH_DAILY_R1`: `4,230`
- `XPT_STAKTRAKR_RESEARCH_DAILY_R1`: `4,229`
- `XPD_STAKTRAKR_RESEARCH_DAILY_R1`: `4,229`

Twelve Data hourly-derived XAU research line:

- required months: `54`
- selected daily rows: `1,177`
- minimum selected 16:00 America/New_York observations in any required month: `15`

Official GPR companions:

- proven vintage origins: `54`
- `GPRT_OFFICIAL_GIT_PIT`: `25,515` vintage-specific observation rows
- `GPRA_OFFICIAL_GIT_PIT`: `25,515` vintage-specific observation rows
- each companion series has `54/54` origin vintages.

The GPR companion row totals are vintage-specific reconstruction rows across the 54 separate origin lineages; they are not asserted to be 25,515 unique calendar months.

## 6. No-write and governance assertions

Successful engineering evidence states:

- `database_writes = NONE`
- `model_scores = NONE`
- `forecast_writes = NONE`
- `decision_writes = NONE`
- `engine_runtime_writes = NONE`
- `raw_market_values_logged = false`
- `production_write_authority_active = false`

The writer's persist path is not usable from the feature branch even when the reserved future token is injected; the canonical-branch guard was tested and passed.

## 7. Production Neon pre-write state

Production identity checked:

- project: `winter-art-94880101`
- branch: `br-gentle-mouse-b22dzkr1`
- database: `neondb`

After the successful engineering preflight, a direct read-only production check confirmed:

- `monthly_forecast_contracts = 0`
- `decision_signal_snapshots = 0`
- `decision_runs = 0`
- `decision_events = 0`
- current governed runtime: `ACTIVE = 6`, `WAITING = 5`, `BLOCKED = 1`.

A direct namespace audit also confirmed that all 12 reserved Broad R1 series identities currently have:

- no existing `source_registry` row;
- zero existing `observations` rows.

Therefore no pre-existing series-identity collision is currently present.

## 8. Binding stop point

The implementation is technically ready for governed append-safe source-data persistence, but canonical manifest v1.36 does not currently grant Broad Research Data Spine R1 production-persistence authority.

Current stop condition:

`BLOCKED_CANONICAL_WRITE_AUTHORITY_NOT_YET_FROZEN`

Do not write the 71,075 built research observations to production Neon until a canonical manifest amendment explicitly authorizes the Broad R1 source-data persistence scope and activates the reserved token under the frozen guards.

This blocker is governance-only; the ingestion engineering preflight itself is PASS.
