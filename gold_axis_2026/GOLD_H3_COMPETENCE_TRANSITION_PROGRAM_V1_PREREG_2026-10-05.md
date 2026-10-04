# GOLD H3 — Competence Transition Program V1 Preregistration

**Date:** 2026-10-05
**Status:** multi-view mechanism research + post-hoc synthesis challenger.
**Objective:** explain and exploit the apparent 2026 transition in Handoff expert competence without reducing the problem to a single static regime or one tuned threshold.

## Existing facts frozen before this program

1. Combined baseline: 126/191 = 65.97%, BA 66.31%.
2. Frozen pre-2026 SELLR challenger:
   - threshold = 2.3677413378977423
   - selected on 2025 only
   - 2026 stress: one action, one rescue, zero broken.
3. BOCPD Handoff V4 hysteresis:
   - post-hoc development result = 10 actions, 8 rescue, 2 broken, net +6
   - 132/191 = 69.11%
   - competence entry = 2026-05-27
4. Adversarial audit:
   - 92.6% of 162 nearby parameter combinations have positive net
   - chronology permutation P(net >= +6) = 0.0284
   - stationary 2025-competence null P(net >= +6) = 0.0004
   - offline competence split around 2026-04-30.

This program must not relabel V4 as independent validation.

# Workstream A — Label-free multi-view drift

Goal: detect whether market geometry itself changes before the competence transition, without using reversal outcomes or Handoff rescue/broken labels.

## Views

### A1 Internal structure
- |h_ret_12|
- trend_strength
- adverse_excursion
- path_consistency
- opposite_semivar_share
- session_against_trend
- trend_close_location

### A2 Options / liquidity
- signed_opt_pressure
- signed_d_opt_pressure
- opt_total_z20
- gc_volume_z20
- gc_volume_accel_5

### A3 Cross-asset / macro geometry
- core_confirmation
- cross_dispersion
- gold_daily_ret1
- usd_ret1
- tnx_chg1
- ndx_ret1
- vix_ret1

## Drift score

For every origin:
- reference window: prior 120 origins, excluding the latest 5;
- recent window: current + prior 4 origins;
- robust location = reference median;
- robust scale = 1.4826 * MAD, fallback to reference std;
- per-view score = Euclidean norm of the standardized recent-vs-reference mean shift.

Pre-2026 calibration uses 2023-2025 only and no target labels.

For each view:
- q90 and q95 are fixed from its 2023-2025 score distribution.
- View alarm = score >= q95.
- Broad view alarm = score >= q90.

Multi-view drift definitions:
- STRICT2 = at least two q95 view alarms.
- BROAD2 = at least two q90 view alarms.
- FISHER99 = combined `sum(-log(1 - percentile_view))` >= its 99th percentile in 2023-2025.

Report first 2026 dates and Handoff rescue/broken prevalence inside vs outside these states.
These states are diagnostic only; no trading threshold is selected from 2026.

# Workstream B — SELLR-triggered competence state (STCR)

This is a post-hoc synthesis challenger, not an independent OOS result.

Entry:
- canonical Handoff alarm is present;
- frozen SELLR signal fires using the already-selected 2025 threshold 2.3677413378977423;
- enter TRUST immediately at that origin.

Persistence:
- remain TRUST on subsequent canonical Handoff alarms;
- exit only after two consecutive **matured acted BROKEN** outcomes;
- any matured acted RESCUE resets broken streak to zero.

No BOCPD entry threshold is used.
This asks whether an independently frozen structural reversal signal can serve as the catalyst for a longer-lived competence regime.

Report:
- 2025 formation behavior;
- 2026 entry date;
- actions/rescue/broken/net/precision;
- assisted accuracy/BA;
- remaining-53 rescues;
- month-deletion robustness;
- entry-location permutation benchmark.

# Workstream C — Online expert aggregation

Treat KEEP and Handoff-FLIP as two experts with delayed outcome feedback.

Evaluate fixed-share Hedge with:
- adaptive learning rate: eta_t = sqrt(8*log(2)/t), where t is matured Handoff feedback count;
- fixed-share alpha in {0.02, 0.05, 0.075, 0.10};
- initial weights 0.5 / 0.5;
- process all 2025 formation outcomes first;
- in 2026 update only when target_end_date_h3 has matured;
- FLIP only when Handoff expert weight > KEEP weight.

No alpha is selected from 2026.
Alpha=0.05 is the named central prior, corresponding approximately to one expert-regime switch per 20 matured Handoff alarms.

Report all four variants.

# Workstream D — Convergence test

The program is considered mechanistically encouraging only if at least two of the following independently point to the same broad transition region:
- label-free multi-view drift,
- frozen SELLR trigger,
- online fixed-share weight crossing,
- BOCPD/V4 competence entry,
- offline competence change point.

No date is manually aligned.

# Governance

- 2026 labels cannot alter Workstream A thresholds.
- SELLR threshold is inherited unchanged from the pre-2026 tournament.
- STCR is explicitly post-hoc synthesis and must be labeled as such.
- Fixed-share variants are all reported; no 2026 winner picking.
- The purpose is to identify a reproducible competence-transition mechanism and define a prospective controller, not to maximize retrospective 2026 accuracy.
