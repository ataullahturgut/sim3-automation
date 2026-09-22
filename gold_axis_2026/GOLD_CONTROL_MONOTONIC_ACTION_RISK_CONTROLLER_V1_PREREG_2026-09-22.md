# GOLD CONTROL — MONOTONIC ACTION-RISK CONTROLLER V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `MONOTONIC_ACTION_RISK_CONTROLLER_V1_RESEARCH`  
**Frozen parent:** SQRT-HAR-DR  
**Frozen verifier:** `UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH`  
**Runtime authority:** NONE  
**Production DB writes:** FORBIDDEN

## 1. Objective

Test whether the direct BAD_SUPPRESSION controller improves when its learned risk surface is forced to obey safety-coherent monotonicity.

Target:
`bad = 1` iff next-day actual direction is DOWN on a Router-V2 UP origin.

The controller does not modify SQRT or Router V2.

## 2. Development / challenge split

- **2024:** development and coefficient fitting only.
- **2025:** researcher-visible locked challenge only.

No 2025 outcome may alter features, constraints, thresholds, regularization or action rules.

## 3. Frozen competence variants

Reuse the exact two causal competence constructions from Direct Action-Risk Controller V1.

### F30
Most recent 30 matured UP calls of the selected Router-V2 expert, using the same legacy-bucket history when available and the same global fallback semantics.

`fixed30_precision = true_UP / available_calls`

with at most 30 calls.

### D30
Exponentially discounted Beta-Binomial competence over matured prior UP calls of the selected expert.

Event half-life = **30 prior UP calls**:

`w_lag = 2^(-lag/30)`

Beta(1,1) prior.

`discounted_precision = (1 + weighted_true_UP)/(2 + weighted_total)`.

No window or half-life tuning is allowed.

## 4. Features

Fit two separate BAD_SUPPRESSION ridge-logistic models on 2024 daily Router-UP origins.

### Model MF30
1. `sqrt_normalized_risk_score`
2. `1 - fixed30_precision`

### Model MD30
1. `sqrt_normalized_risk_score`
2. `1 - discounted_precision`

Each feature is standardized using 2024 training mean and population standard deviation.

Intercept is free.

L2 penalty:
- lambda = **1.0** on slopes only.

## 5. Monotonicity constraints

For both models:

- coefficient on standardized SQRT risk must satisfy `beta_sqrt >= 0`;
- coefficient on competence error must satisfy `beta_error >= 0`.

Interpretation:
- stronger SQRT downside-risk evidence may not reduce BAD_SUPPRESSION probability;
- worse UP-expert competence may not reduce BAD_SUPPRESSION probability.

The constrained ridge-logistic optimum is obtained by exact active-set comparison across:
1. both slopes free subject to nonnegativity;
2. SQRT slope fixed at 0;
3. competence-error slope fixed at 0;
4. both slopes fixed at 0.

For each active set, optimize the remaining free coefficients to convergence; discard infeasible solutions with a negative constrained slope; choose the feasible candidate with minimum penalized negative log-likelihood.

No post-result sign flipping is allowed.

## 6. Conservative model aggregation

For each Router-UP origin:

`p_bad = max(p_bad_MF30, p_bad_MD30)`.

Both formulations must consider a suppression sufficiently safe.

## 7. Frozen action rule

On an SQRT alarm origin:

- Router V2 ABSTAIN -> `RETAIN_DOWN`
- Router V2 UP and `p_bad > 0.35` -> `RETAIN_DOWN`
- Router V2 UP and `0.20 < p_bad <= 0.35` -> `WATCH_DOWN`
- Router V2 UP and `p_bad <= 0.20` -> `SUPPRESS_DOWN`

These thresholds are unchanged from Direct Action-Risk Controller V1.

WATCH is not suppression.

## 8. Locked 2025 metrics

Report:
- RETAIN / WATCH / SUPPRESS counts;
- actual UP / DOWN anatomy in each action;
- SUPPRESS precision;
- false-alarm reduction;
- true-DOWN retention;
- remaining forced-DOWN precision;
- net suppression benefit.

Benchmark against:
- frozen hard Router-V2 veto;
- unconstrained Direct Action-Risk Controller V1.

## 9. Decision rule

`SUPPORTED_AS_MONOTONIC_SUCCESSOR` only if 2025 satisfies all:

1. SUPPRESS actions >= 3;
2. SUPPRESS precision > **62.50%**;
3. true-DOWN retention >= **90%**;
4. remaining forced-DOWN precision >= **52.70%**;
5. WATCH actions >= 3;
6. false-alarm reduction > 0.

If SUPPRESS <3 while retention >=90%:
`TOO_CONSERVATIVE_INSUFFICIENT_SUPPRESS_SUPPORT`.

If retention <90%:
`SUPPRESS_SAFETY_FAILED`.

If WATCH <3:
`MIDDLE_ACTION_NOT_ESTABLISHED`.

## 10. Forbidden actions

Do not:
- change F30 or D30;
- tune lambda;
- change action thresholds;
- add features after 2025 is read;
- fit on SQRT alarm subset only;
- alter Router V2;
- use 2025 for model selection;
- choose one of MF30/MD30 after seeing 2025; max-risk aggregation is binding.

## 11. Governance

- no random split;
- matured-only competence;
- 2025 locked from parameter learning;
- no production writes;
- no runtime promotion.
