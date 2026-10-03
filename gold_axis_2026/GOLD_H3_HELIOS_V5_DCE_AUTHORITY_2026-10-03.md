# HELIOS-H3 V5-DCE — DOMINANT-EXPERT CONTRADICTION EXCEPTION AUTHORITY

**Date:** 2026-10-03  
**Identity:** `HELIOS_H3_V5_DCE_RESEARCH`  
**Parent:** `HELIOS_H3_V4_RGE_RESEARCH`  
**Status:** POST-HOC / MECHANISM-TEST RESEARCH

## 1. Problem

V4-RGE protects HELIOS V2 in 2023-2025 and opens broader OPAL only after causal non-consensus regret turns positive.
Its remaining 2026 misses show two distinct mechanisms:
1. broad regret gate can open too late for a small number of high-quality reversals;
2. after expansion is active, low-market-share rejects are mostly correctly rejected.

V5-DCE tests one narrow exception to the first problem without weakening V4's broad safety gate.

## 2. Scientific framing

The exception is treated as a **specialist / sleeping expert**:
it is awake only at a narrowly defined decision point and otherwise V4 remains unchanged.

The design also follows safe-policy-improvement logic:
default to the trusted baseline and deviate only where independent origin-safe evidence indicates a high-confidence decision point.

## 3. Frozen inputs

All inputs already exist in frozen causal ledgers:
- HELIOS macro gate;
- OPAL override;
- HELIOS consensus indicator;
- V3-GT policy-market flip share;
- AURORA active expert;
- AURORA DART posterior `prob_path_superior = Pr(PATH_GLOBAL superior to STRUCTURAL_IRIS)`;
- AURORA probability.

No current/future target information is used.

## 4. Binding DCE rule

Start from V4-RGE.

A DCE exception is allowed only when ALL are true:
1. V4 did not already route;
2. HELIOS macro gate is ACTIVE;
3. OPAL override is true;
4. HELIOS consensus candidate is false;
5. V3-GT weighted flip share > 0.50;
6. AURORA active expert is `PATH_GLOBAL`;
7. frozen `Pr(PATH_GLOBAL superior) > 0.50`.

If all conditions hold:
- flip AURORA direction;
- use mirrored AURORA probability `1 - p_AURORA`.

Otherwise:
- retain V4 probability exactly.

The posterior threshold 0.50 is the natural Bayesian majority boundary; it is not selected by historical performance.

## 5. Interpretation

This is called a dominant-expert contradiction event:
- the frozen AURORA state machine currently trusts PATH_GLOBAL;
- the frozen Bayesian disagreement posterior still judges PATH more likely superior than not;
- nevertheless the independent OPAL / game-theoretic reversal layer strongly contradicts the current call.

The hypothesis is that this rare contradiction can identify abrupt local failures of an otherwise dominant PATH regime before the slower broad-regret expansion gate opens.

This is a mechanism hypothesis, not a causal claim about markets.

## 6. Binding evaluation

Compare:
- AURORA
- HELIOS V2
- HELIOS V3-GT
- HELIOS V4-RGE
- HELIOS V5-DCE
- raw OPAL.

Report:
- accuracy;
- balanced accuracy;
- Brier;
- logloss;
- routed events;
- rescue / broken / net rescue;
- 2023, 2024, 2025, 2026 and 2025-2026.

Hard guardrail:
- V5 must not change any 2023 or 2024 call relative to V4;
- any 2025 change must be reported call-by-call rather than hidden in aggregate.

## 7. Inference

- paired circular moving-block bootstrap;
- 10,000 replicates;
- block lengths 5 and 10;
- V5 vs AURORA, V2, V3-GT and V4;
- periods 2025-2026 and 2026;
- COT-vintage clustered bootstrap for V5-routed net rescue.

## 8. Sensitivity diagnostics

Binding posterior threshold remains 0.50.
Diagnostic thresholds:
- 0.40
- 0.60
- 0.70
- 0.75
- 0.80.

Binding GT threshold remains 0.50.
Diagnostics:
- 0.60
- 0.70
- 0.80.

No sensitivity result may replace binding after seeing its performance.

## 9. Governance

V5-DCE is post-hoc mechanism research developed after historical error anatomy.
Even if historical results improve, AURORA remains the frozen prospective champion.
Operational promotion requires a separate future-origin freeze with no retrospective retuning.
