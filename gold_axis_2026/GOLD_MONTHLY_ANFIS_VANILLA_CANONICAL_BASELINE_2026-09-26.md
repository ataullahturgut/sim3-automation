# GOLD MONTHLY FORECAST — VANILLA ANFIS CANONICAL BASELINE

Date: 2026-09-26
Status: COMPLETE / FROZEN BASELINE
Canonical run: 36203300191 — SUCCESS / OUTPUT_GATE=PASS
Artifact: 10893275355
Script: gold_axis_2026/tools/vw_midas_anfis_vanilla_v3_checked.py

## Authority basis
Jang (1993), ANFIS: Adaptive-Network-Based Fuzzy Inference System, IEEE TSMC 23(3), 665-685, DOI 10.1109/21.256541.
Canonical hybrid learning: consequent parameters by least squares in forward pass; premise parameters by gradient descent in backward pass.
Jang step-size logic retained: initial 0.01, +10% after four consecutive error reductions, -10% after two alternating increase/decrease combinations.
Checking-data selection is used to prevent premise over-training.

## Project adaptation
- 8 unchanged governed VW-MIDAS inputs.
- 4 Gold/Silver/Platinum/Palladium return outputs jointly.
- First-order Sugeno/TSK.
- 5 compact Gaussian rules.
- Product AND and normalized firing.
- Training-only deterministic k-means initialization to avoid 8-input grid rule explosion.
- No metaheuristic.
- Per-origin chronological inner checking: last 20% of pre-target history, minimum 12 observations.
- Epoch chosen by minimum checking MSE, then model refit on all origin-safe history for the chosen epoch count.
- Maximum 100 epochs.
- No random split.
- DB READ_ONLY.
- Target month excluded.
- 2025 and 2026 excluded from method selection.

## Verification history
- V1 fixed-step pilot ran successfully but was not accepted as canonical because all origins still improved at the 50-epoch boundary.
- A subsequent attempted patch produced a compile-only failure and no scientific result.
- V2 Jang-step run passed but showed training-boundary overfit: most origins minimized training error near epoch 100.
- V3 added canonical checking-data control and is the accepted baseline.
- Independent finite-difference verification of analytic premise gradients showed max discrepancies about 1.2e-10 for centers and 1.4e-9 for log-spreads.

## Final results
| Period | n | Sum AE USD | Direction | MAE | MAPE % | RMSE | Relative MAE vs RW |
|---|---:|---:|---:|---:|---:|---:|---:|
| DEV 2022-04..2024-12 | 33 | 1852.0465 | 21/33 = 63.64% | 56.1226 | 2.7080 | 69.8707 | 1.0535 |
| 2025 transport | 12 | 1515.6415 | 9/12 = 75.00% | 126.3035 | 3.6924 | 162.1034 | 0.8984 |
| 2026 Jan-Jul stress | 7 | 2027.0317 | 4/7 = 57.14% | 289.5760 | 6.2912 | 330.8185 | 1.2226 |

DEV yearly:
- 2022: Sum AE 425.2522; direction 6/9 = 66.67%.
- 2023: Sum AE 608.2073; direction 6/12 = 50.00%.
- 2024: Sum AE 818.5870; direction 9/12 = 75.00%.

Checking diagnostics:
- DEV selected epochs: median 22, min 1, max 87; 0/33 at max epoch.
- 2025 selected epochs: median 17, min 1, max 53; 0/12 at max epoch.
- 2026 selected epochs: median 17, min 1, max 18; 0/7 at max epoch.

## Comparison
Vanilla ELMFIS DEV: Sum AE 1996.2933; direction 20/33.
Vanilla ANFIS improves the unoptimized ELMFIS baseline to Sum AE 1852.0465 and 21/33 direction.

Current global leaders remain:
- FULL7 ANN: Sum AE 1428.86; direction 22/33.
- REDUCED4 ANN: Sum AE 1431.46; direction 24/33.
- SMA-ELMFIS: Sum AE 1651.45; direction 25/33.

Therefore Vanilla ANFIS is materially better than Vanilla ELMFIS, but it does not enter the current global DEV Pareto frontier.

## Decision
- Vanilla ANFIS implementation: ACCEPT as canonical baseline.
- ANFIS family: NOT CLOSED by baseline result.
- Hybrid/metaheuristic ANFIS: NOT STARTED; requires user stage-gate approval.
- 2025/2026 results are reporting/stress only and did not affect this decision.
