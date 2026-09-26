# GOLD MONTHLY FORECAST — ANFIS FAMILY FINAL CLOSURE

Date: 2026-09-26
Status: COMPLETE
Branch: gold-midas-headswap-v1-20260925

## 1. Frozen authority
- Target: H=1 next calendar month average XAU/USD price via joint Gold/Silver/Platinum/Palladium return outputs.
- Inputs: unchanged governed 8-feature VW-MIDAS contract.
- DEV selection authority: 2022-04..2024-12, n=33.
- 2025: transport reporting only.
- 2026 Jan-Jul: retrospective stress reporting only.
- Random split: NONE.
- Target-month leakage: NONE.
- DB: READ_ONLY.

## 2. Vanilla ANFIS anchor
Canonical checked Jang-style ANFIS:
- first-order Sugeno/TSK;
- 5 Gaussian compact rules;
- LSE consequents;
- gradient premise learning;
- chronological checking-data early stopping.

Vanilla DEV:
- SumAE 1852.0465
- Direction 21/33 = 63.64%

## 3. Broad hybrid screen
32/32 metaheuristic-ANFIS hybrids executed.
27 passed the scientific forecast gate.
Five broad-screen methods were rejected for pathological forecast magnitude in at least one reporting origin:
ABC, WOA, FPA, HGS, AOA.

Stage-2 valid Pareto parents before ANFIS-specific literature extension:
- MFO-ANFIS: SumAE 1630.3325, direction 20/33.
- HHO-ANFIS: SumAE 1646.1336, direction 23/33.

## 4. Stage-3 parity refinements
| Method | Gate | DEV SumAE | Direction |
|---|---|---:|---:|
| MPA-CPA | PASS | 1918.5637 | 18/33 |
| PSO-TLBO Hybrid | PASS | 3156.9979 | 19/33 |
| TLBO-tuned PSO | PASS | 3465.1623 | 20/33 |
| Adaptive PSO | FAIL scientific gate | 363283.4306 | 22/33 |
| Adaptive TLBO | FAIL scientific gate | 24830.2156 | 17/33 |
| Adaptive Crow | FAIL scientific gate | 3432.3536 | 18/33 |
| DE-tuned PSO | FAIL scientific gate | 9166.1914 | 18/33 |
| MPA-SCA | FAIL scientific gate | 3275.4131 | 20/33 |
| MPA-GA | FAIL scientific gate | 3242.7176 | 20/33 |

No parity-refinement model improves the valid MFO/HHO frontier.

## 5. Stage-3C ANFIS-specific literature hybrids

### ChHHO-ANFIS
Chaotic initialization + HHO premise optimization + local Jang-style ANFIS refinement.

DEV:
- SumAE: 1413.029779
- MAE: 42.8191
- MAPE: 2.10768%
- RMSE: 54.8274
- Direction: 23/33 = 69.70%
- Worst APE: 6.0975%
- Relative MAE vs RW: 0.80377

2025 reporting:
- SumAE 1252.0542
- Direction 9/12 = 75%
- MAE 104.3378
- MAPE 2.97123%

2026 Jan-Jul reporting:
- SumAE 1178.1395
- Direction 5/7 = 71.43%
- MAE 168.3056
- MAPE 3.70774%
- Relative MAE vs RW 0.71058

Reproducibility:
- independent rerun produced identical metrics: PASS.

### MVO-ANFIS
Initial implementation was BLOCKED by a vector-to-scalar wormhole update bug.
The implementation was corrected and rerun successfully.

Final MVO results:
- DEV SumAE 2057.3973
- Direction 17/33
- 2025 SumAE 1378.2897, direction 9/12
- 2026 SumAE 5600.4172, direction 4/7

Decision: scientifically valid run, but not competitive and not robust enough for promotion.

## 6. ANFIS robustness of ChHHO
Yearly DEV SumAE / direction:
- 2022 Apr-Dec: 397.8794 / 7 of 9
- 2023: 395.7140 / 7 of 12
- 2024: 619.4364 / 9 of 12

Against ANN champions:
- Leave-one-origin aggregate SumAE comparison: ChHHO remains below FULL7 in 24/33 omissions.
- ChHHO remains below REDUCED4 in 26/33 omissions.
- However monthly paired absolute-error HAC/Newey-West comparisons do not establish a statistically decisive difference over FULL7/REDUCED4; the DEV lead is modest.
- Signed forecast-error correlation: ChHHO vs FULL7 0.9084; vs REDUCED4 0.8887.
Thus ChHHO is the current point-estimate leader, not proof of universal superiority.

## 7. Controlled ANFIS ensemble diagnostics
No arbitrary subset search was permitted.

ChHHO + HHO fixed grid:
- best full-DEV diagnostic weight on fixed 0/.25/.5/.75/1 grid = 75% ChHHO + 25% HHO
- DEV SumAE 1383.1589, direction 22/33

But expanding prequential weight selection yields:
- SumAE 1446.3209
- direction 21/33

Therefore optimized/adaptive ANFIS weight selection is NOT promoted.
ChHHO single remains the frozen ANFIS family champion.

## 8. Family decision
- Vanilla ANFIS: architecture anchor.
- MFO/HHO: reserve ANFIS benchmarks.
- ChHHO-ANFIS: PRIMARY ANFIS CHAMPION.
- MVO: valid but rejected for promotion.
- Stage-3 parity refinements: closed, no new Pareto point.
- Learned/tuned ensemble weights: closed; prequential evidence does not support them.

ANFIS family development is COMPLETE.
