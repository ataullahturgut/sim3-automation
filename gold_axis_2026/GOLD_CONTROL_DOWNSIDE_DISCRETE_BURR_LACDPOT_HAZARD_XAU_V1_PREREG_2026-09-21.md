# GOLD CONTROL — DISCRETE-BURR LACD-POT EXTREME-DOWN HAZARD V1 PREREGISTRATION

**Date:** 2026-09-21  
**Identity:** `DOWNSIDE_DISCRETE_BURR_LACDPOT_HAZARD_XAU_V1_RESEARCH`  
**Primary authority:** Bień-Barkowska (2024), *Forecasting extreme negative returns in gold and silver: A discrete-duration approach to POT models*, DOI 10.1002/asmb.2759.  
**Mathematical reconstruction authority:** Bień-Barkowska (2020), *Forecasting Extreme Returns in Financial Markets: A Discrete Duration Framework*, DOI 10.12693/APhysPolA.138.48.  
**Manifest update:** DEFERRED UNTIL USER REVIEWS RESULTS  
**Runtime authority:** NONE  
**Production writes:** NONE

## 1. Scientific target

Forecast the **one-trading-day-ahead probability of an extreme negative Gold return**. This is not a generic UP/DOWN classifier.

## 2. Data contract

Primary daily Gold source:
`public.usable_observations`, series `XAU_STAKTRAKR_RESEARCH_DAILY_R1`.

Authority boundary:
- current registry status is research-only / not PIT;
- values are historical market-price observations, used only for retrospective research;
- this V1 does not claim canonical NY17 equivalence or source-faithful LBMA replication.

Daily loss:
`L_t = -log(P_t/P_(t-1))`.

Formation sample:
- earliest available valid daily observation through 2023-12-31.

Validation/challenge:
- 2024 fixed validation;
- 2025 locked retrospective challenge.

## 3. Frozen extreme-event definition

Following the source POT convention, an extreme loss event occurs when:
`L_t > u`.

Threshold:
- `u` = empirical 95th percentile of formation-sample negated log returns;
- threshold is frozen before 2024 and never recomputed using 2024/2025.

Event excess magnitude:
`e_i = y_i-u > 0`.

Inter-event duration:
`x_i = t_i-t_(i-1)` in retained trading-day index units.

## 4. Frozen discrete-duration hazard model

Primary distribution: right-shifted **discrete Burr** duration model.

LACD state:
`log(Psi_i)=omega + beta*log(Psi_(i-1)) + alpha*log(x_(i-1)) + zeta*log(e_(i-1))`.

Continuous Burr survival:
`S_B(x)=(1 + eta*(x/Phi_i)^kappa)^(-1/eta)`.

Mean-normalizing scale reconstruction:
`Phi_i = Psi_i * eta^(1/kappa) * Gamma(1/eta) / [Gamma(1+1/kappa)*Gamma(1/eta-1/kappa)]`.

Constraints:
- `kappa>0`;
- `eta>0`;
- `eta<kappa`;
- `|beta|<0.995`;
- no sign constraint on alpha or zeta.

Right-shifted discrete Burr probability:
`P(X_i=x)=S_B(x-1)-S_B(x)`, x=1,2,...

One-day hazard after the last event:
`h(x)=1-S_B(x)/S_B(x-1)`.

The dynamic state for the next duration is updated only after a completed extreme event.

Initial state:
- `Psi_1` fixed to mean formation inter-event duration as an explicit reconstruction choice.

Estimation:
- maximum likelihood on completed formation event durations only;
- deterministic multi-start L-BFGS-B / unconstrained transformed parameters;
- no 2024/2025 fitting or threshold tuning.

## 5. Baselines

- constant event probability = formation extreme-event rate;
- geometric duration hazard using the same constant event probability.

## 6. Binary alert reconstruction

The source-native output is probability/hazard. For event-detection diagnostics only:
- alert threshold = 95th percentile of fitted formation daily hazard probabilities;
- frozen before 2024;
- no validation/challenge threshold search.

## 7. Mandatory metrics

For 2024 and 2025:
- extreme-event count/rate;
- mean predicted hazard;
- Brier score;
- log loss;
- Brier skill versus constant-rate baseline;
- ROC AUC and average precision where defined;
- alert coverage;
- extreme-event recall;
- alert precision;
- false-alert rate;
- event-day mean/median hazard versus non-event days;
- top-decile hazard event concentration.

Research-interest gate on 2024:
- Brier skill > 0;
- ROC AUC >= 0.55;
- alert event recall >= 0.15;
- alert precision strictly above unconditional event rate.

2025 cannot rescue a failed 2024 gate.

If and only if the 2024 gate passes, 2025 transport is supported when the unchanged model also has:
- Brier skill > 0;
- ROC AUC >= 0.50;
- alert recall >= 0.10;
- alert precision strictly above the 2025 unconditional extreme-event rate.

## 8. Interpretation lock

This experiment evaluates **extreme negative-event timing**, not ordinary DOWN-day direction.

Possible conclusions:
- `PRE2025_EXTREME_DOWN_HAZARD_SUPPORTED`
- `PRE2025_EXTREME_DOWN_HAZARD_NOT_SUPPORTED`
- `2025_HAZARD_TRANSPORT_SUPPORTED`
- `2025_HAZARD_TRANSPORT_NOT_SUPPORTED`.

No manifest change occurs in the workflow.
