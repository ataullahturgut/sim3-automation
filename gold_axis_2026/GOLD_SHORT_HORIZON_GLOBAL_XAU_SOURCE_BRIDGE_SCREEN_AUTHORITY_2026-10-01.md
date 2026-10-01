# GOLD SHORT-HORIZON GLOBAL XAU — Existing Source Bridge Screen Authority

**Date:** 2026-10-01
**Status:** FROZEN PRE-RUN

## Goal

Select the best already-existing global XAU live/operational extension for the long historical XAU target.

Historical anchor:
- XAU_STAKTRAKR_RESEARCH_DAILY_R1
- calendar-date label semantics
- 2010-01-04 onward.

Candidate existing global XAU series:
- XAU_EOD_TWELVE_NY17
- XAU_DAILY_XAUS.

No BIST series.
No GLDM/MGC target.
No new external source.

## Date semantics

- StakTrakr historical XAU: use observation_ts UTC calendar date as the source date label.
- NY17: use America/New_York trade date derived from the true 17:00 ET timestamp.
- XAU_DAILY_XAUS: use its observation_ts calendar date as stored by the daily history pipeline.

No lag search is allowed for selection.

## Metrics

On exact common dates:
- common return pairs
- Pearson daily log-return correlation
- Spearman daily log-return correlation
- sign agreement
- mean absolute return difference
- return-difference SD
- median level ratio
- level-ratio coefficient of variation.

## Preferred bridge rule

Choose the candidate with:
1. at least 60 common return pairs;
2. highest Pearson daily-return correlation;
3. if Pearson differs by <=0.01, higher sign agreement;
4. report but do not post-hoc lower any quality gate.

Reference quality gate:
- Pearson >=0.90
- sign agreement >=80%
- return-difference SD <=0.75%.

If no candidate meets the reference quality gate:
- historical XAU may still be used for retrospective model development,
- but prospective live extension remains unresolved and must not be silently stitched.

2025 remains frozen for model selection.
