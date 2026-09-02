# GOLD CONTROL — CAUSAL PATCH R1 MONTHLY LEVEL INPUT CHANGE CONTROL V5

**Date frozen:** 2026-09-02  
**Status:** `FROZEN_BEFORE_V5_SOURCE_RESULT`  
**Parent manifest:** v1.18  
**Parent issuer candidate:** `CAUSAL_PATCH_R1_REPRO_V1_3_XAU_ONLY_ORIGIN_SAFE`  
**Reserved V5 identity:** `CAUSAL_PATCH_R1_REPRO_V1_4_XAU_MONTHLY_LEVEL_ORIGIN_SAFE`

## 1. Problem statement

The V4 bridge proved the prospective continuation of the Patch feature channels and the locked 43-month model impact. The V4 executable still computes its training return target and forecast level with `gold_monthly` from the historical CORE5 artifact:

`y_t = log(gold_monthly_t / gold_monthly_{t-1})`

and

`forecast_t = gold_monthly_{t-1} * exp(predicted_log_return_t)`.

At a real month-end origin the just-completed month's CORE5/World Bank final-vintage monthly value is not proven available. The existing governed World Bank lineage explicitly preserves retrieval-time truth and requires lag for historical replay. Therefore V4 alone is not sufficient to issue a real end-month forecast without an explicit operational monthly-level continuation.

This is an input/measurement continuation problem only. It does not reopen model search.

## 2. Frozen V5 operational monthly-level candidate

Series identity:

`PATCH_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V5`

Provider:

- Twelve Data
- symbol `XAU/USD`
- interval `1h`
- requested timezone `America/New_York`

Daily measurement rule:

- select the hourly bar whose `datetime` is exactly `16:00:00` New York time;
- Twelve documentation defines the bar timestamp as the bar-open time and `close` as the price at the end of the bar; therefore this is the close at the end of the 16:00–17:00 ET bar;
- require a unique positive finite selected close for each returned market date;
- no interpolation or forward fill.

Monthly measurement rule:

- for a completed calendar month, take the arithmetic mean of all valid selected daily closes whose local bar date belongs to that month;
- require at least 15 valid selected daily observations for each month used by the model;
- the current/origin month is eligible only after the final required 16:00–17:00 ET bar has completed; a current incomplete bar may not be used;
- issuance timestamp must remain truthful; no backdating.

Semantic labels explicitly prohibited:

- CORE5
- World Bank Pink Sheet
- LBMA fixing/benchmark
- COMEX settlement
- official market close
- `XAU_EOD_TWELVE_NY17`

This is a separately named Patch operational monthly-level measurement.

## 3. Source/semantic materiality gates — frozen before V5 result

The following materiality limits are inherited unchanged from the already pre-result-frozen Gold Control monthly-gold bridge research contract. They are not selected after inspecting V5:

- monthly level correlation versus canonical CORE5 `gold_monthly`: `>= 0.995`;
- median absolute relative level gap: `<= 50 bps`;
- p95 absolute relative level gap: `<= 100 bps`;
- consecutive monthly log-return correlation: `>= 0.95`;
- monthly return direction agreement: `>= 0.80`.

Hard coverage gates:

1. every CORE5 month required for Patch training/validation from `2011-02` through `2026-07` must have a valid V5 monthly level;
2. no duplicate selected daily date;
3. every selected daily close finite and positive;
4. every required month has at least 15 selected daily closes;
5. no observation from a later month may enter an earlier monthly mean;
6. raw vendor market values are not printed to logs;
7. no Neon, forecast-ledger, or Decision Store write occurs during source/model-impact audit.

Source PASS identity:

`PATCH_MONTHLY_LEVEL_BRIDGE_V5_SOURCE_PASS`

Failure identity:

`BLOCKED_PATCH_MONTHLY_LEVEL_BRIDGE_V5_SOURCE_NOT_PROVEN`

## 4. Locked V5 model-impact rule after source PASS

Only after the source/semantic gate passes, reconstruct the Patch monthly return target and forecast anchor using the V5 operational monthly-level series for all model samples:

`y_t^V5 = log(monthly_level_t^V5 / monthly_level_{t-1}^V5)`

`forecast_t^V5 = monthly_level_{t-1}^V5 * exp(predicted_log_return_t^V5)`.

The canonical H=1 evaluation target remains the frozen CORE5/production-closure actual; V5 operational monthly levels are not relabelled as canonical actuals.

Unchanged model properties:

- Patch Transformer architecture class unchanged;
- `L=252`, `P=21`, `D=32` unchanged;
- V4 XAU-only daily-return feature channel unchanged;
- V3 NASDAQ completed-month semantic unchanged;
- FEDFUNDS/USDCNY/GPR semantics unchanged;
- optimizer/loss/training procedure unchanged;
- locked evaluation window `2023-01→2026-07`, `N=43` unchanged;
- auto selector OFF;
- auto ensemble primary OFF.

Frozen model-impact gates remain exactly the V4 gates:

- canonical target reconciliation `43/43`;
- RW reconciliation `43/43`;
- deterministic repeat equality;
- zero future-information violations;
- no geometry re-selection;
- MAPE `< RW MAPE`;
- MAE `< RW MAE`;
- worst APE `<= 1.25 × RW worst APE`.

PASS identity:

`PATCH_R1_V5_MONTHLY_LEVEL_MODEL_IMPACT_PASS`

FAIL identity:

`PATCH_R1_V5_MONTHLY_LEVEL_MODEL_IMPACT_FAIL_NO_RETUNE`

No failed V5 result may be followed by threshold relaxation or silent source substitution.

## 5. Evidence boundary

A V5 PASS remains `HISTORICAL_REPLAY_MODEL_IMPACT`, not prospective evidence. It only proves that the fully operationalized input/measurement construction is historically eligible under the same frozen gates.

After V5 PASS, freeze the V5 executable/input identity, reconcile the manifest, implement the immutable forecast input snapshot + forecast contract writer, construct the complete forward EngineSnapshot, and arm the first eligible `PROSPECTIVE_SHADOW` issuance.
