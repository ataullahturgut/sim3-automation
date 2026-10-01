# GOLD INTRAMONTH OPPORTUNITY — Stage 5 Robustness, Calibration & Decision-Threshold Authority

**Date:** 2026-10-01  
**Status:** FROZEN PRE-RUN AUTHORITY  
**Parent:** `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md`

## 1. Frozen core

Target:
- **K100**
- `MFE5 >= SIGMA20 × sqrt(5)`

Model:
- **G_ONLY / HGB_CLASS**

Frozen Stage-3 settings:
- learning_rate=0.05
- max_iter=100
- max_leaf_nodes=7
- max_depth=3
- min_samples_leaf=40
- l2_regularization=1.0
- fixed seed
- 5-origin prequential refit
- full 5-observation label-maturity purge.

No new features.
No monthly-context feature.
No hyperparameter tuning.

## 2. Evaluation authority

Selection:
- DEV daily origins only, 2022-01..2024-12.

2025:
- fully blocked until calibration + threshold rule is frozen.

2026:
- opened / not selection authority.

## 3. Probability calibration candidates

### RAW
Use frozen Stage-3 HGB probability unchanged.

### PLATT
Chronology-safe expanding logistic calibration:
- input = logit(raw probability)
- target = matured prior K100 outcomes
- refit every 5-origin prediction block
- minimum prior OOS calibration sample = **126**
- require at least 20 positives and 20 negatives
- before minimum support, fallback to RAW
- LogisticRegression L2, C=1.0, no tuning.

### ISOTONIC
Chronology-safe expanding isotonic calibration:
- input = raw probability
- target = matured prior K100 outcomes
- refit every 5-origin block
- minimum prior OOS calibration sample = **252**
- require at least 50 positives and 50 negatives
- out_of_bounds = clip
- before minimum support, fallback to RAW.

Only prior **out-of-sample Stage-3 predictions** may train a calibrator. In-sample model probabilities are forbidden.

## 4. Calibration metrics

Primary:
- Brier score.

Co-primary:
- log loss.

Supporting:
- ECE with fixed 10 equal-width probability bins
- calibration slope/intercept where estimable
- PR-AUC
- ROC-AUC
- probability spread.

Calibration method can replace RAW only if:
- Brier improves by >= **0.5% relative**
- log loss is not worse
- no DEV year has Brier deterioration worse than **3% relative** versus RAW.

If no candidate passes:
- keep RAW.

## 5. Frozen alert-threshold candidate set

Evaluate on the selected probability stream only:

- **T20 = p >= 0.20**
- **T25 = p >= 0.25**
- **T30 = p >= 0.30**
- **T35 = p >= 0.35**
- **T40 = p >= 0.40**
- **T45 = p >= 0.45**
- **T50 = p >= 0.50**

No post-hoc threshold insertion.

## 6. Alert metrics

For every candidate:
- alert count
- alert rate
- true opportunities captured
- opportunity recall
- precision
- false-opportunity count/rate
- F1 supporting only
- mean / median realized MFE5 after alert
- mean / median realized MAE5 after alert
- same metrics in monthly-DOWN reporting subset
- same metrics by DEV year.

## 7. Cluster / duplicate-alert diagnostic

Because 5-observation target windows overlap, daily alerts may cluster around the same rally.

Report a descriptive **episode-deduplicated** diagnostic:
- consecutive alert origins separated by <=2 Gold observations are one alert episode;
- episode is successful if any member origin is K100-positive.

This diagnostic does not replace the daily-origin primary metrics in Stage 5.

## 8. Alert promotion gate

A threshold is **USABLE PASS** only if on aggregate DEV:

1. precision >= **35%**
2. opportunity recall >= **20%**
3. alert rate between **5% and 35%**
4. precision exceeds unconditional DEV K100 prevalence by at least **5 percentage points**
5. each DEV year has:
   - at least 5 alerts
   - precision >= **25%**
6. monthly-DOWN subset:
   - at least 10 alerts aggregate
   - precision >= **25%**.

If multiple thresholds pass:
- select the highest precision candidate whose recall is within 5 percentage points of the highest-recall passing candidate;
- if none satisfy that tie rule, select highest F1 among passing candidates.

This is an alert-operability gate, not a trading-profit gate.

## 9. No trading P&L yet

Stage 5 does not define:
- entry price
- stop
- take-profit
- transaction costs
- execution timing
- position sizing.

Therefore trading return is not a promotion criterion.

## 10. Mandatory robustness views

Report:
- by 2022 / 2023 / 2024
- monthly-DOWN / monthly-UP
- low / medium / high SIGMA20 tercile
- probability bucket.

No subset may be used to create a new threshold after inspection.

## 11. Decision hierarchy

1. freeze calibration: RAW / PLATT / ISOTONIC
2. freeze threshold if any candidate passes
3. if no threshold passes:
   - retain probability model only;
   - do not force an alert rule;
   - Stage 5 fails operational-alert promotion.
4. only after full Stage-5 freeze may 2025 transport be inspected.

## 12. Required outputs

- prediction-level calibrated probability table
- calibration metric table
- threshold metric table
- yearly threshold table
- monthly-direction slice table
- volatility-tercile table
- alert-episode diagnostic
- selected calibration / threshold
- immutable hashes.
