# GOLD CONTROL — MARKET SHOCK + MACRO EVENT JOINT AUDIT — 2026 YTD PREREG

**Status:** `PREREGISTERED_HISTORICAL_RESEARCH_AUDIT / NOT_PRODUCTION_AUTHORITY`  
**Frozen before inspecting the 2026 YTD joint result.**

## Scope

This is a separate follow-on holdout audit for **2026-01-01 through 2026-08-31 23:59:59Z**. It does not modify or reinterpret the completed 2024-2025 Joint Audit V1.

## Frozen identities

- Market Shock: `MARKET_SHOCK_CHALLENGER_V3 @ 12edc11e42b58d9c91fb587efdda9269cae4c91a`
- Macro Event: `MACRO_EVENT_SUCCESSOR_V3`
- XAU: governed Neon `XAU_RESEARCH_TWELVE_5MIN_CACHE_V1`, Twelve Data `XAU/USD`, 5-minute closes.
- Market Shock standalone status remains failed/not promoted regardless of this joint result.

## Frozen test rules

Exactly the same joint-test logic as the preregistered 2024-2025 Joint Audit V1 is retained:

1. Strong Macro Event state is only `GOLD_ADVERSE_MACRO_SHOCK` or `GOLD_SUPPORTIVE_MACRO_SHOCK`.
2. Market Shock match window is `[release, release+10m]`.
3. Macro direction is the sign of the frozen Macro Event V3 score.
4. Market Shock direction is the frozen V3 shock direction.
5. Direction concordance requires equal non-zero signs.
6. Post-confirmation continuation is measured from the first matched Market Shock close to the latest available close at or before `release+30m`, signed by the Macro Event direction.
7. Matched controls use the same weekday/time-of-day via offsets `-7,+7,-14,+14,-21,+21,-28,+28` days; up to four controls per event; controls with another Macro Event within ±60m are excluded.
8. Shock-incidence enrichment uses one-sided Fisher exact test.
9. Direction concordance uses exact one-sided binomial test against 0.5.
10. No threshold, event family, direction rule, timing window, or acceptance rule may be changed after observing the 2026 result.

## Interpretation

Because 2026 YTD contains only a small number of strong Macro Event observations, this audit is an **independent corroboration test**, not a sample-size cure. A positive result can strengthen the joint-context hypothesis but cannot by itself authorize production or rehabilitate Market Shock V3 as a standalone model.

Evidence class: `HISTORICAL_RESEARCH_AUDIT`.  
Prospective claim: `FALSE`.  
Production authority: `FALSE`.  
Neon writes: `NONE`.
