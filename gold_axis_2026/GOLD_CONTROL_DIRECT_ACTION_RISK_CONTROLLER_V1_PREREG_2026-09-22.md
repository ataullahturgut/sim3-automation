# GOLD CONTROL — DIRECT ACTION-RISK CONTROLLER V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `DIRECT_ACTION_RISK_CONTROLLER_V1_RESEARCH`  
**Frozen parent:** SQRT-HAR-DR  
**Frozen verifier:** `UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH`  
**Runtime authority:** NONE  
**Production DB writes:** FORBIDDEN

## 1. Objective

Address the two defects found in the controller audit:

1. cumulative Wilson-LCB is not a transport-stable absolute action score;
2. the controller should estimate BAD_SUPPRESSION risk directly rather than threshold a proxy.

The new controller therefore predicts:

`P(actual DOWN | Router V2 emits UP, current causal evidence)`

and maps that risk into RETAIN / WATCH / SUPPRESS.

Router V2 itself is unchanged.

## 2. Development and challenge split

- **2024:** controller development / parameter learning.
- **2025:** researcher-visible locked challenge.

No 2025 outcome, threshold or coefficient may alter the controller.

## 3. Router-UP development sample

Fit only on 2024 daily rows where frozen Router V2 emits UP.

Target:
- `bad = 1` if next-day actual direction is DOWN;
- `bad = 0` if next-day actual direction is UP.

The controller is learned on all Router-UP daily origins, not only SQRT alarm origins, to avoid fitting on the four-event 2024 alarm intersection.

## 4. Time-stable competence variants

For the direct expert selected by Router V2 at an origin, compute two causal competence estimates using only matured prior UP calls of that selected expert under the same legacy context when available; otherwise use the same frozen global fallback semantics.

### Variant F30 — fixed effective sample

Use the most recent **30** matured UP calls of the selected expert.

`fixed30_precision = true_UP / 30`

If fewer than 30 are available in the relevant history, use all available matured calls.

Rationale: 30 is the existing Router-V2 minimum support requirement and prevents confidence from rising merely because cumulative history grows indefinitely.

### Variant D30 — exponentially discounted Beta-Binomial

Use all matured prior UP-call outcomes of the selected expert, ordered from oldest to newest, with exponential event weights:

`w_lag = 2^(-lag/30)`

so the half-life is **30 prior UP calls**.

Use Beta(1,1) prior pseudo-counts.

`discounted_precision = (1 + weighted_true_UP) / (2 + weighted_total)`

Rationale: same effective timescale as F30, but with smooth forgetting rather than a hard window.

## 5. SQRT evidence feature

Use frozen parent:

`sqrt_normalized_risk_score`

available at the same origin.

No other SQRT variable is allowed in V1.

## 6. Two preregistered direct BAD-risk models

Fit two separate ridge-logistic regressions on 2024 Router-UP daily rows.

Target is `bad`.

### Model F30
Features:
1. `sqrt_normalized_risk_score`
2. `1 - fixed30_precision`

### Model D30
Features:
1. `sqrt_normalized_risk_score`
2. `1 - discounted_precision`

Learning:
- standardize each feature using 2024 training mean and population standard deviation;
- include intercept;
- L2 penalty `lambda = 1.0` on slopes only;
- Newton-Raphson optimization until max coefficient change < 1e-10 or 100 iterations.

No hyperparameter search is allowed.

## 7. Conservative model-uncertainty aggregation

For every Router-UP origin:

`p_bad = max(p_bad_F30, p_bad_D30)`

The maximum is used so suppression is allowed only if **both** parameter-learning formulations consider the action sufficiently safe.

This rule is frozen before 2025 scoring.

## 8. Three actions

On an SQRT alarm origin:

- Router V2 ABSTAIN -> `RETAIN_DOWN`
- Router V2 UP and `p_bad > 0.35` -> `RETAIN_DOWN`
- Router V2 UP and `0.20 < p_bad <= 0.35` -> `WATCH_DOWN`
- Router V2 UP and `p_bad <= 0.20` -> `SUPPRESS_DOWN`

The 0.20 boundary corresponds to the project's existing minimum 80% true-DOWN-retention safety concept. WATCH is a non-suppressing uncertainty region, not a deleted alarm.

## 9. 2025 locked evaluation

Report on 2025 SQRT alarms:

- RETAIN / WATCH / SUPPRESS counts;
- SUPPRESS good/bad anatomy;
- suppression precision;
- false-alarm reduction;
- true-DOWN retention;
- remaining forced-DOWN precision;
- WATCH actual-UP / actual-DOWN anatomy;
- net benefit.

Compare with frozen hard Router-V2 veto:
- 16 suppressions;
- 10 good / 6 bad;
- 62.50% suppression precision;
- 86.67% true-DOWN retention;
- 52.70% remaining forced-DOWN precision.

## 10. Decision rule

`SUPPORTED_AS_ACTION_RISK_SUCCESSOR` only if 2025 satisfies all:

1. SUPPRESS actions >= 3;
2. SUPPRESS precision > 62.50%;
3. true-DOWN retention >= 0.90;
4. remaining forced-DOWN precision >= 52.70%;
5. WATCH actions >= 3;
6. false-alarm reduction > 0.

If safety passes but SUPPRESS<3:
`TOO_CONSERVATIVE_INSUFFICIENT_SUPPRESS_SUPPORT`.

If true-DOWN retention <0.90:
`SUPPRESS_SAFETY_FAILED`.

If WATCH<3:
`MIDDLE_ACTION_NOT_ESTABLISHED`.

## 11. Forbidden actions

Do not:
- tune W=30 or half-life=30;
- tune lambda;
- add features after 2025 is read;
- change action thresholds;
- train on SQRT alarm subset only;
- alter Router V2;
- use 2025 for model selection;
- choose F30 or D30 after seeing 2025; the max-risk aggregation is binding.

## 12. Governance

- no random split;
- chronological/matured-only feature construction;
- 2025 locked from parameter selection;
- no production writes;
- no runtime promotion.
