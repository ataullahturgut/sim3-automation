# GOLD MONTHLY FORECAST — ANFIS STAGE 4.2 ENSEMBLE BASELINES

Date: 2026-09-26
Status: COMPLETE
Pools: frozen in Stage 4.1 before any ensemble evaluation.

## Authority
- DEV only for model/variant assessment: 2022-04..2024-12, n=33.
- 2025/2026 reporting only.
- No retraining of base ANFIS models.
- Original successful prediction artifacts only.
- Random split: none.
- Target-month leakage: none.

## Frozen pools

FULL5:
- Vanilla
- ChHHO
- MFO
- HHO
- MPA-CPA

REDUCED4:
- Vanilla
- ChHHO
- HHO
- MPA-CPA

## Evaluated baseline variants

1. SIMPLE_AVERAGE
2. MEDIAN
3. EXPANDING_PREQUENTIAL_INVERSE_MAE
   - first 6 DEV origins equal-weight;
   - thereafter weights use only prior DEV origins;
   - weights proportional to inverse prior MAE;
   - no future DEV origin contributes to current weight.

## DEV results

| Pool | Variant | ΣAE | Direction | MAE | MAPE % | RMSE | Rel MAE vs RW |
|---|---|---:|---:|---:|---:|---:|---:|
| FULL5 | Simple average | 1455.0858 | 21/33 = 63.64% | 44.0935 | 2.14967 | 57.9015 | 0.82769 |
| FULL5 | Median | 1560.6489 | 22/33 = 66.67% | 47.2924 | 2.30843 | 60.9636 | 0.88774 |
| FULL5 | Prequential inverse-MAE | 1464.6751 | 21/33 = 63.64% | 44.3841 | 2.16651 | 58.2689 | 0.83315 |
| REDUCED4 | Simple average | **1451.0643** | **23/33 = 69.70%** | **43.9716** | **2.14903** | **57.4237** | **0.82541** |
| REDUCED4 | Median | 1490.2975 | 23/33 = 69.70% | 45.1605 | 2.20330 | 58.6174 | 0.84772 |
| REDUCED4 | Prequential inverse-MAE | 1460.5157 | 22/33 = 66.67% | 44.2581 | 2.16643 | 57.8422 | 0.83078 |

Reference ChHHO-ANFIS single:
- DEV ΣAE 1413.0298
- direction 23/33
- MAE 42.8191
- RMSE 54.8274

## Main finding

No Stage 4.2 baseline ensemble beats ChHHO-ANFIS on DEV ΣAE.

Best ensemble baseline:
- REDUCED4 simple average = 1451.0643 / 23/33.

Compared with ChHHO:
- price error worsens by 38.0345 USD cumulative AE;
- direction is unchanged at 23/33.

Therefore basic aggregation does not improve the current ANFIS price leader.

## Frozen inverse-MAE external weights

FULL5 final all-DEV inverse-MAE weights for reporting only:
- Vanilla 18.06%
- ChHHO 23.67%
- MFO 20.52%
- HHO 20.32%
- MPA-CPA 17.43%

REDUCED4:
- Vanilla 22.72%
- ChHHO 29.78%
- HHO 25.56%
- MPA-CPA 21.93%

## External reporting only

### FULL5
2025:
- simple ΣAE 1058.2611 / 8/12
- median 1242.8932 / 8/12
- frozen inverse-MAE 1058.2571 / 8/12

2026 Jan-Jul:
- simple 1480.9659 / 4/7
- median 1459.9523 / 5/7
- frozen inverse-MAE 1443.8735 / 4/7

### REDUCED4
2025:
- simple 1102.8411 / 8/12
- median 1313.6746 / 7/12
- frozen inverse-MAE 1086.8488 / 8/12

2026 Jan-Jul:
- simple 1468.7008 / 5/7
- median 1501.4557 / 4/7
- frozen inverse-MAE 1421.6361 / 5/7

These external figures did not affect the Stage 4.2 decision.

## Decision

- REDUCED4 simple average: retain as best Stage 4.2 ensemble baseline.
- FULL5 simple average: retain as role-complete benchmark.
- Median ensemble: do not promote.
- Inverse-MAE weighting: do not promote based on Stage 4.2.
- ChHHO remains the strongest ANFIS DEV price candidate.

Next authorized step:
Stage 4.3 — learned/simplex weight experiment under honest expanding-prequential DEV.

## Control and compliance
- Stage 4.1 frozen pools unchanged: PASS.
- DEV-only variant assessment: PASS.
- 2025/2026 excluded from selection: PASS.
- Honest prequential weighting: PASS.
- Stage 4.2: COMPLETE.
