# GOLD MONTHLY FORECAST — ANFIS STAGE 4.3 OPTIMIZED SIMPLEX WEIGHTS

Date: 2026-09-26
Status: COMPLETE

## Authority
- Pools frozen in Stage 4.1.
- DEV only: 2022-04..2024-12, n=33.
- 2025/2026 reporting only.
- No base-model retraining.
- Random split: none.
- Target-month leakage: none.

## Method
Non-negative simplex weights:
- w_j >= 0
- sum_j w_j = 1
- objective = minimize cumulative absolute price error (ΣAE)
- solved by exact linear programming.

Two evaluations:
1. Full-DEV fit evaluated on the same DEV period — diagnostic only, not honest evidence.
2. Expanding-prequential DEV:
   - first 6 origins use equal weights;
   - thereafter weights are re-fit using only earlier DEV origins;
   - current/future origins are excluded.

## FULL5
Pool:
Vanilla, ChHHO, MFO, HHO, MPA-CPA.

Full-DEV optimized weights:
- Vanilla 0.00%
- ChHHO 59.52%
- MFO 0.00%
- HHO 28.04%
- MPA-CPA 12.44%

Same-sample diagnostic:
- ΣAE 1346.1099
- direction 22/33
- MAE 40.7912
- RMSE 54.2856
- MAPE 2.00519%

Honest expanding-prequential:
- ΣAE 1535.0724
- direction 21/33
- MAE 46.5173
- RMSE 62.5881
- MAPE 2.29935%

## REDUCED4
Pool:
Vanilla, ChHHO, HHO, MPA-CPA.

Full-DEV optimum is mathematically identical to FULL5 because MFO receives zero weight:
- Vanilla 0.00%
- ChHHO 59.52%
- HHO 28.04%
- MPA-CPA 12.44%

Same-sample diagnostic:
- ΣAE 1346.1099
- direction 22/33

Honest expanding-prequential:
- ΣAE 1607.0930
- direction 21/33
- MAE 48.6998
- RMSE 63.8463
- MAPE 2.41965%

## Reference
ChHHO-ANFIS single:
- DEV ΣAE 1413.0298
- direction 23/33
- MAE 42.8191
- RMSE 54.8274

Stage 4.2 best baseline:
- REDUCED4 simple average 1451.0643 / 23/33.

## Interpretation
The in-sample optimized simplex appears to improve ChHHO materially:
1413.03 -> 1346.11.

However this improvement does not survive honest chronological meta-evaluation:
- FULL5 prequential 1535.07
- REDUCED4 prequential 1607.09

Both are materially worse than ChHHO single.

This is direct evidence of ensemble-weight meta-overfit in the n=33 DEV meta-sample.

The full-DEV solution is also sparse:
- zero Vanilla weight;
- zero MFO weight in FULL5;
- ~60% weight on ChHHO.

That sparsity is retained only as diagnostic evidence and is not promoted.

## Reporting-only frozen-weight behavior
If the full-DEV diagnostic weights are frozen and applied externally:

2025:
- ΣAE 1225.8880
- direction 8/12
- MAE 102.1573

2026 Jan-Jul:
- ΣAE 1092.5019
- direction 6/7
- MAE 156.0717

These values do not alter the selection decision because the weights failed honest DEV evaluation.

## Decision
- Optimized simplex: NOT PROMOTED.
- ChHHO remains primary ANFIS price candidate.
- Proceed to Stage 4.4 shrinkage only as a controlled anti-overfit test.
- No arbitrary weight-grid or component-subset expansion is authorized.

## Control and compliance
- Frozen pools unchanged: PASS.
- Full-DEV fit labeled diagnostic only: PASS.
- Honest expanding-prequential evaluation: PASS.
- 2025/2026 excluded from selection: PASS.
- Stage 4.3: COMPLETE.
