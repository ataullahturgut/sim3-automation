# GOLD MONTHLY — Original Sources Refetch, Official Parsing and Neon Shadow Ingest Verification

**2026-10-23 • Research-source staging COMPLETED • Canonical training/forecast series NOT MODIFIED**

## Actual actions and results (not a plan)

Original source files:
- [StakTrakr source](https://github.com/lbruton/StakTrakr/blob/02964d0324dde362099976c867f5077a369acaa5/data/spot-history-2026.json) fixed git commit `02964d0324dde362099976c867f5077a369acaa5`, Git blob `ce0775767fad3d9d56431b5ca57c3e47a3c3a70b`, compared to original `ed2e549f82ba0d1cd3ca32842b82d3888d301e01`. **224 overlapping observations changed**, **330 newly added in upstream file** across five source metal labels. Aug/Sep four target metals fully present.
- [Official GPR archives](https://github.com/iacoviel/iacoviel.github.io/tree/master/gpr_archive_files) versioned `data_gpr_export_202609.xls` and `data_gpr_export_202610.xls` Git commits `21449bec606bc5a5b1bf58d08ce526dc35d66c94`, `8b903073ea4ce9caf9b2f238e792685ca17270f4`; original Git blob checks pass.
- [World Bank monthly commodity price spreadsheet](https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx), **Monthly Prices** tab, **Gold** column 70, `$/troy oz`, source document says updated **2026-10-02**. SHA-256 `ea1c350827878ea3bbe30e3cda16a13fd3bd5b409b8458940dc94a36b5a33154`.

### Neon append-only research staging — confirmed readback

**Gold monthly research database** Neon project `winter-art-94880101`, database `neondb`, schema `gold_monthly_h1`.

1. `gold_monthly_h1.original_source_shadow_daily_v1`: created isolated source-lineage controlled table; inserted **244** rows, precisely **four metals × 61 dates**:
   - 2026-08 Gold, Silver, Platinum, Palladium each **31**, 10 weekends per metal (21 weekdays).
   - 2026-09 Gold, Silver, Platinum, Palladium each **30**, 8 weekends per metal (22 weekdays).
   - Every observation marks `firstprint_verified=false`, status `RESEARCH_SHADOW_UNVERIFIED_PROVIDER`; retains commit and original Git blob, label `source=sqld`, no `provider` attribution. Unique source_commit/date/metal prevents overwrites.
2. `gold_monthly_h1.original_source_shadow_monthly_v1`: created isolated vintage-controlled table; inserted **18** monthly values:
   - Official `2026-09` GPR Git vintage: **6 values** (Jul/Aug 2026 × GPR, GPRT, GPRA), release archival commit **2026-09-01 14:27:55Z**.
   - Official `2026-10` GPR Git vintage: **9 values** (Jul/Aug/Sep 2026 × GPR, GPRT, GPRA), release archival commit **2026-10-01 14:19:21Z**.
   - Official World Bank `2026-10-02_OCT_PINK_SHEET` vintage: **3 gold monthly means** (Jul/Aug/Sep 2026); release date **2026-10-02**, exact intra-day publication clock not certified.
   - Unique source_family/version/series/month prevents accidental old-value replacements. GPR August vintage **117.918846** (Sep-release) versus **125.621384** (Oct-release). Keep BOTH, never put later GPR into earlier prediction.
   - 2026-08 WB Gold **4411 USD/oz**, 2026-09 WB Gold **4319 USD/oz**.
3. **Read-only integrity query** confirmed exact per-metal counts **61**, no false firstprint flags, zero Aug/Sep entries added into `public.observations` canonical StakTrakr series, **53 archived ChHHO forecast records still present**. No update/delete run and no production model promotion.

### Comparable historical-source gold means from staged data

| Month | StakTrakr mean ALL calendar days | StakTrakr weekDAY only | Official WB |
|---|---:|---:|---:|
| 2026-08 | 4393.419 | 4407.304 | 4411.000 |
| 2026-09 | 4336.493 | 4327.880 | 4319.000 |

Historical observations' `timestamp YYYY-MM-DD 12:00:00` is not proven first market publication; the same GitHub aggregator is not necessarily the same `LBMA` price methodology/fixing or actual provider as earlier years, especially `sqld` rows.

### Verified code and dedicated CI

[Actions run #39919096396 — SUCCESS](https://github.com/ataullahturgut/sim3-automation/actions/runs/39919096396) prints:
- `SAME_UPSTREAM_SOURCE_STAGING_GATE=PASS`
- `OFFICIAL_GPR_WB_SOURCE_BYTES_GATE=PASS`
- `OFFICIAL_GPR_WB_MONTHLY_VALUES_EXTRACTION=PASS`
- `{"validated_daily":244,"validated_official_monthly":18,"only_research_shadow":true,"original_firstprint_verified":false}`.

Implementations:
- `tools/gold_monthly_refresh_original_stak_sources_v1.py` — compares revisions and generates 244-row stage.
- `tools/gold_monthly_original_gpr_wb_source_gate_v1.py` — pinned source byte hashes.
- `tools/gold_monthly_parse_official_2026_vintages_v1.py` — extracts correct GPR metrics/vintages and World Bank Gold units/dates.
- `tools/gold_monthly_original_sources_neon_shadow_ingest_v1.py` — reproducible, idempotent, opt-in **SHADOW ONLY** importer with strict counts/commit/source and firstprint rejection; valid input contract tested in CI without connecting Neon.
- `.github/workflows/gold-monthly-original-source-refresh-v1.yml` — download original sources, hashes, extracts, import contract validation; never DB writes from CI.

## Remaining gate: clean MODEL SOURCE, not retrieval

This operation has finished the **same-original-source August/September acquisition + Neon research ingestion**, NOT a full production-training source replacement. Never blend these into the canonical `XAU/XAG/XPT/XPD_STAKTRAKR_RESEARCH_DAILY_R1` without a separate method/source PIT decision.

Still need:
- Upstream `sqld` actual market provider, timezone and price/fixing definition (also February–July 2026 rows with mixed and unverified provider).
- Historic first-publication timestamps for metal prices: date-only `12:00` research backfill is not a firstprint.
- Consistent model `origin_cutoff` selection. Sep 2026 GPR release (Sep 1) cannot be used to forecast Sep 2026 at Aug 31; Oct 1 release cannot predict Oct 2026 at Sep 30. WB Oct 2 final Sep gold cannot be used Sep 30.
- GPR origin vintages prior to March 2022 remain unverified; 2022+ historical training can use old historical dates from later available archived versions.
- Model 2025–2026 full optimized retrospective run on a scientifically approved unbroken data source has **NOT** been executed here. Existing results are frozen and not promoted.

**Disposition:** SOURCE_REFRESH_PASS / NEON_SHADOW_244_DAILY_18_MONTHLY_PASS / ORIGINAL_SOURCE_REVISIONS_PRESERVED / MODEL_INTEGRATION_BLOCKED_ON_SOURCE_FIRSTPRINT / NO_CANONICAL_MUTATION.
