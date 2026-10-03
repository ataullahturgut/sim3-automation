# DIVERGE-H3 V1 — PREREGISTRATION

**Date:** 2026-10-03  
**Identity:** `DIVERGE_H3_V1`  
**Branch:** `gold-h3-diverge-v1-20261003`  
**Evidence class:** `RETROSPECTIVE_RESEARCH_NOT_FULL_PIT`  
**Role:** cross-asset non-confirmation / momentum-reversal candidate specialist.

## 1. Purpose

DIVERGE-H3 asks whether Gold's current 12-hour momentum is being confirmed or contradicted by the most recently completed cross-asset state.

It is **not** a general UP/DOWN model and does not replace AURORA, OPAL or HELIOS V5-DCE.

Target:
`reversal_target = 1[y_up != momentum_up]`

Operational universe:
`aurora_follows_momentum == True`.

## 2. Frozen source family

### Gold / Silver
Source:
`GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_DAILY_PRICES.csv`

Use:
- prior completed Gold daily return
- prior completed Silver daily return
- Gold-minus-Silver return gap

The frozen metal history is the same clean lineage already used by the clean H3 research chain. Historical reconstruction is not presented as pristine prospective PIT evidence.

### Broad USD
Series:
- FRED / Federal Reserve H.10 `DTWEXBGS`
- semantic: broad trade-weighted U.S. dollar index
- exact ICE DXY is **not** substituted.

### U.S. 10-year yield
Series:
- FRED / Federal Reserve H.15 `DGS10`
- daily change in percentage points.

### Nasdaq-100
Series:
- FRED `NASDAQ100`
- daily return.

### VIX
Series:
- FRED `VIXCLS` / Cboe lineage
- daily log change.

WTI/Brent are excluded from V1 because no governed daily series is presently registered in the project. They may not be introduced after seeing 2026 outcomes.

## 3. Origin-safe alignment

Canonical H3 feature cutoff is the project's daily feature date associated with the 17:00 ET decision reference.

For every source:
- select the latest source observation with `source_date < feature_cutoff_date`;
- same-date close/value is forbidden even if a provider historically reports it before 17:00 ET;
- no lag search is permitted;
- no forward-fill across an unbounded gap.

Maximum acceptable staleness:
- Silver/Gold: 5 calendar days
- DGS10: 7 calendar days
- DTWEXBGS: 7 calendar days
- NASDAQ100: 5 calendar days
- VIXCLS: 5 calendar days

Rows violating staleness are excluded.

This conservative t-1 rule is frozen before model results.

## 4. Frozen feature family

Let `s = +1` for current 12h Gold momentum UP and `s = -1` for DOWN.

Prior-day/raw state:
1. `silver_ret1`
2. `gold_daily_ret1`
3. `usd_ret1`
4. `dgs10_chg1`
5. `ndx_ret1`
6. `vix_ret1`

Momentum-conditioned divergence features:
7. `mom_x_silver = s * silver_ret1`
8. `mom_x_usd = s * usd_ret1`
9. `mom_x_yield = s * dgs10_chg1`
10. `mom_x_ndx = s * ndx_ret1`
11. `mom_x_vix = s * vix_ret1`
12. `mom_x_gold_silver_gap = s * (gold_daily_ret1 - silver_ret1)`

Macro confirmation composite:
13. `core_confirmation = mean(s*z_silver, -s*z_usd, -s*z_yield)`

Cross-market stress:
14. `cross_dispersion = std(z_silver, z_usd, z_yield, z_ndx, z_vix)`
where each z-value is the current completed source return/change standardized against the **preceding** 60 source observations (rolling mean/std use `shift(1)`), so unlike units are never averaged directly.

No feature search or sign-rule revision is allowed after 2026 outcomes are inspected.

### Pre-execution semantic amendment
Before any model execution or outcome inspection, the confirmation composite was changed from raw unlike units to backward-looking source-specific z-scores. No threshold, label, period, source, or 2026 result was inspected in making this correction.

## 5. Model

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

## 6. Period roles

- DEV / threshold selection: 2023-01-01 through 2024-12-31
- confirmation: 2025
- final holdout: 2026, opened only after confirmation PASS

2026 cannot influence source choice, lags, features, signs, model, threshold or confirmation rules.

## 7. Candidate threshold selection

Frozen grid:
`[0.35, 0.40, 0.45, 0.50, 0.55, 0.60]`

Use only DEV rows with `aurora_follows_momentum=True`.

Objective:
- maximize reversal F2.

Eligibility:
- candidate precision >= 0.45
- candidate rate <= 0.40.

Tie-break:
1. higher reversal recall
2. higher precision
3. lower candidate rate
4. higher threshold

No eligible threshold => `NO_ELIGIBLE_DIVERGE_THRESHOLD`.

## 8. 2025 confirmation

All must pass:
1. DIVERGE reversal recall > OPAL candidate recall on the same eligible universe.
2. DIVERGE identifies >=1 true reversal where OPAL candidate is false.
3. DIVERGE candidate precision >=0.40.
4. `OPAL ∪ DIVERGE` reversal recall > OPAL recall.

Failure => 2026 formal holdout remains unopened.

## 9. 2026 holdout

Only after 2025 PASS:
- reversal recall
- precision
- candidate rate
- OPAL overlap
- DIVERGE-only true reversal count
- OPAL ∪ DIVERGE recall
- number of V5-missed / OPAL-no-candidate reversals nominated by DIVERGE
- diagnostic forced-flip rescue / broken / net relative to V5

No router is promoted from this specialist result alone.

## 10. Governance

DIVERGE-H3 is an independent challenger.  
FLOW-H3 and SKEW-H3 remain externally blocked under their frozen identities.  
HAZARD-H3 remains a failed DEV-gate challenger.  
DIVERGE results may not be used to retroactively alter those contracts.
