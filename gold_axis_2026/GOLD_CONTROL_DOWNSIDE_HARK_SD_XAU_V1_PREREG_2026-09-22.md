# GOLD CONTROL — DOWNSIDE HARK-SD V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `DOWNSIDE_HARK_SD_XAU_V1_RESEARCH`  
**Parent:** `DOWNSIDE_RAW_VS_SQRT_HAR_DR_MULTIORIGIN_V1_RESEARCH`  
**Immediate diagnostic precursor:** `DOWNSIDE_ME_SQRT_HAR_DR_XAU_V1_RESEARCH`  
**Manifest update:** FORBIDDEN IN THIS EXPERIMENT; user requested results first  
**Runtime / production authority:** NONE

## 1. Research question

Does treating downside semideviation as a noisy observation of a latent downside-risk state improve one-day-ahead downside-risk forecasting, and is any improvement specifically attributable to **time-varying quarticity-informed measurement uncertainty** rather than merely using a Kalman filter?

This is a cross-disciplinary state-estimation transfer implemented in a finance-authority form close to HARK.

## 2. Method authority and adaptation boundary

Method authority:
- Buccheri & Corsi (2021), HARK/SHARK: latent realized volatility in a 22-state HAR representation estimated by Kalman filter with time-varying measurement-error variance informed by realized quarticity;
- realized semivariance asymptotics: Barndorff-Nielsen, Kinnebrock & Shephard;
- project downside-risk representation: `SD_t=sqrt(DR_t)`.

This experiment is **not** claimed as an exact HARK replication. The adaptation changes:
- total realized variance -> downside realized semivariance;
- variance level -> downside semideviation;
- measurement variance -> downside semideviation delta-method variance proxy.

No time-varying HAR coefficients, score-driven dynamics, macro variables, regime labels, jumps, direction labels or nonlinear learners are permitted in V1.

## 3. Data contract

Source: `public.xau_intraday_research_cache_5m`.

- America/New_York;
- weekdays only;
- retain date if >=240 five-minute closes;
- intraday returns are consecutive within-date log-close returns only;
- no overnight/cross-date return enters realized measures.

For retained day t with M_t intraday returns:

`DR_t = sum_i r_(t,i)^2 I(r_(t,i)<0)`

`SD_t = sqrt(DR_t)`

`RQminus_t = (2*M_t/3) * sum_i r_(t,i)^4 I(r_(t,i)<0)`

Frozen semideviation measurement-error variance proxy:

`h_t = 5 * RQminus_t / (16 * M_t * DR_t)`

which equals `ME_SD_t^2` from the prior ME-SQRT preregistration.

Days with `DR_t<=0` or `RQminus_t<=0` are invalid; no epsilon rescue.

## 4. State-space model

Observation equation:

`y_t = SD_t = Z a_t + eps_t`

where:
- `a_t = [x_t, x_(t-1), ..., x_(t-21)]'` is a 22-dimensional latent downside-semideviation state;
- `Z=[1,0,...,0]`;
- `eps_t ~ N(0,h_t)` for the time-varying model.

Latent HAR transition:

`x_(t+1) = b0 + bd*x_t + bw*mean(x_t,...,x_(t-4)) + bm*mean(x_t,...,x_(t-21)) + eta_(t+1)`

`eta_(t+1) ~ N(0,q)`.

Equivalent first row of transition matrix T:
- lag 0 coefficient: `bd + bw/5 + bm/22`;
- lags 1..4: `bw/5 + bm/22`;
- lags 5..21: `bm/22`.

Rows 2..22 shift the latent state by one day.

Process covariance Q is zero except `Q[0,0]=q`.

Final forecast:
- one-step latent forecast `xhat_(t+1|t)`;
- DR forecast = `xhat_(t+1|t)^2`;
- any nonpositive one-step latent forecast is a domain failure and is not repaired.

## 5. Frozen model set

### A. SQRT_HAR_DR
Existing OLS benchmark:
- target `SD_(t+1)`;
- predictors `SD_t`, mean5(SD), mean22(SD);
- final DR forecast = squared SD forecast.

### B. HARK_SD_CONST
Same 22-state latent HAR-Kalman model, but observation variance is frozen at each annual origin:

`h_const = median(h_t)`

over formation dates only.

This isolates the effect of latent-state filtering without time-varying measurement confidence.

### C. HARK_SD_TV
Primary candidate.

Observation variance uses the causal day-specific `h_t`.

This isolates the incremental value of quarticity-informed time-varying measurement uncertainty.

## 6. Parameter estimation

For each annual origin and each HARK model:
- parameters `b0,bd,bw,bm,q` estimated only on formation dates;
- standard Gaussian Kalman prediction-error likelihood;
- data scaled by formation median SD for numerical conditioning; saved/reported coefficients converted to original SD scale;
- deterministic single start:
  - `b0,bd,bw,bm` from OLS SQRT-HAR on the identical formation chronology;
  - `q` from variance of OLS SD residuals;
- optimizer: SciPy L-BFGS-B;
- max iterations 3000;
- tolerance `1e-10`;
- broad frozen bounds on scaled parameters:
  - intercept [-5,5];
  - HAR coefficients each [-3,3];
  - log(q) [-20,5];
- optimizer failure is a model failure, not a trigger for alternate starts.

Initialization at the first usable 22-state origin:
- state vector = the first 22 observed scaled SD values in reverse chronological order;
- state covariance diagonal = corresponding observation variances in the same order;
- no smoother is used;
- only forward filtered states are permitted.

## 7. Chronology and OOS filtering

Annual expanding-origin parameter estimation:
- 2022 parameters use data through 2021-12-31;
- 2023 through 2022-12-31;
- 2024 through 2023-12-31;
- 2025 through 2024-12-31;
- 2026 YTD through 2025-12-31.

Parameters are frozen once per target year.

Inside each target year:
- the Kalman state is carried forward causally;
- day t observation may update the latent state only after day t is complete;
- the resulting one-step forecast is for the next retained trading day;
- no target-day observation enters its own forecast.

Evidence classification:
- this identity was designed after inspection of historical Gold results;
- 2022-2024 are retrospective development/falsification evidence;
- 2025/2026 are retrospective stress evidence;
- none is pristine confirmatory evidence.

## 8. Shared evaluation

Same annual formation-only thresholds as the parent:
- historical mean DR;
- high-risk nearest-rank Q80;
- extreme negative next-day return nearest-rank Q05.

Mandatory metrics:
- MSE, MAE, DR-QLIKE, OOS R2;
- correlation;
- forecast mean / realized mean;
- calibration intercept/slope and absolute slope error;
- high-risk AUC, precision, recall, F1, coverage;
- alert-conditional DOWN and extreme-negative-return rates;
- domain failures;
- estimated `q`;
- average/min/max Kalman gain for current observation;
- average formation and OOS observation variance `h_t`.

## 9. Frozen retrospective feasibility gate

`HARK_SD_TV = RETROSPECTIVE_LATENT_STATE_SUPPORTED` only if all hold on 2022-2024:

1. HARK_SD_TV MSE < SQRT_HAR_DR in at least 2 of 3 years;
2. pooled 2022-2024 HARK_SD_TV MSE < pooled SQRT MSE;
3. pooled HARK_SD_TV DR-QLIKE <= pooled SQRT DR-QLIKE;
4. HARK_SD_TV absolute calibration-slope error improves versus SQRT in at least 2 of 3 years;
5. HARK_SD_TV AUC is never more than 0.02 below SQRT in any year;
6. no nonpositive HARK_SD_TV latent forecast;
7. HARK_SD_TV pooled MSE <= HARK_SD_CONST pooled MSE;
8. HARK_SD_TV pooled QLIKE <= HARK_SD_CONST pooled QLIKE.

Conditions 7-8 are essential: a passing result must show that **time-varying measurement confidence** adds value beyond generic Kalman smoothing.

No result-dependent retuning, alternate initialization, multistart or parameter-grid rescue is permitted under V1.
