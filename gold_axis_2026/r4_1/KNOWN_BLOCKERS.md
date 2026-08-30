# Known Blockers

The following are intentionally not reconstructed from hindsight:

1. **Exact original VW-MIDAS-SVR Adapt V2 production runner/source chain** — analytical archived outputs exist, but the original immutable runner/raw preprocessing chain is not fully retained.
2. **Full Macro Event DOWN construction** — partial frozen contract is known (`macro_score <= -1`, Fast DOWN, same-day gold return <= -0.5%), but the exact NFP/unemployment/wage scoring, consensus source, release-vintage and timestamp rules are not fully recovered.
3. **Exact final R4 exposure ladder and arbitration** — prior experiments used 0/25/50/75/100 sleeves, but the exact final production state machine is not proven. This project therefore returns direction/risk states and GVZ cap, not an invented position percentage.
4. **Intraday Emergency** — no exact frozen intraday rule has been recovered. EOD signals default to next-session execution.
5. **Reversal Emergency as automatic direction flip** — rejected. Pre-2026 replay did not support raw >=4% reversal as a reliable automatic trend flip. It remains ALERT_ONLY.
