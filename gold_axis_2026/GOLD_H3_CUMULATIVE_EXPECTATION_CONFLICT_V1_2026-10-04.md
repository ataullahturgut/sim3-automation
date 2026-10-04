# GOLD H3 — CUMULATIVE EXPECTATION CONFLICT V1

**Date:** 2026-10-04  
**Status:** retrospective mechanism diagnostic; not a promotion rule.

## Question

Does Gold H3 reversal become more likely when U.S. rate expectations have been repeatedly repriced in opposite directions across consecutive major macro/Fed releases?

## Construction

Event families:
- ADP
- NFP
- JOLTS
- CPI
- PCE
- FOMC

For each event date, use the official U.S. Treasury 2-year par yield level.

Define the event-to-event 2Y step in basis points:
`step_i = 100 * (2Y_i - 2Y_(i-1))`.

Over the latest 3 event steps:

- `gross3 = sum(abs(step))`
- `net3 = sum(step)`
- `churn3 = gross3 - abs(net3)`
- `conflict_ratio = churn3 / gross3`
- `current_dominance = abs(step_i) / gross3`

Exploratory qualitative conflict flag:
- `churn3 > 0`
- `current_dominance < 0.50`

Interpretation:
recent macro releases have pushed rate expectations back and forth, and the current event is not large enough to dominate/resolve the preceding conflict.

## Results

### March-June 2025

Scored event origins: **19**  
Actual H3 reversals: **7**

Conflict flag:
- events: **13**
- reversals: **6/13 = 46.15%**

If used only when V5 still follows momentum:
- actions: **10**
- rescue: **4**
- broken: **6**
- net: **-2**
- precision: **40.0%**

Continuous separation:
- mean conflict ratio, reversal: **0.624**
- mean conflict ratio, continuation: **0.600**
- mean churn, reversal: **21.43 bp**
- mean churn, continuation: **19.33 bp**
- mean current dominance, reversal: **0.358**
- mean current dominance, continuation: **0.342**

Conclusion: essentially **no useful separation**.

### July-September 2025

Scored event origins: **17**  
Actual H3 reversals: **5**

Conflict flag:
- events: **12**
- reversals: **5/12 = 41.67%**
- all five reversals were inside the conflict state.

If used only when V5 still follows momentum:
- actions: **8**
- rescue: **5**
- broken: **3**
- net: **+2**
- precision: **62.5%**

Continuous separation:
- mean conflict ratio, reversal: **0.598**
- mean conflict ratio, continuation: **0.247**
- mean churn, reversal: **12.80 bp**
- mean churn, continuation: **5.33 bp**
- mean current dominance, reversal: **0.136**
- mean current dominance, continuation: **0.381**

Conclusion: strong H2 separation.

## July 29-August 1 episode

Official/reported macro sequence:

- **Jul 29 JOLTS:** 7.437M openings, below ~7.50M Reuters consensus -> labor-softening impulse.
- **Jul 30 ADP:** +104K vs +75K consensus -> stronger labor impulse.
- **Jul 30 FOMC:** rate held; Powell declined to signal a September cut. September cut odds fell from roughly 65% to ~50% after the meeting.
- **Jul 31 PCE:** headline/core monthly inflation +0.3%; y/y measures were firmer than expected at 2.6% headline and 2.8% core.
- **Aug 1 NFP:** +73K vs +110K consensus with very large prior-month downward revisions; September cut odds jumped from ~38% to ~81%, and the 2Y yield fell sharply.

H3 behavior:
- Jul 29: reversal, V5 missed.
- Jul 30: reversal, V5 missed.
- Jul 31: reversal, V5 missed.
- Aug 1: continuation.

Mechanistic interpretation:
the Jul 29-31 period contains unresolved, alternating labor/inflation/Fed repricing. Aug 1 is different: the employment shock is large enough to dominate the preceding disagreement and establish a new directional rate-expectation regime.

## Scientific conclusion

The cumulative-expectation idea is **not a universal reversal rule**.

It is strongly informative in Jul-Sep 2025 but almost non-informative in Mar-Jun 2025.

Therefore:
- do not promote or threshold-tune CE-CONFLICT as a standalone FLIP signal;
- do not claim the Jul-Sep result generalizes;
- retain it as a **regime-dependent state variable**.

The more important finding is that the *predictive meaning of expectation conflict changes by regime*, consistent with the earlier H1/H2 relationship-inversion diagnosis.

A successor should model whether the market is in an **expectation-fragmentation regime** before allowing CE-CONFLICT to influence reversal probability.
