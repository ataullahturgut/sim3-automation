# GOLD CONTROL — DIRECT ACTION-RISK CONTROLLER V1 RESULT

**Date:** 2026-09-22  
**Identity:** `DIRECT_ACTION_RISK_CONTROLLER_V1_RESEARCH`  
**Preregistration:** `d5529a3364176de16b61fd79b99ec91b04c8f469`  
**Final status:** `NOT_SUPPORTED_AS_ACTION_RISK_SUCCESSOR`  
**Runtime authority:** NONE

## 1. What was changed

Frozen Router V2 was not modified.

The controller replaced cumulative absolute Wilson thresholds with two time-stable competence constructions:

- **F30:** most recent 30 selected-expert UP calls;
- **D30:** exponentially discounted Beta-Binomial competence with 30-call half-life.

Two separate ridge-logistic BAD_SUPPRESSION models were trained on 2024 daily Router-UP cases:

- target = actual DOWN;
- features = SQRT normalized risk + competence error;
- L2 lambda = 1.0;
- no hyperparameter search.

Operational risk was the conservative maximum:

`p_bad = max(p_bad_F30, p_bad_D30)`

Actions:
- p_bad <= 0.20 -> SUPPRESS
- 0.20 < p_bad <= 0.35 -> WATCH
- p_bad > 0.35 -> RETAIN

## 2. 2024 development

2024 Router-UP daily sample:
- n = 42
- actual UP = 26
- actual DOWN = 16

Both models converged in 5 Newton iterations.

Training Brier:
- F30 = **0.2322**
- D30 = **0.2286**

On the 17 SQRT alarms:
- RETAIN = 13
- WATCH = 4 = 3 UP / 1 DOWN
- SUPPRESS = 0

This is development evidence only.

## 3. Locked 2025 challenge

No coefficient, window, half-life, regularization or threshold changed.

On 90 SQRT alarms:

| Action | Count | Actual UP | Actual DOWN |
|---|---:|---:|---:|
| RETAIN | 77 | 35 | 42 |
| **WATCH** | **8** | **7** | **1** |
| **SUPPRESS** | **5** | **3** | **2** |

SUPPRESS performance:
- suppression precision = **60.00%**
- false-alarm reduction = **6.67%**
- true-DOWN retention = **95.56%**
- remaining forced-DOWN precision = **50.59%**
- net suppression benefit = **+1**

Frozen hard Router-V2 benchmark:
- 16 suppressions
- 10 good / 6 bad
- suppression precision = 62.50%
- true-DOWN retention = 86.67%
- remaining forced-DOWN precision = 52.70%

## 4. What improved

The controller solved one prior structural failure:

> WATCH did not collapse.

Eight 2025 SQRT alarms remained in the middle state, and **7 of those 8 were actual UP**.

The controller also became materially safer:
- hard veto true-DOWN retention = **86.67%**
- action-risk controller = **95.56%**

So fixed-effective-sample / discounted competence did improve stability and conservatism.

## 5. Why the preregistered gate still failed

SUPPRESS precision was only **60.00%**, below the hard-veto 62.50% benchmark.

Remaining forced-DOWN precision was **50.59%**, below the hard-veto 52.70%.

Therefore V1 cannot be promoted.

An important diagnostic is the fitted SQRT-risk coefficient. Both 2024 models learned a **negative** coefficient on `sqrt_normalized_risk_score`: within the 2024 Router-UP development sample, larger SQRT normalized risk was associated with lower estimated BAD_SUPPRESSION probability.

That relationship did not transport reliably. In 2025, some strong-SQRT-risk Router-UP cases were suppressed but were actual DOWN.

This means the next controller should not allow a flexible fit to learn an economically/safety-incoherent sign without constraint.

## 6. Binding interpretation

The experiment is useful but not a success.

It establishes that:
- fixed-window and discounted competence prevent confidence-scale drift;
- a genuine WATCH state can survive out of sample;
- direct BAD_SUPPRESSION modeling can improve true-DOWN retention;
- but the unconstrained 2024 ridge-logit risk ordering is not reliable enough for SUPPRESS decisions.

The particularly strong 2025 WATCH anatomy (7 UP / 1 DOWN) is descriptive only. It may **not** be converted post hoc into a new suppression rule.

Next clean method:
- Learn-Then-Test / risk-control calibration of the **action** itself, or
- a monotonicity-constrained risk model in which stronger SQRT downside-risk evidence cannot reduce estimated BAD_SUPPRESSION risk.

`DIRECT_ACTION_RISK_CONTROLLER_V1_RESEARCH = NOT_SUPPORTED_AS_ACTION_RISK_SUCCESSOR / NOT_RUNTIME`
