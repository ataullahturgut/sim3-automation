# GOLD CONTROL — LEARN-THEN-TEST ACTION-RISK V1 RESULT

**Date:** 2026-09-22  
**Identity:** `LEARN_THEN_TEST_ACTION_RISK_V1_RESEARCH`  
**Preregistration:** `8de202f3cfe2c33eb6abffb7df3d4d656666fb88`  
**Final status:** `BLOCKED_INSUFFICIENT_ALARM_CONDITIONAL_CALIBRATION_SUPPORT`  
**Runtime authority:** NONE

## 1. What was tested

This study deliberately corrected the earlier conditioning mismatch.

The risk target was not all-daily false suppression. It was exactly:

[
P(	ext{SUPPRESS} mid 	ext{actual DOWN and SQRT alarm})
]

with:
- `alpha = 0.20`;
- `delta = 0.10`;
- equivalently, at least 80% true-DOWN retention at 90% confidence.

Before any candidate policy could be scored, the preregistered protocol required a calibration-support feasibility check.

## 2. 2024 support

2024 contains:
- SQRT alarms = **17**;
- actual-DOWN SQRT alarms = **7**;
- actual-UP / false forced-DOWN alarms = **10**.

For zero observed bad suppressions, the exact best-case binomial condition is:

[
(1-alpha)^n le delta
]

Therefore:

[
n_{min} = lceil log(0.10)/log(0.80) ceil = 11
]

But available support is only:

[
n=7
]

Even with **zero** bad suppressions, the best possible tail probability would be:

[
0.8^7 = 0.2097152
]

which is larger than `delta=0.10`.

## 3. Consequence

The mandatory support gate fails.

Therefore, by preregistered rule:

- no candidate suppression policies were scored;
- no threshold family was selected;
- 2025 was not read/scored under this identity;
- alpha/delta were not relaxed;
- the problem was not silently redefined as all-daily risk.

## 4. Interpretation

This is not evidence that Learn-Then-Test is a poor method.

It is evidence that the **current alarm-conditional calibration sample is too small to make the safety claim we actually care about**.

This is important because a weaker workaround would be easy but scientifically misleading:
- using all daily DOWN cases gives much more data,
- but it does not directly control true-DOWN loss *conditional on an SQRT alarm*.

The correct conclusion is therefore a support limitation, not a failed controller.

## 5. Binding decision

`LEARN_THEN_TEST_ACTION_RISK_V1_RESEARCH = BLOCKED_INSUFFICIENT_ALARM_CONDITIONAL_CALIBRATION_SUPPORT / NOT_RUNTIME`

The next clean step is to extend same-clock pre-2025 SQRT + frozen-verifier historical support until there are at least **11** actual-DOWN alarm calibration cases; more is preferable if a finite policy family is to be tested with multiplicity control.

No 2025-based rescue is authorized.
