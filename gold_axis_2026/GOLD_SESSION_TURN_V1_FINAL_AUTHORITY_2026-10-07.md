# SESSION TURN V1 — FINAL AUTHORITY

**Date:** 2026-10-07
**Status:** COMPLETE / WINDOW-SPECIFIC CORRECTION EVIDENCE RETAINED

## Identity

SESSION TURN V1 is a fixed tail-unbalanced reversal specialist layered on fresh SESSION AURORA.

Frozen rule:
- latest 120 active completed hourly returns;
- prior 250 same-session anchors;
- minimum 120 valid prior anchors;
- 80th-percentile positive/negative semivariance tails;
- no fitted classifier;
- no threshold search;
- both-tail state = uncertainty only / no forced flip.

2022 is tail-history warm-up only.
2023–2024 are development.
2025 is frozen transport.
2026 is unopened.

## Development result

Three session heads passed the frozen role-aware correction gate:

### Sobti Asia Afternoon
- N = 175
- AURORA BA = 52.76%
- TURN BA = 54.74%
- TURN UP recall = 49.47%
- TURN DOWN recall = 60.00%
- overrides = 9
- rescues = 6
- breaks = 3
- net rescue = +3

### Sobti Asia Morning
- N = 170
- AURORA BA = 50.00%
- TURN BA = 50.88%
- overrides = 7
- rescues = 4
- breaks = 3
- net rescue = +1

### WGC Asia
- N = 102
- AURORA BA = 47.36%
- TURN BA = 52.77%
- TURN UP recall = 78.26%
- TURN DOWN recall = 27.27%
- overrides = 8
- rescues = 5
- breaks = 3
- net rescue = +2

All other heads failed development because TURN produced non-positive net rescue and/or degraded the AURORA comparator.

## Frozen 2025 transport

### Sobti Asia Afternoon
- N = 137
- AURORA BA = 48.92%
- TURN BA = 49.66%
- AURORA Brier = 0.2755
- TURN Brier = 0.2735
- overrides = 1
- rescues = 1
- breaks = 0
- net rescue = +1

Decision:
- retains a small positive correction contribution;
- keep as a window-specific correction candidate.

### Sobti Asia Morning
- N = 140
- AURORA BA = 56.50%
- TURN BA = 55.13%
- overrides = 2
- rescues = 0
- breaks = 2
- net rescue = -2

Decision:
- transport fails;
- do not retain as a correction candidate.

### WGC Asia
- N = 104
- AURORA BA = 55.32%
- TURN BA = 55.96%
- overrides = 3
- rescues = 2
- breaks = 1
- net rescue = +1
- Brier 0.2670 -> 0.2690

Decision:
- direction contribution remains mildly positive;
- calibration deteriorates slightly;
- retain only as a low-weight conditional correction candidate, not as a probability model replacement.

## Binding decision

1. SESSION TURN V1 is complete and clock-safe.
2. TURN is not a stand-alone direction engine.
3. Sobti Asia Afternoon TURN remains a valid conditional correction candidate.
4. WGC Asia TURN remains a lower-confidence conditional correction candidate because direction improves but Brier worsens.
5. Sobti Asia Morning TURN is rejected after frozen transport deterioration.
6. Europe, NY/London, Late-US and WGC US are not retained.
7. TURN contributes only when its frozen tail condition fires; it receives no unconditional direction vote.
8. No 2025 retuning occurred.
9. 2026 remains unopened.
