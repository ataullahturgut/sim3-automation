# GOLD CONTROL — SIMPLE EXPERT SOURCE-BINDING V2 CHANGE CONTROL

**Freeze date:** 2026-09-03  
**Status:** `FROZEN_BEFORE_SOURCE_BINDING_RESULT`  
**Parent manifest:** v1.23  
**Canonical branch:** `gold-r4-direction-engine`

## 1. Problem statement

The governed multi-expert registry contains reproducible formulas for `RW_R1` and `MOMENTUM_3M_R1`, but both forward H=1 experts are blocked by `BLOCKED_FORWARD_MONTHLY_LEVEL_SOURCE_NOT_BOUND`.

This change control addresses only that source-binding blocker. It does **not** alter the H=1 target, selector policy, ensemble policy, direction system, Causal Patch, VW, Macro Event, Emergency, BOCPD, GVZ, or any position/action mapping.

The archived R1 identities remain immutable historical/replay evidence. A new forward source binding receives new model-version identities and must never be represented as recovery of an original production source that was not retained.

Reserved forward identities:

- `RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND`
- `MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND`

## 2. Authority and governance basis

The project applies the following principles as internal engineering governance:

1. Federal Reserve/OCC/FDIC SR 26-2 (2026) emphasizes conceptual soundness, clear model limitations, ongoing monitoring, outcome analysis, validation, and documented adjustments. Gold Control is not claiming banking-regulatory applicability; these are used as model-risk-management analogies.
2. NIST AI RMF Govern 1.6 supports maintaining an inventory of systems/models and their operational status.
3. Hyndman & Athanasopoulos, *Forecasting: Principles and Practice*, requires forecasting evaluation to preserve temporal order; rolling forecasting origins use only observations prior to the evaluated outcome.
4. CME/EBS identifies 17:00 ET as the trade-date roll for Spot FX & Precious Metals.
5. Twelve Data documents that IANA timezones can be requested for intraday intervals and that `datetime` identifies the opening time of the requested interval.

Project-internal source evidence already frozen before this change:

- `PATCH_MONTHLY_LEVEL_BRIDGE_V6_SOURCE_PASS`;
- `gold_axis_2026/patch_repro_v1/prospective_monthly_level_v6_source_evidence.json`;
- the audited hourly source semantic is Twelve Data `XAU/USD`, `1h`, `America/New_York`, selecting the `16:00:00` bar close as the end of the 16:00–17:00 ET hour;
- V6 showed 43/43 anchor-month coverage, no low-count months, level correlation `0.9999928156091437`, median absolute level gap `6.6813 bps`, p95 gap `22.5423 bps`, monthly-return correlation `0.9990941273318381`, and return-sign agreement `0.9761904761904762` versus the daily-training monthly level.

## 3. Frozen source binding

New source identity:

`SIMPLE_EXPERT_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V2`

Construction:

- provider: Twelve Data;
- symbol: `XAU/USD`;
- interval: `1h`;
- requested timezone: `America/New_York`;
- select only bars whose returned `datetime` ends in `16:00:00`;
- treat each selected close as the end-of-hour value for the 16:00–17:00 ET interval;
- for each completed calendar month, use the arithmetic mean of positive finite selected closes;
- require at least 15 unique selected trading dates per month;
- reject duplicate dates;
- no interpolation;
- no forward fill;
- no provider substitution;
- no relabelling as LBMA, settlement, official close, CORE5, World Bank, or `XAU_EOD_TWELVE_NY17`;
- the source is a separately named monthly measurement built from the already audited Twelve hourly semantic.

The historical validation fetch must cover at least `2022-09-01` through `2026-06-30`, because the January 2023 Momentum forecast requires four completed input months (`2022-09..2022-12`).

Because the first three required months precede the already frozen V6 hourly-anchor audit window, the new validation must independently extend the same source-materiality audit over **all required source months `2022-09..2026-06`** against the frozen CORE5 monthly target artifact. The inherited V6 materiality thresholds remain unchanged:

- level correlation `>= 0.995`;
- median absolute relative level gap `<= 50 bps`;
- p95 absolute relative level gap `<= 100 bps`;
- consecutive monthly log-return correlation `>= 0.95`;
- monthly return direction agreement `>= 0.80`.

This extension is a source-semantic gate, not a forecast-performance tuning step.

## 4. Frozen formulas

### Random Walk V2

For target month `t`, let `L[p]` be the source-bound monthly level for completed month `p=t-1`.

`forecast_RW(t) = L[t-1]`

No drift, scaling, calibration, or post-result adjustment is permitted.

### 3M Momentum V2

Use the four completed source-bound monthly levels `L[t-4], L[t-3], L[t-2], L[t-1]`.

For the last three simple returns:

`r_i = L[i] / L[i-1] - 1`

then:

`forecast_MOM(t) = L[t-1] * (1 + mean(last 3 simple returns))`

This preserves the current `MOMENTUM_3M_R1` mathematical formula; only the explicitly named forward input measurement changes, therefore the model version changes to V2.

## 5. Locked historical evaluation

Target definition remains the frozen H=1 target: **next calendar month's average XAU/USD price**.

Locked evaluation window:

`2023-01 → 2026-07`, `N=43`.

Historical actuals and archived R1 comparators must reconcile to the immutable `locked_replay_v6_monthly_level_43.csv` artifact before any V2 result is accepted.

For every target month:

- all V2 source inputs must be from completed prior calendar months;
- no target-month or later value may enter a forecast;
- the validation script must report zero future-information violations;
- source coverage must be complete for every required input month;
- every required source month must have at least 15 selected hourly observations.

## 6. Pre-result acceptance gates

These gates are frozen before running the new source-binding evaluation. They may not be relaxed after seeing the result.

### 6.1 Hard integrity gates

All must pass:

1. Parent source evidence decision is exactly `PATCH_MONTHLY_LEVEL_BRIDGE_V6_SOURCE_PASS`.
2. Extended source-materiality audit over required months `2022-09..2026-06` passes every unchanged V6 materiality threshold in section 3.
3. Actual reconciliation = `43/43`.
4. Archived R1 RW reconciliation = `43/43`.
5. Archived R1 Momentum reconciliation = `43/43`.
6. Required source-month coverage = `100%`.
7. Low-count required source months = `0`.
8. Duplicate selected source dates = `0`.
9. Future-information violations = `0`.
10. Deterministic formula rerun max absolute difference = `0`.
11. No raw Twelve market value may be logged into CI output/evidence.
12. No Neon, forecast ledger, or Decision Store write is permitted during validation.

### 6.2 Source-substitution materiality / non-inferiority gates

These thresholds are internal Gold Control change-control materiality criteria, not claimed as universal industry standards. They are frozen to prevent an adverse source substitution from being accepted merely because a new source is operationally convenient.

For each expert separately:

- V2 forecast-vector Pearson correlation versus archived R1 forecast vector `>= 0.995`;
- V2 MAPE `<= 1.05 × R1 MAPE`;
- V2 MAE `<= 1.05 × R1 MAE`;
- V2 worst APE `<= 1.10 × R1 worst APE`.

A V2 expert passes only if both hard integrity and its own non-inferiority gates pass.

No threshold, formula, source rule, date window, or benchmark may be changed after the result in order to convert FAIL into PASS.

## 7. Result identities

Random Walk:

- PASS: `RW_R2_SOURCE_BINDING_MODEL_IMPACT_PASS`
- FAIL: `BLOCKED_RW_R2_SOURCE_BINDING_MODEL_IMPACT_FAIL_NO_RETUNE`

3M Momentum:

- PASS: `MOMENTUM_3M_R2_SOURCE_BINDING_MODEL_IMPACT_PASS`
- FAIL: `BLOCKED_MOMENTUM_3M_R2_SOURCE_BINDING_MODEL_IMPACT_FAIL_NO_RETUNE`

Joint downstream gate:

- both PASS: `SIMPLE_EXPERT_V2_SOURCE_BINDING_PASS`
- otherwise: `BLOCKED_SIMPLE_EXPERT_V2_SOURCE_BINDING_NOT_FULLY_PROVEN`

## 8. Evidence boundary

Historical validation remains `HISTORICAL_REPLAY_MODEL_IMPACT`; it is not prospective performance evidence.

After and only after a model-specific PASS:

1. registry may be updated to the new V2 identity and `EXECUTABLE_FORWARD_EXPERT`;
2. an immutable snapshot-backed writer may be implemented/rehearsed;
3. a real pre-outcome `EARLY_INDICATIVE` output may be issued as `PROSPECTIVE_SHADOW` for a future target;
4. the issued row remains `canonical_authority=false`;
5. `NOT_PROVEN_EXPERT_SELECTION_RULE`, `AUTO_SELECTOR=OFF`, and `AUTO_ENSEMBLE=OFF` remain unchanged;
6. no V2 output may be converted into BUY/SELL/HOLD/EXIT/REDUCE or an exposure percentage.

## 9. Manifest reconciliation rule

If the frozen validation passes, the canonical manifest must be incremented under normal change control and explicitly document the new source-bound expert identities, their source semantic, evidence class, and remaining selector/decision locks.

If validation fails, the manifest must retain the blocker and record the failed candidate without retuning.