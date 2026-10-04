# GOLD H3 — Handoff Delayed V1b Preregistration

**Date:** 2026-10-04
**Status:** separate challenger identity after HSM V1 same-origin FLIP failed its 2025 gate.
**Purpose:** test whether the Handoff sequence is an early warning that should arm the *next* origin rather than flip the same origin.

## Rationale

HSM V1 showed that the same-origin direct FLIP interpretation was not viable on 2025:
best structural variant = 6 actions, 3 rescue, 3 broken, net 0.

The underlying audit nevertheless showed:
- signal mechanisms often rise at t-1/t-2 before reversal episodes;
- internal fragility acceleration is positive on missed reversals and negative on correct continuations in both 2025 and 2026.

Therefore V1b changes **timing only**, not the signal families.

## State machine

At origin t:
1. External pressure existed in t-1 or t-2.
2. Internal state is elevated at t.
3. Internal state accelerated from t-1 to t.
4. If 1-3 hold, set ARMED(t)=True.

At the next available origin t+1:
5. Act only if ARMED(t)=True.
6. Act only if the combined baseline at t+1 still follows the prevailing momentum at t+1.
7. Act only if the prevailing momentum direction at t+1 is unchanged from t; if momentum itself already flipped, the warning is considered resolved and no Handoff action is needed.
8. Apply the already-frozen strong-pro-risk topology veto at t+1.
9. If all conditions survive, FLIP the combined baseline at t+1.

## Existing combined baseline

HELIOS V5-DCE + frozen SAGE/OCS exception-only + frozen RuleFlow V3-TG.

## Fixed score definitions

Inherited unchanged from HSM V1:
- external pressure = leadlag_score
- internal state = max(fragility_score, flow_score)
- internal acceleration = internal_now - internal_lag1
- external lookback = max(t-1,t-2)

## 2025-only structural grid

- external threshold: {0.60, 0.67, 0.75}
- internal threshold: {0.60, 0.67, 0.75}
- internal acceleration minimum: {0.00, 0.05, 0.10, 0.15}

No other threshold is permitted after seeing 2026.

## 2025 eligibility gate

Same gate as HSM V1:
- actions >= 6
- rescue precision >= 60%
- net rescue > 0
- action rate <= 15%
- among action months, >=70% non-negative
- worst action-month net >= -1

Selection tie-break:
1. highest net
2. highest precision
3. fewer actions
4. stricter q_external
5. stricter q_internal
6. larger acceleration threshold

If no rule passes, V1b closes and 2026 is not opened.

## 2026 stress

If a 2025 rule passes, apply it unchanged to all 191 mature 2026 origins and report rescue/broken/net, accuracy, balanced accuracy, action dates, and remaining-53 rescues.

## Scientific status

This is a new retrospective challenger created after V1 failed on 2025. 2025 is development for V1b. 2026 is not used for V1b threshold selection, but because the general Handoff concept was motivated by earlier 2026 diagnostics, the 2026 stress remains retrospective evidence rather than pristine prospective OOS validation.
