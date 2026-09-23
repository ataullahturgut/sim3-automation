# GOLD CONTROL — RESIDUAL ONE-SIDED UP-2 LOGIT V1 INTEGRITY AMENDMENT

**Date:** 2026-09-23  
**Identity:** `RESIDUAL_ONE_SIDED_UP2_LOGIT_V1_RESEARCH`  
**Timing:** before any model scoring.

## Reason

Preregistration section 6 asked for exact-date external-vs-governed diagnostics on all nine UP-2 inputs.

That wording is too broad for model-state features:
- `sqrt_score` is source/year formation-specific by construction;
- `direct_up_fraction` and `legacy_up_fraction` are outputs of frozen experts/context reconstructed on each source chronology.

They are not raw feed quantities and therefore should not be forced to numerically match across providers on the same date.

## Frozen clarification

Cross-source exact-date harmonization diagnostics apply only to the **source-derived market-state inputs**:

1. `lag1_close_return`
2. `downside_share`
3. `intraday_end_norm`
4. `close_location`
5. `trough_recovery_norm`
6. `last_quarter_return_norm`

The three model/context-state features are validated instead by their own frozen aggregate reconstruction contracts:

- `sqrt_score`: exact frozen SQRT alarm counts/intersections must reproduce;
- `direct_up_fraction`: direct-expert states feed the exact Router reconstruction;
- `legacy_up_fraction`: frozen legacy context feeds the exact Router reconstruction.

No feature, parameter, threshold, target-year outcome, or gate is changed by this amendment.

If raw/source-derived feature harmonization is materially poor, the study is blocked before scoring.
