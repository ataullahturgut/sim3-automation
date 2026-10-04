# GOLD H3 — Handoff Competence BOCPD V1 Preregistration

**Date:** 2026-10-04
**Status:** causal sequential competence model; 2025 formation, frozen 2026 retrospective stress.
**Purpose:** detect when the Handoff signal itself has entered a reliable regime, instead of trying to infer that regime from static market-state features.

## Core idea

For every canonical Handoff alarm, define a matured binary competence outcome:

- 1 = flipping the existing combined baseline would RESCUE the H3 call
- 0 = flipping would BREAK a correct H3 call

The sequence of these competence outcomes is modeled with Bayesian Online Changepoint Detection (BOCPD), using a Beta-Bernoulli segment model.

This is a meta-trust model:
- it does **not** predict Gold direction on non-Handoff origins;
- it estimates whether the Handoff expert is currently trustworthy;
- it updates only after each H3 target has matured.

## Canonical Handoff alarm

Before competence filtering:

- external_premax >= 0.60
- internal_now >= 0.60
- internal_d1 >= 0.00
- existing combined baseline still follows prevailing H3 momentum

Existing combined baseline:
HELIOS V5-DCE + frozen SAGE/OCS exception-only + frozen RuleFlow V3-TG.

No topology veto is imposed by this competence model.

## Bayesian segment model

For each competence regime:

theta = probability that a Handoff FLIP is a rescue.

Prior:
- theta ~ Beta(0.5, 0.5) (Jeffreys prior)

For a run-length state with R past rescues and B past broken flips:
- posterior theta ~ Beta(R+0.5, B+0.5)
- predictive rescue probability = (R+0.5)/(R+B+1)

## BOCPD

Constant geometric hazard over **Handoff alarms**, not calendar days.

Expected competence-run candidates:
- 4 alarms
- 6 alarms
- 8 alarms
- 12 alarms

Hazard = 1 / expected_run.

The expected-run setting is selected by maximum sequential log predictive evidence on **2025 Handoff alarms only**.

No 2026 outcome may influence the hazard.

At each alarm:
1. use only the run-length posterior and matured outcomes from earlier alarms;
2. compute pre-outcome mixture predictive rescue probability;
3. compute pre-outcome mixture probability that theta > 0.50;
4. decide ACT or REJECT;
5. only after the H3 target matures, update BOCPD with the current competence outcome.

## Frozen action rule

ACT / FLIP the Handoff alarm only if, before observing its outcome:

- predictive rescue probability >= 0.60
- P(theta > 0.50) >= 0.80

Otherwise reject Handoff and KEEP the existing combined baseline.

These thresholds are fixed before 2026 replay and are not searched.

## 2025 formation

2025 Handoff alarms are used only for:
- expected-run/hazard selection by log predictive evidence;
- carrying the final 2025 BOCPD posterior state into 2026.

2025 action performance is descriptive only and does not alter the thresholds.

## Frozen 2026 sequential stress

Replay all 2026 origins chronologically.

For each 2026 Handoff alarm:
- use only BOCPD state from previously matured Handoff outcomes;
- record predictive rescue probability, P(theta>0.5), MAP run length, changepoint probability proxy/run reset state, action/reject decision;
- after target maturity, update with rescue/broken outcome.

Report:
- selected expected run
- 2025 evidence by hazard candidate
- 2026 Handoff alarms
- acted / rejected
- rescue / broken / net / precision
- remaining missed reversals rescued
- baseline vs assisted accuracy / balanced accuracy
- monthly action net
- exact action chronology
- when the competence engine first begins trusting Handoff

## Governance

- 2026 does not select the hazard.
- 2026 does not select the action threshold.
- No future Handoff outcome updates the state before its target matures.
- No market-regime feature is tuned on 2026.
- The Handoff concept itself was discovered retrospectively using 2026 diagnostics, so this remains a strict retrospective stress rather than pristine prospective OOS validation.
