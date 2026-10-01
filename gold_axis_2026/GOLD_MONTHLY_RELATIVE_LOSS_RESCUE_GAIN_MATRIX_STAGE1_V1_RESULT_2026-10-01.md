# GOLD MONTHLY — Relative-Loss / Rescue-Gain Matrix Stage 1 V1

**Date:** 2026-10-01  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS / DEV-ONLY SELECTION AUTHORITY / NO SWITCH AUTHORIZED

## 1. Purpose

Build the frozen Exact16 DEV month × model matrix for `gain(j,t)=|error_ChHHO,t|-|error_j,t|` before fitting any contextual selector. Positive gain means the challenger beat ChHHO.

## 2. Coverage and frozen pool

- DEV targets: **2022-04..2024-12 (33 months)**
- Main: **ChHHO-ANFIS**
- Challengers: **15 frozen Exact16 alternatives**
- Specialist Hedge warning months: **20** = 10 realized HIGH/MEDIUM + 10 realized NORMAL false warnings
- Non-warning DEV months: **13**
- 2025/2026: **not used for selection or fitting in Stage 1**

## 3. All 33 DEV months — fixed challenger diagnostic

| Rank | Challenger | Gain vs ChHHO (USD) | Wins |
|---:|---|---:|---:|
| 1 | DE_ABC_RBFNN | -2.81 | 13/33 |
| 2 | PLS1_V1 | -7.00 | 18/33 |
| 3 | LMC2_RBF_M32 | -11.14 | 17/33 |
| 4 | FULL7_ANN | -15.83 | 19/33 |
| 5 | REDUCED4_ANN | -18.43 | 16/33 |
| 6 | SVR_DAILY_SUMMARY12 | -36.16 | 17/33 |
| 7 | BOOST_CATBOOST_ORDERED | -47.40 | 16/33 |
| 8 | AOA_ELM | -61.07 | 15/33 |
| 9 | SVR_CURRENT8 | -105.87 | 18/33 |
| 10 | CNN_LSTM_LB6 | -115.54 | 16/33 |
| 11 | SVR_MIXED20 | -166.28 | 12/33 |
| 12 | CNN_LSTM_LB3 | -175.08 | 16/33 |
| 13 | LSTM_LB3 | -176.95 | 16/33 |
| 14 | LSTM_LB6 | -181.14 | 12/33 |
| 15 | BOOST_RANDOM_FOREST_ANCHOR | -201.46 | 11/33 |

**Finding:** no single frozen challenger beats ChHHO on cumulative AE across all 33 DEV targets.

## 4. Specialist Hedge warning months

Across all 20 warning months, the best fixed challenger is **LMC2_RBF_M32**, but its gain is **-16.11 USD** with 11/20 monthly wins. Therefore even the best fixed warning fallback is worse than KEEP ChHHO.

On the 10 realized HIGH/MEDIUM warning months only (hindsight anatomy):
- LMC2_RBF_M32: **+101.76 USD**, 8/10 wins
- REDUCED4_ANN: **+88.52 USD**, 7/10
- AOA_ELM: **+71.52 USD**, 5/10
- FULL7_ANN: **+68.87 USD**, 6/10
- LSTM_LB3: **+54.36 USD**, 7/10
- PLS1_V1: **+47.66 USD**, 7/10
- CNN_LSTM_LB6: **+46.78 USD**, 6/10

This confirms the prior result: rescue exists when ChHHO is genuinely elevated-error, but false warnings erase fixed-fallback gains.

## 5. Oracle headroom

On the 20 frozen warning months:
- ChHHO ΣAE: **1127.89 USD**
- best-alternative-every-warning hindsight gain: **445.76 USD**
- KEEP-or-best-alternative hindsight gain: **469.73 USD**

Across all 33 DEV targets, KEEP-or-best-alternative hindsight gain is **708.51 USD**.

These are ceilings, not operational results.

## 6. Context diagnostics

Simple one-variable associations with best available warning-month rescue gain are weak:
- p_HIGH: **r = +0.265**
- direction agreement: **r = +0.174**
- dispersion: **r = +0.191**
- ChHHO absolute distance from ensemble median: **r = -0.121**
- ChHHO IQR distance: **r = -0.191**
- ChHHO forecast percentile: **r = -0.325**

Regime/state cells are also heterogeneous. No single R0/R1/R2, NORMAL/EXTREME/TRANSITION, consensus, dispersion, or p_HIGH rule is promoted.

A particularly important DEV warning case is **2023-03**: router warning, realized NORMAL, and **0/15 alternatives beat ChHHO**. This is the historical failure mode that any selector must learn to leave as KEEP MAIN / abstain.

## 7. Regression gate

The Stage-1 build reproduces the already frozen Rescueability V1 checkpoints:
- all-warning LMC2 gain: **-16.11 USD**
- elevated-warning LMC2 gain: **+101.76 USD**
- elevated-warning LMC2 wins: **8/10**
- warning KEEP-or-best oracle gain: **469.73 USD**

Therefore the 33-month matrix is consistent with the previous 20-warning analysis.

## 8. Binding decision

- No fixed fallback is promoted.
- No model is removed from the frozen 15-challenger pool in Stage 1.
- No hard regime/consensus/dispersion rule is promoted.
- 2025/2026 remains outside selection authority.
- **Next stage:** freeze a low-capacity, origin-safe Contextual Relative-Loss / Rescue-Gain Predictor V1 and evaluate it with chronological DEV validation, preserving KEEP MAIN and ABSTAIN.
