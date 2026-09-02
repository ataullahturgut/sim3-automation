# GOLD CONTROL — CAUSAL PATCH R1 DAILY FEATURE PIT CHANGE CONTROL V7

**Date frozen:** 2026-09-02  
**Status:** `FROZEN_BEFORE_V7_MODEL_RESULT`  
**Parent candidate:** `CAUSAL_PATCH_R1_REPRO_V1_5_DAILY_TRAIN_HOURLY_ANCHOR_ORIGIN_SAFE`  
**Reserved V7 identity:** `CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE`  
**Evidence class:** `HISTORICAL_REPLAY_MODEL_IMPACT` only until a genuinely future origin is issued.  

## 1. Gap being closed

V6 proved the monthly training-level bridge and hourly month-end anchor bridge, but its daily-return feature helper permitted `1day` observations dated on the forecast origin calendar date. Gold Data R2.7 explicitly treats same-exchange-day vendor `1day` bars as ineligible because they may still be in progress.

This is a point-in-time issuer-safety repair, not a model search.

## 2. Frozen V7 change

For every training, validation and test sample:

- `origin_date = target_month_start - 1 calendar day`;
- eligible Twelve Data `XAU/USD`, `1day` feature observations must satisfy `observation_date < origin_date`;
- therefore no same-origin-date `1day` bar may enter the 252-return input window;
- no forward fill, interpolation, alternate provider, NY17 relabelling or synthetic observation is allowed.

The following remain unchanged from V6:

- Patch Transformer architecture family;
- geometry `L=252 / P=21 / D=32`;
- optimizer, loss, seeds, training/validation split logic and ensemble-of-seeds median;
- daily training monthly-level semantic;
- hourly month-end anchor semantic;
- NASDAQ/FEDFUNDS/USD-CNY/GPR rules;
- locked evaluation window `2023-01 → 2026-07`, `N=43`;
- Random Walk benchmark and acceptance gates.

## 3. Hard PIT gate

PASS requires across all 43 locked test origins:

- exactly 43 target samples;
- at least 252 eligible daily-return observations per origin;
- selected daily feature maximum date is strictly earlier than the origin date;
- `same_origin_date_feature_uses = 0`;
- `future_information_violations = 0`;
- deterministic repeated replay equality;
- target reconciliation `43/43`;
- RW reconciliation `43/43`.

## 4. Frozen performance gate

After the hard PIT gate passes, V7 must satisfy the inherited V6/V4 model-impact gates:

- MAPE `< RW MAPE`;
- MAE `< RW MAE`;
- worst APE `<= 1.25 × RW worst APE`.

No result-dependent change to cutoff, source, geometry, threshold, architecture or training rules is allowed.

## 5. Decision identities

PASS:

`PATCH_R1_V7_COMPLETED_SESSION_DAILY_FEATURE_MODEL_IMPACT_PASS`

FAIL:

`PATCH_R1_V7_COMPLETED_SESSION_DAILY_FEATURE_MODEL_IMPACT_FAIL_NO_RETUNE`

A PASS remains historical replay evidence. It does not itself authorize a `PRODUCTION` forecast row. It only makes the executable/input identity eligible for the immutable forward snapshot + contract issuance path.

## 6. Write isolation

This audit/model-impact run must write:

- Neon: `NONE`;
- forecast ledger: `NONE`;
- Decision Store: `NONE`;
- raw vendor market values to logs: `NO`.
