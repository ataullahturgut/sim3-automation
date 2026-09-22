# GOLD CONTROL — UP EXPERT ROUTER V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `UP_EXPERT_ROUTER_V1_RESEARCH`  
**Role:** select the most credible active UP expert on each daily origin while controlling false-UP burden  
**Runtime authority:** NONE  
**Production DB writes:** FORBIDDEN

## 1. Research question

Can a causal, class-specific expert-selection layer improve the reliability of UP calls relative to any single existing daily UP model?

The router does **not** forecast DOWN. Its outputs are:
- `UP`: at least one eligible expert currently says UP and is selected;
- `ABSTAIN`: no eligible active UP expert.

The downstream SQRT-veto use case is not evaluated until the router is frozen standalone.

## 2. Candidate pool frozen before router scoring

The pool is restricted to the five highest-ranked same-clock daily UP candidates from the v2.00 false-UP-clean ledger:

1. `TTSM_S2`
2. `TTSM_S1`
3. `BONATO_AR1_RM_QBOOST_H1`
4. `AR1_RM_LOGIT`
5. `RM_LOGIT`

`RV_LOGIT`, `AR1_LOGIT`, `RSK_LOGIT`, FAST, AlexNet, weekly, H5/H20 and monthly models are excluded from the router pool:
- the first three have materially larger false-UP burden;
- FAST is a trend state and original clock is not parent-equivalent;
- AlexNet clock mismatch remains unresolved;
- weekly/H5/H20/monthly horizons are not the same next-day target.

## 3. Data and target alignment

Authoritative candidate artifacts are the already-frozen 2023, 2024 and 2025 forecast/signal tables.

Required exact alignment before scoring:
- same `origin_date`;
- same `target_date`;
- actual return sign identical across TTSM, Bonato h=1 and realized-moment logit artifacts on common rows.

Bonato rows are restricted to `horizon == 1`.

Any row failing exact target-date or actual-sign equivalence is excluded and reported. No nearest-date matching, forward fill or interpolation.

## 4. Time split

- **2023:** development / competence-history formation only.
- **2024:** frozen validation.
- **2025:** locked retrospective challenge / transport only.

No 2024 or 2025 result may change a router rule.

For every origin, competence statistics use only matured prior targets. The algorithm may update causally after an outcome matures; it may never use the current target or future targets.

## 5. Expert UP definitions

- TTSM_S2 active-UP iff `ttsm_s2_signal == +1`.
- TTSM_S1 active-UP iff `ttsm_s1_signal == +1`.
- BONATO_AR1_RM_QBOOST_H1 active-UP iff `AR1_RM_QBOOST_q0.50 > 0`.
- AR1_RM_LOGIT active-UP iff `AR1_RM_LOGIT_pred_up == 1`.
- RM_LOGIT active-UP iff `RM_LOGIT_pred_up == 1`.

## 6. Causal competence state

For expert j at origin t, using only matured prior common rows:

- `n_up_j`: number of prior origins on which expert j emitted UP;
- `tp_up_j`: those UP calls followed by actual UP;
- `fp_up_j`: those UP calls followed by actual DOWN;
- `precision_j = tp_up_j / n_up_j`;
- `false_up_fpr_j = fp_up_j / N_actual_down_history`.

To stabilize small samples, ranking uses a one-sided 90% Wilson lower confidence bound for UP precision with z = 1.2815515655446004.

## 7. Eligibility gate

An expert can be selected only when all are true:

1. it currently emits UP;
2. `n_up_j >= 30`;
3. historical UP precision > 0.50;
4. historical false-UP FPR < 0.50.

These thresholds are frozen before 2024 scoring and are not optimized.

## 8. Selection rule

Among eligible active-UP experts:

1. choose highest Wilson lower bound of UP precision;
2. tie-break by lower historical false-UP FPR;
3. then higher raw historical UP precision;
4. then fixed identity order:
   `TTSM_S2 > TTSM_S1 > BONATO_AR1_RM_QBOOST_H1 > AR1_RM_LOGIT > RM_LOGIT`.

If no expert is eligible, output `ABSTAIN`.

No majority vote, top-2 combination, threshold sweep, learned meta-classifier or post-score rescue is allowed in V1.

## 9. Fixed-expert benchmark

A single fixed benchmark expert is selected using **2023 only**:

- among candidates with >=30 UP calls and 2023 UP precision > 0.50;
- choose lowest 2023 false-UP FPR;
- tie-break higher 2023 UP precision, then the same fixed identity order.

The benchmark identity is frozen after computing 2023 only and before 2024 metrics are read.

## 10. Metrics

For 2024 validation and unchanged 2025 challenge:

- total common origins;
- router UP outputs;
- coverage;
- true UP among router outputs;
- false UP among router outputs;
- UP precision;
- UP-alarm error = 1 - precision;
- false-UP FPR = false UP outputs / all actual DOWN origins;
- actual-UP recall = true UP outputs / all actual UP origins;
- selected-expert counts;
- abstain count.

Benchmark metrics are computed on the same common rows.

## 11. Promising gate

V1 is `PROMISING` only if 2024 satisfies all:

1. router UP outputs >= 20;
2. coverage >= 0.10;
3. router UP precision >= fixed benchmark precision + 0.03 absolute;
4. router false-UP FPR <= fixed benchmark FPR - 0.05 absolute.

2025 cannot rescue a failed 2024 gate.

If 2024 passes, 2025 transport is considered stable only if:
- router precision is not below benchmark precision; and
- router FPR is not above benchmark FPR.

## 12. Governance

- no random split;
- no 2025 tuning;
- no threshold search;
- no production writes;
- no runtime promotion;
- no SQRT intersection until this standalone router result is frozen.
