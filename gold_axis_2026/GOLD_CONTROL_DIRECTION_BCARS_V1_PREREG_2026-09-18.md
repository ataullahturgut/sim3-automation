# GOLD CONTROL — DIRECTION_BCARS_V1_RESEARCH PREREGISTRATION

**Date:** 2026-09-18  
**Identity:** `DIRECTION_BCARS_V1_RESEARCH`  
**Status:** `FROZEN_BEFORE_BCARS_V1_2025_REPLAY`  
**Evidence class:** historical research replay only; no runtime or production authority

## 1. Objective

Evaluate the benchmark Beta Conditional Autoregressive Shape model B-CARS(1,1) from Xie, Sun & Fan (2023) as a next-week Gold direction challenger.

Primary literature authority:
Xie, H., Sun, Y. & Fan, P. (2023), *Return direction forecasting: a conditional autoregressive shape model with beta density*, Financial Innovation 9:82, DOI `10.1186/s40854-023-00489-z`.

The source paper is monthly S&P 500. This V1 is explicitly a **Gold weekly adaptation**, not a claim of exact frequency replication.

## 2. Frozen source and weekly interval semantics

Provider: Twelve Data  
Symbol: `XAU/USD`  
Provider interval: `1h`  
Requested timezone: `America/New_York`

Research OHLC retrieval span:
`2022-02-21 00:00 America/New_York` through `2025-12-31 23:59:59 America/New_York`.

No production database write is authorized. The OHLC backfill is an immutable research artifact only.

Weekly close axis:
- Monday-start calendar week;
- candidate close bar = exact provider `16:00:00 America/New_York` 1h bar on Monday-Friday;
- weekly close = close field of the last actually observed eligible candidate bar in that week;
- no interpolation;
- no forward-fill;
- no provider substitution.

Weekly interval high for week t:
- let the selected provider timestamp for prior weekly close be `T_(t-1)`;
- let current selected weekly close timestamp be `T_t`;
- `H_t = max(high_j)` over validated provider 1h bars with `T_(t-1) < timestamp_j <= T_t`;
- thus the high is taken over the actual interval between consecutive weekly close anchors, not merely the maximum of hourly closes.

Source-paper high adjustment is preserved:
`H_t^a = max(H_t, C_(t-1))`.

## 3. Up-ratio decomposition

Use log prices:
`p_t = ln(C_t)`
and adjusted log high
`h_t = ln(H_t^a)`.

Define:
`u_t = h_t - p_(t-1)`
`d_t = h_t - p_t`
`R_t = u_t + d_t`
`ur_t = u_t / R_t`.

Identity audit:
`r_t = p_t-p_(t-1) = R_t*(2*ur_t-1)`.

Every weekly row must satisfy the identity to floating-point tolerance and `R_t>0`.

No boundary clipping is permitted in V1. If any modeled `ur_t` is exactly 0 or 1, V1 must fail closed and a separately governed boundary-treatment successor is required.

## 4. Frozen B-CARS(1,1) model

`ur_t ~ Beta(alpha_t, beta)`

`k_t = E(ur_t | Omega_t) = alpha_t/(alpha_t+beta)`

`k_t = omega + gamma*k_(t-1) + tau*ur_(t-1)`

with:
- `omega > 0`;
- `gamma >= 0`;
- `tau >= 0`;
- `omega + gamma + tau <= 1`;
- `beta > 0`.

Then:
`alpha_t = k_t*beta/(1-k_t)`.

Log likelihood:
`sum_t [lgamma(alpha_t+beta)-lgamma(alpha_t)-lgamma(beta) + (alpha_t-1)ln(ur_t) + (beta-1)ln(1-ur_t)]`.

## 5. Frozen initialization and numerical MLE contract

The source paper does not specify a software-level recursion initializer. V1 therefore freezes the following source-grounded Gold implementation choice before 2025 scoring:

For each estimation sample:
`k_1 = omega / (1-gamma-tau)`,
using the source paper's unconditional-mean identity. The constraint parameterization keeps the denominator positive.

Numerical parameterization:
- represent `omega, gamma, tau, slack` by a four-part softmax, with slack logit fixed at zero;
- therefore all components are positive and sum to one;
- `omega+gamma+tau = 1-slack < 1`;
- `beta = exp(log_beta)`.

Optimizer:
- deterministic L-BFGS-B;
- free logits bounded to [-12, 12];
- `log_beta` bounded to [-8, 8];
- fixed multi-start set, identical at every origin:
  1. weights (0.25,0.25,0.25,0.25), beta=1.0
  2. (0.10,0.70,0.10,0.10), beta=0.5
  3. (0.05,0.85,0.05,0.05), beta=1.0
  4. (0.10,0.20,0.60,0.10), beta=0.5
  5. (0.20,0.30,0.30,0.20), beta=2.0

Choose the converged solution with the highest in-sample log likelihood. If no start converges to a finite solution, that origin is `MODEL_FIT_BLOCKED` and is not silently substituted.

## 6. OOS chronology and estimation window

The source paper uses an extending-window out-of-sample procedure. V1 preserves that structure.

Initial estimation window:
exactly the first **52 valid weekly up-ratios**.

At each subsequent origin:
1. estimate B-CARS(1,1) using every up-ratio available through that origin;
2. forecast `k_(t+1)=omega+gamma*k_t+tau*ur_t`;
3. native direction forecast:
   - UP if `k_(t+1) > 0.5`;
   - DOWN otherwise;
4. advance one week and re-estimate on the expanded history.

The 52-week initial window is frozen to align the first direction evaluation with the existing weekly direction-research lane while preserving source-style expanding estimation.

Chronology labels:
- 2023: implementation/development audit;
- 2024: fixed pre-2025 validation;
- after the pre-2025 checkpoint is frozen, 2025 is replayed unchanged;
- the 19-event volatility overlay is applied only after the complete 2025 weekly forecast table is frozen.

No random split.

## 7. Native and derived outputs

Native B-CARS output:
`k_forecast = E(ur_(t+1)|Omega_t)`.

Native direction rule:
`k_forecast > 0.5 => UP`, otherwise DOWN.

Optional research diagnostic only:
`P_ext(UP)=1-F_Beta(0.5; alpha_forecast,beta)`.

This Beta-tail probability is a Gold-derived probabilistic extension for calibration diagnostics; it must not be misrepresented as the source paper's native direction rule.

## 8. Required metrics

Primary direction diagnostics:
- accuracy;
- balanced accuracy;
- UP sensitivity;
- DOWN sensitivity;
- forecast UP/DOWN counts;
- confusion counts;
- always-UP baseline;
- previous-week-sign baseline.

Continuous-target diagnostics:
- MSE of `k_forecast` versus realized `ur`;
- historical-mean up-ratio forecast MSE;
- source-style `R2_oos = 1 - MSE_BCARS_sum / MSE_historical_mean_sum`.

Derived-probability diagnostics, clearly labeled extension:
- Brier;
- log loss;
- probability range/calibration.

## 9. Locks

Forbidden under V1:
- tuning model order from 2025;
- changing weekly frequency after 2025 scoring;
- changing the initial 52-week window after 2025 scoring;
- changing optimizer/multistart/initialization after 2025 scoring;
- clipping boundary up-ratios after seeing outcomes;
- adding exogenous variables;
- adding FAST/GVZ/BOCPD/Macro/Emergency inputs;
- adding NO_SIGNAL;
- source/provider substitution;
- event-conditioned origin selection;
- post-2025 rescue tuning under the same identity.

Any alternative frequency, B-CARS(1,2)/(2,1), boundary treatment, exogenous-input version, threshold shift or regime-conditioned extension requires a separately named successor.
