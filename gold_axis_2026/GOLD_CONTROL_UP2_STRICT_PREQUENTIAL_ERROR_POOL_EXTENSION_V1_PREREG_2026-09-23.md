# GOLD CONTROL — UP-2 STRICTLY PREQUENTIAL ERROR-POOL EXTENSION V1 PREREGISTRATION

**Date:** 2026-09-23  
**Identity:** `UP2_STRICT_PREQUENTIAL_ERROR_POOL_EXTENSION_V1_RESEARCH`  
**Purpose:** enlarge the historical UP-2 error/anatomy pool without target-year leakage before fitting any continuation-mimic veto  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Motivation

The current mechanism-gap audit identified `last_hour_trend_r2` as a stable candidate discriminator between:
- true UP-2 rebound calls; and
- false-UP actual-DOWN continuation-mimic calls.

However the governed pre-2025 UP-2 call sample is only 11 cases (8 true UP, 3 false UP).

Before fitting a veto, this study attempts to recover additional **strictly prequential historical UP-2 decisions** from the corrected external 2020–2021 route-consistent residual history.

This study does not change or retune UP-2.

## 2. Frozen source and route

Use the exact residual population already frozen for UP-2 formation:

- corrected external Dukascopy route-consistent residual rows 2020–2021;
- total 98 =46 UP +52 DOWN;
- every row must satisfy:
  - SQRT HIGH RISK;
  - Frozen Primary UP Verifier V2 ABSTAIN.

Pinned authorities are unchanged from One-Sided UP-2 V1.

## 3. Frozen UP-2 model

Use exactly the One-Sided UP-2 V1 model:
- same 9 features;
- L2 logistic regression;
- C=1.0;
- lbfgs;
- same standardization logic;
- no hyperparameter search.

## 4. Strict nested prequential decision construction

For external residual row `i`, sorted chronologically:

1. Require at least 40 matured residual rows before `i`.
2. Build a calibration ledger using only rows before `i`:
   - for every earlier row `j >= 40`, fit the frozen model on rows strictly before `j`;
   - score row `j`;
   - collect only these strictly prequential historical scores.
3. Among calibration rows realized DOWN, require at least 20 scores.
4. Set:
   `tau_i = max(0.50, nearest-rank q80 of prior strictly-prequential DOWN scores)`.
5. Fit the frozen model on all residual rows strictly before `i`.
6. Score row `i`.
7. Emit historical `UP2_CALL` iff `p_up_i > tau_i`; otherwise `ABSTAIN`.

Thus no external row may use its own label or any future external row to form its model or threshold.

Rows before sufficient calibration support are marked `NOT_SCORABLE_PREQUENTIAL_SUPPORT`, not forced.

## 5. Error-cell labels

For scorable historical rows:
- `CAPTURED_UP`
- `MISSED_UP`
- `FALSE_UP_ACTUAL_DOWN`
- `REJECTED_DOWN`

The study reports exact counts and dates.

## 6. Mechanism features

For each scorable row compute the 18 path-dynamic features frozen in:
`DIRECTION_MECHANISM_GAP_AUDIT_V1_RESEARCH`.

Primary continuation-mimic candidate:
- `last_hour_trend_r2`.

Secondary context candidate:
- `late_downside_intensity`.

No feature is added or removed after scoring.

## 7. External-to-governed feature integrity

On exact-date 2020–2021 external/governed overlap where both paths are representable, report:
- n overlap;
- Pearson and median absolute difference for all 18 mechanism features.

Minimum transfer gate for the two promoted mechanism candidates:
- overlap >=300;
- `late_downside_intensity` Pearson >=0.90;
- `last_hour_trend_r2` Pearson >=0.80;
- median absolute difference of `last_hour_trend_r2` <=0.15.

If the promoted feature gate fails, the historical pool may still be reported but cannot be used to justify a veto.

## 8. Outputs

Report:
- number of scorable external rows;
- first/last scorable dates;
- call/abstain counts;
- four error-cell counts;
- precision, recall, false-UP FPR, coverage of the historical prequential UP2 calls;
- `last_hour_trend_r2` group medians and Cliff's delta for captured-UP vs false-UP actual-DOWN;
- `late_downside_intensity` group medians and Cliff's delta for captured-UP vs missed-UP;
- row-level ledger.

## 9. Decision use

This is a **sample-generation / mechanism-support study**, not a model-selection test.

A future continuation-mimic veto may be preregistered only if:
- at least 5 historical UP2 calls are recovered; and
- at least 2 false-UP actual-DOWN hard negatives are recovered; and
- the promoted external/governed feature transfer gate passes.

No threshold for the future veto is chosen in this study.

## 10. Governance

- no random split;
- no target/future leakage;
- no 2025 use;
- no 2026 use;
- no modification of frozen UP-2;
- no veto fitting under this identity;
- no production writes;
- no runtime promotion.
