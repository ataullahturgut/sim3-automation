# GOLD MONTHLY FORECAST — ANFIS STAGE 2 PARENT FREEZE

Date: 2026-09-26
Status: COMPLETE
Selection authority: DEV 2022-04..2024-12 only

## Broad screen closure
- Vanilla ANFIS anchor: DEV SumAE 1852.0465, direction 21/33.
- 32 metaheuristic ANFIS hybrids were executed.
- 27 passed the scientific forecast gate.
- 5 were rejected by the gate because at least one reported forecast had pathological return magnitude: ABC, WOA, FPA, HGS, AOA.
- Rejected models are not eligible as Stage-2 parents even when their DEV point looks attractive.

## DEV Pareto parents among scientifically valid hybrids
### MFO-ANFIS — price parent
- SumAE 1630.3324527130
- Direction 20/33 = 60.61%
- MAE 49.4040
- RMSE 65.3297
- Relative MAE vs RW 0.92738
- Worst APE 8.3751%
- Year SumAE: 2022 405.3168; 2023 497.9625; 2024 727.0532

### HHO-ANFIS — direction/balance parent
- SumAE 1646.1336302364
- Direction 23/33 = 69.70%
- MAE 49.8828
- RMSE 64.2761
- Relative MAE vs RW 0.93637
- Worst APE 7.9854%
- Year SumAE: 2022 439.0662; 2023 545.7450; 2024 661.3224

## Complementarity diagnostic
MFO/HHO signed-error correlation = 0.69370.
A diagnostic equal-weight average gives SumAE 1484.3500 but only 19/33 direction.
This is NOT an authorized ensemble; it shows price-error complementarity with direction degradation.

## Frozen roles
- Vanilla ANFIS: architecture anchor only.
- MFO-ANFIS: primary price parent.
- HHO-ANFIS: direction/balance parent.
- Other valid broad-screen models: reserve/benchmark only.
- ABC/WOA/FPA/HGS/AOA: scientific-gate rejects, ineligible as parents.

## Governance
No 2025/2026 metric was used to choose parents.
No random split.
No target-month leakage.
DB remained READ_ONLY.
