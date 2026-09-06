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
Historical production StakTrakr R1 is pinned and ends 2026-07-31. It is not silently extended.

For this reconstruction only, use one coherent current-source family:
- Myfxbook XAUUSD daily historical close
- Myfxbook XAGUSD daily historical close
- Myfxbook XPTUSD daily historical close
- Myfxbook XPDUSD daily historical close

Identity:
`MYFXBOOK_FOUR_METAL_AUG31_RECONSTRUCTION_V1`

The exact August values used are frozen in:
`gold_axis_2026/data_pipeline/myfxbook_four_metal_august_2026_reconstruction_snapshot.csv`

Use only dates <= 2026-08-31 and only dates where all four metals are present.
No imputation, interpolation, or mixed provider fill.

## 4. Bridge gate frozen before model output — corrected source-overlap window
The first engineering attempt used a July bridge, but GitHub Actions received HTTP 403 when trying to fetch Myfxbook HTML directly. No model forecast was produced in that attempt.

Before any model output, the bridge window is therefore corrected to the direct overlap between:
- frozen Myfxbook August reconstruction snapshot; and
- upstream StakTrakr commit `ed2e549f82ba0d1cd3ca32842b82d3888d301e01`, whose 2026 spot-history payload contains August observations through 2026-08-19.

Bridge comparison uses exact common dates in 2026-08-02..2026-08-19.

Required, frozen before forecast output:
- >= 12 exact common four-metal dates;
- for each metal, median daily APE <= 2.5%;
- for each metal, 95th-percentile daily APE <= 7.5%;
- for each metal, overlap-window mean APE <= 3.0%;
- no sign inversion or unit mismatch.

If any gate fails: `BLOCKED_AUG31_MYFXBOOK_STAKTRAKR_BRIDGE_NOT_PROVEN` and no V1 September forecast is issued.

This correction changes only the source-overlap diagnostic window. It does not change model mathematics, target, feature definitions, hyperparameter grid, historical replay results, or forecast output after seeing a forecast; no forecast existed when this correction was frozen.

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
- preserve source evidence, retrieval time, common dates, bridge metrics, model configuration, forecast and benchmark.
