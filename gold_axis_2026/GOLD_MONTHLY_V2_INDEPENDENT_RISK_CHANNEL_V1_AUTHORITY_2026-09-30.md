# GOLD MONTHLY — V2 Independent Risk Channel V1 Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED / DOWNSTREAM RISK AUDIT

## 1. Question

Transition V2 was not reliable enough to act as a semantic regime-change gate or as a stationary alarm-weight multiplier.

This experiment asks a different question:

> Does a frozen V2 TRANSITION flag, used as its own contextual risk-warning channel at forecast origin t, add useful next-month HIGH/MEDIUM risk information beyond the existing alarm set?

V2 is not modified.

## 2. Chronology

For each forecast row:
- origin month = t;
- target month = t+1;
- V2 state/status at origin t is used;
- target severity at t+1 is evaluation only.

No target-month V2 state is used.

## 3. Frozen source

Use:
- `GOLD_MONTHLY_ALARM_REGIME_V2_RELIABILITY_AUDIT_V1_2026-09-30.json`
- primary schedule already embedded: **EXPANDING_REFIT**
- 58 rows.

Frozen existing alarm unions:
- `T0_STANDARD`
- `ANY_VISIBLE`.

Independent V2 risk warning:
- ON if `v2_transition_flag == true`
- OFF otherwise.

No V2 threshold, regime threshold, alarm definition, or severity threshold is changed.

## 4. Outcomes

Primary:
- HIGH next-month target.

Secondary:
- ELEVATED = HIGH or MEDIUM.

For V2 STABLE and TRANSITION report:
- n;
- HIGH count/rate;
- MEDIUM count/rate;
- ELEVATED count/rate;
- NORMAL count/rate;
- HIGH risk ratio TRANSITION/STABLE;
- ELEVATED risk ratio TRANSITION/STABLE;
- absolute risk differences.

## 5. Independent / non-redundant test

Primary independent slice:

### V2_TRANSITION + NO_ANY_VISIBLE

Report:
- n;
- HIGH;
- MEDIUM;
- NORMAL;
- HIGH rate;
- ELEVATED rate.

Compare with:

### V2_STABLE + NO_ANY_VISIBLE

This asks whether V2 sees risk specifically where all frozen alarms are silent.

Also report the same split for `NO_T0_STANDARD`.

## 6. Union augmentation test

Reconstruct, without tuning:

- `ANY_VISIBLE_OR_V2 = ANY_VISIBLE OR V2_TRANSITION`
- `T0_STANDARD_OR_V2 = T0_STANDARD OR V2_TRANSITION`.

For each report:
- events;
- HIGH hits;
- MEDIUM hits;
- false calls;
- HIGH recall;
- ELEVATED recall;
- false-call rate;
- useful-call rate.

Compare against the original frozen union in the same period.

## 7. Periods

Primary validation:
- DEV targets 2022-04..2024-12.

Opened descriptive:
- 2025-01..2025-12;
- 2026-01..2026-08;
- combined 2025-01..2026-08.

Also report full common 58-row sample.

2025/2026 cannot select or rescue a failed DEV candidate.

## 8. Regime-stratified diagnostic

Within live V2 semantic context report:
- R0;
- R1;
- R2;
- BELIRSIZ

crossed with:
- STABLE;
- TRANSITION.

For each cell report severity composition and event count.

Cells n<3 are SMALL_N.

## 9. DEV candidate rule

V2 may become a candidate independent risk channel only if primary DEV satisfies all:

1. HIGH rate in TRANSITION > HIGH rate in STABLE;
2. ELEVATED rate in TRANSITION > ELEVATED rate in STABLE;
3. at least one DEV HIGH target occurs in `V2_TRANSITION + NO_ANY_VISIBLE`.

This is deliberately minimal. It does not optimize a threshold.

If any condition fails:
- no independent V2 operational warning is promoted;
- opened 2025/2026 results remain descriptive only;
- do not retune V2.

## 10. Governance

Forbidden:
- retuning V2;
- selecting a different V2 threshold;
- changing alarms;
- changing severity cutoffs;
- fitting weights;
- suppressing existing alarms;
- forecast correction;
- routing/model switching.

This stage only measures whether frozen V2 has independent risk value.
