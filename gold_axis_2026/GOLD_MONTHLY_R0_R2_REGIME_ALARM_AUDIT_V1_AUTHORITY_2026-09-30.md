# GOLD MONTHLY — R0/R2 Regime Alarm Audit V1 Authority

**Date:** 2026-09-30
**Status:** PRE-REGISTERED / DESCRIPTIVE REGIME-CONDITIONAL AUDIT
**Purpose:** measure existing alarm behavior separately inside confidently identified R0 and R2 origin regimes, using the same protocol as the completed R1 audit.

## 1. Scope
- Existing ChHHO targets: 2021-11..2026-08.
- Regime is always the **forecast origin month's** regime.
- Never condition on target-month regime.

## 2. Primary regime definition
For R0 and R2 separately:
- origin-month HMM state equals the tested regime;
- filtered posterior probability >= 0.60;
- origin month is not OOD.

Raw-state sensitivity:
- include all raw HMM assignments regardless of posterior floor;
- report OOD separately.

## 3. Alarm definitions
Frozen unchanged:
- A, B, C, D, E, G, H, I1, I2, T1_WGC.

Union summaries:
- T0_STANDARD
- ANY_VISIBLE.

## 4. Outcome definition
APE severity remains binding:
- NORMAL <2.5%
- MEDIUM 2.5%..<3.0%
- HIGH >=3.0%.

For each alarm and union within each regime report:
- events
- HIGH hits
- MEDIUM hits
- NORMAL false calls
- false-call rate
- useful-call rate
- HIGH recall within that regime
- exact hit and false-call target months.

Also report:
- all confident regime target months
- HIGH and MEDIUM targets
- HIGH targets with no visible alarm
- raw-state sensitivity.

## 5. Cross-regime comparison
After R0/R2 calculation, compare with frozen R1 audit using identical metrics.

Required cross-regime table:
- regime target count
- HIGH count
- ANY_VISIBLE HIGH recall
- ANY_VISIBLE false-call rate
- T0_STANDARD HIGH recall
- T0_STANDARD false-call rate
- per-signal event / HIGH / MEDIUM / false-call rates.

## 6. Governance
- No alarm selection.
- No alarm weighting.
- No threshold tuning.
- No forecast correction.
- No routing/model switching.
- This stage only determines whether existing alarm behavior differs descriptively by independently discovered market regime.
