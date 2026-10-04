# OPA-H3 V1 — GOLD OPTIONS POSITIONING ASYMMETRY PREREGISTRATION

**Date:** 2026-10-04  
**Identity:** `OPA_H3_V1`  
**Branch:** `gold-h3-option-positioning-v1-20261004`  
**Binding champion:** `SAGE_H3_V2_EXCEPTION_ONLY`

## Objective

Test whether official CME daily aggregate Gold option CALL/PUT positioning adds an independent, origin-safe reversal-rescue channel beyond HELIOS V5-DCE / SAGE V2.

OPA is not CME CVOL skew and must not be described as implied-volatility skew. It uses aggregate option volume and preliminary open interest from the official CME daily-volume workbook.

## Source

Anonymous official CME FTP:
- host: `ftp.cmegroup.com`
- directory: `/daily_volume`
- file family: `daily_volume_YYYYMMDD.xlsx`
- exchange: `COMEX(STATS)`
- commodity indicator: `OG`
- rows:
  - `GOLD CALL`, option indicator `O`
  - `GOLD PUT`, option indicator `O`

Fields:
- Total Volume
- preliminary Open Interest

## Point-in-time rule

Canonical H3 feature cutoff remains the frozen project origin.

Same-trade-date CME daily workbook values are forbidden.

For each H3 origin, use only the most recent valid source row with:
`trade_date < feature_cutoff_date`.

Calendar staleness > 7 days fails closed.

No missing OI or volume values are imputed.

## Frozen features

1. `oi_log_ratio = log(call_oi / put_oi)`
2. `oi_asym = (call_oi-put_oi)/(call_oi+put_oi)`
3. `d_oi_asym_1`
4. `d_oi_log_ratio_1`
5. `call_dlog_oi_1`
6. `put_dlog_oi_1`
7. `vol_log_ratio = log(call_vol / put_vol)`
8. `vol_asym = (call_vol-put_vol)/(call_vol+put_vol)`
9. `d_vol_asym_1`
10. `d_vol_log_ratio_1`
11. `momentum_x_oi_asym`
12. `momentum_x_d_oi_asym`

No feature selection may use 2025 or 2026 outcomes.

## Target and eligible universe

Baseline direction = HELIOS V5-DCE.

Eligible rows:
- V5 follows the frozen momentum direction.

Target:
`rescue_target = 1[y_up != v5_pred]`.

Thus OPA estimates whether a V5 momentum-continuation call should be reversed.

SAGE V2 OCS exceptions are preserved. During incremental evaluation, an OPA proposal that overlaps a frozen SAGE V2 OCS exception is not counted as a new OPA action.

## Model

- StandardScaler
- LogisticRegression
- C = 1.0
- solver = lbfgs
- class_weight = balanced
- seed = 20261004
- monthly expanding-origin refit
- minimum matured eligible training rows = 80

## Chronology

- DEV / threshold selection: 2023-2024 only
- untouched confirmation: 2025
- final holdout: 2026 only if 2025 confirmation passes

Threshold grid:
`[0.35, 0.40, 0.45, 0.50, 0.55, 0.60]`

DEV eligibility:
- precision >= 0.45
- candidate rate <= 0.35

Selection:
1. maximize F2
2. higher recall
3. higher precision
4. lower candidate rate
5. higher threshold

If no threshold passes: `OPA_DEV_FAIL`.

## 2025 confirmation gate

On non-overlap incremental OPA actions:
- rescue - broken > 0
- precision >= 0.50
- at least 2 rescues
- SAGE V2 + OPA full-direction accuracy >= SAGE V2 on the same covered 2025 origins

If the gate fails, 2026 outcomes remain closed for promotion decisions.

## 2026 holdout reporting

If 2025 passes:
- OPA candidate count
- non-overlap actions
- rescue / broken / net
- action precision
- SAGE V2 accuracy vs SAGE V2+OPA accuracy on the identical covered origin set
- Brier / log-loss where probability mapping is coherent
- half-year stability
- overlap with SAGE V2 OCS

No 2026 outcome may change features, model, threshold or source lag.
