# GOLD CONTROL — DIRECTION_BCT_CTW_V1_RESEARCH PREREGISTRATION

**Date:** 2026-09-18  
**Identity:** `DIRECTION_BCT_CTW_V1_RESEARCH`  
**Status:** `FROZEN_BEFORE_BCT_V1_2025_REPLAY`  
**Evidence class:** historical research replay only; no runtime or production authority

## 1. Objective

Evaluate an exact Bayesian Context Tree / Context Tree Weighting (BCT/CTW) next-week Gold direction model using the same weekly binary return-sign target as RSM-52 and VLMC-BS-52, without selecting BCT hyperparameters from 2025 outcomes.

Primary authority:
Kontoyiannis, Mertzanis, Panotopoulou, Papageorgiou & Skoularidou (2022), *Journal of the Royal Statistical Society: Series B*, 84(4), 1287-1322, DOI `10.1111/rssb.12511`.

## 2. Frozen data and target

Series:
`XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`.

Weekly construction is identical to the frozen RSM/VLMC direction lane:
- Monday-Friday New York-local observations only;
- Monday-start calendar weeks;
- weekly close = last actually observed governed weekday in the week;
- no interpolation;
- no forward-fill;
- no alternate-provider substitution.

Weekly return:
`r_w = ln(C_w/C_(w-1))`.

Binary state:
`x_w = 1[r_w > 0]`; otherwise `0`.

Target:
next represented calendar-week return direction.

Rolling information window:
exactly 52 prior weekly return signs.

## 3. Frozen Bayesian model

Alphabet:
`A={0,1}`, so `m=2`.

Maximum context depth:
`D=10`.

Tree-prior parameter:
`beta=0.5`.

For binary data this equals the paper's practical default
`beta ≈ 1 - 2^(-m+1)`
and is also the classical binary CTW special case.

For every leaf/context s:
`theta_s ~ Dirichlet(1/2,1/2)`
(Jeffreys prior).

For count vector `a_s=(a_s(0),a_s(1))`, the integrated local evidence is the Dirichlet-multinomial / Krichevsky-Trofimov marginal

`P_e(a_s) = Gamma(1)/Gamma(M_s+1) * product_j Gamma(a_s(j)+1/2)/Gamma(1/2)`

with `M_s=a_s(0)+a_s(1)`.

CTW recursion:
- at depth D: `P_w,s=P_e,s`;
- at depth <D:
  `P_w,s = beta*P_e,s + (1-beta)*P_w,s0*P_w,s1`.

The root value is the exact prior predictive likelihood averaged over all proper context-tree models of depth at most D and their transition parameters.

## 4. Window conditioning and next-week probability

Each 52-symbol rolling window is partitioned exactly as required by the BCT/CTW likelihood:
- first D=10 signs = fixed initial context;
- remaining 42 signs = observations scored by CTW.

For candidate next symbol `a in {0,1}`, append a to the 52-symbol window and recompute the exact prior predictive likelihood with the same first 10 signs as initial context.

Define:

`q_a = P_D^*(x_11,...,x_52,a | x_1,...,x_10)`.

The native next-week probability is

`P(UP) = q_1 / (q_0 + q_1)`.

This normalized two-candidate form is algebraically equivalent to the sequential predictive ratio and is used for numerical stability/auditability.

Direction rule:
- UP if `P(UP)>=0.5`;
- DOWN otherwise.

There is no NO_SIGNAL band in V1.

## 5. Why D=10 is frozen

The BCT paper uses D=10 extensively in its model-selection experiments and recommends `beta≈1-2^(-m+1)` in practice. For binary data, beta is therefore 0.5.

D=10 is adopted here as a source-grounded V1 maximum-depth choice before the BCT 2025 replay. It is not selected by searching Gold 2025 accuracy and will not be changed under this identity after results are inspected.

No alternative D grid is evaluated under V1.

## 6. Chronology

- 2022-03 onward: warm-up/history;
- 2023: implementation/development audit after 52-sign warm-up;
- 2024: fixed pre-2025 validation;
- 2025: historical locked replay under the frozen BCT specification;
- frozen 19-event volatility table: overlay only after the complete 2025 weekly forecast table is frozen.

Important evidence label:
2025 has already been researcher-visible at the broader Gold Control programme level. It is therefore not represented as a pristine blind holdout. The protection here is narrower: no BCT V1 hyperparameter, threshold, depth, prior or feature choice may be selected from its outcomes.

No random split.

## 7. Required outputs and metrics

Every origin must retain:
- origin week and close date;
- target week;
- log prior predictive likelihood for the 52-symbol training window;
- candidate log likelihood for appended DOWN;
- candidate log likelihood for appended UP;
- normalized P(UP);
- forecast direction;
- realized next-week direction only in evaluation output.

Metrics:
- accuracy;
- balanced accuracy;
- Brier score;
- log loss;
- UP sensitivity;
- DOWN sensitivity;
- forecast class counts;
- confusion counts;
- calibration summary;
- always-UP baseline;
- previous-week-sign baseline;
- comparison with frozen RSM-52 and VLMC-BS-52.

## 8. Locks

Forbidden under V1:
- choosing D or beta from 2025;
- tuning a probability threshold on 2025;
- changing the 52-week window after outcome inspection;
- switching source/provider;
- adding FAST/GVZ/BOCPD/Macro/Emergency inputs;
- adding NO_SIGNAL after seeing results;
- random split;
- event-conditioned origin selection;
- post-2025 rescue tuning under the same identity.

Any later BCT depth study, alternate prior, expanded/longer training history, richer alphabet or Gold Control context augmentation requires a separately named successor/change-control step.
