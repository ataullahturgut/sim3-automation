# GOLD CONTROL — 2025 EMERGENCY REVERSAL VOLNORM V3 RESULT

**Date:** 2026-09-15  
**Identity:** `EMERGENCY_REVERSAL_VOLNORM_SUCCESSOR_V3`  
**Evidence:** `HISTORICAL_REPLAY / RETROSPECTIVE_DIAGNOSTIC`  
**Status:** `PROMISING_RETROSPECTIVE_RESEARCH / INSUFFICIENT_SUPPORT_FOR_PROMOTION`  
**Production/database write:** NONE

---

## 1. Why V3 is the scored identity

The original R4.1 Emergency Reversal used a fixed raw `%4` displacement/reversal rule and depended on a monthly forecast level. Authority review found that a volatility-normalized path-reversal formulation is more appropriate for Gold Control research because exceptional movement should be judged relative to time-varying local volatility and because reversal is naturally defined from running peaks/troughs.

The old `%4` code remains untouched as a historical baseline.

Successor history:

- **V1:** blocked before 2025 because its 16:00 ET research source failed the frozen 2023 coverage gate.
- **V2:** formation passed, but its first 2025 engine run exposed a source-governance bug: non-weekday provider bars entered the path. The entire V2 2025 result was invalidated and withdrawn before use as performance evidence.
- **V3:** corrective-only successor. It keeps the same pre-frozen detector mathematics and 14:00 ET source clock but explicitly restricts the governed path to Monday-Friday dates and enforces `selected dates <= calendar weekdays`.

No threshold, volatility window, source hour or state-transition rule was changed using the invalid V2 performance output.

---

## 2. Frozen V3 detector before the valid 2025 replay

Formation-only workflow run: `35023205527` — PASS.

Frozen identity:

- configuration SHA-256: `fdb2c6238fc194afd9c5a253ae232790bdde5b6faa49cbcd96811972d5a83a84`;
- implementation SHA-256: `4adcec3043b141babd38a7bef9ed854f3fdb868bd84a88a32e835fa1e6921cbd`;
- formation timeline SHA-256: `1600b810e4ea724f6f863ca11505d30e49c3288271476dd8be0f0b7ac14aff69`.

Frozen detector:

- Twelve Data `XAU/USD`, 1-hour, `America/New_York`;
- exact 14:00 ET hourly-open bar close;
- Monday-Friday only;
- 20 immediately prior observed returns for local volatility;
- current return excluded from its own volatility estimate;
- running peak/trough path movement normalized by accumulated lagged path variance;
- directional leg threshold: 2.0 path-vol units;
- reversal threshold: 2.0 path-vol units;
- EXTREME annotation threshold: 3.0;
- no monthly forecast input;
- no fixed raw-percent threshold.

Formation 2022–2024 produced 11 reversal transitions over 750 eligible post-warmup rows (1.47% alert rate) with deterministic repeat equality and prefix invariance. No 2025 observation was consumed during V3 formation.

---

## 3. Valid 2025 engine-first execution

Corrected challenge workflow run: `35023484477` — PASS.

The challenge remained two-stage:

1. V3 generated and froze the complete eligible 2025 engine timeline without loading the 19-event volatility inventory.
2. Only after the engine timeline was hashed was the independent frozen 19-event inventory overlaid.

2025 source accounting:

- calendar Monday-Friday dates: 261;
- selected valid 14:00 weekday closes: 256;
- coverage: 98.08%;
- weekend engine rows: 0;
- weekend provider bars rejected over the 2022–2025 source retrieval: 14;
- engine timeline SHA-256: `5b2470179c6d506427ce71287352f24f8fc7519c439bfeec9394c1cf57e8ec39`.

2025 V3 alert count:

- total reversal alerts: **6**;
- UP alerts: **3**;
- DOWN alerts: **3**;
- MAJOR alerts: **4**;
- EXTREME alerts: **2**.

---

## 4. Complete 2025 reversal-alert inventory

| Date | Alert | V3 severity | V3 path score | Reference extreme | Same-day frozen volatility event |
|---|---|---|---:|---|---|
| 2025-03-28 | UP_ALERT | MAJOR | +2.0370 | 2024-04-30 trough | none |
| 2025-04-04 | DOWN_ALERT | EXTREME | -3.1122 | 2025-04-02 peak | **DOWN / EXTREME — aligned** |
| 2025-04-09 | UP_ALERT | MAJOR | +2.1865 | 2025-04-07 trough | **UP / EXTREME — aligned** |
| 2025-10-09 | DOWN_ALERT | MAJOR | -2.5269 | 2025-10-08 peak | none |
| 2025-10-13 | UP_ALERT | MAJOR | +2.3060 | 2025-10-09 trough | **UP / MAJOR — aligned** |
| 2025-10-21 | DOWN_ALERT | EXTREME | -4.5890 | 2025-10-20 peak | **DOWN / EXTREME — aligned** |

No 2025 V3 alert coincided with a frozen volatility event in the opposite direction.

---

## 5. Frozen 19-event overlay

Primary same-date accounting:

- frozen volatility event-days: **19**;
- V3 reversal alerts: **6**;
- same-date direction-aligned overlaps: **4**;
- same-date direction-opposed overlaps: **0**;
- frozen volatility event-days with no V3 reversal alert: **15**;
- V3 alerts with no same-date frozen volatility overlay: **2**;
- event-days not testable because the V3 source date was absent: **0**.

Descriptive ratios only:

- 4/6 V3 alerts (66.7%) coincide on the same date with a frozen abnormal-volatility event;
- 4/19 frozen volatility event-days (21.1%) coincide with a V3 reversal transition.

These percentages are **not** universal precision/recall claims because the V3 target is a path reversal while the 19-event inventory is a one-day abnormal-return target. The two unmatched V3 alerts are therefore labelled `NO_SAME_DAY_VOLATILITY_OVERLAY`, not automatically universal false alarms.

Secondary descriptive proximity, frozen after engine output:

- direction-aligned V3 alert within ±1 observed source day: **5/19** event-days;
- direction-aligned V3 alert within ±3 observed source days: **7/19** event-days.

The same-date comparison remains the primary result; these windows may not replace it post hoc.

---

## 6. Relevant downside behavior

The successor directly addresses an area where a trend-state motor can be weak: sharp reversals against an established path.

Among the frozen DOWN volatility events:

- **2025-04-04 DOWN / EXTREME:** exact same-day V3 `DOWN_ALERT`, V3 score `-3.1122`;
- **2025-10-21 DOWN / EXTREME:** exact same-day V3 `DOWN_ALERT`, V3 score `-4.5890`;
- 2025-10-17 DOWN / MAJOR: no same-day V3 alert; nearest aligned V3 DOWN alert is 2 observed source days away;
- 2025-02-14 and 2025-12-29 DOWN events: no nearby same-date reversal transition.

Thus V3 does not solve all downside volatility, but it supplies sparse, role-specific reversal evidence on some of the largest downside events.

---

## 7. Interpretation

The valid V3 replay is materially more informative than the old raw `%4` rule as a research architecture:

- it adapts to the prevailing volatility regime;
- it operates directly on the price path rather than requiring a monthly average-level forecast;
- its alerts are sparse rather than continuously active;
- four of six 2025 alerts coincide exactly with frozen abnormal-volatility dates;
- every same-date overlap is direction-aligned;
- two exact DOWN/EXTREME event-days are captured by DOWN reversal alerts.

However, the sample remains small: only six reversal transitions occurred in 2025. In addition, the research process had already observed 2025 outcomes through an invalid predecessor execution, even though V3 parameters were not changed from those results. Therefore this replay is **not** human-blind OOS or prospective evidence.

Current research status:

`PROMISING_RETROSPECTIVE_RESEARCH / INSUFFICIENT_SUPPORT_FOR_PROMOTION`

V3 should remain a research successor until later prospective-shadow evidence tests whether its sparse reversal alerts continue to add information beyond FAST and other governed contexts.

---

## 8. Reproducibility and invalid-result guard

Valid formation run: `35023205527`.  
Valid corrected 2025 run: `35023484477`.

The invalid V2 run `35022855051` and all of its 2025 scores/counts are explicitly withdrawn and must not be used in aggregate motor comparisons.

No database or production signal state was written by V1, V2 or V3 research execution.