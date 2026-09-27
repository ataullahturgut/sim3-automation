# GOLD MONTHLY — BOOSTING FAMILY AUTHORITY & STAGE 0 FREEZE

Date: 2026-09-27
Status: **STAGE 0 COMPLETE — AUTHORITY / PROTOCOL FROZEN**
Project: GOLD MONTHLY FORECAST
Target: **H=1 next-calendar-month average XAU/USD**

## 1. Authority basis

Primary method authorities:
- Friedman (2001), *Greedy Function Approximation: A Gradient Boosting Machine*, Annals of Statistics, DOI 10.1214/aos/1013203451.
- Chen & Guestrin (2016), *XGBoost: A Scalable Tree Boosting System*, KDD, DOI 10.1145/2939672.2939785.
- Ke et al. (2017), *LightGBM: A Highly Efficient Gradient Boosting Decision Tree*, NeurIPS 30.
- Prokhorenkova et al. (2018), *CatBoost: Unbiased Boosting with Categorical Features*, NeurIPS 31.

Gold-specific evidence:
- Ben Jabeur, Mefteh-Wali & Viviani, *Forecasting gold price with the XGBoost algorithm and SHAP interaction values*, Annals of Operations Research, DOI 10.1007/s10479-021-04187-w.
  - Monthly gold data, Jan-1986..Dec-2019, 408 observations.
  - Compares XGBoost, CatBoost and other ML models; reports XGBoost as the strongest model.
  - Important limitation for our project: the paper randomly partitions 80% train / 20% test and uses tenfold CV, so its reported error cannot be used as a chronological benchmark.
  - Reported tuned XGBoost parameters include learning_rate=0.05, n_estimators/iterations=500, max_depth=5, subsample=0.7, colsample_bytree=0.7, min_child_weight=4.
- Cohen & Aiche (2023), *Forecasting gold price using machine learning methodologies*, Chaos, Solitons & Fractals 175:114079.
  - Uses lagged financial/market predictors; finds GBRT and XGBoost valuable for gold forecasting.
- Suan, Anbananthen & Kanan (2026), *Gold Price Forecasting Using Machine Learning Models with Hyperparameter Optimization for Inflation Hedging*, Emerging Science Journal 10(3), DOI 10.28991/ESJ-2026-010-03-016.
  - Monthly data, 2009–2024.
  - Compares RF, XGBoost, Gradient Boosting, LightGBM, LSTM, GRU.
  - Tuning methods include TPE, Grid Search and CMA-ES.
  - Reports CMA-ES-optimized Gradient Boosting as the best model in that study.

Interpretation:
- XGBoost has strong direct gold-specific evidence.
- Classical GBRT must be treated as a first-class candidate, not merely an anchor.
- CatBoost has direct gold-comparison evidence and is retained.
- LightGBM remains a required family member, but its leaf-wise capacity must be controlled on our small monthly sample.
- Random Forest is a **non-boosting comparator only**.

## 2. Binding project contract

### Forecast
- H=1 only.
- Forecast origin = previous completed calendar month-end.
- Primary output = next-month average XAU/USD price.

### Frozen inputs for the first production lane
Exactly 8 origin-safe VW-MIDAS predictors:
1. GOLD_MR
2. GOLD_VW
3. SILVER_MR
4. SILVER_VW
5. PLATINUM_MR
6. PLATINUM_VW
7. PALLADIUM_MR
8. PALLADIUM_VW

No macro/predictor expansion inside the main Boosting checklist. Any later predictor extension must be a separate research lane.

### Data / chronology
- DEV selection: **2022-04..2024-12**, n=33.
- 2025: **LOCKED TRANSPORT / REPORT-ONLY**.
- 2026 available months: **RETROSPECTIVE STRESS / REPORT-ONLY**.
- DB: READ_ONLY.
- Random split: PROHIBITED.
- Train/validation: expanding or rolling chronological only.
- At target month Y, no Y actual or future feature may affect fitting/tuning.
- 2025/2026 must not select algorithm, target form, loss, tree depth, learning rate, number of trees, regularization, subsampling or optimizer.

### Stage-1 reference target
To preserve parity with the existing monthly project:
- model target = **next-month Gold log return**;
- forecast price = origin-known previous monthly Gold price × exp(predicted log return).

Direct price-level prediction is reserved for **Stage 2 target ablation**.

### Scaling
- Canonical tree models will receive the raw frozen predictor values.
- No mandatory z-score normalization for trees.
- Any preprocessing must be fit strictly inside each origin if later introduced.

## 3. Scoring contract

Primary:
1. **DEV cumulative absolute price error (SigmaAE)**.

Secondary:
2. direction correct / 33 and direction accuracy;
3. MAE;
4. RMSE;
5. MAPE / WAPE;
6. relative MAE versus random walk;
7. yearly stability and worst-month error later.

R² is descriptive only and must not drive selection because price-level trends can make R² misleading.

## 4. Stage 1 canonical model set

Stage 1 will run **5 models in one batch** because they are independent and share the same frozen data/protocol:

### 1. GBRT
Implementation: scikit-learn GradientBoostingRegressor.
Canonical no-tuning baseline:
- loss = squared_error
- n_estimators = 100
- learning_rate = 0.10
- max_depth = 3
- min_samples_leaf = 1
- subsample = 1.0
- random_state = 1701

### 2. XGBoost
Implementation: XGBRegressor.
Canonical no-tuning baseline:
- objective = reg:squarederror
- n_estimators = 100
- learning_rate = 0.30
- max_depth = 6
- min_child_weight = 1
- gamma = 0
- subsample = 1.0
- colsample_bytree = 1.0
- reg_alpha = 0
- reg_lambda = 1
- tree_method = hist
- random_state = 1701

The Jabeur gold-specific tuned preset is **not** used as the canonical baseline; it enters the controlled capacity/regularization stages so we can distinguish algorithm effect from literature-tuned effect.

### 3. CatBoost
Implementation: CatBoostRegressor.
Baseline:
- loss_function = RMSE
- iterations = 100
- depth = 6
- learning_rate = 0.03
- l2_leaf_reg = 3
- boosting_type = Ordered
- random_seed = 1701
- allow_writing_files = False

Ordered boosting is kept because the primary CatBoost authority explicitly motivates ordered/prequential constructions to reduce prediction shift.

### 4. LightGBM
Implementation: LGBMRegressor.
Canonical no-tuning baseline:
- objective = regression
- n_estimators = 100
- learning_rate = 0.10
- num_leaves = 31
- max_depth = -1
- min_child_samples = 20
- subsample = 1.0
- colsample_bytree = 1.0
- reg_alpha = 0
- reg_lambda = 0
- random_state = 1701

This intentionally exposes the native high-capacity LightGBM baseline; Stage 3 will test smaller leaf/depth structures.

### 5. Random Forest anchor
Implementation: RandomForestRegressor.
- n_estimators = 500
- max_features = 1.0
- bootstrap = True
- random_state = 1701
- n_jobs fixed/reported
- comparator only; not a Boosting family winner unless explicitly reclassified later.

## 5. Software freeze

Stage 1 environment:
- Python 3.12
- scikit-learn 1.9.1
- XGBoost 3.4.1
- LightGBM 4.7.0
- CatBoost 1.2.10

The exact installed versions must be written to the result artifact.

## 6. Legacy LightGBM / CatBoost run audit

Existing files:
- `gold_axis_2026/tools/vw_midas_lightgbm_catboost_v1.py`
- `.github/workflows/gold-midas-lightgbm-catboost-v1.yml`

Existing successful run:
- Run ID: **36105855475**
- Job ID: **107978083624**
- Commit: `81d0a6ba2f5c9d26c11e4135ad91998ceb3af389`
- Artifact ID: **10850784265**

Legacy reported DEV:
- CatBoost MAE 44.378077 -> implied SigmaAE **1464.4765**, direction 57.58%.
- LightGBM MAE 44.694939 -> implied SigmaAE **1474.9330**, direction 60.61%.

These results are **EXPLORATORY_ONLY / NOT CANONICAL EVIDENCE** because:
1. hyperparameters are selected on the full 2022-04..2024-12 DEV interval and then performance is reported on that same interval;
2. selection objective is DEV Gold log-return MAE rather than the project's primary price-domain SigmaAE;
3. the implementation predicts all four metal returns via MultiOutputRegressor/MultiRMSE instead of the new canonical Gold-only lane;
4. it covers only LightGBM and CatBoost, not the frozen five-model Stage-1 comparison.

The old result is retained because it is an encouraging signal and prevents accidental duplication, but it cannot determine the new family winner.

## 7. Frozen checklist

- **Stage 0 — Authority & Protocol Freeze: COMPLETE**
- Stage 1 — Canonical Baselines: GBRT + XGBoost + CatBoost + LightGBM + RF anchor
- Stage 2 — Target & Loss Ablation: log-return vs direct price; squared vs robust losses where supported
- Stage 3 — Capacity Scan: depth/leaves, learning rate, tree count, leaf/child constraints
- Stage 4 — Regularization & Subsampling
- Stage 5 — Nested Optimization: TPE/Optuna for promoted models; CMA-ES specifically eligible for GBRT due direct monthly-gold evidence
- Stage 6 — Stability & Feature Audit: yearly/worst-month + SHAP/feature stability + seed stability
- Stage 7 — DEV-only Final Selection
- Stage 8 — Freeze + 2025 transport + 2026 stress reporting
- Stage H — Hybrid research lane **only if** the frozen Boosting family is genuinely competitive

## 8. Stage gates

A stage may promote candidates only from DEV evidence available up to that stage.

Do not:
- inspect 2025/2026 to rescue or tune a model;
- use random K-fold CV for our model selection;
- open decomposition, PSO/GA/WOA or ensembles before the base family is understood;
- run hundreds of optimizer trials before capacity and regularization behavior are mapped;
- change the frozen 8-feature production lane mid-checklist.

## 9. Stage 1 execution rule

Next action after user approval:
- run the 5 canonical models together;
- Gold-only;
- frozen 8 features;
- expanding-origin DEV only;
- no hyperparameter selection;
- report SigmaAE + direction + supporting metrics;
- do **not** open 2025/2026;
- stop after Stage 1.

## Kontrol ve Uyum Özeti

- Authority scan: PASS.
- Direct gold-specific Boosting evidence: PASS.
- Monthly gold evidence: PASS.
- Known literature random-split weakness identified: PASS.
- H=1 contract: FROZEN.
- Frozen 8 predictors: FROZEN.
- DEV-only selection: FROZEN.
- 2025/2026 hidden until Stage 8: FROZEN.
- Random split: PROHIBITED.
- DB: READ_ONLY.
- Legacy LightGBM/CatBoost run: AUDITED, EXPLORATORY_ONLY.
- Stage 0: **COMPLETE**.
- Next stage: **Stage 1 only**.


---

## 10. Pre-outcome Stage-plan amendment — 2026-09-27

User-approved methodological correction: before target/loss ablation, test whether the Boosting family is being handicapped by the current preprocessed 8-feature representation.

Revised order:
- Stage 0 — Authority & Protocol Freeze: COMPLETE
- Stage 1 — Canonical Baselines: COMPLETE
- **Stage 2 — Feature Representation Ablation: ACTIVE NEXT**
- Stage 3 — Target & Loss Ablation
- Stage 4 — Capacity Scan
- Stage 5 — Regularization & Subsampling
- Stage 6 — Nested Optimization
- Stage 7 — Stability & Feature Audit
- Stage 8 — DEV-only Final Selection
- Stage 9 — Freeze + 2025 transport + 2026 stress
- Stage H — Hybrid only if justified

### Stage 2 frozen representation set

All representations are constructed strictly from information available by the previous completed month (origin). The model target remains next-month Gold log return and all Stage-1 model hyperparameters remain fixed.

**R0 CURRENT8**
- Existing 8 origin-safe VW-MIDAS predictors:
  GOLD_MR, GOLD_VW, SILVER_MR, SILVER_VW, PLATINUM_MR, PLATINUM_VW, PALLADIUM_MR, PALLADIUM_VW.
- This is the Stage-1 reference.

**R1 RAW_LEVEL_LAGS8**
For each of Gold, Silver, Platinum, Palladium:
- previous completed month average level;
- one additional lagged monthly average level.
Total = 8 raw level features.

**R2 SIMPLE_RETURNS8**
For each metal:
- 1-month log return;
- 3-month log momentum.
Total = 8 simple return/momentum features.

**R3 DAILY_SUMMARY12**
For each metal, using daily values only from the completed origin month:
- origin-month open-to-close log return;
- realized volatility = sqrt(sum(daily log-return^2));
- log high/low range.
Total = 12 daily-summary features.

**R4 MIXED20**
- CURRENT8 (8);
- current origin-month raw level for each metal (4);
- 3-month log momentum for each metal (4);
- realized volatility for each metal (4).
Total = 20 features.

Rationale:
- R1 tests whether absolute regime/level information was lost.
- R2 tests whether the GPR-weighted VW transform is unnecessary relative to simple temporal derivatives.
- R3 tests whether compressing the complete daily path into one VW statistic discards useful within-month structure.
- R4 tests a controlled combination without opening a large feature-engineering search.

### Stage 2 execution rules
- Same five Stage-1 estimators and exactly the same canonical hyperparameters.
- Gold-only target.
- No target/loss changes.
- No hyperparameter tuning.
- No feature subset search inside a representation.
- No random split.
- DEV only: 2022-04..2024-12.
- 2025/2026 are not opened.
- Primary comparison: DEV SigmaAE; direction is secondary.
- Report every model × representation combination, then identify the best representation within each model for promotion to Stage 3.
- Stage 2 does not authorize changing the project-wide frozen input contract for other model families.


### Stage 2 engineering correction before any valid outcome
The first Stage-2 execution failed before producing results because R2 3-month momentum is not buildable for historical targets 2010-03 and 2010-04. No model evidence was produced.

To avoid unequal training-history confounding, the valid Stage-2 comparison uses a **common historical training start of 2010-05** for every representation and every estimator. This is the earliest target for which all five frozen representations are simultaneously buildable from the common metal history.

CURRENT8 Stage-1 exact reproduction remains a separate reconciliation check using the original Stage-1 history. The Stage-2 comparative CURRENT8 score uses the common 2010-05 history, like all other representations.


## 11. Stage 2 closure — 2026-09-27

**Stage 2 Feature Representation Ablation: COMPLETE / PASS.**

Binding conclusion:
- CatBoost Ordered → CURRENT8 remains the primary lane.
- XGBoost → RAW_LEVEL_LAGS8 is the price-error lane; CURRENT8 retained as direction challenger.
- GBRT → DAILY_SUMMARY12.
- LightGBM → RAW_LEVEL_LAGS8; MIXED20 retained as balanced challenger.
- Random Forest anchor → DAILY_SUMMARY12.

The feature-representation hypothesis is supported but algorithm-specific. No alternative representation beats the absolute Stage-1 CatBoost CURRENT8 SigmaAE of 1460.4339.

Full report:
`GOLD_MONTHLY_BOOSTING_STAGE2_FEATURE_REPRESENTATION_REPORT_2026-09-27.md`

Next authorized stage after user approval:
**Stage 3 — Target & Loss Ablation only.**


## 12. Stage 3 pre-outcome freeze — Target & Loss Ablation

**Stage 3 is authorized.**

Promoted Stage-2 lanes are frozen:
- CATBOOST_ORDERED__CURRENT8, history start 2010-03.
- XGBOOST__RAW_LEVEL_LAGS8, history start 2010-03.
- XGBOOST__CURRENT8 direction challenger, history start 2010-03.
- GBRT__DAILY_SUMMARY12, history start 2010-03.
- LIGHTGBM__RAW_LEVEL_LAGS8, history start 2010-03.
- LIGHTGBM__MIXED20 balanced challenger, history start 2010-05.
- RANDOM_FOREST_ANCHOR__DAILY_SUMMARY12, history start 2010-03.

### Targets
Each lane is tested with exactly two targets:
1. LOGRET: next-month Gold log return; reconstruct price as previous origin-known Gold price × exp(prediction).
2. DIRECT_PRICE: next-month average XAU/USD price directly.

### Losses
No capacity, regularization, sampling or feature changes are allowed.

- GBRT:
  - squared_error
  - absolute_error
  - huber with canonical alpha=0.9
- XGBoost:
  - reg:squarederror
  - reg:absoluteerror
  - Pseudo-Huber is explicitly deferred because huber_slope is target-scale sensitive and choosing it here would open an additional tuning dimension.
- CatBoost:
  - RMSE
  - MAE
  - Huber is deferred because delta is obligatory and scale-dependent.
- LightGBM:
  - regression (L2)
  - regression_l1 (L1)
  - huber with canonical alpha=0.9
- Random Forest anchor:
  - no loss variants; target ablation only.

### Selection
- DEV 2022-04..2024-12 only.
- Primary: price SigmaAE.
- Secondary: direction correct, RMSE/MAE.
- 2025/2026 remain unopened.
- No random split.
- No optimizer / hyperparameter search.
- Every candidate uses its Stage-2 frozen feature lane and compatible maximum history.
- Stage 3 stops after target/loss selection; Stage 4 capacity scan requires separate approval.


## 13. Stage 3 closure — 2026-09-27

**Stage 3 Target & Loss Ablation: COMPLETE / PASS.**

Binding target decision:
- **LOGRET -> price reconstruction remains the only promoted target.**
- DIRECT_PRICE was dramatically worse across all tested lanes and is closed for Stage 4+.

Promoted configurations:
- CatBoost Ordered -> CURRENT8 -> LOGRET -> RMSE.
- GBRT -> DAILY_SUMMARY12 -> LOGRET -> absolute_error.
- XGBoost primary price lane -> RAW_LEVEL_LAGS8 -> LOGRET -> reg:squarederror.
- LightGBM primary lane -> MIXED20 -> LOGRET -> regression_l1.
- RF comparator -> DAILY_SUMMARY12 -> LOGRET.

Retained XGBoost challengers:
- CURRENT8 + reg:squarederror for direction.
- CURRENT8 + reg:absoluteerror as price/balance challenger.

Full report:
`GOLD_MONTHLY_BOOSTING_STAGE3_TARGET_LOSS_REPORT_2026-09-27.md`

Next authorized stage after user approval:
**Stage 4 — Capacity Scan only.**


## 14. Stage 4 pre-outcome freeze — Capacity Scan

**Stage 4 is authorized.**

Everything frozen from Stage 3 remains fixed:
- Target: LOGRET only.
- CatBoost Ordered: CURRENT8 + RMSE.
- GBRT: DAILY_SUMMARY12 + absolute_error.
- XGBoost primary: RAW_LEVEL_LAGS8 + reg:squarederror.
- XGBoost direction challenger: CURRENT8 + reg:squarederror.
- LightGBM: MIXED20 + regression_l1.
- RF comparator: DAILY_SUMMARY12 + native squared-error forest.

No regularization/subsampling tuning is allowed in Stage 4 beyond capacity-related minimum leaf/child constraints explicitly listed below.

### Capacity profiles

#### CatBoost Ordered
- C0_SHALLOW_100: depth=4, iterations=100, learning_rate=0.03
- C1_SHALLOW_300: depth=4, iterations=300, learning_rate=0.03
- C2_BASELINE: depth=6, iterations=100, learning_rate=0.03
- C3_MEDIUM_300: depth=6, iterations=300, learning_rate=0.03
- C4_DEEP_LOWLR: depth=8, iterations=300, learning_rate=0.02

Other CatBoost parameters remain Stage-3 frozen, including l2_leaf_reg=3 and Ordered boosting.

#### GBRT
- G0_SHALLOW: max_depth=2, n_estimators=100, learning_rate=0.10, min_samples_leaf=2
- G1_SHALLOW_SLOW: max_depth=2, n_estimators=300, learning_rate=0.03, min_samples_leaf=2
- G2_BASELINE: max_depth=3, n_estimators=100, learning_rate=0.10, min_samples_leaf=1
- G3_MEDIUM_SLOW: max_depth=3, n_estimators=300, learning_rate=0.03, min_samples_leaf=2
- G4_HIGHER_CAPACITY: max_depth=4, n_estimators=300, learning_rate=0.03, min_samples_leaf=2

Loss remains absolute_error.

#### XGBoost
The same five capacity profiles are evaluated on both RAW_LEVEL_LAGS8 price lane and CURRENT8 direction lane:
- X0_SHALLOW_CONSERVATIVE: max_depth=2, n_estimators=300, learning_rate=0.03, min_child_weight=3
- X1_SHALLOW_MEDIUM: max_depth=3, n_estimators=300, learning_rate=0.05, min_child_weight=2
- X2_MEDIUM: max_depth=4, n_estimators=200, learning_rate=0.05, min_child_weight=1
- X3_BASELINE: max_depth=6, n_estimators=100, learning_rate=0.30, min_child_weight=1
- X4_DEEP_SLOW: max_depth=6, n_estimators=300, learning_rate=0.03, min_child_weight=2

Other Stage-3 XGBoost parameters remain fixed: gamma=0, subsample=1, colsample_bytree=1, reg_alpha=0, reg_lambda=1.

#### LightGBM
- L0_SMALL: num_leaves=7, max_depth=3, min_child_samples=15, n_estimators=300, learning_rate=0.03
- L1_SHALLOW: num_leaves=15, max_depth=4, min_child_samples=15, n_estimators=300, learning_rate=0.03
- L2_MEDIUM: num_leaves=15, max_depth=5, min_child_samples=10, n_estimators=200, learning_rate=0.05
- L3_BASELINE: num_leaves=31, max_depth=-1, min_child_samples=20, n_estimators=100, learning_rate=0.10
- L4_HIGHER_CAPACITY: num_leaves=31, max_depth=6, min_child_samples=10, n_estimators=300, learning_rate=0.03

Objective remains regression_l1. No subsampling or L1/L2 regularization changes yet.

#### Random Forest comparator
Limited capacity audit only:
- R0_BASELINE: max_depth=None, min_samples_leaf=1, n_estimators=500
- R1_SHALLOW: max_depth=4, min_samples_leaf=3, n_estimators=500
- R2_MEDIUM: max_depth=6, min_samples_leaf=2, n_estimators=500

### Governance
- DEV only: 2022-04..2024-12.
- 2025/2026 remain unopened.
- No random split.
- No feature, target or loss changes.
- No gamma, subsample, colsample, L1/L2, bagging or other Stage-5 regularization search.
- Primary metric: DEV price SigmaAE.
- Secondary: direction, MAE, RMSE.
- Exact Stage-3 baseline reproduction is mandatory.
- Stage 4 stops after selecting capacity profile(s); Stage 5 requires separate approval.


## 15. Stage 4 closure — 2026-09-27

**Stage 4 Capacity Scan: COMPLETE / PASS.**

Promoted primary capacity profiles:
- CatBoost -> C2_BASELINE: depth6, iterations100, learning_rate0.03.
- GBRT -> G0_SHALLOW: depth2, n_estimators100, learning_rate0.10, min_samples_leaf2.
- XGBoost RAW -> X0_SHALLOW_CONSERVATIVE: depth2, n_estimators300, learning_rate0.03, min_child_weight3.
- LightGBM MIXED20 L1 -> L4_HIGHER_CAPACITY: num_leaves31, max_depth6, min_child_samples10, n_estimators300, learning_rate0.03.
- RF comparator -> R0_BASELINE.

Retained challengers:
- CatBoost C4_DEEP_LOWLR: SigmaAE 1481.2619, direction 22/33.
- XGBoost CURRENT8 X2_MEDIUM: direction 22/33.

Family price leader remains CatBoost C2 at SigmaAE 1460.4339.
GBRT improved to 1500.4295 / 22 directions.
LightGBM improved to 1534.6087 / 22 directions.

Full report:
`GOLD_MONTHLY_BOOSTING_STAGE4_CAPACITY_REPORT_2026-09-27.md`

Next authorized stage after user approval:
**Stage 5 — Regularization & Subsampling only.**


## 16. Stage 5 pre-outcome freeze — Regularization & Subsampling

**Stage 5 is authorized.**

All Stage-4 promoted feature/target/loss/capacity choices are frozen. Stage 5 may change only regularization and/or sampling controls listed below.

Authority basis:
- XGBoost: reg_alpha/reg_lambda, gamma, subsample and colsample_bytree are native regularization/sampling controls.
- CatBoost: l2_leaf_reg, random_strength and bootstrap/subsample controls are native overfit controls.
- LightGBM: lambda_l1/lambda_l2 plus bagging_fraction / feature_fraction (sklearn aliases subsample / colsample_bytree) are native controls.
- GBRT: subsample and max_features are the controlled stochastic-regularization levers.
- Random Forest remains comparator only.

### Frozen Stage-5 lanes

1. CATBOOST_PRICE
   - CURRENT8 / LOGRET / RMSE
   - depth=6, iterations=100, learning_rate=0.03
2. CATBOOST_BALANCED
   - CURRENT8 / LOGRET / RMSE
   - depth=8, iterations=300, learning_rate=0.02
3. GBRT_PRICE_BALANCED
   - DAILY_SUMMARY12 / LOGRET / absolute_error
   - depth=2, n_estimators=100, learning_rate=0.10, min_samples_leaf=2
4. XGBOOST_PRICE
   - RAW_LEVEL_LAGS8 / LOGRET / reg:squarederror
   - depth=2, n_estimators=300, learning_rate=0.03, min_child_weight=3
5. XGBOOST_DIRECTION
   - CURRENT8 / LOGRET / reg:squarederror
   - depth=4, n_estimators=200, learning_rate=0.05, min_child_weight=1
6. LIGHTGBM_PRICE_BALANCED
   - MIXED20 / LOGRET / regression_l1
   - num_leaves=31, max_depth=6, min_child_samples=10, n_estimators=300, learning_rate=0.03
7. RF_COMPARATOR
   - DAILY_SUMMARY12 / LOGRET
   - Stage-4 R0 baseline only; no Stage-5 search.

### CatBoost regularization profiles
Applied separately to CATBOOST_PRICE and CATBOOST_BALANCED:
- CB_R0_BASELINE: Stage-4 settings unchanged (l2_leaf_reg=3; implicit library bootstrap/random_strength behavior).
- CB_R1_L2_10: l2_leaf_reg=10.
- CB_R2_RANDOM2: random_strength=2.
- CB_R3_BERNOULLI80: bootstrap_type=Bernoulli, subsample=0.8.
- CB_R4_COMBO: l2_leaf_reg=10, random_strength=2, bootstrap_type=Bernoulli, subsample=0.8.

No use_best_model / early stopping; no validation-set peeking.

### GBRT regularization profiles
Capacity remains G0:
- G_R0_BASELINE: subsample=1.0, max_features=None.
- G_R1_ROW90: subsample=0.90.
- G_R2_ROW80: subsample=0.80.
- G_R3_FEATURE80: max_features=0.80.
- G_R4_COMBO80: subsample=0.80, max_features=0.80.

### XGBoost regularization profiles
Applied separately to PRICE and DIRECTION lanes:
- X_R0_BASELINE: reg_alpha=0, reg_lambda=1, gamma=0, subsample=1, colsample_bytree=1.
- X_R1_L2_5: reg_lambda=5.
- X_R2_L1_001: reg_alpha=0.01.
- X_R3_SAMPLE80: subsample=0.80, colsample_bytree=0.80.
- X_R4_COMBO: reg_alpha=0.01, reg_lambda=5, gamma=0.001, subsample=0.80, colsample_bytree=0.80.

Gamma is tested only inside the pre-frozen combo profile; no adaptive gamma search occurs in Stage 5.

### LightGBM regularization profiles
Capacity remains L4:
- L_R0_BASELINE: reg_alpha=0, reg_lambda=0, subsample=1, subsample_freq=0, colsample_bytree=1.
- L_R1_L2_1: reg_lambda=1.
- L_R2_L1_01: reg_alpha=0.1.
- L_R3_BAG80: subsample=0.80, subsample_freq=1.
- L_R4_FEATURE80: colsample_bytree=0.80.
- L_R5_COMBO: reg_alpha=0.1, reg_lambda=1, subsample=0.80, subsample_freq=1, colsample_bytree=0.80.

### Governance
- DEV only: 2022-04..2024-12.
- 2025/2026 remain unopened.
- No random split.
- No feature/target/loss/capacity changes.
- No optimizer / TPE / CMA-ES.
- No early stopping against DEV.
- Exact Stage-4 baseline replay is mandatory for every promoted lane.
- Primary metric: DEV price SigmaAE.
- Secondary: direction, MAE, RMSE.
- Stage 5 stops after regularization/subsampling selection; Stage 6 nested optimization requires separate approval.


## 17. Stage 5 closure — 2026-09-27

**Stage 5 Regularization & Subsampling: COMPLETE / PASS.**

Binding results:
- CatBoost PRICE: keep baseline, 1460.4339 / 20 directions.
- CatBoost BALANCED: keep baseline, 1481.2619 / 22.
- GBRT: keep baseline, 1500.4295 / 22.
- LightGBM: keep baseline, 1534.6087 / 22.
- XGBoost RAW price: keep baseline, 1673.0823 / 19.
- XGBoost CURRENT8 combo: 1583.8535 / 20; retained as price/balance challenger.
- XGBoost CURRENT8 L2=5: 1679.8372 / **23**; retained as direction challenger.
- RF comparator unchanged.

Full report:
`GOLD_MONTHLY_BOOSTING_STAGE5_REGULARIZATION_REPORT_2026-09-27.md`

Next authorized stage after user approval:
**Stage 6 — Nested chronological optimization only.**


## 17. Stage 5 closure — 2026-09-27

**Stage 5 Regularization & Subsampling: COMPLETE / PASS.**

Binding conclusions:
- CatBoost price: retain Stage-4 baseline regularization.
- CatBoost balanced: retain Stage-4 baseline regularization.
- GBRT: retain full-sample Stage-4 baseline; row/feature subsampling degraded performance.
- XGBoost RAW price: retain Stage-4 baseline regularization.
- LightGBM MIXED20 L1: retain Stage-4 baseline regularization.
- XGBoost CURRENT8 direction challenger: promote **reg_lambda=5**, yielding direction 23/33 and SigmaAE 1679.8372.
- RF remains comparator only.

Primary family price leader remains CatBoost at SigmaAE 1460.4339.
No Stage-5 price regularization profile beats the Stage-4 price leaders.

Full report:
`GOLD_MONTHLY_BOOSTING_STAGE5_REGULARIZATION_REPORT_2026-09-27.md`

Next authorized stage after user approval:
**Stage 6 — Nested Chronological Optimization only.**
