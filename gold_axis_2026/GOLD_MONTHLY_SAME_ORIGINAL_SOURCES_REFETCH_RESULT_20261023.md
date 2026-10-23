# GOLD MONTHLY — ORIGINAL-SOURCE REFETCH 2026 AUG/SEP + GPR + WORLD BANK

**23 October 2026 | Source code versioned on research branch | Refresh SUCCESS | Source authority NOT promoted into canonical Neon**

## Critical correction to earlier audit

Previous audit [GOLD_MONTHLY_2010_2026_DATA_GOVERNANCE_COMPLETION_REPORT_20261023.md](GOLD_MONTHLY_2010_2026_DATA_GOVERNANCE_COMPLETION_REPORT_20261023.md) described Aug/Sep 2026 four-metal daily observations as absent. **They are absent in local Neon series `XAU/XAG/XPT/XPD_STAKTRAKR_RESEARCH_DAILY_R1`, but NOT absent from the same original StakTrakr GitHub source!** Earlier conclusion that the external source could not supply those periods was **wrong**. The original GitHub pinned archive already contained Aug 1–19 (19 days × 4); updated source now has all Aug and Sep days for all four metals.

## Exact original sources, verified downloads

### Four metals — original source again

- Repository: [lbruton/StakTrakr](https://github.com/lbruton/StakTrakr)
- File: `data/spot-history-2026.json`
- **Old pinned source** `ed2e549f82ba0d1cd3ca32842b82d3888d301e01`, Git blob `64e025fb943b31b7bc8b89c6cf521db4210f560b`, **1,063 observations** including copper.
- **New pinned upstream source** `02964d0324dde362099976c867f5077a369acaa5`, Git blob `ce0775767fad3d9d56431b5ca57c3e47a3c3a70b`, **1,393 observations** including copper.
- Old-to-new comparison: **330 new records** (all five metal labels); **224 existing records changed**; **zero deletions**. Existing data should **never** be silently overwritten using a newly pulled `main` branch.
- Aug 2026: **31 calendar dates × 4 = 124** price observations, 21 weekdays / 10 weekends.
- Sep 2026: **30 calendar dates × 4 = 120** price observations, 22 weekdays / 8 weekends.
- **244 four-metal Aug/Sep price observations staged** into a separate 90-day Actions artifact, no direct Neon write. The original GitHub file is still the authority for this staged research dataset, pinned to the specific commit; no third-party raw market prices copied into the Git repository.
- The Aug/Sep values have `source=sqld` and **no `provider` attribution**; their `timestamp` is `YYYY-MM-DD 12:00:00` but **does not certify publication at noon**. Therefore same GitHub *publisher/aggregator source* ≠ verified same LBMA **fixing/benchmark** across previous decades. These are **research-only shadow rows**, not automatically canonical.
- Original-vs-current **224 price revisions** across 2026 Apr–Aug include possible material price differences. Old archival model 2026 Jan–Jul results must stay pinned to old snapshot; a new 2026 current-vintage model requires fully independent replays with vintage labels.

### GPR — original official source again

Repository [iacoviel/iacoviel.github.io](https://github.com/iacoviel/iacoviel.github.io/tree/master/gpr_archive_files), official historical monthly Git archive:

| GPR vintage | Exact initial archived Git commit | Git commit UTC | Git blob SHA |
|---|---|---|---|
| 2026-09 `data_gpr_export_202609.xls` | `21449bec606bc5a5b1bf58d08ce526dc35d66c94` | Sep 1 2026 14:27:55 UTC | `253056ac5d54881c1f3e5767087ef682e258c7a5` |
| 2026-10 `data_gpr_export_202610.xls` | `8b903073ea4ce9caf9b2f238e792685ca17270f4` | Oct 1 2026 14:19:21 UTC | `a46ff84a7e9fe83f5d1b73186d161aeba57b4da0` |

Both files fetched and original **Git blob SHAs verified**. They contain GPR monthly histories through August and September respectively according to the monthly release convention. **Values have not yet been parsed into Neon; scientific origin/timestamp gate remains.**

### Gold target — original official World Bank monthly Pink Sheet again

- Original official [World Bank Commodity Markets page](https://www.worldbank.org/en/research/commodity-markets), link `Monthly prices`.
- Official workbook download `https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx`
- Successfully downloaded **586,099 bytes**; SHA-256 `ea1c350827878ea3bbe30e3cda16a13fd3bd5b409b8458940dc94a36b5a33154`; XLSX signature verified. This is actual official World Bank workbook, no substitute aggregator. **Contents not parsed/linked to model targets yet.** Publication occurs after period end: cannot use Aug final price to predict Aug at Jul-end.

## Actual source-refetch CI and artifact

[GitHub Actions run 39917419899 — SUCCESS](https://github.com/ataullahturgut/sim3-automation/actions/runs/39917419899). The job:

1. Downloads old and new `lbruton/StakTrakr` pinned Git blobs, **verifies both hashes**, audits all existing overlapping date-metal pairs and rejects deletion.
2. Creates 2026 Aug/Sep complete four-metal **244-row research-only staging JSON**, retaining each record's `source`, `provider`, source Git commit, blob SHA, calendar date and weekend flag. No imputation or canonical source change.
3. Downloads original `iacoviel` Sep/Oct 2026 `.xls` with exact Git commit and hash verification.
4. Downloads the actual World Bank `CMO-Historical-Data-Monthly.xlsx` file, verifies file signature, size and SHA.
5. Uploads audit/manifest and staged 244 data rows as `gold-monthly-original-sources-staging-a36a690d962df55a122b74e9a37bbc76e71fe32c`, artifact ID **12485406839**, retention 90 days. No third-party market prices committed directly to repository or written to Neon.

Research files:
- `gold_axis_2026/tools/gold_monthly_refresh_original_stak_sources_v1.py`
- `gold_axis_2026/tools/gold_monthly_original_gpr_wb_source_gate_v1.py`
- `.github/workflows/gold-monthly-original-source-refresh-v1.yml`

## Next stage / limits

**Data collection from same original sources is DONE.** Prior description `No source data Aug/Sep` must now be interpreted as **local DB ingest missing**, not **upstream absent**.

Before model promotion:
- Parse official World Bank Aug/Sep target gold average from retrieved workbook, with release timestamp and revision provenance, not from secondary site.
- Parse GPR `data_gpr_export_202609.xls` and `202610.xls` to monthly histories; enforce archive_commit_at and model origin constraint.
- Verify original StakTrakr `sqld` pricing semantics (market provider, fixing timing, weekend treatment) and revisions. Keeping the same GitHub aggregator is necessary for continuity but does **not** prove the upstream provider/benchmark is unchanged.
- **Write only to separate versioned Neon `SHADOW` staging series after approval of data contract; original 2010–Jul 2026 canonical rows, 52 ChHHO forecast records, and main app remain unchanged.** Do not overwrite archival 2026 prices whose source revision differs.
- No new full monthly ChHHO training was performed after source refresh. Existing 2025/2026 previously-opened tests are not blind future results.

**Status: SOURCE-FETCH SUCCESS / UPSTREAM-REVISION-AUDITED / RESEARCH-ROWS STAGED / MODEL NOT REFRESHED / NEON NOT WRITTEN.**
