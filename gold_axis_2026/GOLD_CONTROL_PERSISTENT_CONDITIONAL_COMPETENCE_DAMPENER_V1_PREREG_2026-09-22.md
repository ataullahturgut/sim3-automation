# GOLD CONTROL — PERSISTENT CONDITIONAL-COMPETENCE DAMPENER V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `PERSISTENT_CONDITIONAL_COMPETENCE_DAMPENER_V1_RESEARCH`  
**Parent downside sensor:** frozen `DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_RESEARCH` / SQRT-HAR-DR  
**Verifier:** frozen `UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH`  
**Safety reference:** frozen `PERSISTENT_RISK_STATE_DAMPENER_V1_RESEARCH`  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Research question

The persistence gate solved most of the historical safety problem but became highly conservative: it retained 98.43% of true DOWN alarms while removing only 6 of 143 false parent alarms.

This successor tests one narrow hypothesis:

> Within a persistent high-risk state, Router-UP should remain WATCH by default, but suppression authority may be restored for a specific Router expert/context cell only after that same cell has accumulated enough causally matured persistent-alarm evidence and its one-sided confidence bound shows better-than-chance UP precision.

This study does not change the SQRT parent, Router expert set, Router ranking, persistence definition, or non-persistent action.

## 2. Binding chronology and governance

- Random split: forbidden.
- 2025: excluded from policy definition, threshold selection, scoring, rescue, and model selection.
- 2026: excluded from policy definition, threshold selection, scoring, rescue, and promotion.
- 2020 crisis evidence is mandatory and cannot be removed.
- External 2018–2021 history remains research-only corrected 276-bar session-masked V2 evidence.
- Governed DB access is read-only.
- No grid search over sample size, confidence level, competence threshold, expert grouping, or persistence parameters.
- Because prior 2020–2024 failures and the persistence result are already researcher-visible, all results remain retrospective hypothesis stress, not prospective certification.

## 3. Frozen persistence safety layer

The persistence state is copied unchanged from the frozen safety reference:

- use the latest 20 completed daily downside-realized-variance observations ending at the forecast origin;
- compare each to the evaluation year's frozen formation `Q80_Y`;
- `PERSISTENT_HIGH` iff at least 9 of those 20 completed days have `DR >= Q80_Y`;
- otherwise `NON_PERSISTENT`;
- if 20 completed observations are unavailable, suppression authority is denied.

No N=20 / K=9 / 0.01 anomaly-level tuning is permitted.

## 4. Frozen conditional-competence cell

For a current SQRT alarm where Router V2 emits UP, define the Router cell as:

`(selected_expert, legacy_bucket)`

where:
- `selected_expert` is the exact expert selected by frozen Router V2;
- `legacy_bucket` is frozen Router V2 context: `CONSENSUS_UP` or `NON_CONSENSUS_UP`.

For a current `PERSISTENT_HIGH` alarm, competence history contains only earlier rows satisfying all of:

1. SQRT parent alarm;
2. Router V2 = UP;
3. `PERSISTENT_HIGH`;
4. same `selected_expert`;
5. same `legacy_bucket`;
6. target outcome matured by the current forecast origin.

No global fallback and no neighboring-cell pooling is allowed in V1.

## 5. Frozen competence test

For the matured same-cell history:

- `n_cell` = number of matured Router-UP persistent-alarm cases;
- `tp_cell` = number whose actual next-day direction was UP;
- `precision_cell = tp_cell / n_cell`;
- compute the same one-sided 90% Wilson lower confidence bound convention already used by frozen Router V2, with z = 1.2815515655446004.

Persistent-state suppression authority is granted iff:

- `n_cell >= 30`; and
- `Wilson_LCB90(precision_cell) > 0.50`.

The minimum 30 is inherited from frozen Router V2's competence eligibility floor; it is not selected from this successor's outcomes. The 0.50 boundary means evidence must support better-than-chance UP precision at the same one-sided 90% confidence convention.

## 6. Frozen controller

Evaluate only existing SQRT alarm rows.

1. Router V2 = ABSTAIN -> `RETAIN_DOWN`.
2. Router V2 = UP + `NON_PERSISTENT` -> `SUPPRESS_DOWN` exactly as the frozen persistence reference.
3. Router V2 = UP + `PERSISTENT_HIGH` + competence authorized -> `SUPPRESS_DOWN`.
4. Router V2 = UP + `PERSISTENT_HIGH` + competence not authorized -> `DOWN_WATCH`.
5. Insufficient persistence history -> `DOWN_WATCH`.

Thus V1 can only recover additional utility inside persistent states when causal same-cell evidence is strong enough. It cannot remove any suppression already permitted by the frozen non-persistent reference.

## 7. Mandatory integrity gate

Before scoring, reproduce the frozen parent/Router intersections exactly:

- 2020: 212 SQRT alarms; Router UP total 185; overlap 140; universal-veto good/bad = 80/60.
- 2021: 28 alarms; Router UP total 33; overlap 2; good/bad = 1/1.
- 2022: 11 alarms; Router UP total 22; overlap 0.
- 2023: 2 alarms; Router UP total 19; overlap 0.
- 2024: 17 alarms; Router UP total 42; overlap 4; good/bad = 3/1.

Also reproduce the frozen common-row and legacy-context count checks.

Any mismatch => `BLOCKED_INTEGRITY_MISMATCH`.

## 8. Primary safety target

Prioritized error:

`BAD_SUPPRESSION = SUPPRESS_DOWN on an actual DOWN SQRT alarm`.

Primary risk:

`P(SUPPRESS_DOWN | actual DOWN AND SQRT alarm)`.

Frozen risk-control parameters:
- alpha = 0.20;
- delta = 0.10.

Report:
- n actual-DOWN SQRT alarms;
- x bad suppressions;
- empirical bad-suppression rate;
- exact one-sided binomial lower-tail p-value at alpha=0.20;
- exact 90% Clopper-Pearson upper bound.

Retrospective safety diagnostic passes only when p <= 0.10.

## 9. Utility target relative to the frozen safety reference

Frozen persistence reference:
- good suppressions = 6;
- bad suppressions = 2;
- false-alarm reduction = 4.20%;
- true-DOWN retention = 98.43%.

The successor achieves a utility gain only if:
- the primary retrospective safety diagnostic still passes; and
- good suppressions are strictly greater than 6.

No additional arbitrary coverage threshold is introduced.

## 10. Required reporting

Report pooled and year-by-year:
- parent alarms;
- actual DOWN / UP;
- RETAIN / WATCH / SUPPRESS;
- good / bad suppressions;
- false-alarm reduction;
- true-DOWN retention;
- suppression precision;
- baseline and remaining forced-DOWN precision;
- precision change;
- added suppressions relative to persistence reference;
- added good and added bad suppressions;
- persistent Router-UP cases by selected expert / legacy bucket;
- competence-authorized cases and their causal n / precision / LCB at decision time.

Show 2020 separately.

## 11. Decision semantics

- `BLOCKED_INTEGRITY_MISMATCH`: frozen reconstruction differs.
- `REJECTED_SAFETY`: primary exact retrospective safety diagnostic fails.
- `SAFE_NO_UTILITY_GAIN`: safety passes but good suppressions do not exceed the frozen reference's 6.
- `RETROSPECTIVE_UTILITY_GAIN_NOT_CERTIFIED`: safety passes and good suppressions exceed 6.

No status authorizes runtime promotion.

## 12. Next-step rule

If V1 is safe but does not improve utility, do not tune n=30, Wilson confidence level, 0.50 threshold, cell definition, or persistence N/K under the same identity.

Any broader pooling, discounted competence, Bayesian hierarchy, Mondrian risk control, or non-exchangeable conformal risk method requires a new preregistration.

If V1 improves utility while retaining the safety diagnostic, freeze it as a retrospective research candidate and seek independent/prospective same-clock evidence before any promotion.
