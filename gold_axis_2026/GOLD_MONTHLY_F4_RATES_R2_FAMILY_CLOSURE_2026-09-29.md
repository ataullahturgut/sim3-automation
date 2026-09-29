# GOLD MONTHLY — F4 RATES R2 ORTHOGONAL PAIR + FAMILY CLOSURE

**Date:** 2026-09-29  
**Status:** COMPLETE / VALID / NOT PROMOTED / RATES NATIVE F4 FAMILY CLOSED  
**Selection window:** DEV 2022-04..2024-12 only  
**2025 used for selection:** NO  
**2026 used for selection:** NO

## 1. R2 design

R2 adds two economically orthogonalized monthly Rates signals to CURRENT8:

1. `REAL10_MONTHLY_MEAN_DIFF = mean(REAL10[p]) - mean(REAL10[p-1])`
2. `BREAKEVEN10_MONTHLY_MEAN_DIFF = [mean(NOM10[p])-mean(REAL10[p])] - [mean(NOM10[p-1])-mean(REAL10[p-1])]`

Constraints:
- daily Rates VW: **NOT USED**
- GPR weighting on Rates: **NOT USED**
- H.15 release lag: **2 calendar days**
- same downstream chronological train-only scaling / ChHHO-ANFIS / local-refit path as BASE.

Dimension-aware optimizer:
- CURRENT8 8 + R2 2 = **10 total inputs**
- antecedent parameter dimension = **100**
- POP = **30**
- generations = **45**
- repeats = **3**

## 2. Authoritative execution

- workflow: **Gold Monthly F4 Rates R2 Orthogonal Pair V1**
- authoritative run: **36572341391**
- head commit: **17e61eb4819120419f003194a8dd50e039978abc**
- 6/6 DEV shards: **SUCCESS**
- summarize: **SUCCESS**
- summary artifact: **11036170615**
- summary artifact digest: `sha256:087b2d6f62ba486d872dc5f1d4f8d8eb5549a6bd778d18aa474c7b9c7757456a`

Earlier run **36572222708** failed before scientific scoring because the helper attempted to unpack numeric monthly values as date/value tuples. It is classified **TECHNICAL_IMPLEMENTATION_FAILURE / NOT_SCIENTIFIC_RESULT**. The R2 formula and frozen design were unchanged in the authoritative rerun.

## 3. DEV result

### BASE CURRENT8
- ΣAE: **1413.0297794084559**
- Direction: **23/33 = 69.70%**

### R2
- ΣAE: **1716.9570365398133**
- Direction: **19/33 = 57.58%**

### Difference vs BASE
- ΣAE deterioration: **+303.92725713135746 USD**
- relative deterioration: **+21.51%**
- direction change: **-4 correct months**
- paired wins / losses / ties: **15 / 18 / 0**
- median paired AE improvement (BASE − R2): **-8.6342994027 USD**
- mean paired AE improvement: **-9.2099168828 USD**
- signed mean bias: **-13.6002083193 USD**
- worst R2 month: **2024-03**
- worst R2 absolute error: **140.2185519019 USD**

## 4. Year-by-year

| Year | BASE ΣAE | R2 ΣAE | BASE − R2 |
|---|---:|---:|---:|
| 2022 | 397.8793858088 | 509.6600703776 | -111.7806845688 |
| 2023 | 395.7139916371 | 521.6554410640 | -125.9414494269 |
| 2024 | 619.4364019625 | 685.6415250982 | -66.2051231357 |

R2 is worse than BASE in all three DEV calendar-year slices.

## 5. Rates redesign sequence

| Variant | Representation | DEV ΣAE | Direction |
|---|---|---:|---:|
| BASE | CURRENT8 | **1413.029779** | **23/33** |
| Rates(4) | Nom MR/VW + Real MR/VW | 6102.555639 | 16/33 |
| R1 | Real-yield monthly mean change only | 1837.635158 | 19/33 |
| R2 | Real-yield change + breakeven change | **1716.957037** | **19/33** |

R2 improves on R1 by **120.6781212954545 USD** ΣAE, but remains **303.92725713135746 USD** worse than BASE and loses four correct directions.

The sequence strongly supports the diagnosis that the original four-input Rates failure contained a major representation/dimensionality component. Compact orthogonalization materially repairs the failure, but the repaired Rates signal still does not add net DEV value to the native ChHHO-ANFIS input space.

## 6. Family decision

Under the user-approved stop rule:

- R2 beats BASE: **NO**
- Rates native F4 family promotion: **NO**
- further Rates native-input redesign: **CLOSED**
- Rates family status in this F4 native-integration track: **CLOSED / NOT PROMOTED**
- 2025 transport for R2: **NOT OPENED**
- 2026 stress for R2: **NOT OPENED**
- prior PIT Rates residual-layer evidence in other model architectures remains historical evidence and is not deleted or reinterpreted.
- next external family: **FX**
- FX execution status: **NOT STARTED**

This closure applies to the current F4 native ChHHO-ANFIS integration path, not to every possible residual-correction or alternative-model Rates architecture.
