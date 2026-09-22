# GOLD CONTROL — HARMONIZED PRE-2022 SQRT + ROUTER EXTENSION V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `HARMONIZED_PRE2022_SQRT_ROUTER_EXTENSION_V1_RESEARCH`  
**Runtime authority:** NONE  
**Production DB writes:** FORBIDDEN

## 1. Purpose

Use the newly staged Dukascopy-derived XAUUSD feature spine to test whether 2020 and 2021 can add valid pre-2025 SQRT alarm support.

This is a **harmonized external-source extension**, not a claim that the external source is literally the same vendor feed as the governed cache.

## 2. Source acceptance frozen before 2020/2021 model outcomes

Overlap audit against the governed 5-minute cache over 2020-04-06..2021-12-30 produced:

- common days = 345;
- common-date return correlation = 0.9999746;
- return-sign agreement = 99.4186%;
- close-level correlation = 0.9999991;
- log realized-variance correlation = 0.9981286;
- log downside-realized-variance correlation = 0.9979377;
- top-20% downside-risk state agreement = 99.4203%.

These diagnostics are frozen as the basis for permitting a research-only harmonized extension.

## 3. Historical feature source

Use:
`gold_axis_2026/external_data/dukascopy_xauusd_mid_5m_daily_features_2018_2021.csv`

Construction:
- public one-minute Dukascopy bid/ask mirror;
- exact bid/ask timestamp inner join;
- mid close = (bid+ask)/2;
- 5-minute last-close resampling;
- America/New_York daily grouping;
- weekdays only;
- >=240 5-minute bars;
- zero-realized-variance retained weekdays removed in the consolidated file.

## 4. Frozen model rules

Reconstruct without alteration:

### SQRT-HAR-DR
- same daily downside realized variance definitions;
- same HAR daily/weekly/monthly windows;
- same yearly expanding formation;
- same minimum formation n=250;
- same 80th-percentile formation high-risk threshold;
- alarm iff SQRT-HAR-DR forecast >= formation threshold.

Evaluate only target years 2020 and 2021.

### UP Router V2 direct experts
- TTSM-S2;
- TTSM-S1;
- Bonato AR1_RM QBoost h=1 median;
- AR1_RM_LOGIT;
- RM_LOGIT.

All original expert parameters remain frozen.

### Router competence
For year Y:
- formation = common expert rows with target year Y-1;
- matured within-year outcomes added causally;
- same legacy context;
- same >=30 UP calls;
- precision >0.50;
- false-UP FPR <0.50;
- one-sided 90% Wilson lower-bound ranking;
- same fixed expert tie order.

## 5. Primary outputs

For 2020 and 2021 report:
- SQRT alarm count;
- actual-DOWN / actual-UP anatomy;
- Router-UP overlap;
- good / bad veto anatomy.

Then report combined 2020-2024 support in two layers:

1. **governed-source primary support:** 2022-2024, unchanged;
2. **harmonized research support:** 2020-2024 including external 2020-2021.

Do not silently replace the governed support set.

## 6. LTT implication

Recompute only the support arithmetic:
- total actual-DOWN SQRT alarms;
- bad suppressions under frozen Router-UP hard veto;
- exact one-sided binomial p-value for alpha=0.20.

No new suppression policy is selected in this study.

## 7. Forbidden actions

Do not:
- use 2025;
- retune any expert;
- retune SQRT;
- alter source-harmonization metrics after outcomes;
- call the external data governed same-source evidence;
- choose a new veto policy from 2020/2021 outcomes.

## 8. Governance

- no random split;
- no production writes;
- no runtime promotion.
