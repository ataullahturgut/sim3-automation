# GOLD CONTROL — EXTERNAL DUKASCOPY XAUUSD FEATURE SPINE V1 RESULT

**Date:** 2026-09-22  
**Identity:** `EXTERNAL_DUKASCOPY_XAUUSD_FEATURE_SPINE_V1_RESEARCH`  
**Status:** `STAGED_AND_SOURCE_HARMONIZATION_DIAGNOSTIC_PASSED`  
**Authority:** RESEARCH STAGING ONLY — NOT GOVERNED INPUT / NOT RUNTIME

## 1. Data staged

A public XAUUSD one-minute bid/ask history mirror was used only as a retrieval source for older research evidence.

Raw third-party minute files were **not copied** into the Gold Control repository.

The staged Gold Control artifact is a compact daily feature spine derived as:

`bid/ask inner join -> mid close -> 5-minute last close -> America/New_York daily realized features`.

Derived features include:
- daily last mid close;
- retained 5-minute bar count;
- realized variance;
- realized third moment;
- downside realized variance;
- positive / negative realized semivariance;
- average / maximum bid-ask spread.

Staged period:
- 2018-01-01 through 2021-12-31.

Consolidated artifact:
- `gold_axis_2026/external_data/dukascopy_xauusd_mid_5m_daily_features_2018_2021.csv`

Consolidated audit:
- `gold_axis_2026/external_data/dukascopy_xauusd_mid_5m_daily_features_2018_2021_audit.json`

After dropping seven zero-variance holiday rows:
- retained days = **1038**.

## 2. Provenance

Every staged half-year audit stores:
- source repository identity;
- source month;
- exact ask blob SHA;
- exact bid blob SHA;
- source row counts;
- timestamp-inner-join row count.

This allows the external-derived feature spine to be independently reproduced.

## 3. Overlap harmonization with governed internal cache

Overlap against `public.xau_intraday_research_cache_5m`:

- common days = **345**
- first common = 2020-04-06
- last common = 2021-12-30

Close-return comparison:
- n = 344
- Pearson correlation = **0.9999746**
- sign agreement = **99.4186%**
- mean absolute return difference = **0.00004326**

Level comparison:
- close correlation = **0.9999991**
- median external/internal close ratio = **0.99999725**

Realized-risk comparison:
- log realized variance correlation = **0.9981286**
- log downside realized variance correlation = **0.9979377**
- median RV ratio = **0.9977241**
- median downside-RV ratio = **0.9955379**

Top-20% downside-risk state:
- both high = 69
- external-only high = 1
- internal-only high = 1
- neither high = 274
- state agreement = **99.4203%**

## 4. Interpretation

The overlap diagnostics indicate extremely close source agreement for levels, returns and realized-risk measures.

That is sufficient to classify the external-derived spine as a **credible research extension candidate**.

It is not sufficient by itself to silently merge the data into a frozen governed model identity.

Any pre-2022 SQRT/Router extension using this spine must receive a new preregistered research identity and must:
1. reproduce the governed 2020-2021 overlap where possible;
2. report source-boundary sensitivity;
3. preserve 2025 as non-tuning evidence;
4. keep production DB read-only.

## 5. Governance

- raw third-party data not redistributed in project;
- only derived daily research features stored;
- production database unchanged;
- no runtime promotion;
- no 2025 tuning.
