# R47 — 2026 May H3 original expert stack: strict historical as-of rerun gate and measured input-vintage sensitivity

**Date**: 2026-10-12. **Status**: `SOURCE_VINTAGE_SENSITIVITY_RECOMPUTED`; `FULL_EXPERT_REFIT_BLOCKED_BY_MISSING_UNREVISIONED_PIT_INPUTS`. No new H3 model score or true live firstprint is asserted. Preserve R46 and original R42 labels.

## 1. Authorized task and attempted scope

Recompute May 2026 H3 base experts (original A1/NOVA → TwelveData IRIS/AIM → SENTRY/DART/AURORA → RIFT/TURN/VEGA/OPAL → HELIOS V5 → SAGE/RuleFlow → DPTC-Q95) with only data actually available at corresponding May dates; do not shift H3's native D0→D3 source-average target.

**Root execution blocker**: `GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_DAILY_PRICES.csv` and trained/generated historical expert ledgers were built with *later frozen* StakTrakr data, some 2026 May origin prices reaggregated/revised by September. Original model training and expert posterior states were computed with these revised 2026 and pre-2026 source-vintages, and no historic May-2026 model-parameter blob / issued forecast run exists. Merely patching 21 May issue origin prices and reusing October trained coefficients/metadata does **NOT** reproduce the exact same original stacked model under historical point-in-time conditions. Some May origin prices were absent from observed contemporaneous GitHub commits. No falsified forward accuracy estimate.

## 2. Data-reconstruction work actually executed

- R46 independently re-ran the full original **2026 DPTC decision controller** on its preexisting HANDOFF timeline and recorded 2026 SAGE+RuleFlow and V5 outputs with corrected mixed-date target parsing. EXACT original 13 2026 Q95 actions reproduced, and frozen 21 May votes **17/21 = 80.95%** reproduced. That is a controller and frozen-ledger replay, NOT retraining all base learners.
- For each 21 May issue, R46 compared the 2026 pinned September `sqld` four-metal daily source with the last **sampled upstream Git repository snapshot no later than May issue day 15:00TR**. The status is 7/21 origin missing from sampled Git snapshot; 12/21 present but at least one metal revised; 2/21 fully matched.
- R47 independently numerically re-ran an **input-sensitive native H3 target reconstruction** in the 14 rows with a present sampled origin Gold price, keeping original third-source-day final target price unchanged:
  `original_y=sign(frozen_A[target_date]/frozen_A[cutoff_date])`
  versus
  `sensitivity_y=sign(frozen_A[target_date]/sampled_pre_15TR_A[cutoff_date])`.
  Two source-label directions flip (May19 and May27 issues). This is a controlled sensitivity calculation only: two vintages are mixed deliberately, and the May source prices may have represented **partial-day** averages. The fixed model votes were not recomputed on revised inputs, so this is **not** new model accuracy.
- In the subset of 14 sampled origin-available days, frozen fixed Q95 votes match original final frozen H3 source label on 11/14; if merely replacing *origin* spot with early vintage while keeping final *target* same, fixed votes match 9/14. Neither fraction is a backtest success estimate (selected nonrandom subset, partial-day/revised inputs, mismatched vendor versions, no full model retrain). Missing seven May dates must not be treated as any direction.
- On these fourteen price-available origins, absolute source revision across four metal prices:
  - Gold median **0.3457%**, max **1.8421%**.
  - Silver median **0.61665%**, max **6.6573%**.
  - Platinum median **0.66405%**, max **3.3151%**.
  - Palladium median **0.69515%**, max **2.0774%**.
  These are *single-source earliest sampled repository vintage vs later frozen*, not independent quote validation.
- Full row-level source clock, all four original/early metal prices, daily-return revision %, counterfactual target sign, Q95 decision, and Git SHA: `GOLD_R47_20261012_H3_MAY_ISSUE_VINTAGE_ORIGIN_REVISION_DIRECTION_SENSITIVITY.csv`. R46 full 21-row lineage: `GOLD_R46_20261012_MAY_H3_Q95_SOURCE_CLOCK_VINTAGE_AND_FROZEN_REPLAY_21.csv`.

## 3. Detailed changed-direction cases

| May issue | Cutoff | Original pinned gold cutoff | Sampled prior-repo gold cutoff | Pinned target source price | Original label | Origin-swap label | Frozen Q95 vote |
|---|---|---:|---:|---:|---|---|---|
| **May19** | May18 | 4547.06 | 4522.86 | 4530.49 | DOWN | UP | DOWN |
| **May27** | May26 | 4520.98 | 4542.23 | 4530.32 | UP | DOWN | UP |

The source label is *strongly sensitive* in these near-zero expected moves. These changed signs **must not be called actual genuine target labels** until the cross-source coherent daily settlement/average and full-day completion are demonstrated. This sensitivity shows that even label-direction agreement may depend on the provider's backfilled price vintage.

## 4. Why simple 'rerun with yesterday's price' cannot solve the problem

1. The main H3 panel uses rolling XAU/XAG/XPT/XPD daily price returns (lags 1,3,5,10,21; rolling sigma20) and macro/FX/exogenous publication-lag features. Revising any observation changes many subsequent training/forecast feature rows, not only one origin.
2. IRIS and AIM features arise from earlier-day 16NY hourly candle **CLOSE** and historical expert logit state, which are tied to earlier predictors generated from originally frozen price features; these must be re-fit, not just reuse May probability columns.
3. SENTRY/DART and HELIOS depend on scores of earlier *matured* H3 targets; changing target averages alters whether the expert had historically been competent. All outcome-maturity and trust state must be reconstructed, with issuer/publisher timestamps certified.
4. DPTC-Q95 itself was constructed in October 2026 *after studying 2026 failures*. Even if one could reconstruct using 2026 May historical input quotes, the historic `May07` actual-issued DPTC forecast does not exist. Present answer remains retrospective backtest / possible simulated-PIT re-estimation.

## 5. What would support a qualified genuine refit

Required before claiming full `PIT_H3_REFIT_PASS`:
- point-in-time completed (not partial) UTC full-day Au/Ag/Pt/Pd source averages for all *past model training and heldout May 2026 origins*, with first-published-at timestamps or reconstructed, validated immutable raw samples from May 2026;
- provider firstprint/revision metadata for TwelveData XAU 1h, CME official final releases, cross-market daily, COT, H15/H10 and target labels, with stable source/vintage joins;
- rebuild base learner panels and fit monthly rolling models from training matured strictly before each issue; record model params/code SHA/provenance and exact issued_at clock; verify original 2026 Q95 posthoc limitation independently.
- outside-sample dates after 2026-10-05 (not May 2026) to validate *prospective performance* of already frozen Q95 or a preregistered successor.

**Decision**: `FULL_EXPERT_REFIT=BLOCKED`; `SOURCE_INPUT_VINTAGE_AUDIT=COMPLETE`; `H3_LABEL_SENSITIVITY=RECOMPUTED`; `ORIGINAL_FROZEN_Q95_REPLAY=17/21, NOT LIVE`; `PIT_MAY_Q95_ACCURACY=UNKNOWN`. Do not report 9/14 or 17/21 as verified original H3 May real-time prediction accuracy.

## Source references
- Repo `ataullahturgut/sim3-automation`, branch `gold-execution-channel-audit-20261006`: R42/R45/R46 code/artifacts; scripts `gold_short_horizon_global_xau_readiness_r2.py`, `gold_h3_nova_v1.py`, `gold_h3_iris_v1.py`, `gold_h3_aim_v1.py`, `gold_h3_dptc_v1.py`.
- Upstream `lbruton/StakTrakr/data/spot-history-2026.json` at historical issuer-period Git snapshots (SHA per R46), compared with source-pinned `54fdf1c8d39b7b6c7b874d0f30f784296e886044`.
- Daily price firstprint repair details in upstream `devops/pollers/shared/spot-year-history.js` (STRK-403): previously frozen **partial-day** `sqld` average was overwritten by a completed UTC-day reaggregation in corrected historic history.
