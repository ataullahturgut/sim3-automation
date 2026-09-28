# GOLD MONTHLY FORECAST — BOOSTING STAGE 6C-D0 CAUSAL VMD–XGBOOST RESULT

Date: 2026-09-28
Status: COMPLETE / SCIENTIFIC GATE PASS / NOT PROMOTED / D1 CLOSED_NOT_OPENED

## Method
Canonical causal VMD representation feeding the frozen Stage-5 XGBoost X_R4_COMBO learner.

Authority:
- Guo et al. (2025), Computational Economics 66(2), 1157-1189.
  DOI: 10.1007/s10614-024-10736-9.
- Dragomiretskiy & Zosso (2014), IEEE Transactions on Signal Processing 62(3), 531-544.
  DOI: 10.1109/TSP.2013.2288675.
- vmdpy 0.2 reference implementation.

Gold-paper standalone D0 VMD parameters: NOT_FOUND.
Pre-outcome frozen canonical parameters:
- alpha=2000
- tau=0
- K=3
- DC=0
- init=1
- tol=1e-7

Representation:
- monthly Gold prefix through t-1 only
- if prefix length odd, drop oldest month to preserve the t-1 endpoint
- three VMD mode endpoints + residual endpoint
- feature dimension=4
- each historical training row decomposed from its own prefix
- global decomposition BLOCKED

## Scientific gates
- VMD smoke/determinism gate: PASS
- Output gate: PASS
- Scientific gate: PASS
- DB authority invariants unchanged: PASS
- Max reconstruction relative error: 0.0
- vmdpy package: 0.2
- Features requiring oldest-month drop for parity: 60
- Feature payload SHA256: 60ebaf3a6c43b85497e805a190001d28d8cc15d71f08af3eaa89bd7e1c300a60

Residual energy ratio:
- mean: 0.0023394709975851245
- median: 0.00264569994809864
- max: 0.0034887189664831444

## Frozen XGBoost CURRENT8 comparator
- DEV SigmaAE: 1583.8534958594905
- MAE: 47.9955604806
- RMSE: 61.0528338569
- MAPE: 2.3212903741%
- relative MAE vs RW: 0.9009405551
- direction: 20/33 = 60.61%

Yearly:
- 2022: SigmaAE 383.0717717760, direction 5/9
- 2023: SigmaAE 471.8753196693, direction 7/12
- 2024: SigmaAE 728.9064044142, direction 8/12

## Causal VMD-XGBoost
- DEV SigmaAE: 2019.062388221052
- MAE: 61.1837087340
- RMSE: 72.9859405817
- MAPE: 2.9966202810%
- WAPE: 2.9712726811%
- relative MAE vs RW: 1.1484996520
- direction: 15/33 = 45.45%
- worst AE: 172.8726087609 (2024-04)

Yearly:
- 2022: SigmaAE 578.2272320349, direction 3/9
- 2023: SigmaAE 588.8682899964, direction 5/12
- 2024: SigmaAE 851.9668661897, direction 7/12

## Delta versus frozen CURRENT8 XGBoost
- SigmaAE worsened by +435.2088923616
- direction worsened by -5 correct months
- relative MAE vs RW rose above 1.0

## Pre-outcome D1 gate
Criterion A:
DEV SigmaAE < 1583.8534958594905
Result: FALSE.

Criterion B:
direction >= 22/33 AND DEV SigmaAE <= 1.05 * 1583.8534958594905
Result: FALSE.

Therefore:
PROCEED_TO_D1 = FALSE.
Stage 6C-D1 causal VMD + residual CEEMDAN-XGBoost is CLOSED_NOT_OPENED.
Stage 6C-D2 WOA optimization is also NOT AUTHORIZED.

## Interpretation
Canonical causal VMD did not supply useful standalone predictive representation under the monthly H=1 protocol. Performance was materially worse than both the frozen XGBoost comparator and random-walk aggregate MAE.

Combined with Stage 6C-C causal CEEMDAN-XGBoost failure, the decomposition branch has not earned further complexity under the pre-outcome gate.

## Decision
CAUSAL VMD-XGBOOST is NOT PROMOTED.
D1 CLOSED_NOT_OPENED.
D2 NOT AUTHORIZED.

The next Boosting-family task is controlled ensemble/complementarity using already-completed DEV models, followed by stability/robustness and final family freeze.

## Reproducibility
GitHub Actions run: 36383935285
Job: 108805248611
Result payload SHA256: 116e9aca3f42ecadb24dad0e5e06e83f9b9ddd6e098b1d021d7a61c8d6a5c1df
Scientific gate: BOOSTING_STAGE6C_D0_GATE=PASS
