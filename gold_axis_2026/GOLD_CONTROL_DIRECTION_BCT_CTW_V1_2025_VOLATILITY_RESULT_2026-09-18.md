# GOLD CONTROL — DIRECTION_BCT_CTW_V1_RESEARCH 2025 VOLATILITY OVERLAY

**Date:** 2026-09-18  
**Identity:** `DIRECTION_BCT_CTW_V1_RESEARCH`  
**Status:** `FROZEN_EVENT_OVERLAY_COMPLETE / NO_PROMOTION`  
**Forecast table frozen before overlay:** `GOLD_CONTROL_DIRECTION_BCT_CTW_V1_2025_WEEKLY_FORECASTS_2026-09-18.csv`  
**Locked 2025 result frozen before overlay:** `GOLD_CONTROL_DIRECTION_BCT_CTW_V1_2025_RESULT_2026-09-18.md`  
**Event authority:** `GOLD_CONTROL_2025_VOLATILITY_CHALLENGE_CONTRACT_V1_2026-09-15.md`

## Overlay rule

No BCT/CTW parameter is changed here. Each event is mapped to its Monday-start target week and compared with the weekly direction already frozen for that week from the prior week's last actual governed close.

The event list does not select forecast origins and is not an input to BCT/CTW.

BCT/CTW is a weekly direction model, not a volatility-event detector. This overlay is direction agreement only.

## Aggregate result

- event-days = 19
- correct event directions = 14
- raw event-direction agreement = 73.68%
- event-direction balanced accuracy = 50.00%
- UP event agreement = 14/14 = 100.00%
- DOWN event agreement = 0/5 = 0.00%
- EXTREME event agreement = 2/5 = 40.00%
- MAJOR-only event agreement = 12/14 = 85.71%
- lead from frozen weekly origin to event date = median 4 calendar days, range 3-7

## Event-by-event frozen comparison

| Event | Tier | z | Event dir. | Frozen origin | Lead | P(UP) | BCT dir. | Match |
|---|---|---:|---|---|---:|---:|---|---|
| 2025-02-10 | MAJOR | 2.3407 | UP | 2025-02-07 | 3d | 0.5472 | UP | YES |
| 2025-02-14 | MAJOR | -2.2468 | DOWN | 2025-02-07 | 7d | 0.5472 | UP | NO |
| 2025-02-18 | MAJOR | 2.1885 | UP | 2025-02-14 | 4d | 0.5895 | UP | YES |
| 2025-03-13 | MAJOR | 2.1237 | UP | 2025-03-07 | 6d | 0.5821 | UP | YES |
| 2025-04-04 | EXTREME | -3.3930 | DOWN | 2025-03-28 | 7d | 0.6428 | UP | NO |
| 2025-04-09 | EXTREME | 3.2185 | UP | 2025-04-04 | 5d | 0.6025 | UP | YES |
| 2025-04-10 | MAJOR | 2.3440 | UP | 2025-04-04 | 6d | 0.6025 | UP | YES |
| 2025-07-21 | MAJOR | 2.0611 | UP | 2025-07-18 | 3d | 0.5813 | UP | YES |
| 2025-08-01 | MAJOR | 2.5481 | UP | 2025-07-25 | 7d | 0.6090 | UP | YES |
| 2025-09-02 | MAJOR | 2.6673 | UP | 2025-08-29 | 4d | 0.6077 | UP | YES |
| 2025-09-22 | MAJOR | 2.6254 | UP | 2025-09-19 | 3d | 0.6641 | UP | YES |
| 2025-09-29 | MAJOR | 2.3040 | UP | 2025-09-26 | 3d | 0.6853 | UP | YES |
| 2025-10-06 | MAJOR | 2.7911 | UP | 2025-10-03 | 3d | 0.6883 | UP | YES |
| 2025-10-13 | MAJOR | 2.5043 | UP | 2025-10-10 | 3d | 0.7134 | UP | YES |
| 2025-10-16 | MAJOR | 2.9074 | UP | 2025-10-10 | 6d | 0.7134 | UP | YES |
| 2025-10-17 | MAJOR | -2.0589 | DOWN | 2025-10-10 | 7d | 0.7134 | UP | NO |
| 2025-10-21 | EXTREME | -4.1054 | DOWN | 2025-10-17 | 4d | 0.7345 | UP | NO |
| 2025-12-22 | EXTREME | 4.0174 | UP | 2025-12-19 | 3d | 0.6290 | UP | YES |
| 2025-12-29 | EXTREME | -6.6415 | DOWN | 2025-12-26 | 3d | 0.6616 | UP | NO |

## Interpretation

The raw event-direction agreement is mechanically driven by the class balance because BCT/CTW forecast UP for every 2025 target week.

The frozen event inventory contains 14 UP and 5 DOWN event-days. BCT/CTW therefore matches all 14 UP events and misses all 5 DOWN events, yielding 73.68% raw agreement but exactly 50% balanced event-direction accuracy.

The probability layer is much better behaved than VLMC-BS, but this does not translate into DOWN classification under the frozen 0.5 rule.

This overlay provides no evidence that BCT/CTW V1 predicts abnormal-move direction or volatility-event occurrence.

## Decision

The event overlay does not support promotion.

Binding status:
`EVALUATED / NO_PROMOTION / WEAK_DIRECTIONAL_DISCRIMINATION`.

No post-2025 threshold shift, alternate D, NO_SIGNAL band or context augmentation is authorized under V1.
