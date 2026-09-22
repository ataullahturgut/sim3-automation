# GOLD CONTROL — FAST SQRT-CLOCK RECON V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** FAST_SQRT_CLOCK_RECON_V1_RESEARCH  
**Parent:** DOWNSIDE_UP_COUNTERSIGN_VETO_V2_FULLHISTORY_RESEARCH  
**Runtime authority:** NONE  
**Production writes:** FORBIDDEN

## Purpose

The frozen historical FAST engine uses the Twelve Data-derived NY17 daily series. During V2 alignment audit, that daily target axis does not match the SQRT parent axis on all parent-alarm rows because the SQRT parent retains only New York-local weekdays with at least 240 five-minute bars.

This successor asks whether the **unchanged FAST state logic**, applied to the exact SQRT daily-close clock, has useful counter-sign value.

This is a reconstruction, not the original FAST output.

## Frozen construction

Input daily close panel is exactly the parent SQRT source:

- table: public.xau_intraday_research_cache_5m;
- timezone: America/New_York;
- weekdays only;
- retain day iff count(*) >= 240;
- daily close = last observed close by observation_ts.

State logic is unchanged from Gold R4 FAST:

- SMA20;
- compare close[t-1] with SMA20[t-1];
- compare close[t] with SMA20[t];
- ROBUST_UP iff both comparisons are UP;
- ROBUST_DOWN iff both comparisons are DOWN;
- otherwise MIXED.

No threshold, window or persistence change is permitted.

## Evaluation

Primary: exact SQRT alarm origins in 2023–2024.

Stress: unchanged 2025 SQRT alarm origins.

Veto rule:
- if reconstructed FAST state == ROBUST_UP, suppress the forced-DOWN interpretation;
- otherwise retain it.

Metrics:
- GOOD_VETO;
- BAD_VETO;
- veto precision;
- false-alarm reduction;
- true-DOWN retention;
- remaining forced-DOWN precision;
- net veto benefit.

The same safety criterion from V2 applies:
- true-DOWN retention >= 0.80;
- at least 3 vetoes for useful action support.

2025 cannot tune or rescue the pre-2025 result.
