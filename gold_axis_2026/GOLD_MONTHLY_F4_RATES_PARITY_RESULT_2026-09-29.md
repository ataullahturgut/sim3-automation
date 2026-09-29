# GOLD MONTHLY — F4 RATES PARITY FAMILY RESULT

**Date:** 2026-09-29  
**Status:** COMPLETE / VALID RESULT / COMBINED RATES BLOCK NOT PROMOTED  
**Role:** First family-decomposition lane after ALL6-COMPACT  
**Selection window:** DEV 2022-04..2024-12 only  
**2025 used for selection:** NO  
**2026 used for selection:** NO

## 1. Authoritative execution

- workflow: **Gold Monthly F4 Rates Parity Family V1**
- run: **36569188686**
- head commit: **c2d1e2148725ff9cae481ea28e724056617220a2**
- 6/6 independent DEV shards: **SUCCESS**
- merge/summary: **SUCCESS**
- summary artifact: **11033071845**
- summary artifact digest: `sha256:d8abaeae0fd2c90f605d7c4beca4763ea2106f0bf475caefd00d9e054506850d`

## 2. Frozen BASE

- CURRENT8 inputs: **8**
- DEV ΣAE: **1413.0297794084559**
- Direction: **23/33 = 69.70%**

BASE authority is the already-passed exact companion artifact from the ALL6 parity line.

## 3. Rates parity specification

Added Rates variables:

1. NOM10_MR_ANALOG
2. NOM10_VW_ANALOG
3. REAL10_MR_ANALOG
4. REAL10_VW_ANALOG

Representation:
- monthly mean yield difference;
- GPR-conditioned weighted intramonth daily first differences;
- H.15 release cutoff: **2 calendar days**;
- same downstream chronological training-only scaling / ANFIS / local-refit path as CURRENT8.

Dimension-aware optimizer:
- CURRENT8 8 + Rates 4 = **12 total inputs**
- antecedent parameter dimension = **120**
- POP = **36**
- generations = **45**
- repeats = **3**

## 4. DEV result

### BASE
- ΣAE: **1413.0297794084559**
- Direction: **23/33 = 69.70%**

### CURRENT8 + Rates(4)
- ΣAE: **6102.555639186698**
- Direction: **16/33 = 48.48%**

### Difference
- absolute deterioration: **+4689.525859778241 USD**
- relative deterioration: **+331.88%**
- direction change: **-7 correct months**
- paired wins / losses / ties: **12 / 21 / 0**
- median paired AE improvement (BASE − Rates): **-11.9534526814 USD**
- mean paired AE improvement: **-142.1068442357 USD**
- signed mean bias: **-131.7716439599 USD**
- worst month: **2022-04**
- worst absolute error: **1905.4333029326 USD**

The result is not explained by one outlier alone: Rates loses **21 of 33** paired DEV months and the median paired improvement is negative.

## 5. Year-by-year DEV comparison

| Year | BASE ΣAE | Rates ΣAE | BASE − Rates |
|---|---:|---:|---:|
| 2022 | 397.8793858088 | 4276.9230276669 | -3879.0436418581 |
| 2023 | 395.7139916371 | 659.9945124678 | -264.2805208307 |
| 2024 | 619.4364019625 | 1165.6380990520 | -546.2016970895 |

The combined four-variable Rates block is worse than BASE in all three DEV calendar-year slices.

## 6. Dimensionality / redundancy diagnosis

Using pre-target history through 2024-11:

- pre-target rows: **177**
- BASE rank: **8/8**
- Rates-augmented rank: **12/12**
- BASE standardized design condition number: **6.8806909603**
- Rates-augmented condition number: **9.1955539275**
- condition-number ratio: **1.3364**

The design remains full rank, so there is no exact linear dependence. However, the Rates block contains substantial within-family redundancy:

- NOM10_VW vs REAL10_VW: **corr = +0.8266**
- NOM10_MR vs REAL10_MR: **corr = +0.8194**
- NOM10_MR vs NOM10_VW: **corr = +0.5937**
- REAL10_MR vs REAL10_VW: **corr = +0.5183**

Largest Rates-vs-CURRENT8 absolute correlation:
- Gold_MR1 vs REAL10_MR_ANALOG: **corr = -0.5240**

Interpretation: the 4-variable Rates block adds genuine rank but also strong internal redundancy, especially nominal-vs-real representations.

## 7. Decision

- Rates combined 4-input native block: **NOT PROMOTED**
- Rates family-wide rejection: **NOT YET AUTHORIZED**
- 2025 transport for this combined block: **NOT OPENED**
- 2026 stress for this combined block: **NOT OPENED**
- reason not to close family: strong within-family redundancy plus prior project evidence that PIT Rates can help in other architectures.
- next scientifically clean Rates step, if the family is to be resolved before moving on:
  - nominal-only pair;
  - real-only pair;
  - MR-only pair;
  - VW-only pair;
  each with dimension-adjusted optimizer parity.

No FX/VIX/Nasdaq/Energy family test was run in this step.
