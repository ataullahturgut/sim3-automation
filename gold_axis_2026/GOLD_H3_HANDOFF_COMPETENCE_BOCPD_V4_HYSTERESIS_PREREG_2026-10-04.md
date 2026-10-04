# GOLD H3 — Handoff Competence BOCPD V4 Hysteresis Preregistration

**Date:** 2026-10-04
**Status:** post-hoc mechanistic successor; retrospective development diagnostic.

## Hypothesis

Competence is a regime state with persistence. Re-evaluating trust from scratch at every alarm causes chattering and discards useful state persistence.

V4 preserves the V1 global BOCPD competence model and adds a hysteretic trust state.

## Frozen pieces inherited from V1

- canonical Handoff alarm:
  - external_premax >= 0.60
  - internal_now >= 0.60
  - internal_d1 >= 0
  - combined baseline follows momentum
- Beta-Bernoulli BOCPD with Jeffreys Beta(0.5,0.5) segment prior
- expected competence run = 4 Handoff alarms
- entry condition:
  - predictive P(rescue) >= 0.60
  - mixture P(theta > 0.50) >= 0.80
- authoritative 191-origin 2026 challenge
- all competence updates occur only after H3 target maturity

## New hysteresis rule

Trust state starts OFF.

### Entry
If trust is OFF and the frozen V1 entry condition is satisfied at a Handoff alarm:
- set trust ON
- ACT / FLIP that alarm.

### While trust is ON
- ACT on every canonical Handoff alarm.
- Maintain a streak of **matured Handoff competence failures**:
  - RESCUE outcome -> failure streak resets to 0
  - BROKEN outcome -> failure streak += 1

### Exit
If the failure streak reaches **2 consecutive matured BROKEN outcomes**:
- set trust OFF before the next decision.

Rejected alarms while trust is OFF still produce observable competence outcomes after maturity and continue to update BOCPD, because counterfactual FLIP correctness is known from the realized H3 target.

The two-strike exit is a structural hysteresis choice intended to avoid regime-state chattering after one noisy miss. It is not tuned after this preregistration.

## Reporting

- first trust entry
- each trust exit/re-entry
- acted/rejected alarms
- rescue/broken/net/precision
- baseline vs assisted accuracy / balanced accuracy
- remaining-53 rescues
- monthly net
- full chronology including trust state and failure streak

## Governance

This V4 was motivated after inspecting V1 chronology, so the 2026 replay is **post-hoc model development**, not validation. No other threshold, hazard, alarm definition or exit rule may change after this preregistration.
