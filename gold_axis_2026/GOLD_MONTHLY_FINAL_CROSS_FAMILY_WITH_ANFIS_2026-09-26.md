# GOLD MONTHLY FORECAST — FINAL CROSS-FAMILY AUDIT WITH ANFIS

Date: 2026-09-26
Status: COMPLETE
Active criteria: DEV cumulative absolute error (SumAE, lower) + monthly direction accuracy (higher)
DEV: 2022-04..2024-12, n=33
2025/2026: reporting/stress only

## 1. Family champions

### ANN
FULL7 ANN:
- DEV SumAE 1428.8590
- Direction 22/33
- MAE 43.2988
- RMSE 55.6338

REDUCED4 ANN:
- DEV SumAE 1431.4587
- Direction 24/33
- MAE 43.3775
- RMSE 54.9665

### ELM
AOA-ELM price benchmark:
- DEV SumAE 1474.1021
- Direction 20/33

TLBO-ELM direction benchmark:
- DEV SumAE 1758.7507
- Direction 23/33

### ELMFIS
SMA-ELMFIS:
- DEV SumAE 1651.4482
- Direction 25/33 = 75.76%

ABC-ELMFIS:
- DEV SumAE 1524.8854
- Direction 21/33

### ANFIS
ChHHO-ANFIS:
- DEV SumAE 1413.0298
- Direction 23/33 = 69.70%
- MAE 42.8191
- RMSE 54.8274
- reproducibility rerun: identical metrics PASS

ChHHO therefore dominates the prior FULL7 ANN point on both active DEV criteria:
- lower SumAE: 1413.03 vs 1428.86
- higher direction: 23/33 vs 22/33

The margin in monthly paired absolute loss is modest and not statistically decisive under HAC/Newey-West diagnostics; interpret ChHHO as the current point-estimate leader, not proof of universal superiority.

## 2. Updated single/frozen-family DEV Pareto
| Model | Family | DEV SumAE | Direction |
|---|---|---:|---:|
| ChHHO-ANFIS | ANFIS | 1413.03 | 23/33 |
| REDUCED4 ANN | ANN ensemble | 1431.46 | 24/33 |
| SMA-ELMFIS | ELMFIS | 1651.45 | 25/33 |

FULL7 ANN is no longer on this frontier because ChHHO has both lower error and higher direction.

## 3. Year and leave-one-origin robustness
DEV yearly SumAE:
- 2022 Apr-Dec: ChHHO 397.88; FULL7 346.69; REDUCED4 364.63.
- 2023: ChHHO 395.71; FULL7 436.10; REDUCED4 434.82.
- 2024: ChHHO 619.44; FULL7 646.07; REDUCED4 632.00.

DEV yearly direction:
- 2022: ChHHO 7/9; FULL7 8/9; REDUCED4 8/9.
- 2023: ChHHO 7/12; FULL7 6/12; REDUCED4 7/12.
- 2024: ChHHO 9/12; FULL7 8/12; REDUCED4 9/12.

Leave-one-origin:
- ChHHO retains lower aggregate SumAE than FULL7 in 24/33 omissions.
- ChHHO retains lower aggregate SumAE than REDUCED4 in 26/33 omissions.

## 4. Reporting-only transport

### 2025
- ChHHO: SumAE 1252.05, direction 9/12.
- FULL7: SumAE 1035.78, direction 11/12.
- REDUCED4: SumAE 1040.82, direction 11/12.

### 2026 Jan-Jul
- ChHHO: SumAE 1178.14, direction 5/7.
- FULL7: SumAE 1401.32, direction 5/7.
- REDUCED4: SumAE 1438.58, direction 5/7.

Interpretation:
- ChHHO is stronger in the 2026 stress window on price error.
- ANN ensembles are stronger in 2025 transport.
- No model is uniformly best across all regimes.

## 5. Controlled no-fit cross-family ensemble diagnostics
Only role-defined, no-fit equal averages and a small frozen grid were inspected. No combinatorial subset search.

### ChHHO + REDUCED4 equal average
DEV:
- SumAE 1388.7364
- Direction 21/33
- MAE 42.0829
- RMSE 53.3402

2025:
- SumAE 1104.8512
- Direction 9/12

2026:
- SumAE 1037.3573
- Direction 6/7

This is a useful PRICE-ERROR ENSEMBLE BENCHMARK, but direction is weaker on DEV than either parent.

### ChHHO + FULL7 equal average
DEV:
- SumAE 1404.1152
- Direction 22/33

2025:
- SumAE 1125.5600
- Direction 9/12

2026:
- SumAE 1016.0599
- Direction 6/7

### ChHHO + SMA-ELMFIS equal average
DEV:
- SumAE 1314.3674
- Direction 24/33

But transport/stress is not stable:
- 2025 SumAE 1408.3209, direction 8/12
- 2026 SumAE 1595.2911, direction 3/7

### ChHHO magnitude + SMA sign
DEV:
- SumAE 1343.8766
- Direction 25/33

Reporting:
- 2025 SumAE 1157.0386, direction 10/12
- 2026 SumAE 2040.1395, direction 3/7

Decision: SMA hard-direction combinations are NOT promoted because the DEV gain does not transport consistently, repeating the prior SMA-overlay warning.

## 6. Learned-weight test
Expanding prequential fixed-grid weight selection:

ChHHO + REDUCED4:
- DEV SumAE 1472.4153
- Direction 22/33

ChHHO + FULL7:
- DEV SumAE 1446.7335
- Direction 22/33

ChHHO + HHO:
- DEV SumAE 1446.3209
- Direction 21/33

Therefore learned/adaptive cross-family weights are not supported by honest prequential DEV evidence.
No stacking/meta-learner is opened.

## 7. Final working hierarchy

### Primary single-model monthly price role
ChHHO-ANFIS
- current lowest DEV SumAE among frozen family champions;
- direction stronger than prior FULL7;
- deterministic rerun confirmed;
- survives leave-one-origin robustness reasonably well.

### Price-error ensemble benchmark
Equal ChHHO + REDUCED4
- lower DEV SumAE than either parent;
- strong 2026 reporting;
- direction sacrifice prevents it from replacing ChHHO as the balanced primary.

### Balanced price/direction challenger
REDUCED4 ANN
- slightly higher price error;
- stronger DEV direction 24/33;
- strongest 2025 transport among these main candidates.

### Direction specialist
SMA-ELMFIS
- 25/33 DEV direction;
- retain as confirmation/disagreement specialist only;
- no hard override.

### ELM role
AOA-ELM/TLBO-ELM retained as single-model benchmark family only.

## 8. Governance decision
- ANFIS family: COMPLETE.
- ANN family: COMPLETE.
- ELM family: COMPLETE.
- ELMFIS family: COMPLETE.
- Final cross-family audit: COMPLETE.
- Random split: NONE.
- Target-period leakage: NONE.
- 2025/2026 used for tuning/weight selection: NO.
- DB writes: NONE.
- Learned ensemble/stacking expansion: CLOSED under current sample size.

Current research conclusion:
ChHHO-ANFIS is the new primary single-model monthly candidate, while REDUCED4 ANN and SMA-ELMFIS retain complementary direction roles. No single method is uniformly superior across all historical regimes.
