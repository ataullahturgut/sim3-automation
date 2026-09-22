# GOLD CONTROL — MONOTONIC ACTION-RISK CONTROLLER V1 RESULT

**Date:** 2026-09-22  
**Identity:** `MONOTONIC_ACTION_RISK_CONTROLLER_V1_RESEARCH`  
**Preregistration:** `a696308de6cc646fc9925ddb34f1299c21ab6609`  
**2024 fit frozen before 2025:** `194d9a1fb25f08379c1645089fdd55d079fcdc19`  
**Final status:** `TOO_CONSERVATIVE_INSUFFICIENT_SUPPRESS_SUPPORT`  
**Runtime authority:** NONE

## 1. What changed

The frozen Router V2 remained unchanged.

The controller reused:
- F30 competence;
- D30 discounted competence;
- SQRT normalized risk.

But unlike the previous unconstrained ridge-logit controller, both BAD-risk models were forced to obey:

- `beta_sqrt >= 0`
- `beta_competence_error >= 0`

so stronger SQRT downside-risk evidence or worse UP-expert competence could never reduce estimated BAD_SUPPRESSION risk.

## 2. 2024 constrained fit

2024 Router-UP development sample:
- n = 42
- actual DOWN = 16
- actual UP = 26

The active-set audit showed:

- the unconstrained F30 model wanted negative SQRT and negative competence-error slopes;
- the unconstrained D30 model also wanted negative SQRT and negative competence-error slopes;
- fixing only one slope at zero still left the other fitted slope negative;
- therefore the **only feasible monotone optimum fixed both slopes at zero**.

Both monotone models became the same intercept-only model:

[
p_{bad} = 16/42 = 0.380952
]

Training Brier = **0.23583**.

This fit was committed and frozen **before any 2025 challenge read**.

## 3. Consequence for the action rule

Frozen action thresholds:

- `p_bad <= 0.20` -> SUPPRESS
- `0.20 < p_bad <= 0.35` -> WATCH
- `p_bad > 0.35` -> RETAIN

Since the frozen monotone model gives:

[
p_{bad}=0.380952 > 0.35
]

every Router-UP origin becomes **RETAIN_DOWN**.

## 4. Locked 2025 challenge

2025 SQRT baseline:
- alarms = 90
- true DOWN = 45
- false forced-DOWN = 45
- baseline precision = 50.00%

Monotonic controller:

| Action | Count | Actual UP | Actual DOWN |
|---|---:|---:|---:|
| RETAIN | **90** | 45 | 45 |
| WATCH | **0** | 0 | 0 |
| SUPPRESS | **0** | 0 | 0 |

Therefore:
- true-DOWN retention = **100%**
- false-alarm reduction = **0%**
- remaining forced-DOWN precision = **50.00%**
- SUPPRESS support = **0**

## 5. Interpretation

The monotonic constraint fixed the previous model's safety-incoherent sign problem, but it also exposed a deeper fact:

> the 2024 development data do not contain a usable monotone two-feature signal strong enough to justify suppression.

The unconstrained controller obtained action variation partly by learning the wrong sign. Once that was forbidden, the model became intercept-only.

So the monotonic version is safer but operationally useless as a suppressor.

This is a useful negative result. It tells us not to keep tuning logistic coefficients or thresholds around the same two features.

The next scientifically cleaner method is **Learn-Then-Test / risk-control calibration of the action itself**, where the object being calibrated is the suppression action/risk rather than a parametric BAD-risk probability surface.

## 6. Binding decision

`MONOTONIC_ACTION_RISK_CONTROLLER_V1_RESEARCH = TOO_CONSERVATIVE_INSUFFICIENT_SUPPRESS_SUPPORT / NOT_RUNTIME`

No 2025 value was used to alter the fit or thresholds.
