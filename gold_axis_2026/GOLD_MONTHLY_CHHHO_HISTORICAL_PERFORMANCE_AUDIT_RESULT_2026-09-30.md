# GOLD MONTHLY — Historical ChHHO Performance Audit Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS  
**Workflow:** Gold Monthly ChHHO Historical Performance Audit V1  
**Run:** **36698427012**  
**Artifact:** **11088508878**  
**Authority commit:** `9e260efc73b421b79ecea8f0f8217e1f5bf00e81`  
**Code commit:** `1ac65d66871f5edacdac4dd108395958bd17e434`  
**Workflow commit:** `ed43d05a7ae9ff41c50c2eebd0639088d048ce08`

## 1. Main conclusion

The historical ChHHO evidence must be split into three blocks.

### H1 — 2013-09..2021-10 counterfactual same-method replay
This block is **not effective as a forecasting baseline**:
- n = 98
- ΣAE = **6141.85 USD**
- MAE = **62.67 USD**
- MAPE = **4.65%**
- RMSE = **155.06 USD**
- direction = **54/98 = 55.1%**
- relative MAE vs random walk = **1.90**
- HIGH_AE months = **25/98**
- worst target = **2019-03**, AE **1290.22 USD**, APE **99.17%**

The counterfactual model is materially worse than random walk overall and contains extreme unstable forecasts.

Therefore H1 must **not** be used as strong ChHHO-specific alarm validation evidence.

### H2 — 2021-11..2022-03 valid same-method pre-DEV
This block is scientifically admissible:
- n = 5
- ΣAE = **208.32 USD**
- MAE = **41.66 USD**
- MAPE = **2.29%**
- direction = **2/5 = 40%**
- relative MAE vs RW = **0.886**
- HIGH_AE months = **1/5**
- worst = **2021-12**, AE **85.62 USD**

Small sample, but forecast error is not globally pathological.

### H3 — 2022-04..2024-12 frozen canonical DEV
This is the canonical model block:
- n = 33
- ΣAE = **1413.03 USD**
- MAE = **42.82 USD**
- MAPE = **2.11%**
- RMSE = **54.83 USD**
- direction = **23/33 = 69.7%**
- relative MAE vs RW = **0.804**
- HIGH_AE months = **8/33**

This block shows the main ChHHO model is materially better than random walk on canonical DEV.

## 2. H1 yearly performance

| Year | n | MAE USD | MAPE | Dir | Rel.MAE vs RW | HIGH_AE |
|---|---:|---:|---:|---:|---:|---:|
| 2013* | 4 | 138.07 | 10.65% | 50.0% | 4.25 | 3 |
| 2014 | 12 | 64.94 | 5.08% | 33.3% | 2.14 | 4 |
| 2015 | 12 | 40.69 | 3.45% | 58.3% | 1.41 | 2 |
| 2016 | 12 | 76.65 | 6.22% | 50.0% | 2.03 | 3 |
| 2017 | 12 | 21.61 | 1.73% | 66.7% | 0.85 | 0 |
| 2018 | 12 | 23.29 | 1.83% | 58.3% | 1.03 | 0 |
| 2019 | 12 | 143.27 | 10.77% | 58.3% | 4.51 | 5 |
| 2020 | 12 | 52.17 | 2.95% | 66.7% | 1.02 | 4 |
| 2021* | 10 | 51.83 | 2.90% | 50.0% | 1.41 | 4 |

*Partial year.

The block is heterogeneous: 2017-2018 are reasonable, while 2013-2016 and especially 2019 are poor.

## 3. H1 HIGH_AE months

AE > 63.06 USD:

- 2013-09 — 123.23
- 2013-10 — 124.65
- 2013-11 — 260.12
- 2014-01 — 81.20
- 2014-02 — 364.06
- 2014-03 — 63.88
- 2014-09 — 64.78
- 2015-01 — 65.08
- 2015-03 — 168.35
- 2016-02 — 119.84
- 2016-03 — 488.10
- 2016-10 — 80.02
- 2019-03 — 1290.22
- 2019-06 — 71.79
- 2019-08 — 71.55
- 2019-10 — 77.48
- 2019-11 — 75.87
- 2020-03 — 75.70
- 2020-04 — 125.50
- 2020-07 — 77.01
- 2020-12 — 105.52
- 2021-03 — 89.42
- 2021-04 — 68.87
- 2021-06 — 88.28
- 2021-08 — 80.02

## 4. H2/H3 HIGH_AE months

H2:
- **2021-12 — 85.62**

H3:
- 2022-05 — 79.94
- 2022-07 — 64.95
- 2022-11 — 102.20
- 2023-01 — 100.74
- 2023-08 — 77.53
- 2024-03 — 131.58
- 2024-07 — 71.01
- 2024-11 — 119.13

## 5. Numerical stability audit of worst H1 cases

Several H1 disasters coincide with very poor design-matrix conditioning.

Examples:

### 2019-03
- forecast = **10.78 USD**
- actual = **1301 USD**
- predicted log return = **-4.8077**
- AE = **1290.22 USD**
- design condition number ≈ **2.32e24**

### 2016-03
- forecast = **1733.10**
- actual = **1245**
- predicted log return = **+0.3676**
- AE = **488.10**
- condition ≈ **3.03e3**

### 2014-02
- forecast = **935.94**
- actual = **1300**
- predicted log return = **-0.2845**
- AE = **364.06**
- condition ≈ **5.10e6**

### 2015-03
- forecast = **1010.65**
- actual = **1179**
- AE = **168.35**
- condition ≈ **5.55e33**

### 2020-04
- forecast = **1557.50**
- actual = **1683**
- AE = **125.50**
- condition ≈ **1.65e18**

Binding interpretation:
- H1 is not merely a slightly weaker historical period.
- It contains counterfactual extrapolation/numerical-instability failures.
- These H1 errors cannot be used as clean evidence that E/G did or did not predict ChHHO failure.

## 6. Where E and G fire

### Pre-discovery market-state occurrences

#### E-level (>20% above prior MA12)
Origins / targets:
- 2011-08 -> 2011-09 — main model unbuildable
- 2011-09 -> 2011-10 — main model unbuildable
- 2020-08 -> 2020-09 — H1 buildable
- 2024-10 -> 2024-11 — canonical H3

Model outcomes where available:
- 2020-09: **full E TRUE**, AE **26.68**, APE 1.39% — NOT high error
- 2024-11: E-level TRUE but **full E FALSE**, AE **119.13** — high error, already D mechanism

Thus full E pre-discovery model-specific evidence remains:
- 1 buildable full-E event
- 0 high-error events

#### G (Gold 3m <= -10%)
Origins / targets:
- 2013-04 -> 2013-05 — main model unbuildable
- 2013-05 -> 2013-06 — unbuildable
- 2013-06 -> 2013-07 — unbuildable
- 2013-07 -> 2013-08 — unbuildable
- 2016-12 -> 2017-01 — H1 buildable
- 2022-07 -> 2022-08 — canonical H3

Available model outcomes:
- 2017-01: AE **33.75**, APE 2.83% — NOT high error
- 2022-08: AE **35.85**, APE 2.03% — NOT high error

Thus available pre-discovery G model-specific evidence:
- 2 buildable events
- 0 high-error events

But independent market-state history still shows G is associated with larger subsequent Gold movement.

## 7. Later discovery-period occurrences

These are not independent validation.

### Full E
- 2025-05 — high ChHHO error
- 2025-11 — high ChHHO error
- 2026-01 — high ChHHO error
- 2026-03 — high ChHHO error

### G
- 2026-07 — high ChHHO error
- 2026-08 — high ChHHO error

## 8. Binding conclusion

1. The old H1 counterfactual ChHHO replay is **not an effective historical forecast baseline** and must not be used as if it were a clean backtest.
2. H2 and especially H3 show the actual current model becomes reasonable/effective in the scientifically governed period.
3. E remains unvalidated as a model-error alarm.
4. G remains a valid historical market-risk / high-movement warning, but available clean model-specific evidence does not validate it as a ChHHO high-error alarm.
5. Historical market-state evidence for G remains usable because it does not depend on the unstable H1 model.
6. H1 model-specific alarm conclusions are downgraded to exploratory diagnostics only.
