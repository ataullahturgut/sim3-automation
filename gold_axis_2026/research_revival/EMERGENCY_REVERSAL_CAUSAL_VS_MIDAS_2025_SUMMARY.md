# Emergency Reversal 2025 — CAUSAL reference vs MIDAS reference

## Scope
- Frozen governed engine remains `EMERGENCY_REVERSAL` with `CAUSAL_PATCH / patch_v7` monthly reference.
- Research challenger: `EMERGENCY_REVERSAL_MIDAS_CHALLENGER_V1`.
- Challenger changes exactly one ingredient: monthly reference is `VW_MIDAS_MSVR_SUCCESSOR_V1` instead of `CAUSAL_PATCH`.
- Emergency thresholds are unchanged: absolute monthly-reference displacement >=4% to arm direction; reversal >=4% from running peak/trough to alert.
- Calendar-month reset remains unchanged.
- Same governed daily origins and same 28 hindsight-reconstructed >=2% economic swings are used.
- No threshold tuning, interpolation, forward-fill, or post-score rescue is used.
- Frozen production/governed identity is NOT changed by this experiment.

## Input verification
`VW_MIDAS_MSVR_SUCCESSOR_V1` has an available frozen historical H=1 reference on all 204 retrospective-challenge origins in 2025.

2025 monthly MIDAS references (USD/oz):
- Jan 2656.8043
- Feb 2808.2031
- Mar 2905.0890
- Apr 3100.6255
- May 3264.7704
- Jun 3334.4437
- Jul 3400.9748
- Aug 3327.4606
- Sep 3481.4008
- Oct 3798.3947
- Nov 4092.4791
- Dec 4172.6586

## Head-to-head event results
| Metric | Frozen CAUSAL reference | MIDAS challenger |
|---|---:|---:|
| 2025 governed origins | 204 | 204 |
| Non-OFF alert origins | 22 (10.8%) | 32 (15.7%) |
| DOWN_ALERT origins | 12 | 22 |
| UP_ALERT origins | 10 | 10 |
| ZAMANINDA swings | 2 | 2 |
| GEC_AMA_KULLANILABILIR swings | 2 | 2 |
| COK_GEC swings | 1 | 3 |
| KACIRDI swings | 23 | 21 |
| Correct alert with >=25% move remaining | 4/28 (14.3%) | 4/28 (14.3%) |
| Any correct alert before swing endpoint | 5/28 (17.9%) | 7/28 (25.0%) |
| New correct alert formed inside swing | 4 | 6 |

## What changed
All CAUSAL-vs-MIDAS alert differences in 2025 occur in May. MIDAS creates 10 extra `DOWN_ALERT` origin-days; CAUSAL remains `OFF` on those dates.

The mechanism is transparent:
- On 2025-05-06 close = 3434.70.
- MIDAS May reference = 3264.7704, so displacement = +5.20%, which exceeds the +4% arming threshold.
- CAUSAL May reference = 3305.6005, so displacement = +3.91%, below the +4% threshold; CAUSAL does not arm an UP shock.
- From the 3434.70 running peak, close reaches 3235.24 on 2025-05-12, a -5.81% reversal, so the MIDAS challenger emits `DOWN_ALERT`.

This creates two additional swing hits:
1. 2025-05-06 -> 2025-05-14 DOWN -7.38%: first MIDAS `DOWN_ALERT` 2025-05-12, only 21.32% of the swing remains -> `COK_GEC`.
2. 2025-05-23 -> 2025-05-30 DOWN -2.01%: first MIDAS `DOWN_ALERT` 2025-05-28, only 4.27% remains -> `COK_GEC`.

Therefore MIDAS increases sensitivity but does not improve the economically usable >=25%-remaining count under the frozen diagnostic.

## Important unchanged events
For the economically most important October reversal, both references behave identically:
- 2025-10-20 -> 2025-10-29 DOWN -9.87%.
- Both emit `DOWN_ALERT` on 2025-10-21 at close 4130.33.
- About 45.0% of the decline remains.

Both references also behave identically for:
- 2025-11-04 -> 2025-11-12 UP +6.85%: `UP_ALERT` on Nov 10, ~32.8% remaining.
- 2025-11-17 -> 2025-12-28 UP +12.03%: `UP_ALERT` on Nov 24, ~81.9% remaining.
- 2025-12-28 -> 2026-01-01 DOWN -4.80%: `DOWN_ALERT` on Dec 29, but only ~7.8% remains.

## Decision
`EMERGENCY_REVERSAL_MIDAS_CHALLENGER_V1` is a valid research challenger because the only changed component is the already-governed frozen monthly H=1 reference. It is more sensitive than the CAUSAL-reference version in 2025, but the extra sensitivity produces only two additional correct swing detections and both are economically late under the existing diagnostic.

The 2025 evidence therefore does NOT justify replacing the frozen CAUSAL-reference Emergency Reversal with MIDAS. The defensible conclusion is:

- CAUSAL reference: sparser.
- MIDAS reference: more sensitive in May.
- Useful >=25%-remaining swing capture: tie at 4/28.
- Major October crash detection: identical.
- Promotion/replacement: NOT PROVEN.

Keep the governed Emergency Reversal unchanged and retain the MIDAS version as a research-only challenger for multi-year testing before any architecture change.
