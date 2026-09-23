# GOLD CONTROL — DOWN VERIFIER CANDIDATE AUDIT V1 PREREGISTRATION

**Date:** 2026-09-23  
**Identity:** `DOWN_VERIFIER_CANDIDATE_AUDIT_V1_RESEARCH`  
**Risk motor:** frozen SQRT-HAR-DR  
**UP verifier:** frozen `UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH`  
**Target subset:** SQRT high-risk alarm + frozen UP verifier ABSTAIN  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Research question

The frozen UP verifier has useful positive-UP information, but its ABSTAIN state is not a DOWN label.

This audit asks:

> Among days where SQRT signals high downside risk and the frozen UP verifier abstains, do any already-frozen same-clock daily direction motors emit a sufficiently clean positive DOWN signal to justify a dedicated DOWN-verifier successor?

This is a candidate audit, not a runtime promotion study.

## 2. Frozen candidate pool

Only already-tested, same-clock, next-day daily models that can be reconstructed exactly from the governed 5-minute XAU panel are eligible.

Ten candidates are frozen before scoring:

1. `TTSM_S2`
2. `TTSM_S1`
3. `TSM`
4. `BONATO_AR1_RM_QBOOST_H1`
5. `BONATO_AR1_QBOOST_H1`
6. `AR1_RM_LOGIT`
7. `RM_LOGIT`
8. `RV_LOGIT`
9. `RSK_LOGIT`
10. `AR1_LOGIT`

Excluded:
- FAST/SLOW/MONTHLY_DIRECTION_3M as direct candidates because they are context/slow-clock states, not same-clock next-day classifiers;
- Altuntaş AlexNet because its target-clock alignment remains unresolved;
- H5/H10/H20/weekly/monthly models because the horizon is not the same next-day target;
- any new model or threshold derived after seeing this audit.

## 3. Frozen DOWN-call definitions

No thresholds are tuned.

- TTSM_S2: DOWN iff frozen signal = -1; signal 0 = ABSTAIN.
- TTSM_S1: DOWN iff frozen signal = -1; signal 0 = ABSTAIN.
- TSM: DOWN iff frozen TSM signal = -1.
- BONATO_AR1_RM_QBOOST_H1: DOWN iff frozen h=1 median forecast q0.50 < 0.
- BONATO_AR1_QBOOST_H1: DOWN iff frozen h=1 median forecast q0.50 < 0.
- Each logit model: DOWN iff frozen p(UP) < 0.50.

No confidence-band, probability, magnitude or consensus threshold is added.

## 4. Frozen UP-verifier reconstruction

The audit reconstructs the already-frozen Router V2 exactly from its preregistered causal competence rule.

Direct UP experts:
- TTSM_S2
- TTSM_S1
- BONATO_AR1_RM_QBOOST_H1
- AR1_RM_LOGIT
- RM_LOGIT

Legacy competence context:
- FAST_UP
- SLOW_UP
- MONTHLY_DIRECTION_3M_UP

Router V2 rules remain unchanged:
- same-bucket matured history, global fallback if bucket UP-call support <30;
- eligibility requires historical UP calls >=30, UP precision >0.50, false-UP FPR <0.50;
- one-sided 90% Wilson LCB ranking;
- fixed tie order TTSM_S2 > TTSM_S1 > BONATO_AR1_RM_QBOOST_H1 > AR1_RM_LOGIT > RM_LOGIT.

Before candidate scoring, reconstruction must reproduce the frozen Router V2 metrics:
- 2022: Router UP=22;
- 2023: Router UP=19;
- 2024: Router UP=42, TP=26, FP=16;
- 2025: Router UP=37, TP=27, FP=10, all selected by RM_LOGIT.

Any mismatch => `BLOCKED_INTEGRITY_MISMATCH`.

## 5. SQRT parent integrity

Use the exact frozen SQRT parent forecast ledger from commit:
`2926796b6a7e9048d2c091c9c571cb928b773e02`.

Required alarm counts:
- 2022=11
- 2023=2
- 2024=17
- 2025=90

Required pre-2025 Router overlap:
- 2022 Router-UP overlap=0;
- 2023 overlap=0;
- 2024 overlap=4 = 3 actual UP / 1 actual DOWN.

## 6. Primary pre-2025 candidate audit

Primary candidate-selection population:

`SQRT alarm AND Router V2 ABSTAIN`

for target years 2022–2024 only.

Expected support from the frozen historical extension:
- 30 total SQRT alarms;
- 4 Router-UP;
- **26 Router-ABSTAIN**;
- Router-ABSTAIN actual direction = **13 DOWN / 13 UP**.

For each candidate report:
- available rows;
- DOWN calls;
- correct DOWN calls;
- false DOWN calls;
- DOWN precision;
- DOWN recall over the 13 actual-DOWN subset;
- false-DOWN FPR over the 13 actual-UP subset;
- DOWN-call coverage;
- one-sided 90% Wilson lower bound for DOWN precision.

## 7. Frozen exploratory selection rule

This is a research-candidate selector only, not a certification gate.

A candidate is eligible for locked-2025 transport only if on the 2022–2024 primary subset:
- DOWN calls >=5;
- DOWN precision >0.50;
- false-DOWN FPR <0.50.

Among eligible candidates choose:
1. highest one-sided 90% Wilson lower bound on DOWN precision;
2. lower false-DOWN FPR;
3. higher raw DOWN precision;
4. higher DOWN recall;
5. fixed candidate order listed in section 2.

If none is eligible, selection is `NONE` and 2025 candidate transport is not used to rescue the audit.

No multi-model ensemble, vote, threshold sweep or post-result combination is allowed in V1.

## 8. Locked 2025 transport

Only the single candidate selected from 2022–2024 may be evaluated on the locked 2025 subset:

`2025 SQRT alarm AND reconstructed frozen Router V2 ABSTAIN`.

2025 may not:
- change the selected candidate;
- change a threshold;
- create a combination;
- rescue a failed pre-2025 candidate.

Report the same DOWN metrics and compare them descriptively with the abstain-subset DOWN prevalence.

## 9. Interpretation

Possible statuses:

- `BLOCKED_INTEGRITY_MISMATCH`
- `NO_EXISTING_DOWN_CANDIDATE_ELIGIBLE`
- `PRE2025_DOWN_CANDIDATE_SELECTED_2025_TRANSPORT_WEAK`
- `PRE2025_DOWN_CANDIDATE_SELECTED_2025_TRANSPORT_SUPPORTIVE`

For the last label, 2025 is called supportive only if the frozen selected candidate has:
- at least 5 DOWN calls;
- DOWN precision > the 2025 abstain-subset DOWN prevalence;
- false-DOWN FPR <0.50.

This does not create production authority.

## 10. Governance

- random split: forbidden;
- no model retraining beyond each model's already-frozen expanding-origin rule;
- no threshold tuning;
- 2025 unavailable for candidate selection;
- 2026 excluded;
- governed DB read-only;
- no production writes;
- no runtime promotion.
