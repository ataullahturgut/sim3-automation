# CLAUDE R74 — Risse (2019) perspective: economic value of XAU/USD forecasts by horizon — PREREGISTRATION

Date: 2026-10-13. Written and committed before any R74 data extraction, forecast or portfolio result.
Source paper: M. Risse (2019), "Combining wavelet decomposition with machine learning to forecast gold
returns", *International Journal of Forecasting* 35, 601–615 (DOI 10.1016/j.ijforecast.2018.11.008).

## The perspective taken from the paper
1. Judge forecasts by **economic value** for a mean–variance investor, not only by statistical accuracy.
   Risse finds R²_OS of only +0.93% (monthly) but a CER gain of +5.28 percentage points and terminal
   wealth more than double the historical-mean benchmark (full sample 1992–2016).
2. Weights `w_t = r̂_{t+1} / (γ σ̂²_{t+1})`, γ = 3. Economic value can come from the **mean** forecast
   r̂ and/or from the **variance** forecast σ̂².
3. **MODWT (Haar)** decomposition of predictors into frequency bands, fed to **SVR (RBF)**.

Link to our program: P1/P2/P6 found no forecastable mean at DAY/OVN; P3 found forecastable
**variance**. In the paper's framework a forecastable variance alone can add economic value
(volatility timing, Moreira & Muir 2017), which has not been tested in this repository.

## Questions
- Q1: Does the paper's DWT-SVR mean forecast beat the historical mean (HM) for XAU/USD at short horizons?
- Q2: Does volatility timing (μ = HM, σ̂² = EWMA forecast) add economic value over the HM strategy?
- Q3: Which horizon h gives the largest **net-of-cost** economic value, and is it stable?

## Data cohorts (read-only Neon; reported separately, never pooled)
- **A — exact clock (PIT-clean):** daily XAU/USD price at 16:45 TR from the P1 panels
  (`data_claude_p1/`; 2020–2025 EV/Dukascopy, 2026 direct Dukascopy). Predictors: gold's own returns only.
  Horizons: h = 1, 3, 5 trading days (16:45 → 16:45).
- **B — long daily (research-only):** `XAU_STAKTRAKR_RESEARCH_DAILY_R1`, `XAG_...`, `XPT_...` (2010-01 to
  2026-07; daily values timestamped "12:00", clock/time zone unverified, no PIT claim) and `NASDAQ100_FRED`
  lagged by one extra day (conservative against clock ambiguity). Horizons: h = 1, 5, 10, 21 trading days.
- Risk-free: `CORE5_FEDFUNDS_RESEARCH_R1` (monthly %, previous month's value used, accrued per day).
- Gold excess return over h: `r = ln(P_{t+h}/P_t) − rf·h/252`.

## Forecasts (decision at t; only data ≤ t; expanding re-estimation at every rebalance)
- **HM:** expanding mean of past non-overlapping h-horizon excess returns (paper's benchmark).
- **DWT-SVR (paper):**
  - Features: causal Haar MODWT wavelet coefficients W1..W4 and smooth V4 of daily log returns of each
    predictor series, evaluated at t with past data only (Cohort A: gold; Cohort B: gold, silver,
    platinum, NASDAQ100). This is the real-time coefficient version, not the two-sided MRA.
  - sklearn SVR, RBF kernel, standardized features and target, ε = 0.1, γ_kernel = 1/K, C = 3 (= 3σ_y
    on the standardized target), as in the paper.
  - Training: all past non-overlapping h-blocks (minimum 120), capped at the latest 1500.
- **SVR-RAW (control):** same SVR on raw lagged daily returns of the same series (lags 1–5 plus
  past h-day and 21-day returns).
- Variance forecast for the weight:
  - (i) **PAPER**: rolling variance of daily excess returns over the last 2520 days (Cohort A: expanding), × h.
  - (ii) **EWMA**: RiskMetrics λ = 0.94 on daily returns, × h.

## Strategies (rebalanced every h trading days, non-overlapping)
- **S0 HM-PAPER:** μ = HM, σ² = PAPER (the paper's benchmark).
- **S1 DWT-SVR-PAPER:** μ = DWT-SVR, σ² = PAPER (the paper's model).
- **S2 SVR-RAW-PAPER.**
- **S3 VOL-TIMING:** μ = HM, σ² = EWMA.
- **S4 DWT-SVR-EWMA.**
- **S5 Buy-and-hold:** w = 1.
- Weights are clipped to [−0.5, 1.5]. Portfolio excess return `w·r`.
- Costs: one-way c·|w_t − w_{t−1}| with c ∈ {0, 2, 5, 10, 25} bp. 25 bp is a rough retail/bank-like
  proxy, not a real bank quote.

## Metrics (per cohort × horizon × period)
- R²_OS of the mean forecast vs HM (Campbell–Thompson) with the Clark–West test.
- Annualized CER = mean − ½γ·var (γ = 3, annualized by 252/h).
- ΔCER vs S0, Sharpe ratio, terminal wealth, maximum drawdown, average turnover.
- Break-even one-way cost at which ΔCER = 0.
- ΔCER significance: moving-block bootstrap of the per-period utility difference (block = 6 periods,
  5000 draws, one-sided).

Evaluation periods:
- Cohort B: 2015–2022 (historical, not previously used in this program's exact-clock work), DEV 2023–24,
  opened 2025–26.
- Cohort A: DEV 2023–24, opened 2025, 2026 (separate source).

## Primary hypotheses and gate
Primary family, Holm-corrected over all (cohort, horizon, hypothesis) combinations:
- **H1:** S1 R²_OS > 0 (Clark–West one-sided p).
- **H2:** S3 ΔCER > 0 vs S0 at c = 5 bp.
- **H3:** S4 ΔCER > 0 vs S3 at c = 5 bp.

Evaluation window per hypothesis:
- Cohort B: pooled 2015–2024.
- Cohort A: DEV 2023–24.

A hypothesis is **SUPPORTED** only if all four hold:
1. Holm-adjusted p < 0.05.
2. The effect has the same sign in each available sub-period: 2015–2022 and 2023–24 for Cohort B;
   2023 and 2024 for Cohort A.
3. The opened 2025–26 sign is reported (a reversal is flagged; it cannot rescue a result).
4. The cost is reported at which the gain disappears.

**Optimal horizon:** the horizon with the largest S3/S4 ΔCER at c = 5 bp among SUPPORTED horizons. If
none is supported, the answer is "no horizon shows robust net economic value".

## Honesty rules
- No hyperparameter, band (J = 4), clip, γ, λ or horizon changes after results.
- Economic value is computed on mid prices and is hypothetical: no profitability claim without bank
  bid/ask quotes (CLAUDE.md).
- Cohort B has an unverified daily clock and no PIT certification; its results are labelled
  research-only.
