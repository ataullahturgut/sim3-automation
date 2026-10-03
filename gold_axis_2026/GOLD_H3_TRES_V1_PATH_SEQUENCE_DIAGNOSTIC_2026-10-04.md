# TRES-H3 V1 — POST-STAGE2 PATH-SEQUENCE DIAGNOSTIC

**Date:** 2026-10-04  
**Status:** diagnostic after TRES V1 Stage-2 meta-model failure; historical development evidence only.

## Why this diagnostic was run

Stage 1 showed a stable origin-time signal for the first-passage REVERSAL event, but Stage 2 showed that passing those probabilities through a second V5 error-risk logistic model destroyed rather than improved discrimination.

Inspection of Stage-0 paths reveals a more basic abstraction problem: the Stage-1 competing-risk model is **absorbing at the first barrier hit**. Real H3 reversals can first move strongly with momentum and only then reverse.

## Fixed 1.00×sigma20 path motifs

Using the already-frozen Stage-0 barrier with no parameter change:

- C_ONLY: 527 origins; terminal reversal **6.45%**
- R_ONLY: 199 origins; terminal reversal **99.50%**
- C_THEN_R: 23 origins; terminal reversal **95.65%**
- R_THEN_C: 6 origins; terminal reversal **0.00%**
- NONE: 274 origins; terminal reversal **46.35%**

This shows that **order matters**. An absorbing first-passage label misclassifies the economically important C→R transition as continuation.

## Last decisive barrier state

At h=1,2,3 independently classify the momentum-normalized cumulative return as:
- C if g_h >= +B
- R if g_h <= -B
- N otherwise.

The final path-state is the most recent non-N decisive barrier observed by H3:

- **CONTINUATION_LAST**: n=533; terminal reversal **6.38%**
- **REVERSAL_LAST**: n=222; terminal reversal **99.10%**
- **NONE / unresolved**: n=274; terminal reversal **46.35%**

Representative sequence counts:

CONTINUATION_LAST:
- CCC 168
- NCC 127
- NNC 95
- CNN 47
- CCN 39
- NCN 38
- CNC 13
- NRC 3

REVERSAL_LAST:
- NRR 83
- NNR 62
- NRN 29
- RRR 19
- CNR 9
- NCR 7
- RRN 5
- CRR 5

NONE:
- NNN 274

## Binding interpretation

The correct next representation is not an absorbing first-event competing risk.

A stronger path target is a three-state **last decisive path state**:

1. REVERSAL_LAST
2. CONTINUATION_LAST
3. UNRESOLVED

This state is almost deterministically related to terminal H3 direction when a decisive barrier occurs, while UNRESOLVED explicitly carries ambiguity.

It also has a natural uncertainty interpretation:
- positive/reversal membership = P(REVERSAL_LAST)
- negative/continuation membership = P(CONTINUATION_LAST)
- neutral membership = P(UNRESOLVED)

This provides a principled bridge to Picture / Neutrosophic / fuzzy confidence governance without inventing arbitrary membership functions.
