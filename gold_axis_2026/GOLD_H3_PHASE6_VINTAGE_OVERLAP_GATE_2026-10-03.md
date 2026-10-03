# H3 PHASE 6 — VINTAGE / OVERLAP-AWARE EVIDENCE ACCOUNTING GATE

**Date:** 2026-10-03  
**Status:** **ENTRY_GATE_EVALUATED / NO_NEW_MULTI_SPECIALIST_EVIDENCE**

## Intended function

Phase 6 is not a forecasting model. It is an evidence-accounting layer that must prevent correlated evidence from being counted as independent.

Frozen design requirements:
- repeated OPAL events from the same COT vintage count as one evidence family;
- specialists sharing the same underlying observation family must not receive naïvely additive confidence;
- overlapping H3 outcomes must be clustered/discounted in competence evidence;
- evidence identity must include source vintage / available-as-of lineage.

## Entry condition

Phase 5 must produce at least one admissible new specialist in addition to OPAL.

Phase 5 result:
- FLOW full: blocked
- FLOW-VOL: DEV gate failed
- SKEW: blocked
- HAZARD: DEV gate failed
- DIVERGE exact: source blocked
- DIVERGE proxy: DEV gate failed
- HELIOS V6 union: NO_ADMISSIBLE_EXPANSION

## Binding result

There is no new multi-specialist evidence set to de-correlate.

Therefore:
> **Phase 6 is completed as an entry-gate result. No new evidence weights are fit.**

The vintage/overlap accounting specification remains mandatory for any future V6 resurrection. It is not abandoned; it is simply not estimable in a meaningful new multi-specialist market in this batch.

No 2026 outcome is used to choose vintage penalties, overlap discounts, cluster windows, or specialist-correlation weights.
