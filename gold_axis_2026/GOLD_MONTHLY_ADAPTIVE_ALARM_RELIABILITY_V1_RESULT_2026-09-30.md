# GOLD MONTHLY — Adaptive Alarm Reliability V1 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS / ADAPTIVE CANDIDATE FAIL  
**Binding conclusion:** pre-2025 chronology-safe evidence does **not** support a rolling or exponentially decayed reliability memory. The selected mechanism is EXPANDING history. The observed late-R2 E/H rise can be learned sequentially even without explicit recency weighting, but a hard 0.50 reliability gate still suppresses too many genuine HIGH/MEDIUM alarms.

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_ADAPTIVE_ALARM_RELIABILITY_V1_AUTHORITY_2026-09-30.md`
- authority commit: `cb3b3abd619cc6b797d832464b7770aa4a9e42fb`

Code:
- `gold_axis_2026/tools/gold_monthly_adaptive_alarm_reliability_v1.py`
- code commit: `9056b64517dff18d0d0735e43c08b051b07a82b5`

Workflow:
- `.github/workflows/gold-monthly-adaptive-alarm-reliability-v1.yml`
- workflow commit: `65c2eba5ce56eca2caf8866778e65b905230dfb9`

Execution:
- workflow: **Gold Monthly Adaptive Alarm Reliability V1**
- run: **36773748629**
- artifact: **11123949742**
- artifact digest: `sha256:bbace723ed9c75729741ca78f7e6398da7b21809fe3412db4e8f66c77138e78d`
- scientific gate: **PASS**

## 2. Frozen candidate set

Candidates:
- EXPANDING
- ROLL_12
- ROLL_18
- ROLL_24
- ROLL_36
- HL_6
- HL_12
- HL_18
- HL_24

Fixed prior strength:
- 4

Fixed hard diagnostic gate:
- reliability >= 0.50

No 2025/2026 outcome was used to choose memory.

## 3. DEV selection result

Chronology-safe DEV:
- targets 2022-04..2024-12
- 45 individual signal events
- 20 useful
- 25 false.

Candidate Brier scores:

1. **EXPANDING: 0.287268**
2. ROLL_36: 0.287268
3. HL_24: 0.289101
4. HL_18: 0.289785
5. HL_12: 0.291209
6. ROLL_18: 0.291697
7. ROLL_24: 0.294164
8. HL_6: 0.295642
9. ROLL_12: 0.298660

ROLL_36 ties EXPANDING because the available historical memory inside the DEV span is effectively contained within 36 months.

All shorter / more aggressive recency mechanisms are worse.

Selected:
- **EXPANDING**

Therefore the pre-2025 selection does not support explicit recency forgetting.

## 4. DEV probability discrimination remains weak

EXPANDING:
- Brier: **0.287268**
- log loss: 0.770655
- mean score on useful events: **0.4603**
- mean score on false calls: **0.5198**

The ordering is reversed:
- false calls receive higher mean reliability than useful calls.

Thus neither recency nor expanding signal-history probability is a satisfactory direct classifier on DEV.

## 5. Fixed 0.50 gate still fails

Raw DEV ANY_VISIBLE:
- 25 events
- 8 HIGH
- 2 MEDIUM
- 15 false
- HIGH recall 100%.

EXPANDING reliability gate >=0.50:
- 12 events
- **5 HIGH**
- 0 MEDIUM
- 7 false
- HIGH-hit retention **62.5%**
- false-call reduction **53.3%**.

Pre-registered requirements:
- HIGH retention >=80% -> **FAIL**
- false reduction >=20% -> PASS.

The gate suppresses too much useful coverage.

Raw T0:
- 11 events
- 4 HIGH
- 2 MEDIUM
- 5 false.

Gated T0:
- 5 events
- **1 HIGH**
- 0 MEDIUM
- 4 false.

This is operationally unusable.

## 6. Why aggressive recency does not help DEV

Short windows suppress some noisy T1/I2 events, but they also erase sparse useful evidence for A/H/C/D.

Examples under short-window variants include suppression of:
- 2023-08 HIGH via A/I2/T1
- 2024-03 HIGH via I2/T1
- 2024-04 MEDIUM via H/T1
- 2024-07 MEDIUM via C/H
- 2024-11 HIGH via D.

So a simple “forget old history faster” rule does not solve the sparse-alarm problem.

## 7. Opened 2025-2026 sequential transport

Because EXPANDING was selected, the selected mechanism and baseline are identical.

Opened event-level:
- 15 signal events
- 10 useful
- 5 false
- Brier: **0.239903**
- log loss: 0.672497
- mean score useful: **0.5362**
- mean score false: **0.5040**.

Unlike DEV, discrimination is now in the correct direction, but only modestly.

This again supports non-stationarity in the alarm process.

## 8. Opened hard-gate result remains unacceptable

Raw ANY_VISIBLE:
- 12 events
- 7 HIGH
- 2 MEDIUM
- 3 false
- HIGH recall 87.5%
- useful rate 75%.

Reliability-gated ANY_VISIBLE:
- 7 events
- **4 HIGH**
- 1 MEDIUM
- 2 false
- HIGH-hit retention **57.1%**
- useful rate 71.4%.

Useful opened rows suppressed include:
- origin 2025-01 H -> target Feb HIGH
- origin 2025-02 B -> target Mar HIGH
- origin 2025-04 E -> target May MEDIUM
- origin 2026-07 G -> target Aug HIGH.

Thus hard suppression remains wrong even after sequential learning.

## 9. Important positive finding: E/H beliefs do update naturally

Although explicit recency was rejected, the expanding Bayesian score itself adapts when new outcomes arrive.

### At 2024-12
Before late-R2 E evidence:
- E: **0.451**, no observed events
- H: **0.480**
- I2: **0.454**
- T1: **0.377**

### At 2025-06
After E's first useful event and additional H evidence:
- E: **0.585**
- H: **0.539**
- I2: 0.462
- T1: 0.382

Thus E/H have already moved above I2/T1 by mid-2025.

### At 2025-12
- E: **0.667**
- H: **0.583**
- I2: 0.467
- T1: 0.385

### At 2026-04
- E: **0.758** from 4/4 observed useful events
- H: **0.620** from 6/9 useful
- I2: 0.471
- T1: 0.387

### At 2026-08
- E: **0.750**
- H: **0.615**
- I2: **0.438**
- T1: **0.370**

Therefore the system does naturally learn the late-R2 change in the *relative ordering* of signals.

The problem is not failure to learn E/H.

The problem is:
- sparse signals start with uncertain scores;
- a fixed hard threshold suppresses them before enough observations accumulate;
- some useful one-off alarms such as G can remain below threshold despite being valuable.

## 10. Structural interpretation

The previous concept-drift finding remains important, but a simple rolling/decay memory is not the right solution.

Current evidence says:

1. Alarm ecology changes over time.
2. E/H become relatively stronger in late R2.
3. Standard expanding learning is already capable of reflecting this once observations arrive.
4. Faster forgetting does not improve historical OOF calibration.
5. Hard probability gating destroys HIGH/MEDIUM coverage.

So the next design should not be:
- shorter rolling windows;
- more aggressive decay;
- another 0.50 suppression threshold.

## 11. Binding decision

Reject:
- rolling/half-life adaptive reliability as an operational replacement;
- hard reliability gating.

Retain:
- expanding signal reliability as a **descriptive confidence track**;
- its sequential E/H vs I2/T1 ordering as useful context.

No alarm is suppressed or reweighted from this result.

## 12. Next defensible question

The remaining problem is asymmetric:

> How can the system use reliability information without suppressing rare but potentially critical signals before they accumulate enough history?

A defensible next experiment is a **confidence-tier / evidence-strength overlay** rather than a binary gate:

- separate estimated reliability from evidence amount;
- label signals as e.g. ESTABLISHED / EMERGING / WEAK-EVIDENCE;
- never suppress solely because a sparse signal score is below 0.50;
- test whether confidence tiers can reduce false-call interpretation while preserving HIGH coverage.

Alternatively, test the previously promising **cross-model consensus + low-dispersion false-call suppressor**, which had removed DEV false calls without losing HIGH/MEDIUM in its pilot and is structurally independent of sparse alarm-history probabilities.
