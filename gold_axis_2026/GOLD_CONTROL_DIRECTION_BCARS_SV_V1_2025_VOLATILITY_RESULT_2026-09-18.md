# GOLD CONTROL — DIRECTION_BCARS_SV_V1_RESEARCH 2025 VOLATILITY OVERLAY

**Date:** 2026-09-18  
**Identity:** `DIRECTION_BCARS_SV_V1_RESEARCH`  
**Status:** `FROZEN_EVENT_OVERLAY_COMPLETE / NO_PROMOTION`  
**Forecast table frozen before overlay:** `GOLD_CONTROL_DIRECTION_BCARS_SV_V1_2025_WEEKLY_FORECASTS_2026-09-18.csv`  
**Locked 2025 result frozen before overlay:** `GOLD_CONTROL_DIRECTION_BCARS_SV_V1_2025_RESULT_2026-09-18.md`  
**Event authority:** `GOLD_CONTROL_2025_VOLATILITY_CHALLENGE_CONTRACT_V1_2026-09-15.md`

## Overlay rule

No model is refit here. Each frozen event is mapped to its Monday-start target week and compared with the B-CARS-SV weekly direction already frozen for that week.

The event inventory is not an input to the model and does not select a more favorable forecast origin, threshold, model order or transformation.

B-CARS-SV is a weekly direction model, not a volatility-event detector. This overlay measures direction agreement only.

## Aggregate result

- event-days = 19
- correct event directions = 14
- raw event-direction agreement = 14/19 = 73.68%
- event-direction balanced accuracy = 50.00%
- UP event agreement = 14/14 = 100.00%
- DOWN event agreement = 0/5 = 0.00%
- EXTREME event agreement = 2/5 = 40.00%
- MAJOR-only event agreement = 12/14 = 85.71%

## Event-by-event frozen comparison

| Event | Tier | z | Event dir. | Target week | k(raw) | P_ext(UP) | Forecast | Match |
|---|---|---:|---|---|---:|---:|---|---|
| 2025-02-10 | MAJOR | 2.3407 | UP | 2025-02-10 | 0.5257 | 0.5349 | UP | YES |
| 2025-02-14 | MAJOR | -2.2468 | DOWN | 2025-02-10 | 0.5257 | 0.5349 | UP | NO |
| 2025-02-18 | MAJOR | 2.1885 | UP | 2025-02-17 | 0.5171 | 0.5232 | UP | YES |
| 2025-03-13 | MAJOR | 2.1237 | UP | 2025-03-10 | 0.5369 | 0.5509 | UP | YES |
| 2025-04-04 | EXTREME | -3.3930 | DOWN | 2025-03-31 | 0.5929 | 0.6329 | UP | NO |
| 2025-04-09 | EXTREME | 3.2185 | UP | 2025-04-07 | 0.5859 | 0.6227 | UP | YES |
| 2025-04-10 | MAJOR | 2.3440 | UP | 2025-04-07 | 0.5859 | 0.6227 | UP | YES |
| 2025-07-21 | MAJOR | 2.0611 | UP | 2025-07-21 | 0.5655 | 0.5924 | UP | YES |
| 2025-08-01 | MAJOR | 2.5481 | UP | 2025-07-28 | 0.5641 | 0.5905 | UP | YES |
| 2025-09-02 | MAJOR | 2.6673 | UP | 2025-09-01 | 0.5792 | 0.6118 | UP | YES |
| 2025-09-22 | MAJOR | 2.6254 | UP | 2025-09-22 | 0.5974 | 0.6387 | UP | YES |
| 2025-09-29 | MAJOR | 2.3040 | UP | 2025-09-29 | 0.6037 | 0.6482 | UP | YES |
| 2025-10-06 | MAJOR | 2.7911 | UP | 2025-10-06 | 0.6125 | 0.6615 | UP | YES |
| 2025-10-13 | MAJOR | 2.5043 | UP | 2025-10-13 | 0.6184 | 0.6705 | UP | YES |
| 2025-10-16 | MAJOR | 2.9074 | UP | 2025-10-13 | 0.6184 | 0.6705 | UP | YES |
| 2025-10-17 | MAJOR | -2.0589 | DOWN | 2025-10-13 | 0.6184 | 0.6705 | UP | NO |
| 2025-10-21 | EXTREME | -4.1054 | DOWN | 2025-10-20 | 0.6204 | 0.6738 | UP | NO |
| 2025-12-22 | EXTREME | 4.0174 | UP | 2025-12-22 | 0.5994 | 0.6429 | UP | YES |
| 2025-12-29 | EXTREME | -6.6415 | DOWN | 2025-12-29 | 0.6083 | 0.6562 | UP | NO |

## Interpretation

The high raw event agreement is mechanically driven by the event-direction class balance. B-CARS-SV forecasts UP on all 19 event weeks, therefore it matches all 14 UP events and misses all 5 DOWN events.

The event-direction balanced accuracy is exactly 50%, and none of the five DOWN abnormal-volatility events is anticipated directionally.

The overlay therefore provides no evidence of useful abnormal-move direction discrimination.

## Decision

Binding status remains:

`EVALUATED / NO_PROMOTION / PRE2025_VALIDATION_FAILED / WEAK_DIRECTIONAL_DISCRIMINATION`.

The small positive 2025 continuous up-ratio R2_oos is retained as a descriptive continuous-forecast result only; it does not justify promotion as a direction motor.
