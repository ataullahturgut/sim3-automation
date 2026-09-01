# GOLD CONTROL — H=1 SUCCESSOR VALIDATION CONTRACT R2

**Freeze date:** 2026-09-01  
**Reserved model family:** `GOLD_H1_SUCCESSOR_R2`  
**Reserved engine lane:** `R4.2-SHADOW-CANDIDATE`  
**Evidence status:** `VALIDATION_CONTRACT_FROZEN; HISTORICAL_REPLAY_AUTHORIZED; NO_PROSPECTIVE_FORECAST_ISSUED`

## 1. Why R2 exists

R1 correctly required source/PIT readiness before model scoring, but its preferred future-target wording over-specialized the H=1 target as a monthly average of the new Twelve NY17 decision-reference series.

Subsequent pre-score evidence established that the archived H=1 forecast target was instead the legacy `CORE5 monthly average gold USD/oz` series and that this target is materially identical to the official World Bank Pink Sheet monthly Gold series over the full audited 2016-01→2026-07 window:

- 127/127 common months;
- 123/127 exact equality;
- 127/127 within USD 0.50;
- maximum absolute difference USD 0.33;
- level correlation 0.9999999987.

Therefore R2 preserves the original economic H=1 question — **next calendar month's average XAU/USD gold price** — while separating its monthly outcome benchmark from the daily R4 decision-reference source.

R2 is frozen before any successor comparative model score is produced.

## 2. Target and origin

### 2.1 Forecast target

Canonical successor historical outcome series:

`XAU_MONTHLY_WB_PINKSHEET`

Economic semantic:

> World Bank Pink Sheet monthly average Gold price, London afternoon fixing basis, USD per troy ounce.

Role:

- historical H=1 realized target/outcome benchmark;
- legacy-compatible continuation of the archived `CORE5 gold_monthly` target semantic;
- never relabelled as Twelve NY17.

### 2.2 Daily decision reference remains separate

`XAU_EOD_TWELVE_NY17` remains the canonical R4 daily 17:00 ET internal decision-reference lineage.

It is **not** the R2 historical monthly forecast target.

This separation is intentional:

- monthly forecast outcome = World Bank/CORE5-compatible monthly Gold average;
- daily current-state/decision reference = Twelve NY17.

No provider substitution or semantic relabelling is implied.

### 2.3 Forecast origin

For target month `T`:

> origin = end of calendar month `T-1`.

No September 2026 forecast created after 2026-08-31 may be called prospective. The first possible fully compliant future H=1 issuance remains October 2026 at the real 2026-09-30 origin.

## 3. Historical target availability rule

The World Bank workbook now stored in Neon is a current/final-vintage historical research surface retrieved in 2026. It is not backdated as if it had physically existed in Neon at old origins.

For causal historical replay, target feedback is therefore deliberately conservative:

> At origin month-end `m`, a model may use finalized monthly-target values only through month `m-1`.

Equivalently, when forecasting target month `T=m+1`, the latest permissible target outcome input is `T-2`.

This one-completed-month feedback lag prevents a current World Bank workbook from being treated as contemporaneously published at historical month-end.

The target month itself and origin-month finalized World Bank outcome are never used as predictor information.

## 4. Historical macro PIT reconstruction

The first common R2 macro surface is deliberately small and contains only source domains whose historical real-time/as-of accessibility was proven before scoring and whose full month-end reconstruction was successfully persisted to Neon.

Frozen series:

- `DGS10_ALFRED_PIT_ME` — US 10Y Treasury constant maturity yield;
- `DFF_ALFRED_PIT_ME` — effective federal funds rate domain;
- `DEXCHUS_ALFRED_PIT_ME` — CNY per USD;
- `NASDAQ100_ALFRED_PIT_ME` — NASDAQ-100 index.

Each row represents the latest valid source observation visible in the official FRED/ALFRED real-time view as of that historical month-end.

Important evidence rule:

- `provider_as_of` carries the historical month-end reconstruction boundary;
- `retrieved_at` remains the true 2026 reconstruction time;
- these rows are `HISTORICAL_REPLAY_RECONSTRUCTION`, not evidence that Gold Control physically stored them at the old origin;
- replay code must query this named reconstruction lineage explicitly and must not pretend `observations_as_of(old_origin)` can see rows retrieved in 2026.

Neon persistence evidence: GitHub Actions run `33538748716`, job `99959440836`, `SUCCESS`; retrieval run `1b4ccbe6-0372-411e-95d9-eb832d637a00`.

Persisted canonical coverage:

- `XAU_MONTHLY_WB_PINKSHEET`: 127 rows, 2016-01→2026-07;
- each of the four ALFRED PIT month-end series: 128 rows, 2016-01-31→2026-08-31;
- one lineage and one quality class per series;
- 639 observations written, zero revisions;
- forecast-input snapshots remained 0;
- monthly forecast contracts remained 0;
- derived feature snapshots remained 1.

Thus the persistence is historical research reconstruction only; it did not issue a forecast.

## 5. Inputs deliberately deferred from the first R2 comparative run

The following do not block the first acceptable successor validation run:

- `DTWEXBGS` — 2016 ALFRED as-of access not proven in the audited route;
- `SP500` / `DJIA` — 2016 historical FRED as-of route not proven in the audited route;
- VIX / GVZ — long history exists, but historical publication/PIT contract is not yet frozen for successor scoring;
- GPR/GPRT/GPRA — long current history exists, historical vintage chain remains `NOT_PROVEN`;
- NEM, Barrick B, HL.PR.B, GLL, DZZ and four-metal mixed-frequency features — conditional research only;
- exact DXY, legacy `^TNX`, GPY, legacy `long_term_trend`, `volatility`, `g_volatility` — blocked/unrecovered legacy identities/definitions;
- `PATCH_SUCCESSOR` — deferred until a complete new input/model contract is frozen before a future score run.

These may enter only under a later versioned change-control. They may not be added after inspecting R2 results.

## 6. Common replay window and warm-up

Stored common input history starts at 2016-01. To avoid shortening model minimum-history requirements after seeing results, R2 freezes:

- warm-up/development history: `2016-01 → 2018-06`;
- common outer historical replay: `2018-07 → 2026-07`;
- common outer N = 97 target months;
- completed calendar-year robustness buckets for gate decisions: `2019 → 2025`;
- 2018 partial and 2026 partial results are reported but are not counted as completed-year buckets.

All results are `HISTORICAL_REPLAY`.

## 7. Frozen causal feature construction

For target month `T` and origin month-end `T-1`:

Target-history inputs may use only finalized targets through `T-2`.

Frozen target-derived inputs for macro models:

- `log_y_lag2 = log(y[T-2])`;
- one-month simple return ending `T-2`;
- prior one-month simple return ending `T-3`;
- three-month mean simple return using only values no later than `T-2`.

Frozen macro inputs at origin `T-1`:

- DGS10 level and one-month change;
- DFF level and one-month change;
- log DEXCHUS level and one-month log change;
- log NASDAQ100 level and one-month log change.

No target-month information enters features.

All feature scaling is fit inside the training fold only.

## 8. Frozen candidate set R2

### Mandatory benchmark

`RW_R2_PIT`

- forecast = latest permissible finalized monthly target level (`T-2`).

### Target-only controls

`DRIFT_R2_PIT`

- fit linear monthly drift over the latest 12 permissible finalized target levels through `T-2`;
- extrapolate two target steps to `T`.

`MOM3_R2_PIT`

- arithmetic mean of the latest three permissible simple monthly target returns through `T-2`;
- compound that mean for two target steps from the latest permissible target level.

`DAMPED_TREND_R2_PIT`

- Holt damped-trend model on permissible target history through `T-2`;
- deterministic fit;
- forecast two target steps to `T`.

### Macro candidates

All predict `log(y[T])` from the exact frozen feature vector in Section 7.

`RIDGE_MACRO_R2`

- StandardScaler fit inside each training fold;
- Ridge `alpha=1.0`;
- no post-score retuning.

`HUBER_MACRO_R2`

- StandardScaler fit inside each training fold;
- HuberRegressor `epsilon=1.35`, `alpha=0.0001`, `max_iter=1000`;
- no post-score retuning.

`SVR_RBF_MACRO_R2`

- StandardScaler fit inside each training fold;
- RBF SVR `C=10`, `gamma='scale'`, `epsilon=0.02` on log target;
- no post-score retuning.

No auto-selector and no auto-ensemble are allowed in R2.

## 9. Replay implementation rules

- random split prohibited;
- expanding-origin fit at every target month;
- no future target or future macro rows;
- no current-state `canonical_latest` substitution for a historical origin;
- historical ALFRED reconstruction must be selected by the exact named series plus `provider_as_of <= origin`;
- World Bank target values are historical outcomes and use the one-completed-month feedback lag in Section 3;
- each candidate must use the same 97-month outer target window;
- any candidate that cannot produce all common-window forecasts is `BLOCKED_INCOMPLETE_COMMON_WINDOW` and is not ranked;
- deterministic rerun equality is required before eligibility.

## 10. Metrics and gate

Primary comparative metric:

`Relative_MAE_vs_RW = sum(abs(error_candidate)) / sum(abs(error_RW_R2_PIT))`

Report:

- MAE;
- MAPE;
- sMAPE;
- median absolute error;
- RMSE;
- monthly win rate vs RW;
- directional accuracy as diagnostic only;
- completed-year MAE ratios vs RW;
- 2018 partial / 2026 partial diagnostics.

A candidate becomes `HISTORICAL_REPLAY_SHADOW_ELIGIBLE` only if all hold:

1. source/provenance/PIT audit PASS;
2. deterministic rerun PASS;
3. complete 97-month common window;
4. `Relative_MAE_vs_RW < 1.00`;
5. MAPE <= RW MAPE;
6. median absolute error <= RW median absolute error;
7. candidate beats RW in at least 4 of the 7 completed calendar years 2019–2025;
8. no completed year has candidate MAE > 1.50 × RW MAE;
9. no unresolved leakage/input exception.

If no candidate passes:

`REJECT_ALL_SUCCESSOR_CANDIDATES_R2`.

Among candidates passing all gates, rank by:

1. lowest aggregate `Relative_MAE_vs_RW`;
2. lower median absolute error;
3. simpler model class / fewer degrees of freedom.

Passing this gate authorizes only future prospective-shadow preparation, not live production.

## 11. Forecast-state database rule

Historical reconstructed observations belong in the observation/source-vintage data plane.

They do **not** belong in `forecast_input_snapshots` or `monthly_forecast_contracts` as retroactive issued forecasts.

Those append-only forecast-state tables remain reserved for a real issuance created before target realization.

At the real September month-end origin, if the successor lane is ready, the October forecast must first persist a true immutable input snapshot and then an H=1 forecast contract with evidence class `PROSPECTIVE_SHADOW`.

## 12. R4.2 bridge remains separate

A historical forecast winner does not automatically become the R4 monthly price reference.

Before a future R4.2 decision row:

- generic fields `monthly_price_reference` and `monthly_price_reference_model_id` must replace VW-specific semantics in a new contract;
- Level/Reversal geometry must be checked without hindsight threshold retuning;
- `NOT_PROVEN_POSITION_MAPPING` remains binding;
- `action_state` remains null.

## 13. Immediate next gate

R2 input readiness is now sufficient for the first controlled comparative replay.

Next task:

`RUN SUCCESSOR_CANDIDATE_SET_R2 ON THE FROZEN 2018-07→2026-07 HISTORICAL_REPLAY WINDOW; APPLY THE PRE-FROZEN RW GATES; DO NOT ISSUE A PROSPECTIVE FORECAST.`
