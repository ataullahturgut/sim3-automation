# GOLD NEXT-DAY DIRECTION — HOURLY XAU MANIFEST

**Date:** 2026-10-02  
**Status:** ACTIVE RESEARCH / V1 COMPLETE  
**Source:** `XAU_USD_TWELVE_1H_RESEARCH_V1`

## Objective

Predict whether the next available trading day's 16:00 America/New_York XAU/USD anchor will be UP or DOWN versus the current day's 16:00 anchor.

Forecast issue: immediately after current-day 16:00 NY hourly bar.

## Data

- raw XAU/USD hourly observations: **17,644**
- source coverage: 2022-01-02 .. 2024-12-31
- usable daily issue rows after feature/target maturity: **705**
- 2022 = initial training history
- 2023-2024 = strict expanding out-of-sample scoring

## Features

Past-only hourly transforms:
- 1h / 3h / 6h / 12h / 24h log returns
- 6h / 12h / 24h realized hourly-return volatility
- 6h / 12h / 24h up-hour fraction
- 12h / 24h log close range
- 6h / 12h / 24h log-price slope
- local-day first-bar-to-16:00 session return

## V1 models

### Logistic L2

2023-2024:
- N **468**
- accuracy **54.91%**
- balanced accuracy **54.41%**
- Brier **0.2598**
- log loss **0.7178**
- UP recall **64.23%**
- DOWN recall **44.59%**

2023:
- accuracy **56.25%**
- balanced accuracy **56.35%**

2024:
- accuracy **53.69%**
- balanced accuracy **52.76%**

### HistGradientBoosting

2023-2024:
- accuracy **48.29%**
- balanced accuracy **47.98%**
- Brier **0.2807**
- log loss **0.7625**

### Baselines

Expanding majority-probability:
- 2023-2024 accuracy **52.56%**
- balanced accuracy **50.00%**
- Brier **0.2497**
- log loss **0.6925**

Same-day session-momentum direction:
- accuracy **47.86%**
- balanced accuracy **47.81%**

## Initial interpretation

- The simple Logistic model extracts a directional signal from hourly XAU structure and exceeds majority-direction accuracy by about 2.35 percentage points.
- The probability stream is not yet well calibrated: Brier/log-loss remain worse than the majority-probability baseline.
- The nonlinear HGB V1 does not improve the result.
- The signal persists in both 2023 and 2024, but is weaker in 2024.
- Current asymmetry: UP recall materially exceeds DOWN recall.

Largest standardized Logistic coefficients:
1. ret_12h +0.740
2. upfrac_12h -0.529
3. upfrac_24h +0.440
4. session_ret -0.328
5. range_24h -0.244
6. upfrac_6h +0.226
7. rv_24h +0.221
8. slope_6h -0.203

## Provenance

- authority: `GOLD_NEXTDAY_DIRECTION_HOURLY_AUTHORITY_2026-10-02.md`
- result: `GOLD_NEXTDAY_DIRECTION_HOURLY_RESULT_2026-10-02.md`
- workflow run: **37002176253**

## Next research

Before adding external data, inspect:
- monthly/market-state variability,
- DOWN misses,
- coefficient stability,
- simple calibration,
- whether a compact subset can improve 2024 stability.

2025/2026 hourly scoring requires extending the same 1h raw source beyond 2024 under an explicit source/clock refresh; it is not available in the current registered 1h research backfill.


## V2 — Ordered hourly lag experiment

Authority:
- `GOLD_NEXTDAY_DIRECTION_HOURLY_LAG_V2_AUTHORITY_2026-10-02.md`

Workflow run:
- **37004250723**

Representation:
- 24 ordered recent hourly returns
- four six-hour prior-day return blocks
- realized volatility / up-hour fractions
- shock magnitude and shock age
- same-sign streak
- current and previous session return
- 46 total V2 features.

Strict 2023-2024 OOS results:

| Model | Accuracy | Balanced acc | Brier | Log loss | False calls |
|---|---:|---:|---:|---:|---:|
| V1 Logistic L2 | **54.49%** | **53.96%** | 0.2600 | 0.7182 | **45.51%** |
| Lag Logistic L2 | 48.93% | 48.57% | 0.2776 | 0.7628 | 51.07% |
| Lag Elastic-Net Logistic | 49.79% | 49.31% | 0.2633 | 0.7233 | 50.21% |
| Lag MLP-16 | 49.15% | 48.99% | 0.4576 | 3.0826 | 50.85% |
| Majority probability | 52.56% | 50.00% | **0.2497** | **0.6926** | 47.44% |

Year split:
- V1 Logistic: 2023 **55.36%**, 2024 **53.69%**
- Lag Logistic L2: 2023 **50.89%**, 2024 **47.13%**
- Lag Elastic-Net: 2023 **51.34%**, 2024 **48.36%**
- Lag MLP-16: 2023 **54.91%**, 2024 **43.85%**.

Interpretation:
- preserving 24 individual hourly return lags did **not** improve the V1 summary-feature Logistic model;
- the full lag representation overfits materially, especially in 2024;
- Elastic-Net reduces but does not remove the deterioration;
- the MLP is severely overconfident and unstable;
- the useful signal is more likely in compact path summaries/interactions than in a raw 24-hour lag vector.

The coefficient audit still identifies structured lag effects, especially lag 15, lag 16, lag 13 and the 24-29h block, but these effects are not stable enough in the full V2 representation to improve OOS performance.

V2 result files:
- `GOLD_NEXTDAY_DIRECTION_HOURLY_LAG_V2_RESULT_2026-10-02.md`
- `GOLD_NEXTDAY_DIRECTION_HOURLY_LAG_V2_METRICS_2026-10-02.csv`
- `GOLD_NEXTDAY_DIRECTION_HOURLY_LAG_V2_COEFFICIENTS_2026-10-02.csv`.


## V3 — One-by-one hourly lag selection

Authority:
- `GOLD_NEXTDAY_DIRECTION_HOURLY_LAG_V3_SELECTION_AUTHORITY_2026-10-02.md`

Workflow run:
- **37006109253**

Selection design:
- all 24 hourly return lags tested individually on 2023;
- 2023 used as lag-selection/development year;
- greedy forward retention with frozen criteria;
- selected subset then frozen and reported on 2024;
- no 2025/2026 data used.

Selected hourly lag:
- **`hr_ret_lag2` only**.

One-at-a-time 2023 leading effects versus V1:
- lag2: accuracy +0.89 pp; balanced accuracy +0.90 pp; Brier +0.0002
- lag19: accuracy +0.45 pp; balanced accuracy +0.47 pp; Brier -0.0014
- lag8: accuracy +0.45 pp; balanced accuracy +0.45 pp; Brier -0.0008
- lag3: accuracy +0.00 pp; balanced accuracy +0.03 pp; Brier -0.0013
- lag22: accuracy +0.00 pp; balanced accuracy -0.01 pp; Brier -0.0038; log loss -0.0130.

Frozen selected-subset results:

| Model | Period | Accuracy | Balanced acc | Brier | UP recall | DOWN recall | False calls |
|---|---|---:|---:|---:|---:|---:|---:|
| V1 | 2023 | 55.36% | 55.47% | 0.2591 | 67.57% | 43.36% | 44.64% |
| V3 + lag2 | 2023 | **56.25%** | **56.37%** | 0.2593 | **69.37%** | 43.36% | **43.75%** |
| V1 | 2024 | 53.69% | 52.76% | 0.2609 | 61.48% | 44.04% | 46.31% |
| V3 + lag2 | 2024 | **54.51%** | **53.59%** | **0.2606** | **62.22%** | **44.95%** | **45.49%** |
| V1 | 2023-2024 | 54.49% | 53.96% | 0.2600 | 64.23% | 43.69% | 45.51% |
| V3 + lag2 | 2023-2024 | **55.34%** | **54.80%** | **0.2600** | **65.45%** | **44.14%** | **44.66%** |

Interpretation:
- the full 24-lag vector was harmful, but **one individual lag adds a small, persistent directional improvement**;
- lag2 survives both the 2023 selection year and 2024 frozen-subset confirmation;
- the gain is about +0.85 pp accuracy over 2023-2024 and lowers false calls by about 0.85 pp;
- probability quality is essentially unchanged;
- other lags may help calibration without improving direction and are retained in the audit table, not promoted into the V3 subset.

V3 evidence:
- `GOLD_NEXTDAY_DIRECTION_HOURLY_LAG_V3_RESULT_2026-10-02.md`
- `GOLD_NEXTDAY_DIRECTION_HOURLY_LAG_V3_ONE_AT_A_TIME_2023.csv`
- `GOLD_NEXTDAY_DIRECTION_HOURLY_LAG_V3_SELECTION_STEPS_2026-10-02.csv`
- `GOLD_NEXTDAY_DIRECTION_HOURLY_LAG_V3_METRICS_2026-10-02.csv`.
