# GOLD CONTROL — DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH 2025 VOLATILITY OVERLAY

**Date:** 2026-09-18  
**Identity:** `DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH`  
**Status:** `FROZEN_EVENT_OVERLAY_COMPLETE`  
**Pre-2025 checkpoint commit:** `c08455979092d4641b972da67c3ae73964c4bb15`  
**2025 forecast freeze commit:** `5796969efc503ec1c9ee09513fbe5a3909dd6f63`

The complete corrected 2025 forecast table was frozen before this event inventory was applied. No model is refit and no cutoff, window, threshold or input is changed here.

| Window | Correct | Raw | Balanced | UP events | DOWN events | EXTREME | Event forecasts UP/DOWN |
|---|---:|---:|---:|---:|---:|---:|---:|
| 26 | 12/19 | 63.16% | 42.86% | 12/14 | 0/5 | 2/5 | 17/2 |
| 52 | 12/19 | 63.16% | 49.29% | 11/14 | 1/5 | 2/5 | 15/4 |
| 104 | 14/19 | 73.68% | 69.29% | 11/14 | 3/5 | 3/5 | 13/6 |

## Interpretation

- k=26 misses all 5 DOWN events.
- k=52 matches 1/5 DOWN events.
- k=104 matches 3/5 DOWN events and reaches 69.29% event-direction balanced accuracy.
- The k=104 event subset does not establish standalone promotion: its locked 2025 weekly accuracy is 61.54%, weekly balanced accuracy 55.14%, and weekly DOWN sensitivity 40%, all evaluated against a 71.15% always-UP raw baseline.
- The event overlay is downstream diagnostic evidence only and cannot select the window after the fact.

No post-overlay tuning is authorized under V2.
