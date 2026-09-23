# GOLD CONTROL — UP-2 CONTINUATION-MIMIC VETO V1 PREREGISTRATION

**Date:** 2026-09-23  
**Identity:** `UP2_CONTINUATION_MIMIC_VETO_V1_RESEARCH`  
**Role:** retrospective feasibility test for a narrow failure detector behind Frozen One-Sided UP-2 Logit V1  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Motivation and methodological status

The preceding failure-anatomy and mechanism-gap audits identified one stable path-dynamic candidate that distinguishes:
- `CAPTURED_UP` cases; and
- `FALSE_UP_ACTUAL_DOWN` continuation-mimic hard negatives.

The candidate is `last_hour_trend_r2`.

Because this feature was nominated after inspecting governed 2022–2024 and locked-2025 anatomy, this V1 is explicitly **retrospective mechanism-feasibility research**, not pristine confirmatory validation.

The purpose is only to determine whether the identified mechanism can plausibly improve the existing UP-2 signal without excessive loss of true UP calls.

## 2. Frozen architecture

```text
SQRT HIGH RISK
   |
Frozen Primary UP Verifier V2
   |
ABSTAIN
   |
Frozen One-Sided UP-2 Logit V1
   |
UP2
   |
Continuation-Mimic Veto V1
   /                  \
VETO                KEEP_UP2
```

The veto never creates an UP or DOWN direction signal. It only suppresses an existing UP-2 call.

## 3. Training population

Use the already frozen corrected external 2020–2021 route-consistent residual population:
- n=98;
- 46 actual UP;
- 52 actual DOWN;
- every row satisfies SQRT HIGH RISK + Primary UP Verifier V2 ABSTAIN.

The veto is trained on actual DOWN versus UP across this residual population, not on in-sample reconstructed UP-2 errors.

This preserves chronology: external 2020–2021 precedes governed 2022–2024.

## 4. Frozen feature

Exactly one predictor:

- `last_hour_trend_r2`

Definition is frozen by `DIRECTION_MECHANISM_GAP_AUDIT_V1_RESEARCH`:
- final 12 retained 5-minute returns;
- form local cumulative path including local start zero;
- OLS versus bar index;
- use coefficient of determination R²;
- R²=0 if terminal cumulative path has zero variance.

No other feature is used in V1.

## 5. Model

Target:
- `actual_down = 1`;
- `actual_up = 0`.

Model:
- logistic regression;
- L2 penalty;
- C=1.0;
- lbfgs;
- class_weight=None;
- max_iter=5000.

Standardization:
- training-set mean/std only;
- zero std ->1.0.

No hyperparameter sweep.

## 6. One-sided veto threshold

Threshold is calibrated strictly prequentially within external 2020–2021:

1. sort 98 residual rows chronologically;
2. from row 40 onward, fit the same one-feature logistic on prior rows only and score the next row;
3. collect these strictly prequential p(DOWN) scores;
4. retain scores belonging to realized UP rows, because vetoing these is the costly error;
5. require at least 20 realized-UP calibration scores;
6. compute nearest-rank q80 of historical UP p(DOWN) scores;
7. freeze: `tau_veto = max(0.50, q80_UP_prequential_pDOWN)`.

Final veto model:
- fit one-feature logistic on all external 2020–2021 residual rows;
- for a future frozen UP-2 call, emit VETO iff `p_down > tau_veto`.

No governed target-year information enters model or threshold.

## 7. Governed evaluation populations

### Retrospective feasibility population
Frozen governed UP-2 calls in 2022–2024:
- 11 calls;
- 8 true UP;
- 3 false-UP actual-DOWN.

Because `last_hour_trend_r2` was nominated using these outcomes, this population is **not independent confirmation**. It is only a feasibility check.

### Locked 2025 descriptive transport
Frozen governed 2025 UP-2 calls:
- 25 calls;
- 13 true UP;
- 12 false-UP actual-DOWN.

2025 does not tune model or threshold and cannot rescue a failed feasibility result. Because 2025 anatomy was already inspected, this is also descriptive rather than pristine confirmation.

2026 excluded.

## 8. Metrics

For 2022–2024 and locked 2025 separately report:
- original UP2 calls;
- original true UP / false UP;
- veto calls;
- false-UP cases successfully removed;
- true-UP cases incorrectly vetoed;
- false-UP reduction;
- true-UP retention;
- remaining UP2 calls;
- remaining precision;
- remaining false-UP count;
- veto p(DOWN) distributions by true/false UP2 outcome.

## 9. Frozen feasibility gate

V1 is `FEASIBILITY_SUPPORTED` on 2022–2024 only if all hold:

1. at least 1 of the 3 false-UP actual-DOWN calls is vetoed;
2. false-UP reduction >=33.33%;
3. true-UP retention >=75%;
4. remaining UP2 precision > frozen baseline 72.73%.

If the gate fails, no threshold/model relaxation under V1.

2025 cannot rescue failure.

## 10. Integrity

Require:
- external residual count 98 =46 UP +52 DOWN;
- exact frozen governed UP2 call counts 11 and 25;
- `last_hour_trend_r2` source transfer already passed in prior external/governed harmonization: Pearson 0.992823 and median absolute difference 0.009717 on n=345 overlap.

Recompute and report this transfer diagnostic again if possible.

## 11. Final statuses

- `BLOCKED_INTEGRITY`
- `VETO_V1_FEASIBILITY_NOT_SUPPORTED`
- `VETO_V1_FEASIBILITY_SUPPORTED`

## 12. Governance

- retrospective feasibility only;
- no random split;
- no 2025 tuning;
- no 2026 use;
- no feature/model sweep;
- no automatic cascade promotion;
- no production writes;
- no runtime authority.