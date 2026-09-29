# GOLD MONTHLY — F4 RATES R1 REAL-YIELD COMPACT RESULT

**Date:** 2026-09-29  
**Status:** COMPLETE / VALID / NOT PROMOTED  
**Role:** Rates representation redesign — R1  
**Selection window:** DEV 2022-04..2024-12 only  
**2025 used for selection:** NO  
**2026 used for selection:** NO

## 1. R1 design

R1 adds exactly one Rates variable to CURRENT8:

- `REAL10_MONTHLY_MEAN_DIFF = mean(REAL10[p]) - mean(REAL10[p-1])`

Constraints:
- no nominal yield input;
- no daily VW Rates feature;
- no GPR weighting on Rates;
- H.15 release lag: 2 calendar days;
- same downstream chronological train-only scaling / ChHHO-ANFIS / local-refit path as BASE.

Dimension-aware optimizer:
- CURRENT8 8 + R1 1 = **9 total inputs**
- antecedent parameter dimension = **90**
- POP = **27**
- generations = **45**
- repeats = **3**

## 2. Authoritative execution

- workflow: **Gold Monthly F4 Rates R1 Real Yield V1**
- run: **36570943295**
- head commit: **472db002a6f6fb6fb3700623386416179ca76aa0**
- 6/6 DEV shards: **SUCCESS**
- summarize: **SUCCESS**
- summary artifact: **11033588984**
- summary artifact digest: `sha256:050e47f0c94711c7a73c8c5204e2c7734327de6301589607bf407a167c95842e`

## 3. DEV result

### BASE CURRENT8
- ΣAE: **1413.0297794084559**
- Direction: **23/33 = 69.70%**

### R1 — CURRENT8 + one monthly real-yield change
- ΣAE: **1837.6351578352678**
- Direction: **19/33 = 57.58%**

### Difference vs BASE
- ΣAE deterioration: **+424.605378426812 USD**
- relative deterioration: **+30.05%**
- direction change: **-4 correct months**
- paired wins / losses / ties: **14 / 19 / 0**
- median paired AE improvement (BASE − R1): **-7.2854732528 USD**
- mean paired AE improvement: **-12.8668296493 USD**
- signed mean bias: **-8.3247270751 USD**
- worst R1 month: **2024-03**
- worst R1 absolute error: **154.8141711720 USD**

## 4. Year-by-year

| Year | BASE ΣAE | R1 ΣAE | BASE − R1 |
|---|---:|---:|---:|
| 2022 | 397.8793858088 | 509.7708299865 | -111.8914441777 |
| 2023 | 395.7139916371 | 635.9704031861 | -240.2564115490 |
| 2024 | 619.4364019625 | 691.8939246626 | -72.4575227001 |

R1 is worse than BASE in all three DEV calendar-year slices.

## 5. Representation / dimensionality diagnosis

The earlier parity-correct four-variable Rates block produced:
- ΣAE **6102.555639186698**
- Direction **16/33**

R1 produces:
- ΣAE **1837.6351578352678**
- Direction **19/33**

Therefore reducing Rates from four partially redundant features to one compact real-yield feature reduces ΣAE by:
- **4264.92048135143 USD**
- **69.89%** relative to the four-variable Rates block

and recovers:
- **+3 correct directions**

This is strong evidence that the earlier Rates(4) failure was materially driven by representation/dimensionality/redundancy, not merely by the existence of Rates information.

However, R1 still does not outperform the frozen BASE.

## 6. Decision

- R1 representation: **VALID**
- R1 promotion: **REJECTED**
- conclusion "Rates contains no useful signal": **NOT AUTHORIZED**
- representation/dimension hypothesis: **SUPPORTED**
- 2025 transport: **NOT OPENED**
- 2026 stress: **NOT OPENED**

Next Rates redesign step remains pre-outcome:
- R2 = compact orthogonal monetary pair:
  1. monthly real-yield change;
  2. monthly breakeven-inflation change = nominal10 − real10;
- total inputs 10;
- D=100;
- POP=30;
- 45 generations;
- 3 repeats.

R2 is not run by this report.
