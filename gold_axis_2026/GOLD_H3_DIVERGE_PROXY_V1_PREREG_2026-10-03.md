# DIVERGE-PROXY-H3 V1 — PREREGISTRATION

**Date:** 2026-10-03  
**Identity:** `DIVERGE_PROXY_H3_V1`  
**Branch:** `gold-h3-diverge-proxy-v1-20261003`  
**Evidence class:** `RETROSPECTIVE_PROXY_MECHANISM_TEST`  
**Role:** source-independent mechanism ablation for cross-asset non-confirmation.

## 1. Why this separate identity exists

The exact-source DIVERGE-H3 V1 contract was preregistered first but could not execute:
- FRED graph transport timed out;
- direct Federal Reserve DDP transport returned an empty body in the GitHub runner;
- no DEV threshold/result was produced.

Therefore exact DIVERGE-H3 remains **SOURCE_BLOCKED**.

This proxy identity tests the same cross-asset-divergence hypothesis without pretending the proxy sources are the frozen exact authority series.

## 2. Frozen sources

Gold/Silver:
- `GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_DAILY_PRICES.csv`

Cross-asset daily closes through Yahoo chart transport:
- U.S. Dollar Index proxy: `DX-Y.NYB`
- U.S. 10Y yield proxy: `^TNX`
- Nasdaq-100: `^NDX`
- VIX: `^VIX`

These are explicitly retrospective research proxies. They do not overwrite the project's H.10/H.15/Cboe source identities.

## 3. Origin alignment

For each H3 feature cutoff:
- use latest source observation with `source_date < feature_cutoff_date`;
- same-day values forbidden;
- no lag search;
- maximum staleness: 7 calendar days for USD/TNX, 5 for Gold/Silver/NDX/VIX.

## 4. Frozen feature family

Let `s=+1` for 12h Gold momentum UP, `s=-1` for DOWN.

Raw prior-date state:
1. `silver_ret1`
2. `gold_daily_ret1`
3. `usd_ret1`
4. `tnx_chg1`
5. `ndx_ret1`
6. `vix_ret1`

Momentum-conditioned:
7. `mom_x_silver = s*silver_ret1`
8. `mom_x_usd = s*usd_ret1`
9. `mom_x_yield = s*tnx_chg1`
10. `mom_x_ndx = s*ndx_ret1`
11. `mom_x_vix = s*vix_ret1`
12. `mom_x_gold_silver_gap = s*(gold_daily_ret1-silver_ret1)`

Each external return/change also receives a backward-looking 60-observation z-score, standardized against the preceding observations only.

13. `core_confirmation = mean(s*z_silver, -s*z_usd, -s*z_yield)`
14. `cross_dispersion = std(z_silver,z_usd,z_yield,z_ndx,z_vix)`

No post-result feature search.

## 5. Model

- StandardScaler
- LogisticRegression
- C=1.0
- solver=lbfgs
- class_weight=balanced
- seed=20261003
- monthly expanding-origin refit
- minimum matured training rows=80

Target:
`reversal_target = 1[y_up != momentum_up]`

Candidate universe:
`aurora_follows_momentum == True`.

## 6. Period roles

- DEV: 2023-2024
- confirmation: 2025
- final holdout: 2026 only after confirmation PASS

2026 cannot select source, feature, sign, lag, threshold or gate.

## 7. DEV threshold selection

Frozen grid:
`[0.35,0.40,0.45,0.50,0.55,0.60]`

Objective:
- maximize reversal F2

Eligibility:
- precision >= 0.45
- candidate rate <= 0.40

Tie-break:
1. recall descending
2. precision descending
3. candidate rate ascending
4. threshold descending

No eligible threshold => `NO_ELIGIBLE_DIVERGE_PROXY_THRESHOLD`.

## 8. 2025 confirmation

All must pass:
1. proxy recall > OPAL recall on same eligible universe;
2. >=1 true OPAL-missed reversal is nominated;
3. proxy precision >=0.40;
4. OPAL ∪ proxy recall > OPAL recall.

Failure => no formal 2026 evaluation.

## 9. 2026 holdout

Only after confirmation PASS:
- reversal recall / precision / candidate rate
- OPAL overlap
- proxy-only true reversals
- OPAL ∪ proxy recall
- V5-missed + OPAL-no-candidate reversals nominated
- diagnostic forced-flip rescue/broken/net

No HELIOS promotion from proxy evidence alone.

## 10. Interpretation rule

A PASS means only:
> cross-asset divergence contains useful complementary reversal information and exact-source DIVERGE deserves further data engineering.

A FAIL means:
> this preregistered proxy representation did not produce a sufficiently selective candidate channel.

It does not alter FLOW, SKEW, HAZARD, OPAL or V5.
