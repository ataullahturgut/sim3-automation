# GOLD CONTROL — DIRECTION_VLMC_BS_V1_RESEARCH PREREGISTRATION

**Date:** 2026-09-18  
**Identity:** `DIRECTION_VLMC_BS_V1_RESEARCH`  
**Status:** `FROZEN_BEFORE_2025_PRICE_RETURN_TEST`  
**Evidence class:** historical research replay only; no runtime or production authority

## 1. Objective

Replicate the bootstrapped Variable-Length Markov Chain (VLMC-BS) direction-of-change method used by Liu, Papailias & Quinn (2021) on Gold Control XAU/USD weekly return-sign data, preserving point-in-time chronology and prohibiting any 2025-driven model choice.

Primary literature anchors:
- Liu, Papailias & Quinn (2021), *International Review of Financial Analysis*, 74, 101677, DOI 10.1016/j.irfa.2021.101677.
- Mächler & Bühlmann (2004), *Journal of Computational and Graphical Statistics*, 13, 435-455.
- Bühlmann & Wyner (1999), *Annals of Statistics*, 27, 480-513.

## 2. Frozen data and target

Series: `XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`.

Weekly construction is identical to the frozen RSM V1 research lane:
- Monday-Friday New York-local observations only;
- calendar week begins Monday;
- weekly close = last actually observed governed weekday in that week;
- no interpolation;
- no forward-fill;
- no alternate-provider substitution.

Weekly return:
`r_w = ln(C_w / C_(w-1))`.

Binary symbol:
`x_w = 1[r_w > 0]`; otherwise `0`.

Target: next represented calendar-week return direction.

Rolling information window: exactly 52 prior weekly symbols.

Direction rule for the final forecast:
- UP if fitted `P(UP) >= 0.5`;
- DOWN otherwise.

## 3. Classical context algorithm

For a candidate context `w`, let `N(w)` denote the number of occurrences in the 52-symbol sequence. The maximal tree is the largest context tree whose terminal contexts have been observed at least twice.

For transition symbol `a in {0,1}`, estimate

`P_hat(a|w) = N(w followed by a) / N_minus1(w)`,

where the final occurrence is excluded from the denominator when it has no following symbol.

For a terminal context `wu` and its pruned parent `w`, use the context-algorithm divergence

`Delta(wu) = N(wu) * sum_a P_hat(a|wu) * log(P_hat(a|wu)/P_hat(a|w))`.

Terms with `P_hat(a|wu)=0` contribute zero.

Prune `wu` to `w` when `Delta(wu) < K`. Repeat until no additional pruning is possible.

For prediction, use the longest active context matched by the observed past; if no child branch is active, back off to the corresponding shorter active context/root.

## 4. Frozen bootstrap tuning

Initial large-tree cutoff:
`K0 = 0.30`.

Candidate cutoffs:
`K = 0.40, 0.42, ..., 2.50`.

Bootstrap replications:
`B = 1000`.

Simulation burn-in:
`n_start = 10000`.

Reproducibility seed:
`seed = 1521`.

Rationale:
- `K0=0.3` and the `0.4..2.5` grid with `0.02` spacing are taken from Liu, Papailias & Quinn (2021).
- `B=1000` and `n_start=10000` follow the explicit Mächler-Bühlmann bootstrap example.
- seed 1521 is used as a reproducibility control consistent with that tutorial example; the commodity paper does not claim this seed.

At each real forecast origin:
1. fit the large VLMC on the 52 observed symbols using `K0`;
2. simulate `B` independent sequences of length 53 from that fitted VLMC after burn-in;
3. for each candidate K, fit a VLMC to bootstrap symbols 1..52;
4. predict bootstrap symbol 53;
5. compute mean zero-one loss;
6. choose the K with minimum mean zero-one loss.

If multiple K values tie exactly on bootstrap loss, choose the **smallest K on the ascending grid**. This is a preregistered implementation tie rule and favors the first optimum on the source-style ordered grid; it is not chosen from 2025 performance.

## 5. Final origin-level fit and output

After `K_star` is selected from bootstrap:
- refit VLMC on the real 52-symbol window with `K_star`;
- find the active context for the current past;
- output empirical `P(UP)` from that context;
- forecast UP if `P(UP)>=0.5`, otherwise DOWN.

Every origin must persist:
- origin week / close date;
- target week;
- `K_star`;
- bootstrap minimum loss;
- number of K values tied at the minimum;
- maximal/final tree order;
- final context count;
- active context;
- active context depth;
- active-context support;
- transition counts to UP/DOWN;
- `P(UP)`;
- forecast direction;
- realized next-week direction only in evaluation output.

## 6. Chronology

- 2022-03 onward: warm-up/history.
- 2023: implementation/development audit after 52-symbol warm-up.
- 2024: fixed pre-2025 validation.
- 2025: locked historical test only after this preregistration, implementation and pre-2025 checkpoint are frozen.
- 2025 volatility events: overlay only after the complete 2025 weekly forecast table is frozen.

No random split.

## 7. Required evaluation

Primary:
- success rate / directional accuracy.

Required diagnostics:
- balanced accuracy;
- Brier score;
- log-loss;
- UP sensitivity;
- DOWN sensitivity;
- forecast class distribution;
- confusion counts;
- calibration summary;
- comparison to always-UP, previous-week-sign and frozen RSM-52.

A high raw accuracy with one-sided forecasts must not be represented as strong directional discrimination.

## 8. Locks

Forbidden under V1:
- choosing K grid, K0, B, seed, lookback or threshold from 2025 outcomes;
- changing the 52-week window after seeing 2025;
- source/provider substitution;
- adding FAST/GVZ/BOCPD/Macro/Emergency inputs;
- NO_SIGNAL threshold tuning;
- flat voting;
- random split;
- event-conditioned origin selection;
- post-2025 rescue tuning under the same model identity;
- relabelling historical replay as prospective evidence.
