# GOLD MONTHLY — Alarm × Live Regime × Transition V2 Reliability Audit V1 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS / DESCRIPTIVE ONLY  
**Binding conclusion:** V2 status does contain alarm-relevant information, but the effect is strongly period/regime dependent. In DEV, V2 TRANSITION is mostly an alarm-distrust environment; in opened 2025-2026 it is instead concentrated on HIGH-error months. Therefore V2 should not receive one global alarm multiplier. The useful next question is a regime-specific/shrunk reliability model, not a binary global boost/suppress rule.

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_ALARM_REGIME_V2_RELIABILITY_AUDIT_V1_AUTHORITY_2026-09-30.md`
- authority commit: `6535a204e11687bb3eab0de96e81ad24e7120d7c`

Code:
- `gold_axis_2026/tools/gold_monthly_alarm_regime_v2_reliability_audit_v1.py`
- code commit: `ad7143cde6b4b0e608d752cbcf3d6633658e82c3`

Workflow:
- `.github/workflows/gold-monthly-alarm-regime-v2-reliability-audit-v1.yml`
- workflow commit: `26319045d3ae7aedda19ebfaaa331ff10f524382`

Execution:
- workflow: **Gold Monthly Alarm Regime V2 Reliability Audit V1**
- run: **36763775587**
- artifact: **11120035621**
- artifact digest: `sha256:636f2cffcb98ac35dd2ae7acd194b041bbca0cab2d3d7f8c68795002d20790f9`
- scientific gate: **PASS**

## 2. Chronology

Every alarm row is joined to **V2 EXPANDING_REFIT at the forecast origin month**.

For origin t:
- V2 live semantic regime/status at t is used;
- alarm/forecast outcome is evaluated at target t+1.

No target-month V2 state is used.

## 3. Primary DEV result — targets 2022-04..2024-12

DEV has 33 target months.

V2 live cells:
- R0_STABLE: 8
- R0_TRANSITION: 2
- R1_STABLE: 5
- R1_TRANSITION: 4
- R2_STABLE: 11
- BELIRSIZ_TRANSITION: 3

No confident R2_TRANSITION month appears in this DEV window.

### T0_STANDARD, STABLE vs TRANSITION

STABLE:
- 24 target months
- HIGH targets: 7
- alarm events: 9
- HIGH hits: 4
- MEDIUM hits: 2
- false calls: 3
- HIGH recall: **57.1%**
- false-call rate: **33.3%**
- useful-call rate: **66.7%**

TRANSITION:
- 9 target months
- HIGH targets: 1
- alarm events: 2
- HIGH hits: 0
- MEDIUM hits: 0
- false calls: **2**
- HIGH recall: **0%**
- false-call rate: **100%**
- useful-call rate: **0%**

Thus on DEV, T0 alarms firing during V2 TRANSITION were entirely false.

### ANY_VISIBLE, STABLE vs TRANSITION

STABLE:
- 19 alarm events
- 7 HIGH hits
- 2 MEDIUM hits
- 10 false calls
- HIGH recall: **100%**
- false-call rate: **52.6%**
- useful-call rate: **47.4%**

TRANSITION:
- 6 alarm events
- 1 HIGH hit
- 0 MEDIUM hits
- **5 false calls**
- HIGH recall: **100%**
- false-call rate: **83.3%**
- useful-call rate: **16.7%**

Therefore, in DEV, V2 TRANSITION marks a substantially noisier alarm environment.

## 4. The clearest same-regime case: R1

### R1_STABLE
5 target months:
- 2 HIGH
- 1 MEDIUM
- 2 NORMAL.

ANY_VISIBLE:
- 5 events
- 2 HIGH hits
- 1 MEDIUM hit
- 2 false
- false-call rate **40%**
- useful-call rate **60%**.

### R1_TRANSITION
4 target months:
- **all 4 NORMAL**.

ANY_VISIBLE:
- 2 alarm events
- **2/2 false**
- false-call rate **100%**.

T0_STANDARD:
- 1 event
- **1/1 false**.

Individual examples:
- B: 1 event -> false.
- T1_WGC: 1 event -> false.

This is direct evidence that, in the DEV R1 sample, V2 TRANSITION is useful as an alarm-distrust context.

Sample size remains small.

## 5. R0 and R2 DEV

R0_TRANSITION is only 2 target months:
- one HIGH;
- one NORMAL.

ANY_VISIBLE:
- 2 events;
- 1 HIGH hit;
- 1 false;
- 50% false rate.

This is too small for a stable modifier.

R2 in DEV is almost entirely STABLE:
- R2_STABLE n=11
- 3 HIGH, 1 MEDIUM, 7 NORMAL.

ANY_VISIBLE:
- 6 events
- 3 HIGH hits
- 1 MEDIUM hit
- 2 false
- false-call rate **33.3%**
- useful-call rate **66.7%**.

Selected individual R2_STABLE descriptive results:
- B: 1/1 HIGH hit
- C: 1/1 MEDIUM hit
- D: 1/1 HIGH hit
- H: 3 events -> 1 MEDIUM + 2 false
- T1_WGC: 3 events -> 2 HIGH + 1 false.

## 6. Opened 2025 result

V2 live cells:
- R2_STABLE: 11
- BELIRSIZ_TRANSITION: 1.

The only Transition origin:
- **2025-08 -> target 2025-09**
- target severity: **HIGH**
- alarm A fired
- T0_STANDARD: HIGH_HIT
- ANY_VISIBLE: HIGH_HIT.

Thus 2025 Transition evidence is useful, but n=1 and opened.

## 7. Opened 2026 result

V2 live cells:
- R2_STABLE: 6
- R2_TRANSITION: 1
- BELIRSIZ_TRANSITION: 1.

The two Transition origins both precede HIGH target errors:

### Origin 2026-05
- V2 = R2_TRANSITION
- target 2026-06 = **HIGH**
- APE about **8.57%**
- no frozen alarm fired
- T0_STANDARD = OFF
- ANY_VISIBLE = OFF.

V2 identifies a high-risk month that the existing alarm set completely misses.

### Origin 2026-07
- V2 = BELIRSIZ_TRANSITION
- target 2026-08 = **HIGH**
- APE about **7.89%**
- G fired
- ANY_VISIBLE = HIGH_HIT
- T0_STANDARD = OFF.

### 2026 aggregate

TRANSITION:
- 2 target months
- **2/2 HIGH**
- ANY_VISIBLE fires once and that call is useful
- no false call.

STABLE:
- 6 target months
- 1 HIGH, 1 MEDIUM, 4 NORMAL
- ANY_VISIBLE: 4 events -> 1 HIGH + 1 MEDIUM + 2 false
- false-call rate **50%**.

This is the opposite direction from DEV.

## 8. Opened 2025-2026 combined

Transition origins:
- 3 months
- **3/3 targets are HIGH**.

ANY_VISIBLE:
- 2 events
- 2 HIGH hits
- 0 false
- useful-call rate **100%**
- HIGH recall only **2/3 = 66.7%**, because the 2026-05 transition produced no frozen alarm.

T0_STANDARD:
- 1 event
- 1 HIGH hit
- 0 false
- HIGH recall **1/3 = 33.3%**.

Stable origins:
- 17 months
- 5 HIGH, 3 MEDIUM, 9 NORMAL.

ANY_VISIBLE:
- 10 events
- 5 HIGH hits
- 2 MEDIUM hits
- 3 false
- false-call rate **30%**
- useful-call rate **70%**.

Thus in the opened period, V2 TRANSITION is not an alarm-distrust state; it is concentrated on severe forecast-error months.

## 9. Opened R2_STABLE individual alarms

Within opened 2025-2026 R2_STABLE, n=17:

- **E:** 4 events -> 2 HIGH + 2 MEDIUM + **0 false**
- **H:** 3 events -> 2 HIGH + 1 MEDIUM + **0 false**
- A: 1 false
- B: 1 HIGH hit
- G: 1 false
- I1: 1 false
- I2: 1 false
- T1_WGC: 1 false.

E and H are descriptively strong here, but this is opened evidence and sample sizes remain small.

## 10. Important test: V2 "false transitions" are not automatically useless

Across the full common 58-row audit, V2 has **11 TRANSITION flags outside the reference semantic-transition zones**.

Those 11 target outcomes are:
- **3 HIGH**
- **2 MEDIUM**
- 6 NORMAL.

So 5/11 are materially non-NORMAL forecast-error months even though the V2 flag is a "false transition" under the semantic reference definition.

ANY_VISIBLE within these outside-zone V2 flags:
- 7 alarm events
- 3 HIGH hits
- 1 MEDIUM hit
- 3 false
- HIGH recall **100%**
- useful-call rate **57.1%**
- false-call rate **42.9%**.

Examples of outside-zone V2 flags that were alarm-relevant:
- 2021-11 origin -> 2021-12 HIGH, H hit.
- 2022-01 origin -> 2022-02 MEDIUM, T1_WGC hit.
- 2022-04 origin -> 2022-05 HIGH, I1 hit.
- 2025-08 origin -> 2025-09 HIGH, A hit.

Examples that were genuinely noisy:
- 2023-04 -> B false.
- 2023-10 -> I2 + T1_WGC false.
- 2024-01 -> T1_WGC false.

Therefore the earlier statement "V2 false transition = useless" is too strong.

## 11. V2 flags inside semantic reference zones are not automatically better for alarms

Full common sample, V2 TRANSITION inside reference zones:
- n=5
- 2 HIGH
- 3 NORMAL.

ANY_VISIBLE:
- 3 events
- 1 HIGH hit
- 2 false
- useful-call rate **33.3%**
- false-call rate **66.7%**.

Thus semantic correctness of V2 transition is not the same thing as alarm usefulness.

That is a major finding of this audit.

## 12. Binding interpretation

The user's hypothesis is partly supported:

> V2 may still be valuable even though it is imperfect as a semantic regime-change classifier.

However, the correct role is not a single global "TRANSITION = trust less" or "TRANSITION = trust more" multiplier.

Observed behavior:

### DEV
- Transition is mostly an **alarm-noise / distrust** environment.

### Opened 2025-2026
- Transition is a **high-risk forecast-error environment**.
- 3/3 transition origins precede HIGH errors.
- existing alarms catch only 2/3 with ANY_VISIBLE.

Therefore the effect changes by period and regime composition.

A global V2 multiplier would fail:
- suppressing alarms in all transitions would help some DEV false calls but would suppress useful 2025-2026 signals;
- boosting all transition alarms would amplify DEV noise.

## 13. What should be tested next

Do **not** discard V2.

Do **not** use it as a standalone semantic-transition gate.

The next defensible model is:

**Alarm × live regime × V2-status reliability with shrinkage / partial pooling.**

The unit is not just:
- signal A/B/H/etc.

It is:
- signal × live regime × STABLE/TRANSITION.

Because cells are sparse, raw ratios such as 1/1 or 2/2 must not be used directly.

A later preregistered model should:
- estimate a global signal reliability prior;
- partially pool by R0/R1/R2;
- add a V2 STABLE/TRANSITION effect only where supported;
- use V2 semantic posterior rather than forcing uncertain months into a hard regime;
- cross-validate only on chronology-safe historical/DEV folds;
- keep 2025/2026 descriptive/opened.

No alarm weight is authorized by the present audit.
