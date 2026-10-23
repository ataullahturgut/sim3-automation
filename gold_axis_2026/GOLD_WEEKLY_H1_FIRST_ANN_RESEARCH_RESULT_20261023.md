# GOLD WEEKLY H=1 — First four-metal ANN real 234-week replay

**Date:** 2026-10-23
**Branch:** gold-weekly-h1-ann-v1-20261023
**Monthly branch:** gold-midas-headswap-v1-20260925 — no monthly code changed.
**Workflow:** https://github.com/ataullahturgut/sim3-automation/actions/runs/40001347644 — ALL SUCCESS.
**Full result artifact:** gold-weekly-h1-ann-first-model-complete-2022-2026-v1.
**Scientific status:** Chronology/leakage research PASS; superior-to-baseline performance NOT established.

## Frozen new weekly research contract

- Horizon H=1 complete ISO calendar week. Issued after the previous week is complete, predicts next Mon–Sun weekly aligned-day **mean** XAU/USD and the **last common trading-day reference quote**.
- The second endpoint is NOT an official Friday exchange market-close tick. Source StakTrakr uses LBMA-labeled daily prices.
- Four metals in fixed order AU AG PT PD. 16 input features, four for each metal: previous weekly-average log return, last-vs-first observed daily price log move, within-week realized daily log-return volatility, within-week high/low log ratio. Only last completed week and one week before it.
- Independently trained ANN, NOT monthly FULL7 model weights. Architecture input 16, hidden 8 tanh, 2 standardized output returns. sklearn MLPRegressor solver lbfgs, alpha=1, max_iter=180, tol=1e-5, random_state=1701. No hyperparameters selected by viewing 2025/2026.
- Target 1: next week mean over previous-week mean, log return. Target 2: next week's final common daily quote over previous-week final quote, log return.
- Expanding training, one forecast model fit each prior-week origin, only known completed histories and training-only X/Y scaler.
- Evaluation 2022-04-04 through 2026-09-21; 234 targets. Most recent pinned price data is September 2026; week 2026-09-28 is incomplete and excluded.
- Data from lbruton/StakTrakr pinned pre-2026 Git commit ed2e549f82ba0d1cd3ca32842b82d3888d301e01 and 2026 Git commit 02964d0324dde362099976c867f5077a369acaa5. Only these original source-specific PRICE_SQL rows and MONTHLY_SQL monthly exact parity from gold_monthly_h1_neon_source_v2.py. 873 valid complete aligned weeks from 2010-01-04 to 2026-09-21; 3+ same-day prices for all four metals in each week.
- Single source payload verified by SHA-256 a36cebdd1dc2b46766e42407bdf275115b1656e500b3cc3dadfba8a1d5597b2e.
- **First-print/PIT NOT certified.** These are retrospective pinned Git research data, not evidence of prices exactly available historically at each time.
- No Neon writes; original monthly model code unchanged.
- 234/234 target weeks PASS active poison: target-week prices multiplied by 1234 and future 2099 sample cannot affect model inputs, training labels or features; one pilot whole-model rerun verified exact output invariant.

## Weekly mean endpoint

| Target period | weeks | ANN MAPE | previous-week-naive MAPE | ANN ΣAE USD | naive ΣAE USD | ANN correct weekly mean direction |
|---|---:|---:|---:|---:|---:|---:|
| DEV 2022-04..2024-12 | 144 | 1.307515% | **1.295812%** | 3927.832927 | 3853.294167 | 88/144 (61.11%) |
| TEST 2025 | 52 | 1.971075% | **1.824877%** | 3666.630279 | 3362.927500 | 31/52 (59.62%) |
| STRESS 2026 Jan..Sep21 | 38 | **2.301405%** | 2.789669% | 4041.513926 | 4903.868000 | 26/38 (68.42%) |

April 2022 pilot: target week 2022-04-04 mean forecast 1939.540652, actual 1928.630000, APE 0.56572%.

## Final observed daily reference quote endpoint

| Target period | weeks | ANN MAPE | naive previous quote MAPE | ANN ΣAE USD | naive ΣAE USD | ANN correct last-quote direction |
|---|---:|---:|---:|---:|---:|---:|
| DEV 2022-2024 | 144 | 1.792207% | **1.516420%** | 5360.716289 | 4539.550000 | 71/144 |
| TEST 2025 | 52 | 2.574472% | **2.104955%** | 4773.845343 | 3934.450000 | 22/52 |
| STRESS 2026 Jan-Sep | 38 | 4.553286% | **4.490630%** | 7536.267884 | 7482.230000 | 22/38 |

**Scientific decision:** MODEL FITTING AND CHRONOLOGY ACCEPTED; do NOT promote ANN weekly mean endpoint because it loses to naive baseline in DEV and 2025, though it beats it in already opened 2026 stress. Do NOT promote final quote ANN, worse than naive in all 3 periods. No application production integration or automatic trading. Future research only from DEV, and historical as-of firstprint verification remains important.

## Source and workflow

Runner: gold_axis_2026/tools/gold_weekly_h1_ann_4metal_v1.py
Actions: .github/workflows/gold-weekly-h1-ann-four-metal-v1.yml
Artifact: gold-weekly-h1-ann-first-model-complete-2022-2026-v1 (all 234 predictions and summaries).
