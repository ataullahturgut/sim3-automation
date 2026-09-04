# Gold Control — VW-MIDAS-SVR XAU Successor V1 Change Control

**Freeze date:** 2026-09-04  
**Identity:** `VW_MIDAS_SVR_XAU_SUCCESSOR_V1`  
**Status:** `PRE_REGISTERED_RESEARCH_SUCCESSOR_V1`  
**Authority:** subordinate to `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.32, current production Neon state, `GOLD_CONTROL_UNRESOLVED_ENGINE_SUCCESSOR_ROADMAP_2026-09-04.md`, and `GOLD_CONTROL_V130_UNRESOLVED_ENGINE_RECOVERY_AUDIT_2026-09-04.md`.

## 1. Why this is a new identity

Archived `VW_MIDAS_MSVR` remains `BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN`.

The published Wang et al. (2026) VW-MIDAS-MSVR model is a four-metal multi-output model. Current Gold Control source entitlement does not prove a governed four-metal XAU/XAG/XPT/XPD forward surface, and the archived project executable still has unresolved identities/definitions including `GPY`, `long_term_trend`, `volatility`, `g_volatility`, provider lineage and revision-safe PIT reconstruction.

Therefore this successor is intentionally:

- **XAU only**;
- **single-output SVR**, not MSVR;
- a new source and validation contract;
- not a claim of exact reproduction of Wang et al. or the archived Gold Control motor.

## 2. Methodological authority and adaptation boundary

Primary family authority:

Xianning Wang, Jian Wu, Yuchen Pan, Ni Zhang, Tuo Wang, Juan Liu (2026), **“What drives precious metals pricing? An explainable Mixed-frequency machine learning approach,” Mineral Economics**, DOI `10.1007/s13563-025-00586-8`.

The paper supports the research family concepts used here:

- mixed monthly/daily information;
- support-vector regression;
- variable weighting of high-frequency observations;
- GPR-guided state adaptation;
- log-return target representation with price-level recovery.

This successor does **not** import the paper’s proprietary/processed feature table or claim identical source identities. The model below is a Gold Control adaptation frozen before validation output is inspected.

GPR authority:

Dario Caldara and Matteo Iacoviello (2022), **“Measuring Geopolitical Risk,” American Economic Review 112(4)** and the authors’ official GPR vintage archive. Historical vintages are required for this V1 PIT reconstruction; current final-vintage GPR may not silently replace a missing historical vintage.

## 3. Role and hard governance locks

Role:

`H1_MONTHLY_PRICE_RESEARCH_EXPERT`

V1 is research-only. It grants no production/runtime authority.

Frozen locks:

- `AUTO_SELECTOR = OFF`
- `AUTO_ENSEMBLE = OFF`
- `NOT_PROVEN_EXPERT_SELECTION_RULE`
- `NOT_PROVEN_POSITION_MAPPING`
- direction vote = `false`
- no BUY / SELL / HOLD / EXIT / REDUCE mapping
- no production DB write
- no Decision Store write
- no backdated prospective claim
- no replacement of the archived `VW_MIDAS_MSVR` row
- no use of validation/locked outcomes to alter features, source identities, hyperparameter grid, windows or gates in V1.

## 4. Forecast target and origin

Canonical business horizon remains H=1:

> next calendar month’s average XAU/USD price from the completed month-end immediately before the target month.

For this historical research implementation, the model/replay lineage is separately named:

`XAU_MONTHLY_AVG_NY17_HOURLY_RESEARCH_V1`

It is the arithmetic mean of valid daily Twelve Data `XAU/USD` 1-hour bars selected at `16:00:00 America/New_York`, treated as the hour ending at the project’s internal 17:00 ET reference.

This lineage is **not** the exact production `XAU_EOD_TWELVE_NY17` 1-minute 16:59 bar and must never be described as an official settlement/close. Any later prospective-shadow use requires a separate bridge to the exact production target/input lineage.

## 5. Frozen source-readiness gate

Historical mixed-frequency replay may execute only if all of the following pass before any model score is emitted:

1. Twelve Data symbol is exactly `XAU/USD`.
2. Interval is exactly `1h`.
3. Time zone is exactly `America/New_York`.
4. Daily decision-reference selector is exactly bar timestamp `16:00:00`.
5. Required source window begins `2020-03-01` and runs through at least `2026-08-31`.
6. Every completed month in the required window contains at least 15 valid positive daily references.
7. No month in the required window is silently skipped.
8. Raw vendor prices are not committed to GitHub or printed into CI logs.
9. Research retrieval time remains the true current retrieval time; bars are not falsely represented as records physically persisted at old forecast origins.
10. GPR PIT reconstruction must succeed from the official vintage archive for every required origin; if any required vintage is absent/unparseable, model scoring stops as `BLOCKED_GPR_VINTAGE_PIT_NOT_PROVEN`.

If Twelve history fails the fixed start/coverage gate, V1 stops as:

`BLOCKED_TWELVE_HOURLY_COMMON_HISTORY_INSUFFICIENT_FOR_FROZEN_V1_WINDOW`

The start date may not be moved after seeing model scores.

## 6. GPR availability contract

For forecast origin at the end of calendar month `p`:

- month-`p` GPR is not assumed available at `p` month-end;
- use GPR observation for `p-1`;
- reconstruct it from the official monthly vintage released in month `p`, named by the official archive convention `data_gpr_export_YYYYMM.xls`;
- normalize GPR causally inside that same vintage using only GPR observations dated no later than `p-1`:

`GPR_norm = (GPR_{p-1} - historical_min) / (historical_max - historical_min)`

If the denominator is zero, use the frozen neutral value `0.5`.

No current-vintage substitution is permitted when a required historical vintage is missing.

## 7. Mixed-frequency variable-weight feature

For each origin month `p`, construct daily XAU log returns from sequential valid NY17-hourly research references. The first valid day of `p` uses the last valid reference before the month boundary as its predecessor.

Frozen dynamic decay:

`lambda_p = 0.1 * exp(-10 * GPR_norm_p)`

For origin-month daily return `r_i`, with age `a_i = 0` for the most recent return and increasing backward:

`w_i = exp(-lambda_p * a_i) / sum_j exp(-lambda_p * a_j)`

`VW_DAILY_RETURN_p = sum_i w_i * r_i`

The constants `0.1` and `10` are frozen before replay and are not retuned in V1.

## 8. Frozen feature vector

Only these features are admitted in V1:

1. `MR_lag1`
2. `MR_lag2`
3. `MR_lag3`
4. `MR_abs_lag1`
5. `MR_MA_3`
6. `MR_MA_6`
7. `MR_sign_lag1`
8. `VW_DAILY_RETURN`
9. `GPR_norm_lagged`
10. `month_sin`
11. `month_cos`

Monthly return features are calculated only from completed research-lineage monthly averages available at the origin. Calendar features refer to the known target calendar month.

Not admitted in V1:

- `GPY`;
- legacy `long_term_trend`;
- legacy `volatility`;
- legacy `g_volatility`;
- DXY/`^TNX` convenience identities;
- Barrick/Hecla/Newmont/ETF auxiliary proxies;
- silver/platinum/palladium inputs;
- any post-score feature addition.

## 9. Model and tuning contract

Model:

`sklearn.svm.SVR(kernel='rbf')`

All feature scaling and target scaling are fitted inside each training fold only.

Frozen hyperparameter candidate grid:

- `C ∈ {0.25, 1.0, 4.0}`
- `gamma ∈ {0.05, 0.20, 0.80}`
- `epsilon ∈ {0.01, 0.05, 0.10}`

At every outer forecast origin, choose the tuple with lowest mean absolute **log-return** error on the last up-to-12 eligible inner expanding one-step origins. Inner validation target outcomes must be known by that inner origin. Tie-break order is lower `C`, then lower `gamma`, then lower `epsilon`.

Minimum fit sample = 24 completed target months. If unavailable, that outer origin is ineligible rather than shortening the minimum after observing performance.

## 10. Frozen research windows

Source/input construction window:

`2020-03` through `2026-08` minimum required coverage.

Development/history accumulation:

`2020-04` through `2022-12`.

Untouched validation window:

`2023-01` through `2024-12`.

Locked diagnostic replay:

`2025-01` through `2026-07`.

Current-month reconstruction target:

`2026-09` from the completed `2026-08-31` information boundary, if all source gates pass. Because V1 is being executed on 2026-09-04, this output is `ORIGIN_RECONSTRUCTION / HISTORICAL_REPLAY`, never a prospective issuance.

This specialized V1 window is **not** a silent amendment of `SUCCESSOR_CANDIDATE_SET_R1`; V1 remains a separate legacy-specialized research lane and cannot be ranked against R1 candidates as though they shared the same 2016+ common window.

## 11. Benchmark and metrics

Mandatory benchmark:

`RW = origin-month XAU_MONTHLY_AVG_NY17_HOURLY_RESEARCH_V1`.

Primary validation statistic:

`Relative_MAE_vs_RW = sum(abs(candidate_error)) / sum(abs(RW_error))`.

Also report:

- MAE
- MAPE
- sMAPE
- RMSE
- median absolute error
- monthly win rate vs RW
- directional accuracy as diagnostic only
- calendar-year MAE ratio vs RW.

## 12. Frozen validation classification

V1 may be labelled `HISTORICAL_REPLAY_SPECIALIZED_SHADOW_ELIGIBLE` only if, on the untouched 2023-01..2024-12 validation window:

1. source-readiness/PIT gate = PASS;
2. deterministic rerun = PASS;
3. prefix/future-invariance tests = PASS;
4. `Relative_MAE_vs_RW < 1.00`;
5. candidate MAPE <= RW MAPE;
6. candidate median absolute error <= RW median absolute error;
7. candidate monthly win rate vs RW >= 0.50;
8. each completed validation calendar year has candidate MAE <= 1.50 × RW MAE;
9. no source/feature leakage exception remains.

Locked 2025-01..2026-07 results are **diagnostic only** and cannot rescue a failed validation gate.

Even if every historical gate passes, maximum V1 status is research/shadow eligibility. Live production remains prohibited until a separate prospective-shadow issuer contract and genuinely future origins are accumulated.

## 13. Determinism and PIT tests required

Before acceptance:

- feature computation deterministic from identical source payloads;
- future-prefix invariance: adding future rows cannot change an earlier origin feature/prediction;
- outer scaler fitted only on prior rows;
- inner scaler fitted only on its prior rows;
- target month excluded from its own feature vector/training set;
- GPR vintage month strictly satisfies the frozen availability rule;
- source retrieval performs no DB write;
- engine performs no DB write;
- evidence labels `prospective_claim=false`.

## 14. Promotion consequences

V1 cannot:

- change current production runtime counts;
- unblock archived `VW_MIDAS_MSVR`;
- create `monthly_forecast_contracts`, `decision_signal_snapshots`, `decision_runs` or `decision_events` rows;
- become the automatic monthly price reference;
- alter Emergency thresholds;
- enter an ensemble or selector.

Any of those actions require a later explicit change control after prospective evidence exists.
