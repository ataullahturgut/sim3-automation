# GOLD CONTROL — NP-CONSTRAINED SUPPRESSOR V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `NP_CONSTRAINED_SUPPRESSOR_V1_RESEARCH`  
**Frozen parent risk model:** SQRT-HAR-DR annual-origin downside-risk alarm  
**Frozen verifier:** `UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH`  
**Runtime authority:** NONE  
**Production DB writes:** FORBIDDEN

## 1. Objective

Test a Neyman-Pearson-style suppression controller whose primary safety constraint is:

> suppress as many false forced-DOWN SQRT alarms as possible while constraining the probability of suppressing a true DOWN.

This study does not retrain SQRT and does not modify Router V2.

## 2. Frozen suppression score

For every daily origin on which frozen Router V2 emits `UP`, define:

`suppression_score = selected expert's one-sided 90% Wilson lower confidence bound on historical UP precision`.

If Router V2 emits `ABSTAIN`, set the suppression score to negative infinity and suppression is impossible.

No SQRT outcome, 2025 outcome, or SQRT-alarm-subset performance enters the score.

## 3. NP safety target

Prioritized error:

`BAD_SUPPRESSION = SUPPRESS_DOWN when actual next-day direction is DOWN`.

Target upper bound:

`alpha = 0.20`.

Confidence level:

`1 - delta = 0.90`, so `delta = 0.10`.

These values are frozen because prior Gold Control governance already requires at least 80% true-DOWN retention and Router V2 competence already uses 90% Wilson lower bounds.

## 4. Calibration period

**2024 daily common panel** is calibration for this downstream controller.

Calibration uses all exact same-clock daily rows in 2024, not only SQRT alarms.

Only actual-DOWN calibration rows are used to select the NP threshold.

Let:
- n0 = number of 2024 actual-DOWN daily rows;
- scores on these n0 rows be sorted ascending as S_(1) <= ... <= S_(n0).

Choose the smallest order-statistic index k such that:

`P[Binomial(n0, 1-alpha) >= k] <= delta`.

The NP threshold is `tau = S_(k)`.

Operational suppression rule:

`SUPPRESS_DOWN` iff:
1. SQRT raises an alarm;
2. Router V2 emits UP;
3. suppression_score > tau.

Strict `>` is used to handle score ties conservatively.

Otherwise the action is `RETAIN_DOWN`.

If no such k exists, the study is `BLOCKED_INSUFFICIENT_CALIBRATION_SUPPORT`.

## 5. Evaluation

### Calibration diagnostics — 2024
Report:
- n0;
- k;
- tau;
- number of daily 2024 true-DOWN rows above tau;
- number of 2024 daily UP rows above tau;
- SQRT-alarm intersection anatomy after applying the calibrated threshold.

These are calibration diagnostics only, not an independent validation claim.

### Researcher-visible locked challenge — 2025
Apply the frozen 2024 threshold unchanged to 2025.

Report on 2025 SQRT alarm origins:
- baseline TP / FP;
- suppressions;
- good suppressions;
- bad suppressions;
- suppression precision;
- false-alarm reduction;
- true-DOWN retention;
- remaining forced-DOWN precision;
- precision change versus baseline;
- net suppression benefit.

2025 is not fresh blind evidence because it is researcher-visible historically, but no 2025 value may alter tau or any rule.

## 6. Benchmarks

Compare against:
1. no suppressor;
2. frozen hard Router-V2 veto from `SQRT_UP_ROUTER_V2_COUNTERSIGN_VETO_V1_RESEARCH`.

No new benchmark threshold is tuned.

## 7. Decision rule

The NP controller is `SUPPORTED_AS_SAFER_SUCCESSOR` only if 2025 simultaneously satisfies:

1. at least 3 suppressions;
2. true-DOWN retention >= 0.80;
3. remaining forced-DOWN precision >= hard-veto remaining precision;
4. suppression precision >= hard-veto veto precision;
5. false-alarm reduction > 0.

If fewer than 3 suppressions occur but the safety constraint holds, classify `TOO_CONSERVATIVE / INSUFFICIENT_ACTION_SUPPORT`.

If true-DOWN retention < 0.80, classify `SAFETY_CONSTRAINT_FAILED`.

## 8. Forbidden actions

Do not:
- tune alpha;
- tune delta;
- change Router V2;
- change the suppression score;
- use SQRT alarm outcomes to choose tau;
- use 2025 to change tau;
- add FAST/SLOW/GVZ/Macro/Event logic after seeing results;
- convert this study into a three-action controller; that belongs to a separate identity.

## 9. Governance

- no random split;
- chronological matured-only Router V2 competence;
- no production writes;
- no runtime promotion.
