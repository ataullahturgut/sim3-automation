# GOLD MONTHLY — Alarm False-Call Suppressor Screen V1 Authority

**Date:** 2026-09-30
**Status:** PRE-REGISTERED EXPLORATORY SCREEN
**Scope:** DEV 2022-04..2024-12 only. Test whether origin-known cross-model forecast consensus can suppress false alarms without suppressing true HIGH/MEDIUM alarms.

## 1. Motivation

Existing A/B/C/D/E/G/H/I1/I2/T1 signals are risk-oriented. None is an explicit SAFE / anti-alarm signal.

Simple signal voting is not a valid suppressor because multiple simultaneous risk warnings can still occur in NORMAL months.

Test a distinct origin-known source of evidence:
**cross-model forecast consensus.**

## 2. Data

Use the exact 16-model competitive DEV pool frozen by Cross-Model Error Overlap V1:
- competitive rule: DEV ΣAE <= 1.15 × ChHHO DEV ΣAE;
- exact per-origin forecasts already retained;
- no model is retrained for this screen.

Use Unified Alarm Matrix V2 for alarm outcomes.

Scope:
- DEV targets 2022-04..2024-12 only.

No 2025/2026 model-selection data enter suppressor construction.

## 3. Origin-known consensus features

At each origin, using only forecasts available at that origin:

- MEDIAN_FCST = median competitive-model forecast.
- IQR_FCST = Q75 - Q25 of competitive forecasts.
- DISPERSION_PCT = IQR_FCST / abs(MEDIAN_FCST) ×100.
- CHHHO_DEV_PCT = abs(ChHHO forecast - MEDIAN_FCST) / abs(MEDIAN_FCST) ×100.
- RW = frozen random-walk price available at origin.
- UP_SHARE = share of competitive forecasts above RW.
- DOWN_SHARE = share below RW.
- DIRECTION_CONSENSUS = max(UP_SHARE, DOWN_SHARE).
- CHHHO_DIRECTION_AGREEMENT = share of competitive models having the same direction as ChHHO versus RW.

No actual target price is used to compute these features.

## 4. Candidate SAFE vetoes

These are fixed before viewing screen outcomes.

### V1_TIGHT_CENTRAL
From month 7 onward, using only prior months' consensus features:
- DISPERSION_PCT <= expanding prior Q25; AND
- CHHHO_DEV_PCT <= expanding prior median.

Interpretation: models are tightly clustered and ChHHO is not an outlier.

### V2_STRONG_DIRECTION_CONSENSUS
- CHHHO_DIRECTION_AGREEMENT >= 0.80; AND
- DISPERSION_PCT <= expanding prior median.

### V3_CENTRAL_ONLY
- CHHHO_DEV_PCT <= expanding prior Q25.

Expanding thresholds use only prior forecast states, never target outcomes.

Minimum prior history = 6 DEV origins. Months before sufficient history are INELIGIBLE, not forced to false.

## 5. Evaluation

Apply each veto separately to:
- T0_STANDARD = A/B/C/D/H;
- T0_ALL_VISIBLE = A/B/C/D/E/G/H/I1/I2;
- ANY_VISIBLE = all T0 signals plus T1_WGC.

For alarm events eligible for the veto, report:
- false calls removed;
- HIGH hits incorrectly suppressed;
- MEDIUM hits incorrectly suppressed;
- retained HIGH recall within the full DEV HIGH set;
- false-call rate before and after among eligible alarm events.

Also report exact target lists.

## 6. Interpretation

A useful suppressor should remove multiple NORMAL false calls while suppressing few or no HIGH/MEDIUM hits.

This screen is exploratory and does not authorize a production veto even if a candidate looks favorable.

No new alarm thresholds may be tuned from results.
