# SESSION OPAL V1 — PREREGISTRATION / IDENTITY CONTRACT

**Date:** 2026-10-07  
**Status:** BINDING BEFORE SESSION RUN

## Role

OPAL is a COT/options-positioning reversal specialist layered on top of fresh SESSION AURORA.

It is not a primary direction engine.

## Upstream

Mandatory upstream:
- fresh SESSION AURORA probability/state;
- pre-target XAU hourly momentum state.

Archived H3 AURORA/OPAL predictions are prohibited.

## Reversal target

For each session row:

- `momentum_up = 1` when pre-target 12h XAU hourly return >= 0;
- otherwise `momentum_up = 0`.

Reversal target:
- 1 when actual session direction differs from `momentum_up`;
- 0 otherwise.

## Canonical OPAL features

Exactly 18 variables:

- opt_mm_net
- opt_prod_net
- opt_swap_net
- opt_other_net
- d_opt_mm_net
- d_opt_prod_net
- opt_mm_z52
- opt_prod_z52
- opt_swap_z52
- opt_other_z52
- spec_hedger_gap
- spec_swap_gap
- fut_mm_net
- fut_prod_net
- trend_x_opt_mm
- trend_x_opt_prod
- trend_x_spec_hedger_gap
- trend_strength

Trend terms use the sign of pre-target 12h XAU momentum.

`trend_strength = abs(ret_12h) / (rv_12h + eps)`.

## COT publication-time rule

Binding corrected authority:
- use `GOLD_COT_GOLD_PIT_STATE_RAW_REBUILT_2026-10-06.csv`;
- use only the latest report satisfying:
  `cot_available_at_utc <= session_start_utc`;
- official delayed publication dates override the default schedule;
- no date-only +7 shortcut.

## Estimator

Frozen historical OPAL estimator:
- StandardScaler
- LogisticRegression(C=1.0, class_weight=balanced)
- reversal threshold = 0.70
- random seed = 20261003

Minimum matured same-window training rows:
- 80.

## Causal replay

State is independent by partition/window.

For each session/month:
- train only on same-window rows whose target `end_utc` is no later than the first target start in the scored month;
- fit the reversal model on matured history only;
- score the untouched month;
- no current or overlapping session outcome enters training.

## Correction rule

Start from fresh AURORA probability.

Only when:
1. AURORA direction follows pre-target momentum, and
2. OPAL reversal probability >= 0.70

may OPAL override AURORA.

If momentum is UP and OPAL fires:
- `p_opal = 1 - p_reversal`.

If momentum is DOWN and OPAL fires:
- `p_opal = p_reversal`.

Otherwise:
- `p_opal = p_aurora`.

## Evaluation chronology

- 2023–2024: development / confirmation
- 2025: frozen transport only for OPAL heads passing pre-2025 gate
- 2026: unopened

## Frozen pre-2025 acceptance gate

For each session:

1. 2023 OPAL accuracy no worse than AURORA by >1 pp.
2. 2024 OPAL accuracy no worse than AURORA by >1 pp.
3. 2023 OPAL Brier no worse than AURORA by >0.003.
4. 2024 OPAL Brier no worse than AURORA by >0.003.
5. 2023–2024 combined OPAL Balanced Accuracy >= AURORA Balanced Accuracy.
6. combined minimum class recall >= 30%.
7. combined net rescue > 0.
8. at least one actual override by end-2024.

Only heads passing all conditions may open 2025.

No 2025 result may alter:
- the 18-feature set;
- C=1.0;
- class weighting;
- minimum training rows;
- 0.70 reversal threshold;
- COT availability rule;
- momentum horizon;
- correction logic.
