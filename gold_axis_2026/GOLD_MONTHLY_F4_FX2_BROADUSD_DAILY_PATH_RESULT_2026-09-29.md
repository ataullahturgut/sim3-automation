# GOLD MONTHLY — F4 FX2 BROAD USD DAILY-PATH RESULT

**Date:** 2026-09-29  
**Status:** COMPLETE / VALID / NOT PROMOTED  
**Role:** Second FX family-decomposition lane  
**Selection window:** DEV 2022-04..2024-12 only  
**2025 used for selection:** NO  
**2026 used for selection:** NO

## 1. FX2 design

FX2 adds two compact Broad USD features to CURRENT8:

1. `BROADUSD_MR1 = log(mean(BROADUSD[p]) / mean(BROADUSD[p-1]))`
2. `BROADUSD_DAILY_RMS_VOL = sqrt(mean(diff(log(BROADUSD_eligible_p))^2))`

Interpretation:
- feature 1 = monthly USD direction/level change
- feature 2 = intramonth short-run FX path volatility
- source: Fed H.10 Broad USD index
- sign of MR1: positive = USD strengthening
- H.10 release cutoff: **7 calendar days**
- GPR weighting on FX: **NOT USED**
- same downstream chronological train-only scaling / ChHHO-ANFIS / local-refit path as BASE

Dimension-aware optimizer:
- CURRENT8 8 + FX2 2 = **10 total inputs**
- antecedent parameter dimension = **100**
- POP = **30**
- generations = **45**
- repeats = **3**

## 2. Authoritative execution

- workflow: **Gold Monthly F4 FX2 Broad USD Daily Path V1**
- run: **36575331412**
- head commit: **d6f1fe245587bbcd82cf4d4ffdbaf4f53378b182**
- 6/6 DEV shards: **SUCCESS**
- summarize: **SUCCESS**
- summary artifact: **11037330894**
- summary artifact digest: `sha256:a14e70151f71d3ed1561b5f85f0d4d0c0a976317f919f746032436a1dd14da36`

## 3. DEV result

### BASE CURRENT8
- ΣAE: **1413.0297794084559**
- Direction: **23/33 = 69.70%**

### FX2
- ΣAE: **1787.6000747067567**
- Direction: **17/33 = 51.52%**

### Difference vs BASE
- ΣAE deterioration: **+374.57029529830083 USD**
- relative deterioration: **+26.51%**
- direction change: **-6 correct months**
- paired wins / losses / ties: **14 / 19 / 0**
- median paired AE improvement (BASE − FX2): **-10.0237615596 USD**
- mean paired AE improvement: **-11.3506150090 USD**
- signed mean bias: **-12.6547936971 USD**
- worst FX2 month: **2023-10**
- worst FX2 absolute error: **147.5005218662 USD**

## 4. Year-by-year

| Year | BASE ΣAE | FX2 ΣAE | BASE − FX2 |
|---|---:|---:|---:|
| 2022 | 397.8793858088 | 497.9770602238 | -100.0976744150 |
| 2023 | 395.7139916371 | 668.6239808455 | -272.9099892084 |
| 2024 | 619.4364019625 | 620.9990336374 | -1.5626316749 |

## 5. FX family sequence

| Variant | Representation | DEV ΣAE | Direction |
|---|---|---:|---:|
| BASE | CURRENT8 | **1413.029779** | **23/33** |
| FX1 | Broad USD monthly mean log change | 2532.593559 | 20/33 |
| FX2 | Broad USD monthly change + daily RMS volatility | **1787.600075** | 17/33 |

FX2 improves on FX1 by **744.9934843068533 USD** ΣAE, but remains **374.57029529830083 USD** worse than BASE and loses six correct directions.

The 2024 yearly error is almost identical to BASE, but 2022 and especially 2023 remain worse.

## 6. Decision

- FX2 representation: **VALID**
- FX2 promotion: **REJECTED**
- FX family-wide rejection: **NOT YET AUTHORIZED**
- reason: daily volatility was tested, but daily directional path with a true compact MIDAS lag-weighting mechanism has not yet been tested
- 2025 transport: **NOT OPENED**
- 2026 stress: **NOT OPENED**

Next FX-only test:
- FX3 = Broad USD monthly MR1 + training-only compact directional MIDAS scalar over daily Broad USD returns
- use a parsimonious lag-weight function rather than GPR weighting
- no extra currency pairs
- total input count remains **10**
- dimension **100**
- POP **30**
- 45 generations / 3 repeats

FX3 is NOT run by this report.
