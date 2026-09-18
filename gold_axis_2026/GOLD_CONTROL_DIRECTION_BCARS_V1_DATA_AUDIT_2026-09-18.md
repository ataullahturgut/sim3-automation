# GOLD CONTROL — B-CARS TRUE OHLC DATA AUDIT

**Date:** 2026-09-18  
**Status:** `PASS_WITH_PRE2025_BOUNDARY_OBSERVATIONS`

- provider: Twelve Data
- symbol: XAU/USD
- provider interval: 1h
- timezone: America/New_York
- workflow run: `35378481735`
- artifact id: `10561586832`
- artifact digest: `sha256:bde1280ebb9dabc9a687ac3bb0ac48ef34d0648c0547de5397aa6e704b9e6806`
- weekly input CSV SHA-256: `e7048cb9e478495e8832486cac4f763260dbcca6ab329ef7f4fc5e8216a41d9b`
- unique validated hourly OHLC bars: 23,965
- weekly close anchors: 205
- weekly up-ratio rows: 204
- maximum decomposition identity absolute error: 6.94e-18
- production database writes: NONE

The modeled sample begins at target week 2022-03-07.

Two exact pre-2025 boundary observations are present:
- 2022-08-15: ur=0
- 2024-04-22: ur=0

Both boundary-week closes and their previous weekly closes match the governed Neon series `XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`; therefore the boundary values are treated as genuine data, not an extraction error.
