# GOLD H3 — Topology-Conditioned Handoff Competence BOCPD V3 Preregistration

**Date:** 2026-10-04
**Status:** post-hoc mechanistic successor; not independent validation.

## Hypothesis

Handoff competence changes through time, but the competence process may differ by cross-asset topology.

Use two independent BOCPD competence streams:
- **STRONG_PRO_RISK**: trailing-60 Gold–Nasdaq correlation > 0, Gold–VIX correlation < 0, and at least one two-sided correlation p < 0.05.
- **OTHER_TOPOLOGY**: all other states.

The topology definition is exactly the already-frozen RuleFlow V3-TG definition. No new topology threshold is introduced.

## Handoff alarm

Unchanged:
- external_premax >= 0.60
- internal_now >= 0.60
- internal_d1 >= 0
- existing combined baseline follows prevailing H3 momentum.

## Competence model

Each topology stream has an independent Beta-Bernoulli BOCPD:
- Jeffreys Beta(0.5,0.5) segment prior
- expected competence run = **4 Handoff alarms**, frozen from Competence BOCPD V1
- update only after the corresponding alarm's H3 target has matured

## Frozen action rule

Unchanged from V1:
- predictive P(rescue) >= 0.60
- mixture P(theta > 0.50) >= 0.80

If both pass: FLIP existing combined baseline.
Otherwise: KEEP.

## Chronology

Initialize each topology stream only with its own 2025 Handoff outcomes.
Replay the authoritative **191-origin 2026 challenge** chronologically.
No 2026 outcome may update a stream before its target maturity.

## Reporting

- 2025 initialization by topology
- 2026 acted/rejected Handoff alarms
- rescue/broken/net/precision
- remaining-53 rescues
- baseline vs assisted accuracy and balanced accuracy
- topology-specific action performance and first trusted origin
- monthly net and full action chronology

## Governance

This V3 is motivated by the already-observed 2026 topology interaction, therefore its 2026 replay is explicitly post-hoc mechanistic research. Hazard, Handoff thresholds, topology definition and trust thresholds are frozen before this run.
