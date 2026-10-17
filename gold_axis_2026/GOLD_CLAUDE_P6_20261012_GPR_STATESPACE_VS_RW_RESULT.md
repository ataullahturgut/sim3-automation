# CLAUDE P6 — Gaussian-process (GP-LAG) and local-linear-trend (LLT) vs random walk: RESULT — **REJECT (negative)**

Prereg `GOLD_CLAUDE_P6_20261012_GPR_STATESPACE_VS_RW_PREREG.md` (commit `ec2ca3d5`, pushed before any
P6 forecast). Code `tools/gold_claude_p6_20261012_gpr_statespace_vs_rw.py`; outputs
`GOLD_CLAUDE_P6_20261012_{SUMMARY.json,SCORE_ROWS.csv}`. Inputs: committed P1 panels only.

## What was predicted
The same DAY/OVN exact-clock log return and implied price level as P1. GP-LAG uses a nonlinear
kernel on the last 5 DAY and OVN returns plus pre-issue segment returns. LLT is a Kalman
local-linear-trend on the merged 09:00/16:45 log-price series, forecasting the filtered slope.
This is a methodological control: no new information beyond past prices.

## Primary gate (8 tests, Holm) — all fail
Pooled DEV 2023–24 MSE gain (bp², positive = better) and one-sided DM p:

| Target | GP vs RW | GP vs INT | LLT vs RW | LLT vs INT |
|---|---|---|---|---|
| DAY (n=515) | +10.1 (0.32) | +12.6 (0.27) | +1.0 (0.45) | +3.5 (0.34) |
| OVN (n=395) | −66.4 (0.97) | −81.2 (0.995) | +19.7 (0.033) | +5.0 (0.15) |

Holm-adjusted: all p = 1.0 except OVN LLT vs RW, 0.26. No model beats both RW and INT in both
DEV years. **Verdict: REJECT.**

## Per-year errors (RMSE bp / price MAE USD) and direction
| Target, year | N | RW | INT | GP-LAG | LLT | GP R²_OS vs RW | LLT R²_OS vs RW |
|---|---|---|---|---|---|---|---|
| DAY 2023 | 256 | 47.75 / 6.77 | 47.77 / 6.77 | 47.45 / 6.79 | 47.82 / 6.79 | +1.23% | −0.30% |
| DAY 2024 | 259 | 54.61 / 9.74 | 54.64 / 9.74 | 54.68 / 9.77 | 54.53 / 9.67 | −0.26% | +0.29% |
| DAY 2025 | 258 | 67.69 / 16.99 | 67.65 / 16.93 | 67.67 / 16.85 | 67.49 / 16.70 | +0.07% | +0.59% |
| DAY 2026* | 45 | 86.83 / 27.46 | 86.87 / 27.46 | 86.83 / 28.23 | 86.71 / 27.40 | 0.00% | +0.27% |
| OVN 2023 | 198 | 58.98 / 8.57 | 58.91 / 8.55 | 60.22 / 8.84 | 58.82 / 8.53 | −4.28% | +0.52% |
| OVN 2024 | 197 | 64.52 / 11.10 | 64.35 / 11.05 | 64.40 / 11.05 | 64.36 / 11.06 | +0.39% | +0.51% |
| OVN 2025 | 198 | 86.75 / 23.27 | 86.37 / 23.22 | 86.28 / 23.21 | 86.48 / 23.24 | +1.06% | +0.61% |

\*2026 DAY: 45 rows with segment features, separate source. OVN 2026 BLOCKED (as in P1).

- **GP-LAG direction.** Accuracy and balanced accuracy are at or below always-UP. DAY 2023: acc
  49.8% / BA 48.7% vs always-UP 48.6%. DAY 2024: 45.2% / 48.4% vs 57.9%. OVN 2023: 45.5% / 44.9% vs
  58.6%. GP log-loss beats the expanding UP prior only in DAY 2023 (0.6940 vs 0.6962) and is worse
  in the other DEV blocks (DAY 2024 0.6952 vs 0.6868; OVN 2023 0.7083 vs 0.6911; OVN 2024 0.6904 vs 0.6888).
- **LLT.** The filtered slope almost never changes sign: it predicts UP on every row (DOWN recall
  0.00), i.e. it is a time-varying drift. Its small OVN gains vs RW (+0.5%) equal the INT drift
  gain and do not beat INT.
- **GP 90% interval coverage.** 93.4% / 91.1% (DAY 2023/24), 85.3% (2025): about calibrated in DEV
  and under-covered in 2025, consistent with P3's volatility-shift finding.

## Answer to the program question
A flexible nonlinear probabilistic model (GP regression) and a time-varying-trend state-space
model extract **no** forecastable information from past XAU/USD prices beyond the random walk and
the historical drift at the DAY and OVN horizons. Low price-level errors (for example a DAY 2023
price MAE of $6.77–6.79 for every model) come from the random walk itself, not from skill. This
replicates, at our exact clocks, why level-RMSE/MAPE reports such as Jin & Xu (2025) cannot be
read as predictive skill.
