# TR09 H3 | Lagged five-session realized-volatility tail test — protocol (2026-10-22)

Status: PRE-RESULT FROZEN EXPLORATORY HYPOTHESIS. No trading/model promotion.

## One predeclared hypothesis
At 09:00 Europe/Istanbul, **high trailing five eligible 09:00-to-09:00 realized volatility** may indicate increased probability of a >=2% XAU/USD decline at the 09:00 quote three *eligible sessions* later. Direction (UP/DOWN) is a secondary mandatory diagnostic, not a selection objective.

- Data: Neon `Gold Control` project `winter-art-94880101`, read-only table `public.gold_research_histdata_xau15m_candidate`; HistData fixed-EST M1-derived M15 candidates, `native_minute_bars=15`. Origin 09:00TR = close of M15 bar starting 08:45TR (06:00UTC completed). Archive retrieved 2026-10-08; original historical publication firstprint is **NOT** verified. No future feature, no 2025/26 calibration.
- Calendar: Mon–Fri excluding 2023-01-02, 2023-04-07, 2023-12-25, 2024-01-01, 2024-03-29, 2024-12-25, 2025-01-01, 2025-04-18, 2025-12-25, 2026-01-01, 2026-04-03; exact known 2026-09-25 missing 09 quote is **not** a holiday. Every needed 09 quote (current, prior five, target third) must exist with `native_minute_bars=15`; otherwise exclude, never skip an absent trading day.
- Feature at origin t: `v5=sqrt((sum_{j=0..4} (ln(P_{t-j}/P_{t-j-1}))^2)/5)`. All six prices known by 09:00TR on origin. Fixed binary gate `high=v5>Q75_train(v5)`, with Q75 from **matured 2023–24 train only** (PostgreSQL `percentile_cont(0.75)` or linearly interpolated sorted quantile). No 2025/26 threshold tuning.
- Label: `y_up=1[P_{t+3}>P_t]`; `y_down2=1[P_{t+3}/P_t<=0.98]`. Target is exact third eligible session at 09:00TR; not the legacy native H3 D0→D3 daily-mean label.
- Training: 2023-01-01..2024-12-31 origins **with target<=2024-12-31**; purge crossing-year labels. For high vs low, Laplace `p=(events+1)/(n+2)`, separately for UP and downside. Direction UP if `p_up>=0.5`.
- Comparison on **identical available rows**: (A) unconditional Laplace rate from the same train, (B) previous two-consecutive-UP feature with separately refitted Laplace rates on identical train rows, (C) new high-v5 feature. Per 2025 and 2026 Jan–Sep report N, BA, UP/DOWN recall, direction Brier, downside Brier and event counts. No per-year retuning, no cherry-picked subset.
- Legacy R66/native H3 is a different target and must **not** be ranked against this target as a like-for-like predictor. If included, explicitly mark horizon mismatch.
- Reject if no consistent downside Brier and direction-calibration benefit across both years, or if performance depends on one inspected year. 2025 and 2026 are repeatedly examined exploratory samples, **not independent validation**. Lock 2027 as prospective PIT evaluation with bank BID/ASK and firstprint proof before trading claims.
- Existing canonical manifest, production model, and previous reports are untouched.
