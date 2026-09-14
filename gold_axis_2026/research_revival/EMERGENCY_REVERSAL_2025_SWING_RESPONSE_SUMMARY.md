# EMERGENCY_REVERSAL 2025 — %2 Economic Swing Response Audit

## Scope
- Working benchmark: `WORKING_2025_2PCT_SWING_BENCHMARK.csv` (28 hindsight-reconstructed >=2% economic swings touching 2025).
- Engine: frozen R4.1 `EMERGENCY_REVERSAL`.
- This benchmark is separate from the frozen 3-sigma GC-BREAK event label.
- No interpolation, forward-fill, fabricated state, or post-score threshold tuning is used.
- Diagnostic remaining-move buckets are kept identical to FAST/SLOW: >=75% `ZAMANINDA`, 25-75% `GEC_AMA_KULLANILABILIR`, <25% `COK_GEC`, no correct alert before the swing endpoint `KACIRDI`.

## Frozen mechanism
R4.1 first arms an abnormal monthly displacement when close differs from the monthly reference by at least 4%. After an UP shock it tracks the running peak and emits `DOWN_ALERT` after a >=4% reversal from that peak. After a DOWN shock it tracks the running trough and emits `UP_ALERT` after a >=4% rebound from that trough. State resets on a new calendar month.

For the engine-wise historical export, the monthly reference is `patch_v7` / CAUSAL_PATCH frozen H1 replay. The function argument in `emergency.py` is historically named `monthly_vw_forecast`, but the exporter actually supplies CAUSAL_PATCH `patch_v7`.

## 2025 state activity
Across the 204 retrospective-challenge governed origins:
- `OFF`: 182 origins
- `DOWN_ALERT`: 12 origins
- `UP_ALERT`: 10 origins
- Non-OFF alert share: 22/204 = 10.8%

Four new alert episodes start in 2025:
1. 2025-10-21 `DOWN_ALERT` — 9 governed origins through 2025-10-31.
2. 2025-11-10 `UP_ALERT` — 4 governed origins through 2025-11-13.
3. 2025-11-24 `UP_ALERT` — 6 governed origins through 2025-11-30.
4. 2025-12-29 `DOWN_ALERT` — 3 governed origins through 2025-12-31.

All four episode onsets are directionally aligned with the contemporaneous working swing at the onset date, but two alerts persist into the immediately following opposite swing and become wrong carry-over evidence.

## Event-level results
- Total swings: 28
- `ZAMANINDA`: 2
- `GEC_AMA_KULLANILABILIR`: 2
- `COK_GEC`: 1
- `KACIRDI`: 23
- Correct alert while >=25% of the swing remained: 4/28 = 14.3%.
- Swings with any correct alert before the endpoint: 5/28 = 17.9%.

### Reaction provenance
- New correct alert formed inside the swing: 4
- Correct alert carried from a preceding alert episode: 1
- No correct alert before the swing endpoint: 23
- Of the four new correct alerts, three retained >=25% of the move; one (2025-12-29) arrived after about 92% of the benchmark move had already occurred.

## Direction split
UP swings (14):
- Correct alert: 2
- Usable >=25% remaining: 2
- Missed: 12

DOWN swings (14):
- Correct alert: 3
- Usable >=25% remaining: 2 (one new alert, one carried alert)
- Too late: 1
- Missed: 11

## Key events

### Major value-add: 2025-10-20 -> 2025-10-29 DOWN -9.87%
- `EMERGENCY_REVERSAL` is `OFF` on 2025-10-20.
- It emits a new `DOWN_ALERT` on 2025-10-21 at close 4130.33.
- About 45.0% of the benchmark decline is still ahead.
- In the separate audits, FAST does not turn `ROBUST_DOWN` until 2025-10-28 (about 4.5% remaining) and SLOW never confirms `ROBUST_DOWN` before the swing endpoint.
- This is the clearest 2025 example of genuine complementary value from Emergency Reversal.

### Correct but carried: 2025-10-30 -> 2025-11-04 DOWN -2.43%
- The prior `DOWN_ALERT` episode remains active at the new swing start.
- It is therefore directionally correct from the start, but this is not a newly detected reversal.

### Useful UP reversal: 2025-11-04 -> 2025-11-12 UP +6.85%
- New `UP_ALERT` on 2025-11-10.
- About 32.8% of the swing remains.
- Useful, but not early.

### Strong UP context: 2025-11-17 -> 2025-12-28 UP +12.03%
- New `UP_ALERT` on 2025-11-24.
- About 81.9% of the swing remains.
- This is the strongest timely new Emergency Reversal response in the year.

### Too late: 2025-12-28 -> 2026-01-01 DOWN -4.80%
- New `DOWN_ALERT` on 2025-12-29.
- Only about 7.8% of the benchmark move remains.
- Correct direction, but economically very late under the working diagnostic.

## Failure modes
- The engine is intentionally sparse: it requires both a >=4% monthly-reference displacement and a later >=4% reversal from the running extreme.
- Consequently it misses most ordinary >=2% swings and cannot be judged as a universal direction detector.
- Monthly reset can cut continuity across month boundaries; for example an alert state is re-armed/reset when the calendar month changes.
- Alert persistence can lag a fast V-turn. The 2025-10-21 `DOWN_ALERT` persists into the 2025-10-29 -> 2025-10-30 UP swing, and the 2025-11-10 `UP_ALERT` persists into the 2025-11-12 -> 2025-11-17 DOWN swing.

## Interpretation
`EMERGENCY_REVERSAL` is not a broad turning-point detector. It is a sparse abnormal-reversal specialist. Its 2025 value is concentrated in a few large dislocations, especially the 20-29 October decline where it materially outperforms FAST and SLOW on timing. It does not rescue most other downside blind spots and should therefore remain a selective complementary context, not a replacement for FAST/SLOW or a universal break engine.
