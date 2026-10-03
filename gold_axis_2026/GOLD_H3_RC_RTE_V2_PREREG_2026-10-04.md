# RC-RTE-H3 V2 — SHADOW CREDIBILITY CONTROLLER PREREGISTRATION

**Date:** 2026-10-04  
**Identity:** `RC_RTE_SHADOW_H3_V2`  
**Branch:** `gold-h3-rc-rte-v2-20261004`  
**Status:** **PREREGISTERED BEFORE 2026 OPENING**

## 1. Motivation

RC-RTE V1 showed that static regime enablement can become stale within a semester.

2025 H2 chronology:
- pre-H2 regime 0 had historical proposal precision 70.0%;
- pre-H2 regime 2 had historical proposal precision 60.7%;
- nevertheless H2 static gating produced 6 rescue / 14 broken / net -8.

The degradation became observable from matured proposal outcomes early in the block.

V2 therefore adds an origin-safe, self-extinguishing credibility layer.

## 2. Base regime engine

Unchanged from RC-RTE V1:
- four custom origin-state axes;
- KMeans K=3;
- regime map fitted on matured pre-block data only;
- frozen proposal union = SB OR OPT OR MAT;
- static regime enabled if training proposal support >=8, precision >=0.55, net rescue >0.

No state axis, cluster count or specialist threshold changes.

## 3. Shadow proposal outcomes

Every proposal is tracked whether or not RC-RTE acts on it.

For a proposal:
- shadow utility = +1 if flipping V5 would have corrected the direction;
- shadow utility = -1 if flipping V5 would have broken a correct V5 call.

A shadow utility may enter credibility memory only when:
`target_end_date_h3 <= current feature_cutoff_date`.

Thus no unresolved future outcome can affect the current decision.

## 4. Dynamic credibility rule

Credibility is maintained separately for each fitted regime.

Within each sequential test block:
- before three matured in-block shadow proposals exist for a regime, use the static regime enablement state;
- once at least three matured shadow proposals exist, inspect the **last 3**;
- dynamic regime permission is ON only if last-3 net utility >= +1, i.e. at least 2 of the last 3 shadow proposals were successful;
- if last-3 net <= -1, permission is OFF;
- vetoed proposals continue to generate shadow outcomes after maturity, so a regime can re-enable if the last three shadow proposals recover to >= +1.

No other memory length or utility threshold is searched.

## 5. Sequential pre-2026 evaluation

Use the same blocks as RC-RTE V1:

- 2024 H2: fit on all eligible origins before 2024-07-01
- 2025 H1: fit on all eligible origins before 2025-01-01
- 2025 H2: fit on all eligible origins before 2025-07-01

Within each test block:
- scaler and KMeans remain fixed;
- static enablement remains fixed;
- only shadow credibility evolves origin by origin from matured proposal outcomes.

## 6. Robustness gate

Across the three sequential blocks, V2 must satisfy:
- gated candidates >=10
- net rescue >= +4
- rescue precision >=0.58
- at least 2 of 3 blocks have net rescue >0
- no block net rescue < -1
- pooled assisted accuracy > pooled V5 accuracy

Failure => `NO_ROBUST_RC_RTE_V2_RULE`; 2026 remains unopened.

## 7. 2026 final holdout

Only after robustness PASS.

Final pre-2026 fit:
- state scaler / KMeans / static regime enablement use data through 2025-12-31 only.

During 2026:
- shadow credibility updates only from proposal outcomes whose H3 target has matured by the current origin;
- no 2026 threshold or state tuning;
- the final rule is applied sequentially once.

Report:
- candidates / rate
- rescued / broken / net
- rescue precision
- eligible accuracy change
- whole-clean-2026 accuracy
- OPAL-no-candidate missed reversal coverage
- number of credibility ON/OFF transitions by regime.

## 8. Governance

2025 H2 was used to motivate this controller and is development data.

The first independent evaluation of RC-RTE V2 is 2026, and 2026 may be opened only if the full pre-2026 robustness gate passes.
