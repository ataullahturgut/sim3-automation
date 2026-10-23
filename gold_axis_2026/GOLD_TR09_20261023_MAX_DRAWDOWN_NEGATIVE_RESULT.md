# TR09 H3 — Trailing five-session maximum drawdown, executed negative result (2026-10-23)

**Decision:** REJECT for model promotion. An actual read-only Neon SQL evaluation was executed after pre-result preregistration, and an independent in-tool JavaScript calculation agreed with the SQL metrics. No notification-worthy improvement; no production change. No original report or canonical manifest overwritten.

## Reproduction and lineage
- GitHub branch `gold-execution-channel-audit-20261006`; branch HEAD before preregistration: `4f078f7db5dfcb00057244db59c6e9a836ceedc6`. Canonical `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md` blob `279dae0b2d5694593adda076d644a5d186241304` read first, unchanged.
- Preregistration committed **before scoring**: `GOLD_TR09_20261023_LAGGED5_MAX_DRAWDOWN_PREREG.md` at commit `b2ffa0a0bb83b03a55ee83de9c1d6b73d11c3ceb`.
- Exact **read-only PostgreSQL** reproduction: `tools/gold_tr09_20261023_max_drawdown_reproduce.sql` (commit `f43f17a26744a9c61e9c535ab2e893f3822d7b1c`). It produces all metrics below; no external files or fitting packages required. Database: Neon `winter-art-94880101`, `public.gold_research_histdata_xau15m_candidate`.
- Fixed-EST HistData M1→M15 08:45–09:00 Europe/Istanbul completed 15-minute close; six previous/current exact 09:00 anchor prices, future exact third eligible 09:00 target. Weekends and listed Good Friday/Christmas/New Year dates excluded. Missing 2026-09-25 quote is an outage; fail closed. Historical data retrieved **2026-10-08**, so firstprint/actual origin-time vendor availability remains **UNVERIFIED**. Historical exercise only; 09:00 completion does not imply executable zero-latency quote.
- 2023–2024 train: **N496** after full five-session lookback and year-boundary target purge; **27** >=2% downside events. 2025 **N258**, 2026 Jan–Sep **N188**. Training Q75 max drawdown = **0.0176338965292272** (1.7634%); training Q75 five-return realized vol = **0.010206552832574104**.
- Four arms fitted by Laplace rates on the **same N496 train rows** and scored on the **same test rows**: constant; two-UP streak; five-session realized-vol Q75; new max-drawdown Q75. Direction UP iff fitted P(UP)>=0.5. Lower Brier is better.

## Exact 2025 results, N258 (161 UP / 97 DOWN / 23 >=2% declines)

| Arm | BA | UP recall | DOWN recall | Direction Brier | Tail Brier |
|---|---:|---:|---:|---:|---:|
| Constant | 50.00% | 100.00% | 0.00% | 0.2400672 | 0.0822839 |
| Two-UP | 52.51% | 68.94% | 36.08% | 0.2406951 | 0.0822271 |
| Five-session vol Q75 | 50.00% | 100.00% | 0.00% | 0.2440358 | **0.0795049** |
| **New max-drawdown Q75** | **50.00%** | **100.00%** | **0.00%** | **0.2402204** | **0.0820787** |

Max-drawdown high-risk group **8/72=11.11%** actual downside events; low group **15/186=8.06%**.

## Exact 2026 Jan–Sep results, N188 (92 UP / 96 DOWN / 40 >=2% declines)

| Arm | BA | UP recall | DOWN recall | Direction Brier | Tail Brier |
|---|---:|---:|---:|---:|---:|
| Constant | 50.00% | 100.00% | 0.00% | 0.2535882 | 0.1920017 |
| Two-UP | 46.22% | 68.48% | 23.96% | 0.2609284 | 0.1922523 |
| Five-session vol Q75 | 50.00% | 100.00% | 0.00% | 0.2585391 | **0.1882070** |
| **New max-drawdown Q75** | **50.00%** | **100.00%** | **0.00%** | **0.2545877** | **0.1908302** |

Max-drawdown high-risk group **22/112=19.64%** actual downside events; low group **18/76=23.68%**. The conditional ranking observed in 2025 reverses in 2026, so the high-drawdown flag is not stable across inspected years.

## Interpretation and scientific gate
The new candidate improves downside Brier relative to constant only marginally (2025 -0.0002052; 2026 -0.0011715), **loses to the already-tested five-session volatility arm in both years**, worsens direction Brier relative to constant in both years, and predicts UP for every test row (DOWN recall 0%). This is **not a forecasting advancement**. Existing two-UP and volatility comparisons were repeated on equal sample solely as required controls, not a new search.

No evidence of a certified source firstprint at the 09:00 decision point. 2025/2026 have been repeatedly inspected, are not independent holdouts, and 3-session labels overlap. Do not use nominal per-day significance tests or bank P&L claims. Keep **2027 prospective, issue-before-outcome, source-vintage-certified** evaluation with actual bank bid/ask before any trading recommendation. The native H3 daily-mean model has a different target and was intentionally not ranked against this clock-specific label.

**Final:** This attempt does not meet the user-facing meaningful-progress notification threshold. Store the negative result to prevent duplicate work; continue researching other timestamp-verifiable hypotheses without changing production.
