# GOLD CONTROL — FROZEN UP CASCADE 2026 REPLAY AUTHORITY

**Date:** 2026-10-02  
**Status:** FROZEN BEFORE REPLAY  
**Purpose:** Evaluate the already-frozen UP architecture on 2026 historical stress without changing any rule.

## Components

1. Frozen Primary UP Verifier V2
   - identity: `UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH`
   - direct experts: TTSM-S2, TTSM-S1, Bonato AR1_RM QBoost h=1, AR1_RM_LOGIT, RM_LOGIT
   - legacy context: FAST_UP, SLOW_UP, MONTHLY_DIRECTION_3M_UP
   - same eligibility, Wilson-LCB ranking, bucket support and tie-break as frozen V2.

2. Frozen One-Sided UP-2 Logit V1
   - identity: `RESIDUAL_ONE_SIDED_UP2_LOGIT_V1_RESEARCH`
   - exact 9-feature vector
   - L2 LogisticRegression C=1.0
   - exact prequential DOWN-Q80 threshold algorithm
   - operates only on `SQRT HIGH RISK + Primary Router ABSTAIN`.

## 2026 chronology

Primary Router competence history:
- continue the frozen 2024 -> 2025 causal competence path into 2026;
- 2026 rows update competence only after their own matured target is known, exactly as the frozen causal algorithm does.

UP-2:
- train for 2026 on route-consistent residual rows strictly before 2026:
  - external 2020-2021 residual history;
  - governed 2022-2025 residual history.
- compute the 2026 threshold from strictly prequential historical DOWN scores only.
- no 2026 label enters training or threshold calibration.

## Data horizon

Use the frozen SQRT parent panel through its last available 2026 target date (currently 2026-08-31) and the same governed 5-minute cache/provider/clock used by the frozen direction research.

## Integrity requirements

Before accepting 2026 output, the replay must reproduce frozen historical facts:

Primary Router V2:
- 2024: 42 UP calls = 26 true + 16 false
- 2025: 37 UP calls = 27 true + 10 false.

Primary residual:
- 2022-2024 pooled: n=26 = 13 UP + 13 DOWN
- 2025: n=74 = 35 UP + 39 DOWN.

UP-2 historical scoring:
- 2022-2024 pooled: 11 calls = 8 true + 3 false
- 2025: 25 calls = 13 true + 12 false.

Any mismatch blocks interpretation.

## 2026 required metrics

Primary UP V2 standalone:
- eligible timeline n
- UP outputs
- true UP / false UP
- UP precision
- call-error rate
- false-UP FPR
- actual-UP recall
- coverage
- selected-expert counts.

SQRT + Primary residual:
- 2026 SQRT alarms
- Router-UP intersection
- residual n and UP/DOWN composition.

UP-2 on residual:
- calls
- true UP / false UP
- precision
- missed-UP recall
- false-UP FPR
- coverage
- AUC
- Brier
- frozen 2026 tau.

Combined positive-UP evidence inside the SQRT route:
- Primary-UP positives + UP-2 positives
- true/false counts
- precision
- false alarm per emitted UP call.

## Governance

- 2026 is retrospective stress, not model-selection evidence.
- no feature, threshold, expert membership, ranking rule, history support, or model parameter changes.
- no production writes.
- no runtime promotion.
