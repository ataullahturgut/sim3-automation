# GOLD CONTROL — VW_MIDAS_MSVR_SUCCESSOR_V1 AUG31 → SEPTEMBER RECONSTRUCTION CONTRACT

Frozen: 2026-09-06
Model: `VW_MIDAS_MSVR_SUCCESSOR_V1`
Scope: CURRENT-MONTH ORIGIN RECONSTRUCTION / HISTORICAL_REPLAY, NOT PROSPECTIVE

## 1. Purpose
Produce the September 2026 H=1 monthly-average XAU/USD reference using the completed 2026-08-31 information boundary, consistent with manifest v1.37 section 5 semantics.

This output is calculated on 2026-09-06 and MUST be labelled:
`ORIGIN_RECONSTRUCTION / HISTORICAL_REPLAY`
It MUST NOT claim that the forecast was issued on 2026-08-31.

## 2. Target/origin
- origin: completed 2026-08-31 information boundary
- target: 2026-09 monthly-average XAU/USD
- frozen V1 mathematics/architecture/grid: unchanged from the 2026-09-06 V1 change-control

## 3. August 2026 four-metal reconstruction bridge
Historical StakTrakr R1 is pinned and ends 2026-07-31. It is not silently extended.

For this reconstruction only, use one coherent current-source family:
- Myfxbook XAUUSD daily historical close
- Myfxbook XAGUSD daily historical close
- Myfxbook XPTUSD daily historical close
- Myfxbook XPDUSD daily historical close

Identity:
`MYFXBOOK_FOUR_METAL_AUG31_RECONSTRUCTION_V1`

Use only dates <= 2026-08-31 and only dates where all four metals are present.
No imputation, interpolation, or mixed provider fill.

## 4. Bridge gate frozen before model output
Before using Myfxbook August values in V1, compare July 2026 Myfxbook daily closes with the historical StakTrakr R1 panel on exact common dates.

Required:
- >= 20 exact common four-metal dates in July 2026;
- for each metal, median daily APE <= 2.5%;
- for each metal, 95th-percentile daily APE <= 7.5%;
- for each metal, July monthly-mean APE <= 3.0%;
- no sign inversion or unit mismatch.

If any gate fails: `BLOCKED_AUG31_MYFXBOOK_STAKTRAKR_BRIDGE_NOT_PROVEN` and no V1 September forecast is issued.

These gates are diagnostic continuity gates, not historical model-performance gates.

## 5. August completeness
Required before model execution:
- exact four metals available;
- >= 20 common dates in August 2026;
- last common date = 2026-08-31;
- no target-month September row may enter the feature set.

## 6. GPR
Use `GPR_OFFICIAL_GIT_PIT` origin vintage `2026-08`.
Frozen lag rule remains p-1, so the GPR observation used for the August-origin feature is 2026-07 from that origin vintage.
No current/final GPR substitution.

## 7. Hyperparameter selection
For target 2026-09, select `(C, epsilon, gamma_scale)` using the frozen nested expanding-origin rule and only eligible target months `< 2026-09`.
Completed August 2026 outcomes may be included in the training set because they are known at the 2026-08-31 origin.
No September actual/partial data may enter selection, fitting, scaling, or features.

## 8. Price-level measurement
For this reconstruction, the August Gold anchor is the arithmetic mean of Myfxbook XAUUSD closes on the common-four-metal August dates.
September point forecast = August common-date Gold mean × exp(predicted September Gold log return).
Same-origin Random Walk = the same August anchor.

This is a reconstruction measurement bridge and must not be presented as identical to CORE5 without disclosure.

## 9. Output governance
- no production Neon write;
- no `monthly_forecast_contracts` write;
- no decision-store write;
- no runtime mutation;
- no selector/ensemble activation;
- output artifact only on feature branch;
- preserve source URLs, retrieval time, common dates, bridge metrics, model configuration, forecast and benchmark.
