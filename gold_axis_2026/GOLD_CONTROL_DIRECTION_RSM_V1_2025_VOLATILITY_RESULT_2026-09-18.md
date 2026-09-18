# GOLD CONTROL — DIRECTION_RSM_V1_RESEARCH 2025 VOLATILITY OVERLAY

**Date:** 2026-09-18  
**Identity:** `DIRECTION_RSM_V1_RESEARCH`  
**Status:** `FROZEN_EVENT_OVERLAY_COMPLETE / NO_PROMOTION`  
**Forecast table frozen before overlay:** `GOLD_CONTROL_DIRECTION_RSM_V1_2025_WEEKLY_FORECASTS_2026-09-18.csv`  
**Overlay rows:** `GOLD_CONTROL_DIRECTION_RSM_V1_2025_VOLATILITY_OVERLAY_2026-09-18.csv`  
**Event authority:** `GOLD_CONTROL_2025_VOLATILITY_CHALLENGE_CONTRACT_V1_2026-09-15.md`

## 1. Model being overlaid

This overlay does not refit RSM.

The already-frozen weekly model is:

`p_up(w) = (1/52) * sum(x_(w-51), ..., x_w)`

with `x_w = 1[r_w > 0]`, using the prior 52 weekly return signs and forecasting UP when `p_up >= 0.5`.

The complete 52-row 2025 weekly forecast table was frozen before event dates were overlaid.

## 2. Overlay rule

For each frozen 2025 abnormal-volatility event:
1. map the event date to its Monday-start calendar week;
2. retrieve the RSM forecast already issued from the previous week's last actual governed close for that target week;
3. compare the frozen weekly RSM direction with the event-day direction;
4. do not search backward or forward for a more favorable RSM origin.

The volatility event dates therefore do not choose, alter or filter forecast origins.

RSM is a weekly direction model, not an event/no-event volatility alarm. This overlay measures only pre-existing direction agreement on abnormal-move dates. It is not volatility-event precision, recall or detection accuracy.

## 3. Aggregate results

- event-days = 19
- raw event-direction agreement = 14/19 = 73.68%
- event-direction balanced accuracy = 50.00%
- UP event agreement = 14/14 = 100.00%
- DOWN event agreement = 0/5 = 0.00%
- EXTREME event agreement = 2/5 = 40.00%
- MAJOR-only event agreement = 12/14 = 85.71%
- lead from frozen weekly origin to event date = median 4 calendar days, range 3-7 days

## 4. Event-by-event frozen comparison

| Event date | Tier | z | Event dir. | Prior weekly origin | Lead | p(UP) | RSM dir. | Match |\n|---|---|---:|---|---|---:|---:|---|---|\n| 2025-02-10 | MAJOR | 2.3407 | UP | 2025-02-07 | 3d | 0.5962 | UP | YES |\n| 2025-02-14 | MAJOR | -2.2468 | DOWN | 2025-02-07 | 7d | 0.5962 | UP | NO |\n| 2025-02-18 | MAJOR | 2.1885 | UP | 2025-02-14 | 4d | 0.6154 | UP | YES |\n| 2025-03-13 | MAJOR | 2.1237 | UP | 2025-03-07 | 6d | 0.5962 | UP | YES |\n| 2025-04-04 | EXTREME | -3.3930 | DOWN | 2025-03-28 | 7d | 0.6154 | UP | NO |\n| 2025-04-09 | EXTREME | 3.2185 | UP | 2025-04-04 | 5d | 0.5962 | UP | YES |\n| 2025-04-10 | MAJOR | 2.3440 | UP | 2025-04-04 | 6d | 0.5962 | UP | YES |\n| 2025-07-21 | MAJOR | 2.0611 | UP | 2025-07-18 | 3d | 0.5962 | UP | YES |\n| 2025-08-01 | MAJOR | 2.5481 | UP | 2025-07-25 | 7d | 0.5962 | UP | YES |\n| 2025-09-02 | MAJOR | 2.6673 | UP | 2025-08-29 | 4d | 0.6154 | UP | YES |\n| 2025-09-22 | MAJOR | 2.6254 | UP | 2025-09-19 | 3d | 0.6346 | UP | YES |\n| 2025-09-29 | MAJOR | 2.3040 | UP | 2025-09-26 | 3d | 0.6346 | UP | YES |\n| 2025-10-06 | MAJOR | 2.7911 | UP | 2025-10-03 | 3d | 0.6538 | UP | YES |\n| 2025-10-13 | MAJOR | 2.5043 | UP | 2025-10-10 | 3d | 0.6538 | UP | YES |\n| 2025-10-16 | MAJOR | 2.9074 | UP | 2025-10-10 | 6d | 0.6538 | UP | YES |\n| 2025-10-17 | MAJOR | -2.0589 | DOWN | 2025-10-10 | 7d | 0.6538 | UP | NO |\n| 2025-10-21 | EXTREME | -4.1054 | DOWN | 2025-10-17 | 4d | 0.6538 | UP | NO |\n| 2025-12-22 | EXTREME | 4.0174 | UP | 2025-12-19 | 3d | 0.6923 | UP | YES |\n| 2025-12-29 | EXTREME | -6.6415 | DOWN | 2025-12-26 | 3d | 0.7115 | UP | NO |\n
## 5. Interpretation

The raw 73.68% event-direction agreement is mechanically explained by class direction.

The frozen 19-event inventory contains:
- 14 UP events;
- 5 DOWN events.

The frozen RSM-52 model forecast UP for every 2025 target week. It therefore:
- matches all 14 UP events;
- misses all 5 DOWN events.

This produces 73.68% raw agreement but exactly 50% balanced direction accuracy. It is the event-level analogue of the same failure seen in the complete 2025 weekly test.

The EXTREME subset is especially important: only 2 of 5 extreme event directions match the RSM forecast.

Accordingly, this overlay provides no evidence that RSM-52 anticipates the direction of abnormal-volatility events. It also provides no evidence of volatility-event detection because RSM emits a weekly direction every week and does not predict whether an abnormal event will occur.

## 6. Decision

The volatility overlay does not change the model status:

`EVALUATED / NO_PROMOTION / WEAK_DIRECTIONAL_DISCRIMINATION`.

No event-conditioned threshold/window rescue is permitted under `DIRECTION_RSM_V1_RESEARCH`.
