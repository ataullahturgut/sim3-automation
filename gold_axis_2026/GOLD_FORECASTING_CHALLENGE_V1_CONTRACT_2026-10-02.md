# GOLD FORECASTING CHALLENGE V1 — SEALED MODEL-BUILDING CONTRACT

**Date:** 2026-10-02  
**Status:** FROZEN BEFORE SEALED TEST  
**Researcher:** ChatGPT model-building side  
**Tester:** User / challenge owner  
**Target:** Global XAU daily **H3 UP/DOWN direction**

## 1. Purpose

The challenge asks one narrow question:

> Can a disciplined pre-registered research process build a materially useful XAU H3 direction model without seeing the final test outcomes before the model is locked?

This is not a search for the best historical backtest after seeing all years.

## 2. Data identity

Use only the existing origin-safe daily project panel:

- identity: `GLOBAL_XAU_PUBLIC_STAKTRAKR_R2`
- pinned public metals reconstruction and already-audited point-in-time clocks
- target: `target_r3 > 0` = UP, otherwise DOWN.

No 2025/2026 outcomes are used anywhere in Challenge V1.

## 3. Time split

To avoid using the already-opened 2022-2024 DEV period as the sealed challenge test:

- **research/training history:** 2010-01-01 .. 2018-12-31
- **model selection / validation:** 2019-01-01 .. 2020-12-31
- **sealed final test:** **2021-01-01 .. 2021-12-31**

The 2021 labels must not be inspected, summarized, searched, or used for any choice until the champion specification is committed to the repository.

## 4. Candidate feature blocks

Fixed before validation results:

1. `GOLD_ONLY`
   - gold_r1, gold_r3, gold_r5, gold_r10, gold_r21, sigma20

2. `CORE3`
   - GOLD_ONLY
   - silver_r1, silver_r5, silver_r21, silver_age_days
   - platinum_r1, platinum_r5, platinum_r21, platinum_age_days

3. `CORE4`
   - CORE3
   - palladium_r1, palladium_r5, palladium_r21, palladium_age_days

4. `CORE3_SAFE_EXTERNAL`
   - CORE3
   - DGS10, DFII10, BREAKEVEN10_PROXY
   - BROAD_USD_INDEX, EURUSD_QUOTE, GBPUSD_QUOTE, JPY_PER_USD, CHF_PER_USD, CNY_PER_USD
   - VIX, NDX

Missing external values are filled using the **training-only median** for that feature.

## 5. Candidate models

Exactly these fixed models are allowed in the selection stage:

1. `LOGIT_L2`
   - StandardScaler
   - LogisticRegression(C=1.0, L2)

2. `LOGIT_EN`
   - StandardScaler
   - LogisticRegression(C=0.30, elastic-net, l1_ratio=0.50, saga)

3. `LDA_SHRINK`
   - StandardScaler
   - LinearDiscriminantAnalysis(solver=lsqr, shrinkage=auto)

4. `HGB`
   - HistGradientBoostingClassifier
   - learning_rate=0.03
   - max_iter=150
   - max_depth=3
   - min_samples_leaf=30
   - l2_regularization=1.0

5. `RANDOM_FOREST`
   - 300 trees
   - max_depth=4
   - min_samples_leaf=20
   - max_features=sqrt
   - class_weight=balanced

6. `EXTRA_TREES`
   - 300 trees
   - max_depth=4
   - min_samples_leaf=20
   - max_features=sqrt
   - class_weight=balanced

No additional model, hyperparameter, feature, interaction, regime rule or threshold may be invented after 2019-2020 results are seen.

## 6. Selection protocol

Validation = 2019-2020 only.

- chronological expanding predictions;
- 5-origin test blocks;
- a training label is usable only after its H3 target-end date is mature at the test block feature cutoff;
- no random split.

Champion selection is deterministic:

1. maximize **balanced accuracy**;
2. tie-break by lower **Brier**;
3. tie-break by lower **log loss**;
4. tie-break by simpler feature block in order GOLD_ONLY, CORE3, CORE4, CORE3_SAFE_EXTERNAL;
5. tie-break by model order listed above.

The exact winning feature block + model is written to a lock file and committed **before** sealed 2021 evaluation.

## 7. Baselines

Final 2021 report must include:

- expanding prior UP probability / majority-direction baseline;
- fixed `CORE3 + LOGIT_L2` comparator;
- locked Challenge V1 champion.

## 8. Full-coverage metrics

Primary:
- **balanced accuracy**

Required supporting:
- accuracy
- false-call rate
- Brier
- log loss
- UP recall
- DOWN recall
- confusion matrix counts
- prediction standard deviation.

## 9. Selective-call audit

The champion may also be evaluated as a confidence-filtered model, but **not tuned on 2021**.

From 2019-2020 validation predictions only, freeze confidence cutoffs for approximately:

- 60% coverage
- 40% coverage

using `abs(p_up - 0.5)`.

On sealed 2021 report:
- realized coverage
- selective accuracy
- selective balanced accuracy
- false-call rate
- UP/DOWN call counts.

The full-coverage result remains mandatory; abstention cannot hide it.

## 10. Integrity rule

Challenge V1 is invalid if 2021 target labels or any 2021 target-derived performance statistic are inspected before the champion lock commit.

After the champion lock commit, 2021 is evaluated once. Any subsequent modification is a new challenge version, not a repair of V1.

## 11. What counts as evidence

The final challenge report must show:

- validation leaderboard;
- champion lock file and commit hash;
- sealed-test workflow run;
- 2021 baselines and champion metrics;
- selective-call audit;
- exact predictions ledger artifact.

No post-hoc narrative can change the frozen model or score.
