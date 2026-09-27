# GOLD MONTHLY — BOOSTING STAGE 3 TARGET & LOSS ABLATION REPORT

Date: 2026-09-27
Status: **STAGE 3 COMPLETE — PASS**
Scope: DEV 2022-04..2024-12 only (n=33)
2025/2026: NOT OPENED / NOT EVALUATED

## Objective
With Stage-2 feature lanes frozen, test:
1. LOGRET target -> price reconstruction.
2. DIRECT_PRICE target.
3. Supported canonical loss variants without opening capacity/regularization tuning.

## Authority-supported losses
- GBRT: squared_error, absolute_error, Huber(alpha=0.9).
- XGBoost: reg:squarederror, reg:absoluteerror.
- CatBoost: RMSE, MAE.
- LightGBM: regression(L2), regression_l1(L1), Huber(alpha=0.9).
- Random Forest: target ablation only.

Pseudo-Huber / CatBoost Huber were deferred because their scale-sensitive parameters would introduce an extra tuning dimension.

## Baseline reconciliation
Every Stage-2 promoted baseline was reproduced exactly (absolute difference = 0.0), including:
- CatBoost CURRENT8 LOGRET/RMSE: 1460.433935309605
- XGBoost RAW LOGRET/L2: 1695.55569760265
- XGBoost CURRENT8 LOGRET/L2: 1778.0649251965765
- GBRT DAILY LOGRET/L2: 1594.083510057147
- LightGBM RAW LOGRET/L2: 1719.8522417746606
- LightGBM MIXED20 LOGRET/L2: 1720.4059274852286
- RF DAILY LOGRET: 1491.5506937156672

## Main result: direct price is rejected for this Boosting family
Across every lane, DIRECT_PRICE was dramatically worse than LOGRET.

Examples:
- CatBoost CURRENT8 RMSE: LOGRET 1460.43 vs DIRECT_PRICE 19295.66
- GBRT DAILY squared: LOGRET 1594.08 vs DIRECT_PRICE 15247.85
- XGBoost RAW squared: LOGRET 1695.56 vs DIRECT_PRICE 2460.29
- LightGBM MIXED20 L2: LOGRET 1720.41 vs DIRECT_PRICE 5162.58
- RF DAILY: LOGRET 1491.55 vs DIRECT_PRICE 15698.38

Binding conclusion:
**Boosting Stage 4+ uses LOGRET target only.**
Direct price target is not promoted.

## Best result by algorithm / lane

### CatBoost Ordered — CURRENT8
- LOGRET + RMSE: **SigmaAE 1460.4339**, direction 20/33
- LOGRET + MAE: 1544.4815, direction 20/33

Decision:
**Keep RMSE.**
No improvement over Stage 1, but CatBoost remains the overall Boosting leader.

### GBRT — DAILY_SUMMARY12
- LOGRET + absolute_error: **SigmaAE 1568.1002**, direction 20/33
- LOGRET + squared_error: 1594.0835, direction 20/33
- LOGRET + Huber: 1636.1204, direction 20/33

Improvement from Stage-2 baseline:
- 1594.0835 -> **1568.1002**
- improvement = **25.9833 SigmaAE**

Decision:
**Promote LOGRET + absolute_error.**

### XGBoost — RAW_LEVEL_LAGS8 price lane
- LOGRET + squared_error: **1695.5557**, direction 18/33
- LOGRET + absolute_error: 1942.6187, direction 16/33

Decision:
**Keep squared_error.**

### XGBoost — CURRENT8 direction lane
- LOGRET + squared_error: 1778.0649, **direction 21/33**
- LOGRET + absolute_error: **1698.6387**, direction 20/33

Decision:
- Price challenger: CURRENT8 + absolute_error.
- Direction challenger: CURRENT8 + squared_error remains retained.
- Primary XGBoost price lane remains RAW_LEVEL_LAGS8 + squared_error because 1695.5557 is slightly lower than CURRENT8 + absolute_error.

### LightGBM — RAW_LEVEL_LAGS8
- LOGRET + L2: 1719.8522, direction 18/33
- LOGRET + Huber: 1719.8522, direction 18/33
- LOGRET + L1: 1884.4313, direction 18/33

No useful loss improvement.

### LightGBM — MIXED20 balanced lane
- LOGRET + **L1**: **1635.4056**, **direction 22/33**
- LOGRET + L2: 1720.4059, direction 19/33
- LOGRET + Huber: 1720.4059, direction 19/33

This is a meaningful Stage-3 improvement:
- price SigmaAE: 1720.4059 -> **1635.4056**
- improvement = **85.0003**
- direction: 19/33 -> **22/33**

Decision:
**LightGBM primary lane becomes MIXED20 + regression_l1.**
RAW_LEVEL_LAGS8 is no longer the primary LightGBM lane.

### Random Forest anchor — DAILY_SUMMARY12
- LOGRET: **1491.5507**, direction 20/33
- DIRECT_PRICE: 15698.3822, direction 16/33

Decision:
Keep LOGRET comparator unchanged.

## Stage-4 promoted set

Primary Boosting configurations:
1. **CatBoost Ordered / CURRENT8 / LOGRET / RMSE**
   - SigmaAE 1460.4339
   - direction 20/33
2. **GBRT / DAILY_SUMMARY12 / LOGRET / absolute_error**
   - SigmaAE 1568.1002
   - direction 20/33
3. **XGBoost / RAW_LEVEL_LAGS8 / LOGRET / reg:squarederror**
   - SigmaAE 1695.5557
   - direction 18/33
4. **LightGBM / MIXED20 / LOGRET / regression_l1**
   - SigmaAE 1635.4056
   - direction 22/33

Retained special challenger:
- XGBoost / CURRENT8 / LOGRET / reg:squarederror
  - direction 21/33
- XGBoost / CURRENT8 / LOGRET / reg:absoluteerror
  - SigmaAE 1698.6387, direction 20/33

Comparator:
- RF / DAILY_SUMMARY12 / LOGRET
  - SigmaAE 1491.5507, direction 20/33

## Overall interpretation

The target-domain question is now resolved:
- **LOGRET is strongly preferred.**
- DIRECT_PRICE is not competitive and should not consume further search budget.

Loss choice is model-specific:
- CatBoost prefers RMSE.
- GBRT benefits from L1/absolute error.
- XGBoost RAW prefers squared error.
- LightGBM MIXED20 benefits strongly from L1.

The family leader remains CatBoost CURRENT8 at SigmaAE 1460.43, still above the strongest existing project families (~1413–1416). Stage 4 capacity tuning is therefore justified, but Boosting is not yet the project leader.

## Provenance
- Run ID: 36316620996
- Job ID: 108612417045
- Commit: 1e782d8467d27ed9fb68fd638508d45504bd75d1
- Artifact ID: 10930777702
- Artifact SHA256: f40b45eff717a65c8283d6fb8511bb6c2b20a0aecd12aecd3d1fd25c7eb0afe3
- Deterministic payload SHA256: 4176ad25e0d826a604a3f589764a6a8d847986731616d0ead422e78e5db14465

## Kontrol ve Uyum Özeti
- Stage 3: PASS.
- Stage-2 baseline reconciliation: PASS / exact.
- Determinism: PASS.
- Feature lanes changed: NO.
- Capacity changed: NO.
- Hyperparameter search: NONE.
- Random split: NONE.
- 2025/2026 opened: NO.
- DB writes: NONE.
- Target decision: LOGRET retained; DIRECT_PRICE rejected.
- Next stage: Stage 4 Capacity Scan only.
