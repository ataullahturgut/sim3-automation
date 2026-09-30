# GOLD MONTHLY — R1-Regime Alarm Audit V1 Authority

**Date:** 2026-09-30
**Status:** PRE-REGISTERED / DESCRIPTIVE REGIME-CONDITIONAL AUDIT
**Purpose:** measure existing alarm behavior when the forecast origin is confidently in R1.

## 1. Scope

Use only targets with existing ChHHO model results:
- 2021-11..2026-08
- 58 targets.

For each target, condition on the regime of its **origin month** (the completed month available when the forecast/alarm is produced), never the target month's regime.

## 2. R1 definition

Primary R1 subset:
- origin-month HMM state = R1;
- filtered posterior probability >= 0.60;
- origin month is not flagged OOD.

Origin months with R1 maximum posterior but probability <0.60 are classified BELIRSIZ and excluded from the primary R1 subset.

Also report a sensitivity view using all raw R1 assignments regardless of posterior confidence.

## 3. Alarm definitions

Do not change any existing signal definition:
- A, B, C, D, E, G, H, I1, I2;
- T1_WGC.

T1_WGC is allowed in the audit because its report describes the preceding/origin month, but it must be labeled as an early-target-month report signal rather than a month-end T0 signal.

## 4. Outcomes

Binding APE severity:
- NORMAL <2.5%
- MEDIUM 2.5%..<3.0%
- HIGH >=3.0%.

For each signal within confident R1:
- events;
- HIGH hits;
- MEDIUM hits;
- NORMAL false calls;
- false-call rate;
- useful-call rate;
- HIGH recall among HIGH targets whose origins are confident R1;
- exact hit and false-call target months.

Also report:
- all confident-R1 target months;
- all HIGH targets arising from confident-R1 origins;
- all MEDIUM targets arising from confident-R1 origins;
- HIGH R1 months with no visible alarm;
- union summaries for T0_STANDARD and ANY_VISIBLE.

## 5. Governance

- No alarm selection.
- No alarm weighting.
- No threshold tuning.
- No forecast correction.
- No routing/model switching.
- This audit answers only: how do existing alarms behave inside independently discovered R1?
