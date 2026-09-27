# GOLD MONTHLY — BOOSTING STAGE 4 CAPACITY SCAN REPORT

Date: 2026-09-27
Status: **STAGE 4 COMPLETE — PASS**
Scope: DEV 2022-04..2024-12 only (n=33)
2025/2026: NOT OPENED / NOT EVALUATED

## Objective
With Stage-3 feature / target / loss choices frozen, test controlled model-capacity profiles only.

Primary metric: DEV price SigmaAE.
Secondary: direction correct, MAE, RMSE.

## Baseline reconciliation
Every Stage-3 baseline was reproduced exactly (absolute difference = 0.0):
- CatBoost CURRENT8 RMSE: 1460.433935309605
- GBRT DAILY ABS: 1568.1002319206916
- XGBoost RAW L2: 1695.55569760265
- XGBoost CURRENT8 L2 direction lane: 1778.0649251965765
- LightGBM MIXED20 L1: 1635.4055892431354
- RF DAILY comparator: 1491.5506937156672

## Results

### CatBoost Ordered — CURRENT8 — RMSE

| Profile | SigmaAE | Direction |
|---|---:|---:|
| **C2_BASELINE** depth6 / 100 / lr0.03 | **1460.4339** | 20/33 |
| C0_SHALLOW_100 depth4 / 100 / lr0.03 | 1469.4936 | 19/33 |
| C4_DEEP_LOWLR depth8 / 300 / lr0.02 | 1481.2619 | 22/33 |
| C1_SHALLOW_300 depth4 / 300 / lr0.03 | 1512.7318 | **23/33** |
| C3_MEDIUM_300 depth6 / 300 / lr0.03 | 1534.2701 | 22/33 |

Interpretation:
- Stage-3 baseline remains the **price-error leader**.
- More trees do not improve SigmaAE here.
- C4 is the strongest balanced challenger: only +20.83 SigmaAE versus price leader, but +2 direction months.
- C1 has the highest direction count (23/33) but materially worse price error.

Stage-5 promotion:
- Primary: **C2_BASELINE**.
- Balanced challenger: **C4_DEEP_LOWLR**.
- C1 direction-only result retained as evidence but not primary Stage-5 lane unless a later direction-specific branch is opened.

### GBRT — DAILY_SUMMARY12 — absolute_error

| Profile | SigmaAE | Direction |
|---|---:|---:|
| **G0_SHALLOW** depth2 / 100 / lr0.10 / leaf2 | **1500.4295** | **22/33** |
| G1_SHALLOW_SLOW | 1505.7824 | 20/33 |
| G2_BASELINE | 1568.1002 | 20/33 |
| G3_MEDIUM_SLOW | 1597.2165 | 19/33 |
| G4_HIGHER_CAPACITY | 1602.0473 | 18/33 |

Improvement versus Stage 3:
- 1568.1002 -> **1500.4295**
- gain = **67.6708 SigmaAE**
- direction = 20/33 -> **22/33**

Interpretation:
- This model clearly prefers **shallower trees**.
- Increasing depth degrades both price error and direction.

Stage-5 promotion:
- **G0_SHALLOW**.

### XGBoost — RAW_LEVEL_LAGS8 — squared error

| Profile | SigmaAE | Direction |
|---|---:|---:|
| **X0_SHALLOW_CONSERVATIVE** depth2 / 300 / lr0.03 / child3 | **1673.0823** | **19/33** |
| X3_BASELINE | 1695.5557 | 18/33 |
| X2_MEDIUM | 1762.0058 | 16/33 |
| X4_DEEP_SLOW | 1793.7322 | 18/33 |
| X1_SHALLOW_MEDIUM | 1841.1735 | 17/33 |

Improvement versus Stage 3:
- 1695.5557 -> **1673.0823**
- gain = **22.4733 SigmaAE**
- direction = 18/33 -> **19/33**

Interpretation:
- XGBoost also prefers a conservative shallow profile on the RAW lane.

Stage-5 promotion:
- **X0_SHALLOW_CONSERVATIVE**.

### XGBoost — CURRENT8 direction challenger

| Profile | SigmaAE | Direction |
|---|---:|---:|
| X0_SHALLOW_CONSERVATIVE | **1667.4122** | 18/33 |
| **X2_MEDIUM** | 1724.9639 | **22/33** |
| X3_BASELINE | 1778.0649 | 21/33 |
| X1_SHALLOW_MEDIUM | 1790.3084 | 21/33 |
| X4_DEEP_SLOW | 1795.8156 | 21/33 |

Interpretation:
- The price-error optimum and direction optimum are different.
- X0 gives the best XGBoost CURRENT8 price error but only 18 directions.
- X2 gives **22/33 direction**, improving the prior direction baseline by one month.

Stage-5 status:
- X0 RAW remains primary XGBoost price lane.
- **X2 CURRENT8** retained as a direction challenger only.

### LightGBM — MIXED20 — L1

| Profile | SigmaAE | Direction |
|---|---:|---:|
| **L4_HIGHER_CAPACITY** leaves31 / depth6 / child10 / 300 / lr0.03 | **1534.6087** | **22/33** |
| L2_MEDIUM | 1561.4081 | 19/33 |
| L0_SMALL | 1598.2705 | 20/33 |
| L1_SHALLOW | 1604.6227 | 19/33 |
| L3_BASELINE | 1635.4056 | 22/33 |

Improvement versus Stage 3:
- 1635.4056 -> **1534.6087**
- gain = **100.7969 SigmaAE**
- direction remains **22/33**

Interpretation:
- Unlike GBRT/XGBoost, LightGBM benefits from higher controlled capacity under MIXED20 + L1.
- Lower learning rate with more trees and constrained depth substantially improves price error.

Stage-5 promotion:
- **L4_HIGHER_CAPACITY**.

### Random Forest comparator — DAILY_SUMMARY12

| Profile | SigmaAE | Direction |
|---|---:|---:|
| **R0_BASELINE** | **1491.5507** | 20/33 |
| R2_MEDIUM | 1506.0032 | 21/33 |
| R1_SHALLOW | 1512.3159 | 20/33 |

Decision:
- Keep **R0_BASELINE** as comparator.
- No further RF-specific optimization priority.

## Overall Stage-4 leaders

1. **CatBoost C2_BASELINE** — SigmaAE **1460.4339**, direction 20/33.
2. CatBoost C0_SHALLOW_100 — 1469.4936, direction 19/33.
3. CatBoost C4_DEEP_LOWLR — 1481.2619, direction 22/33.
4. RF comparator R0 — 1491.5507, direction 20/33.
5. **GBRT G0_SHALLOW** — 1500.4295, direction 22/33.
6. CatBoost C1_SHALLOW_300 — 1512.7318, direction **23/33**.
7. **LightGBM L4_HIGHER_CAPACITY** — 1534.6087, direction 22/33.

## Binding interpretation

Capacity matters materially and in algorithm-specific directions:
- CatBoost: baseline capacity is already strongest for price error.
- GBRT: **shallower is better**.
- XGBoost: **shallower/conservative is better** for price error.
- LightGBM: **higher but constrained capacity is better**.
- RF: baseline remains adequate as comparator.

The Boosting family overall leader remains:
**CatBoost CURRENT8 / LOGRET / RMSE / depth6 / 100 trees / lr0.03**
with SigmaAE **1460.4339**.

No Stage-4 capacity profile beats the strongest existing nonlinear project families (~1413–1416), so Boosting is still promising but not yet the overall project leader.

## Stage-5 promoted configurations

Primary lanes:
1. CatBoost C2_BASELINE.
2. GBRT G0_SHALLOW.
3. XGBoost RAW X0_SHALLOW_CONSERVATIVE.
4. LightGBM L4_HIGHER_CAPACITY.

Retained challengers:
- CatBoost C4_DEEP_LOWLR as price/direction-balanced challenger.
- XGBoost CURRENT8 X2_MEDIUM as direction challenger.

Comparator:
- RF R0_BASELINE.

Stage 5 will change only regularization/subsampling controls. Feature, target, loss and promoted capacity remain frozen.

## Provenance
- Run ID: 36317344803
- Job ID: 108614445222
- Commit: 0824441f4b2c1f78f271cb0afd108f975ff6f21e
- Artifact ID: 10930749198
- Artifact SHA256: d7acd5c265610956667d7b52bd9d1b948ebfe07d557ca1592d48dd2d9e93628e
- Deterministic payload SHA256: 01ca046fad1359e7a43d14b3985350961357906b897d533af50e89b4406f3a84

## Kontrol ve Uyum Özeti
- Stage 4: PASS.
- Stage-3 baseline reconciliation: PASS / exact.
- Determinism: PASS.
- Feature changed: NO.
- Target/loss changed: NO.
- Regularization/subsampling search: NONE.
- Random split: NONE.
- 2025/2026 opened: NO.
- DB writes: NONE.
- Next stage: Stage 5 Regularization & Subsampling only.
