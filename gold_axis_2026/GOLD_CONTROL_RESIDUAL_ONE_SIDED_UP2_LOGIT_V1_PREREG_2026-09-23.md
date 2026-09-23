# GOLD CONTROL — RESIDUAL ONE-SIDED UP-2 LOGIT V1 PREREGISTRATION

**Date:** 2026-09-23  
**Identity:** `RESIDUAL_ONE_SIDED_UP2_LOGIT_V1_RESEARCH`  
**Role:** second positive-UP specialist operating only after frozen UP Verifier V2 ABSTAIN  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Research question

Inside the exact residual route

`SQRT HIGH RISK + Frozen UP Verifier V2 ABSTAIN`

can a second, deliberately one-sided specialist recover a **small but high-confidence subset of missed UP cases** without producing excessive false-UP calls?

This model is not a general direction forecaster and is not a replacement for frozen UP Verifier V2.

Binding cascade under test:

```
SQRT HIGH RISK
      |
Frozen UP Verifier V2
   /             \
 UP              ABSTAIN
 |                  |
VERIFIED UP      UP-2 specialist
                /             \
              UP              ABSTAIN
              |                  |
      VERIFIED UP-2        downstream resolver
```

The UP-2 specialist is allowed only two outputs:
- `UP2`
- `ABSTAIN`

It never emits DOWN.

## 2. Methodological family

The design is a fixed **one-sided / Neyman-Pearson-style selective classifier**:

- base score model: L2 logistic regression;
- positive class: realized next-close UP;
- negative class: realized next-close DOWN;
- selection threshold is calibrated only from prior matured residual-history DOWN scores;
- threshold aims to constrain false-UP acceptance rather than maximize ordinary accuracy.

No model family sweep is allowed under this identity.

## 3. Route-consistent population

A row may be used for either training or testing only if it satisfies, at its own origin:

1. frozen SQRT-HAR-DR = HIGH RISK;
2. frozen UP Verifier V2 = ABSTAIN.

Rows already emitted as VERIFIED UP by the primary verifier are excluded from UP-2 training and evaluation.

Expected route-consistent counts:

External corrected history:
- 2020: 72 =37 DOWN +35 UP;
- 2021: 26 =15 DOWN +11 UP;
- pooled external: 98 =52 DOWN +46 UP.

Governed pre-2025 residual tests:
- 2022: 11 =6 DOWN +5 UP;
- 2023: 2 =1 DOWN +1 UP;
- 2024: 13 =6 DOWN +7 UP;
- pooled 2022–2024: 26 =13 DOWN +13 UP.

Locked 2025 transport:
- 74 =39 DOWN +35 UP.

Any mismatch blocks interpretation.

## 4. Frozen inputs

All features are origin-safe and available by the origin close.

### A. Risk state
1. `sqrt_score`  
   Frozen SQRT normalized risk score:
   `sqrt_forecast / yearly q80`.

### B. Daily / intraday state
2. `lag1_close_return`  
   Log close-to-close return from previous retained day to origin day.

3. `downside_share`  
   `sum(r_i^2 I(r_i<0)) / sum(r_i^2)`.

4. `intraday_end_norm`  
   `sum(r_i) / sqrt(RV)`.

5. `close_location`  
   Let `C_j = cumulative sum of intraday returns`.  
   `(C_end - min(C)) / (max(C)-min(C))`; if range is zero use 0.5.

6. `trough_recovery_norm`  
   `(C_end - min(C)) / sqrt(RV)`.

7. `last_quarter_return_norm`  
   Sum of returns in the final 25% of the retained origin-day path divided by `sqrt(RV)`.

### C. Expert-disagreement state
8. `direct_up_fraction`  
   Fraction of the five frozen direct UP experts currently voting UP:
   - TTSM-S2
   - TTSM-S1
   - Bonato AR1_RM QBoost h=1
   - AR1_RM_LOGIT
   - RM_LOGIT

9. `legacy_up_fraction`  
   `legacy_up_count / 3` from:
   - FAST_UP
   - SLOW_UP
   - MONTHLY_UP

No target-day feature, future return, CBR output, or 2025 outcome enters the feature vector.

## 5. Source construction

### External 2020–2021
Corrected external daily spine:
`gold_axis_2026/external_data/v2/dukascopy_xauusd_govsession_mid_5m_daily_features_2018_2021.csv`
at commit `509c5ffa762f4ea49644b8ffe723ed2591ba52bf`.

Raw path reconstruction:
`kevingtlin/Market-Data-Lab@922f83a60cc574e7395fb27397077288055a1ef6`.

Use the already frozen exact source/session construction:
- bid/ask timestamp inner join;
- mid close;
- UTC 5-minute last-close bars;
- America/New_York;
- weekdays;
- remove 17:00–17:55 maintenance;
- no raw third-party files committed.

### Governed 2022–2025
Read-only:
`public.xau_intraday_research_cache_5m`.

No production writes.

## 6. Mandatory integrity before scoring

Reproduce exactly:
- external 2020 SQRT alarms 212 =97 DOWN +115 UP;
- external 2021 SQRT alarms 28 =16 DOWN +12 UP;
- external Router-UP overlap 2020 =140, leaving 72 residual;
- external Router-UP overlap 2021 =2, leaving 26 residual;
- governed unresolved 2022/2023/2024 =11/2/13;
- locked 2025 unresolved =74.

External path source must again reproduce the corrected daily spine and pass the previously frozen path-harmonization gate.

For the nine UP-2 features, exact-date external-vs-governed overlap diagnostics must be reported on CBR-representable common dates. No feature-specific target threshold is tuned from those diagnostics; they are source-integrity evidence only.

## 7. Fixed score model

For each target year Y:

Training pool:
- all matured route-consistent residual rows strictly before year Y.

Standardization:
- feature-wise mean and standard deviation computed only on Y training rows;
- zero/near-zero standard deviations replaced by 1.0;
- no target-year standardization information.

Model:
- `sklearn.linear_model.LogisticRegression`;
- penalty = L2;
- C = 1.0;
- solver = lbfgs;
- class_weight = None;
- max_iter = 5000;
- random_state irrelevant / no stochastic split.

No hyperparameter search.

## 8. One-sided chronological threshold calibration

Ordinary 0.50 classification is NOT used.

Within each Y training pool:

1. sort rows chronologically by target date;
2. beginning only after at least **40 prior residual cases**, fit the same fixed logistic model on prior rows and predict the next matured row;
3. collect these strictly prequential training-history probabilities;
4. take only calibration scores whose realized label was DOWN;
5. require at least **20** matured DOWN calibration scores;
6. compute the nearest-rank 80th percentile of those DOWN scores;
7. freeze:
   `tau_Y = max(0.50, q80_down_prequential)`.

Target-year decision:
- emit `UP2` iff `p_up > tau_Y`;
- otherwise `ABSTAIN`.

The intent is approximately 20% historical false-UP acceptance among DOWN calibration cases, while retaining a positive-probability floor of 0.50.

No target-year threshold tuning.

## 9. Chronology

- 2022: train external residual 2020–2021 only;
- 2023: train external + governed residual 2022;
- 2024: train external + governed residual 2022–2023;
- locked 2025: train external + governed residual 2022–2024.

No random split.

2025 is locked transport only and cannot select features, threshold rule, or model settings.

2026 excluded.

## 10. Metrics

Per year and pooled 2022–2024:
- n residual;
- actual UP / DOWN;
- UP2 calls;
- true UP;
- false UP;
- UP2 precision;
- missed-UP recall;
- false-UP FPR;
- coverage;
- one-sided 90% Wilson LCB precision;
- ROC AUC of p_up;
- Brier score;
- frozen tau;
- train n;
- prequential calibration n / DOWN n.

Also report:
- feature coefficients after standardization;
- annual route/source composition;
- row-level ledger.

## 11. Frozen pre-2025 gate

`PRE2025_RESIDUAL_UP2_SIGNAL` only if pooled 2022–2024:

1. exact n = 26;
2. UP2 calls >= 4;
3. raw UP precision > 0.50;
4. one-sided 90% Wilson LCB UP precision > 0.50;
5. false-UP FPR <= 0.25.

If this gate fails, 2025 cannot rescue V1.

## 12. Locked 2025 descriptive transport

Report unchanged V1 on the exact 74 locked residual rows.

Descriptive transport is marked supportive only if:
- UP2 calls >=5;
- UP precision > locked residual UP base rate `35/74 = 47.2973%`;
- false-UP FPR <0.50.

This does not override a failed pre-2025 gate.

## 13. Final statuses

- `BLOCKED_SOURCE_OR_ROUTE_INTEGRITY`
- `BLOCKED_CALIBRATION_SUPPORT`
- `RESIDUAL_UP2_V1_NOT_SUPPORTED`
- `PRE2025_RESIDUAL_UP2_SIGNAL_ONLY`
- `RESIDUAL_UP2_SIGNAL_WITH_SUPPORTIVE_LOCKED2025_TRANSPORT`

## 14. Governance

- primary UP Verifier V2 remains frozen;
- no automatic ensemble;
- UP2 does not override primary VERIFIED UP;
- UP2 emits no DOWN;
- no random split;
- no 2025 tuning;
- no 2026 use;
- no post-hoc feature deletion/addition under this identity;
- no production writes;
- no runtime promotion.
