# GOLD H3 RULEFLOW V3-TG — TOPOLOGY-GATED SUCCESSOR PREREG

**Date:** 2026-10-04  
**Status:** diagnostic successor freeze; NOT validated  
**Parent:** RuleFlow V2 closure commit `7548bbe2174d8baadf18df937e48c841c2223bd9`

## Why V3 exists

RuleFlow V2 failed the frozen 2026 Q2-Q3 stress with 4 actions, 0 rescue, 4 broken. Root-cause analysis showed that the absolute-correlation macro-breadth feature discarded the sign/topology of Gold's risk relationship.

The successor therefore preserves every V2 expectation-hotspot and internal-susceptibility rule and changes only the treatment of the Gold-Nasdaq/VIX topology.

## Frozen V2 core retained

Expectation hotspot:
- conflict_ratio > 0.359
- current_dominance > 0.294
- current_dominance <= 0.502

V2 causal gate:
- internal susceptibility >= 0.60
- OR macro breadth >= 0.30

Action eligibility before topology:
- hotspot = True
- V2 causal gate = True
- V5 follows event-day momentum

## New topology veto

Using the same `GOLD_H3_DIVERGE_PROXY_V1_PANEL_2026-10-03.csv` and the same origin-safe rolling history, calculate prior-60-origin Pearson correlations:
- r_GN = corr(Gold daily return, Nasdaq return)
- r_GV = corr(Gold daily return, VIX return)

Define **STRONG_PRO_RISK** iff all are true:
1. r_GN > 0
2. r_GV < 0
3. at least one of the two Pearson correlations is statistically different from zero at two-sided alpha = 0.05.

For n=60 complete observations, the corresponding absolute-r critical value is approximately 0.2542. If effective n differs because of missing values, use the exact Pearson p-value for that n.

### Decision

- If V2 would FLIP and topology = STRONG_PRO_RISK -> **VETO / KEEP V5**
- Otherwise -> preserve the frozen V2 decision exactly.

This is deliberately a veto, not a reverse rule. A pro-risk state does not authorize an opposite-direction trade by itself.

## Why not require 20d + 60d sign agreement

A strict two-window topology confirmation was considered first:
- SAFE only if both 20d and 60d show Gold-NDX < 0 and Gold-VIX > 0;
- PRO-RISK only if both 20d and 60d show Gold-NDX > 0 and Gold-VIX < 0;
- otherwise TRANSITION.

This is retained only as a sensitivity analysis. It is not the binding V3 rule because it can suppress valid reversals during genuine topology transitions.

## Required diagnostic report

Replay the already-consumed evidence only as diagnosis:
- 2025 discovery
- 2026 Q1 frozen stress
- 2026 Q2-Q3 consumed stress

Report:
- V2 actions / rescue / broken / net / precision
- V3 actions / rescue / broken / net / precision
- rescue retention
- broken suppression
- topology-stratified hotspot reversal rate
- strict 20d+60d sensitivity
- per-action rolling correlations and p-values

No diagnostic result may be relabeled as out-of-sample validation.

## Prospective rule

The topology veto is frozen by this document. The first genuinely unseen evidence must come from origins after the existing clean prospective cutoff of **2026-10-05**. No threshold or sign rule may be changed in response to those outcomes without opening a new challenger identity.
