# GOLD MONTHLY — FAILURE ANATOMY BEFORE HYBRIDIZATION

**Date:** 2026-10-02  
**Purpose:** Diagnose the monthly problem before designing another hybrid model.

## Evidence used

Origin-level predictions were audited for the common DEV window 2022-04..2024-12 (n=33) from:

- ChHHO-ANFIS
- FULL7 equal-weight ANN ensemble
- REDUCED4 equal-weight ANN ensemble
- RBFNN Stage-4 FULL simple-average ensemble
- RBFNN Stage-4 REDUCED simple-average ensemble

2025 and 2026 Jan-Jul were used only as transport/stress diagnostics.

The RBFNN rows in this audit are Stage-4 ensemble rows, not the single DE-ABC RBFNN leader.

## 1. The main problem is directional asymmetry, not uniformly weak models

DEV side-specific recall:

| Model | Direction | UP recall | DOWN recall | DEV SigmaAE |
|---|---:|---:|---:|---:|
| ChHHO-ANFIS | 23/33 = 69.70% | 64.71% | **80.00%** | **1413.03** |
| FULL7 ANN | 22/33 = 66.67% | 76.47% | 60.00% | 1428.86 |
| REDUCED4 ANN | **24/33 = 72.73%** | **82.35%** | 66.67% | 1431.46 |
| RBFNN FULL average | 20/33 = 60.61% | 70.59% | 53.33% | 1453.79 |
| RBFNN REDUCED average | 20/33 = 60.61% | 76.47% | 46.67% | 1493.51 |

The strongest families are asymmetric in opposite directions:

- ChHHO is the strongest DOWN specialist in this row-level set.
- REDUCED4 ANN is the strongest UP specialist.
- Therefore a hybrid should not average them blindly; it should decide when each directional specialty is credible.

## 2. Regime composition changes make a single global direction bias unstable

2025 contained:
- 11 UP months
- 1 DOWN month.

Direction accuracy:
- ChHHO: 75.00%
- FULL7 ANN: 91.67%
- REDUCED4 ANN: 91.67%
- RBFNN FULL average: 83.33%.

2026 Jan-Jul contained:
- 2 UP months
- 5 DOWN months.

Direction accuracy:
- ChHHO: 71.43%
- FULL7 ANN: 71.43%
- REDUCED4 ANN: 71.43%
- RBFNN FULL average: 85.71%.

This is consistent with the DEV anatomy: models with stronger UP recall look excellent in an UP-dominated year, while DOWN-specialist behavior matters more when the regime reverses.

## 3. Naive averaging is unlikely to solve the problem

DEV signed forecast-error correlations are very high:

- ChHHO vs ANN FULL7: 0.91
- ChHHO vs ANN REDUCED4: 0.89
- ANN FULL7 vs ANN REDUCED4: 0.99
- ANN vs RBFNN ensemble errors: roughly 0.96-0.97.

Thus most models share the same large price-error shocks.

A majority direction vote across the five audited models reaches only:
- 69.70% DEV direction accuracy

which does not beat the strongest individual direction model.

Conclusion:
- price averaging can reduce variance;
- simple voting does not address the systematic side/regime failure.

## 4. There is real complementarity, but it is sparse

Across 33 DEV months:

- all five models correct: 14 months
- all five wrong: 5 months
- only one model correct: 4 months
- in all four single-rescuer months, that model was ChHHO.

Single-rescuer ChHHO months:
- 2022-10
- 2023-03
- 2024-03
- 2024-06.

When ChHHO is wrong, REDUCED4 ANN is correct on about 50% of those ChHHO-error months.

When REDUCED4 ANN is wrong, ChHHO is correct on about 44% of those months.

This is exactly the type of complementarity a router can exploit if the correct expert can be identified from origin-known state variables.

## 5. Some months are structural common failures

All audited models miss:

- 2023-05
- 2023-07
- 2023-08
- 2023-10
- 2024-11.

Note:
- 2023-10 has actual monthly price equal to the previous-month anchor, so the project's sign-direction rule assigns an exact zero direction. A non-zero forecast cannot score that month as direction-correct. It should be treated separately in directional error anatomy.

The remaining common-failure months are more important for model development because switching among existing families cannot repair them.

## 6. Agreement itself contains useful reliability information

Five-model unanimous-direction DEV calls:
- 19 / 33 months = 57.58% coverage
- accuracy = **73.68%**.

Transport/stress diagnostics:
- 2025 unanimous calls: 9/12, accuracy 88.89%
- 2026 Jan-Jul unanimous calls: 3/7, accuracy 100%.

The external samples are small and already opened, so these percentages are diagnostic only. Still, they support a model hypothesis:

> cross-family agreement/disagreement should be an explicit predictor of reliability, not discarded by averaging.

## 7. What should be preserved

A new monthly architecture should preserve:

1. **Price magnitude**
   - ChHHO / RBFNN / ANN price forecasts are already competitive.
   - Do not replace them with another unconstrained price learner.

2. **ChHHO DOWN specialization**
   - DEV DOWN recall 80%.

3. **REDUCED4 ANN UP specialization**
   - DEV UP recall 82.35%.

4. **Cross-family consensus**
   - unanimous directions are materially more reliable on DEV.

## 8. What must be improved

1. Identify when the current market is an UP-specialist or DOWN-specialist environment using only origin-known variables.
2. Detect disagreement regimes where one family should override another.
3. Detect common-failure states where all families are likely unreliable.
4. Avoid learned continuous ensemble weights; previous ANN weight optimization already showed meta-overfit with n=33.
5. Do not fit a high-capacity stacking model on 33 DEV origins.

## 9. Recommended new architecture

Working name:

**ADCR — Asymmetric Directional Consensus Router**

It should be a low-capacity overlay, not another base forecaster.

Inputs to the router:
- direction forecast from ChHHO
- direction forecast from REDUCED4 ANN
- optionally RBFNN DE-ABC / RBFNN family direction once exact origin rows are integrated
- absolute forecast displacement from RW for each family
- cross-family forecast spread
- number/fraction of experts agreeing UP vs DOWN
- origin-known CURRENT8 state
- simple regime descriptors derived only from origin-known history.

Core rule:
- unanimous/strong consensus: preserve consensus;
- disagreement: choose between the historically strong UP specialist and strong DOWN specialist using a chronological side-specific reliability model;
- common-failure / low-reliability state: mark UNCERTAIN or preserve the best price anchor without claiming strong direction.

Price magnitude:
- preserve a strong frozen price anchor;
- router changes sign only when its reliability rule is satisfied.

## 10. Paper hypothesis

A defensible paper hypothesis is:

> Monthly gold forecasting error is directionally asymmetric across heterogeneous model families. A low-capacity, side-specific cross-family reliability router can preserve the price accuracy of strong base forecasters while improving weak-direction recall and avoiding the meta-overfit associated with continuous ensemble weighting.

This hypothesis follows directly from the observed model anatomy and is preferable to inventing another optimizer before diagnosing the existing errors.
