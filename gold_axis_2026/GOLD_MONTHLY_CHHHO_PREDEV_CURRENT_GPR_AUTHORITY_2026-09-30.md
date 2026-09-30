# GOLD MONTHLY — ChHHO Pre-DEV Current-Method GPR Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED / SAME-METHODOLOGY HISTORICAL PIT AUTHORITY  
**Purpose:** valid pre-DEV ChHHO backcast using the same GPR methodology as the canonical 2022+ project.

## Source

Official repository:
- `iacoviel/iacoviel.github.io`

Official current-method file:
- `gpr_files/data_gpr_export.xls`

The official current GPR page (`gpr.Rmd`) distributes `data_gpr_export.xls` and states that the search terms/methodology were changed in 2021 relative to the old GPR index.

The official Git history of `data_gpr_export.xls` begins on **2021-10-18**, so the earliest scientifically admissible current-method pre-DEV forecast origin is **2021-10**.

## Frozen origin-time rule

For each origin month p:
1. cutoff = last calendar day of p at 17:00 America/New_York;
2. select the latest commit of exactly `gpr_files/data_gpr_export.xls` with committer timestamp <= cutoff;
3. read the file exactly at that commit;
4. retain GPR observations only through p-1;
5. require p-1 to exist;
6. require >=24 monthly observations;
7. no later/current file substitution;
8. no old-method `gpr_web_latest.xlsx` substitution.

## Frozen execution range

Origins:
- 2021-10
- 2021-11
- 2021-12
- 2022-01
- 2022-02

Targets:
- 2021-11
- 2021-12
- 2022-01
- 2022-02
- 2022-03

The exact buildable subset is determined only by source availability/content.

## Model and alarm rules

Use the unchanged canonical ChHHO-ANFIS implementation and frozen 8-feature VW-MIDAS contract.

Evaluate unchanged A/C/D/E/G definitions. B remains warning-only.

No threshold tuning from these five months is permitted.

## Interpretation

This is a small-sample historical validation window. It can falsify a supposedly universal alarm mechanism if a clean false alarm occurs, but it cannot establish production-grade precision/recall on its own.

The earlier 2019-2021 backcast using `gpr_web_latest.xlsx` is invalidated and excluded.
