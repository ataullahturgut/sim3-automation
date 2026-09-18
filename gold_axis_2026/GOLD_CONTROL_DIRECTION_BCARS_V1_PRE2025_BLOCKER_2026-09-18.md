# GOLD CONTROL — DIRECTION_BCARS_V1_RESEARCH PRE-2025 BLOCKER

**Date:** 2026-09-18  
**Identity:** `DIRECTION_BCARS_V1_RESEARCH`  
**Status:** `BLOCKED_PRE2025_BOUNDARY_SUPPORT / NOT_SCORED / NOT_PROMOTED`

## Finding

The true Twelve Data XAU/USD 1h OHLC research artifact produces two exact boundary up-ratios inside the modeled pre-2025 sample:

- target week 2022-08-15: `ur=0.0`;
- target week 2024-04-22: `ur=0.0`.

These are not close-axis mismatches. The weekly closes on both weeks and their immediately preceding weeks match the governed `XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1` weekly close axis exactly.

The source high adjustment `H_t^a=max(H_t,C_(t-1))` therefore legitimately gives `u_t=0` in those weeks because the prior weekly close was not exceeded over the subsequent weekly interval.

## Consequence

The benchmark B-CARS likelihood uses an ordinary Beta density whose support is the open interval `(0,1)`. Exact `ur=0` is therefore outside the likelihood support.

The preregistered B-CARS V1 contract explicitly forbids silent clipping and requires fail-closed behavior when a modeled up-ratio equals 0 or 1.

Therefore:

`DIRECTION_BCARS_V1_RESEARCH = BLOCKED_PRE2025_BOUNDARY_SUPPORT`.

No 2025 model scoring was performed under this identity.

A boundary-safe successor may be separately preregistered using only this pre-2025 finding.
