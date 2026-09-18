# GOLD CONTROL — DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH PRE-2025 CHECKPOINT

**Date:** 2026-09-18  
**Identity:** `DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH`  
**Status:** `PRE2025_CHECKPOINT_COMPLETE / FROZEN_BEFORE_CORRECTED_2025_REPLAY`  
**Checkpoint commit:** `c08455979092d4641b972da67c3ae73964c4bb15`

## Corrected source-faithful implementation

- source weekly return = sum of governed daily simple percentage returns;
- binary sign = 1 iff weekly return > 0;
- pinned reference implementation: R 4.4.1 + VLMC 1.4-4;
- rolling windows: 26, 52, 104 weeks;
- K0 = 0.30;
- K grid = 0.40..2.50 by 0.02;
- bootstrap B = 1000;
- burn-in = 10000;
- bootstrap classification uses `VLMC::predict(type="class")`;
- final direction uses P(UP)>=0.5;
- each window's K is calibrated once pre-OOS and frozen for subsequent rolling replay.

## Frozen cutoff calibration

| Window | K* | Bootstrap matches | Loss | Tied K count | Initial order |
|---|---:|---:|---:|---:|---:|
| 26 | 0.40 | 696/1000 | 0.304 | 4 | 4 |
| 52 | 0.54 | 713/1000 | 0.287 | 2 | 5 |
| 104 | 0.40 | 757/1000 | 0.243 | 4 | 8 |

## Own-support pre-2025 results

| Window | Period | n | Accuracy | Balanced | UP sens. | DOWN sens. | UP/DOWN forecasts |
|---|---|---:|---:|---:|---:|---:|---:|
| 26 | 2023 | 52 | 0.5000 | 0.5060 | 0.4286 | 0.5833 | 22 / 30 |
| 26 | 2024 | 53 | 0.5660 | 0.5641 | 0.6667 | 0.4615 | 32 / 21 |
| 52 | 2023 | 43 | 0.5116 | 0.5186 | 0.4583 | 0.5789 | 19 / 24 |
| 52 | 2024 | 53 | **0.6792** | **0.6781** | 0.7407 | 0.6154 | 30 / 23 |
| 104 | 2024 | 44 | 0.5682 | 0.5583 | 0.6667 | 0.4500 | 27 / 17 |

## Fair 2024 common support

All three windows are simultaneously eligible beginning **2024-03-04**, n=44.

| Window | Accuracy | Balanced | UP sens. | DOWN sens. | Brier | Log loss |
|---|---:|---:|---:|---:|---:|---:|
| 26 | 0.5909 | 0.5833 | 0.6667 | 0.5000 | 0.3378 | 5.4576 |
| 52 | **0.6364** | **0.6292** | 0.7083 | **0.5500** | **0.2694** | **3.5810** |
| 104 | 0.5682 | 0.5583 | 0.6667 | 0.4500 | 0.3377 | 6.0234 |

## Pre-2025 interpretation

The corrected k=52 specification provides the strongest pre-2025 validation evidence on both its full 2024 support and the fair 2024 common support. Unlike the old V1 result, it does not fail the 2024 direction-validation check.

However, V2 does not select a Gold winner from 2025. All three source-feasible windows are frozen and carried unchanged into the corrected 2025 replay.

Probability quality remains problematic because empirical VLMC transition probabilities can hit exactly 0 or 1; V2 does not add smoothing after seeing this evidence.
