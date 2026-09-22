# GOLD CONTROL — SQRT × UP ROUTER V2 COUNTERSIGN VETO V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `SQRT_UP_ROUTER_V2_COUNTERSIGN_VETO_V1_RESEARCH`  
**Parent risk model:** frozen SQRT-HAR-DR annual-origin downside-risk alarm  
**Verifier:** frozen `UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH`  
**Runtime authority:** NONE  
**Production DB writes:** FORBIDDEN

## 1. Question

When SQRT-HAR-DR raises a downside-risk alarm, can the already-frozen UP Expert Router V2 safely suppress false forced-DOWN interpretations?

A veto means `NO-DOWN / SUPPRESSED`. It is not a BUY signal and not an unconditional UP forecast.

## 2. Frozen verifier

No Router V2 rule may change in this study.

Direct experts:
- TTSM-S2
- TTSM-S1
- Bonato AR1_RM QBoost h=1
- AR1_RM_LOGIT
- RM_LOGIT

Legacy competence context:
- FAST_UP = FAST ROBUST_UP
- SLOW_UP = SLOW ROBUST_UP
- MONTHLY_UP = MONTHLY_DIRECTION_3M UP
- CONSENSUS_UP iff at least 2 of 3 are UP; otherwise NON_CONSENSUS_UP

Competence uses matured historical outcomes only, same-bucket history when expert UP support >=30, otherwise frozen global fallback, then V1 eligibility and one-sided 90% Wilson-LCB ranking.

Verifier emits either:
- `UP`
- `ABSTAIN`

Only `UP` can veto SQRT.

## 3. Evaluation periods

Primary pre-2025 validation:
- **2024 only**, because Router V2 uses 2023 as competence formation and 2024 as its first frozen validation year.

Locked stress:
- **2025**, unchanged.

No 2025 result may alter Router V2 or this veto rule.

## 4. Exact alignment

Join by exact `origin_date`.

Required:
- Router target_date == SQRT target_date;
- actual next-day direction sign identical;
- no nearest-date matching;
- no forward fill;
- no interpolation.

Any mismatch is reported and excluded.

## 5. Parent definitions

On each SQRT alarm:
- actual DOWN iff `target_close_return < 0`;
- actual UP otherwise.

Baseline forced-DOWN anatomy:
- TP = SQRT alarm and actual DOWN;
- FP = SQRT alarm and actual UP.

Router V2 veto:
- if Router V2 emits UP on the same origin, suppress the forced-DOWN call;
- otherwise retain the forced-DOWN call.

## 6. Metrics

For 2024 primary and 2025 stress:

- SQRT alarm count;
- exact-overlap alarm count;
- baseline TP / FP;
- baseline forced-DOWN precision;
- router-UP veto count;
- GOOD_VETO = veto on actual UP;
- BAD_VETO = veto on actual DOWN;
- veto precision = GOOD_VETO / veto count;
- false-alarm reduction = GOOD_VETO / baseline FP;
- true-DOWN retention = (TP - BAD_VETO) / TP;
- remaining forced-DOWN precision;
- precision change versus no-veto baseline;
- net veto benefit = GOOD_VETO - BAD_VETO.

## 7. Promising gate

Primary 2024 is `PROMISING` only if all hold:

1. at least 3 vetoes;
2. veto precision >= 0.65;
3. false-alarm reduction >= 0.25;
4. true-DOWN retention >= 0.80;
5. remaining forced-DOWN precision improves by >= +0.05 absolute.

2025 cannot rescue a failed 2024 gate.

If 2024 passes, 2025 transport is considered supportive only if:
- veto precision >= 0.60;
- true-DOWN retention >= 0.75;
- remaining forced-DOWN precision does not fall below baseline.

## 8. Forbidden actions

Do not:
- change Router V2 thresholds;
- change legacy consensus definition;
- add GVZ/Macro/Event/Emergency overlays;
- tune on SQRT alarm subset;
- optimize a new Boolean rule;
- use 2025 to rescue 2024;
- reinterpret veto as UP trade;
- make production/runtime changes.

## 9. Governance

- no random split;
- no 2025 tuning;
- no production writes;
- no runtime promotion.
