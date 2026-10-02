# GOLD SHORT-HORIZON GLOBAL XAU — Raw-Source CART Pattern Screen Authority

**Date:** 2026-10-02  
**Status:** FROZEN PRE-RUN  
**Target:** Global XAU daily H3 direction  
**Purpose:** test whether the already-available raw daily source families contain simple, interpretable regime/pattern structure before building a more complex regime router.

## 1. Model

Single shallow CART classifier:

- criterion: log-loss
- max_depth: 3
- min_samples_leaf: 60
- random_state: 20261001
- probability threshold: 0.50
- no hyperparameter search.

The model is deliberately small so its split rules can be inspected later.

## 2. Raw source families under test

Long-history daily sources usable in the 2022-2024 DEV program:

- Gold — active R2 pinned StakTrakr reconstruction
- Silver — active R2 pinned StakTrakr reconstruction
- Platinum — active R2 pinned StakTrakr reconstruction
- Palladium — active R2 pinned StakTrakr reconstruction
- NASDAQ-100 — `NASDAQ100_FRED`
- S&P 500 — `SP500_FRED`
- Dow Jones Industrial Average — `DJIA_FRED`.

The XAU 1-hour series is not mixed into this first screen because its available history starts in 2022 and therefore cannot support the same pre-DEV expanding-history contract at the start of 2022. It is reserved for a separate intraday add-on screen.

## 3. Minimal lag-safe transforms

Raw source identities remain unchanged. For stationarity and comparability the screen creates only deterministic past-looking transforms:

- 1-day log return
- 5-day log return
- 21-day log return

for each raw daily price/index source.

For Gold only, the existing past-looking 20-day realized daily-return volatility (`sigma20`) is also included.

No future observation enters a feature.

## 4. Source blocks

The same CART is evaluated on four fixed blocks:

1. `GOLD_ONLY`
2. `METALS4` = Gold + Silver + Platinum + Palladium
3. `GOLD_EQUITY3` = Gold + NASDAQ-100 + S&P 500 + DJIA
4. `ALL7` = all seven daily raw sources.

This is a source-family screen, not a feature-search loop.

## 5. Evaluation

- DEV authority: 2022-2024 only.
- chronological expanding training.
- five-origin DEV blocks.
- a training label is usable only if its H3 target-end date is mature by the block feature-cutoff date.
- 2025/2026 are not used in this screen.
- report Brier, log loss, accuracy, balanced accuracy, prediction SD, annual metrics.
- preserve split counts, feature importances and the final pre-2025 tree rules for later log/rule inspection.

## 6. Interpretation

This experiment answers only:

**Do these already-available raw daily source families produce a simple nonlinear H3 direction pattern that a shallow tree can exploit?**

A positive result may motivate a later regime/router design. It does not itself authorize a router or tactical rule.
