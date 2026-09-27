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
