# GOLD MONTHLY — ChHHO-ANFIS F2 Representation Audit

**Date:** 2026-09-29  
**Status:** COMPLETE / DEV-ONLY / ZERO NEON  
**Decision:** RETAIN CURRENT8 REPRESENTATION (MR1 + VW)

## 1. Scientific question

After F1 retained all eight CURRENT8 information channels, F2 tested whether the same information families should be represented differently.

Frozen reference:
- Gold/Silver/Platinum/Palladium
- MR1 = previous completed-month log return
- VW = existing GPR-conditioned causal within-month daily return summary

Tested challengers:
- MR3, MR6
- realized volatility (RV)
- monthly range
- mean absolute daily return (ABSRET)
- both all-metal replacements and one-metal-at-a-time replacements

No external variables, no lag-search combinations, no 2025/2026 tuning.

## 2. Authority

Workflow:
- run **36540846993**
- head commit **bbb7765dfa2eccd33995b6fd2a1bf64821d20597**
- summary artifact **11020404994**
- summary digest `sha256:999d51afd3f235c3a43918cf2aa977b55544c72f3a3a4b7626b846a537002b33`
- baseline artifact **11020117481**
- Neon reads: **0**

F2 baseline parity:
- CURRENT8 DEV ΣAE **1413.0297794085**
- direction **23/33**
- parity: **PASS**

## 3. Main ranking

Best non-baseline challengers:

| Variant | DEV ΣAE | Direction | ΔΣAE vs CURRENT8 |
|---|---:|---:|---:|
| CURRENT8 | **1413.0298** | **23/33** | — |
| Palladium MR3 | 1418.9295 | 19/33 | -5.8997 |
| Gold MR6 | 1486.7031 | 21/33 | -73.6733 |
| MR6 all | 1498.2281 | 22/33 | -85.1983 |
| Palladium RV | 1614.9330 | 17/33 | -201.9032 |
| Gold MR3 | 1619.2379 | 23/33 | -206.2081 |
| Platinum RV | 1644.9810 | 18/33 | -231.9512 |
| Palladium MR6 | 1658.3514 | 19/33 | -245.3216 |
| Gold RV | 1662.2175 | 18/33 | -249.1878 |
| Palladium Range | 1662.4286 | 18/33 | -249.3989 |

Other tested representations were materially worse.

Notable:
- ABSRET all: **2021.0769 / 17**
- RANGE all: **2165.1015 / 15**
- RV all: **4003.8097 / 14**
- Silver MR6: **22076.0121 / 18**
- MR3 all: **7,102,263.9236 / 19**
- Platinum Range: **8.2563e18 / 17** (pathological instability)

## 4. Robustness gate

Predeclared exploratory robustness gate:
1. aggregate ΣAE improvement vs CURRENT8;
2. months improved >= months worsened;
3. positive median paired AE improvement;
4. improvement in at least 2 of 3 DEV years.

Result:

**ROBUST_PASS = []**

No representation challenger passed.

### Closest challenger: Palladium MR3
- ΣAE: **1418.9295**
- direction: **19/33**
- months improved/worsened: **18/15**
- median paired AE improvement: **+0.3007**
- yearly ΔΣAE vs CURRENT8:
  - 2022: **+94.47**
  - 2023: **-93.37**
  - 2024: **-7.00**

Therefore it is not stable enough to replace Palladium MR1.

## 5. Interpretation

### 5.1 MR1 remains preferred
Neither MR3 nor MR6 provides a robust replacement for the current one-month return representation.

### 5.2 VW remains preferred
Replacing VW with RV, RANGE or ABSRET generally deteriorates both price error and direction.

### 5.3 Longer momentum is not universally useful
Gold MR6 shows some local month-level benefit but worsens total ΣAE and direction. Silver MR6 is highly unstable. No common 3M/6M momentum replacement is justified.

### 5.4 Pathological variants are architecture-stability evidence
Extreme results (especially MR3-all, Silver MR6, Platinum Range) are not literal feature-importance scores. They indicate that ChHHO-ANFIS can become unstable under some transformed input geometries.

Therefore F2 does not authorize adding these representations alongside CURRENT8. Doing so would expand the feature space and create a new feature-selection problem; that question belongs to a separately frozen experiment if ever reopened.

## 6. Binding decision

**CURRENT8 representation remains frozen for F3:**
- each metal MR = **MR1**
- each metal daily summary = **existing GPR-conditioned VW**

No F2 challenger is promoted.

Next stage:
**F3 lag architecture audit**.

F3 should test lag structure around the retained MR1/VW representation without re-opening representation selection:
- L1/current origin representation (baseline)
- compact lag packages such as L1+L2, L1+L2+L3, L1/L3/L6
- parsimonious distributed/MIDAS lags where applicable
- chronological inner selection only
- 2025 remains locked.

## 7. Kontrol ve Uyum Özeti

- F2 variants: **26/26 completed**
- baseline parity: **PASS**
- robust challenger: **NONE**
- CURRENT8 MR1+VW retained: **YES**
- external features: **NONE**
- 2025 selection/tuning: **NONE**
- 2026 selection/tuning: **NONE**
- random split: **NONE**
- Neon reads: **0**
- next stage: **F3 lag architecture audit**
