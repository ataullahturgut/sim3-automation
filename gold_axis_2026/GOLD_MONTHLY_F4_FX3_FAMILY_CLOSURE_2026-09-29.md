# GOLD MONTHLY — F4 FX3 DIRECTIONAL MIDAS + FX FAMILY CLOSURE

**Date:** 2026-09-29  
**Status:** COMPLETE / VALID / NOT PROMOTED / FX NATIVE F4 FAMILY CLOSED  
**Selection window:** DEV 2022-04..2024-12 only  
**2025 used for selection:** NO  
**2026 used for selection:** NO

## 1. FX3 design

FX3 uses two compact Broad USD features:

1. `BROADUSD_MR1 = log(mean(BROADUSD[p]) / mean(BROADUSD[p-1]))`
2. one daily directional Broad USD scalar from daily log returns using a parsimonious exponential-Almon MIDAS weighting.

MIDAS contract:
- family: exponential Almon
- age normalization: newest daily return = 0, oldest = 1
- frozen candidate set selected before outcome
- weight parameters selected separately at each outer origin
- selection uses only the ANFIS inner-train pool
- the ANFIS validation block is untouched by MIDAS parameter selection
- MIDAS nested selection objective: univariate Gold log-return MAE on a chronological subvalidation split
- GPR weighting on FX: **NOT USED**
- no additional currency pairs

Dimension-aware optimizer:
- CURRENT8 8 + FX3 2 = **10 total inputs**
- antecedent parameter dimension = **100**
- POP = **30**
- generations = **45**
- repeats = **3**

## 2. Authoritative execution

- workflow: **Gold Monthly F4 FX3 Directional MIDAS V1**
- run: **36576876579**
- head commit: **ea2bd5c5a119929ef448d6853941b89f5e056337**
- 6/6 DEV shards: **SUCCESS**
- summarize: **SUCCESS**
- summary artifact: **11037952667**
- summary artifact digest: `sha256:d0a553ffa7caaa4119143dacfebb9292338378832722e1537da60c2a5a222842`

## 3. DEV result

### BASE CURRENT8
- ΣAE: **1413.0297794084559**
- Direction: **23/33 = 69.70%**

### FX3
- ΣAE: **1829.800218215398**
- Direction: **20/33 = 60.61%**

### Difference vs BASE
- ΣAE deterioration: **+416.77043880694214 USD**
- relative deterioration: **+29.49%**
- direction change: **-3 correct months**
- paired wins / losses / ties: **13 / 20 / 0**
- median paired AE improvement (BASE − FX3): **-6.7261486840 USD**
- mean paired AE improvement: **-12.6294072366 USD**
- signed mean bias: **-13.3699152671 USD**
- worst FX3 month: **2024-04**
- worst FX3 absolute error: **170.1781399883 USD**

## 4. Year-by-year

| Year | BASE ΣAE | FX3 ΣAE | BASE − FX3 |
|---|---:|---:|---:|
| 2022 | 397.8793858088 | 474.9861766507 | -77.1067908419 |
| 2023 | 395.7139916371 | 636.4661928370 | -240.7522011998 |
| 2024 | 619.4364019625 | 718.3478487277 | -98.9114467652 |

FX3 is worse than BASE in all three DEV calendar-year slices.

## 5. MIDAS-weight selection diagnostic

Selected exponential-Almon weight parameters across 33 DEV outer origins:

- (-8.0, 0.0): **26 origins**
- (0.0, 0.0): **4 origins**
- (-1.0, 0.0): **1 origin**
- (1.0, -2.0): **1 origin**
- (2.0, -2.0): **1 origin**

The dominant choice is the strongest recency-decay candidate. This indicates that, when allowed to select using nested pre-validation history, the daily Broad USD path usually prefers the newest daily returns rather than equal or hump-shaped weighting. The resulting signal nevertheless does not improve the frozen BASE.

## 6. FX family sequence

| Variant | Representation | DEV ΣAE | Direction |
|---|---|---:|---:|
| BASE | CURRENT8 | **1413.029779** | **23/33** |
| FX1 | Broad USD monthly mean log change | 2532.593559 | 20/33 |
| FX2 | monthly change + daily RMS volatility | **1787.600075** | 17/33 |
| FX3 | monthly change + directional Almon-MIDAS daily return | 1829.800218 | **20/33** |

FX2 is the best FX native-input price-error variant, while FX3 recovers direction relative to FX2. Neither beats the BASE on the project’s primary criteria.

## 7. Family decision

Per the user-approved stop rule:

- FX3 beats BASE on ΣAE: **NO**
- FX3 direction at least equals BASE: **NO**
- further native-input FX redesign: **CLOSED**
- FX native F4 family: **CLOSED / NOT PROMOTED**
- 2025 transport for FX1/FX2/FX3: **NOT OPENED**
- 2026 stress for FX1/FX2/FX3: **NOT OPENED**
- historical residual-correction evidence involving USD/CNY or other architectures remains historical and is not deleted or reinterpreted.
- next external family in the one-family-at-a-time decomposition sequence: **VIX**
- VIX execution status: **NOT STARTED**

This closure applies to the current F4 native ChHHO-ANFIS input-integration path.
