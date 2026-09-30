# GOLD MONTHLY — Alarm × Live Regime × Transition V2 Reliability Audit V1 Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED / DESCRIPTIVE DOWNSTREAM AUDIT

## 1. Question

The prior Transition V2 detector was rejected as a pure semantic-transition classifier because it produced too many out-of-reference-zone transition flags historically.

This audit asks a different question:

> Even when V2 is imperfect as a semantic regime-change detector, does its live STABLE/TRANSITION status identify materially different alarm reliability?

This is specifically an alarm-reliability audit, not a re-validation or retuning of V2.

## 2. Critical chronology

For every forecast/alarm row:
- origin month = t;
- forecast target month = t+1.

Use only V2 information dated **origin month t**.

No target-month V2 state is allowed.

## 3. Primary live market-state source

Primary schedule:
- **Transition V2 EXPANDING_REFIT**.

For each origin month use:
- V2 semantic state / semantic label;
- V2 semantic posterior;
- V2 transition flag / status.

The audit does **not** use the older frozen/full-sample regime label as the primary conditioning state.

Primary regime-status cells:
- R0_STABLE
- R0_TRANSITION
- R1_STABLE
- R1_TRANSITION
- R2_STABLE
- R2_TRANSITION
- BELIRSIZ_STABLE
- BELIRSIZ_TRANSITION

The semantic state used for confident cells is V2's live prototype-aligned state at the origin.

## 4. Alarm source

Use the already-frozen alarm outputs from:
- GOLD_MONTHLY_R0_R1_R2_REGIME_ALARM_AUDIT_V1_2026-09-30.json

Signals:
- A
- B
- C
- D
- E
- G
- H
- I1
- I2
- T1_WGC
- T0_STANDARD
- ANY_VISIBLE

No alarm definition or threshold is changed.

## 5. Alarm outcome definitions

Existing frozen outcome field is preserved:

- HIGH_HIT
- MEDIUM_HIT
- FALSE_CALL
- OFF

For any signal and cell report:
- target months n;
- HIGH target count;
- MEDIUM target count;
- NORMAL target count;
- alarm event count;
- HIGH hits;
- MEDIUM hits;
- false calls;
- HIGH recall = HIGH hits / HIGH target count;
- MEDIUM recall = MEDIUM hits / MEDIUM target count;
- false-call rate = false calls / alarm event count;
- useful-call rate = (HIGH hits + MEDIUM hits) / alarm event count.

No score or ranking is fitted in V1.

## 6. Periods

Report separately:

### DEV
Target months:
- 2022-04..2024-12.

### Opened 2025
Target months:
- 2025-01..2025-12.

### Opened 2026
Target months:
- 2026-01..2026-08.

### Opened combined
- 2025-01..2026-08.

### Full common audit
- all alarm rows with a matching V2 origin row.

2025/2026 are already opened and descriptive only.

## 7. Primary comparison

For every regime R0/R1/R2 and every signal with events:

Compare:
- regime + STABLE
versus
- same regime + TRANSITION.

Report raw differences in:
- false-call rate;
- useful-call rate;
- HIGH recall;
- event count.

Do not compute or optimize a transition multiplier.

Cells with event count <3 are labeled SMALL_N.

## 8. Does a "false transition" still matter for alarms?

V2 reference transition zones are used only as a diagnostic label.

For V2 TRANSITION origin months, classify:
- IN_REFERENCE_ZONE
- OUTSIDE_REFERENCE_ZONE

Then report alarm behavior separately.

This directly tests:

> Are V2's semantic "false transitions" nevertheless months in which alarm reliability changes?

A V2 flag outside a reference transition zone is **not** automatically treated as useless in this audit.

## 9. Union-level priority

The primary union summaries are:
- T0_STANDARD
- ANY_VISIBLE

For each period and live state cell report:
- HIGH coverage;
- MEDIUM hits;
- false calls;
- false-call rate;
- useful-call rate.

This directly connects to the project's goal of retaining HIGH coverage while reducing false alarms.

## 10. Individual-signal priority

For A/B/C/D/E/G/H/I1/I2/T1_WGC:
- report all state cells;
- flag SMALL_N;
- do not interpret 1/1 or 2/2 cells as stable reliability.

Special attention is descriptive only:
- B in R1;
- H in R1 vs R2;
- I2 in R0/R1;
- T1_WGC in R1;
- E in R2.

These were identified by the prior regime audit and are not new selection criteria.

## 11. Optional posterior view

Also report alarm behavior in broad V2 transition-confidence buckets using the live semantic posterior:

- HIGH_CONF: semantic probability >=0.80
- MID_CONF: 0.60..0.80
- BELIRSIZ: <0.60

crossed with STABLE/TRANSITION.

This is descriptive only and does not change V2.

## 12. Decision rule for the audit

This stage does not promote a weighting rule.

After results:

- If TRANSITION status shows a consistent and materially different alarm false-call/useful-call profile within the same regime across DEV and opened periods, it becomes a candidate reliability modifier for a later preregistered shrinkage model.
- If the effect is inconsistent, sparse, or reverses by period, keep V2 descriptive only.

No thresholds, alarm definitions, regime assignments, or V2 logic may be changed after seeing this audit.

## 13. Governance

Forbidden:
- retuning V2;
- changing alarm thresholds;
- selecting alarms from 2025/2026 outcomes;
- weighting alarms in this stage;
- forecast correction;
- model routing.

This stage is measurement only.
