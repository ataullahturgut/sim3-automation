# GOLD CONTROL — PERSISTENT RISK-STATE DAMPENER V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `PERSISTENT_RISK_STATE_DAMPENER_V1_RESEARCH`  
**Parent downside sensor:** frozen `DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_RESEARCH` / SQRT-HAR-DR  
**Verifier:** frozen `UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH`  
**Immediate predecessor:** `REGIME_GATED_SELECTIVE_DAMPENER_V1_RESEARCH` (Q80–Q90 instantaneous magnitude gate; rejected for safety)  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Research question

The universal Router hard veto failed, and the first regime-aware successor based only on current SQRT forecast magnitude (Q80–Q90 versus >=Q90) also failed the frozen safety diagnostic. Therefore this study does not retune Q90 or search another instantaneous magnitude cutoff.

It tests one low-flexibility hypothesis only:

> Router-UP suppression may be unsafe when downside risk is persistently elevated across recent completed days, even when the current SQRT forecast is not individually extreme. Router suppression authority should therefore be disabled during a causally defined persistent high-risk state.

No Router threshold, expert membership, competence rule, SQRT coefficient, Q80 alarm definition, or tie-break is changed.

## 2. Chronology and evidence governance

- Random split: forbidden.
- 2025: excluded from policy definition, threshold selection, scoring, and rescue.
- 2026: excluded from policy definition, threshold selection, scoring, and promotion.
- 2020 crisis regime: mandatory evidence and may not be removed as an outlier.
- External 2018–2021 history: research-only corrected 276-bar session-masked V2 spine.
- Governed DB: read-only.
- No threshold grid, no alternate lookback, no result-dependent rescue under this identity.
- Because the 2020 failure and prior controller failures are already researcher-visible, all 2020–2024 results are retrospective hypothesis stress, not prospective certification.

## 3. Frozen persistent-state definition

For each evaluation year Y, retain the parent SQRT-HAR-DR formation and its existing nearest-rank `Q80_Y` threshold, calculated only from target dates <= 31 December Y-1.

At each forecast origin date d:

1. Take the latest 20 completed daily downside-realized-variance observations ending at and including origin d. These are all available at the forecast origin.
2. Count
   `C_d = number of those 20 completed days with DR >= Q80_Y`.
3. Define `PERSISTENT_HIGH` iff `C_d >= 9`.
4. Otherwise define `NON_PERSISTENT`.
5. If fewer than 20 completed observations are available, define `INSUFFICIENT_HISTORY` and deny suppression authority.

The lookback and cutoff are frozen before scoring:
- lookback N = 20 completed trading days;
- nominal exceedance probability p0 = 0.20, inherited from Q80;
- anomaly level = 0.01;
- K = 9 is the smallest integer satisfying
  `P[Binomial(20, 0.20) >= K] <= 0.01`;
- exact tail at K=9 is approximately 0.0099817863.

Thus K is derived analytically from the parent Q80 semantics, not selected by outcome search.

The current target day's DR or direction is never used in the state definition.

## 4. Frozen three-action controller

Evaluation occurs only on existing SQRT alarm rows.

1. Router V2 = ABSTAIN -> `RETAIN_DOWN`.
2. Router V2 = UP and state = `PERSISTENT_HIGH` -> `DOWN_WATCH`.
3. Router V2 = UP and state = `INSUFFICIENT_HISTORY` -> `DOWN_WATCH`.
4. Router V2 = UP and state = `NON_PERSISTENT` -> `SUPPRESS_DOWN`.

`DOWN_WATCH` retains the parent DOWN alarm. Router-UP is recorded as a countersignal but has no deletion authority.

No current SQRT magnitude gate beyond the already-frozen parent Q80 alarm is allowed in this V1 controller.

## 5. Mandatory integrity gate

Before scoring the new policy, reconstruct the frozen parent and Router intersections exactly:

- 2020: 212 SQRT alarms; Router-UP total 185; alarm overlap 140; 80 good / 60 bad universal-veto cases.
- 2021: 28 alarms; Router-UP total 33; overlap 2; 1 good / 1 bad.
- 2022: 11 alarms; Router-UP total 22; overlap 0.
- 2023: 2 alarms; Router-UP total 19; overlap 0.
- 2024: 17 alarms; Router-UP total 42; overlap 4; 3 good / 1 bad.

Also retain the frozen common-row and legacy-context count checks used in the predecessor.

Any mismatch => `BLOCKED_INTEGRITY_MISMATCH`; controller scoring is invalid.

## 6. Primary safety target

Prioritized error:

`BAD_SUPPRESSION = SUPPRESS_DOWN on an actual DOWN SQRT alarm`.

Primary risk:

`P(SUPPRESS_DOWN | actual DOWN AND SQRT alarm)`.

Frozen risk-control parameters:
- alpha = 0.20;
- delta = 0.10.

Report:
- actual-DOWN parent alarms n;
- bad suppressions x;
- empirical bad-suppression rate x/n;
- exact one-sided binomial lower-tail p-value under alpha=0.20;
- exact 90% Clopper-Pearson upper bound.

The retrospective safety diagnostic passes only when p <= 0.10.

## 7. Required diagnostics and utility reporting

Report pooled and by year:

- parent alarm count;
- actual DOWN / UP count;
- RETAIN / WATCH / SUPPRESS count;
- good and bad suppressions;
- suppression precision;
- false-alarm reduction;
- true-DOWN retention;
- baseline and remaining forced-DOWN precision;
- precision change;
- persistent versus non-persistent parent-alarm support;
- Router-UP count within each state;
- 20-day exceedance-count distribution on parent alarms.

2020 must be displayed separately.

## 8. Frozen comparators

Without retuning, report alongside the new policy:

1. no-suppression parent baseline;
2. rejected universal hard Router-V2 veto;
3. rejected Q80–Q90 instantaneous regime-gated dampener V1.

## 9. Decision semantics

- `BLOCKED_INTEGRITY_MISMATCH`: frozen reconstruction differs.
- `REJECTED_SAFETY`: exact retrospective safety diagnostic fails.
- `SAFE_BUT_NONUSEFUL`: safety passes but no false alarm is successfully removed.
- `RETROSPECTIVELY_PROMISING_NOT_CERTIFIED`: safety passes and at least one false alarm is successfully removed.

Even a promising result cannot authorize runtime promotion because the hypothesis was formed after visible historical failures.

## 10. Next-step rule

If V1 fails, do not tune N=20, K=9, or the 0.01 anomaly level under this identity. The next successor must use a new preregistration, most plausibly alarm-conditional/within-regime Router competence or a hierarchical/non-exchangeable risk-control formulation.

If V1 is retrospectively promising, freeze it and seek genuinely new or independent same-clock evidence before any promotion.
