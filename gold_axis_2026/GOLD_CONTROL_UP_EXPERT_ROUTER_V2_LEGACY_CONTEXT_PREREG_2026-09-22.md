# GOLD CONTROL — UP EXPERT ROUTER V2 LEGACY-CONTEXT PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH`  
**Parent router:** `UP_EXPERT_ROUTER_V1_RESEARCH`  
**Legacy audit:** `LEGACY12_UP_INCLUSION_AUDIT_V1_RESEARCH`  
**Runtime authority:** NONE  
**Production DB writes:** FORBIDDEN

## 1. Research question

Can the original Gold Control legacy direction/context layer improve the competence selection of the modern daily UP experts without converting legacy context engines into equal daily votes?

## 2. Direct daily UP expert pool

The direct expert pool is unchanged from Router V1:

1. TTSM_S2
2. TTSM_S1
3. BONATO_AR1_RM_QBOOST_H1
4. AR1_RM_LOGIT
5. RM_LOGIT

## 3. Legacy context included

The following original-engine states are reconstructed with frozen rules on the exact same daily-close axis:

- FAST_UP = FAST state == ROBUST_UP
- SLOW_UP = SLOW state == ROBUST_UP
- MONTHLY_UP = MONTHLY_DIRECTION_3M == UP

Define:
- `legacy_up_count = FAST_UP + SLOW_UP + MONTHLY_UP`
- `legacy_bucket = CONSENSUS_UP` iff legacy_up_count >= 2, else `NON_CONSENSUS_UP`.

The legacy states do not emit the router's final UP prediction by themselves. They only condition historical competence.

Other original engines remain role-preserved:
- CAUSAL_PATCH / VW_MIDAS_MSVR_SUCCESSOR_V1 / MOMENTUM_3M = strategic monthly priors only;
- MACRO_EVENT_SUCCESSOR_V2 = event-time specialist only;
- GVZ_RISK = risk context only;
- RANDOM_WALK = benchmark only;
- BOCPD_RETURN_SUCCESSOR_V1 = blocked where daily historical origin state is unavailable;
- EMERGENCY_LEVEL / EMERGENCY_REVERSAL = NOT_PROVEN as independent daily direction experts.

They are retained in the architecture but are not forced into this daily score when pre-2025 comparable evidence is absent.

## 4. Time split

- 2023: development/history formation.
- 2024: frozen validation.
- 2025: locked retrospective challenge.

No rule may change after 2024 scoring and 2025 cannot rescue a failed 2024 gate.

## 5. Causal competence

For each active direct expert j at origin t:

1. collect only matured prior rows;
2. select prior rows with the same `legacy_bucket`;
3. compute expert-j UP-call count, true-UP count, false-UP count, UP precision and false-UP FPR within that bucket;
4. if bucket-specific UP-call count < 30, fall back to the expert's global matured history;
5. apply Router V1 eligibility:
   - historical UP calls >= 30;
   - historical UP precision > 0.50;
   - historical false-UP FPR < 0.50;
6. rank eligible active experts by one-sided 90% Wilson lower bound on UP precision;
7. tie-break lower false-UP FPR, then higher raw UP precision, then fixed identity order:
   TTSM_S2 > TTSM_S1 > BONATO_AR1_RM_QBOOST_H1 > AR1_RM_LOGIT > RM_LOGIT.

If no direct expert is eligible, output ABSTAIN.

## 6. No new tuning

Forbidden:
- threshold search;
- changing the >=2 legacy consensus definition after scoring;
- changing the 30-call bucket support threshold;
- allowing FAST/SLOW/MONTHLY to become direct votes after seeing results;
- 2025-based rescue;
- adding GVZ/Macro/Emergency conditionals post hoc.

## 7. Benchmarks

Compare V2 against:
1. fixed 2023-selected RM_LOGIT benchmark;
2. frozen Router V1 2024/2025 metrics.

## 8. Metrics

For 2024 and 2025:
- UP outputs;
- coverage;
- true UP / false UP;
- UP precision;
- false-UP FPR;
- actual-UP recall;
- selected-expert counts;
- abstention;
- results by legacy bucket.

## 9. Promising gate

V2 is PROMISING only if 2024 satisfies all:

1. UP outputs >= 20;
2. coverage >= 0.10;
3. UP precision >= fixed RM_LOGIT precision + 0.03 absolute;
4. false-UP FPR <= fixed RM_LOGIT FPR - 0.05 absolute;
5. UP precision >= Router V1 precision;
6. false-UP FPR <= Router V1 false-UP FPR.

2025 transport is diagnostic only.

## 10. Governance

- no random split;
- no 2025 tuning;
- no production writes;
- no runtime promotion;
- role contracts preserved.
