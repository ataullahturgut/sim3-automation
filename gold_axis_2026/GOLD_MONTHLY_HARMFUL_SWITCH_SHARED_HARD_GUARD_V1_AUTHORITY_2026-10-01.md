# GOLD MONTHLY — Harmful-Switch / Shared-Hard Safety Guard V1 Authority

**Date:** 2026-10-01  
**Status:** DEV-ONLY SAFETY-GUARD AUTHORITY / NO PRODUCTION SWITCH

## 1. Purpose

The frozen Rescue-Gain Predictor V1 can identify positive aggregate rescue headroom, but its DIRECT_SWITCH policy still produces harmful switches. This stage asks:

> Can an origin-known safety guard veto low-quality switch recommendations while preserving meaningful rescue gains?

The guard does not change ChHHO, Specialist Hedge, the Exact16 pool, or the frozen Rescue-Gain Predictor V1.

## 2. Frozen upstream stack

- Main forecast: ChHHO_ANFIS.
- Reliability router: frozen Specialist Hedge.
- Rescue predictor: **RIDGE_CORE_A10**.
- Base action policy: **DIRECT_SWITCH**.
- Challenger pool: frozen 15 Exact16 alternatives.
- DEV authority: 2022-04..2024-12.
- 2025/2026 may only be used after the DEV guard is frozen.

## 3. Guard target

The guard acts only when:
1. Specialist Hedge warns; and
2. frozen Rescue-Gain Predictor V1 recommends SWITCH.

Guard action:
- ALLOW -> execute the frozen challenger switch.
- VETO -> KEEP MAIN.

ABSTAIN is equivalent to VETO / KEEP for scoring.

## 4. Origin-known guard diagnostics

Derived only from frozen predictor outputs and origin-known context:
- top predicted rescue gain;
- selected challenger's historical residual RMSE;
- top-gain / residual-RMSE ratio;
- fraction of 15 challengers with predicted positive rescue gain (positive breadth);
- median predicted rescue gain across 15 challengers;
- second-best predicted rescue gain and top-vs-second margin;
- p_HIGH / p_ELEVATED;
- Exact16 direction agreement and dispersion;
- ChHHO ensemble-median / IQR position.

No realized target-month error or severity may enter the guard decision.

## 5. Pre-registered deterministic guard candidates

Baseline:
- **NO_GUARD**: allow every frozen DIRECT_SWITCH.

Breadth gates:
- **BREADTH_50**: allow when positive breadth >= 0.50.
- **BREADTH_67**: allow when positive breadth >= 2/3.
- **BREADTH_80**: allow when positive breadth >= 0.80.

Confidence gates:
- **CONF_050**: allow when top predicted gain >= 0.50 × selected-challenger residual RMSE.
- **CONF_100**: allow when top predicted gain >= 1.00 × residual RMSE.
- **CONF_150**: allow when top predicted gain >= 1.50 × residual RMSE.

Combined gates:
- **BREADTH67_CONF050**
- **BREADTH67_CONF100**
- **BREADTH50_CONF100**

All thresholds are frozen before opened transport.

## 6. DEV evaluation protocol

To reduce same-sample rule selection risk:

### A. Full DEV descriptive table
Report every guard candidate on the same chronological warning decisions used by Predictor V1.

### B. Expanding guard-selection replay
- First **4 frozen predictor switch opportunities** are guard-selection warm-up.
- Starting with the 5th switch opportunity, select among the pre-registered guards using only prior switch opportunities.
- Selection objective: highest prior cumulative gain versus KEEP.
- Tie-breaks: fewer harmful allowed switches, lower worst incremental harm, lower action coverage.
- Evaluate the selected guard on the next opportunity, then update history.

This replay is the main scientific gate.

### C. Final DEV freeze for opened transport
Only if the expanding replay improves versus NO_GUARD/KEEP in a meaningful way, freeze one deterministic candidate using DEV only. Final-candidate preference:
1. positive full-DEV gain versus KEEP;
2. fewer harmful switches than NO_GUARD;
3. lower worst incremental harm;
4. retain at least two beneficial switches.

## 7. Scientific gate

A guard is not accepted merely for increasing cumulative gain. It must also reduce harmful-switch count or worst incremental harm versus NO_GUARD.

Even a DEV PASS does not authorize production. The frozen guard must be transported to already-opened 2025..2026 without retuning.

## 8. Opened transport boundary

2025/2026 is descriptive only. It may answer:
- whether cumulative rescue gain is preserved;
- whether harmful-switch count falls;
- whether the 2026-03 shared-hard failure is vetoed.

It may not alter guard thresholds, candidate set, predictor, or challenger pool.
