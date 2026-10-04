# GOLD H3 — RULEFLOW V3-TG PRE-2025 BACKCAST PREREG

**Date:** 2026-10-04  
**Status:** FIXED-RULE HISTORICAL BACKCAST  
**Years:** 2023 and 2024  
**Purpose:** test the already-frozen RuleFlow V3-TG rule on earlier years without changing any threshold, sign rule, or action logic.

## Binding rule identity

The tested rule is exactly RuleFlow V3-TG:

1. Build the V2 expectation hotspot from the last three changes in event-day U.S. 2-year Treasury yield:
   - conflict_ratio > 0.359
   - current_dominance > 0.294
   - current_dominance <= 0.502
2. V2 causal gate:
   - internal susceptibility >= 0.60 OR
   - macro breadth >= 0.30
3. Candidate only if HELIOS V5-DCE follows event-day momentum.
4. V3-TG veto:
   - 60-origin corr(Gold daily return, Nasdaq return) > 0
   - 60-origin corr(Gold daily return, VIX return) < 0
   - at least one of those two Pearson correlations has two-sided p < 0.05
   - if so: veto FLIP and KEEP V5.
5. Otherwise preserve the V2 FLIP.

No threshold or sign change is permitted after seeing 2023-2024 outcomes.

## Event universe

Same six macro/Fed families used in RuleFlow discovery/stress:
- ADP
- NFP
- JOLTS
- CPI
- Core PCE / PCE
- FOMC

Same-day releases are merged to one event date because the expectation state uses one event-day 2-year yield observation.

## 2-year yield source

FRED DGS2, daily U.S. 2-year Treasury constant maturity yield.  
For a release date with no DGS2 observation because the market is closed, use the latest prior available DGS2 value and flag the row as carried-forward.

## Existing model/data sources

- HELIOS V5-DCE predictions: frozen clean file
- H3 structural state: frozen RIFT panel
- macro topology: frozen DIVERGE panel
- target/outcome: existing H3 frozen targets

## Evaluation

Report separately for 2023 and 2024:
- event rows
- hotspots
- gated hotspots
- V2 actions
- V3-TG surviving actions
- rescue / broken / net
- precision
- V5 baseline full-year accuracy
- V5 + V3-TG full-year accuracy
- balanced accuracy
- every action date and topology state

Also report combined 2023-2024.

## Scientific status

This is stronger than the 2025-2026 diagnostic because these years were not used to discover the topology veto. It is still a historical backcast, not prospective validation. Event-date reconstruction and DGS2 sourcing must be fully logged.
