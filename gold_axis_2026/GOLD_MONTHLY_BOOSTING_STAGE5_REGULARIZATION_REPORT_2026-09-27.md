# GOLD MONTHLY — BOOSTING STAGE 5 REGULARIZATION & SUBSAMPLING REPORT

Date: 2026-09-27
Status: **STAGE 5 COMPLETE — PASS**
Scope: DEV 2022-04..2024-12 only (n=33)
2025/2026: NOT OPENED / NOT EVALUATED

## Objective
With Stage-4 feature / target / loss / capacity choices frozen, test only regularization and sampling controls.

## Baseline reconciliation
Every Stage-4 baseline was reproduced exactly (absolute difference = 0.0):
- CatBoost price: 1460.433935309605
- CatBoost balanced: 1481.261937710369
- GBRT: 1500.42946858865
- XGBoost price: 1673.0823484831108
- XGBoost direction lane: 1724.9639029353484
- LightGBM: 1534.6087211346264
- RF comparator: 1491.5506937156672

## Results by lane

### CatBoost PRICE
Best:
- **CB_R0_BASELINE**
- SigmaAE **1460.4339**
- Direction **20/33**

Tested stronger L2, random_strength, Bernoulli subsampling and combo regularization did not improve the price leader.

Decision:
**Keep Stage-4 baseline unchanged.**

### CatBoost BALANCED
Best by price and direction:
- **CB_R0_BASELINE**
- SigmaAE **1481.2619**
- Direction **22/33**

L2=10 was very close on price (1483.0309) but gave no directional improvement.
Sampling/combo profiles were worse.

Decision:
**Keep Stage-4 balanced baseline unchanged.**

### GBRT
Best:
- **G_R0_BASELINE**
- SigmaAE **1500.4295**
- Direction **22/33**

Row subsampling / feature subsampling / combo regularization did not improve the Stage-4 shallow model.

Decision:
**Keep Stage-4 G0 shallow model unchanged.**

### XGBoost PRICE lane
Best price:
- **X_R0_BASELINE**
- SigmaAE **1673.0823**
- Direction **19/33**

Best direction:
- **X_R1_L2_5**
- SigmaAE 1709.1001
- Direction **20/33**

Regularization did not improve the main RAW price lane.

Decision:
**Keep XGBoost RAW price baseline unchanged.**

### XGBoost CURRENT8 direction lane
This is the only lane where Stage 5 materially changed the trade-off.

Stage-4 baseline:
- SigmaAE 1724.9639
- Direction 22/33

Best PRICE/BALANCE profile:
- **X_R4_COMBO**
- reg_alpha=0.01
- reg_lambda=5
- gamma=0.001
- subsample=0.80
- colsample_bytree=0.80
- SigmaAE **1583.8535**
- Direction **20/33**

Improvement in price error:
- 1724.9639 -> **1583.8535**
- gain = **141.1104 SigmaAE**

Best DIRECTION profile:
- **X_R1_L2_5**
- reg_lambda=5
- SigmaAE **1679.8372**
- Direction **23/33 = 69.70%**

This improves the Stage-4 direction lane:
- direction 22/33 -> **23/33**
- price error also improves 1724.9639 -> **1679.8372**

Decision:
- Retain **X_R1_L2_5** as the official direction challenger.
- Retain **X_R4_COMBO** as the XGBoost price/balance challenger.
- RAW-level XGBoost remains the architecture-specific price lane, but the CURRENT8 combo is now lower in SigmaAE than RAW baseline and therefore must enter Stage 6 optimization comparison.

### LightGBM
Best:
- **L_R0_BASELINE**
- SigmaAE **1534.6087**
- Direction **22/33**

L2, L1, bagging, feature sampling and combo regularization did not beat the Stage-4 L4 higher-capacity baseline.

Decision:
**Keep Stage-4 baseline unchanged.**

### Random Forest comparator
Unchanged:
- SigmaAE **1491.5507**
- Direction **20/33**

No further RF tuning priority.

## Overall interpretation

Stage 5 did **not** improve the main CatBoost, GBRT, LightGBM or RAW-XGBoost price leaders. Their unregularized Stage-4 configurations remain preferred.

The important exception is the XGBoost CURRENT8 lane:
- stronger L2 regularization raises direction to **23/33**;
- combined regularization + sampling lowers SigmaAE to **1583.8535**.

Therefore XGBoost should not be represented by only the RAW_LEVEL_LAGS8 lane in Stage 6. Both CURRENT8 regularized challengers are retained.

## Stage-6 promoted configurations

Primary price lanes:
1. **CatBoost PRICE baseline**
   - SigmaAE 1460.4339
   - direction 20/33
2. **GBRT baseline**
   - SigmaAE 1500.4295
   - direction 22/33
3. **LightGBM baseline**
   - SigmaAE 1534.6087
   - direction 22/33
4. **XGBoost CURRENT8 combo challenger**
   - SigmaAE 1583.8535
   - direction 20/33
5. XGBoost RAW baseline
   - SigmaAE 1673.0823
   - direction 19/33

Direction/balance challengers:
- **XGBoost CURRENT8 + L2=5**
  - SigmaAE 1679.8372
  - direction **23/33**
- CatBoost balanced baseline
  - SigmaAE 1481.2619
  - direction 22/33

Comparator:
- RF baseline: 1491.5507 / 20/33.

Stage 6 may now perform nested chronological optimization only on promoted lanes; 2025/2026 remain locked.

## Provenance
- Run ID: 36318796396
- Job ID: 108618490828
- Commit: 372eef7762459525fa68dd8aeb1f6a3d4c160fdb
- Artifact ID: 10932321747
- Artifact SHA256: 3935121b3506bc4b8f236a3eec8503b1c5eb9b3c72f1bad02da06253a689716b
- Deterministic payload SHA256: f7c2272b42578f1e0cade3f8911238a4ef465d715eae91616703b7fc6d5bdb3c

## Kontrol ve Uyum Özeti
- Stage 5: PASS.
- Stage-4 baseline reconciliation: PASS / exact.
- Determinism: PASS.
- Feature changed: NO.
- Target/loss changed: NO.
- Capacity changed: NO.
- Optimizer: NONE.
- Early stopping: NONE.
- Random split: NONE.
- 2025/2026 opened: NO.
- DB writes: NONE.
- Next stage: Stage 6 Nested Optimization only.
