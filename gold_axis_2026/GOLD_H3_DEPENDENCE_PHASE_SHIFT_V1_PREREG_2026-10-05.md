# GOLD H3 — Dependence Phase-Shift V1 Preregistration

**Date:** 2026-10-05
**Status:** label-free dependence-structure diagnostic.

## Motivation

The broad multi-view mean-shift detector did not identify the April-May 2026 competence transition. Yet Handoff alarms show a sharp chronology change:
- before 2026-04-30: strong-pro-risk topology is absent;
- from 2026-04-30 onward: strong-pro-risk topology becomes frequent.

This suggests **dependence/correlation drift**, not marginal feature drift.

## Origin-safe topology

At every origin, using the prior 60 origins only:
- r_GN = corr(Gold daily return, Nasdaq return)
- r_GV = corr(Gold daily return, VIX return)
- STRONG_PRO_RISK iff r_GN > 0, r_GV < 0, and at least one two-sided Pearson p < 0.05.

## Label-free phase diagnostics

1. **Persistence run length**
   - consecutive STRONG_PRO_RISK origin count.
   - calibrate run-length q95 and q99 using origins before 2026-01-01 only.

2. **Correlation-vector shift**
   - vector = [r_GN, r_GV]
   - reference = prior 120 topology observations excluding latest 5
   - recent = current + prior 4
   - robust standardized mean-shift norm.
   - q95 calibrated before 2026 only.

3. **DEPENDENCE_PHASE**
   - STRONG_PRO_RISK is true, and
   - either run length is above pre-2026 q95 or correlation-vector shift is above pre-2026 q95.

No Handoff outcomes or reversal labels enter these thresholds.

## Report

- pre-2026 run-length calibration and max run
- first 2026 persistence/shift/phase dates
- Handoff rescue/broken precision inside vs outside the phase for 2025 and 2026
- whether phase onset precedes SELLR trigger (2026-05-21) and BOCPD V4 entry (2026-05-27)

This diagnostic does not create a trading rule.
