# GOLD MONTHLY — F4 ALL6-COMPACT DIAGNOSTIC RESULT

**Date:** 2026-09-29  
**Status:** COMPLETE / VALID DIAGNOSTIC RESULT  
**Role:** System-level diagnostic challenger, not final promotion  
**Selection window:** DEV 2022-04..2024-12 only  
**2025 used for selection:** NO  
**2026 used for selection:** NO  

## 1. Authoritative execution

- workflow: **Gold Monthly F4 ALL6 Compact Sharded Diagnostic V1**
- run: **36567473694**
- head commit: **59fff6bba43eda027884af0088919a5c25d4d96c**
- execution: **6 independent outer-origin shards**
- all shards: **6/6 SUCCESS**
- merge/summary: **SUCCESS**
- summary artifact: **11032667656**
- summary artifact digest: `sha256:c743f4e06185e6a64574cb78f5b35451123a2ea0ca9458a41c900a4118903c27`

The sharded execution is scientifically equivalent to a single sequential DEV run because each outer target is independent and the ChHHO seed depends on target/repeat, not execution order.

Earlier single-job runs are superseded for authority:
- run **36565588421**: first attempt contained a post-computation feature-name reporting bug; not authoritative.
- run **36566088448**: BASE companion completed successfully and its artifact **11032345750** was used as the exact BASE control for the authoritative sharded summary. The remaining single-job ALL6 computation is not the authority result.

## 2. Frozen BASE control

BASE companion parity: **PASS**

- CURRENT8 inputs: **8**
- antecedent parameter dimension: **80**
- POP: **24**
- generations: **45**
- repeats: **3**
- DEV ΣAE: **1413.0297794084559**
- Direction: **23/33 = 69.70%**
- MAE: **42.8190842245**

This reproduces the frozen canonical ChHHO-ANFIS reference.

## 3. ALL6-COMPACT specification

CURRENT8 plus six daily external families:

1. Rates
2. FX / Broad USD
3. VIX
4. Nasdaq-100
5. WTI
6. Brent

External block = 14 variables:
- Rates: 4
- Broad USD: 2
- VIX: 2
- Nasdaq-100: 2
- WTI: 2
- Brent: 2

Total inputs: **22**

Optimizer parity:
- antecedent parameter dimension: **220**
- POP: **66**
- generations: **45**
- repeats: **3**

All external variables passed the frozen B1 transform parity and B2 processing/preprocessing parity gates before this run.

## 4. DEV result

### BASE
- ΣAE: **1413.0297794084559**
- Direction: **23/33 = 69.70%**

### ALL6-COMPACT
- ΣAE: **2870.961742339026**
- MAE: **86.9988406769**
- Direction: **19/33 = 57.58%**

### Difference
- ΣAE deterioration: **+1457.93196293057 USD**
- relative ΣAE deterioration: **+103.18%**
- Direction change: **-4 correct months**
- paired monthly wins: **10**
- paired monthly losses: **23**
- ties: **0**
- median paired AE improvement (BASE − ALL6): **-10.4520781833 USD**
- mean paired AE improvement: **-44.1797564524 USD**
- ALL6 signed mean bias: **+23.8535037779 USD**
- worst ALL6 month: **2022-05**
- worst ALL6 absolute error: **920.8863163163 USD**

## 5. Year-by-year DEV comparison

| Year | BASE ΣAE | ALL6 ΣAE | BASE − ALL6 |
|---|---:|---:|---:|
| 2022 | 397.8793858088 | 1416.8927688302 | -1019.0133830214 |
| 2023 | 395.7139916371 | 629.5864873830 | -233.8724957458 |
| 2024 | 619.4364019625 | 824.4824861259 | -205.0460841634 |

ALL6 is worse than BASE in aggregate in **all three DEV calendar-year slices**.

## 6. Interpretation

The ALL6 system-level challenger **does not improve** the frozen CURRENT8 ChHHO-ANFIS baseline under processing and optimizer parity.

This result does **not** authorize the conclusion that Rates, FX, VIX, Nasdaq, WTI and Brent are individually useless.

The experiment changes the model from 8 to 22 inputs simultaneously. The degradation can arise from:
- one or more harmful families,
- redundant/correlated families,
- interaction effects,
- high-dimensional premise search difficulty,
- weak signal dilution,
- a small subset of pathological origins.

Therefore the next scientific stage is the frozen **family decomposition + dimensionality/redundancy diagnosis**, followed only then by constrained compact selection.

## 7. Gate decision

- B0 Data Authority V2: **PASS**
- B1 transform parity: **PASS**
- B2-A downstream processing/preprocessing parity: **PASS**
- B2-B optimizer + BASE parity: **PASS**
- ALL6 diagnostic execution: **PASS**
- ALL6 performance improvement over BASE: **NO**
- ALL6 final promotion: **REJECTED**
- external-family-wide rejection: **NOT AUTHORIZED**
- next step: **FAMILY DECOMPOSITION + DIMENSIONALITY/REDUNDANCY DIAGNOSIS**

No 2025 transport or 2026 stress run is authorized for ALL6 in its current 22-input form.
