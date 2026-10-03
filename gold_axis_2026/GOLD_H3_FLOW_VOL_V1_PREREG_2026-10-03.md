# FLOW-VOL-H3 V1 — PREREGISTRATION

**Date:** 2026-10-03
**Identity:** FLOW_VOL_H3_V1
**Branch:** gold-h3-flow-v1-20261003
**Role:** volume-only ablation inside FLOW stage; NOT a replacement for FLOW_H3_V1.

## Purpose
Test whether daily GC futures activity volume alone adds high-recall momentum-reversal visibility beyond OPAL.

## Source
Primary retrieval candidate: Yahoo Finance GC=F daily history, used only as a contract-level/continuous futures volume proxy.
This is not treated as official CME aggregate VOI and is not silently relabeled as CME DataMine.

## PIT rule
For each H3 feature cutoff date t, use only the most recent volume observation with trade_date < t.
Same-day volume is forbidden. This conservative one-trading-day lag is fixed before any model result is inspected.

## Target
reversal_target = 1[y_up != momentum_up]
Eligible context = aurora_follows_momentum == True.

## Frozen features
- dlog_volume_1
- volume_z20
- volume_ratio_20
- volume_accel_5
- momentum_x_dlog_volume
- momentum_x_volume_z20

All rolling statistics are backward-looking and shifted.

## Model
StandardScaler + LogisticRegression
C=1.0
solver=lbfgs
class_weight=balanced
seed=20261003
monthly expanding-origin refit
minimum matured training rows=80.

## Period roles
- DEV / threshold selection: 2023-01-01 through 2024-12-31 only
- confirmation: 2025 only
- final holdout: 2026 only, opened only if confirmation gate passes

## Threshold selection
Frozen grid: [0.35, 0.40, 0.45, 0.50, 0.55]
Objective: maximize reversal F2 on 2023-2024 eligible origins.
Constraints:
- candidate precision >= 0.45
- candidate rate <= 0.35
Tie-breaks:
1. higher recall
2. higher precision
3. lower candidate rate
4. higher threshold
If none eligible: NO_ELIGIBLE_FLOW_VOL_THRESHOLD.

## 2025 confirmation gate
All must pass:
- FLOW-VOL reversal recall > OPAL candidate recall on the same eligible universe
- at least one true reversal missed by OPAL is nominated by FLOW-VOL
- FLOW-VOL candidate precision >= 0.40

If confirmation fails, 2026 remains unopened for formal evaluation.

## 2026 holdout metrics
If confirmation passes:
- true reversal recall
- candidate precision and rate
- FLOW-only true reversal count where OPAL candidate is false
- overlap with OPAL
- OPAL ∪ FLOW-VOL candidate-union reversal recall
- among the known V5-missed / OPAL-no-candidate reversals, how many receive FLOW-VOL candidate
- diagnostic rescue/broken/net opportunity; no router promotion in this stage.

## Governance
No 2026 outcomes may modify features, source lag, model, threshold grid or confirmation gate.
FLOW_VOL_H3_V1 does not alter CLEAN_H3_PROSPECTIVE_V1, OPAL or HELIOS V5.
