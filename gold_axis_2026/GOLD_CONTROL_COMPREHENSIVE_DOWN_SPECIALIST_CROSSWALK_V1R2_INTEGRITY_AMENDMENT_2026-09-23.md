# GOLD CONTROL — COMPREHENSIVE DOWN-SPECIALIST CROSSWALK V1R2 INTEGRITY AMENDMENT

**Date:** 2026-09-23  
**Successor identity:** `COMPREHENSIVE_DOWN_SPECIALIST_CROSSWALK_V1R2_RESEARCH`  
**Parent preregistration:** `COMPREHENSIVE_DOWN_SPECIALIST_CROSSWALK_V1_RESEARCH` at commit `1a2a445c239f9f4674aa2fd7f303b11fbd43bbe6`.

## Why V1 was blocked

The V1 integrity gate found that V1.53's exact-NY17 target sign does not map one-to-one onto the SQRT parent target-day sign on the attempted date join. The first mismatch list began with:

- 2024-04-16
- 2025-05-01
- 2025-05-02
- 2025-05-07
- 2025-05-13

Therefore V1.53 and the SQRT parent are not proven to share the same target clock under a simple `target_date` join.

The V1 run is **BLOCKED** and its V1.53 crosswalk numbers are non-authoritative.

## R2 correction

R2 makes one integrity-only change:

- all V1.53 candidates and the moderate-downshock diagnostic are removed from candidate scoring;
- V1.53 is recorded as `NOT_PROVEN_TARGET_CLOCK_ALIGNMENT`;
- no V1.53 output may influence candidate eligibility, ranking, 2025 transport, or conclusions.

This is not a performance-based exclusion. It is required because same-clock target identity failed.

All other candidate families, frozen rules, thresholds, support requirements and screen-positive criteria remain unchanged from V1:

- Cross-domain V1;
- CBR-DTW path V1;
- S&P 500 cross-market V1;
- heterogeneous consensus V1.

The previous narrow-baseline audit remains carried forward as a separate negative screen.

## Integrity

R2 must still reproduce:

- primary unresolved subset 26 = 13 DOWN + 13 UP;
- locked 2025 unresolved subset 74 = 39 DOWN + 35 UP;
- Router V2 frozen annual counts;
- cross-domain target sign;
- original full-2024 CBR/SP500/consensus aggregate outputs.

Any failure among those retained same-clock sources blocks R2.

## Governance

No threshold, candidate rule, metric or 2025 selection rule changed after seeing V1 outcomes. The only change is removal of a source whose target-clock identity failed the preregistered integrity test.
