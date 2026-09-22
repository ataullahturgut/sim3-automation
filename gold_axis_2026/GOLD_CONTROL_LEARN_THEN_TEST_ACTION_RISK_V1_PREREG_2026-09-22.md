# GOLD CONTROL — LEARN-THEN-TEST ACTION-RISK V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `LEARN_THEN_TEST_ACTION_RISK_V1_RESEARCH`  
**Frozen parent:** SQRT-HAR-DR  
**Frozen verifier:** `UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH`  
**Runtime authority:** NONE  
**Production DB writes:** FORBIDDEN

## 1. Objective

Test whether a Learn-Then-Test style risk-control layer can certify a suppression policy without fitting a new parametric BAD_SUPPRESSION probability surface.

The operational safety target remains the project-native quantity:

`BAD_SUPPRESSION_RATE = P(SUPPRESS_DOWN | actual DOWN AND SQRT alarm)`.

Equivalently, true-DOWN retention must be at least 80%.

## 2. Risk-control target

- target bad-suppression rate: `alpha = 0.20`
- confidence: `1-delta = 0.90`
- therefore `delta = 0.10`

No weaker alpha or confidence level may be substituted after seeing support.

## 3. Calibration population

The calibration population is restricted to **2024 SQRT alarm origins whose next-day outcome is actual DOWN**.

This is deliberate: unlike NP Suppressor V1, the LTT safety claim is conditioned on the exact operational stratum that matters.

Let `n_down_alarm` be the number of such calibration cases.

## 4. Mandatory support gate before policy scoring

Before evaluating any candidate suppression rule, verify whether the calibration sample is large enough to certify alpha=0.20 at delta=0.10 even under the best possible empirical outcome of zero bad suppressions.

For zero observed bad suppressions, the exact one-sided binomial condition is:

`(1-alpha)^n <= delta`.

Thus minimum required support is:

`n_min = ceil(log(delta)/log(1-alpha))`.

With alpha=0.20 and delta=0.10, this quantity must be computed and reported.

If `n_down_alarm < n_min`, stop immediately with:

`BLOCKED_INSUFFICIENT_ALARM_CONDITIONAL_CALIBRATION_SUPPORT`

and do **not** score candidate policies or read 2025 challenge outcomes for this study.

## 5. Candidate policy family — only if support gate passes

If and only if support is sufficient, evaluate the following predeclared finite family on the 2024 calibration stratum:

- P0: frozen hard Router-V2 UP veto
- P1: Router-V2 UP and `min(F30,D30) >= 0.60`
- P2: Router-V2 UP and `min(F30,D30) >= 0.65`
- P3: Router-V2 UP and `min(F30,D30) >= 0.70`
- P4: Router-V2 UP and `min(F30,D30) >= 0.75`

F30 and D30 are the already-frozen time-stable competence constructions from Direct Action-Risk Controller V1.

No SQRT-alarm outcome enters these competence measures.

## 6. LTT testing rule — only if support gate passes

For each candidate policy, let x be the number of calibration actual-DOWN SQRT alarms that the policy suppresses.

Use the exact one-sided binomial test of:

`H0: bad-suppression rate > alpha`.

Control familywise error across the five candidates by Bonferroni:

`delta_policy = 0.10 / 5 = 0.02`.

A policy is risk-certified only if its exact upper confidence bound / p-value rejects H0 at delta_policy.

Among risk-certified policies, choose the policy with the largest number of good suppressions on 2024 SQRT false-DOWN alarms; tie-break by fewer total suppressions, then higher competence threshold.

## 7. 2025 challenge — only after a 2024-certified policy exists

If no policy is certified, 2025 is not scored under this identity.

If a policy is certified, freeze it and apply unchanged to 2025.

Report:
- suppressions;
- good / bad suppressions;
- suppression precision;
- false-alarm reduction;
- true-DOWN retention;
- remaining forced-DOWN precision.

2025 may not alter the certified policy.

## 8. Forbidden actions

Do not:
- relax alpha;
- relax delta;
- replace alarm-conditional risk with all-daily risk;
- use 2025 to rescue insufficient 2024 support;
- add or remove policy thresholds after calibration;
- fit a new classifier;
- alter Router V2;
- convert a blocked support result into a retrospective policy comparison.

## 9. Governance

- no random split;
- exact alarm-conditional safety target;
- no 2025 tuning;
- no production writes;
- no runtime promotion.
