# GOLD CONTROL — RESIDUAL TRAJECTORY / REBOUND MORPHOLOGY UP-2 V1 PREREGISTRATION

**Date:** 2026-09-23  
**Identity:** `RESIDUAL_TRAJECTORY_REBOUND_UP2_V1_RESEARCH`  
**Role:** second-stage positive-UP specialist operating only after frozen UP Verifier V2 ABSTAIN  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Research question

Inside the exact residual route

`SQRT HIGH RISK + Frozen UP Verifier V2 ABSTAIN`

can the **origin-day intraday trajectory shape itself** identify a selective subset of missed UP cases?

This experiment is intentionally different from the prior two residual-UP studies:

- it does **not** recycle direct-expert votes as its primary decision mechanism;
- it does **not** use local dynamic expert selection;
- it uses only the geometry/morphology of the completed origin-day intraday return path.

The model outputs only:
- `UP2_MORPH`
- `ABSTAIN`

It never emits DOWN.

## 2. Route-consistent population

A row is eligible only if, at its own origin:

1. frozen SQRT-HAR-DR = HIGH RISK;
2. frozen UP Verifier V2 = ABSTAIN.

Expected exact counts:

External corrected history:
- 2020: 72 =37 DOWN +35 UP;
- 2021: 26 =15 DOWN +11 UP;
- pooled external: 98 =52 DOWN +46 UP.

Governed pre-2025 tests:
- 2022: 11 =6 DOWN +5 UP;
- 2023: 2 =1 DOWN +1 UP;
- 2024: 13 =6 DOWN +7 UP;
- pooled 2022–2024: 26 =13 DOWN +13 UP.

Locked 2025:
- 74 =39 DOWN +35 UP.

Any mismatch blocks interpretation.

## 3. Frozen morphology feature set

All features are computed from the completed origin-day 5-minute return path only.

Let:
- `r_t` be retained intraday log returns;
- `C_t = cumulative sum(r_t)`;
- `RV = sum(r_t^2)`;
- `scale = sqrt(RV)`;
- `t*=argmin(C_t)` be the trough index;
- `peak_before_t* = max(C_0,...,C_t*)`;
- `drawdown = peak_before_t* - C_t*`.

The fixed feature vector is:

1. **downside_share**  
   `sum(r_t^2 I(r_t<0)) / RV`

2. **max_drawdown_norm**  
   `drawdown / scale`

3. **trough_position**  
   `t* / (N-1)`

4. **recovery_to_close_ratio**  
   `(C_end - C_t*) / max(drawdown, 1e-8)`

5. **close_location**  
   `(C_end - min(C)) / max(max(C)-min(C), 1e-8)`

6. **post_trough_return_norm**  
   `(C_end - C_t*) / scale`

7. **last_quarter_return_norm**  
   sum of the final 25% of retained intraday returns divided by `scale`

8. **post_trough_positive_fraction**  
   fraction of post-trough returns strictly >0; if no post-trough return exists, use 0.5.

No SQRT score, legacy context, direct expert vote, CBR output, target-day feature, macro value, or future return enters the morphology vector.

## 4. Fixed classifier

Base model:
- `sklearn.linear_model.LogisticRegression`
- L2 penalty
- C=1.0
- lbfgs
- class_weight=None
- max_iter=5000

Reason for using a low-capacity classifier:
the sample is small, and this experiment is intended to test whether the frozen trajectory morphology contains recoverable signal rather than optimize a large model.

No model-family or hyperparameter sweep is allowed.

## 5. One-sided threshold calibration

Ordinary 0.50 classification is not the acceptance rule.

For each target year Y:

1. use only matured route-consistent residual rows strictly before Y;
2. sort the training pool chronologically;
3. beginning only after at least 40 prior residual cases, fit the fixed logistic model on prior rows and score the next matured row;
4. collect strictly prequential historical probabilities;
5. retain the scores belonging to realized DOWN rows;
6. require at least 20 DOWN calibration scores;
7. calculate nearest-rank q80 of those DOWN scores;
8. freeze `tau_Y = max(0.50, q80_down_prequential)`.

Decision on year Y:
- emit `UP2_MORPH` iff `p_up > tau_Y`;
- otherwise `ABSTAIN`.

No target-year threshold tuning.

## 6. Chronology

- 2022: train external residual 2020–2021 only;
- 2023: train external + governed residual 2022;
- 2024: train external + governed residual 2022–2023;
- locked 2025: train external + governed residual 2022–2024.

No random split.

2025 is locked transport only and cannot select features, model settings, threshold rule, or acceptance gate.

2026 excluded.

## 7. Source authorities

Use the exact same pinned source and route authorities as the already completed residual-UP studies:

- corrected external daily spine commit `509c5ffa762f4ea49644b8ffe723ed2591ba52bf`;
- transient raw path mirror `kevingtlin/Market-Data-Lab@922f83a60cc574e7395fb27397077288055a1ef6`;
- frozen SQRT code commit `ad0fc4dcbe1687833bd9a153cd4bc6a754523464`;
- frozen Router/down-audit reconstruction base `7982b422476df61eb0339b74265afd553414f2d2`;
- route-consistent construction frozen by `b22235f04dc48b173a93a98cc2ce22081bb0054e`.

Governed intraday source is read-only `public.xau_intraday_research_cache_5m`.

## 8. Mandatory source-integrity gate

Before scoring, compute all eight morphology features on the exact-date external-vs-governed CBR-representable overlap.

Require:
- overlap >=300 dates;
- Pearson correlation >=0.90 for each continuous morphology feature except `post_trough_positive_fraction`;
- Pearson correlation >=0.85 for `post_trough_positive_fraction`;
- trough-position absolute difference median <=0.05 of the session;
- no non-finite features.

These thresholds are frozen before scoring.

The already frozen external daily reconstruction and exact SQRT/Router route counts must also reproduce.

## 9. Metrics

Per year and pooled 2022–2024:
- residual n;
- actual UP / DOWN;
- UP2_MORPH calls;
- true UP;
- false UP;
- precision;
- missed-UP recall;
- false-UP FPR;
- coverage;
- one-sided 90% Wilson LCB precision;
- ROC AUC;
- Brier score;
- tau;
- training n;
- prequential calibration n / DOWN n;
- standardized coefficients.

Also report:
- exact row ledger;
- descriptive comparison against frozen One-Sided UP-2 Logit V1 and frozen Local-DES V1.

No result-dependent hybrid is permitted.

## 10. Frozen pre-2025 gate

Supportive only if pooled 2022–2024:

1. exact n=26;
2. UP2_MORPH calls >=4;
3. precision >0.50;
4. one-sided 90% Wilson LCB precision >0.50;
5. false-UP FPR <=0.25.

This is intentionally the same acceptance gate used for the prior residual-UP specialists.

## 11. Locked 2025 descriptive transport

Supportive only if:
- calls >=5;
- precision > residual UP base rate `35/74 = 47.2973%`;
- false-UP FPR <0.50.

2025 cannot rescue a failed pre-2025 gate.

## 12. Final statuses

- `BLOCKED_SOURCE_OR_ROUTE_INTEGRITY`
- `BLOCKED_CALIBRATION_SUPPORT`
- `RESIDUAL_TRAJECTORY_UP2_V1_NOT_SUPPORTED`
- `PRE2025_RESIDUAL_TRAJECTORY_UP2_SIGNAL_ONLY`
- `RESIDUAL_TRAJECTORY_UP2_SIGNAL_WITH_SUPPORTIVE_LOCKED2025_TRANSPORT`

## 13. Governance

- no random split;
- no feature sweep;
- no threshold sweep;
- no target-year tuning;
- no 2025 tuning;
- no 2026 use;
- no automatic ensemble with previous UP-2 models;
- no production writes;
- no runtime promotion.
