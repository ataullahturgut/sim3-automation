# CLAUDE P6 — Gaussian-process and local-linear-trend forecasts vs random walk: PREREGISTRATION

Date: 2026-10-12. Investigator: Claude (independent; GPT-6 P6 work not read). Protocol PR #93, stage P6:
a **methodological control, not a new-information mechanism**. Written and committed before any P6
forecast is computed. The P1 panels and P1 results (RW ≈ INT, no segment information) are already
known; P6 asks whether a flexible probabilistic model extracts anything P1's linear models missed.

## Targets (identical to P1; panels `data_claude_p1/`)
DAY: decision 08:45, `y = ln P(16:45)/P(09:00)`; OVN: decision 16:30, `y = ln P(next 09:00)/P(16:45)`
(bp). Price-level forecast `P̂ = P_origin·exp(ŷ)`, error in USD/oz. 2020–22 warm-up only; DEV 2023–24;
2025 opened; 2026 separate source (OVN 2026 BLOCKED as in P1).

## Models (frozen)
- **RW**: ŷ = 0. **INT**: expanding mean of prior same-type targets (as in P1).
- **GP-LAG** (Gaussian-process regression; mechanism: nonlinear dependence on recent path).
  - Features, all known before the decision and standardized on the training window:
    - DAY: last 5 eligible DAY returns, last 5 eligible OVN returns, `f_us`, `f_asia` (P1 definitions).
    - OVN: last 5 OVN returns, last 5 DAY returns, `g_daysofar`.
  - Missing lagged values are set to 0 and rows without segment features are skipped.
  - Kernel: `ConstantKernel·RBF(length_scale, isotropic) + WhiteKernel`, sklearn `GaussianProcessRegressor`,
    `normalize_y=True`, one optimizer start.
  - Training set: the most recent 750 prior eligible windows (cap for tractability).
  - Hyperparameters re-optimized on the first eligible decision of each calendar month; between
    refits the GP is re-conditioned daily on all prior windows (last 750) with frozen hyperparameters.
  - Predictive mean → ŷ; predictive sd → p_up = Φ(ŷ/sd).
- **LLT** (local linear trend state space; mechanism: time-varying drift, the trend-extrapolation
  idea behind level-forecasting papers such as Jin & Xu 2025).
  - statsmodels `UnobservedComponents(level='local linear trend')` on the merged clock series of log
    prices (09:00 and 16:45 each day, in time order, regular steps assumed). MLE refit monthly, Kalman
    filter updated with every new observation.
  - Forecast of the next window return = filtered slope `β_t` (the expected change over one step).
  - For DAY at 08:45 the last observation in the series is the previous 16:45; for OVN at 16:30 it
    is the same day's 09:00.

## Primary gate (row-matched; 2 models × 2 targets × 2 comparators = 8 tests, Holm)
A model is SUPPORTED for a target only if its return MSE is below RW **and** INT in each of 2023 and
2024, **and** pooled DEV one-sided DM (Newey–West 5) p < 0.05 vs each, Holm over 8, **and** no 2025
reversal. Otherwise REJECT.

## Secondary (reported)
Per year: RMSE (bp), price MAE/RMSE (USD), R²_OS vs RW/INT, direction accuracy, balanced accuracy,
UP/DOWN recall vs always-UP, log-loss vs expanding UP prior, 90% interval coverage (GP-LAG only).

## Honesty rules
No kernel, feature, window-cap or refit-schedule change after results. Level metrics are reported
only together with the RW level error (a low level MAPE is not skill). 2025/26 are opened
retrospective periods. No Neon access needed (inputs are the committed P1 panels).
