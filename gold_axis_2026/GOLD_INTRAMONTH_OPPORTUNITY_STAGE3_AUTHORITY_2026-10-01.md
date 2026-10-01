# GOLD INTRAMONTH OPPORTUNITY — Stage 3 Predictability Screen Authority

**Date:** 2026-10-01  
**Status:** FROZEN PRE-RUN AUTHORITY  
**Parent:** `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md`  
**Stage-2 authority artifact:** run 36860536563 / artifact 11161358194

## 1. Question

Can information known at the daily origin predict five-observation Gold upside/downside path outcomes better than prior-history baselines?

Targets:
- binary: K050, K075, K100
- continuous: MFE5, MAE5.

No monthly ChHHO direction/alarm/regime is used in Stage 3.

## 2. Chronology

- background / initial training history: 2011-2021
- DEV evaluation: 2022-2024
- 2025: untouched frozen transport
- 2026: untouched/opened.

No random split.

## 3. Label-maturity rule

A sample with five-observation target beginning after origin t is not known until its fifth future Gold observation has been published.

For a prediction block beginning at origin date D:
- training may include only rows whose complete five-observation label window ends on or before D;
- rows with incomplete/maturing labels are purged.

This is binding and prevents overlapping-window leakage.

## 4. Refit schedule

Strict chronological **5-Gold-origin block prequential evaluation**.

At each DEV block start:
1. freeze all features at block-start origins;
2. fit using all matured prior rows;
3. predict the next up-to-5 DEV origins;
4. advance to the next block;
5. refit.

No outcome from within the current prediction block may affect that block's fitted model.

## 5. Feature blocks

### G_ONLY
- gold_r1
- gold_r3
- gold_r5
- gold_r10
- gold_r21
- sigma20
- rv20
- absret20
- dd_high21
- dist_low21
- reversal_1_vs_5.

### FOUR_METAL
G_ONLY plus:
- silver_r1/r5/r21
- platinum_r1/r5/r21
- palladium_r1/r5/r21
- silver/platinum/palladium age_days
- cross_r1_breadth_pos
- cross_r5_breadth_pos
- cross_r1_dispersion
- cross_r5_dispersion
- gold_comp_r1_divergence
- gold_comp_r5_divergence.

Missing companion values:
- no future fill;
- numeric companion returns imputed with training median;
- staleness ages imputed with training maximum + 1 day;
- missingness is handled only from training data inside each fit.

## 6. Fixed model screen

No hyperparameter tuning in Stage 3.

### Binary targets
1. **LOGIT_L2**
   - StandardScaler
   - LogisticRegression
   - L2
   - C=1.0
   - no class weights.

2. **HGB_CLASS**
   - HistGradientBoostingClassifier
   - learning_rate=0.05
   - max_iter=100
   - max_leaf_nodes=7
   - max_depth=3
   - min_samples_leaf=40
   - l2_regularization=1.0.

### Continuous targets
1. **RIDGE**
   - StandardScaler
   - Ridge(alpha=1.0).

2. **HUBER**
   - StandardScaler
   - HuberRegressor(epsilon=1.35, alpha=0.0001, max_iter=500).

3. **HGB_REG**
   - HistGradientBoostingRegressor
   - learning_rate=0.05
   - max_iter=100
   - max_leaf_nodes=7
   - max_depth=3
   - min_samples_leaf=40
   - l2_regularization=1.0
   - loss=squared_error.

## 7. Frozen baselines

Binary:
- expanding matured prior prevalence
- rolling-252 matured prior prevalence.

Continuous:
- expanding matured prior median
- rolling-252 matured prior median.

Stage-3 script recomputes these with the same label-maturity rule. Stage-2 summary baselines are descriptive references; Stage-3 matured baselines are the direct comparison authority.

## 8. Metrics

Binary:
- Brier score primary
- log loss co-primary
- PR-AUC supporting
- ROC-AUC supporting
- calibration slope/intercept if feasible
- prevalence and prediction spread.

Continuous:
- MAE primary
- RMSE co-primary
- Spearman correlation supporting
- top-quartile discrimination for MFE5.

## 9. Promotion gate

A Stage-3 candidate is a **predictive PASS** only if, on 2022-2024 chronological DEV:

Binary:
- Brier improves by >=1% relative to the better frozen baseline;
- log loss is not worse than the better baseline;
- predictions are non-degenerate.

Continuous:
- MAE improves by >=1% relative to the better frozen baseline;
- RMSE is not worse than the better baseline.

Feature block selection is DEV-only.

No 2025 result can rescue or select a failing candidate.

## 10. Stage decision logic

- If no target/model passes: do not force Stage 4; redesign features/target using DEV only.
- If one or more pass: freeze the strongest evidence set and then Stage 4 tests monthly ChHHO context incrementally using the exact same chronology.
- Stage 4 may not change the Stage-3 core model merely to make monthly context look useful.

## 11. Reproducibility

Required artifact outputs:
- prediction-level DEV table
- model/feature/target metric table
- matured baseline table
- feature availability audit
- selected/rejected status table
- immutable hashes.
