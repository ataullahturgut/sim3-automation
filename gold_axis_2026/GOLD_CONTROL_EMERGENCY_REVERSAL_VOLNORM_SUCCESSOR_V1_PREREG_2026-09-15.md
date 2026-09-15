# GOLD CONTROL — EMERGENCY REVERSAL VOLNORM SUCCESSOR V1 PREREGISTRATION

**Date frozen:** 2026-09-15  
**Identity:** `EMERGENCY_REVERSAL_VOLNORM_SUCCESSOR_V1`  
**Status:** `FROZEN_BEFORE_2025_REPLAY`  
**Production authority:** NONE  
**Database writes:** NONE

## 1. Purpose and predecessor boundary

This successor replaces only the research logic of the old fixed-percentage `EMERGENCY_REVERSAL` rule. The old R4.1 `%4` implementation remains untouched as a historical baseline and is not rewritten.

The successor's role is narrowly defined:

> detect a statistically abnormal reversal from a running price extreme after a statistically abnormal directional leg has first been established.

It is **not** a generic daily direction model, not a monthly forecast-level model, not a structural-break ground-truth generator and not a trading-action engine.

The monthly forecast reference is removed from this successor. Daily XAU price is no longer compared with a forecast of the target month's average price level.

## 2. Authority rationale frozen before 2025

The design follows four methodological points established before the 2025 replay:

1. financial jump/extreme-move methods standardize moves by local/time-varying volatility rather than treating one raw percentage as equally exceptional in every volatility regime;
2. drawdown/reversal is path-dependent and naturally defined relative to running peaks/troughs;
3. gold volatility is time-varying and persistent, making a fixed raw `%4` threshold structurally fragile;
4. Directional Change research explicitly treats fixed thresholds as a robustness limitation and supports dynamic/adaptive thresholds.

Primary methodological references:

- Lee, S. S. & Mykland, P. A. (2008), *Jumps in Financial Markets: A New Nonparametric Test and Jump Dynamics*, Review of Financial Studies 21(6), 2535–2563, DOI `10.1093/rfs/hhm056`.
- Andersen, T. G., Bollerslev, T., Diebold, F. X. & Labys, P. (2003), *Modeling and Forecasting Realized Volatility*, Econometrica 71(2), 579–625, DOI `10.1111/1468-0262.00418`.
- Arouri, M. E. H., Hammoudeh, S., Lahiani, A. & Nguyen, D. K. (2012), *Long memory and structural breaks in modeling the return and volatility dynamics of precious metals*, Quarterly Review of Economics and Finance 52(2), 207–218, DOI `10.1016/j.qref.2012.04.004`.
- Alkhamees, N. & Fasli, M. (2017/2018), *A Directional Change Based Trading Strategy with Dynamic Thresholds*, IEEE DSAA, DOI `10.1109/DSAA.2017.48`.

These references support volatility normalization, path dependence and adaptive thresholds. They do **not** establish a universal `2.0` or `3.0` threshold for this Gold Control motor.

## 3. Source contract

Research source for both formation feasibility and the later 2025 replay:

- provider: Twelve Data;
- symbol: `XAU/USD`;
- interval: `1h`;
- requested timezone: `America/New_York`;
- selected bar: hourly bar opened at `16:00:00`; its close represents the end of the 16:00–17:00 ET hour;
- selected daily value: positive finite `close`;
- no interpolation;
- no forward fill;
- no provider substitution.

This is a **historical research reconstruction**, not the canonical exact-16:59 1-minute NY17 runtime series and not an official settlement/fixing.

Coverage gate for every complete calendar year used in a run:

`selected_weekday_closes / calendar_weekdays >= 0.90`.

Failure of this gate -> `BLOCKED_DATA_COVERAGE`; thresholds may not be relaxed to rescue the run.

## 4. Chronology split

### Formation / feasibility

`2022-01-01 .. 2024-12-31`

This period may be used only to verify that the frozen detector is numerically stable, nondegenerate and reproducible. No 2025 observation or 2025 challenge event may enter this stage.

### Locked retrospective challenge

`2025-01-01 .. 2025-12-31`

The 2025 run is permitted only after:

1. this preregistration exists in Git history;
2. implementation tests pass;
3. formation-only execution passes the frozen feasibility gates;
4. the implementation/configuration hash is recorded.

No parameter may be changed after 2025 output is inspected and then reported under this identity.

## 5. Frozen mathematical definition

Let `P_t` be the selected daily close and

`r_t = ln(P_t / P_{t-1})`.

Local volatility is strictly lagged:

`sigma20_t = sample_std(r_{t-20}, ..., r_{t-1})`.

The current return is excluded from its own scale. At least 20 prior returns are required.

### 5.1 Path-volatility scale

For a running extreme established at observed index `e` and a later observed index `t`:

`path_sigma(e,t) = sqrt(sum_{j=e+1..t} sigma20_j^2)`.

No future sigma and no current-return inclusion in `sigma20_j` are permitted.

### 5.2 Initialization

Before a directional leg is established the detector maintains both a running trough and running peak.

From a running trough `L_e`:

`Z_up(e,t) = ln(P_t / L_e) / path_sigma(e,t)`.

From a running peak `H_e`:

`Z_down(e,t) = ln(P_t / H_e) / path_sigma(e,t)`.

The first side to reach the frozen MAJOR threshold establishes the initial leg:

- `Z_up >= 2.0` -> `UP_LEG`;
- `Z_down <= -2.0` -> `DOWN_LEG`.

Initial leg establishment is **not** a reversal alert.

### 5.3 Reversal detection

While in `UP_LEG`:

- every new higher close resets the running peak to that close;
- otherwise compute the volatility-normalized drawdown from that peak;
- `Z_down <= -2.0` -> one new `DOWN_ALERT`, then state flips to `DOWN_LEG` and the current close becomes the new running trough.

While in `DOWN_LEG`:

- every new lower close resets the running trough;
- otherwise compute the volatility-normalized drawup from that trough;
- `Z_up >= +2.0` -> one new `UP_ALERT`, then state flips to `UP_LEG` and the current close becomes the new running peak.

An alert is emitted only on the transition date. Continued state is not a repeated alert.

Severity annotation:

- `MAJOR`: absolute reversal score `>= 2.0` and `< 3.0`;
- `EXTREME`: absolute reversal score `>= 3.0`.

## 6. Threshold governance

Frozen values:

- volatility window: `20` prior observed returns;
- leg-establishment threshold: `2.0` path-vol units;
- reversal threshold: `2.0` path-vol units;
- extreme annotation: `3.0` path-vol units.

These values are intentionally **not optimized on 2022–2024**. They reuse Gold Control's already-frozen `2σ/3σ` abnormality tiers, but on a different statistic: cumulative path movement normalized by accumulated lagged path variance rather than a one-day return z-score.

Therefore formation results cannot trigger threshold optimization under this identity.

If formation evidence shows numerical degeneracy, this identity is rejected and a separately named successor is required.

## 7. Formation-only feasibility gates

Before 2025 may run:

- source coverage gate passes for 2022, 2023 and 2024;
- deterministic repeat equality: exact;
- prefix invariance: adding future observations cannot change any prior state or alert;
- current return excluded from local volatility: tested;
- no monthly forecast input is consumed;
- no 2025 date is read;
- no production/database write occurs;
- at least `3` reversal alerts are emitted over the full formation interval;
- alert count must be `< 20%` of eligible post-warmup observations.

Failure -> `REJECTED_FORMATION_DEGENERATE_NO_2025_REPLAY`.

## 8. 2025 engine-first evaluation lock

The frozen 19 volatility dates are not passed into the detector.

Order of operations:

1. retrieve/reconstruct the complete eligible 2025 daily source timeline;
2. run the frozen successor over the full timeline;
3. save every daily state, score, extreme date, state age and every new `UP_ALERT`/`DOWN_ALERT`;
4. hash/freeze that engine output;
5. only then load/overlay the independent frozen 19-event volatility inventory.

Primary overlay is **same governed date** because this is an end-of-day reversal detector/confirmation signal, not a day-ahead predictor.

Report separately:

- total 2025 reversal alerts;
- UP_ALERT / DOWN_ALERT counts;
- same-day overlap with frozen volatility events;
- same-day direction-aligned overlap;
- same-day direction-opposed overlap;
- volatility events with no reversal alert;
- reversal alerts with no same-day frozen volatility event.

The last item is reported as `NO_SAME_DAY_VOLATILITY_OVERLAY`, not automatically called a universal false alarm, because a path-reversal event and a one-day abnormal-return event are not identical targets.

Lead/lag at ±1 and ±3 governed observations may be reported descriptively only and may not replace the frozen same-day primary comparison after results are seen.

## 9. Promotion boundary

A positive 2025 retrospective result is not prospective evidence and does not automatically promote this successor into the 12 governed runtime identities.

Possible status after replay:

- `PROMISING_RETROSPECTIVE_RESEARCH`;
- `INSUFFICIENT_SUPPORT`;
- `REJECTED_NO_INCREMENTAL_SIGNAL`;
- `BLOCKED_DATA`.

Promotion requires a later architecture decision and ultimately prospective shadow evidence.
