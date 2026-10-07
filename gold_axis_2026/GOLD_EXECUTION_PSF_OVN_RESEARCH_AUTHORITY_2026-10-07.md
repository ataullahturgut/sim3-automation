# GOLD EXECUTION PSF-OVN RESEARCH AUTHORITY — 2026-10-07

**Status:** PREREGISTERED / DEVELOPMENT-ONLY CHALLENGER
**Target:** 17:00 -> next eligible 09:00 Europe/Istanbul
**Decision origin:** 17:00 Europe/Istanbul
**Selection:** 2023 only
**Confirmation:** 2024
**Transport:** 2025 retrospective frozen transport only
**2025 selection use:** FORBIDDEN

## Scientific motivation

The existing overnight work established that:
- the 16:00-16:30 impulse contains continuous predictive information;
- a simple reversal/first-impulse specialist is stable but only moderately accurate;
- broad hand-built volatility/jump interactions did not improve transport;
- sparse PATH/STRUCTURAL rescue gating does not have enough common-row evidence.

The next challenger therefore changes representation rather than adding more hand-tuned rules.

Literature basis:
1. Choi (2026), Journal of Forecasting, DOI 10.1002/for.70176:
   lead-lag path signatures encode sequential geometry and realized quadratic variation; empirical finance tests include gold.
2. Kokoszka & Zhang (2012), DOI 10.1177/1471082X1201200404:
   cumulative intraday return curves can be modeled as functional objects.
3. Kokoszka & Reimherr (2013), DOI 10.1111/ectj.12006:
   shapes of intraday price curves can contain predictable structure.
4. Jasiak et al. (2026), Journal of Forecasting, DOI 10.1002/for.70127:
   rolling FPCA can forecast incomplete/intraday return functions at 15-minute frequency.
5. Ma et al. (2025), Global Finance Journal, DOI 10.1016/j.gfj.2025.101084:
   precious-metal intraday momentum/reversal is state-dependent.
6. Hallberg Szabadvary et al. (2025), DOI 10.1016/j.mlwa.2025.100664:
   reject-option evaluation should report error/coverage trade-offs rather than force predictions.

## Fixed pre-origin path

Use only XAU/USD 15-minute bars from:
- 14:00 -> 17:00 Europe/Istanbul
- equivalent 11:00 -> 14:00 UTC

All 12 bars are complete by the 17:00 decision origin.

Target:
- 17:00 Europe/Istanbul open
- next eligible 09:00 Europe/Istanbul close
- direction UP/DOWN.

## Fixed representation families

### M0_SCALAR
Low-capacity path summary:
- 3h log return
- realized volatility
- up/down semivolatility balance
- maximum drawdown
- sign-change count
- 16:00-16:30 return
- 16:30-17:00 return

### M1_SIGNATURE
M0 plus:
- depth-2 lead-lag antisymmetric signature area, normalized by realized variance;
- time-price antisymmetric area, normalized by realized volatility.

### M2_FPCA
M0 plus:
- first two rolling functional-PCA scores of the normalized 12-point cumulative-return path.

PCA is fit only on matured historical paths available before each origin.

### M3_SIG_FPCA
M0 + both signature features + FPCA scores.

### M4_SIG_FPCA_MACRO
M3 plus origin-known macro state:
- same-day paired macro surprise released by 17:00;
- maximum absolute PIT-standardized surprise available by 17:00;
- upcoming FOMC before next eligible 09:00.

No target-window outcome or future macro result may enter.

## Estimator

All families:
- StandardScaler
- LogisticRegression L2
- C=1.0
- threshold 0.50
- no boosting / tree search / neural model
- minimum matured training rows = 120.

## Chronology

- 2022: warm-up/training history.
- 2023: discovery/selection only.
- 2024: confirmation only.
- 2025: retrospective frozen transport only.

2023/2024 predictions must be expanding and causal.
2025 must use one frozen fit trained only through 2024.

## Model selection

Choose exactly one family using 2023 only:
1. highest Balanced Accuracy;
2. tie-break lower Brier;
3. tie-break lower feature count.

The selected family is confirmed only if in 2024:
- BA > 50%;
- both UP and DOWN recall >= 35%;
- BA is not more than 2.0 pp below M0 on the same year.

If confirmation fails, PSF is not promoted.

## Selective layer

Only after family selection, choose a confidence reject threshold on 2023 from the fixed set:
- |p-0.5| >= {0.00, 0.05, 0.10, 0.15}

Eligibility:
- coverage >= 30%;
- active N >= 60;
- predicted-UP rate between 10% and 90%.

Choose highest 2023 BA, tie-break coverage.

The threshold is confirmed only if 2024:
- BA > full-coverage selected-family BA;
- active N >= 60;
- both class recalls >= 35%.

2025 may not alter family or threshold.

## Required comparisons

Report for 2023, 2024, 2025:
- N / coverage
- Accuracy / Balanced Accuracy
- UP / DOWN recall
- Brier / Log Loss
- confusion matrix
- risk-coverage selected result

On common 2025 rows compare:
- PSF selected full coverage
- PSF selective policy
- PAIR
- RFR-NOMACRO where active.

Do not call PSF a production model unless 2024 confirms and 2025 transport is directionally coherent.
