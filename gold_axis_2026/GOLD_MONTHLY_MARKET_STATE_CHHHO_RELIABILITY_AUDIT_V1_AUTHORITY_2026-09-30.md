# GOLD MONTHLY — Frozen Market-State × ChHHO Reliability Audit V1 Authority

**Date:** 2026-09-30  
**Status:** PRE-REGISTERED / DOWNSTREAM AUDIT ONLY

## 1. Question

Do the already-frozen market-state layers carry information about the next-month forecast reliability of the primary ChHHO-ANFIS model?

This is a downstream audit. It does **not** modify:
- R0/R1/R2;
- Transition V2;
- Extreme V1;
- ChHHO;
- any alarm definition.

## 2. Critical chronology / join rule

The project forecast is H=1.

For a ChHHO forecast row:
- origin month = t;
- forecast target = t+1.

Therefore market state must be joined by **origin month t**, never by target month t+1.

Example:
- Extreme status dated 2026-01 is information available at the 2026-01 origin and is evaluated against the ChHHO forecast for target 2026-02.

This rule is binding and prevents target-month state leakage.

## 3. Inputs

Frozen upstream evidence:
- ChHHO forecast/error rows from GOLD_MONTHLY_R0_R1_R2_REGIME_ALARM_AUDIT_V1_2026-09-30.json.
- Transition Detector V2 artifact.
- Within-Regime Extreme V1 artifact.

Primary market-state schedule:
- **EXPANDING_REFIT**.

Secondary sensitivity:
- **ANNUAL_ANCHORED**.

## 4. Combined state categories

For each origin month:

1. BOTH
   - Transition V2 = TRANSITION;
   - Extreme V1 = EXTREME.

2. TRANSITION
   - Transition V2 = TRANSITION;
   - Extreme V1 != EXTREME.

3. EXTREME
   - Extreme V1 = EXTREME;
   - Transition V2 != TRANSITION.

4. NORMAL
   - Extreme V1 = NORMAL;
   - Transition V2 != TRANSITION.

5. DEFER
   - Extreme V1 = DEFER;
   - Transition V2 != TRANSITION.

No month is reclassified from its frozen upstream outputs.

## 5. Evaluation windows

### DEV
Target months:
- 2022-04..2024-12
- 33 months
- origin months 2022-03..2024-11.

This is the primary reliability audit window.

### 2025 opened transport
Target months:
- 2025-01..2025-12
- 12 months.

### 2026 opened stress/transport
Target months:
- 2026-01..2026-08
- 8 months.

### Combined opened transport
- 2025-01..2026-08
- 20 target months.

2025/2026 are descriptive only and must not be used to retune any market-state rule.

## 6. Forecast-error metrics

For each state category and period report:

- n;
- cumulative absolute error ΣAE;
- MAE;
- median AE;
- RMSE;
- mean APE;
- median APE;
- worst AE;
- HIGH count/rate;
- MEDIUM count/rate;
- NORMAL count/rate.

Severity is taken unchanged from the existing alarm audit:
- NORMAL < 2.50% APE
- MEDIUM 2.50% to <3.00%
- HIGH >=3.00%.

## 7. Direction metric

For each target month:
- recover origin-month actual price from the prior contiguous ChHHO row whose target equals the current origin;
- predicted direction = forecast price vs origin-month actual;
- actual direction = target actual vs origin-month actual.

Report:
- direction-correct count;
- direction accuracy.

If an origin actual cannot be recovered, direction is NA for that row only.

## 8. Primary contrasts

For EXPANDING_REFIT, report without fitting or tuning:

- EXTREME vs NORMAL:
  - MAE ratio;
  - mean APE difference;
  - HIGH-rate difference;
  - direction-accuracy difference.

- TRANSITION vs NORMAL:
  - same contrasts.

- DEFER vs NORMAL:
  - same contrasts.

- BOTH vs NORMAL if BOTH has at least one observation.

If a category has n=0, report NA.

## 9. Regime-stratified reporting

Where event count permits, report the same error summary by:
- semantic regime R0;
- semantic regime R1;
- semantic regime R2;
crossed with state category.

Do not report a subgroup as stable evidence when n<3; label it SMALL_N.

The semantic regime used is the frozen current-origin regime output from the same schedule.

## 10. Statistical diagnostic

No model or threshold is selected from this audit.

For the primary DEV EXTREME-vs-NORMAL contrast, if both groups have n>=3:
- report a two-sided Mann-Whitney U p-value;
- report a deterministic bootstrap 95% CI for the MAE difference (EXTREME - NORMAL), 10,000 resamples, fixed seed 20260930.

For TRANSITION-vs-NORMAL, do the same if both n>=3.

These are diagnostics only; no p-value threshold controls promotion.

## 11. Interpretation

This audit may conclude:
- state separation appears useful;
- state separation is weak/mixed;
- or a state is associated with lower rather than higher error.

Do not assume EXTREME must mean forecast failure.

A market state is not authorized for alarm weighting solely because its mean error is larger in opened 2025/2026.

## 12. Governance

Forbidden:
- changing any upstream state threshold after seeing ChHHO errors;
- selecting Extreme signals based on forecast errors;
- retuning Transition V2;
- choosing alarm thresholds;
- routing/model switching;
- forecast correction.

The only action in this stage is frozen downstream measurement.
