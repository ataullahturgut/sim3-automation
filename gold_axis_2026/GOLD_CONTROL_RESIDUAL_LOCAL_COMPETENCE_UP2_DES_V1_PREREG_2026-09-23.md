# GOLD CONTROL — RESIDUAL LOCAL-COMPETENCE UP-2 DES V1 PREREGISTRATION

**Date:** 2026-09-23  
**Identity:** `RESIDUAL_LOCAL_COMPETENCE_UP2_DES_V1_RESEARCH`  
**Role:** second positive-UP specialist operating only after frozen UP Verifier V2 ABSTAIN  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Research question

Inside the exact residual route

`SQRT HIGH RISK + Frozen UP Verifier V2 ABSTAIN`

can dynamic/local expert selection recover missed-UP cases by selecting whichever frozen direct UP expert has demonstrated local competence in similar matured residual states?

The model is not a general direction forecaster and never emits DOWN.

Outputs:
- `UP2_DES`
- `ABSTAIN`

## 2. Candidate expert pool

Fixed pool:
1. TTSM_S2
2. TTSM_S1
3. BONATO_AR1_RM_QBOOST_H1
4. AR1_RM_LOGIT
5. RM_LOGIT

No new expert is added under this identity.

The primary frozen Router V2 remains unchanged. This second-stage DES is evaluated only after the primary Router has already ABSTAINed.

## 3. Route-consistent population

A row is eligible only if, at its own origin:
- frozen SQRT-HAR-DR = HIGH RISK;
- frozen UP Verifier V2 = ABSTAIN.

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

## 4. Local state representation

For nearest-neighbour competence estimation use these nine origin-safe context variables:

1. `sqrt_score`
2. `lag1_close_return`
3. `downside_share`
4. `intraday_end_norm`
5. `close_location`
6. `trough_recovery_norm`
7. `last_quarter_return_norm`
8. `direct_up_fraction`
9. `legacy_up_fraction`

Definitions are exactly those frozen in `RESIDUAL_ONE_SIDED_UP2_LOGIT_V1_RESEARCH`.

No target-day observation, CBR outcome, future return, or target-year label enters the state vector.

## 5. Source integrity

Use the exact same pinned route/data authorities as residual UP-2 V1:

- external daily spine commit `509c5ffa762f4ea49644b8ffe723ed2591ba52bf`;
- raw path mirror `kevingtlin/Market-Data-Lab@922f83a60cc574e7395fb27397077288055a1ef6`;
- frozen SQRT code commit `ad0fc4dcbe1687833bd9a153cd4bc6a754523464`;
- frozen primary Router/down-audit reconstruction base `7982b422476df61eb0339b74265afd553414f2d2`;
- route-consistent construction frozen by `b22235f04dc48b173a93a98cc2ce22081bb0054e`.

Raw/source-derived feature harmonization must satisfy the already frozen V1 gate:
- CBR-representable exact-date overlap >=300;
- each of the six source-derived feature Pearson correlations >=0.90;
- lag1 return sign agreement >=90%.

No model scoring if the gate fails.

## 6. Dynamic local competence rule

For each target-year residual case:

### 6.1 Historical library
Use only matured residual rows strictly before the target year.

Chronology:
- 2022: external residual 2020–2021;
- 2023: external + governed 2022 residual;
- 2024: external + governed 2022–2023 residual;
- locked 2025: external + governed 2022–2024 residual.

### 6.2 Standardization
Fit mean/std of the nine state variables on the target-year historical library only.

Replace std <1e-12 by 1.0.

### 6.3 Neighbourhood
- Euclidean distance in standardized nine-dimensional state space;
- fixed `K=25` nearest historical residual rows;
- no distance threshold;
- no target-year information.

K=25 is frozen before scoring as a support-first local window for the initial n=98 residual formation pool.

### 6.4 Expert competence
For each candidate expert that emits UP on the current case:

Within the K=25 local historical neighbours:
- `local_calls` = neighbours where that expert also emitted UP;
- `TP` = local_calls with realized UP;
- `FP` = local_calls with realized DOWN;
- `precision = TP / local_calls`;
- `local_actual_down` = all DOWN labels in the 25 neighbours;
- `FPR = FP / local_actual_down`;
- compute one-sided 90% Wilson lower confidence bound on precision.

Expert is locally eligible only if:
- local_calls >=5;
- precision >0.50;
- FPR <0.50;
- Wilson90 LCB precision >0.50.

No global fallback is allowed. If local support is insufficient, the expert is ineligible.

### 6.5 Selection
If at least one expert is locally eligible, select one by:
1. highest Wilson90 LCB;
2. lower local FPR;
3. higher local precision;
4. fixed expert order listed in section 2.

Emit `UP2_DES`.

Otherwise emit `ABSTAIN`.

## 7. Metrics

Per year and pooled 2022–2024:
- residual n;
- actual UP / DOWN;
- UP2_DES calls;
- true UP;
- false UP;
- precision;
- missed-UP recall;
- false-UP FPR;
- coverage;
- one-sided 90% Wilson LCB precision;
- selected-expert counts;
- mean local calls / precision / FPR / LCB of selected experts;
- neighbourhood source/year provenance.

Also produce exact row ledger.

## 8. Frozen pre-2025 gate

Supportive only if pooled 2022–2024:
1. exact n=26;
2. UP2_DES calls >=4;
3. precision >0.50;
4. one-sided 90% Wilson LCB precision >0.50;
5. false-UP FPR <=0.25.

This is intentionally the same acceptance gate used for Residual One-Sided UP-2 V1.

## 9. Locked 2025 descriptive transport

Supportive only if:
- calls >=5;
- precision > residual UP base rate 35/74 =47.2973%;
- false-UP FPR <0.50.

2025 cannot rescue a failed pre-2025 gate or change K, features, expert pool, or eligibility.

## 10. Comparative reporting

Report side-by-side with frozen Residual One-Sided UP-2 V1:
- pooled 2022–2024 precision / recall / FPR / coverage;
- locked 2025 precision / recall / FPR / coverage.

This is descriptive. No result-dependent hybrid, ensemble, arbitration or winner-selection rule is allowed under V1.

## 11. Final statuses

- `BLOCKED_SOURCE_OR_ROUTE_INTEGRITY`
- `RESIDUAL_LOCAL_DES_V1_NOT_SUPPORTED`
- `PRE2025_RESIDUAL_LOCAL_DES_SIGNAL_ONLY`
- `RESIDUAL_LOCAL_DES_SIGNAL_WITH_SUPPORTIVE_LOCKED2025_TRANSPORT`

## 12. Governance

- no random split;
- no hyperparameter/K sweep;
- no target-year tuning;
- no 2025 tuning;
- no 2026 use;
- no post-hoc expert deletion/addition;
- no automatic ensemble with UP-2 Logit V1;
- DB read-only;
- no production writes;
- no runtime promotion.
