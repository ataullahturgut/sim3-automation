# GOLD CONTROL — EMERGENCY REVERSAL VOLNORM V2 CHALLENGE INVALIDATION

**Date:** 2026-09-15  
**Identity:** `EMERGENCY_REVERSAL_VOLNORM_SUCCESSOR_V2`  
**Invalidated run:** `35022855051`  
**Status:** `INVALID_SOURCE_GOVERNANCE_BUG_DO_NOT_SCORE`

The V2 preregistration and coverage language required **weekday closes**. The implementation selected every exact 14:00 ET provider bar without first restricting the selected calendar date to Monday–Friday.

The defect became visible immediately in the 2025 engine-stage accounting: the run reported 270 selected 2025 observations against only 261 calendar weekdays, proving that non-weekday provider bars had entered the state path.

Consequences:

- the 2025 V2 engine timeline hash `4b77f12dfd99e546e3f791d5a7101635a55d0c088dedf2b1e1c9b4d410e1f447` is invalid for governed evaluation;
- all alert counts and all volatility-overlay counts from run `35022855051` are **withdrawn and must not be used as performance evidence**;
- the V2 formation coverage accounting is also not sufficient evidence because its numerator could include non-weekday bars;
- no threshold, volatility window, state transition or reversal mathematics is being changed in response to the invalid result;
- the defect is a deterministic source-governance compliance correction, not outcome-based model tuning.

V2 is closed as `INVALID_SOURCE_GOVERNANCE_BUG_DO_NOT_SCORE`.

Before any corrected 2025 replay, source discovery/coverage must be rerun using 2022–2024 only with an explicit `Monday-Friday` filter. A separately named successor must freeze the corrected source contract and pass formation gates before 2025 is replayed again.
