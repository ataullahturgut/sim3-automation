# GOLD MONTHLY — Relative-Loss / Rescue-Gain Matrix Stage 1 V1 Authority

**Date:** 2026-10-01  
**Status:** DEV-ONLY ANALYSIS AUTHORITY / NO SWITCH / NO BLEND / NO PRODUCTION ACTION

## Purpose
Before fitting any rescue selector, build the complete frozen Exact16 DEV month-by-model relative-loss matrix.

For challenger j and target month t:

`gain(j,t) = |error_ChHHO,t| - |error_j,t|`

Positive gain means the challenger beat ChHHO. Negative gain means KEEP ChHHO was better.

## Frozen scope
- Main model: ChHHO-ANFIS.
- Competitive pool: exact frozen 16-model pool from Exact16; 15 challengers plus ChHHO.
- DEV authority: 2022-04..2024-12, 33 targets.
- Specialist Hedge is not retuned.
- Market-state and ensemble-geometry variables are origin-known context only.
- 2025/2026 is not used for Stage-1 selection, fitting, thresholding, or model reduction.

## Required outputs
1. Complete 33 × 15 rescue-gain matrix.
2. Fixed-challenger diagnostics for all 33 DEV targets.
3. Separate diagnostics for:
   - all Specialist Hedge warning months;
   - realized HIGH/MEDIUM warning months;
   - realized NORMAL false warnings;
   - non-warning months.
4. Oracle headroom for diagnostic purposes only.
5. Descriptive origin-known context diagnostics.
6. Regression gates against Contextual Rescueability V1.

## Scientific boundaries
Do not promote a fixed fallback from this stage. Do not fit a selector in Stage 1. Do not use 2025/2026 to choose models or thresholds. KEEP MAIN and ABSTAIN must remain valid actions in any later predictor.
