# GOLD MONTHLY — Alarm × Live Regime × V2 Shrinkage Reliability Model V1 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS / CANDIDATE GATE FAIL  
**Binding conclusion:** the pre-registered shrinkage/partial-pooling reliability model does not improve chronology-safe alarm reliability. Adding live regime and V2 status makes event-level probability calibration worse than signal-only history, and the fixed 0.50 gate suppresses too many genuine HIGH/MEDIUM alarm hits. No alarm weighting is authorized.

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_ALARM_REGIME_V2_SHRINKAGE_RELIABILITY_V1_AUTHORITY_2026-09-30.md`
- authority commit: `3d1287370d05420d6a0157e32b7109f26dc4bad4`

Code:
- `gold_axis_2026/tools/gold_monthly_alarm_regime_v2_shrinkage_reliability_v1.py`
- code commit: `7885fa2945b6d6651a52e2c9139dc5c91329e8d1`

Workflow:
- `.github/workflows/gold-monthly-alarm-regime-v2-shrinkage-reliability-v1.yml`
- workflow commit: `9be7f5355d6cd82d313772ed74e672011ee8ef61`

Execution:
- workflow: **Gold Monthly Alarm Regime V2 Shrinkage Reliability V1**
- run: **36767819409**
- artifact: **11123025744**
- artifact digest: `sha256:131a6ac30581d7314c51a02b5ab286a13f8a2d38cf46687fc32373651adc68e2`
- scientific gate: **PASS**

## 2. Frozen model

Outcome:
- useful = HIGH_HIT or MEDIUM_HIT
- false = FALSE_CALL.

Models:
- M0 = signal-only shrinkage
- M1 = signal + soft live regime
- M2 = signal + soft live regime + V2 STABLE/TRANSITION.

Fixed pseudo-counts:
- signal: 4
- signal×regime: 4
- signal×status: 4
- signal×regime×status: 6.

Fixed gate:
- keep signal if reliability score >= 0.50.

No pseudo-count or threshold search occurred.

## 3. Chronology-safe DEV event scoring

DEV:
- targets 2022-04..2024-12
- 33 target months
- 45 individual signal events
- 20 useful events
- 25 false events.

Every DEV row was scored using only origins strictly earlier than that row.

### M0 — signal only

- Brier: **0.28727**
- log loss: 0.77065
- mean score on useful events: **0.4603**
- mean score on false calls: **0.5198**

Even signal-only historical reliability has weak/reversed discrimination:
- false calls receive a higher mean score than useful events.

### M1 — signal + live regime

- Brier: **0.29521**
- log loss: 0.78655
- mean useful score: 0.4396
- mean false score: 0.5117

Adding live regime makes Brier worse than M0.

### M2 — signal + live regime + V2 status

- Brier: **0.30317**
- log loss: 0.80560
- mean useful score: **0.4220**
- mean false score: **0.5066**

M2 is worse again.

Relative M2 Brier change:
- vs M0: **-5.54% improvement** = actually **5.54% worse**
- vs M1: **-2.70% improvement** = actually **2.70% worse**.

Therefore both preregistered Brier-improvement gates fail.

## 4. DEV union gate at fixed 0.50

### Raw ANY_VISIBLE

- events: 25
- HIGH hits: **8**
- MEDIUM hits: **2**
- false calls: **15**
- HIGH recall: **100%**
- useful-call rate: 40%
- false-call rate: 60%.

### M2-gated ANY_VISIBLE

- events: 10
- HIGH hits: **3**
- MEDIUM hits: **0**
- false calls: 7
- HIGH recall: **37.5%**
- useful-call rate: 30%
- false-call rate: 70%.

Relative to raw:
- false calls reduced **53.3%**
- but HIGH-hit retention only **37.5%**.

Pre-registered requirement:
- false reduction >=20%: PASS
- HIGH-hit retention >=90%: **FAIL badly**.

The gate removes many false calls only by also removing most useful alarms.

### Raw T0_STANDARD

- 11 events
- 4 HIGH
- 2 MEDIUM
- 5 false.

### M2-gated T0_STANDARD

- 4 events
- **1 HIGH**
- 0 MEDIUM
- 3 false.

This is unusable as an operational filter.

## 5. Examples of useful DEV signals incorrectly suppressed by M2

At the fixed 0.50 gate M2 suppresses, among others:

- origin 2022-08 -> target 2022-09 HIGH: I2 + T1_WGC
- origin 2022-10 -> target 2022-11 HIGH: A + I2 + T1_WGC
- origin 2023-07 -> target 2023-08 HIGH: A + I2 + T1_WGC
- origin 2024-02 -> target 2024-03 HIGH: I2 + T1_WGC
- origin 2024-03 -> target 2024-04 MEDIUM: H + T1_WGC
- origin 2024-06 -> target 2024-07 MEDIUM: C + H
- origin 2024-10 -> target 2024-11 HIGH: D.

Thus the failure is not only a probability-calibration issue; it directly damages the project's main requirement to retain HIGH coverage.

## 6. Opened 2025-2026 frozen transport

The opened period was scored from a fit frozen at target <=2024-12.
No 2025/2026 outcome entered the fit.

Individual event counts:
- 15 events
- 10 useful
- 5 false.

### Event-level Brier

- M0: **0.27200**
- M1: **0.28429**
- M2: **0.29145**

Again:
- signal-only is best;
- regime addition worsens;
- V2 addition worsens further.

### Raw ANY_VISIBLE

- 12 events
- 7 HIGH
- 2 MEDIUM
- 3 false
- HIGH recall **87.5%**
- useful-call rate **75%**
- false rate 25%.

### M2-gated ANY_VISIBLE

- 5 events
- **2 HIGH**
- 0 MEDIUM
- 3 false
- HIGH recall **25%**
- useful rate 40%
- false rate **60%**.

Relative to raw HIGH hits:
- retention **2/7 = 28.6%**.

False calls:
- no reduction: **3 -> 3**.

Transport therefore independently confirms that the numeric shrinkage gate is harmful.

## 7. Why opened transport fails

The frozen pre-2025 reliability estimates penalize signals that become useful in the R2-heavy 2025-2026 environment.

Examples suppressed by M2:

- 2025-01 H -> target 2025-02 HIGH
- 2025-09 H -> target 2025-10 HIGH
- 2025-04 E -> target 2025-05 MEDIUM
- 2025-10 E -> target 2025-11 HIGH
- 2025-12 E -> target 2026-01 HIGH
- 2026-02 E+H -> target 2026-03 MEDIUM
- 2026-07 G -> target 2026-08 HIGH.

E is especially revealing:
- there was no DEV event history sufficient to learn its later R2 usefulness;
- the frozen shrinkage score remains around 0.451;
- the 0.50 gate therefore suppresses all opened E events even though observed opened E events are useful.

This demonstrates structural non-stationarity / sparse-context failure.

## 8. Candidate gate

Pre-registered M2 requirements:

1. Brier improvement vs M0 >=5% -> **FAIL**
2. Brier improvement vs M1 >=2% -> **FAIL**
3. ANY_VISIBLE HIGH-hit retention >=90% -> **FAIL**
4. ANY_VISIBLE false-call reduction >=20% -> PASS

Overall:
- **CANDIDATE GATE FAIL**.

Opened 2025/2026 is not used to rescue the failed DEV gate.

## 9. Binding interpretation

The prior descriptive audit remains valid:
- live regime and V2 status contain context information;
- V2 transition months behave differently from stable months;
- 2025-2026 transition origins are especially severe.

But the present experiment shows:

> Sparse historical alarm outcomes cannot be converted into a simple stationary numeric reliability weight using this partial-pooling architecture.

The context effect changes over time:
- DEV V2 transition was mostly alarm-noise;
- opened 2025-2026 V2 transition was concentrated on HIGH-error targets.

A historical pooled probability therefore averages incompatible behaviors and suppresses useful recent signals.

## 10. Binding decision

Do not:
- deploy M2 weights;
- suppress alarms at 0.50;
- tune the threshold after seeing the failures;
- tune pseudo-counts;
- treat V2 as a universal positive/negative alarm multiplier.

No alarm weighting is authorized.

## 11. Structural implication

A further useful distinction is now clear:

**V2 can identify risk even when no existing alarm fires.**

Example:
- origin 2026-05 = V2 R2_TRANSITION
- target 2026-06 = HIGH
- no frozen A/B/C/D/E/G/H/I1/I2/T1 alarm fired.

Therefore V2's most plausible role is not necessarily to reweight existing alarms.

If pursued further, it should be tested as a separate contextual/risk channel or as part of a non-stationary/recent-regime model, under a new preregistered design.

The present shrinkage reliability model is rejected.
