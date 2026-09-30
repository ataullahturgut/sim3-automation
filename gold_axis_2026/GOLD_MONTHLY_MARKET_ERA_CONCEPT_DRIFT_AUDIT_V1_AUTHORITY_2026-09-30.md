# GOLD MONTHLY — Market Era / Concept Drift Audit V1 Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED / STRUCTURAL AUDIT

## 1. Question

Recent work produced a strong contradiction:

- in DEV 2022-2024, V2 TRANSITION was mostly a low-error/noisy-alarm context;
- in opened 2025-2026, V2 TRANSITION was concentrated on HIGH-error months.

The key question is now:

> Is this reversal explained by the long R2 market era that began in 2024, or did alarm/V2 behavior change later *within* the R2 era?

This audit is descriptive/structural. It does not create a trading or alarm rule.

## 2. Frozen source and chronology

Use:
- `GOLD_MONTHLY_ALARM_REGIME_V2_RELIABILITY_AUDIT_V1_2026-09-30.json`
- 58 common rows
- V2 primary schedule = EXPANDING_REFIT.

All conditioning variables are attached at forecast origin t.
Outcome severity belongs to target t+1.

No target-month state is used.

## 3. Era boundaries

Era boundaries are fixed from the previously frozen market-regime chronology, not from ChHHO errors:

### PRE_R2_ERA
- origin < 2024-04

### R2_EARLY
- origin 2024-04..2024-12

### R2_LATE
- origin 2025-01..2026-04

### R2_BREAK
- origin 2026-05..2026-07

R2_BREAK is descriptive only because it is the transition/break episode itself.

The central comparison is:
- PRE_R2_ERA
- R2_EARLY
- R2_LATE

If R2 itself explains the change, R2_EARLY and R2_LATE should broadly move in the same direction relative to PRE_R2_ERA.

If R2_EARLY resembles PRE_R2_ERA but R2_LATE changes sharply, that supports **late-R2 / within-regime concept drift**, not a simple R2-versus-old-regimes explanation.

## 4. Primary outcomes

For every era report monthly:
- HIGH count/rate;
- MEDIUM count/rate;
- ELEVATED = HIGH+MEDIUM count/rate;
- NORMAL count/rate.

For existing unions:
- ANY_VISIBLE
- T0_STANDARD

report:
- alarm events;
- HIGH hits;
- MEDIUM hits;
- false calls;
- HIGH recall;
- elevated recall;
- false-call rate;
- useful-call rate.

## 5. V2 risk behavior by era

Within each era compare:
- V2 STABLE
- V2 TRANSITION

on:
- HIGH rate;
- ELEVATED rate;
- NORMAL rate.

Also report:
- V2_TRANSITION + NO_ANY_VISIBLE
- V2_TRANSITION + NO_T0_STANDARD.

This tests whether V2 becomes non-redundant only in the late R2 era.

## 6. Same-regime control

To reduce confounding from comparing old R0/R1 mixtures with R2:

Repeat the era analysis using only rows whose **live V2 semantic state is R2**.

Report both:
- all rows by era;
- live-R2-only rows by era.

This is a key diagnostic.

## 7. Individual signal behavior

For:
- A, B, C, D, E, G, H, I1, I2, T1_WGC

within each era report event-level:
- n events;
- useful = HIGH_HIT or MEDIUM_HIT;
- false = FALSE_CALL;
- useful-call rate;
- false-call rate.

Label n<3 as SMALL_N.

Special attention remains descriptive:
- E
- H
- B
- T1_WGC

because prior audits showed regime-sensitive behavior.

## 8. Diagnostic exact tests

Use two-sided Fisher exact tests, diagnostic only:

Monthly severity:
- HIGH vs non-HIGH:
  - PRE vs R2_EARLY
  - PRE vs R2_LATE
  - R2_EARLY vs R2_LATE

Alarm event usefulness for ANY_VISIBLE and T0:
- useful vs false over the same three pairwise comparisons.

No p-value is used to tune a boundary or create a rule.

## 9. Primary structural interpretation rule

This audit does not have an operational promotion gate.

Interpretation is structural:

### SIMPLE_R2_ERA_EFFECT
Supported only if R2_EARLY and R2_LATE both show broadly the same directional change from PRE in the primary alarm/V2 metrics.

### LATE_R2_CONCEPT_DRIFT
Supported if R2_EARLY remains broadly similar to PRE, while R2_LATE shows a materially different pattern, especially after same-R2 control.

### NO_CLEAR_ERA_EFFECT
Use if differences are sparse/inconsistent.

No post-hoc boundary search is allowed.

## 10. Governance

Forbidden:
- moving the 2024-04 era boundary;
- searching for a better change date;
- retuning V2;
- changing alarms;
- changing severity thresholds;
- fitting weights;
- suppressing alarms;
- forecast correction;
- routing/model switching.

This stage answers only whether the observed reliability reversal is era-dependent.
