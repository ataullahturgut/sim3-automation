# GOLD CONTROL — DIRECTION_BCARS_SV_V1_RESEARCH PREREGISTRATION

**Date:** 2026-09-18  
**Parent:** `DIRECTION_BCARS_V1_RESEARCH`  
**Identity:** `DIRECTION_BCARS_SV_V1_RESEARCH`  
**Status:** `FROZEN_BEFORE_2025_REPLAY`

## 1. Reason for successor

The parent B-CARS V1 is mathematically blocked before 2025 because the true weekly up-ratio sample contains exact zeros. Ordinary Beta likelihood cannot score boundary observations.

This successor preserves the B-CARS(1,1) model and all source/OOS/optimizer rules but applies the standard Smithson-Verkuilen boundary transformation before Beta likelihood estimation.

Reference:
Smithson, M. & Verkuilen, J. (2006), *A better lemon squeezer? Maximum-likelihood regression with beta-distributed dependent variables*, Psychological Methods 11(1), 54-71, DOI `10.1037/1082-989X.11.1.54`.

## 2. Frozen boundary transformation

At every expanding estimation origin with `n` training up-ratios `y_i in [0,1]`, transform **all** training observations as

`y_i^* = (y_i*(n-1)+0.5)/n`.

This maps all observations to the open interval `(0,1)`.

The current training sample size `n` is used at each origin, exactly and deterministically. No epsilon is tuned.

The B-CARS likelihood and recursion are fit to `y^*`.

The 0.5 direction boundary is invariant under this affine transformation:
`y=0.5 <=> y^*=0.5`.

Therefore the native direction decision remains:
- UP iff forecast `k^*_(t+1)>0.5`;
- DOWN otherwise.

For continuous up-ratio error diagnostics only, the forecast mean is mapped back to the original scale:

`k_raw = (n*k^* - 0.5)/(n-1)`.

If this inverse produces a value outside `[0,1]`, the origin is fail-closed; no clipping is permitted.

## 3. Everything else remains frozen from parent V1

Unchanged:
- Twelve Data XAU/USD true 1h HIGH/CLOSE source;
- weekly interval semantics;
- `H_t^a=max(H_t,C_(t-1))`;
- modeled sample starts target week 2022-03-07;
- B-CARS(1,1);
- expanding-window OOS;
- first 52 modeled weekly up-ratios as initial estimation window;
- unconditional-mean recursion initializer;
- deterministic five-start L-BFGS-B numerical contract;
- no exogenous variables;
- no NO_SIGNAL;
- no other Gold Control motor input;
- no random split;
- 2023 development audit;
- 2024 fixed validation;
- freeze pre-2025 checkpoint before 2025 scoring;
- freeze complete 2025 weekly forecast table before event overlay.

## 4. Output interpretation

Native model output remains forecast up-ratio mean `k` and direction from the 0.5 threshold.

A Beta-tail `P_ext(UP)` may be retained only as a derived Gold diagnostic, not as the source paper's native direction rule.

## 5. Locks

The transformation above is adopted because of the two **pre-2025** boundary observations. It may not be altered based on 2025 results.

No alternate epsilon, hurdle/zero-inflated Beta, model order, frequency, threshold, window or feature augmentation may be selected under this identity after 2025 is scored.
