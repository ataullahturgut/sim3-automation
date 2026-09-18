# GOLD CONTROL — DIRECTION_VLMC_BS_V1_RESEARCH 2025 VOLATILITY OVERLAY

**Date:** 2026-09-18  
**Identity:** `DIRECTION_VLMC_BS_V1_RESEARCH`  
**Status:** `FROZEN_EVENT_OVERLAY_COMPLETE / NO_PROMOTION`  
**Forecast table frozen before overlay:** `GOLD_CONTROL_DIRECTION_VLMC_BS_V1_2025_WEEKLY_FORECASTS_2026-09-18.csv`  
**Locked 2025 result frozen before overlay:** `GOLD_CONTROL_DIRECTION_VLMC_BS_V1_2025_RESULT_2026-09-18.md`  
**Event authority:** `GOLD_CONTROL_2025_VOLATILITY_CHALLENGE_CONTRACT_V1_2026-09-15.md`

## 1. Overlay rule

No model is refit here.

Each frozen abnormal-volatility event is mapped to its Monday-start target week. The direction used is the VLMC-BS weekly forecast already frozen for that week and issued from the prior week's last actual governed close.

Event dates do not select a more favorable origin, cutoff, context, threshold or probability.

VLMC-BS is a weekly direction model, not an event/no-event volatility detector. Therefore this overlay measures only whether the pre-existing weekly direction agreed with each abnormal daily move direction.

## 2. Aggregate result

- event-days = 19
- correct event directions = 11
- raw event-direction agreement = 11/19 = 57.89%
- event-direction balanced accuracy = 45.71%
- UP event agreement = 10/14 = 71.43%
- DOWN event agreement = 1/5 = 20.00%
- EXTREME event agreement = 1/5 = 20.00%
- MAJOR-only event agreement = 10/14 = 71.43%
- lead from frozen weekly origin to event date = median 4 calendar days, range 3-7 days

## 3. Event-by-event frozen comparison

| Event | Tier | z | Event dir. | Frozen origin | Lead | K* | P(UP) | VLMC dir. | Match |
|---|---|---:|---|---|---:|---:|---:|---|---|
| 2025-02-10 | MAJOR | 2.3407 | UP | 2025-02-07 | 3d | 0.44 | 0.7500 | UP | YES |
| 2025-02-14 | MAJOR | -2.2468 | DOWN | 2025-02-07 | 7d | 0.44 | 0.7500 | UP | NO |
| 2025-02-18 | MAJOR | 2.1885 | UP | 2025-02-14 | 4d | 0.40 | 1.0000 | UP | YES |
| 2025-03-13 | MAJOR | 2.1237 | UP | 2025-03-07 | 6d | 0.86 | 1.0000 | UP | YES |
| 2025-04-04 | EXTREME | -3.3930 | DOWN | 2025-03-28 | 7d | 0.68 | 0.8000 | UP | NO |
| 2025-04-09 | EXTREME | 3.2185 | UP | 2025-04-04 | 5d | 0.40 | 1.0000 | UP | YES |
| 2025-04-10 | MAJOR | 2.3440 | UP | 2025-04-04 | 6d | 0.40 | 1.0000 | UP | YES |
| 2025-07-21 | MAJOR | 2.0611 | UP | 2025-07-18 | 3d | 1.42 | 0.0000 | DOWN | NO |
| 2025-08-01 | MAJOR | 2.5481 | UP | 2025-07-25 | 7d | 1.40 | 0.6000 | UP | YES |
| 2025-09-02 | MAJOR | 2.6673 | UP | 2025-08-29 | 4d | 0.52 | 0.5000 | UP | YES |
| 2025-09-22 | MAJOR | 2.6254 | UP | 2025-09-19 | 3d | 0.40 | 1.0000 | UP | YES |
| 2025-09-29 | MAJOR | 2.3040 | UP | 2025-09-26 | 3d | 1.06 | 0.6346 | UP | YES |
| 2025-10-06 | MAJOR | 2.7911 | UP | 2025-10-03 | 3d | 0.82 | 1.0000 | UP | YES |
| 2025-10-13 | MAJOR | 2.5043 | UP | 2025-10-10 | 3d | 0.70 | 0.0000 | DOWN | NO |
| 2025-10-16 | MAJOR | 2.9074 | UP | 2025-10-10 | 6d | 0.70 | 0.0000 | DOWN | NO |
| 2025-10-17 | MAJOR | -2.0589 | DOWN | 2025-10-10 | 7d | 0.70 | 0.0000 | DOWN | YES |
| 2025-10-21 | EXTREME | -4.1054 | DOWN | 2025-10-17 | 4d | 1.12 | 0.7143 | UP | NO |
| 2025-12-22 | EXTREME | 4.0174 | UP | 2025-12-19 | 3d | 1.34 | 0.0000 | DOWN | NO |
| 2025-12-29 | EXTREME | -6.6415 | DOWN | 2025-12-26 | 3d | 0.82 | 0.6667 | UP | NO |

## 4. Interpretation

The volatility overlay does not confirm the more encouraging two-sided behavior seen in the complete weekly 2025 test.

Across all 2025 weeks, VLMC-BS achieved 59.03% balanced accuracy and captured 6/16 DOWN weeks. On the frozen abnormal-volatility subset, however:
- only 1 of 5 DOWN event-days is directionally correct;
- only 1 of 5 EXTREME event-days is directionally correct;
- event-direction balanced accuracy falls to 45.71%.

The one correctly anticipated DOWN event is 2025-10-17. The model misses the DOWN events on 2025-02-14, 2025-04-04, 2025-10-21 and 2025-12-29.

This result must not be interpreted as volatility-event precision/recall because the model issues a weekly direction every week and does not predict whether a volatility event will occur.

## 5. Decision

The event overlay provides no basis for promotion.

The binding interpretation remains:
`EVALUATED / NO_PROMOTION / PRE2025_VALIDATION_FAILED`.

The 2025 weekly replay is retained as evidence that VLMC-BS can produce two-sided signals unlike RSM-52, but:
- 2024 validation failed;
- 2025 raw accuracy did not beat always-UP;
- probability calibration is poor;
- volatility-event direction performance is weak.

No post-2025 smoothing, cutoff rescue, window change or event-conditioned tuning is authorized under V1.
