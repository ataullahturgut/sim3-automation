# FAST — 2025 Working Economic Swing Response Summary

**Status:** research diagnostic only; no production authority.  
**Engine:** `FAST` only. No engine combination is performed here.  
**Working benchmark:** unchanged ≥2% directional-change economic-opportunity rule, built from `xau_intraday_research_cache_5m` New York 16:55 observations.  
**FAST evidence:** governed enginewise FAST output on its native daily governed origins. Missing origins are not interpolated or forward-filled.

This working 2% benchmark is separate from, and does not replace, the manifest's frozen volatility-normalized 3-sigma GC-BREAK event label.

## Result

There are 28 working swings overlapping 2025. The raw timing classification is 9 `ZAMANINDA`, 6 `GEC_AMA_KULLANILABILIR`, 4 `COK_GEC`, and 9 `KACIRDI`; therefore 15/28 (53.6%) have at least 25% of the realized swing still ahead when the first matching robust FAST state is observed.

That raw number materially overstates reversal detection. Only 11 of the 28 swings contain a new correct robust FAST transition after the swing begins. Among those 11 fresh reactions, only 1 is `ZAMANINDA`, 6 are `GEC_AMA_KULLANILABILIR`, and 4 are `COK_GEC`. Seven apparent start-aligned successes are stale carry-over of an older robust state, and one additional UP state had already flipped during the immediately preceding opposite swing.

The strongest fresh FAST result is the 2025-08-19 to 2025-10-16 UP swing (+31.60%). FAST starts `ROBUST_DOWN`, becomes `MIXED` on 2025-08-22, and reaches `ROBUST_UP` on 2025-08-25 while approximately 96.7% of the realized benchmark move remains.

The main weakness is downside reversal detection. Of 14 DOWN swings, FAST completely misses 7. Of 14 UP swings it misses 2. Several short DOWN countertrend moves remain `ROBUST_UP` throughout. Even the large 2025-10-20 to 2025-10-29 DOWN swing (-9.87%) is recognized as `ROBUST_DOWN` only on 2025-10-28, with about 4.5% of the realized move remaining.

## Interpretation

FAST behaves primarily as a persistence/continuation and tactical trend-health state, not as a reliable turning-point detector. It can be very useful once a sustained new trend establishes itself, but it is structurally weak on fast V-reversals and short countertrend DOWN swings. This is consistent with its governed role as tactical trend/weakening evidence and argues against treating FAST alone as break authority.

No FAST parameter was changed, the 2% benchmark threshold was not tuned to improve FAST, and no main-model or trading/action mapping was produced.

Detailed engine-level rows: `FAST_2025_SWING_RESPONSE_AUDIT.csv`.  
Engine-independent working benchmark: `WORKING_2025_2PCT_SWING_BENCHMARK.csv`.
