# SESSION MODEL-01B — FEATURE-SELECTED CLASSICAL LOGISTIC — PREREGISTRATION

**Date:** 2026-10-07  
**Status:** BINDING BEFORE 2025 TRANSPORT REVIEW

## Purpose

Test whether the SESSION Model-01 Classical CORE3 Logistic baseline is limited by its fixed feature representation.

Model-01 remains unchanged as the historical baseline. Model-01B changes **only the feature representation** while preserving the classical logistic estimator for the final fit.

## Final estimator identity

- StandardScaler
- LogisticRegression
- L2 penalty
- C = 1.0
- solver = lbfgs
- threshold = 0.50
- class_weight = None

This is intentionally the same final estimator identity as SESSION Model-01.

## Candidate feature universe

### Daily CORE3
- gold_r1, gold_r3, gold_r5, gold_r10, gold_r21, sigma20
- silver_r1, silver_r5, silver_r21, silver_age_days
- platinum_r1, platinum_r5, platinum_r21, platinum_age_days

Daily source-ready rule: latest common daily observation from a **strictly earlier America/New_York calendar date** than target start.

### Session-clock XAU15 state

Rebuilt from governed XAU/USD 15-minute data using the exact target-start clock.

Candidate families:
- returns: 1h, 3h, 6h, 12h, 24h, 48h
- lag2
- realized volatility: 6h, 12h, 24h, 48h
- 24h upside/downside semivolatility and ratio
- jump concentration
- range
- up-fraction
- max drawdown
- recovery
- close location
- 6h / 24h slope
- age of largest positive / negative return

Availability is **strictly before target_start**. A bar becoming available exactly at target_start is rejected. The known New York 17:00–18:00 maintenance interval may use the last real pre-maintenance state under the already-governed deterministic maintenance rule; no synthetic OHLC bar is created.

No target-window observation is permitted.

## Chronology

- 2022: governed warm-up/training support only
- 2023–2024: development and feature selection
- 2025: one-time frozen-specification causal transport
- 2026: unopened for selection

## Feature selection

For every session separately and every 5-row outer development block:

1. Training contains only same-window outcomes whose target_end has matured before the outer block starts.
2. Candidate selection is performed only inside that training history.
3. Up to three chronological inner validation folds are used.
4. StandardScaler + L1 LogisticRegression is used only as a selector.
5. Selector C grid: 0.03, 0.10, 0.30, 1.00, 3.00.
6. C is chosen by inner Balanced Accuracy; candidates within 1pp use lower Brier, then fewer variables, then smaller C.
7. The selected variables are refit with the **unchanged Classical Logistic L2 C=1.0** estimator.
8. The outer block is never used to select its own variables.

## Frozen per-session feature set

After the complete 2023–2024 development replay:

- rank variables by outer-block selection frequency;
- prefer variables selected in both 2023 and 2024;
- freeze 3–8 variables per session;
- if fewer than 3 satisfy cross-year stability, fill from the highest-frequency development-only variables;
- no 2025 outcome may change the frozen set.

## Comparator

On identical development rows compare:
- CORE3_CLASSICAL — fixed 14-variable Model-01 representation
- SELECTED_CLASSICAL — block-local feature-selected representation

Primary metric: Balanced Accuracy.
Required reporting: Accuracy, Balanced Accuracy, UP recall, DOWN recall, Brier, log loss.

## 2025

Use the frozen per-session feature set with the unchanged Classical Logistic estimator in the same five-row causal replay chronology.

No 2025 retuning, variable reselection, threshold change or clock change is allowed.
