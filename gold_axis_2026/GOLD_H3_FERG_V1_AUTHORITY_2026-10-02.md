# FERG-H3 V1 — FORECASTABILITY ERROR-RISK GATE AUTHORITY

**Date:** 2026-10-02  
**Identity:** `FERG_H3_V1_RESEARCH`  
**Project:** GOLD SHORT-HORIZON GLOBAL XAU  
**Base direction engine:** NOVA ledger A1 = frozen ARCR-style 75% global CORE3 Logistic + 25% recent252 balanced Logistic  
**Status:** PREREGISTERED / RESEARCH-ONLY / NO RUNTIME PROMOTION

## 1. Hypothesis

The 2026 failure is not fully explained by novelty. The next question is whether the **forecast error itself is predictable before the H3 target matures**.

FERG does not predict Gold direction directly. It predicts:

`P(ERROR | information available at forecast issue)`

for the frozen A1 H3 direction call.

If forecast error risk is low, the A1 direction is retained as UP or DOWN. If forecast error risk is high, FERG outputs UNCERTAIN.

## 2. Frozen chronology

- Underlying H3 ledger: `GOLD_H3_NOVA_V1_PREDICTIONS_2026-10-02.csv`.
- For every meta-model forecast origin, meta-training rows must satisfy:
  `target_end_date_h3 <= current feature_cutoff_date`.
- No row may train on an H3 outcome that has not matured.
- Meta burn-in/history begins in 2017.
- Selection authority: **2019-2021 only**.
- Confirmation: **2022-2024** (already-opened wider project history, not a pristine blind lockbox).
- 2025 and 2026: frozen report-only transport/stress.
- No 2025/2026 retuning.

## 3. Frozen base call

Base probability:
- `p_A1_arcr`.

Base direction:
- UP iff `p_A1_arcr >= 0.50`,
- otherwise DOWN.

Meta target:
- ERROR = 1 iff base direction is wrong,
- ERROR = 0 iff base direction is correct.

FERG V1 never flips the base direction. It only accepts or abstains.

## 4. Origin-safe meta features

Current-origin features:
- A1 probability distance from 0.50
- A0/global probability distance from 0.50
- A3 probability distance from 0.50
- global-vs-recent probability disagreement
- A1-vs-A3 disagreement
- CORE novelty
- cross-market novelty
- novelty difference
- absolute numerical H3 return forecast
- sign agreement between A3 direction and numerical return head
- conformal half-width
- return-to-conformal-width ratio
- ACI alpha
- base predicted direction flag.

Causal matured-history features, recomputed at every origin:
- prior A1 accuracy over last 20, 60, 126 matured H3 calls
- prior A1 UP precision over last 60 matured calls
- prior A1 DOWN precision over last 60 matured calls
- prior realized H3 return volatility over last 20 and 60 matured outcomes
- prior actual UP share over last 60 matured outcomes.

All lagged features use only already-matured historical rows.

## 5. Frozen meta-model candidates

Two deliberately low-capacity candidates:

1. **META_LOGIT_L2**
   - StandardScaler
   - LogisticRegression L2
   - C=1.0

2. **META_HGB_SHALLOW**
   - HistGradientBoostingClassifier
   - max_depth=2
   - max_iter=80
   - learning_rate=0.05
   - min_samples_leaf=40
   - l2_regularization=1.0

Meta-model predicts P(ERROR).

No larger tree ensemble, neural net or post-2021 hyperparameter search is allowed in V1.

## 6. Selection rule — 2019-2021 only

For every candidate, generate chronological out-of-sample P(ERROR) by expanding refit.

Candidate acceptance thresholds are derived from the candidate's own 2019-2021 P(ERROR) distribution at nominal retained coverages:
- 70%
- 60%
- 50%
- 40%
- 30%
- 20%.

A threshold is eligible if:
- realized retained coverage >= 20%;
- at least 100 accepted calls;
- accepted selective accuracy exceeds the full A1 accuracy by at least 2 percentage points;
- accepted and rejected sets are both non-empty.

Selection order among eligible thresholds:
1. highest selective balanced accuracy,
2. highest selective accuracy,
3. largest accepted-vs-rejected accuracy gap,
4. higher coverage,
5. lower error-probability Brier.

If no threshold is eligible, FERG V1 fails closed and no gate is promoted.

## 7. Evaluation

Meta error-risk quality:
- Brier for ERROR probability
- log loss
- ROC AUC
- mean P(ERROR) on actually correct vs actually wrong calls.

Selective direction quality:
- coverage
- selective accuracy
- selective balanced accuracy
- UP precision
- DOWN precision
- UP capture recall over all actual UP days
- DOWN capture recall over all actual DOWN days
- false-UP FPR over all actual DOWN days
- false-DOWN FPR over all actual UP days
- accepted accuracy
- rejected accuracy
- accepted-vs-rejected accuracy gap.

## 8. Promotion logic

FERG is a mechanism success only if the frozen gate:
- improves 2022-2024 selective accuracy over full A1 while preserving >=20% coverage;
- shows positive accepted-vs-rejected accuracy separation in 2022-2024;
- does not rely on 2025/2026 tuning.

2025/2026 transport is reported regardless of success. Failure there cannot alter V1.

## 9. Output object

For each H3 origin:

`[P_UP_A1, P_ERROR_FERG, FORECASTABILITY, SIGNAL]`

where:
- FORECASTABILITY = 1 - P_ERROR_FERG
- SIGNAL = UP or DOWN when accepted
- SIGNAL = UNCERTAIN when rejected.
