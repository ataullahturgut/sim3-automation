# TR09 H3 — negative five-return path efficiency: executed negative result (2026-10-31)

**Verdict: REJECT; no model promotion, no user alert.** A genuinely new, preregistered signed five-day trend-efficiency hypothesis was executed against connected Neon historical data. It fails both-year tail-risk and two-sided directional criteria. The 2025/2026 risk association changes sign. This is a historical diagnostic only; vendor firstprint, actual 09:00 quote receipt and bank executable ASK/BID are unverified.

## Reproducibility and execution chronology

1. Before work, read branch HEAD `4500e412610b2a0223b52cfe2c76d446abf5b8a5` (2026-10-30 negative report) and canonical `gold_axis_2026/GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md` blob `279dae0b2d5694593adda076d644a5d186241304`. Previous experiments (volatility, MDD, calendar exposure, matured60, downside semivariance, sign chop, shock concentration and acceleration) were preserved.
2. **Preregistered BEFORE outcomes:** `gold_axis_2026/GOLD_TR09_20261031_NEGATIVE_PATH_EFFICIENCY_PREREG.md`, commit `c372de4107f9ee871b2e88c86ab4a59f397b8c36`. Gate: E = ln(p5/p0)/SUM_{i=1..5} abs(ln(pi/p{i-1})), E=0 for zero denominator; TRUE iff E<=-0.50. Unlike earlier tests, this jointly measures negative trend direction and signed path efficiency, not downside squared-share or reversal count.
3. **Frozen SQL before scoring:** `gold_axis_2026/tools/gold_tr09_20261031_negative_path_efficiency_reproduce.sql`, commit `67f5a83d4ca1b321fbee12e5c47a750a7da4b7ba`. Read-only Neon project `winter-art-94880101`, table `public.gold_research_histdata_xau15m_candidate`. Run via connected `run_sql`. Training only 2023–24 origins with targets mature by Dec31 2024 (N496), no later labels for the new arm; test 2025 N258 and 2026 Jan–Sep N188.
4. Independent LAG/LEAD eligible-calendar rebuild, **frozen separately** at `gold_axis_2026/tools/gold_tr09_20261031_negative_path_efficiency_independent_audit.sql`, commit `399efafb5aa18170a7388fe0b1cc16bf08846cc5`; executed against Neon. Matches total annual UP/DOWN/tail counts and target order/purge: all 0 violations. All online comparators use `target_d<origin_d`; both years 0 maturity violations in main query.

## Data and timestamp caveats

Source: HistData candidate historical XAU BID M15, bar starts 08:45 Europe/Istanbul and **nominally completes at 09:00**; 09:00-to-09:00 close-price returns are features, and future label is the third subsequent eligible weekday 09:00. Same exclusions and missing-anchor calendar as 2026-10-30. **No historical independent proof of provider first publication, actual receipt, latency, Turkish bank executable bid/ask or all-in trading cost.** A bar closing at 09:00 cannot be presumed actionable at exactly 09:00. Thus no claim of real-time PIT availability or tradeable success.

## Identical-row comparison with frozen seven controls

BA = balanced accuracy, UP/DOWN recall = sensitivity for each actual direction. Both Brier scores lower-is-better. **2025 N258: UP161/DOWN97/tail23. 2026 Jan–Sep N188: UP92/DOWN96/tail40.**

| Year | Arm | N | BA % | UP recall % | DOWN recall % | UP Brier | Severe-DOWN Brier |
|---|---|---:|---:|---:|---:|---:|---:|
| 2025 | Constant | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2400672 | 0.0822839 |
| 2025 | Two-UP | 258 | 52.5133 | 68.9441 | 36.0825 | 0.2406951 | 0.0822271 |
| 2025 | Vol Q75 | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2440358 | 0.0795049 |
| 2025 | MDD Q75 | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2402204 | 0.0820787 |
| 2025 | Calendar >=5 | 258 | 50.0000 | 100.0000 | 0.0000 | 0.2401858 | 0.0821760 |
| 2025 | Matured60 pooled | 258 | 47.2850 | 83.2298 | 11.3402 | 0.2448019 | 0.0843355 |
| 2025 | Matured60 vol-strat | 258 | 45.9499 | 85.7143 | 6.1856 | 0.2471405 | 0.0787308 |
| 2025 | **NEW negative path efficiency** | **258** | **50.0000** | **100.0000** | **0.0000** | **0.2397556** | **0.0817915** |
| 2026 Jan–Sep | Constant | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2535882 | 0.1920017 |
| 2026 Jan–Sep | Two-UP | 188 | 46.2183 | 68.4783 | 23.9583 | 0.2609284 | 0.1922523 |
| 2026 Jan–Sep | Vol Q75 | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2585391 | 0.1882070 |
| 2026 Jan–Sep | MDD Q75 | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2545877 | 0.1908302 |
| 2026 Jan–Sep | Calendar >=5 | 188 | 50.0000 | 100.0000 | 0.0000 | 0.2531117 | 0.1914909 |
| 2026 Jan–Sep | Matured60 pooled | 188 | 57.0199 | 61.9565 | 52.0833 | 0.2512439 | 0.1767554 |
| 2026 Jan–Sep | Matured60 vol-strat | 188 | 57.7672 | 72.8261 | 42.7083 | 0.2480173 | 0.1792687 |
| 2026 Jan–Sep | **NEW negative path efficiency** | **188** | **50.0000** | **100.0000** | **0.0000** | **0.2529671** | **0.1923803** |

Seven control arms exactly reproduce the 2026-10-30 scores to 7 decimals. New tail Brier is worse than Vol Q75 by **0.0022866 in 2025** and **0.0041733 in 2026**; worse than Matured60 vol-strat by **0.0030607 in 2025** and **0.0131116 in 2026**. New directional BA=50% and DOWN recall=0% in BOTH years, although 2025 UP Brier is marginally below constant. No valid two-sided skill.

## Independent subgroup counts and severe-tail association

| Period | E<=-0.50 | N | UP | DOWN | Severe DOWN | Tail rate |
|---|---|---:|---:|---:|---:|---:|
| 2023–24 purged train | FALSE | 414 | 229 | 185 | 25 | 6.0386% |
| 2023–24 purged train | TRUE | 82 | 44 | 38 | 2 | 2.4390% |
| 2025 | FALSE | 226 | 143 | 83 | 22 | 9.7345% |
| 2025 | TRUE | 32 | 18 | 14 | 1 | 3.1250% |
| 2026 Jan–Sep | FALSE | 149 | 76 | 73 | 30 | 20.1342% |
| 2026 Jan–Sep | TRUE | 39 | 16 | 23 | 10 | 25.6410% |

Independent SQL shows 0 invalid target order and 0 training purge violations. A negative coherent five-day path appears **less** associated with severe future falls in 2023–25, but **more** in 2026. The 2025 TRUE group has only 32 observations and 1 tail event; all annual labels overlap across three-day forecast windows. No causal interpretation or reliable actionable reversal.

## Scientific decision and governance

**Reject** per frozen criteria: BA 50<52.5, DOWN recall 0<20, tail Brier fails to beat BOTH controls in BOTH years. Gate subgroups happen to pass N>=30, but that does not rescue the model. No threshold search, sign inversion, 2026-specific reweighting or posthoc promotion. 2025/26 have been repeatedly examined and are **not independent out-of-sample validation**. 2027 prospective pre-outcome timestamped issuance and verified source firstprints/bank BID/ASK remain mandatory. Main manifest, live model, prior results and production authority remain unchanged.