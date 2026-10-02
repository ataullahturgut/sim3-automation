# IRIS-H3 RETURN V1 — NUMERICAL 3-DAY RETURN HEAD AUTHORITY

**Date:** 2026-10-02  
**Identity:** `IRIS_H3_RETURN_V1_RESEARCH`  
**Parent direction model:** `IRIS_H3_V1_RESEARCH / A1_PLUS_PATH`  
**Status:** PREREGISTERED / RESEARCH-ONLY

## Objective

Add a numerical three-trading-day return forecast to the frozen IRIS-H3 information set without changing the frozen direction champion.

For each H3 origin produce:

`[RET_HAT_H3, LOWER80_H3, UPPER80_H3, SIGN_HAT]`

where the interval is causal conformal and uses only previously matured forecast errors.

## Information set

Exactly the frozen IRIS parent inputs:
- `base_logit` from frozen A1/ARCR probability;
- 1h / 3h / 6h / 12h / 24h / 48h XAU hourly log returns;
- lag-2 hourly return;
- feature-cutoff-day local session return.

Hourly anchor remains 16:00 America/New_York on `feature_cutoff_date`. No forecast-issue-day hourly bar is used.

## Candidate numerical heads

All use StandardScaler and the same expanding monthly chronology:

1. `RIDGE_1` — Ridge(alpha=1)
2. `RIDGE_10` — Ridge(alpha=10)
3. `ELASTIC_0001` — ElasticNet(alpha=0.0001, l1_ratio=0.5)
4. `ELASTIC_0005` — ElasticNet(alpha=0.0005, l1_ratio=0.5)
5. `HUBER` — HuberRegressor(epsilon=1.35, alpha=0.0001)

No 2024-2026 outcome may select the model.

## Chronology

- 2022: initial history and causal residual-bank formation.
- 2023: numerical-head selection authority.
- 2024: frozen confirmation.
- 2025/2026: frozen transport/stress.
- Each monthly model fit uses only rows with `target_end_date_h3 <= test feature cutoff`.

## 2023 selection

Primary:
1. lowest MAE;
2. lowest RMSE;
3. highest return-sign accuracy.

A candidate is eligible only if:
- MAE <= zero-return baseline MAE;
- RMSE <= zero-return baseline RMSE + 0.001.

## Conformal interval

- target coverage: 80%.
- nonconformity: absolute numerical return error.
- residual bank: prior chronological out-of-sample errors whose H3 target has matured by the current feature cutoff.
- maximum residual window: 252.
- minimum residual count: 80.
- interval half-width: empirical 80th percentile using `method="higher"`.
- no 2023/2024/2025/2026 tuning of the interval level.

## Metrics

Numerical:
- MAE
- RMSE
- bias
- correlation
- sign accuracy
- mean predicted return
- mean actual return.

Interval:
- empirical 80% coverage
- mean width
- median width.

Also report 2026 month-by-month:
- N
- mean predicted return
- mean realized return
- MAE
- sign accuracy
- interval coverage
- mean interval width.

## Interpretation

The numerical head does not replace IRIS direction V1. It is an auxiliary magnitude/uncertainty output. A frozen transport failure cannot be repaired inside V1.
