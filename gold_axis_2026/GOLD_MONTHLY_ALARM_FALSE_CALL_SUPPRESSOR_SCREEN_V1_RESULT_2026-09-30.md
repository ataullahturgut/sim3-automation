# GOLD MONTHLY — Alarm False-Call Suppressor Screen V1 Result

**Date:** 2026-09-30
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS
**Scope:** DEV 2022-04..2024-12 only; exploratory suppressor research. No production veto authorized.

## 1. Question

Can an origin-known SAFE / anti-alarm signal suppress false alarm calls without suppressing true HIGH/MEDIUM error warnings?

Existing A/B/C/D/E/G/H/I1/I2/T1 signals are all risk-oriented. None is inherently an opposite/safe alarm.

Simple multi-signal voting was already shown insufficient because multiple simultaneous warnings can still be false.

Therefore this screen tested origin-known **cross-model forecast consensus** using the frozen 16-model competitive pool.

## 2. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_ALARM_FALSE_CALL_SUPPRESSOR_SCREEN_V1_AUTHORITY_2026-09-30.md`
- authority commit: `fc4375f3ff2efef48c7a686c21dfbae57d7d3016`

Execution:
- workflow: **Gold Monthly Alarm False Call Suppressor Screen V1**
- run: **36712803237**
- code commit: `3290b8eb95a3f90277573d614bdd7e2dcd8b5750`
- workflow commit: `1fbd3cda23e2dcc6233e421d4a7d3c958e6c9ca4`
- scientific gate: **PASS**

## 3. Origin-known cross-model features

At each origin:
- forecast median of 16 competitive models;
- forecast IQR / median = DISPERSION_PCT;
- ChHHO distance from competitive median = CHHHO_DEV_PCT;
- share of competitive models agreeing with ChHHO direction versus RW.

No target actual is used in veto features.

Expanding prior-only thresholds:
- minimum prior history 6 DEV origins;
- only earlier forecast states used.

## 4. Continuous separation

Among veto-eligible ANY_VISIBLE alarm rows:

| Outcome | n | Median dispersion | Median ChHHO deviation from consensus | Median direction agreement |
|---|---:|---:|---:|---:|
| HIGH | 5 | 1.241% | 0.999% | 75.0% |
| MEDIUM | 2 | 1.147% | 0.786% | 81.25% |
| NORMAL false calls | 14 | **0.951%** | **0.537%** | **81.25%** |

Descriptive interpretation:
false calls tend to occur when model forecasts are more tightly clustered and ChHHO sits closer to the cross-model consensus.

This is a plausible SAFE-state mechanism, but distributions still overlap.

## 5. Candidate vetoes

### V1_TIGHT_CENTRAL

Definition:
- forecast dispersion <= prior Q25; AND
- ChHHO deviation <= prior median.

Result:
- poor suppressor.
- On ANY_VISIBLE it suppressed **2024-03**, a true HIGH APE 6.10% hit.
- removed zero false calls in that comparison.

Decision:
**REJECT as veto candidate.**

### V2_STRONG_DIRECTION_CONSENSUS

Definition:
- >=80% competitive models agree with ChHHO direction; AND
- forecast dispersion <= prior expanding median.

This was the only clean candidate.

#### ANY_VISIBLE

Before on DEV:
- alarm events 25
- HIGH hits 8
- MEDIUM hits 2
- false calls 15
- false-call rate 60.0%

V2 suppresses:
- **2022-12 — NORMAL, APE 1.755%, I2 + T1_WGC**
- **2024-02 — NORMAL, APE 1.546%, T1_WGC**
- **2024-08 — NORMAL, APE 1.796%, H**

Incorrectly suppressed:
- HIGH: **0**
- MEDIUM: **0**

After:
- events 22
- HIGH 8
- MEDIUM 2
- false calls 12
- false-call rate **54.5%**
- DEV HIGH recall among the full DEV HIGH set remains **100% for the alarm events covered by this screen**.

#### T0_ALL_VISIBLE

V2 suppresses:
- 2022-12
- 2024-08

Both are NORMAL.

Incorrectly suppressed:
- HIGH 0
- MEDIUM 0

False-call rate:
- before 50.0%
- after **44.4%**

#### T0_STANDARD

V2 suppresses:
- 2024-08 only

Incorrectly suppressed:
- HIGH 0
- MEDIUM 0

False-call rate:
- before 45.5%
- after **40.0%**

Decision:
**PROMISING EXPLORATORY SAFE-VETO CANDIDATE.**
No production promotion yet because the sample is small and confined to DEV.

### V3_CENTRAL_ONLY

Definition:
- ChHHO deviation from cross-model median <= prior Q25.

It removes many false calls but also suppresses:
- **2024-11 — HIGH, APE 4.494%**
- **2024-07 — MEDIUM, APE 2.961%**

Decision:
**REJECT.**

## 6. Key finding

There is no existing A-I/T1 "opposite alarm" that reliably cancels another risk signal.

However, a distinct **SAFE-state veto** based on cross-model forecast consensus is plausible:

> When at least 80% of competitive models agree with ChHHO direction and forecast dispersion is no larger than the prior-history median, some risk alarms are false calls rather than true elevated-error events.

In this first DEV-only screen it removed three ANY_VISIBLE false calls with no lost HIGH/MEDIUM hit.

This result is exploratory, not yet validated outside DEV.

## 7. Next scientific requirement

Before promotion:
- compute the same consensus features for 2025 and 2026 using only models that have frozen transport predictions;
- test V2 unchanged;
- do not retune 80% or dispersion threshold;
- if 2025/2026 preserves false-call suppression without hiding HIGH/MEDIUM errors, then open a formal SAFE-VETO validation stage.

No forecast correction.
No routing/model switching.
