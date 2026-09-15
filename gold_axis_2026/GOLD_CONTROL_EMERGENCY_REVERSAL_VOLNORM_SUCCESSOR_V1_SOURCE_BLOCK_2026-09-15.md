# GOLD CONTROL — EMERGENCY REVERSAL VOLNORM SUCCESSOR V1 SOURCE BLOCK

**Date:** 2026-09-15  
**Identity:** `EMERGENCY_REVERSAL_VOLNORM_SUCCESSOR_V1`  
**Status:** `BLOCKED_DATA_COVERAGE_NO_2025_REPLAY`

The V1 preregistration froze the selected Twelve Data `XAU/USD` 1-hour bar opened at `16:00:00` America/New_York and required at least 90% weekday coverage in each complete formation year before any 2025 replay.

The guarded formation run stopped before 2025 because the frozen source gate failed:

| Year | Selected 16:00 closes | Calendar weekdays | Coverage |
|---|---:|---:|---:|
| 2022 | 238 | 260 | 91.54% |
| 2023 | 224 | 260 | **86.15%** |
| 2024 | 245 | 262 | 93.51% |

The 2023 coverage is below the frozen 90% gate. The gate was not relaxed and missing bars were not interpolated, forward-filled or substituted after failure.

Unit tests and the pre-2025 boundary check had passed before the source gate stopped the run. No 2025 observation, 2025 volatility event or 2025 performance result was consumed by V1 formation/model selection.

V1 is therefore closed as `BLOCKED_DATA_COVERAGE_NO_2025_REPLAY`.

A separate pre-2025 source-discovery probe was allowed because it used only 2022–2024 provider data and did not score the detector on 2025. That probe found that the fixed 14:00 ET hourly close has materially better formation coverage and remains very close to the originally intended 16:00 hourly close on overlapping dates. Any use of 14:00 must occur under a separately named successor with a new source preregistration; it may not be silently substituted into V1.
