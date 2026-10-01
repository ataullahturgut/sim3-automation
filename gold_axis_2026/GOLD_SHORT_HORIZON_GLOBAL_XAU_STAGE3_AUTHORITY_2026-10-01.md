# GOLD SHORT-HORIZON GLOBAL XAU — Stage 3 Probability Calibration / Conviction Authority

**Date:** 2026-10-01  
**Status:** FROZEN PRE-RUN  
**Parent:** GOLD_SHORT_HORIZON_GLOBAL_XAU_PROJECT_MANIFEST.md

## 1. Mission

Audit whether the frozen H3 / CORE3 / Logistic L2 direction probabilities contain usable confidence information.

No new direction model is introduced.
No return-magnitude model is introduced.
No P&L rule is tested.
2025 remains frozen.

## 2. Frozen parent engine

- target: XAU_STAKTRAKR_RESEARCH_DAILY_R1
- horizon: H3
- features: CORE3 = Gold + Silver + Platinum
- model: Logistic L2
- Stage 2 status: ROBUST_PASS
- Stage 2 artifact: 11186831488

## 3. Inputs

Use only the frozen Stage-2 DEV prediction ledger:
- 2022-2024 origins
- representation = CORE3
- model = LOGIT_L2
- no 2025 rows
- no 2026 rows.

## 4. Calibration diagnostics

Report raw-probability:
- calibration intercept
- calibration slope
- Brier score
- log loss
- ECE using fixed 0.10-wide probability bins
- prediction standard deviation.

Calibration intercept/slope are descriptive diagnostics only and do not change the frozen engine.

## 5. Chronological calibration challengers

Compare:
1. RAW
2. PLATT
3. ISOTONIC

Calibration challengers are fitted only on prior matured DEV forecast/outcome pairs.

At each 5-origin block start:
- a prior calibration row with origin index j is eligible only when j + 3 <= current block start index;
- minimum calibration support = 100 rows;
- before minimum support is reached, calibrated output falls back to RAW;
- no random split;
- no future DEV outcome enters calibration.

Platt:
- one-variable logistic calibration on logit(raw p)
- effectively unpenalized LogisticRegression with fixed solver/seed.

Isotonic:
- IsotonicRegression
- out_of_bounds = clip.

## 6. Calibration replacement gate

A calibrated probability stream may replace RAW only if:
- Brier improves by at least 0.50% relative to RAW;
- log loss is not worse than RAW;
- prediction SD remains at least 0.02;
- at least 2 of 3 DEV years have non-negative relative Brier improvement vs RAW;
- no DEV year is worse than RAW by more than 2.0% relative Brier.

Otherwise retain RAW.

## 7. Frozen conviction bands

Evaluate exactly:
- <=0.40
- 0.40–0.45
- 0.45–0.50
- 0.50–0.55
- 0.55–0.60
- >=0.60.

For each selected probability stream report:
- N
- mean predicted probability
- realized H3 UP rate
- Brier
- year counts
- realized UP rate by year.

No band boundary may be changed after inspection.

## 8. Conviction-separation gate

For a direction-only economic architecture to be scientifically eligible for the next stage:

High-UP side:
- selected p >= 0.55
- N >= 60
- realized UP rate >= 57.5%.

Low-UP / DOWN side:
- selected p <= 0.45
- N >= 60
- realized UP rate <= 42.5%.

Joint:
- realized UP-rate separation between the two sides >= 15 percentage points;
- each side has at least 15 observations in at least 2 of 3 DEV years.

If these support/separation conditions fail:
- do not design a trading rule from probability thresholds;
- retain the H3 engine as probabilistic research evidence only.

## 9. 2025

2025 is CLOSED:
- no calibration fitting
- no threshold selection
- no band redesign
- no economic evaluation.

## 10. Required outputs

- selected calibration method
- aggregate RAW / PLATT / ISOTONIC metrics
- annual metrics
- reliability bins
- frozen-band table
- band-by-year table
- calibration intercept/slope
- conviction gate decision
- immutable hashes.

## 11. Next stage

If conviction gate passes:
- Stage 4 = direction-only economic architecture preregistration.

If conviction gate fails:
- stop threshold-driven tactical promotion under the current H3 probability engine.
