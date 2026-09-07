# GOLD CONTROL — MARKET SHOCK CHALLENGER V1 REJECTION

**Decision:** `REJECTED_PRIMARY_FORMULA_AUDIT`  
**Decision basis:** pre-holdout authority/code audit; not outcome-driven.  
**Production authority:** `NONE`  
**Neon write:** `NONE`

## Reason

The V1 implementation of the Lee–Mykland Gumbel scale constant used:

`S_n = 1 / (2 * c * sqrt(2 log n))`, with `c = sqrt(2/pi)`.

A primary-author-hosted copy of Lee & Mykland, *Jumps in Financial Markets: A New Nonparametric Test and Jump Dynamics*, Lemma 1 / Eq. (13), gives:

`S_n = 1 / (c * sqrt(2 log n))`.

The V1 implementation therefore makes the Gumbel scale half the primary formula and lowers the rejection threshold. V1 deterministic tests only proved that the code matched its frozen implementation; they did not independently establish that the frozen formula matched the primary source. The primary-source discrepancy invalidates V1 as a candidate regardless of historical outcome.

## Governance consequence

1. V1 historical results, if the already-started workflow completes, are audit-only and must not be used to promote, tune, or select a production shock detector.
2. V1 thresholds/vote logic will not be silently patched under the same challenger identity.
3. A new `MARKET_SHOCK_CHALLENGER_V2` identity is required with the primary Lee–Mykland formula and independent formula tests.
4. Existing `EMERGENCY_LEVEL` / `EMERGENCY_REVERSAL` V1.46 remain untouched.
5. Real-history false-positive rate remains `NOT_PROVEN` without an independent event-label contract.
