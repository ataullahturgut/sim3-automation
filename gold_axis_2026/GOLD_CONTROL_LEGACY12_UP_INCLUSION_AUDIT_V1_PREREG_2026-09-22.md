# GOLD CONTROL — LEGACY 12 UP-INCLUSION AUDIT V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** LEGACY12_UP_INCLUSION_AUDIT_V1_RESEARCH  
**Runtime authority:** NONE  
**Production DB writes:** FORBIDDEN

## Purpose

Audit the original governed 12-engine Gold Control stack for UP/rebound usefulness before any new router excludes it.

The original stack is:
1. CAUSAL_PATCH
2. VW_MIDAS_MSVR_SUCCESSOR_V1
3. MOMENTUM_3M
4. RANDOM_WALK
5. MONTHLY_DIRECTION_3M
6. FAST
7. SLOW
8. MACRO_EVENT_SUCCESSOR_V2
9. BOCPD_RETURN_SUCCESSOR_V1
10. EMERGENCY_LEVEL
11. EMERGENCY_REVERSAL
12. GVZ_RISK

## Role preservation

The audit must not convert every engine into an equal next-day direction vote.

- FAST, SLOW and MONTHLY_DIRECTION_3M may be evaluated descriptively for next-day UP association because they have explicit UP states.
- CAUSAL_PATCH, VW_MIDAS_MSVR_SUCCESSOR_V1 and MOMENTUM_3M remain monthly H=1 experts; their retained monthly direction accuracy is reported separately.
- MACRO_EVENT_SUCCESSOR_V2 remains event-time direction only.
- GVZ_RISK remains risk context only.
- BOCPD_RETURN_SUCCESSOR_V1 remains regime/break context and blocked where the historical daily state is unavailable.
- EMERGENCY_LEVEL and EMERGENCY_REVERSAL remain context unless independent next-day direction performance is proven.
- RANDOM_WALK remains benchmark only.

## Same-clock reconstruction for FAST/SLOW/MONTHLY_DIRECTION_3M

To make their descriptive next-day association directly comparable with the modern daily UP experts, reconstruct only their frozen rules on the exact daily close axis already used by the TTSM/Bonato/logit next-day artifacts.

No parameter change is allowed.

FAST:
- SMA20;
- 2 completed daily observations persistence;
- ROBUST_UP iff t-1 and t are both above their own SMA20.

SLOW:
- completed weekly closes only;
- SMA4 weekly;
- 2 completed-week persistence;
- ROBUST_UP iff previous and current completed weekly closes are both above their respective SMA4.

MONTHLY_DIRECTION_3M:
- use only completed monthly closes before the current origin month;
- compute completed monthly returns;
- UP iff the mean of the last 3 completed monthly returns is > 0.

These reconstructions are descriptive research identities, not claims that the original stored historical runtime outputs existed on the same exact daily axis.

## Evaluation

Use exact next-day rows for 2023, 2024 and 2025.

For every explicit UP state:
- UP calls;
- true UP;
- false UP;
- UP precision;
- false-UP FPR = false UP / all actual DOWN;
- coverage;
- actual-UP recall.

No threshold tuning or post-result combination is permitted.

## Router V2 eligibility output

After scoring, classify each original engine as one of:

- DIRECT_UP_EXPERT_ELIGIBLE
- CONTEXT_ONLY_ELIGIBLE
- SPECIAL_CLOCK_ELIGIBLE
- BENCHMARK_ONLY
- BLOCKED_PRE2025_HISTORY
- NOT_PROVEN

This audit itself does not build a new selector or change Router V1.
