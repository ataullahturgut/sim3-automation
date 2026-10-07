# GOLD SESSION — DPTC STAGE-1C / STAGE-2 PREREGISTRATION

**Date:** 2026-10-07
**Status:** **PREREGISTERED BEFORE SESSION-SELLR / DPTC DEVELOPMENT RESULTS**

## 1. Identity

Historical H3 SELLR scores, bin edges, LLR tables and threshold `2.3677413378977423` are prohibited.

A new **SESSION-SELLR V1** preserves only the recovered algorithmic idea:

`signed feature -> quintile bin -> Laplace-smoothed log P(bin|reversal)/P(bin|continuation) -> additive score`.

DPTC remains a correction/meta-trust controller, not a new stand-alone direction model.

## 2. Chronology

- **2023:** SESSION-SELLR fitting and threshold calibration only.
- **2024:** untouched development selection / DPTC evaluation.
- **2025:** closed until the 2024 transport gate is frozen.
- **2026:** not read.

This split prevents fitting the new SESSION score on the same outcomes used to claim development performance.

## 3. SESSION reversal target

Per partition/window:

`reversal_target = 1[y_up != momentum_up]`

where `momentum_up` is the sign of the pre-target 12-hour XAU return.

## 4. Frozen 11-feature identity

Recovered SELLR features and signs:

1. `adverse_excursion` (+)
2. `trend_strength` (-)
3. `trend_close_location` (-)
4. `session_against_trend` (+)
5. `opposite_semivar_share` (+)
6. `signed_opt_pressure` (+)
7. `signed_d_opt_pressure` (+)
8. `core_confirmation` (-)
9. `cross_dispersion` (+)
10. `topology_rotation` (+)
11. `trend_age` (+)

### Clock rules

- XAU intraday/path features use completed observations strictly before `start_utc`.
- CME daily option-volume state uses a synthetic conservative availability embargo: trade-date D becomes usable no earlier than **00:00 New York on D+1**; session lookup must satisfy availability <= session start.
- Daily cross-market state uses source observations from dates strictly before the session's New-York calendar date.
- Topology is a once-per-daily-state process and must not advance multiple times because several sessions occur on the same date.
- `trend_age` is independent same-window momentum-run age.

## 5. SESSION-SELLR fit

For each `(partition, window)` independently:

- minimum 2023 fitting rows: **80**;
- fit feature quintile edges from 2023 only;
- missing feature values are imputed with the 2023 training median for that feature;
- estimate Laplace-smoothed per-bin LLRs from 2023 reversal/continuation outcomes;
- score 2024 with the frozen 2023 spec;
- candidate thresholds are Q80 / Q85 / Q90 / Q95 of the **2023 fitted score distribution**;
- candidate action is allowed only when the development-frozen balanced base still follows pre-target momentum.

### 2024 SELLR threshold eligibility

- actions >= 4;
- precision >= 60%;
- net rescue > 0;
- action rate <= 15%;
- worst action-month net >= -1.

Tie-break if multiple thresholds pass:
1. highest net rescue;
2. highest precision;
3. fewer actions;
4. higher quantile.

No Handoff confirmation is added to SELLR itself.

## 6. Dependence phase

The daily dependence topology is label-free.

Calibration uses daily states through **2023 only**:

- Q95 strong-run threshold;
- Q99 strong-run threshold;
- Q95 dependence-shift threshold.

For every 2024 session, attach the latest topology state whose daily origin is strictly before the session's NY calendar date.

Frozen variants:

- **DPTC-Q95:** strong_pro_risk AND (strong_run > q95_run OR dep_shift >= q95_shift)
- **DPTC-Q99:** strong_pro_risk AND (strong_run > q99_run OR dep_shift >= q95_shift)

## 7. Handoff and baseline

Use the already-governed exact-clock SESSION Handoff reconstruction and the development-frozen balanced base per partition/window.

DPTC operates only on canonical Handoff alarm events:

- `leadlag_score_premax >= 0.60`;
- `internal_now >= 0.60`;
- `internal_d1 >= 0`;
- baseline direction follows pre-target momentum.

Competence outcome:
- RESCUE=1 when a flip corrects a base error;
- BROKEN=0 when a flip destroys a correct base call.

## 8. DPTC state

State is independent by partition/window.

- TRUST starts false.
- Before TRUST, a dependence-phase Handoff may act as PHASE.
- SESSION-SELLR catalyst on a Handoff enters TRUST.
- While TRUST, every Handoff acts.
- The current target outcome never affects its own decision.
- Only prior acted outcomes with `end_utc <= current start_utc` mature.
- RESCUE resets broken streak.
- BROKEN increments broken streak.
- Exit TRUST after **2 consecutive matured acted BROKEN** outcomes.

## 9. 2024 gate to frozen 2025 transport

A partition/window/variant may open 2025 only if:

- actions >= 4;
- net rescue > 0;
- precision >= 60%;
- assisted Balanced Accuracy >= baseline Balanced Accuracy;
- assisted Accuracy >= baseline Accuracy;
- worst action-month net >= -1.

Q95 and Q99 are separately frozen variants. 2025 may not choose between them.

If no head passes, DPTC closes **NOT PROMOTED** without opening 2025.

## 10. Governance

- No 2025 target/model outcome may be read during Stage-2.
- No H3 SELLR scores or H3 target outcomes may enter the SESSION model.
- No threshold may be changed after Stage-2 results are observed.
