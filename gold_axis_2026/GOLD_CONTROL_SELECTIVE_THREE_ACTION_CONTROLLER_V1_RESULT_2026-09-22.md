# GOLD CONTROL — SELECTIVE THREE-ACTION CONTROLLER V1 RESULT

**Date:** 2026-09-22  
**Identity:** `SELECTIVE_THREE_ACTION_CONTROLLER_V1_RESEARCH`  
**Preregistration:** `4d30b9b00b20d8edd14e61c999b2737570c0caf0`  
**Final status:** `SUPPRESS_SAFETY_FAILED_AND_THREE_ACTION_COLLAPSED`  
**Runtime authority:** NONE

## 1. Frozen thresholds

The controller used two independently preregistered NP-style safety levels from the 2024 full daily panel:

- WATCH: alpha = 0.20, delta = 0.10
- SUPPRESS: alpha = 0.10, delta = 0.10

2024 actual-DOWN calibration support: n0 = 86.

Derived thresholds:
- `tau_watch = 0.4302662741`
- `tau_suppress = 0.4948452868`

Action rule:
- Router ABSTAIN or score <= tau_watch -> RETAIN
- tau_watch < score <= tau_suppress -> WATCH
- score > tau_suppress -> SUPPRESS

## 2. 2024 calibration diagnostics

Across all 205 daily rows:

| Action | Count | Actual UP | Actual DOWN | UP rate |
|---|---:|---:|---:|---:|
| RETAIN | 171 | 97 | 74 | 56.73% |
| WATCH | 25 | 17 | 8 | 68.00% |
| SUPPRESS | 9 | 5 | 4 | 55.56% |

On the 17 SQRT alarm origins:

| Action | Count | Actual UP | Actual DOWN |
|---|---:|---:|---:|
| RETAIN | 13 | 7 | 6 |
| WATCH | 3 | 2 | 1 |
| SUPPRESS | 1 | 1 | 0 |

The 2024 SQRT figures are calibration diagnostics only.

## 3. Locked 2025 challenge

No threshold or rule changed.

Across all 237 daily rows:

| Action | Count | Actual UP | Actual DOWN |
|---|---:|---:|---:|
| RETAIN | 200 | 113 | 87 |
| WATCH | **0** | 0 | 0 |
| SUPPRESS | **37** | 27 | 10 |

On 90 SQRT alarms:

- RETAIN = 74
- WATCH = **0**
- SUPPRESS = **16**
- good suppressions = 10
- bad suppressions = 6
- suppression precision = **62.50%**
- false-alarm reduction = **22.22%**
- true-DOWN retention = **86.67%**
- remaining forced-DOWN precision = **52.70%**

These 16 SUPPRESS actions are exactly the same 16 actions produced by the frozen hard Router-V2 veto.

## 4. Why the three-action idea collapsed

The intended middle region disappeared in 2025.

All 2025 Router-V2 UP scores were above the frozen 2024 `tau_suppress`, so every Router-UP case became SUPPRESS and none became WATCH.

This exposes a structural problem with the score chosen for V1:

> the selected expert's Wilson lower confidence bound is not a stationary absolute scale across years.

As matured history grows, the lower bound can rise because:
- sample support increases;
- estimated expert precision changes;
- the selected expert mix changes.

Therefore a fixed 2024 absolute score threshold can cease to represent the same safety level in 2025.

## 5. Frozen gate

The preregistered SUPPRESS safety requirement was true-DOWN retention >= 90%.

Observed 2025 retention = **86.67%**.

Therefore:
- suppress safety: FAIL
- WATCH count >=3: FAIL because WATCH=0
- three-action successor: NOT SUPPORTED

## 6. Binding interpretation

The three-action concept itself is not rejected, but this implementation is.

The failure is informative:
- using static absolute thresholds on Router Wilson-LCB does not create a stable RETAIN/WATCH/SUPPRESS partition;
- by 2025 the controller collapses back to the hard veto;
- therefore it adds no operational protection over Router V2.

The next controller should use a risk-calibrated action criterion whose meaning is stable over time, rather than a fixed raw confidence threshold.

`SELECTIVE_THREE_ACTION_CONTROLLER_V1_RESEARCH = SUPPRESS_SAFETY_FAILED_AND_THREE_ACTION_COLLAPSED / NOT_RUNTIME`
