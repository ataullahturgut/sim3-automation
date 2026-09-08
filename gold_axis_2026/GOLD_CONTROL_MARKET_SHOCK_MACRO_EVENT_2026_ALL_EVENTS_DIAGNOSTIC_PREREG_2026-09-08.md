# GOLD CONTROL — Market Shock + Macro Event 2026 All-Events Diagnostic Prereg

Date: 2026-09-08
Branch: gold-control-market-shock-macro-event-joint-audit-v1
Evidence class: HISTORICAL_RESEARCH_AUDIT
Production authority: false

## Purpose
Evaluate whether information exists below the frozen Macro Event V3 strong-state gate without changing any frozen Macro Event or Market Shock threshold.

## Frozen identities
- Market Shock: MARKET_SHOCK_CHALLENGER_V3 at source SHA 12edc11e42b58d9c91fb587efdda9269cae4c91a.
- Macro Event: MACRO_EVENT_SUCCESSOR_V3 governed score series.
- XAU: existing governed Twelve Data 5-minute research cache.
- Period: 2026-01-01 through 2026-08-31 only.

## No-change lock
This diagnostic MUST NOT:
- change the Macro Event strong threshold or breadth rule;
- create a new threshold from 2026 outcomes;
- alter Market Shock thresholds or episodes;
- promote either engine;
- write forecasts, decisions, or production state.

## Population
Use all 2026 YTD Macro Event V3 score observations for Employment, Inflation, and FOMC. Retain the existing frozen state label (strong vs MACRO_MIXED_OR_SMALL) but analyze score magnitude continuously.

## Event matching
For each Macro Event release timestamp, test whether frozen Market Shock V3 emits a shock within [release, release+10m]. Use the first shock in that window. Preserve sign of macro score and shock direction.

## Matched controls
For each macro release, attempt up to four calendar/time-of-day matched control timestamps from offsets {-7,+7,-14,+14,-21,+21,-28,+28} days, excluding timestamps within +/-60 minutes of any Macro Event. Use only controls with required XAU coverage.

## Primary diagnostics
1. ALL-EVENT ENRICHMENT: Compare Market Shock incidence across all 2026 macro-event windows with matched controls using one-sided Fisher exact test. Report risk ratio and odds ratio. No binary acceptance claim if controls are structurally zero without accompanying exact p-value.
2. SCORE-MAGNITUDE ASSOCIATION: Compare abs(Macro Event score) between event windows with vs without Market Shock using one-sided Mann-Whitney U (alternative: shock-overlap events have larger absolute scores). Report rank-biserial/AUC-equivalent U/(n1*n0). This is diagnostic only; no threshold selection.
3. DIRECTION CONCORDANCE: Among event windows with Market Shock and non-zero macro score, compare sign(score) vs shock direction. Report exact one-sided binomial p against 0.5.
4. POST-SHOCK CONTINUATION: Diagnostic only. From first overlapping shock to latest XAU close <= release+30m, compute signed log return in macro-score direction. Report hit rate and median; do not use this to redefine the detector.
5. FROZEN-STATE STRATIFICATION: Report results separately for frozen strong states and MACRO_MIXED_OR_SMALL. This is descriptive; no new cutoff.
6. FAMILY DESCRIPTIVE: Employment, Inflation, FOMC counts, overlaps, concordance.

## Interpretation
- Evidence that all-event windows are enriched vs controls means scheduled macro releases carry shock context beyond only the strong subset.
- Evidence that abs(score) is larger in overlap events supports a graded, continuous-strength interpretation.
- Failure of score-magnitude association means the current continuous Macro score does not rank Market Shock incidence well in 2026, even if the strong subset is informative.
- Direction concordance and continuation are separate properties; shock detection/confirmation must not be misrepresented as a directional forecast.
- Results are historical research only and cannot rehabilitate Market Shock V3 standalone or authorize production.

## Literature rationale frozen before outcome inspection
- Elder, Miao & Ramchander (Journal of Banking & Finance, 2012): US macroeconomic surprises have swift/significant intraday effects on metal futures; realized volatility and volume increase around news.
- Sobti, Sehgal & Ilango (International Review of Financial Analysis, 2021): larger news-surprise size and forecast dispersion have stronger effects on gold price discovery; effects are asymmetric/state-dependent.
- Sobti (International Review of Financial Analysis, 2025): US macroeconomic news predicts a material share of intraday gold jumps; FOMC is a dominant news surprise.
