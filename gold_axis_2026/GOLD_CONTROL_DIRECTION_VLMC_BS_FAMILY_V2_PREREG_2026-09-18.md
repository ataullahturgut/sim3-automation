# GOLD CONTROL — DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH PREREGISTRATION

**Date:** 2026-09-18  
**Identity:** `DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH`  
**Status:** `FROZEN_BEFORE_CORRECTED_2025_REPLAY`  
**Supersedes for family-level interpretation:** `DIRECTION_VLMC_BS_V1_RESEARCH`  
**Evidence class:** historical research replay only; no runtime or production authority

## 1. Purpose

Re-evaluate the second direction-method family using a source-faithful rolling VLMC-with-bootstrap implementation based on Liu, Papailias & Quinn (2021) and the reference R package/methodology of Mächler & Bühlmann (2004).

Primary authorities:
- Liu, Papailias & Quinn (2021), *Direction-of-change forecasting in commodity futures markets*, International Review of Financial Analysis 74, 101677.
- Mächler & Bühlmann (2004), *Variable Length Markov Chains: Methodology, Computing, and Software*, JCGS 13(2), 435-455.
- CRAN package `VLMC`, reference implementation by Martin Mächler.

## 2. Corrected weekly input construction

Source series:
`XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`.

The commodity paper states that daily percentage returns are calculated from closing prices and aggregated into weekly returns.

Therefore V2 uses:
- daily simple return `r_d=C_d/C_(d-1)-1`;
- Monday-start calendar week;
- weekly return `r_w=sum(r_d)`;
- binary sign `x_w=1[r_w>0]`, else 0.

No interpolation, forward-fill or provider substitution.

The weekly-sign research surface is materialized once from the governed Neon series and used unchanged by the R reference implementation.

## 3. Source-feasible rolling family

The paper evaluates Markov-chain models at multiple in-sample windows and reports that rolling Markov-chain approaches outperform recursive variants; individual-commodity tables use rolling VLMC/VLMC-BS.

With the retained same-source history beginning in March 2022, V2 evaluates exactly:
- `VLMC_BS_ROLLING_26`
- `VLMC_BS_ROLLING_52`
- `VLMC_BS_ROLLING_104`.

Longer windows are not pre-2025 evaluable on the same source and are not created by provider splicing.

No 2025 outcome may select among 26/52/104.

## 4. Exact reference implementation

Execution authority:
- R reference implementation;
- R package `VLMC` pinned to version 1.4-4;
- `threshold.gen=2` (package/reference default).

For each real forecast origin and each rolling window k:

1. take exactly the prior k weekly binary symbols;
2. fit the initial large model:
   `vlmc(train, cutoff.prune=0.30, threshold.gen=2)`;
3. reset R RNG with `set.seed(1521)` as a reproducibility lock for that origin;
4. generate `B=1000` independent bootstrap sequences of length `k+1` using
   `simulate(initial_model, nsim=k+1, n.start=10000, integer.return=TRUE)`;
5. for every `K=0.40,0.42,...,2.50`, fit
   `vlmc(x_star[1:k], cutoff.prune=K, threshold.gen=2)`;
6. obtain the one-step bootstrap class with the package reference path
   `predict(..., type="class")`, exactly as in the Mächler-Bühlmann bootstrap example;
7. accumulate zero-one classification matches/loss;
8. select the K with minimum bootstrap mean zero-one loss. Exact K-loss ties choose the first/smallest K on the ascending grid, matching R `which.max`/ordered-grid behavior;
9. refit the real rolling window using selected `K_star`;
10. obtain one-step next-symbol probabilities from `predict(..., type="probs")`;
11. retain `P(UP)`;
12. final Gold/source trading-direction rule: UP iff `P(UP)>=0.5`, else DOWN.

Important distinction:
- bootstrap classifier tie behavior is whatever the pinned R `VLMC::predict(type="class")` returns;
- final Gold direction threshold follows the commodity paper's `P>=0.5 => UP` trading rule.

No custom Python tree is authoritative in V2.

## 5. Bootstrap contract

- `K0=0.30`;
- `K grid=0.40..2.50` by 0.02;
- `B=1000`;
- `n.start=10000`;
- R `set.seed(1521)` independently at every real forecast origin;
- no smoothing;
- no minimum-support rescue;
- no NO_SIGNAL band;
- no context augmentation;
- no FAST/GVZ/BOCPD/Macro/Emergency inputs.

The seed reset is a Gold reproducibility lock. The commodity paper does not claim seed 1521; the Mächler-Bühlmann worked bootstrap example uses it.

## 6. Chronology

- 2022: history/warm-up;
- 2023: development/audit where window history permits;
- 2024: fixed pre-2025 validation;
- all pre-2025 results for 26/52/104 must be frozen before corrected 2025 replay;
- 2025: locked historical replay of all three unchanged variants;
- 19-event overlay only after complete 2025 forecast tables are frozen.

No random split.

## 7. Required metrics

For each variant:
- accuracy/success rate;
- balanced accuracy;
- Brier;
- log loss;
- actual and forecast class counts;
- UP sensitivity;
- DOWN sensitivity;
- TP/TN/FP/FN;
- always-UP baseline;
- previous-sign baseline;
- probability range;
- selected K summary.

Primary fair pre-2025 family comparison uses common 2024 support on which all 26/52/104 rolling variants are simultaneously eligible.

## 8. V1 status

`DIRECTION_VLMC_BS_V1_RESEARCH` remains audit-only. It is not authoritative for family-level conclusions because it:
- used weekly-close log-return signs instead of source-text weekly aggregation of daily percentage returns;
- used a custom Python implementation rather than the pinned reference R package;
- tested only k=52;
- used a custom bootstrap classifier implementation.

V2 supersedes V1 only for scientific interpretation of the VLMC-BS family; historical V1 artifacts remain unchanged for auditability.

## 9. Locks

Forbidden under V2:
- selecting k using 2025;
- changing K0, K grid, B, burn-in, seed, package path or final threshold after 2025;
- changing weekly-return construction after 2025;
- provider splicing for longer windows;
- adding external/context features;
- probability smoothing or post-hoc calibration;
- event-conditioned tuning;
- post-2025 rescue under the same identity.
