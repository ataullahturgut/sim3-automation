# GOLD SHORT-HORIZON GLOBAL XAU — Existing Source Bridge Screen Result

**Date:** 2026-10-01  
**Status:** **COMPLETE / NO LIVE BRIDGE PASS**  
**Workflow:** Gold Short Horizon Existing XAU Source Bridge  
**Run:** **36911112098**  
**Artifact:** **11186955894**  
**Artifact digest:** `sha256:890478209702b535a4f718a89a67cedc0a5d4d4c5a8f0210cb948c2406570acd`  
**Authority:** `GOLD_SHORT_HORIZON_GLOBAL_XAU_SOURCE_BRIDGE_SCREEN_AUTHORITY_2026-10-01.md`

## Existing XAU series

- Historical development:
  - `XAU_STAKTRAKR_RESEARCH_DAILY_R1`
  - 4,230 rows
  - 2010-01-04 .. 2026-07-31.

- Live candidate 1:
  - `XAU_EOD_TWELVE_NY17`
  - 497 rows
  - 2021-09-01 .. 2026-09-30.

- Live candidate 2:
  - `XAU_DAILY_XAUS`
  - 143 rows
  - 2026-03-11 .. 2026-10-01
  - current source identity: Yahoo Finance GC=F
  - status: CANDIDATE_NOT_BENCHMARK.

## Bridge metrics

| Candidate | Common return pairs | Pearson | Spearman | Sign agreement | Return-diff SD | Reference gate |
|---|---:|---:|---:|---:|---:|---|
| XAU_EOD_TWELVE_NY17 | 441 | **0.9375** | 0.5443 | 65.3% | 1.049% | FAIL |
| XAU_DAILY_XAUS | 98 | 0.7320 | 0.6568 | 74.5% | 1.200% | FAIL |

NY17 is the closer of the two existing live candidates, but it does not pass same-target equivalence under the frozen bridge gate.

Therefore:
- do not stitch either live series into the historical development target;
- historical global-XAU development remains valid as retrospective research;
- prospective live extension remains a separate unresolved authority issue.

This does not invalidate Stage 1 or Stage 2 DEV evidence because those stages use the historical target consistently and do not splice sources.
