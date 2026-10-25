# TR09 H3 — matured-60 prequential calibration: executed, cross-year negative result (2026-10-25)

**Verdict: REJECT for model promotion. No user notification: preregistered cross-year acceptance failed.** New read-only Neon experiment actually executed and monthly as-of checks independently recomputed; prior studies and canonical manifest unchanged.

## Provenance and as-of constraints
- Original checked branch HEAD `8f81977875e4be99b7b24147333d2885c1ed6fb9`; manifest blob `279dae0b2d5694593adda076d644a5d186241304`. Current branch HEAD immediately before result write `6943da81ca04d4ae1616dd8a2f798eff732ce252`. No prior artifacts overwritten.
- Preregistered **before outcome SQL**: `GOLD_TR09_20261025_MATURED60_ONLINE_CALIBRATION_PREREG.md`, commit `ca5b345440f864c48a254905e77c053489e44553`.
- Exact executable read-only PostgreSQL SQL committed **before execution**: `tools/gold_tr09_20261025_matured60_online_reproduce.sql`, commit `6943da81ca04d4ae1616dd8a2f798eff732ce252`. Actually executed via Neon project `winter-art-94880101`, `public.gold_research_histdata_xau15m_candidate`.
- 09:00 Europe/Istanbul HistData reference: 08:45–09:00 completed M15 close, `native_minute_bars=15`. 3 NEXT eligible weekdays target 09:00; explicitly enumerated holiday exclusions and 2026-09-25 missing quote outage. All five previous 09:00 prices, origin, and target required. **Historical vendor firstprint not proven** (backfill retrieved 2026-10-08), so retrospective research only, no claim of actionable real-time execution or source-certified PIT.
- Training 2023–24 **N496**, target<=2024-12-31, training >=2% downside events **27**, train base tail probability **0.0562248996**. Frozen 5-session volatility Q75 **0.010206552832574104**, max drawdown Q75 **0.0176338965292272**. Online model at each origin uses most recent **60 historical rows whose 3-day target_date is STRICTLY BEFORE origin d**; 20 fixed training-prior pseudo-observations. Independent monthly SQL verification: **all 21 test months have 60 matured observations per issue and 0 as-of maturity violations**; original SQL separately aggregates all metrics. 2025/26 outcomes never included before maturity.
- All six arms evaluated on **identical qualified rows** in each year. Frozen comparators: constant, two-UP, volatility Q75, max-drawdown Q75, calendar>=5. New online arm has an additional *legitimate, already-matured historical label* information budget compared with frozen arms. Do not misrepresent as identical information sets.

## Same-row exact scores
Balanced accuracy (BA) = (UP recall+DOWN recall)/2; Brier lower is better.

| Year | Arm | N | BA | UP recall | DOWN recall | UP Brier | >=2% DOWN Brier |
|---|---|---:|---:|---:|---:|---:|---:|
| 2025 | Constant | 258 | 50.0000% | 100.0000% | 0.0000% | 0.2400672 | 0.0822839 |
| 2025 | Two-UP | 258 | 52.5133% | 68.9441% | 36.0825% | 0.2406951 | 0.0822271 |
| 2025 | Vol Q75 | 258 | 50.0000% | 100.0000% | 0.0000% | 0.2440358 | **0.0795049** |
| 2025 | MDD Q75 | 258 | 50.0000% | 100.0000% | 0.0000% | 0.2402204 | 0.0820787 |
| 2025 | Calendar>=5 | 258 | 50.0000% | 100.0000% | 0.0000% | 0.2401858 | 0.0821760 |
| 2025 | **NEW matured60** | **258** | **47.2850%** | **83.2298%** | **11.3402%** | **0.2448019** | **0.0843355** |
| 2026 Jan–Sep | Constant | 188 | 50.0000% | 100.0000% | 0.0000% | 0.2535882 | 0.1920017 |
| 2026 Jan–Sep | Two-UP | 188 | 46.2183% | 68.4783% | 23.9583% | 0.2609284 | 0.1922523 |
| 2026 Jan–Sep | Vol Q75 | 188 | 50.0000% | 100.0000% | 0.0000% | 0.2585391 | 0.1882070 |
| 2026 Jan–Sep | MDD Q75 | 188 | 50.0000% | 100.0000% | 0.0000% | 0.2545877 | 0.1908302 |
| 2026 Jan–Sep | Calendar>=5 | 188 | 50.0000% | 100.0000% | 0.0000% | 0.2531117 | 0.1914909 |
| 2026 Jan–Sep | **NEW matured60** | **188** | **57.0199%** | **61.9565%** | **52.0833%** | **0.2512439** | **0.1767554** |

Actual labels: 2025 UP161/DOWN97, severe downside23; 2026 UP92/DOWN96, severe downside40. 2026 online tail Brier improves versus vol by 0.0114516 (~6.08%) and direction BA +7.02pp versus constant; but 2025 online tail Brier **worsens** versus vol by 0.0048306, versus constant by 0.0020516, and direction BA -2.72pp versus constant. **Preregistered both-years acceptance fails.**

## Independent monthly verification and temporal diagnostics
Second Neon read-only query (reconstructs original source CTEs, computes 2025/26 month-specific Brier and counts and exposes max prior target_date) returned: 2025 12 monthly groups N sum 258, 2026 Jan–Sep 9 groups N sum188, each min/max mature history=60, **zero** rows with `max_label_target>=origin_d`. Selected actual-vs-average-predicted tail rates: 2025 April 5/21 vs predicted .0551; October 6/23 vs predicted .0347; 2026 March 10/22 vs predicted .1504, June 10/22 vs predicted .2027, July 1/23 vs predicted .2266. This shows slow lagging response to abrupt risk transitions and overlapping 3-day labels; no independent statistical claim.

## Scientific decision
- 2025 deterioration disqualifies promotion even though 2026 retrospective looks better. Do not tune window, prior weight or thresholds on repeatedly inspected 2025/2026 to rescue result; no automatic alert/trading switch.
- Three-day overlapping labels mean effective sample is smaller than row counts. Original HistData source vintage / firstprint at 09:00 remains unverified, and bank executable BID/ASK plus spread absent. These are non-certified backtest references.
- **2025/2026 are not independent holdouts** after repeated inspection. Required 2027 prospective issue-before-outcome with certified vendor timestamps, 09:00 executable quote, 3-day label maturity and unchanged model selection remains binding.
- No canonical manifest changes, no prior result replacement; negative study retained to prevent redundant future research.
