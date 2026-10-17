# CLAUDE R74 — Risse (2019) perspective, economic value by horizon: RESULT — **NOT SUPPORTED (negative)**

Prereg `GOLD_CLAUDE_R74_20261013_RISSE_ECONOMIC_VALUE_HORIZON_PREREG.md` (commit `3d3240d3`, pushed
before data extraction). Inputs (checksum-verified, read-only Neon) and frozen code committed at
`0d18b1fb`. Outputs: `GOLD_CLAUDE_R74_20261013_{SUMMARY.json,PERIOD_ROWS.csv}`.
Economic value is computed on mid prices and is **hypothetical**; this is not a profitability claim
(no bank bid/ask).

## Primary gate (21 tests, Holm) — none supported
| Cohort / horizon | H1: DWT-SVR R²_OS > 0 | H2: volatility timing ΔCER > 0 @5 bp | H3: DWT-SVR+EWMA vs VOL @5 bp |
|---|---|---|---|
| A exact 16:45 TR, h = 1, 3, 5 days (DEV 2023–24) | fail (R²_OS −14% to −36%) | fail (ΔCER +0.6 to +1.3 pp, p 0.38–0.49) | fail |
| B long daily, h = 1, 5, 10, 21 days (2015–2024) | fail (R²_OS −16% to −32%) | fail (ΔCER −0.3 to −1.3 pp) | fail |

All Holm-adjusted p = 1.0. **No horizon shows robust net economic value.**

## Key numbers (annualized CER %, γ = 3, one-way cost 5 bp; HM = paper's historical-mean benchmark)
| Cohort, h, period | N | HM | DWT-SVR (paper) | VOL timing | Buy & hold | DWT-SVR R²_OS | VOL break-even cost |
|---|---|---|---|---|---|---|---|
| A h=1, DEV 2023 | 257 | −0.80 | −18.93 | −5.35 | 4.94 | −21.6% | 0 bp |
| A h=1, DEV 2024 | 259 | 9.51 | −6.69 | **16.33** | 16.49 | −8.1% | 74 bp |
| A h=1, DEV 2023–24 | 516 | 4.39 | −12.75 | 5.54 | **10.76** | −14.3% | 18 bp |
| A h=5, DEV 2023–24 | 103 | 4.71 | −4.25 | 5.96 | **10.86** | −21.3% | 33 bp |
| A h=1, opened 2025 | 258 | 50.07 | −11.44 | **54.71** | 40.67 | −21.0% | 92 bp |
| A h=1, 2026 (other source) | 178 | −40.28 | −32.29 | **0.24** | −22.00 | −5.2% | >500 bp |
| B h=1, 2015–2024 | 2,525 | 1.47 | −12.18 | 1.17 | **4.38** | −15.9% | 1 bp |
| B h=5, 2015–2024 | 505 | 1.56 | −6.13 | 0.63 | **4.40** | −21.1% | 0 bp |
| B h=21, 2015–2024 | 59 | 3.71 | −4.78 | 2.43 | **6.29** | −27.3% | 0 bp |
| B h=21, opened 2025–26 | 20 | 16.51 | 27.02 | 19.88 | 16.51 | +23.9% (CW p=0.01) | 145 bp |

## Findings
1. **The paper's DWT-SVR does not transfer** to short horizons (1–21 trading days) for XAU/USD.
   - R²_OS is strongly negative in every pre-opened period, against the paper's +0.93% (monthly,
     1992–2016, 9 macro predictors).
   - Direction accuracy is about 47–53%, at or below always-UP.
   - Turnover is very high (0.8–1.1 weight units per rebalance), so costs destroy any value.
2. **Volatility timing** (mean = historical drift, variance = EWMA) is the only component with a
   plausible economic effect in the exact-clock cohort. Sharpe 1.33 vs 0.98 (HM) in 2024, 3.04 vs
   2.35 in opened 2025, and +0.24 vs −40.28 CER in 2026.
   - **It fails in 2023** (CER −5.35 vs −0.80) and in the long-daily cohort (2015–2024).
   - It is never significant (best one-sided p = 0.039, Cohort A h=5 DEV 2024; not Holm-significant).
3. **Buy-and-hold beats every timed strategy in DEV** (CER about 11 vs 4–6), consistent with the
   2023–25 gold bull market. The mean–variance weight `μ/(γσ²)` with a small historical drift
   holds too little gold in a trending market.
4. **Opened 2025–26 is regime-dependent.** DWT-SVR turns positive at h = 5/10/21 in Cohort B (R²_OS
   +8.8% / +5.8% / +23.9%) after being strongly negative in 2015–2024. This is the pattern Risse
   reports (wavelet value appears in strong-trend/crisis periods), but it is an opened period and a
   sign reversal, so it is **not** evidence of a usable forecast. It is a hypothesis for prospective
   testing only.

## Answer to "which horizon is optimal?"
None of the tested horizons (Cohort A: 1, 3, 5 days at 16:45 TR; Cohort B: 1, 5, 10, 21 days) gives
statistically robust economic value net of 5 bp costs. Weakly, the economic logic favours **longer
horizons (≥ 5 days) with volatility timing**, because turnover and costs fall (Cohort A
break-even 33 bp at h=5 vs 18 bp at h=1 in DEV) while volatility persistence remains. Even there
the DEV gain over HM is only +1.25 CER points and not significant, and buy-and-hold is better.

## Limits
- Cohort B has an unverified daily clock ("12:00"); it is research-only data.
- Mid-price backtest; no bank quotes; costs are scenario values. γ = 3 and weight clipping to
  [−0.5, 1.5] follow the paper's setting and figure.
- The paper's nine monthly macro predictors were not available at daily frequency with PIT
  integrity; the predictor set differs (precious metals and NASDAQ100).
