# GOLD CONTROL — DIRECTION ENGINE ESTIMATION WINDOW ROBUSTNESS V1

**Date:** 2026-09-24
**Identity:** `DIRECTION_ENGINE_ESTIMATION_WINDOW_ROBUSTNESS_V1`
**Parent cascade:** frozen `SQRT-HAR-DR -> UP Verifier V2 -> UP-2`
**Research authority:** pre-2025 only
**Runtime authority:** NONE
**Production writes:** FORBIDDEN

## Scope
This first execution unit audits the frozen SQRT-HAR-DR risk layer because its training memory is an explicit regression estimation window. The formula, feature set and q80 high-risk semantics remain unchanged. The experiment changes only the number of matured pre-origin training rows.

2025 and 2026 are excluded from code-level selection/evaluation.

## Window surface
For each annual origin 2022, 2023 and 2024:
- build the same SQRT-HAR-DR rows;
- minimum formation = 250 matured rows;
- evaluate deterministic window grid 250,275,... up to available formation;
- also evaluate EXPANDING;
- all thresholds and OLS parameters are fit only on the selected pre-origin training subset.

Selection is not the single best point. Report contiguous robust regions using a multi-metric score over MSE, QLIKE, high-risk AUC and alarm stability across 2022-2024.

## Structural break
At each annual origin, use only pre-origin rows. Fit the frozen SQRT-HAR-DR regression with 0..3 piecewise-constant parameter regimes using dynamic-programming segmented OLS, minimum 125 rows/segment, and BIC selection. The last BIC-selected break defines a BREAK_CONDITIONED candidate. This is an origin-safe Bai-Perron-style segmented-regression approximation, not a claim of exact Bai-Perron critical-value inference.

Compare EXPANDING, robust rolling-window candidates, and BREAK_CONDITIONED on 2022-2024 only.

## Source boundary
Use the governed read-only `public.xau_intraday_research_cache_5m` source. This execution does not silently splice external 2018-2021 data into the governed panel. If the earliest governed history cannot support a requested origin/window, mark it unavailable rather than weakening the minimum formation rule.

## Governance
- no random split;
- no 2025/2026 selection;
- no production writes;
- no runtime promotion;
- frozen SQRT formula/features unchanged;
- Router and UP-2 memory policies are not silently inferred from SQRT because their natural training units differ; they require route/competence-specific follow-on execution under the same umbrella identity.
