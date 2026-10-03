# FLOW-PRELIM-OI-H3 V1 — PREREGISTRATION

**Date:** 2026-10-03  
**Identity:** `FLOW_PRELIM_OI_H3_V1`  
**Branch:** `gold-h3-flow-oi-salvage-v1-20261003`  
**Role:** official-CME preliminary daily Volume+Open-Interest reversal-candidate specialist.  
**Status:** **PREREGISTERED BEFORE MODEL RESULTS**

## 1. Why this separate identity exists

The original FLOW-H3 V1 contract required CME FINAL daily GC open interest and remains frozen/blocked.

A new official source path has now been verified:
- anonymous CME FTP: `ftp.cmegroup.com/daily_volume`
- daily files: `daily_volume_YYYYMMDD.xlsx`
- sheet: `CME Group Vol and OI by Product`
- GC row: Exchange `COMEX(STATS)`, Commodity Indicator `GC`, Product `GOLD FUTURES`, Future/Option = `F`

CME explicitly labels the Open Interest in this report as **preliminary** and states that official final data are released in the Daily Bulletin the following morning.

Therefore this is not relabeled as FLOW_H3_V1. It is a distinct challenger.

## 2. Origin-safe lag rule

Canonical H3 decision reference: 17:00 America/New_York.

Frozen rule:

> For every H3 feature cutoff date t, use only the most recent CME preliminary GC row with trade_date < t.

Same-trade-date preliminary data are forbidden.

This conservative prior-trade-date rule avoids needing to infer the exact intraday publication timestamp of the preliminary file.

No lag search is permitted.

## 3. Source fields

For each eligible CME trade date:
- `gc_total_volume`
- `gc_prelim_open_interest`
- source filename
- source trade date
- parse status

Rows with missing or non-positive Volume or missing/non-positive OI are unavailable, not imputed.

## 4. Frozen feature family

1. `dlog_volume_1`
2. `dlog_oi_1`
3. `volume_z20`
4. `oi_z20`
5. `volume_oi_ratio`
6. `d_volume_oi_ratio_1`
7. `oi_accel_5`
8. `volume_accel_5`
9. `momentum_x_dlog_oi`
10. `momentum_x_volume_z20`

Rolling statistics are backward-looking and may use only source rows prior to the H3 cutoff under the lag rule.

## 5. Target and candidate universe

Target:
`reversal_target = 1[y_up != momentum_up]`

Operational evaluation universe:
`aurora_follows_momentum == True`

FLOW-PRELIM-OI does not directly flip HELIOS V5 in this stage.

## 6. Model

- StandardScaler
- LogisticRegression
- C=1.0
- solver=lbfgs
- class_weight=balanced
- seed=20261003
- monthly expanding-origin refit
- minimum matured training rows=80

Training rows must satisfy:
`target_end_date_h3 <= current month first feature cutoff`.

## 7. Period roles

- DEV / threshold selection: 2023-01-01 through 2024-12-31
- confirmation: 2025-01-01 through 2025-12-31
- final holdout: 2026 only after confirmation PASS and only where preliminary OI coverage exists

2026 may not influence source parsing, features, lags, model or threshold.

## 8. Threshold selection

Frozen grid:
`[0.35, 0.40, 0.45, 0.50, 0.55]`

Use DEV eligible origins only.

Objective:
- maximize reversal F2

Eligibility:
- candidate precision >= 0.45
- candidate rate <= 0.35

Tie-break:
1. higher recall
2. higher precision
3. lower candidate rate
4. higher threshold

No eligible threshold => `NO_ELIGIBLE_FLOW_PRELIM_OI_THRESHOLD`.

## 9. 2025 confirmation

All must pass:
1. FLOW-PRELIM-OI reversal recall > OPAL candidate recall on same eligible universe
2. at least one true reversal missed by OPAL is nominated
3. FLOW-PRELIM-OI precision >= 0.40
4. OPAL ∪ FLOW-PRELIM-OI reversal recall > OPAL recall

Failure => no formal 2026 opening.

## 10. 2026 holdout

Only after confirmation PASS:
- reversal recall
- candidate precision/rate
- OPAL overlap
- FLOW-only true reversals
- union recall
- V5-missed + OPAL-no-candidate reversals nominated
- diagnostic forced-flip rescue/broken/net

If 2026 CME preliminary OI coverage is incomplete, report coverage first and score only the valid covered universe without imputation.

## 11. Governance

- The original FINAL-only FLOW-H3 V1 remains unchanged.
- No 2026 outcome can alter this contract.
- Missing OI is not filled from COT, interpolation, Yahoo, Barchart, or another provider under this identity.
- HELIOS V5-DCE remains binding unless a later separately governed promotion step occurs.
