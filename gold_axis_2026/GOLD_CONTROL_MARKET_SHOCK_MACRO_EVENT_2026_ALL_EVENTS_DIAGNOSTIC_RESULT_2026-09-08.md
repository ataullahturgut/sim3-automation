# GOLD CONTROL — 2026 All-Events Macro Event + Market Shock Diagnostic Result

Date: 2026-09-08
Evidence: HISTORICAL_RESEARCH_AUDIT
Production authority: false
Thresholds changed: false

## Frozen test population
- Period: 2026-01-01 through 2026-08-31.
- Macro Event V3 observations: 21 total (Employment 8, Inflation 8, FOMC 5).
- Frozen strong states: 3.
- Frozen non-strong states: 18.
- Market Shock identity: MARKET_SHOCK_CHALLENGER_V3 at source SHA 12edc11e42b58d9c91fb587efdda9269cae4c91a.
- XAU source: Twelve Data 5-minute governed research cache.

## Preregistered all-event enrichment
- Macro event windows with Market Shock: 5 / 21 = 23.81%.
- Matched control windows with Market Shock: 1 / 84 = 1.19%.
- Risk ratio: 20.0.
- Odds ratio: 25.9375.
- One-sided Fisher exact p = 0.00109584.
- Diagnostic support: YES.

## Score magnitude association
- Shock-overlap events: n=5; median |Macro score| = 1.68623.
- Non-overlap events: n=16; median |Macro score| = 0.34327.
- Mann-Whitney U = 63.0.
- AUC-equivalent = 0.7875.
- One-sided p = 0.0315076.
- Diagnostic support: YES.
- Interpretation: larger absolute Macro Event scores tend to be associated with Market Shock overlap in 2026 YTD. This does not define a new threshold.

## Direction concordance
- Overlapping event windows with nonzero Macro score: 5.
- Macro score sign and Market Shock direction concordant: 5 / 5 = 100%.
- Exact one-sided binomial p = 0.03125.

## Continuation is NOT proven
- Post-shock continuation in Macro-score direction: 2 / 5 = 40%.
- Median signed log return to release+30m = -0.00007375.
- Therefore the joint layer is better interpreted as shock/context confirmation, not a directional continuation forecast.

## Frozen strong vs non-strong
### STRONG
- Events: 3.
- Market Shock overlaps: 3 / 3 = 100%.
- Direction concordance: 3 / 3.

### NON_STRONG
- Events: 18.
- Market Shock overlaps: 2 / 18 = 11.11%.
- Direction concordance among overlaps: 2 / 2.
- Matched controls for these 18 events: 1 / 72 shocks.
- Post-hoc descriptive Fisher one-sided p for non-strong vs their controls ≈ 0.1007; this is borderline and was not a preregistered primary gate.

The two non-strong overlaps were:
1. 2026-07-02 Employment: score +0.004015 (essentially macro-neutral), Market Shock INSTANT_JUMP upward; direction sign mechanically concordant but Macro score magnitude is near zero, so this event must NOT be used as evidence for a lower threshold.
2. 2026-08-07 Employment: score +0.650824, Market Shock INSTANT_JUMP upward; direction concordant.

## Family descriptive
- FOMC: 2 / 5 event windows overlapped Market Shock; both direction-concordant.
- Employment: 2 / 8 overlapped; both direction-concordant; both were frozen non-strong.
- Inflation: 1 / 8 overlapped; direction-concordant.

## Interpretation lock
1. The current frozen strong gate is highly selective and informative in 2026 YTD: 3/3 strong events overlapped Market Shock.
2. Some information exists below the strong gate, but the non-strong subset alone is not yet statistically convincing; one of the two overlaps has a Macro score essentially equal to zero.
3. The continuous magnitude result is more defensible than lowering the frozen threshold: larger |Macro score| is associated with greater Market Shock overlap, but no new cutoff may be selected from these outcomes.
4. The joint layer confirms/labels shocks; it does not prove 30-minute directional continuation.
5. Market Shock V3 standalone remains FAILED_RESEARCH_GATES_NOT_PROMOTED. No production or merge authority is created by this result.
