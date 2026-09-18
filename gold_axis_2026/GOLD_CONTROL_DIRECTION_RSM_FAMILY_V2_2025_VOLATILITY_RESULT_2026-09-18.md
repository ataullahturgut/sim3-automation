# GOLD CONTROL — DIRECTION_RSM_FAMILY_V2_RESEARCH 2025 VOLATILITY OVERLAY

**Date:** 2026-09-18  
**Identity:** `DIRECTION_RSM_FAMILY_V2_RESEARCH`  
**Status:** `FROZEN_EVENT_OVERLAY_COMPLETE / NO_PROMOTION`  
**RSM forecasts frozen before overlay:** `GOLD_CONTROL_DIRECTION_RSM_FAMILY_V2_2025_RSM_FORECASTS_2026-09-18.csv`  
**ERSM forecasts frozen before overlay:** `GOLD_CONTROL_DIRECTION_RSM_FAMILY_V2_2025_ERSM_FORECASTS_2026-09-18.csv`  
**Locked 2025 family result frozen before overlay:** `GOLD_CONTROL_DIRECTION_RSM_FAMILY_V2_2025_RESULT_2026-09-18.md`

## Aggregate frozen overlay

| Variant | Correct | Raw | Balanced | UP events | DOWN events | EXTREME | Event forecasts UP/DOWN |
|---|---:|---:|---:|---:|---:|---:|---:|
| RSM-26 | 14/19 | 73.68% | 50.00% | 14/14 | 0/5 | 2/5 | 19/0 |
| RSM-52 | 14/19 | 73.68% | 50.00% | 14/14 | 0/5 | 2/5 | 19/0 |
| RSM-104 | 14/19 | 73.68% | 50.00% | 14/14 | 0/5 | 2/5 | 19/0 |
| ERSM-26 | 13/19 | 68.42% | 46.43% | 13/14 | 0/5 | 2/5 | 18/1 |
| ERSM-52 | 14/19 | 73.68% | 50.00% | 14/14 | 0/5 | 2/5 | 19/0 |
| ERSM-104 | 14/19 | 73.68% | 56.43% | 13/14 | 1/5 | 2/5 | 17/2 |

## Interpretation

The overlay does not change the locked weekly-family result.

All three RSM variants forecast UP on all 19 event weeks. Their 14/19 raw event agreement is therefore exactly the event-class imbalance: all 14 UP events match and all 5 DOWN events fail.

ERSM-26 emits one DOWN event-week forecast, but that forecast is on the 2025-07-21 UP event and is wrong. It captures 0/5 DOWN events.

ERSM-52 forecasts UP on all 19 event weeks and therefore behaves like the RSM variants on this overlay.

ERSM-104 emits two DOWN event-week forecasts. One is the week containing both the 2025-02-10 UP event and the 2025-02-14 DOWN event; a single weekly direction cannot match both daily events. It therefore records 13/14 UP-event agreement and 1/5 DOWN-event agreement, with balanced event-direction accuracy 56.43%. This isolated event-subset improvement is not evidence for promotion because:
- 2024 common-support balanced accuracy was only 47.50%;
- 2025 weekly balanced accuracy was only 41.89%;
- weekly 2025 DOWN sensitivity was 0/15;
- the event overlay is a downstream diagnostic, not a model-selection surface.

No family member demonstrates stable two-sided weekly direction discrimination.
