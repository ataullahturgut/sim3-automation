# GOLD CONTROL — REGIME-GATED SELECTIVE DAMPENER V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `REGIME_GATED_SELECTIVE_DAMPENER_V1_RESEARCH`  
**Parent downside sensor:** frozen `DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_RESEARCH` / SQRT-HAR-DR  
**Verifier:** frozen `UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH`  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Trigger and question

The corrected external-data/method audit V2 passed after fixing the 288-vs-276 session mismatch and confirmed that the 2020 hard-veto failure is not a loading, clock, SQRT-formula or Router-reconstruction artifact.

The rejected policy is:

`SQRT alarm AND Router V2 UP => SUPPRESS_DOWN`

The frozen Router V2 itself remains unchanged. This study tests one low-flexibility hypothesis only:

> Router-UP may be allowed to suppress a SQRT forced-DOWN alarm in a high-but-not-extreme risk regime, but it must lose suppression authority in the extreme SQRT-risk regime.

No Router threshold, expert membership, competence rule, tie-break or output semantic changes are allowed.

## 2. Chronology and evidence governance

- Random split: forbidden.
- 2025: researcher-visible retrospective stress only; never used to define or tune this policy.
- 2026: not used for policy design or promotion.
- 2020 crisis regime: mandatory evidence; it may not be excluded as an outlier.
- External 2018–2021 history: research-only, using the corrected 276-bar session-masked V2 spine.
- Governed DB: read-only.
- No result-dependent rescue or threshold search under this identity.

Because the broad hard-veto failure and the existence of a 2020 crisis regime are already known, pooled 2020–2024 results under this successor are retrospective hypothesis stress, not pristine prospective confirmation.

## 3. Frozen regime definition

For each evaluation year Y, use only formation rows whose target date is <= 31 December Y-1.

Let:
- `Q80_Y` = frozen nearest-rank 80th percentile of formation target downside realized variance (the existing SQRT alarm threshold);
- `Q90_Y` = nearest-rank 90th percentile of the same formation target downside realized variance, computed by the same nearest-rank convention.

For a frozen SQRT-HAR-DR forecast `F_t`:
- no parent alarm if `F_t < Q80_Y`;
- `HIGH_NON_EXTREME` if `Q80_Y <= F_t < Q90_Y`;
- `EXTREME` if `F_t >= Q90_Y`.

The 90th-percentile boundary is fixed before scoring this policy. No alternative percentile, ratio, absolute threshold or grid search is permitted under V1.

## 4. Frozen three-action policy

The controller is evaluated only on existing SQRT alarm rows.

1. Router V2 = ABSTAIN -> `RETAIN_DOWN`.
2. Router V2 = UP and regime = `EXTREME` -> `DOWN_WATCH`.
   - Operational semantics for this experiment: the DOWN alarm is retained; the UP countersignal is recorded but has no deletion authority.
3. Router V2 = UP and regime = `HIGH_NON_EXTREME` -> `SUPPRESS_DOWN`.

No other feature enters V1.

## 5. Mandatory row-level integrity gate

Before policy scoring, build a unified 2020–2024 alarm ledger containing at minimum:

- origin_date;
- target_date;
- evaluation_year;
- SQRT forecast;
- Q80 threshold;
- Q90 threshold;
- normalized SQRT risk score;
- risk regime;
- actual direction;
- Router V2 UP/ABSTAIN;
- selected expert where available;
- controller action.

The ledger must reproduce the already-frozen parent/intersection counts exactly:

- 2020: 212 SQRT alarms; Router overlap 140; 80 good / 60 bad hard-veto cases.
- 2021: 28 alarms; overlap 2; 1 good / 1 bad.
- 2022: 11 alarms; overlap 0.
- 2023: 2 alarms; overlap 0.
- 2024: 17 alarms; overlap 4; 3 good / 1 bad.

Any mismatch => `BLOCKED_INTEGRITY_MISMATCH`; do not score the controller.

## 6. Primary safety target

Prioritized error is:

`BAD_SUPPRESSION = SUPPRESS_DOWN on an actual DOWN SQRT alarm`.

Primary risk:

`P(SUPPRESS_DOWN | actual DOWN AND SQRT alarm)`.

Frozen safety parameters:
- alpha = 0.20;
- delta = 0.10.

Report:
- n actual-DOWN SQRT alarms;
- x bad suppressions;
- empirical bad-suppression rate;
- exact one-sided binomial lower-tail p-value under alpha=0.20;
- exact 90% upper confidence bound where available.

A strict retrospective risk-control diagnostic passes only if p <= 0.10. Because the hypothesis was formed after prior historical inspection, passing this diagnostic does not create prospective certification.

## 7. Required utility and stability metrics

Report overall and year-by-year:

- SQRT parent alarms;
- RETAIN / WATCH / SUPPRESS counts;
- good suppressions;
- bad suppressions;
- suppression precision;
- false-alarm reduction;
- true-DOWN retention;
- remaining forced-DOWN precision;
- precision change versus the parent forced-DOWN baseline;
- action coverage;
- HIGH_NON_EXTREME versus EXTREME support;
- Router-UP rate by risk regime.

The 2020 crisis year must be shown separately.

## 8. Comparators

Compare against:
1. parent SQRT forced-DOWN baseline;
2. rejected universal hard Router-V2 veto;
3. no-suppression policy.

Do not retune any comparator.

## 9. Decision semantics

Possible V1 outcomes:
- `REJECTED_SAFETY`: safety diagnostic fails materially;
- `SAFE_BUT_NONUSEFUL`: safety improves but useful false-alarm removal collapses;
- `RETROSPECTIVELY_PROMISING_NOT_CERTIFIED`: safety and utility are both materially improved, but no prospective claim is allowed;
- `BLOCKED_INTEGRITY_MISMATCH`: frozen counts cannot be reproduced.

No runtime promotion is authorized by this study.

## 10. Next-step rule

If V1 is retrospectively promising, freeze it and seek genuinely new/prospective or otherwise independent same-clock evidence before promotion. If it fails, do not tune Q90 post hoc under V1; any alternative regime definition requires a new identity and preregistration.
