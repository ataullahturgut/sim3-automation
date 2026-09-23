# GOLD CONTROL — RESIDUAL SEQUENCE-SHAPELET UP SPECIALIST V1 PREREGISTRATION

**Date:** 2026-09-23  
**Identity:** `RESIDUAL_SEQUENCE_SHAPELET_UP_V1_RESEARCH`  
**Role:** sequence-level alternative residual-UP specialist after Frozen Primary UP Verifier V2 ABSTAIN  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Motivation

Aggregate scalar and morphology patches have reached a clear limit:

- One-Sided UP-2 Logit V1 is the only supported second-stage UP method;
- Local-DES V1 is unsupported;
- pure trajectory-morphology V1 is unsupported;
- the scalar continuation-mimic veto based on final-hour trend R² is unsupported;
- missed-UP versus rejected-DOWN scalar/path-summary effects are not stable into locked 2025.

The next distinct hypothesis is that discriminative information may exist in **local subsequence shape** and be erased by aggregate summaries.

V1 therefore tests a low-capacity shapelet-style sequence representation.

## 2. Exact task and route

Population is the exact route:

`SQRT HIGH RISK + Frozen Primary UP Verifier V2 ABSTAIN`.

The model outputs:
- `UP_SHAPELET`
- `ABSTAIN`

It never emits DOWN.

This is an **alternative residual-UP specialist**, not an automatic ensemble with One-Sided UP-2 V1.

## 3. Chronological design

To prevent result-dependent shape selection:

### 2020 — discovery/training only
Corrected external residual population:
- expected n=72 =35 UP +37 DOWN.

Use 2020 labels to:
- generate shapelet candidates;
- select exactly one UP-associated shapelet and one DOWN-associated shapelet;
- fit the fixed 2-feature logistic classifier.

### 2021 — threshold calibration only
Corrected external residual population:
- expected n=26 =11 UP +15 DOWN.

The 2020-trained classifier is frozen before 2021 scoring.
Use only 2021 realized DOWN probabilities to calibrate the one-sided UP acceptance threshold.

No shapelet or model-weight refitting on 2021.

### 2022–2024 — governed pre-2025 evaluation
Exact governed residual population:
- 2022 n=11 =5 UP +6 DOWN;
- 2023 n=2 =1/1;
- 2024 n=13 =7 UP +6 DOWN;
- pooled n=26 =13 UP +13 DOWN.

No parameter or threshold changes.

### 2025 — locked descriptive transport
Exact residual n=74 =35 UP +39 DOWN.
No tuning or rescue.

2026 excluded.

## 4. Sequence representation

For each completed origin day:

1. retained 5-minute log-return path `r_t`;
2. require at least 239 returns;
3. compute full-day `RV=sum(r_t²)`, require RV>0;
4. cumulative path includes session-start zero:
   `C=[0,cumsum(r_t)] / sqrt(RV)`;
5. retain the final **96 five-minute returns** = approximately final 8 hours, represented by the final 97 cumulative-path points;
6. rebase this terminal sequence to start at zero.

Thus V1 focuses on late-session sequence structure suggested by the prior failure anatomy without using a single hand-engineered terminal statistic.

## 5. Shapelet candidate library

Candidates are generated **only from 2020 external residual training rows**.

Fixed point lengths:
- 13 points ≈1 hour;
- 25 points ≈2 hours;
- 49 points ≈4 hours.

For each training sequence and each length:
- candidate starts every 6 points;
- always include the last valid start;
- discard a candidate if its standard deviation <1e-8.

Each candidate is z-normalized.

No candidate from 2021, governed 2022–2025, or 2026 may enter the library.

## 6. Shapelet distance

For a candidate shapelet S of length L and a day's 97-point terminal sequence X:

- enumerate every contiguous L-point window in X;
- z-normalize each window independently;
- compute root-mean-square Euclidean distance to S;
- feature value is the minimum distance.

No DTW is used. This is deliberately different from the earlier CBR whole-path nearest-neighbor model.

## 7. Frozen shapelet selection

For each 2020 candidate, calculate its minimum distance to every 2020 training sequence.

Let Cliff's delta compare:
`distance(actual UP) - distance(actual DOWN)`.

Select exactly:

1. **UP-associated shapelet** = candidate with the most negative Cliff's delta, meaning UP cases tend to lie closer.
2. **DOWN-associated shapelet** = candidate with the most positive Cliff's delta, meaning DOWN cases tend to lie closer.

Deterministic tie-break:
1. larger absolute median distance difference;
2. shorter length;
3. earlier source target date;
4. earlier candidate start.

The two selected shapelets must be different candidates.

No information-gain / length / candidate-count sweep.

## 8. Frozen classifier

Features:
1. minimum distance to selected UP-associated shapelet;
2. minimum distance to selected DOWN-associated shapelet.

Classifier:
- L2 LogisticRegression;
- C=1.0;
- solver=lbfgs;
- class_weight=None;
- max_iter=5000.

Standardize using 2020 training mean/std only.

Target:
- actual UP=1;
- actual DOWN=0.

No other market-state feature enters V1.

## 9. 2021 one-sided calibration

Score every 2021 residual row using the frozen 2020 model.

Require at least 10 realized DOWN calibration rows.

Set:
`tau = max(0.50, nearest-rank q80 of 2021 realized-DOWN p(UP))`.

Thereafter the model and tau are frozen.

Decision:
- `UP_SHAPELET` iff `p_up > tau`;
- else `ABSTAIN`.

2021 is calibration only; its classification performance is reported descriptively but does not choose shapelets or model weights.

## 10. Source-transfer integrity

Selected shapelet distance features are recomputed on exact-date external versus governed paths over the representable 2020–2021 overlap.

Require:
- overlap >=300 dates;
- Pearson correlation >=0.90 for each selected distance feature;
- median absolute difference <=0.10 for each selected distance feature.

If source-transfer fails, governed interpretation is blocked.

## 11. Metrics

For 2021 calibration set, each governed year, pooled 2022–2024, and locked 2025 report:
- n;
- actual UP / DOWN;
- calls;
- true UP / false UP;
- precision;
- missed-UP recall;
- false-UP FPR;
- coverage;
- Wilson90 LCB precision;
- ROC AUC;
- Brier score.

Also report:
- selected shapelet source target date, length, start;
- training Cliff delta and median distance difference;
- logistic standardized coefficients;
- source-transfer diagnostics;
- row ledger.

## 12. Frozen pre-2025 gate

Supportive only if pooled governed 2022–2024:

1. exact n=26;
2. calls >=4;
3. precision >0.50;
4. Wilson90 LCB precision >0.50;
5. false-UP FPR <=0.25.

Same acceptance gate as the completed residual-UP specialists.

No requirement to beat One-Sided UP-2 V1 under this V1 identity; comparison is descriptive.

## 13. Locked 2025 transport

Supportive only if:
- calls >=5;
- precision >35/74 =47.2973%;
- false-UP FPR <0.50.

2025 cannot rescue a failed pre-2025 gate.

## 14. Statuses

- `BLOCKED_SOURCE_OR_ROUTE_INTEGRITY`
- `SHAPELET_UP_V1_NOT_SUPPORTED`
- `PRE2025_SHAPELET_UP_SIGNAL_ONLY`
- `SHAPELET_UP_SIGNAL_WITH_SUPPORTIVE_LOCKED2025_TRANSPORT`

## 15. Governance

- no random split;
- no 2025 tuning;
- no 2026 use;
- shapelets selected from 2020 external only;
- threshold calibrated from 2021 external only;
- no hyperparameter/length sweep beyond the frozen library;
- no automatic ensemble with One-Sided UP-2;
- DB read-only;
- no runtime or production promotion.
