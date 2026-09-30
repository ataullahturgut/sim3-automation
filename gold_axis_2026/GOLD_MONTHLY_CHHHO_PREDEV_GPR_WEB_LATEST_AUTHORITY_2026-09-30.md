# GOLD MONTHLY — ChHHO Pre-DEV GPR Web-Latest PIT Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED HISTORICAL PIT SOURCE AUDIT / NO MODEL RESULT YET  
**Purpose:** determine whether a scientifically valid pre-DEV ChHHO backcast can be reconstructed before the canonical exact-vintage archive begins in 2022-03.

## 1. Why this source is being opened

The canonical series `GPR_OFFICIAL_GIT_PIT` has continuous exact-origin evidence only from 2022-03. Therefore target months before 2022-04 cannot be reconstructed with the existing source contract.

A separate official Git path has now been identified:

- repository: `iacoviel/iacoviel.github.io`
- path: `gpr_files/gpr_web_latest.xlsx`
- owner/source: Caldara–Iacoviello official GPR repository
- observed Git history begins in late 2019 and contains repeated historical updates during 2020-2021.

This source is **not** assumed equivalent to the later `data_gpr_export_YYYYMM.xls` archive. It must pass its own origin-time and content audit.

## 2. Frozen origin-time rule

For forecast origin month `p`:

1. origin cutoff = last calendar day of `p` at **17:00 America/New_York**;
2. inspect Git commit history of exactly `gpr_files/gpr_web_latest.xlsx`;
3. select the latest commit whose Git committer timestamp is **<= origin cutoff**;
4. read the file exactly at that commit;
5. keep GPR observations only through `p-1`;
6. require that observation `p-1` is present;
7. require at least 24 monthly GPR observations through `p-1`;
8. never substitute the current/final GPR file;
9. never use a later monthly snapshot merely because its filename refers to an older month.

If any requirement fails, that origin is **NOT BUILDABLE** and must be skipped, not imputed.

## 3. Frozen ChHHO replay rule

For every source-passing origin:

- use the original ChHHO-ANFIS implementation without optimizer/hyperparameter changes;
- target remains H=1 next-calendar-month average XAU/USD;
- frozen 8 VW-MIDAS features remain Gold/Silver/Platinum/Palladium × {MR,VW};
- the selected origin snapshot supplies the GPR history for every training and target feature at that outer origin;
- preprocessing, validation, optimizer selection and local refinement may use only rows strictly before the target;
- no 2022+ outcome may affect a pre-DEV forecast;
- database access remains READ_ONLY.

## 4. Alarm rules to be evaluated

No threshold search is permitted on the backcast.

### A — Cross-metal fragility
- ChHHO direction = current Gold direction
- |Gold 1m log return| < 2%
- >=2 of Silver/Platinum/Palladium opposite to Gold

### C — Delayed rates catch-up
- Gold 1m < 0
- nominal 10Y monthly-mean change < 0
- real 10Y monthly-mean change < 0
- |ChHHO predicted move| < 1%

### D — Macro-Gold conflict
- Gold 1m > +3%
- Broad USD monthly-mean log change > 0
- nominal 10Y monthly-mean change > 0
- real 10Y monthly-mean change > 0
- ChHHO predicts UP

### E — Extreme level + model disagreement
Discovery-frozen:
- Gold monthly average >20% above trailing 12m average
- |ChHHO predicted return - current Gold 1m return| >5 percentage points

### G — Post-liquidation
Discovery-frozen:
- Gold trailing 3m monthly-average log return <= -10%

B remains warning-only and is not counted as a hard alarm.

## 5. High-error label

Keep the existing frozen alarm target:

**HIGH ERROR = ChHHO absolute price error > 63.06 USD**

This nominal-USD threshold is retained only for continuity with the current alarm research. APE/return-space error must be reported alongside it.

## 6. Macro reconstruction for C/D

For pre-DEV historical alarm characterization only:

- nominal 10Y: FRED DGS10 daily historical observations;
- real 10Y: FRED DFII10 daily historical observations;
- Broad USD: FRED DTWEXBGS daily historical observations;
- monthly means use only observations available under conservative calendar cutoffs:
  - H.15 rates: exclude final 2 calendar days of origin month;
  - H.10 Broad USD: exclude final 7 calendar days of origin month.

This is historical-reconstruction evidence, not vintage-proof macro data. C/D pre-DEV results must therefore be labeled **historical reconstruction**, while the ChHHO GPR source itself must pass the Git PIT rule above.

## 7. Frozen execution range

Audit requested origins from **2019-12 through 2022-02**, corresponding to target months 2020-01 through 2022-03.

The earliest passing origin is determined solely by source availability/content, not by forecast outcomes.

## 8. Required outputs

The run must produce:

- source audit for every requested origin;
- selected official commit SHA/timestamp;
- snapshot SHA256;
- required `p-1` GPR month/value;
- buildable/not-buildable reason;
- ChHHO forecast/actual/AE/APE for every buildable target;
- A/C/D/E/G alarm flags;
- hit/false-alarm/miss counts;
- year-by-year summaries;
- exact source and code provenance.

## 9. Promotion rule

This exercise is **historical validation only**.

It may strengthen or weaken confidence in alarm mechanisms, but it may not:
- retune the alarms;
- select a fallback model;
- authorize routing;
- change ChHHO;
- overwrite canonical 2022+ authorities.

If the web-latest source audit cannot prove enough origins, the backcast remains blocked and that negative result is final unless a different official PIT source is pre-registered first.
