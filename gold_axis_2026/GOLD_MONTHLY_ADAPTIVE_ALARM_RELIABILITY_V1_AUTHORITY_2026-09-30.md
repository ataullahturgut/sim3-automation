# GOLD MONTHLY — Adaptive Alarm Reliability V1 Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED / CHRONOLOGY-SAFE ADAPTATION AUDIT

## 1. Question

Prior audits show that alarm ecology is non-stationary:

- older history is dominated by T1_WGC / I2 with many false calls;
- late R2 is dominated by E / H with much cleaner observed outcomes;
- stationary pooled shrinkage suppresses useful recent alarms.

This experiment asks:

> Can a chronology-safe recency-adaptive reliability process, with its adaptation mechanism selected only from pre-2025 history, improve alarm reliability and naturally shift its signal beliefs as the market changes?

This experiment does not retune raw alarms, V2, regimes, or severity definitions.

## 2. Frozen source

Use:
- `GOLD_MONTHLY_ALARM_REGIME_V2_RELIABILITY_AUDIT_V1_2026-09-30.json`
- 58 monthly rows;
- individual frozen signals:
  - A, B, C, D, E, G, H, I1, I2, T1_WGC.

Outcome for an active individual signal:
- useful = HIGH_HIT or MEDIUM_HIT;
- false = FALSE_CALL.

OFF rows are not signal-event observations.

## 3. Chronology

For scoring an alarm at origin month t:
- only alarm outcomes from rows with origin < t may be used;
- no same-origin or future target outcome enters the score.

This matches real-time use because the previous monthly target outcome is known by the next month-end origin.

## 4. Reliability estimator

For every scoring origin, use weighted prior alarm events.

Weighted global mean:

`m_global = (weighted_useful_all + 1) / (weighted_events_all + 2)`

Signal posterior mean:

`m_signal = (weighted_useful_signal + 4*m_global) / (weighted_events_signal + 4)`

The fixed prior strength is **4** and is not tuned.

No regime, V2, or market-state variable enters this V1 score. The goal is to isolate whether recency adaptation alone solves the non-stationarity problem.

## 5. Frozen memory candidates

The following candidates are fixed before results.

### EXPANDING
- all prior signal events have weight 1.

### Rolling windows
- ROLL_12
- ROLL_18
- ROLL_24
- ROLL_36

An event is included if its origin is within the last W months before the scoring origin.

### Exponential decay
- HL_6
- HL_12
- HL_18
- HL_24

For an event age d months:

`weight = 0.5 ** (d / half_life)`

No other window or half-life may be added after results.

## 6. Pre-2025 mechanism selection

Selection period:
- target months 2022-04..2024-12.

Every event is scored walk-forward using only earlier origins.

For each candidate report:
- event count;
- Brier score;
- log loss;
- mean score on useful events;
- mean score on false calls.

Selection order:
1. lowest Brier;
2. if tied within 1e-12, lowest log loss;
3. if still tied, lexical candidate name.

2025/2026 data are forbidden from mechanism selection.

## 7. Frozen 0.50 gate diagnostic

For each candidate, use the fixed threshold:

`KEEP active signal if adaptive reliability >= 0.50`

Threshold 0.50 is not optimized.

Reconstruct:
- ANY_VISIBLE_GATED: any kept signal among all ten;
- T0_STANDARD_GATED: any kept signal among A/B/C/D/H.

Report against raw frozen unions:
- events;
- HIGH hits;
- MEDIUM hits;
- false calls;
- HIGH recall;
- elevated recall;
- false-call rate;
- useful-call rate;
- HIGH-hit retention;
- false-call reduction.

## 8. Evidence gate on pre-2025 DEV

The selected mechanism is considered an **adaptive candidate** only if all hold on chronology-safe DEV:

1. selected mechanism is not EXPANDING;
2. Brier improvement vs EXPANDING >= 5%;
3. mean score useful > mean score false;
4. selected ANY_VISIBLE_GATED retains >= 80% of raw ANY_VISIBLE HIGH hits;
5. selected ANY_VISIBLE_GATED reduces raw ANY_VISIBLE false calls by >= 20%.

If this fails:
- do not deploy the adaptive gate;
- do not tune windows, half-lives, prior strength, or 0.50 threshold.

## 9. Opened 2025-2026 sequential transport

After the mechanism is selected using pre-2025 only:

- keep the selected mechanism fixed;
- score 2025-01..2026-08 sequentially;
- at each origin t use only rows with origin < t;
- once a 2025/2026 outcome becomes historically available, it may update later scores exactly as a real online system would.

Thus:
- 2025/2026 outcomes do not select the mechanism;
- but the frozen adaptive process is allowed to learn from prior realized 2025/2026 outcomes when scoring later months.

Report:
- selected adaptive event Brier/log loss;
- EXPANDING baseline on the same opened rows;
- fixed 0.50 union diagnostics.

Opened data cannot rescue a failed DEV evidence gate.

## 10. Adaptation-path diagnostics

At frozen checkpoints:
- 2024-12
- 2025-06
- 2025-12
- 2026-04
- 2026-06
- 2026-08

report latent reliability scores for all ten signals under:
- EXPANDING;
- selected mechanism.

Special focus:
- E
- H
- T1_WGC
- I2

Also report their weighted event mass and weighted useful mass.

This answers whether the adaptive process would naturally move away from old alarm ecology and toward newly successful signals.

## 11. Governance

Forbidden:
- using 2025/2026 to choose memory length;
- adding a new candidate after results;
- changing prior strength;
- changing the 0.50 gate;
- changing raw alarm definitions;
- changing regime/V2 definitions;
- forecast correction;
- model routing.

This experiment tests only chronology-safe recency adaptation.
