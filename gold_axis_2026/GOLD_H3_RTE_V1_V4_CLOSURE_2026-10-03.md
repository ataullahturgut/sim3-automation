# GOLD H3 — RTE REVERSAL TRANSITION ENGINE V1–V4 CLOSURE

**Date:** 2026-10-03  
**Final status:** **NO PROMOTION / 2026 HOLDOUT UNOPENED**

## Objective

Build an original reversal-rescue architecture for HELIOS V5-DCE rather than copying another forecasting model.

Core diagnosis entering the batch:
- V5 clean 2026 champion accuracy remains 63.35%;
- residual error is dominated by missed reversals;
- current OPAL candidate generation misses most of those reversals.

The RTE family therefore targeted the exact question:
> when V5 is following prevailing 12h momentum, should that continuation call be overturned?

## V1 — matched-counterfactual transition engine

Architecture:
- V5-conditioned rescue target;
- origin-safe matched continuation twins;
- CME Gold futures volume;
- CME Gold CALL/PUT volume asymmetry;
- path-state features;
- sequential latent transition tension.

CME source coverage:
- 2022: 100%
- 2023: 100%
- 2024: 100%
- 2025: 100%
- 2026 through Sep-30: 100%

DEV 2023-2024:
- pRTE 0.55: 27 rescue / 44 broken / net -17
- 0.60: 26 / 34 / -8
- 0.65: 20 / 25 / -5
- 0.70: 14 / 18 / -4
- 0.75: 13 / 13 / 0
- 0.80: 11 / 11 / 0

Status:
`NO_ELIGIBLE_RTE_THRESHOLD`.

## V1 diagnostic insight

Among high-tension DEV candidates, broken calls were disproportionately sharp probability/tension spikes.

At pRTE >= 0.75:
- rescued median ΔpRTE ≈ +0.004
- broken median ΔpRTE ≈ +0.175
- slow-burn tension therefore looked more selective than sudden spikes.

This generated V2.

## V2 / V2B — slow-burn transition

Rule family:
- prior pRTE >= 0.60
- ΔpRTE <= 0.05
- high current pRTE

2023 standalone design was invalid because origin-safe warm-up left only 12 eligible predictions. Period allocation was corrected without changing the rule family.

2023-2024 development:
- 11 candidates
- 9 rescued
- 2 broken
- net +7
- precision 81.82%

This was the first strong RTE mechanism result.

Untouched 2025 confirmation:
- 1 candidate
- 0 rescued
- 1 broken
- net -1
- confirmation FAIL

Therefore 2026 stayed unopened.

## 2025 failed-confirmation diagnosis

2025 did not fail because pRTE probabilities collapsed:
- q75 pRTE ≈ 0.689
- q90 ≈ 0.792
- 31 origins >= 0.75

Instead the slow-burn morphology itself changed.

2025 reversal-vs-continuation separation was strongest in:
- signed Gold options pressure against momentum: SMD ≈ +0.39
- pRTE: +0.35
- pInst: +0.34

This motivated an option-confirmed transition cascade.

## V3 — option-confirmed transition cascade

Candidate:
- pRTE >= q
- pInst >= 0.50
- signed Gold CALL/PUT volume pressure against current momentum > 0

Development robustness across 2024 H1, 2024 H2, 2025 H1, 2025 H2:

q=0.60:
- aggregate net 0
- precision 50.0%
- block nets: -1, +1, +5, -5

q=0.65:
- aggregate net +2
- precision 51.72%
- block nets: 0, +1, +5, -4

q=0.70:
- aggregate net +2
- precision 52.38%
- block nets: +1, -3, +5, -1

No rule passed block robustness.

Status:
`NO_ROBUST_RTE_V3_RULE`.

2026 remained unopened.

## V4 — material reversal target

Target was reformulated rather than adding another router:
`material_reversal = V5 missed reversal AND abs(H3 return) >= 1.0%`.

Best high-threshold result:
q=0.70:
- 28 candidates
- 15 rescue
- 13 broken
- net +2
- precision 53.57%
- block nets: +3, 0, +4, -5

Again the principal breakdown occurred in 2025 H2.

Status:
`NO_ROBUST_RTE_V4_RULE`.

2026 remained unopened.

## Cross-version conclusion

The batch falsifies several overly simple explanations:
- reversal failure is not solved by aggregate futures Volume/OI;
- it is not solved by path exhaustion alone;
- it is not solved by counterfactual similarity alone;
- it is not solved by static Gold options call/put pressure alone;
- it is not solved by targeting only large reversals.

The strongest RTE development result was real but non-transportable:
- slow-burn V2B: 9 rescue / 2 broken / +7 net / 81.82% precision on 2023-2024;
- failed immediately in 2025.

Across V3 and V4, 2025 H1 is consistently favorable while 2025 H2 is consistently harmful.

This is now evidence that the remaining reversal problem is **state/regime conditional**, not merely a missing scalar threshold.

## Binding next research direction

Do not continue threshold-searching on RTE V1-V4.

Next architecture should be a **Regime-Conditional Reversal Transition Engine**:

1. construct regime state using only origin-available variables;
2. regime assignment must be unsupervised or learned only from pre-2026 development;
3. identify which regime supports slow-burn reversal morphology and which supports option-pressure morphology;
4. allow a specialist to act only inside regimes where its historical causal/mechanistic edge is stable;
5. preserve 2026 as unopened final holdout until the regime router passes 2024-2025 block robustness.

The most important immediate research question is:
> what observable origin-state changed between 2025 H1 and 2025 H2 that caused all reversal-rescue rules to invert?

## Governance

- No RTE version opened 2026 outcome metrics.
- No 2026 threshold tuning occurred.
- HELIOS V5-DCE remains binding.
- CLEAN_H3_PROSPECTIVE_V1 remains untouched.
