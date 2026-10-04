# GOLD H3 — Handoff State Machine V1 Preregistration

**Date:** 2026-10-04
**Status:** 2025-only rule selection followed by frozen 2026 retrospective stress.
**Purpose:** turn the already-observed signal sequence into a selective overlay, not a new standalone reversal model.

## State sequence

1. **NORMAL**
2. **EXTERNAL_PRESSURE** — external lead-lag pressure against the prevailing H3 momentum was elevated in either of the prior two available origins.
3. **INTERNAL_BREAK** — the current origin shows elevated Gold-internal fragility/flow plus a positive origin-to-origin acceleration.
4. **REVERSAL_CANDIDATE** — EXTERNAL_PRESSURE + INTERNAL_BREAK while the current combined baseline still follows prevailing momentum.
5. **TOPOLOGY_VETO** — if 60-origin Gold-Nasdaq correlation is positive, Gold-VIX correlation is negative, and at least one correlation has two-sided Pearson p<0.05, suppress the Handoff FLIP.
6. Otherwise **FLIP** the current combined baseline.

## Existing combined baseline

The pre-Handoff baseline is:
- HELIOS V5-DCE;
- plus frozen SAGE/OCS exception-only FLIPs where available;
- plus frozen RuleFlow V3-TG FLIPs.

If SAGE or RuleFlow already reversed V5, Handoff does not flip again.

## Fixed score definitions

Scores are inherited unchanged from the Remaining-53 Signal Audit.

- external pressure = `leadlag_score`
- internal state = max(`fragility_score`, `flow_score`)
- internal acceleration = current internal state - previous-origin internal state
- external lookback = maximum external pressure across t-1 and t-2 only

All component ranks are origin-safe and use only prior observations.

## 2025-only grid

Search only the following small structural grid on 2025 observations for which the score stack exists:

- external threshold: {0.60, 0.67, 0.75}
- internal threshold: {0.60, 0.67, 0.75}
- internal acceleration minimum: {0.00, 0.05, 0.10, 0.15}

Candidate:
`external_premax >= q_external AND internal_now >= q_internal AND internal_d1 >= delta AND combined_baseline == momentum AND NOT strong_pro_risk`.

No other threshold or condition may be introduced after seeing 2026.

## 2025 eligibility gate

A rule is eligible only if:
- actions >= 6
- rescue precision >= 60%
- net rescue > 0
- action rate <= 15%
- among calendar months containing at least one action, at least 70% are non-negative
- worst action-month net >= -1

Selection among eligible rules:
1. highest total net rescue
2. highest precision
3. fewer actions
4. stricter external threshold
5. stricter internal threshold
6. larger acceleration threshold

If no rule is eligible, HSM V1 closes with no 2026 opening.

## 2026 stress

Only the single selected 2025 rule is applied unchanged to 2026.

Report:
- actions, rescue, broken, net, precision
- monthly action stability
- baseline 2026 correct count / accuracy / balanced accuracy
- HSM-assisted correct count / accuracy / balanced accuracy
- overlap with existing SAGE and RuleFlow exceptions
- dates of every HSM action
- how many of the previously remaining 53 missed reversals are rescued

## Scientific status

Because the Handoff mechanism itself was motivated by retrospective 2026 diagnostics, even a frozen 2025-selection/2026-stress result is **not pristine independent OOS validation**. It is a stricter retrospective stress test intended to prevent direct 2026 threshold tuning.
