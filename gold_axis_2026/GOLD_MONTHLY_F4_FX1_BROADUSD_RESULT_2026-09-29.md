# GOLD MONTHLY — F4 FX1 BROAD USD COMPACT RESULT

**Date:** 2026-09-29  
**Status:** COMPLETE / VALID / NOT PROMOTED  
**Role:** First FX family-decomposition lane  
**Selection window:** DEV 2022-04..2024-12 only  
**2025 used for selection:** NO  
**2026 used for selection:** NO

## 1. FX1 design

FX1 adds exactly one FX variable to CURRENT8:

- `BROADUSD_MONTHLY_MEAN_LOG_CHANGE = log(mean(BROADUSD[p]) / mean(BROADUSD[p-1]))`

Contract:
- source: Fed H.10 Broad USD index
- sign: positive = USD strengthening
- release cutoff: **7 calendar days**
- daily FX VW: **NOT USED**
- GPR weighting on FX: **NOT USED**
- same downstream chronological train-only scaling / ChHHO-ANFIS / local-refit path as BASE

Dimension-aware optimizer:
- CURRENT8 8 + FX1 1 = **9 total inputs**
- antecedent parameter dimension = **90**
- POP = **27**
- generations = **45**
- repeats = **3**

## 2. Authoritative execution

- workflow: **Gold Monthly F4 FX1 Broad USD V1**
- run: **36573963802**
- head commit: **d89713432f54877c551b2b120ab63a655de26b37**
- 6/6 DEV shards: **SUCCESS**
- summarize: **SUCCESS**
- summary artifact: **11036118411**
- summary artifact digest: `sha256:e8b222298bb25b49140cf2f3b77369641c1c9aba2b1e351a26948a0e8950d33f`

## 3. DEV result

### BASE CURRENT8
- ΣAE: **1413.0297794084559**
- Direction: **23/33 = 69.70%**

### FX1
- ΣAE: **2532.59355901361**
- Direction: **20/33 = 60.61%**

### Difference vs BASE
- ΣAE deterioration: **+1119.5637796051542 USD**
- relative deterioration: **+79.23%**
- direction change: **-3 correct months**
- paired wins / losses / ties: **13 / 20 / 0**
- median paired AE improvement (BASE − FX1): **-12.2449977274 USD**
- mean paired AE improvement: **-33.9261751396 USD**
- signed mean bias: **-34.9539510109 USD**
- worst FX1 month: **2022-04**
- worst FX1 absolute error: **769.8660852655 USD**

## 4. Year-by-year

| Year | BASE ΣAE | FX1 ΣAE | BASE − FX1 |
|---|---:|---:|---:|
| 2022 | 397.8793858088 | 1278.0631789155 | -880.1837931067 |
| 2023 | 395.7139916371 | 568.4121785126 | -172.6981868754 |
| 2024 | 619.4364019625 | 686.1182015856 | -66.6817996231 |

FX1 is worse than BASE in all three DEV calendar-year slices.

## 5. Decision

- FX1 representation: **VALID**
- FX1 promotion: **REJECTED**
- FX family-wide rejection: **NOT AUTHORIZED**
- reason: this test uses only the monthly-level Broad USD change and does not yet test the available daily FX path
- 2025 transport: **NOT OPENED**
- 2026 stress: **NOT OPENED**

Next FX-only test should retain the compact family size while adding the daily path:
- `BROADUSD_MR1`
- `BROADUSD_DAILY_PATH`
- total inputs = **10**
- D = **100**
- POP = **30**
- 45 generations / 3 repeats

The daily path should be frozen before outcome; no other FX series should be added in this stage.
