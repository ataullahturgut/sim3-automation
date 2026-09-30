# GOLD MONTHLY — ChHHO Pre-DEV Current-Method GPR V2 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS  
**Workflow run:** 36688284811  
**Artifact:** 11084467079  
**Code commit:** `574f82130fe8b8518b2285c1d7798cabf629c836`  
**Authority commit:** `ae009acc67cbf22c3cd6edaa7e934067823db260`

## Source validity

This V2 run uses the same current GPR methodology family as the canonical 2022+ project:

- official repository: `iacoviel/iacoviel.github.io`
- file: `gpr_files/data_gpr_export.xls`
- official Git history exists from 2021-10-18 onward;
- each origin uses the latest commit available by that origin month-end;
- no later/current file substitution;
- no old-method `gpr_web_latest.xlsx`.

All five requested origins passed the PIT source audit.

## Buildable origins and GPR values

| Origin | Required GPR month | PIT GPR | Official commit |
|---|---|---:|---|
| 2021-10 | 2021-09 | 70.5319 | 5e4dfbf… (2021-10-18) |
| 2021-11 | 2021-10 | 72.1815 | ffbfc5d… (2021-11-18) |
| 2021-12 | 2021-11 | 83.9910 | 3e4a193… (2021-12-21) |
| 2022-01 | 2021-12 | 99.9942 | 8c7040e… (2022-01-12) |
| 2022-02 | 2022-01 | 108.9659 | 2eb0c21… (2022-02-01) |

For sanity, later canonical CORE5 values for those months are 80.70, 79.03, 86.57, 105.35 and 138.67 respectively. The differences are plausible vintage revisions and are materially unlike the invalid old-method 2020 example (333 vs 138).

## ChHHO results

| Target | Origin | AE USD | APE | A | C | D | E | G |
|---|---|---:|---:|---|---|---|---|---|
| 2021-11 | 2021-10 | 8.41 | 0.46% | 0 | 0 | 0 | 0 | 0 |
| 2021-12 | 2021-11 | **85.62** | **4.78%** | 0 | 0 | 0 | 0 | 0 |
| 2022-01 | 2021-12 | 52.16 | 2.87% | 0 | 0 | 0 | 0 | 0 |
| 2022-02 | 2022-01 | 49.67 | 2.68% | 0 | 0 | 0 | 0 | 0 |
| 2022-03 | 2022-02 | 12.46 | 0.64% | 0 | 0 | 0 | 0 | 0 |

Frozen AE high-error threshold = 63.06 USD.

Summary:
- n = 5
- high-error months = 1
- hard alarms = 0
- hits = 0
- false alarms = 0
- misses = 1

The one high-error month is **2021-12**, and none of A/C/D/E/G fired.

## Interpretation

This is the only currently admissible same-methodology pre-DEV ChHHO window.

It is too small to estimate alarm precision/recall reliably. It does show that the alarm set is not exhaustive: a high-error ChHHO month can occur with none of A/C/D/E/G active.

It does **not** falsify A/C/D/E/G because none of those mechanisms generated an event in this five-origin window.

The earlier 21-origin V1 run is invalidated and excluded because it used the old GPR methodology.

## Reconciliation assurance

Separate run 36687542392 demonstrated that the backcast helper reproduces canonical ChHHO features, predictions, train-row counts and diagnostics exactly when supplied with canonical GPR vintages.

Therefore the remaining limitation is historical source coverage, not model-code divergence.
