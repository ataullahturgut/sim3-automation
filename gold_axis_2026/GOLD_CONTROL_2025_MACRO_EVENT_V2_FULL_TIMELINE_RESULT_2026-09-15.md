# GOLD CONTROL — 2025 MACRO EVENT V2 FULL-TIMELINE RESULT

**Date:** 2026-09-15  
**Engine:** `MACRO_EVENT_SUCCESSOR_V2`  
**Challenge:** `GOLD_CONTROL_2025_VOLATILITY_CHALLENGE_V1`  
**Evidence class:** `HISTORICAL_REPLAY_RECONSTRUCTION`  
**Production write:** NONE

---

## 1. Identity decision

The governed Macro Event identity for this 2025 challenge is `MACRO_EVENT_SUCCESSOR_V2`.

This choice was frozen before the new 2025 V2 score outputs were inspected.

`MACRO_EVENT_SUCCESSOR_V4_RELIABILITY_GATE` is not substituted into this challenge because it is a research challenger and its own preregistration states that retrospective 2025 evidence had already been inspected during design. It therefore cannot be represented as an untouched 2025 governed comparator.

No reproducible governed V3 identity replaces V2 in the current 12-engine manifest inventory.

---

## 2. Evaluation direction

The replay obeyed the engine-first rule:

1. compute V2 on every eligible calendar-2025 Employment Situation release origin;
2. retain all outputs, including `MACRO_MIXED_OR_SMALL` / `NO_SIGNAL`;
3. freeze the 11-origin engine timeline;
4. only then overlay the independently frozen 19 daily volatility event-days.

The V2 scoring function receives no volatility-event argument. No V2 threshold, weight, sign, scale rule, breadth rule or source identity was changed from the 2025 outcome.

---

## 3. 2025 data audit

Frozen V2 source run:

`6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a`

For every eligible 2025 release origin, all six frozen V2 input series are present:

- NFP actual first print;
- NFP consensus reconstruction;
- unemployment actual first print;
- unemployment consensus reconstruction;
- AHE actual first print;
- AHE consensus reconstruction.

Calendar-2025 eligible Employment Situation origins: **11**.

The late-2025 schedule is intentional, not a database gap:

- September 2025 reference release: 2025-11-20;
- October 2025 Employment Situation: officially canceled;
- November 2025 reference release: 2025-12-16.

No synthetic October release is inserted.

For the intraday reaction diagnostic, exact Twelve Data one-minute XAU bars required at 08:29 ET and 08:44 ET are present for **11/11** eligible releases.

### PIT limitation

The three consensus series are historical reconstruction from a provider `Forecast` field. Their stored metadata records that the exact historical provider pre-release update timestamp is **not proven**.

Therefore these results are valid only as retrospective historical reconstruction. They are not relabelled as genuinely issued/prospective 2025 signals.

---

## 4. V2 code/method audit

The existing V2 core passed the targeted audit without changing its frozen formula:

- actual-minus-consensus surprise;
- minimum 24 prior complete-case events;
- prior-only median/MAD robust normalization;
- deterministic IQR fallback when MAD degenerates;
- current event excluded from its own scale;
- prefix invariance;
- deterministic replay;
- gold orientation: NFP negative, unemployment positive, AHE negative;
- equal-weight three-component composite;
- strong adverse threshold `score <= -1.0` plus adverse breadth >=2;
- strong supportive threshold `score >= +1.0` plus supportive breadth >=2.

The defect in the old evaluation path was not the V2 score formula itself. The older reaction validator was designed around a limited historical strong-event set and was not suitable for a complete 2025 challenge because it did not expose every eligible 2025 release and false-warning opportunity.

A new fail-closed 2025 full-event-timeline runner was therefore added without altering the V2 core.

---

## 5. Complete calendar-2025 Macro Event V2 timeline

| # | Release date | Reference month | V2 state | Score | Adverse breadth | Supportive breadth | XAU R15 |
|---:|---|---|---|---:|---:|---:|---:|
| 1 | 2025-01-10 | 2024-12 | `MACRO_MIXED_OR_SMALL` | -0.5725 | 2 | 0 | -0.0620% |
| 2 | 2025-02-07 | 2025-01 | `MACRO_MIXED_OR_SMALL` | -0.5787 | 2 | 1 | -0.0639% |
| 3 | 2025-03-07 | 2025-02 | `MACRO_MIXED_OR_SMALL` | +0.2551 | 0 | 2 | +0.3374% |
| 4 | 2025-04-04 | 2025-03 | `MACRO_MIXED_OR_SMALL` | -0.1219 | 1 | 1 | -0.2612% |
| 5 | 2025-05-02 | 2025-04 | `MACRO_MIXED_OR_SMALL` | +0.0775 | 1 | 1 | -0.0583% |
| 6 | 2025-06-06 | 2025-05 | `MACRO_MIXED_OR_SMALL` | -0.2752 | 2 | 0 | -0.1376% |
| 7 | 2025-07-03 | 2025-06 | `MACRO_MIXED_OR_SMALL` | -0.3644 | 2 | 1 | -1.1083% |
| 8 | 2025-08-01 | 2025-07 | `MACRO_MIXED_OR_SMALL` | +0.1279 | 0 | 1 | +0.9520% |
| 9 | 2025-09-05 | 2025-08 | `MACRO_MIXED_OR_SMALL` | +0.2091 | 0 | 1 | +0.7183% |
| 10 | 2025-11-20 | 2025-09 | `MACRO_MIXED_OR_SMALL` | +0.1938 | 1 | 2 | -0.0148% |
| 11 | 2025-12-16 | 2025-11 | `MACRO_MIXED_OR_SMALL` | +0.6232 | 1 | 2 | +0.1969% |

Calendar-2025 strong V2 states: **0 / 11**.  
Calendar-2025 `NO_SIGNAL` states: **11 / 11**.

No strong V2 warning existed to carry into the volatility overlay.

---

## 6. Overlay with the frozen 19 volatility event-days

The primary Macro Event comparison is same-New-York-calendar-date only. V2 first becomes available when the scheduled Employment Situation release arrives at 08:30 ET; it is not a day-ahead signal and it is not carried forward to unrelated later dates.

Of the frozen 19 volatility event-days, only **2** coincide with an eligible Employment Situation release:

| Volatility date | Daily event | Macro eligibility | V2 state | Result |
|---|---|---|---|---|
| 2025-04-04 | DOWN / EXTREME | eligible release | `MACRO_MIXED_OR_SMALL` | `NO_SIGNAL` |
| 2025-08-01 | UP / MAJOR | eligible release | `MACRO_MIXED_OR_SMALL` | `NO_SIGNAL` |

The other **17 / 19** volatility event-days are `NOT_APPLICABLE` for this event-clock engine, not Macro Event misses.

Challenge summary:

- frozen volatility event-days: **19**;
- event-days with eligible Employment Situation release: **2**;
- event-days with no Macro Event origin: **17 NOT_APPLICABLE**;
- same-event strong V2 signals: **0**;
- same-event direction-aligned strong signals: **0**;
- same-event direction-opposed strong signals: **0**;
- eligible same-day volatility events with V2 `NO_SIGNAL`: **2**;
- strong V2 signals on non-volatility release days: **0**.

Zero false warnings must **not** be interpreted as high precision: V2 issued zero strong warnings in calendar 2025.

---

## 7. Native intraday-reaction diagnostic

The event-study reaction data are complete for all 11 releases.

Several releases produced materially visible 15-minute XAU moves despite V2 remaining `MACRO_MIXED_OR_SMALL`, including:

- 2025-07-03: R15 = **-1.1083%**;
- 2025-08-01: R15 = **+0.9520%**;
- 2025-09-05: R15 = **+0.7183%**.

This is evidence that the frozen V2 strong-state gate was highly selective in 2025. It is not permission to lower the V2 threshold after seeing these outcomes.

---

## 8. Interpretation

For the governed 2025 volatility challenge, `MACRO_EVENT_SUCCESSOR_V2` is the methodologically defensible Macro Event comparator because it is the current governed identity and its rule predates this replay.

Its 2025 result is nevertheless weak as a volatility-warning contributor:

- it produced **no strong event signals**;
- it therefore caught **none** of the two volatility event-days on which it was actually eligible;
- it cannot explain the other 17 volatility event-days because those dates had no Employment Situation origin;
- zero false warnings arise from zero strong warnings and are not evidence of useful selectivity.

V2 should remain interpreted as a release-time macro-surprise context engine, not a generic daily volatility detector.

A richer Macro Event successor may be scientifically justified for future research, particularly because large R15 reactions occurred while V2 remained mixed/small. Any such successor must be separately named, designed/tuned without using this locked 2025 challenge as a training target, and validated on later genuinely unseen evidence.

`MACRO_EVENT_SUCCESSOR_V4_RELIABILITY_GATE` may continue as a research family but cannot replace V2 retrospectively and then claim unbiased 2025 challenge evidence.

---

## 9. Reproducibility

Replay tool:

`gold_axis_2026/tools/run_macro_event_v2_2025_volatility_challenge_v1.py`

Preregistration:

`gold_axis_2026/GOLD_CONTROL_2025_MACRO_EVENT_V2_FULL_TIMELINE_PREREG_2026-09-15.md`

Targeted CI validates:

- existing V2 core tests;
- challenge separation;
- all 11 calendar-2025 release origins;
- complete six-series source coverage;
- 08:30 ET release-clock contract;
- 11/11 R15 data coverage;
- zero proven exact provider pre-release consensus timestamps;
- no production/database writes.
