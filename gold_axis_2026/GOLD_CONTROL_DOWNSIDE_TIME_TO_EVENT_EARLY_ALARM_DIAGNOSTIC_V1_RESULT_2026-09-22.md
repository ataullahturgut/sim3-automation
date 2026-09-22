# GOLD CONTROL — TIME-TO-EVENT / EARLY-ALARM DIAGNOSTIC V1 RESULT

**Date:** 2026-09-22  
**Identity:** `DOWNSIDE_TIME_TO_EVENT_EARLY_ALARM_DIAGNOSTIC_V1_RESEARCH`  
**Preregistration commit:** `6d7d3394f6edb40d78e66d7892af95fe23311e6f`  
**Parent forecast evidence:** `gold-downside-consensus-veto-v1-20260922` @ `4f6efce38d636695d44d2fbb3282fa0ec78cc0c2`  
**DB access:** read-only  
**Final status:** `EARLY_ALARM_TIMING_NOT_SUPPORTED`

## 1. Execution integrity

The frozen parent SQRT-HAR-DR annual-origin forecast panel contained 1,023 rows. The retained 5-minute Gold series produced 1,368 daily observations from 2020-04-06 through 2026-08-31.

Daily close returns reconstructed from the DB aligned with the frozen parent `target_close_return` field to maximum absolute error `3.47e-18`.

Formation supervised-history counts were reproduced exactly after the frozen 22-day HAR warm-up:
- 2022: 323
- 2023: 528
- 2024: 731
- 2025: 936
- 2026: 1173

The independently reconstructed formation Q05 thresholds matched the frozen parent `extreme_return_threshold` exactly in every year.

## 2. Primary 2022–2024 falsification result

A t+1 false direction interpretation is a frozen SQRT high-risk alarm for which the origin-to-t+1 close return is nonnegative.

Pooled 2022–2024:

| Cohort | n | convert by t+2 | convert by t+3 | convert by t+5 | Q25 excursion by t+3 | Q05 excursion by t+3 |
|---|---:|---:|---:|---:|---:|---:|
| ALARM_FALSE_T1 | 16 | 31.25% | 37.50% | 43.75% | 31.25% | 18.75% |
| CONTEXT_CONTROL | 26 | 23.08% | 23.08% | 30.77% | 15.38% | 7.69% |
| BROAD_CONTROL | 311 | 24.44% | 37.62% | 48.55% | 22.19% | 4.50% |

Against the intended CONTEXT_CONTROL, t+3 conversion looked directionally interesting:
- absolute lift: +14.42 percentage points;
- risk ratio: 1.625;
- Q25 excursion lift: +15.87 pp;
- Q05 excursion lift: +11.06 pp.

However CONTEXT_CONTROL had only 26 pooled observations, below the preregistered minimum support of 30. The frozen rule therefore requires the result to be judged against BROAD_CONTROL.

Against BROAD_CONTROL:
- t+3 conversion: 37.50% versus 37.62%;
- absolute lift: -0.12 pp;
- risk ratio: 0.997;
- Q25 excursion lift: +9.06 pp;
- Q05 excursion lift: +14.25 pp.

The required conversion-rate condition therefore fails.

## 3. Annual t+3 anatomy

- 2022: alarm false-t1 conversion 40.0% (n=5) vs context 18.18% (n=11), +21.82 pp.
- 2023: alarm 0% (n=1) vs context 50.0% (n=4); context support is insufficient.
- 2024: alarm 40.0% (n=10) vs context 18.18% (n=11), +21.82 pp.
- 2025 stress: alarm 42.22% (n=45) vs context 50.0% (n=18), -7.78 pp.
- 2026 stress: alarm 40.54% (n=74) vs context 20.0% (n=10), +20.54 pp.

The sign of the context lift is unstable and the primary pre-2025 alarm sample is very small.

## 4. Frozen decision

`EARLY_ALARM_TIMING_NOT_SUPPORTED`

The diagnostic does **not** support reformulating the current problem as a time-to-event/hazard model under V1.

There is a weak descriptive severity observation: pre-2025 false-t1 alarms had more Q25/Q05 adverse excursions than the broad control even though their t+3 sign-conversion probability was essentially identical. This is not enough to pass the preregistered early-alarm timing gate and must not be used as a result-dependent rescue.

## 5. Scientific implication

The evidence favors returning to the other preregistered branch of the roadmap: acquire genuinely new direction-resolving information rather than add another timing/classifier layer to the same Gold history.

Priority remains:
1. Gold options skew / volatility surface / put-call asymmetry;
2. Gold futures positioning / volume / open interest / order-flow imbalance;
3. daily origin-safe US real yield;
4. long-history daily DXY / broad USD;
5. liquidity/spread or futures basis;
6. macro-surprise direction.

No runtime promotion, selector/ensemble change or production write is authorized.
