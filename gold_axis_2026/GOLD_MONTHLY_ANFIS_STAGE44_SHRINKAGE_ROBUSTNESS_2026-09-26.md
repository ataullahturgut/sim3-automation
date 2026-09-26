# GOLD MONTHLY FORECAST — ANFIS STAGE 4.4 SHRINKAGE ROBUSTNESS

Date: 2026-09-26
Status: COMPLETE

## Purpose
Stage 4.3 showed severe meta-overfit in unregularized optimized simplex weights.
Stage 4.4 applies the ANN-parity controlled shrinkage remedy:

w_alpha = (1-alpha) * w_equal + alpha * w_optimized

Alpha grid:
0.00, 0.10, 0.25, 0.50, 0.75, 1.00.

For every DEV target:
- first 6 origins use equal weights;
- afterward w_optimized is fit only on earlier DEV origins by exact L1 simplex optimization;
- current/future origins are excluded;
- shrinkage is applied to that origin-safe optimized vector.

Pools remain frozen from Stage 4.1.

## FULL5 prequential alpha curve

| Alpha | DEV ΣAE | Direction | MAE | MAPE % | RMSE |
|---:|---:|---:|---:|---:|---:|
| 0.00 | **1455.0858** | 21/33 | **44.0935** | **2.14967** | **57.9015** |
| 0.10 | 1461.2074 | 21/33 | 44.2790 | 2.16177 | 58.2201 |
| 0.25 | 1470.3897 | 21/33 | 44.5573 | 2.17992 | 58.7638 |
| 0.50 | 1485.6937 | 20/33 | 45.0210 | 2.21018 | 59.8401 |
| 0.75 | 1507.3368 | 21/33 | 45.6769 | 2.25012 | 61.1190 |
| 1.00 | 1535.0724 | 21/33 | 46.5173 | 2.29935 | 62.5881 |

Chosen alpha = **0.00**.

## REDUCED4 prequential alpha curve

| Alpha | DEV ΣAE | Direction | MAE | MAPE % | RMSE |
|---:|---:|---:|---:|---:|---:|
| 0.00 | **1451.0643** | **23/33** | **43.9716** | **2.14903** | **57.4237** |
| 0.10 | 1464.7901 | **23/33** | 44.3876 | 2.17323 | 57.6311 |
| 0.25 | 1485.3788 | 22/33 | 45.0115 | 2.20952 | 58.1348 |
| 0.50 | 1519.6932 | 21/33 | 46.0513 | 2.27001 | 59.4715 |
| 0.75 | 1557.5007 | 21/33 | 47.1970 | 2.33584 | 61.3929 |
| 1.00 | 1607.0930 | 21/33 | 48.6998 | 2.41965 | 63.8463 |

Chosen alpha = **0.00**.

## Reference
ChHHO-ANFIS single:
- DEV ΣAE 1413.0298
- direction 23/33
- MAE 42.8191
- RMSE 54.8274

## Interpretation
Both frozen pools independently select alpha=0.

This means:
- no optimized-simplex contribution is supported;
- the best shrinkage point is the equal-weight endpoint;
- every movement toward learned simplex weights worsens DEV cumulative price error;
- in REDUCED4, direction also deteriorates beyond alpha=0.10.

This is direct evidence that n=33 does not support reliable model-specific weight learning for the ANFIS ensemble pool.

The result mirrors the ANN Stage 4.2 finding, where equal weights also dominated the shrinkage path.

## Decision
- FULL5 chosen alpha = 0.
- REDUCED4 chosen alpha = 0.
- Learned/shrunk ANFIS ensemble weights are CLOSED.
- No further weight-grid, generic stacking, or arbitrary weight optimization is authorized under the current evidence set.
- ChHHO single remains better than both equal-weight endpoints, so no ANFIS ensemble is promoted as primary.

Next authorized step:
Stage 4.5 — final ANFIS ensemble robustness/freeze audit:
- year-by-year;
- leave-one-origin;
- pairwise origin-level comparison;
- leave-one-component-out diagnostic only;
- tail/numerical stability;
- final ANFIS role freeze.

## Control and compliance
- Stage 4.1 pools unchanged: PASS.
- Chronological prequential weighting: PASS.
- 2025/2026 excluded from alpha choice: PASS.
- Random split: NONE.
- Target leakage: NONE.
- Stage 4.4: COMPLETE.
