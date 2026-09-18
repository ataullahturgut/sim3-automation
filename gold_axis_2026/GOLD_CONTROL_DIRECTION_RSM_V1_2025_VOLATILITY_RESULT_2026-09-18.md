# GOLD CONTROL — DIRECTION_RSM_V1_RESEARCH 2025 VOLATILITY OVERLAY

**Date:** 2026-09-18  
**Identity:** `DIRECTION_RSM_V1_RESEARCH`  
**Forecast table frozen before overlay:** `GOLD_CONTROL_DIRECTION_RSM_V1_2025_WEEKLY_FORECASTS_2026-09-18.csv`  
**Event authority:** `GOLD_CONTROL_2025_VOLATILITY_CHALLENGE_CONTRACT_V1_2026-09-15.md`

## Overlay rule

Each frozen event date is mapped to its Monday-start calendar week. The RSM direction used is the weekly forecast already frozen for that target week and issued from the prior week's last actual governed close. Event dates did not select or alter forecast origins.

RSM is a weekly direction model, not a volatility-alarm engine. This overlay measures only whether its pre-week direction agreed with the abnormal daily move direction. It is not volatility-event recall or alarm precision.

## Results

- event-days: 19
- raw event-direction agreement: 73.68%
- event-direction balanced accuracy: 50.00%
- UP event agreement: 100.00%
- DOWN event agreement: 0.00%
- EXTREME event agreement: 40.00%
- MAJOR-only event agreement: 85.71%
- lead from frozen weekly origin to event date: median 4 calendar days, range 3-7

## Interpretation

The raw event-direction agreement is mechanically high because the frozen RSM-52 forecast is UP for every 2025 target week. The event inventory contains 14 UP and 5 DOWN events. Consequently RSM matches every UP event and misses every DOWN event, producing event-direction balanced accuracy of 50%.

This overlay provides no evidence that RSM-52 anticipates the direction of abnormal-volatility events. It must not be called volatility-event prediction accuracy because RSM predicts weekly return direction and emits a direction every week rather than an event/no-event alarm.
