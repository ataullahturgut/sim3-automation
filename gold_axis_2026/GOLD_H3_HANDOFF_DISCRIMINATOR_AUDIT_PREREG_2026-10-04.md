# GOLD H3 — Handoff Rescue-vs-Broken Discriminator Audit Preregistration

**Date:** 2026-10-04
**Status:** retrospective mechanism diagnostic only.
**Purpose:** explain why the broad Handoff warning sometimes corresponds to a true reversal and sometimes to a continuation. This is not a new trading-rule search.

## Canonical Handoff alarm universe

Use the union/core of the HSM V1 structural grid **before topology veto**:

- external_premax >= 0.60
- internal_now >= 0.60
- internal_d1 >= 0.00
- current combined baseline still follows prevailing momentum

where:
- external_premax = max(leadlag_score at t-1, t-2)
- internal_now = max(fragility_score, flow_score)
- internal_d1 = internal_now - internal_now(t-1)

The pre-Handoff combined baseline is HELIOS V5-DCE + frozen SAGE/OCS exceptions + frozen RuleFlow V3-TG exceptions.

Alarm label:
- **RESCUE** if flipping the combined baseline would correct the outcome.
- **BROKEN** if flipping the combined baseline would damage a correct outcome.

## Allowed origin-safe discriminator families

### 1. Handoff anatomy
- external_premax
- internal_now
- internal_d1
- fragility_score
- flow_score
- leadlag current / lag1 / lag2

### 2. Options / repricing tension
From frozen RTE feature/prediction panels:
- p_rte
- p_inst
- rte_tension
- signed_opt_pressure
- signed_d_opt_pressure
- opt_vol_imbalance
- d_opt_vol_imbalance_1
- opt_total_z20

### 3. Futures participation
From frozen RTE and preliminary-OI panels, strict prior-trade-date:
- gc_dlog_volume_1
- gc_volume_z20
- gc_volume_accel_5
- preliminary GC volume
- preliminary GC open interest
- origin-safe one-step changes/ranks where coverage exists

The 2026 preliminary-OI source is incomplete after 2026-03-19; missingness must be reported and OI cannot be a full-year gating variable.

### 4. Cross-asset topology
Origin-safe trailing-60:
- Gold–Nasdaq r
- Gold–VIX r
- p-values
- strong-pro-risk state
- one-origin changes in r_GN and r_GV
- topology rotation magnitude

Topology is **not vetoed before this audit**, because it is itself a candidate discriminator.

### 5. Scheduled-event context
Use only event identity/date already available before or at the feature cutoff:
- scheduled-event indicator
- family where available
- 2Y event-day step/conflict variables where an event is present

Do not use post-H3 event labels or target-derived TRES event-type fields.

## Analyses

For 2025 and 2026 separately, and pooled:
- alarm count, rescue, broken, precision
- continuous feature mean/median by RESCUE vs BROKEN
- standardized mean difference (SMD)
- single-feature ROC AUC, oriented so AUC >= 0.5 and direction is reported
- feature coverage/missingness
- categorical topology/event contingency counts
- rank features by cross-year sign consistency, not pooled fit alone

A feature is called **stable-descriptive** only if:
- its rescue-vs-broken direction agrees in 2025 and 2026;
- each year has >=3 nonmissing RESCUE and >=3 nonmissing BROKEN values;
- |SMD| >= 0.20 in both years.

This label is descriptive; it does not create a trading rule.

## Governance

- No threshold tuning on rescue/broken labels.
- No multivariate classifier.
- No feature combination selected from 2026.
- No 2026 accuracy improvement will be claimed from this audit.
- Any promising discriminator must become a separately preregistered challenger and be frozen using non-2026 development evidence before use.
