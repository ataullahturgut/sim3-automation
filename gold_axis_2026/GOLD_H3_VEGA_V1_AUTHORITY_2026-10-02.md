# VEGA-H3 V1 — VOLATILITY-EXPECTATIONS GAP REVERSAL AUTHORITY

**Date:** 2026-10-02
**Identity:** `VEGA_H3_V1_RESEARCH`
**Parent:** `AURORA_H3_V1_RESEARCH`
**Motivation ancestors:** `RIFT_H3_V1_RESEARCH`, `TURN_H3_V1_RESEARCH`
**Status:** PREREGISTERED / POST-HOC MECHANISM RESEARCH

## 1. Scientific question

AURORA is highly accurate when 12-hour XAU momentum continues and weak when the next H3 move reverses it.

RIFT showed that origin-time price-path reversal features contain some signal but are not stable enough across 2023-2024.
TURN showed that a literature-derived realized-semivariance tail rule is also insufficient.

VEGA tests a genuinely new information channel:

**does the forward-looking options-implied volatility state contain information about whether current XAU momentum is about to reverse?**

## 2. Forward-looking source

- Cboe Gold ETF Volatility Index (GVZ), historical daily close via FRED series `GVZCLS`.
- GVZ is derived from GLD option prices and represents forward-looking expected gold volatility.
- Historical research use only.
- To avoid close-time ambiguity, an H3 origin on feature date D may use only GVZ observations dated **D-1 calendar day or earlier**.

## 3. XAU state

Same validated IRIS 1-hour XAU source:
- anchor 16:00 America/New_York on feature_cutoff_date;
- no issue-date or later XAU bar.

Reversal target:
`REVERSAL = 1[sign(H3 return) != sign(h_ret_12)]`.

VEGA acts only when AURORA direction agrees with 12-hour momentum.

## 4. Fixed VEGA feature set

At each origin, using GVZ only through D-1:

1. `gvz_z252`: current GVZ minus prior-252-observation mean, divided by prior-252 std.
2. `gvz_r1`: 1-observation log change.
3. `gvz_r3`: 3-observation log change.
4. `gvz_r5`: 5-observation log change.
5. `gvz_vs_med20`: log(current GVZ / prior-20-observation median).
6. `iv_rv24_gap`: log((GVZ/100/sqrt(252)) / h_rv_24).
7. `iv_rv48_gap`: log((GVZ/100/sqrt(252)) / (h_rv_48/sqrt(2))).
8. `trend_strength`: abs(h_ret_12)/(h_rv_12+eps).
9. `gvz_shock_x_trend`: gvz_r3 * trend_strength.

No feature search is allowed.

## 5. Reversal head

Model:
- StandardScaler
- LogisticRegression C=1.0
- class_weight=balanced
- monthly expanding refit
- target-maturity rule enforced.

No regularization search.

## 6. Fixed routing

AURORA is default.

If:
- AURORA direction agrees with 12h momentum; and
- VEGA `p_reversal >= 0.70`;

then flip the AURORA direction.

Otherwise retain AURORA.

For a flip:
- if momentum is UP: `p_up = 1-p_reversal`;
- if momentum is DOWN: `p_up = p_reversal`.

Threshold 0.70 is frozen before the run.

## 7. Evaluation

This architecture was motivated after inspecting historical errors including 2026. Therefore all 2022-2026 results are **RETROSPECTIVE_MECHANISM_VALIDATION**, not pristine lockboxes.

Report separately:
- 2022 H2
- 2023
- 2024
- 2025
- 2026
- 2023-2024
- 2025-2026.

Mechanism pass requires:
- 2023 accuracy >= AURORA -1 pp
- 2024 accuracy >= AURORA -1 pp
- 2023 Brier <= AURORA +0.003
- 2024 Brier <= AURORA +0.003
- 2023-2024 aggregate balanced accuracy >= AURORA
- 2023-2024 net rescue > 0.

## 8. Dependence-aware audit

If mechanism passes:
- paired circular moving-block bootstrap
- 10,000 replicates
- block lengths 5 and 10
- VEGA vs AURORA
- periods 2023-2024, 2025-2026, 2026.

## 9. Governance

No 2022-2026 result may change:
- GVZ lag convention;
- feature definitions;
- model class / C;
- reversal threshold.

The existing AURORA prospective ledger remains immutable.

If VEGA passes retrospectively, it must be frozen under a separate future challenger identity before any prospective comparison.
