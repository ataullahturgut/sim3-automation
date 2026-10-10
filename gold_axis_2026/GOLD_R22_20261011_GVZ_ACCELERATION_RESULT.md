# R22: H3 downside-risk GVZ-acceleration test (2026-10-11)

Pre-result prereg: GOLD_R22_CAUSAL_IMPLIED_VOL_ACCELERATION_GVZ_VS_REALIZED_PREISSUE_H3_DOWNSIDE_PREREG_20261011.md. Actual Neon read-only market data, same as R20 with 20 previous dated GVZ observations, no current-day values. Endpoint is exact third subsequent weekday at 09:00 Turkey; decision made at 08:45 using completed bars. L2=30 logistic fit frozen through 2024 for 2025 and 2026. Outcome: probability of a gold decline of at least 1.5% in H3. Scored 254/256/255/116 days for 2023/24/25/26 with 21/35/29/36 downside events.

| Year | Baseline RV+GVZ Brier | GVZ change 5/20 dates | Trend+GVZ change | Trend+negative semivariance | Full |
|---|---:|---:|---:|---:|---:|
| 2023 | .077658 | .078563 | .080463 | .080238 | .082333 |
| 2024 | .115435 | .115987 | .116235 | .116193 | .116136 |
| 2025 | .096303 | .095048 | .094300 | .094906 | .094294 |
| 2026 | .214464 | .218407 | .215484 | .213870 | .215897 |

For 2026, semivariance model highest-risk 20% had 11/23 actual large drops versus lowest-risk 4/23; baseline was 7/23 vs 6/23. Yet the complex variant loses to baseline on both 2023 and 2024 proper probability scores. The 2026 Brier improvement of .000594 is too small to establish robust advancement. No universal source-certified model promotion. These 2025/26 outcomes have been inspected repeatedly, not virgin holdout.
