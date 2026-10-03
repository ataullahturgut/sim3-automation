# HELIOS V6 — CANDIDATE-UNION ADMISSIBILITY RESULT

**Date:** 2026-10-03  
**Branch:** `gold-h3-helios-v6-admissibility-20261003`  
**Status:** **NO_ADMISSIBLE_EXPANSION**

## Purpose

Stage 5 asks whether the preregistered reversal specialists produce a new high-recall candidate universe that can legitimately be unioned with OPAL before any HELIOS V6 router is fitted.

This is an admissibility gate. A specialist that is source-blocked or fails its frozen DEV gate cannot be added merely because a retrospective union might look attractive.

## Inputs and frozen outcomes

| Specialist | Frozen stage result | Admissible to V6 union? | Reason |
|---|---|---|---|
| OPAL | Existing validated specialist | YES | Current candidate universe / incumbent |
| FLOW-H3 full Volume+OI | BLOCKED_EXTERNAL_HISTORICAL_OI_ACCESS | NO | Official historical FINAL GC OI unavailable |
| FLOW-VOL-H3 ablation | NO_ELIGIBLE_FLOW_VOL_THRESHOLD | NO | DEV precision/candidate-rate gate failed |
| SKEW-H3 | BLOCKED_EXTERNAL_CVOL_ENTITLEMENT | NO | Historical Gold CVOL UpVar/DnVar/Skew unavailable |
| HAZARD-H3 | NO_ELIGIBLE_HAZARD_THRESHOLD | NO | DEV precision/candidate-rate gate failed |
| DIVERGE-H3 exact | SOURCE_BLOCKED | NO | Exact-source transport unavailable in runner |
| DIVERGE-PROXY-H3 | NO_ELIGIBLE_DIVERGE_THRESHOLD | NO | DEV precision/candidate-rate gate failed |

## Decision

No new specialist passed its preregistered admission rule.

Therefore the only admissible union is:

`OPAL ∪ {} = OPAL`

That is not a new candidate universe and cannot be called HELIOS V6.

Binding result:

> **HELIOS V6 is NOT FIT and NOT SCORED. Status = NO_ADMISSIBLE_EXPANSION.**

No 2025 or 2026 result is used to relax any failed threshold or source requirement.

## Consequence for the research hypothesis

The research diagnosis remains valid: V5's remaining 2026 error is dominated by missed reversals and current OPAL candidate recall is the structural bottleneck.

However the first preregistered candidate-expansion batch did not deliver an admissible new channel in the current environment:
- two highest-information external channels are blocked by licensed/entitled history;
- the three testable reduced/internal representations did not meet the required selectivity on DEV.

This is a negative but useful result. It prevents false progress through post-hoc union tuning.

## V5 binding state

HELIOS V5-DCE remains unchanged:
- clean 2026 accuracy: 63.35%
- clean 2026 balanced accuracy: 63.76%
- clean 2026 Brier: 0.2425
- clean 2025-2026 accuracy: 65.15%

No new V6 score is reported.
