# Gold Control — BOCPD Return Successor V1 Risk Validation Contract

**Date:** 2026-09-04  
**Status:** `FROZEN_PRE_RESULT_RISK_VALIDATION_V1`  
**Successor:** `BOCPD_RETURN_SUCCESSOR_V1`  
**Prerequisite:** engineering replay contract and implementation are frozen; this document does not alter them.

## 1. Purpose

Engineering reproducibility is not evidence that a regime/break motor has useful decision-support content. This stage therefore evaluates the already-frozen successor state as a **risk/severity context only**.

This validation is deliberately subordinate to the project’s earlier BOCPD audit findings:

- BOCPD did not improve tactical directional-confidence validation and must not become a direction vote;
- the prior project audit found 1-month severity unsupported;
- the prior project audit treated 2–3 month downside severity as the relevant risk horizon;
- the prior Stage-4 tail definition was cumulative forward GOLD return `<= -3%`;
- no exposure action or statistical threshold tuning was authorized;
- locked replay could not be used for approval.

Those previously frozen project criteria are reused to avoid inventing a new success threshold after seeing successor alarm dates.

## 2. No model changes

This stage may not modify:

- `L=36`;
- hazard;
- NIG prior definition;
- development prior values;
- MAP-reset state rule;
- negative completed-month requirement;
- source axis;
- DEV/VAL/LOCK boundaries;
- any successor output already generated.

No new alarm threshold is fitted or introduced.

## 3. Timing and causal alignment

A successor state for month `t` is known only after month `t` closes.

Consequently, diagnostic forward outcomes begin with month `t+1`.

No forward return is used to calculate the state at `t`.

## 4. Outcome definitions

For completed monthly average GOLD price `P_t`:

- `FWD_1M(t) = P_(t+1) / P_t - 1`
- `FWD_2M(t) = P_(t+2) / P_t - 1`
- `FWD_3M(t) = P_(t+3) / P_t - 1`

Primary risk horizon:

`2–3 months`

Tail indicators inherited from the prior project audit:

- `TAIL_2M = 1` if `FWD_2M <= -0.03`, else `0`;
- `TAIL_3M = 1` if `FWD_3M <= -0.03`, else `0`.

`FWD_1M` is reported only as a secondary diagnostic because the prior project audit explicitly did not support 1M severity.

## 5. Evaluation groups

Within validation 2021-01..2023-12:

- `CANDIDATE`: successor state = `ADVERSE_BREAK_CANDIDATE`;
- `NON_CANDIDATE`: all other successor states with the required forward outcome available.

Report separately for each group:

- N;
- mean FWD_1M / FWD_2M / FWD_3M;
- median FWD_1M / FWD_2M / FWD_3M;
- TAIL_2M rate;
- TAIL_3M rate.

Also report candidate-minus-non-candidate differences. No p-value threshold or classifier threshold is introduced in V1.

## 6. Interpretation rule

This stage intentionally does **not** define a new numeric production-pass threshold. The earlier Gold Control BOCPD audit already established that small alarm samples are material and that descriptive separation is insufficient for automatic action.

Therefore:

- if candidate N is zero, status = `NOT_EVALUABLE_NO_VALIDATION_CANDIDATES`;
- if candidate N is nonzero, status = `VALIDATION_RISK_DIAGNOSTIC_COMPLETE`;
- any observed 2–3M downside separation is labelled `DESCRIPTIVE_ONLY`;
- production action remains `NOT_APPROVED` regardless of the locked result;
- direction vote remains `false`;
- historical validation does not itself authorize runtime ACTIVE or canonical decision authority.

This preserves the prior project decision that materially larger evidence is required before a production risk action can be frozen, without inventing a new N cutoff.

## 7. Locked replay

Locked 2024-01..2026-07 is computed only after the validation metrics are produced with the frozen method.

Locked results:

- are `DIAGNOSTIC_ONLY`;
- cannot change model parameters;
- cannot create a threshold;
- cannot approve the motor;
- cannot be combined with validation to tune V1.

For months lacking the full forward horizon by the frozen endpoint, the relevant forward metric is `NOT_AVAILABLE` and excluded only from that horizon’s denominator.

## 8. Required audit gates

- `STATE_OUTPUT_UNCHANGED_PASS`
- `SAME_MONTH_HINDSIGHT_NONE_PASS`
- `PRIMARY_HORIZON_2_3M_PASS`
- `TAIL_DEFINITION_MINUS_3PCT_PASS`
- `NO_NEW_THRESHOLD_PASS`
- `VALIDATION_NO_TUNING_PASS`
- `LOCKED_DIAGNOSTIC_ONLY_PASS`
- `DIRECTION_VOTE_FALSE_PASS`
- `AUTOMATIC_ACTION_NOT_APPROVED_PASS`
- `DATABASE_WRITES_NONE_PASS`

## 9. Maximum conclusion

Even if descriptive risk separation is strong, the maximum conclusion of this historical stage is:

`BOCPD_RETURN_SUCCESSOR_V1 = RESEARCH_SHADOW_CANDIDATE; RISK_DIAGNOSTIC_COMPLETE; PROSPECTIVE_VALIDATION_REQUIRED`

A future origin-time observation under a separately frozen issuer may be classified `PROSPECTIVE_SHADOW`. `LIVE_PRODUCTION` remains prohibited.
