# GOLD CONTROL — ME-SQRT-HAR-DR V1 PREREGISTRATION

**Date:** 2026-09-22
**Identity:** `DOWNSIDE_ME_SQRT_HAR_DR_XAU_V1_RESEARCH`
**Parent:** `DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_RESEARCH`
**Manifest update:** FORBIDDEN IN THIS EXPERIMENT; user requested results first
**Runtime / production authority:** NONE

## 1. Scientific question

Can a HAR downside-risk model improve when it explicitly accounts for the time-varying measurement error of realized downside semivariance?

This is a one-mechanism extension. No macro, trend, regime, jump, classifier, threshold search, nonlinear learner or post-result tuning is permitted.

## 2. Method authority and adaptation boundary

Authority:
- realized semivariance theory: Barndorff-Nielsen, Kinnebrock & Shephard;
- realized-measure measurement-error/HARQ mechanism: Bollerslev, Patton & Quaedvlieg (2016), where daily HAR persistence varies with realized-quarticity-based measurement-error magnitude;
- transformed realized-volatility benchmark: Taylor (2017), including square-root and quartic-root representations and 5-minute downside semivariance among evaluated realized measures.

This experiment is **not** claimed as an exact published model replication. The project adaptation is the application of the HARQ measurement-error logic to the downside semivariance target on a semideviation scale.

## 3. Data contract

Source: `public.xau_intraday_research_cache_5m`.

- timezone: America/New_York;
- weekdays only;
- retain a date with >=240 five-minute closes;
- intraday returns are consecutive within-date log-close returns only;
- no overnight/cross-date return enters realized measures.

For retained day t with M_t nonmissing intraday returns:

`DR_t = sum_i r_(t,i)^2 I(r_(t,i)<0)`

`SD_t = sqrt(DR_t)`

Downside integrated-quarticity proxy:

`RQminus_t = (2*M_t/3) * sum_i r_(t,i)^4 I(r_(t,i)<0)`.

The factor 2 corrects the one-sided fourth-moment expectation under the continuous symmetric reference case.

Using the continuous semivariance asymptotic variance `Var(DR_t error) proportional to (5/(4*M_t))*IQ_t`, the delta-method semideviation measurement-error proxy is frozen as:

`ME_SD_t = sqrt( 5 * RQminus_t / (16 * M_t * DR_t) )`.

If DR_t<=0 the day is invalid. No epsilon-based feature rescue is allowed.

## 4. Frozen models

### RAW_HAR_DR
OLS target DR(t+1), predictors:
- DR_t
- mean5(DR)
- mean22(DR)

### SQRT_HAR_DR
OLS target SD(t+1), predictors:
- SD_t
- mean5(SD)
- mean22(SD)

Final DR forecast = squared SD forecast.

### QUARTIC_HAR_DR_NAIVE
Let Q_t = DR_t^(1/4).

OLS target Q(t+1), predictors:
- Q_t
- mean5(Q)
- mean22(Q)

Final DR forecast = fourth power of the positive transformed forecast.

This is a fixed quartic-root representation benchmark with naive inverse transformation. It is not claimed to reproduce Taylor's full Jensen-adjusted forecast conversion.

### ME_SQRT_HAR_DR
OLS target SD(t+1):

`SD_(t+1) = b0 + (bd + bME*ME_SD_t)*SD_t + bw*mean5(SD) + bm*mean22(SD) + error`.

Equivalent design columns:
- intercept
- SD_t
- mean5(SD)
- mean22(SD)
- `ME_SD_t * SD_t`.

Only one new coefficient, bME.

The theoretical HARQ-style attenuation expectation is bME<0, but the sign is NOT constrained.

Final DR forecast = squared positive SD forecast.

## 5. Chronology

Annual expanding-origin evaluation:
- 2022 model uses targets completed through 2021-12-31;
- 2023 uses through 2022-12-31;
- 2024 uses through 2023-12-31;
- 2025 uses through 2024-12-31;
- 2026 YTD uses through 2025-12-31.

Refit exactly once per year. No target-year outcome enters fitting.

Important evidence classification:
- the measurement-error hypothesis was generated after retrospective inspection of 2022-2026 behavior;
- therefore NONE of these years is pristine confirmatory evidence for this new identity;
- 2022-2024 are retrospective development/falsification evidence;
- 2025/2026 are retrospective stress evidence only.

## 6. Shared thresholds

At each annual origin, formation-only:
- historical mean DR benchmark = mean formation target DR;
- high-risk threshold = nearest-rank Q80 of formation target DR;
- extreme-negative-return threshold = nearest-rank Q05 of formation target close return.

Same thresholds for all models.

## 7. Mandatory outputs

Per year and pooled 2022-2024:
- MSE, MAE, DR-QLIKE, OOS R2 vs frozen historical mean;
- persistence MSE/QLIKE;
- correlation;
- forecast mean / realized mean;
- Mincer-Zarnowitz intercept/slope and absolute slope error;
- high-risk ROC AUC, precision, recall, F1, coverage;
- alert-conditional DOWN rate;
- alert-conditional extreme-negative-return rate;
- transformed forecast domain failures;
- ME-SQRT bME coefficient.

Paired RAW/SQRT/QUARTIC/ME losses must be retained for HAC diagnostics.

## 8. Frozen retrospective feasibility gate

This gate is for deciding whether ME-SQRT merits further prospective research; it is NOT a promotion gate.

ME-SQRT is `RETROSPECTIVE_MECHANISM_SUPPORTED` only if all hold over 2022-2024:
1. ME-SQRT MSE < SQRT-HAR-DR in at least 2 of 3 years;
2. pooled ME-SQRT MSE < pooled SQRT MSE;
3. pooled ME-SQRT DR-QLIKE <= pooled SQRT DR-QLIKE;
4. absolute calibration-slope error improves versus SQRT in at least 2 of 3 years;
5. high-risk AUC is never more than 0.02 below SQRT in any year;
6. no nonpositive transformed OOS forecast;
7. fitted bME is negative in at least 2 of 3 annual origins.

QUARTIC-HAR is a benchmark, not a selectable rescue. Its results must be reported even if it outperforms ME-SQRT.

No result-dependent retuning is permitted under V1.
