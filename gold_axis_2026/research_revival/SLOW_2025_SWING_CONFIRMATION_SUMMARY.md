# SLOW 2025 — %2 Economic Swing Confirmation Audit

## Scope
- Working benchmark: `WORKING_2025_2PCT_SWING_BENCHMARK.csv` (28 hindsight-reconstructed >=2% economic swings touching 2025).
- Engine: frozen `SLOW` completed-W-FRI confirmation state from the governed engine-wise replay.
- This benchmark is separate from the frozen 3-sigma GC-BREAK label.
- SLOW is evaluated in its native role: completed-week confirmation/new-regime evidence, not as an early turning-point detector.
- No interpolation, forward-fill, or missing-state fabrication is used.
- The remaining-move buckets are diagnostic and are the same working thresholds used for FAST: >=75% `ZAMANINDA`, 25-75% `GEC_AMA_KULLANILABILIR`, <25% `COK_GEC`, no correct robust state before the swing endpoint `KACIRDI`.

## Results
- Total swings: 28
- `ZAMANINDA`: 9
- `GEC_AMA_KULLANILABILIR`: 2
- `COK_GEC`: 1
- `KACIRDI`: 16
- Correct robust confirmation while >=25% of the swing remained: 11/28 = 39.3%.

### Reaction provenance
- New correct SLOW confirmation formed inside the swing: 5
- Correct SLOW confirmation already carried into the swing: 6
- SLOW had turned correctly during the preceding opposite swing: 1
- No correct robust confirmation before the swing endpoint: 16

Therefore the raw 11/28 usable count should not be interpreted as 11 newly detected turns. Only 5/28 swings formed a new correct `ROBUST_UP`/`ROBUST_DOWN` confirmation during the swing; of these, 4 retained >=25% of the move and one arrived at the endpoint.

## Direction asymmetry
- UP swings (14): 8 `ZAMANINDA`, 2 `GEC_AMA_KULLANILABILIR`, 1 `COK_GEC`, 3 `KACIRDI`.
- DOWN swings (14): 1 `ZAMANINDA`, 0 usable-late, 0 too-late, 13 `KACIRDI`.
- The sole timely DOWN case (event 26, 2025-11-12 to 2025-11-17) was not a new down confirmation after the swing began: `ROBUST_DOWN` had formed on 2025-11-07 during the preceding UP swing and was carried into the DOWN swing.

## State distribution in calendar 2025
- `ROBUST_UP`: 132 governed origins
- `NOT_YET_ROBUST`: 63
- `ROBUST_DOWN`: 9

The 2025 SLOW state is therefore strongly asymmetric toward UP. The two `ROBUST_DOWN` episodes began on 2025-07-07 and 2025-11-07; both began while the working economic-swing benchmark was in an UP swing.

## Examples
### Strong confirmation
- Event 19, 2025-08-19 -> 2025-10-16, UP +31.60%.
- SLOW starts `NOT_YET_ROBUST`, becomes `ROBUST_UP` on 2025-08-29.
- About 86.6% of the eventual swing remained. This is a genuinely useful completed-week confirmation.

### Failure on a major reversal
- Event 22, 2025-10-20 -> 2025-10-29, DOWN -9.87%.
- SLOW remained `ROBUST_UP` through the swing and never produced `ROBUST_DOWN` before the endpoint.
- It therefore misses this economically important fast downside reversal.

## Interpretation
SLOW behaves as a slow persistence/confirmation channel, not a turn detector. In the strong 2025 bull regime it can confirm sustained UP moves well, but it provides almost no timely downside confirmation. The engine should not be expected to protect against fast downside reversals by itself. Its plausible value is confirmation of persistent regimes after a faster channel has already weakened or flipped.
