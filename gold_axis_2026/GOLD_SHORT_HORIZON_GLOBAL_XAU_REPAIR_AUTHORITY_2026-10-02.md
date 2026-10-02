# GOLD SHORT-HORIZON GLOBAL XAU — Repair / Reproduction Authority

**Date:** 2026-10-02  
**Status:** FROZEN REPAIR AUTHORITY  
**Canonical project:** `GOLD_SHORT_HORIZON_GLOBAL_XAU_PROJECT_MANIFEST.md`

## 1. Purpose

Repair the daily Global-XAU research lane without changing its scientific question or using opened 2025/2026 outcomes for model selection.

This repair must:

1. restore the already-established Gold Control / monthly-project source authority;
2. extend the same StakTrakr four-metal source lineage through completed August and September 2026 where continuity is proven;
3. correct ambiguous timeline labels;
4. reproduce the frozen pre-2025 H3 / CORE3 / Logistic-L2 baseline;
5. rerun frozen 2025 and opened 2026 transport through the latest fully matured H3 target available by 2026-09-30;
6. run a diagnostic-only distribution / regime-shift audit;
7. leave threshold, feature and model selection unchanged.

## 2. Source authority

No new provider search is authorized by this repair.

Historical source identities remain:

- Gold: `XAU_STAKTRAKR_RESEARCH_DAILY_R1`
- Silver: `XAG_STAKTRAKR_RESEARCH_DAILY_R1`
- Platinum: `XPT_STAKTRAKR_RESEARCH_DAILY_R1`
- Palladium: `XPD_STAKTRAKR_RESEARCH_DAILY_R1`.

For completed 2026 dates beyond the persisted historical snapshot, use the existing project public extension mechanism only:

- `lbruton/StakTrakr` annual spot-history files;
- `lbruton/StakTrakrApi` 12:00 hourly snapshots after the annual-file endpoint;
- exact Git commit refs resolved and recorded at execution.

The extension may be appended only if overlapping DB/persisted StakTrakr observations and public StakTrakr observations pass the same-source continuity gate.

No Twelve Data, XAUS, BIST, Yahoo, futures or ETF series may be silently substituted into the historical target.

## 3. Same-source continuity gate

For every core metal:

- compare all available overlapping dates between the persisted StakTrakr research series and the resolved public StakTrakr source;
- require at least 20 overlap observations;
- require all compared positive values to match within numerical tolerance `rtol=1e-8, atol=1e-8`;
- fail closed if the gate fails.

Only observations strictly after the persisted series endpoint may be appended.

## 4. Correct timeline semantics

The repaired ledger must use explicit columns:

- `feature_cutoff_date`: last retained Gold date whose value and derived features are used;
- `forecast_issue_date`: next retained Gold observation date after the feature cutoff; this is the former ambiguous `signal_date`;
- `target_start_date`: equal to the feature-cutoff Gold date for the return clock;
- `target_end_date_h1`, `target_end_date_h3`, `target_end_date_h5`: exact retained Gold dates ending each forward-return target.

Targets remain:

- H1: `log(P[t+1]/P[t])`
- H3: `log(P[t+3]/P[t])`
- H5: `log(P[t+5]/P[t])`.

The repair changes labels, not the target formula.

## 5. Frozen reproduction contract

Pre-2025 frozen comparator:

- horizon: H3
- feature block: CORE3
- model: Logistic Regression L2
- scaler: StandardScaler
- C=1.0
- solver=lbfgs
- max_iter=1000
- random_state=20261001
- DEV issue dates: 2022-2024
- block cadence: 5 origins
- training uses only labels whose H3 target-end date is mature by the block cutoff.

Expected historical Stage-2 anchor:

- Brier about 0.246731
- baseline about 0.249712
- relative Brier improvement about +1.19%
- log loss about 0.686634.

The repair PASS gate is reproduction within numerical tolerance; opened data cannot rescue a reproduction failure.

## 6. Frozen transport contract

Primary mode remains STRICT_FROZEN_FIT:

- fit once using only H3 labels fully mature by 2024-12-31;
- keep preprocessing and coefficients fixed through 2025/2026;
- p>=0.50 => UP, otherwise DOWN;
- conviction bands remain p>=0.55 and p<=0.45;
- no tuning from 2025/2026.

2026 reporting extends through the latest issue date whose H3 outcome is fully observable by 2026-09-30.

## 7. Source-clock audit

The repair also inventories currently registered project sources for:

- XAU current/live anchors;
- H.15 nominal/real rates;
- H.10 Broad USD / FX;
- VIX / GVZ;
- Nasdaq-100 / S&P500 / DJIA;
- WTI / Brent;
- GPR.

This inventory is metadata/coverage evidence only. The current frozen H3 CORE3 engine does not gain new external features during the repair.

## 8. Diagnostic-only drift audit

After frozen transport is scored, report without retuning:

- feature distribution shifts;
- model probability mean/dispersion;
- actual UP share;
- UP/DOWN recall;
- coefficient-sign stability from pre-2025 chronological refits;
- monthly 2026 failure pattern.

No threshold, feature, regime gate or challenger may be selected from 2025/2026 in this repair.

## 9. Output authority

The workflow must commit:

- repaired result markdown;
- summary JSON;
- current source inventory CSV;
- corrected timeline panel CSV;
- frozen H3 transport prediction ledger;
- transport metrics CSV;
- drift diagnostics CSV.

The canonical manifest is updated only after the repair run completes successfully.
