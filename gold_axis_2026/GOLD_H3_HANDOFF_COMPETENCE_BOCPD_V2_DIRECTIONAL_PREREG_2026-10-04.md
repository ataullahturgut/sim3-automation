# GOLD H3 — Direction-Conditioned Handoff Competence BOCPD V2 Preregistration

**Date:** 2026-10-04
**Status:** mechanistic successor after V1; retrospective stress, not pristine OOS.
**Purpose:** test whether Handoff competence evolves differently when the prevailing H3 momentum is UP versus DOWN.

## Motivation

V1 used a single competence process for all Handoff alarms and improved the 2026 combined baseline from 126/191 to 127/191.

A post-V1 audit showed material directional asymmetry in the broad Handoff alarm:
- 2026 UP-momentum Handoff: 11 rescue / 5 broken
- 2026 DOWN-momentum Handoff: 5 rescue / 7 broken

The successor therefore changes only the **competence-state partition**:
- one BOCPD stream for Handoff alarms with momentum_up = 1
- one independent BOCPD stream for momentum_up = 0

No Handoff feature threshold changes.

## Canonical Handoff alarm

Same as V1:
- external_premax >= 0.60
- internal_now >= 0.60
- internal_d1 >= 0
- existing combined baseline still follows prevailing momentum

## BOCPD model

Same Beta-Bernoulli BOCPD as V1:
- Jeffreys Beta(0.5,0.5) segment prior
- expected competence run = **4 Handoff alarms**, frozen from V1's 2025-only evidence selection
- decisions use only outcomes whose H3 targets have already matured

## Direction-conditioned streams

At a Handoff alarm:
- if momentum_up = 1, consult/update only the UP-stream competence posterior;
- if momentum_up = 0, consult/update only the DOWN-stream posterior.

An outcome never updates the opposite-direction stream.

Both streams are initialized using only their corresponding **2025 Handoff alarms**.

## Frozen action rule

Unchanged from V1:
- predictive P(rescue) >= 0.60
- mixture P(theta > 0.50) >= 0.80

If both pass -> FLIP combined baseline.
Otherwise -> KEEP.

## Frozen 2026 stress

Use the same authoritative 191-origin 2026 challenge membership as V1.

Report:
- acted/rejected alarms
- rescue/broken/net/precision
- remaining missed reversals rescued
- baseline vs assisted accuracy and balanced accuracy
- UP-stream and DOWN-stream chronology separately
- first trusted origin in each direction
- monthly net

## Governance

This V2 hypothesis was motivated by inspecting the directional asymmetry of 2026 Handoff outcomes, so its 2026 replay is explicitly **post-hoc mechanistic research**, not validation. No threshold/hazard/feature is tuned after this preregistration.
