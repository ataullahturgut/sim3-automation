# SESSION MODEL-03B — NOVA A1 / ARCR FEATURE-SELECTED CHALLENGER — PREREGISTRATION

**Date:** 2026-10-07  
**Status:** BINDING BEFORE 2025 REVIEW

## Baseline identity

SESSION Model-03 baseline is the already verified NOVA A1 / ARCR session model:

- global head: StandardScaler + LogisticRegression(L2, C=1.0)
- recent head: last 252 matured same-window rows, StandardScaler + LogisticRegression(L2, C=1.0, class_weight=balanced)
- mixture: **0.75 global + 0.25 recent252-balanced**
- threshold: 0.50

The baseline is preserved unchanged.

## Challenger purpose

Test whether A1 improves when its feature representation is selected **for the A1 mixture itself** and separately by session.

Model-01B feature selections are not inherited.

## Candidate universe

### Daily CORE3
- gold_r1, gold_r3, gold_r5, gold_r10, gold_r21, sigma20
- silver_r1, silver_r5, silver_r21, silver_age_days
- platinum_r1, platinum_r5, platinum_r21, platinum_age_days

Availability: latest daily observation from a strictly earlier America/New_York calendar date than session start.

### Session-clock XAU15
- return horizons: 1h, 3h, 6h, 12h, 24h, 48h
- lag2
- realized volatility: 6h, 12h, 24h, 48h
- upside/downside semivolatility and ratio
- jump concentration
- 24h range
- up-fraction
- max drawdown
- recovery
- close location
- 6h / 24h slope
- age of max positive / negative 15m return

Availability: completed 15-minute information with **available_at < target_start**. Equality is prohibited. The existing deterministic NY 17:00–18:00 maintenance exception remains allowed; no synthetic OHLC bar is created.

## Chronology

- 2022: governed warm-up only
- 2023–2024: feature selection + development
- 2025: one-time frozen-specification transport
- 2026: unopened

Only matured same-window targets may enter either A1 head.

## Nested A1-specific selection

For each session and every 5-row outer development block:

1. Form the outer training history using only matured same-window outcomes.
2. Create up to three chronological inner validation folds.
3. Use class-balanced L1 logistic only to propose sparse feature sets for each C in:
   `0.03, 0.10, 0.30, 1.00, 3.00`.
4. Evaluate each proposed set using the **actual A1 mixture**:
   - 0.75 global L2 C=1.0
   - 0.25 recent252 balanced L2 C=1.0
5. Select C by inner Balanced Accuracy; within 1pp prefer lower Brier, then fewer features, then smaller C.
6. Refit the selected features with the actual A1 mixture and score the untouched outer block.
7. Outer outcomes never select their own variables.

## Frozen session set

After 2023–2024 development:
- rank features by outer-block selection frequency;
- prefer features selected in both 2023 and 2024;
- freeze 3–8 variables per session;
- no 2025 outcome may change the set.

## Exact comparator

On identical rows report:
- BASELINE_A1_ARCR — original CORE3 A1
- SELECTED_A1_ARCR — A1 mixture using selected variables

Required metrics:
- N
- Accuracy
- Balanced Accuracy
- UP recall
- DOWN recall
- Brier
- log loss

## 2025

After the session-specific feature sets are frozen, replay both baseline and challenger through the same continuous 5-row causal chronology and report only 2025 rows.

No 2025 tuning, no threshold change, no mixture-weight change, no variable reselection.
