# GOLD CONTROL — COMPREHENSIVE RETAINED DOWN-SPECIALIST CROSSWALK V1 PREREGISTRATION

**Date:** 2026-09-23  
**Identity:** `COMPREHENSIVE_DOWN_SPECIALIST_CROSSWALK_V1_RESEARCH`  
**Risk motor:** frozen `SQRT-HAR-DR`  
**UP verifier:** frozen `UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH`  
**Primary target state:** `SQRT HIGH RISK + UP VERIFIER ABSTAIN`  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Purpose

A prior narrow audit screened only ten baseline daily outputs and was incorrectly summarized too broadly. This preregistration corrects that scope error.

The present audit asks:

> Among already-frozen Gold Control DOWN-specific, reversal, path, cross-market and conditional-direction specialists whose target clock can be aligned without invention, which ones actually emit useful positive DOWN evidence on the unresolved state `SQRT high risk + frozen UP verifier ABSTAIN`?

The study is a retrospective crosswalk. It does not create a new model and does not retune any old one.

## 2. Frozen unresolved populations

### Primary candidate screen

Target years 2022–2024 only.

Use the exact frozen subset already integrity-checked in:
`DOWN_VERIFIER_CANDIDATE_AUDIT_V1_RESEARCH`.

Required support:
- total unresolved rows = 26;
- actual DOWN = 13;
- actual UP = 13;
- 2022 SQRT alarms=11 and Router-UP overlap=0;
- 2023 SQRT alarms=2 and Router-UP overlap=0;
- 2024 SQRT alarms=17 and Router-UP overlap=4, therefore 13 unresolved.

### Locked 2025 transport

2025 is not used to select or redesign any candidate.

Required:
- SQRT alarms=90;
- Router-UP overlap=16;
- unresolved Router-ABSTAIN rows=74;
- actual DOWN=39;
- actual UP=35.

Only a candidate that is screen-positive pre-2025 may receive a 2025 transport label.

## 3. Candidate families frozen before scoring

### A. V1.53 exact-NY17 intraday specialists

Pinned source:
`98e593ac68c67f789bb664f4ffee5517a052ab7d`

Positive DOWN candidates:
1. `V153_RSV_TTSM_S2_DOWN`: DOWN iff frozen V1.53 `sig_ttsm_s2=-1`.
2. `V153_EUROPE_CONT_DOWN`: DOWN iff frozen same-day Europe-session continuation signal=-1.
3. `V153_RAW_MOM20_DOWN`: DOWN iff frozen raw 20-origin momentum sign=-1.

Diagnostic only, not a DOWN candidate:
- `V153_MODERATE_DOWNSHOCK_REVERSAL_UP`: this frozen rule emits UP or NO_SIGNAL only. It is cross-tabbed as an UP/rebound veto diagnostic but cannot qualify as a positive DOWN verifier.

V1.53 retained source begins in 2023. No 2022 value is invented.

### B. Cross-domain conditional direction V1

Pinned result/source:
`8c7a3b7f4b9c580fc599aa41a50b768358488609`

Use the retained exact row forecast artifact and frozen threshold 0.50:
4. `CROSSDOMAIN_STATIC_LOGIT_DOWN`
5. `CROSSDOMAIN_DYNAMIC_LOGIT_D99_DOWN`
6. `CROSSDOMAIN_COMPETING_RISK_DOWN`
7. `CROSSDOMAIN_EXPLICIT_DURATION_DOWN`

No refit is performed in this crosswalk.

### C. CBR-DTW path morphology V1

Pinned source:
`f187f89c166a75cefa8cf60709dcd4ce1027663d`

Reproduce the original yearly expanding formation and original frozen decision rules:
8. `CBR_STRICT_P050_DOWN`
9. `CBR_STRICT_RECALL75_DOWN`
10. `CBR_CONTEXT_P050_DOWN`
11. `CBR_CONTEXT_RECALL75_DOWN`

These variants are available from 2024 under the original model contract. No 2022–2023 predictions are invented.

### D. S&P 500 cross-market veto V1

Pinned source:
`1af5d5eb37d3c34881c206ff11b295d9099e2b0d`

Use original yearly expanding formation and rules:
12. `SP500_Q10_CONFIRM_DOWN`: DOWN confirmation is the complement of the frozen Q10 veto.
13. `SP500_LOGIT_P050_DOWN`
14. `SP500_LOGIT_RECALL75_DOWN`

Available from 2024 under the original contract.

### E. Heterogeneous path + S&P consensus V1

Pinned source:
`4f6efce38d636695d44d2fbb3282fa0ec78cc0c2`

15. `HETERO_CONSENSUS_DOWN`: original frozen rule `max(p_path,p_sp)>=0.50`.

Available from 2024.

## 4. Authority-scan exclusions

The following are explicitly not silently converted into candidates:

- Market Shock / Macro Event: event/minute clock, not the same next-day target.
- Macro-event Employment+Inflation specialist: event-time direction only.
- V1.53 moderate-downshock reversal: UP-only / NO_SIGNAL; diagnostic only.
- weekly, H5/H10/H20 and 3D models: target-horizon mismatch.
- MONTHLY_DIRECTION_3M and MOMENTUM_3M: slow-clock priors, not daily DOWN confirmations.
- Altuntaş AlexNet: target-clock alignment unresolved in the retained authority record.
- V1.63 family: 2024 is training history under that identity; no clean pre-2025 independent candidate screen is available.
- V1.69 and other later 1D research: not imported unless an exact retained same-clock row artifact and frozen pre-2025 decision rule can be proven before scoring.
- V1.48/V1.51/V1.55/V1.57/V1.58 internal variants: exact row-level retained evidence is NOT_FOUND in the canonical consolidation and will not be reconstructed from memory.

These exclusions are evidence-discipline decisions, not claims that the methods are intrinsically useless.

## 5. Metrics

For each candidate on its actually available pre-2025 unresolved rows report:

- available support n;
- actual DOWN / UP;
- DOWN calls;
- correct DOWN;
- false DOWN;
- DOWN precision;
- DOWN recall;
- false-DOWN FPR;
- DOWN-call coverage;
- one-sided 90% Wilson lower bound for DOWN precision.

Also report support by year so a 2024-only model is not presented as a 2022–2024 model.

## 6. Frozen screen-positive criterion

To preserve comparability with the prior narrow audit, a candidate is called `SCREEN_POSITIVE_PRE2025` only if:

- available support n >= 10;
- DOWN calls >= 5;
- DOWN precision > 0.50;
- false-DOWN FPR < 0.50.

No ranking winner is declared from these retrospective data.

All screen-positive candidates, if any, are transported unchanged to locked 2025.

## 7. Locked 2025 interpretation

For each pre-2025 screen-positive candidate:

- use the exact same frozen rule;
- report n, DOWN calls, correct/false DOWN, precision, recall and FPR;
- compare precision with the 2025 unresolved-subset DOWN prevalence 39/74.

Transport is descriptively supportive only if:
- DOWN calls >=5;
- DOWN precision > 39/74;
- false-DOWN FPR <0.50.

2025 cannot create a new candidate, new threshold, ensemble or rescue.

## 8. Integrity

Mandatory:

1. exact primary subset = 26 = 13 DOWN + 13 UP;
2. exact 2025 unresolved subset = 74 = 39 DOWN + 35 UP;
3. reconstructed frozen Router V2:
   - 2022 UP=22;
   - 2023 UP=19;
   - 2024 UP=42 = 26 TP + 16 FP;
   - 2025 UP=37 = 27 TP + 10 FP;
4. 2025 Router selected expert count RM_LOGIT=37;
5. cross-domain retained target sign matches unresolved ledger;
6. CBR/SP500/consensus original full-2024 aggregate metrics reproduce their frozen result artifacts before subset metrics are accepted;
7. V1.53 rules are loaded from the pinned frozen contract without changes.

Any mandatory failure => `BLOCKED_INTEGRITY_MISMATCH`.

## 9. Governance

- random split: forbidden;
- no threshold tuning;
- no model refit except exact reproduction of each candidate's original expanding-origin / frozen formation procedure;
- 2025 unavailable for selection;
- 2026 excluded;
- DB access read-only;
- production writes: NONE;
- runtime promotion: NONE;
- missing row-level evidence: `NOT_PROVEN`, never guessed.
