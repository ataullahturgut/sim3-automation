# XAU execution 2026: genuinely new representation and event-based research result
**October 8, 2026.** This is a completed retrospective investigation, NOT an accepted 2026 bank execution or future untouched holdout. Main goals: Turkey DAY 09–17 and regular weekday OVERNIGHT 17–next09. DO NOT pool Fri→Monday long weekend.

## 1. Three paradigms examined, two actually executed in this round
Unlike prior logistic/HGB/Ridge variants, (i) **multiscale entire 4h pre-origin price trajectory analogy** with nonparametric nearest case retrieval was actually trained/tested; (ii) **observed first passage of symmetric ±0.5% overnight barriers** was audited and modeled as an explicit 3-outcome competing-event probability, not just closing direction. (iii) Bayesian online changepoint detection remains a literature-grounded follow-up idea **NOT implemented or backtested** in this round; no false BOCPD success claim. Source theoretical motivations: Kurbucz et al., Scientific Reports 2025 doi:10.1038/s41598-025-25667-0 for multiscale time-path representation; Adams/MacKay 2007 arXiv:0710.3742 for causal changepoints; observed first barrier competing risks and financial triple-barrier labels (Mathematics 2024 doi:10.3390/math12050780). These publications DO NOT prove this particular gold pipeline's effectiveness.

## 2. Whole-path direction result (no new logistic/boosting model)
Fixed 41 nearest historical multiscale normalized 16-M15-bar shape trajectories, with 5 effective-count historical prior shrinkage, and variant additionally gated by origin-safe prior 4h realized volatility and lagged GVZ. Frozen pre-2025 / pre-2026 and chronological 2023–24 monthly history. Same priced source and label-days vs original SHAPE_GVZ_HGB (2021 historical-start).
Regular OVN BA results:
| Year/source | N | Original HGB | CBR full-shape only | Regime-conditioned CBR |
|---|---:|---:|---:|---:|
| 2023 |187|49.45%|50.29%|49.68%|
| 2024 |190|54.13%|46.04%|51.18%|
| 2025 |192|53.02%|49.27%|55.74%|
| 2026 same-upstream mirror Jan-Aug20 |97|54.79%|46.13%|57.52%|
| 2026 direct-first-party M1 Jan-Oct07 |72|56.56%|45.94%|60.31%|
2025 regime analogue DOWN recall 55.81%; 2026 mirror 46.15%; direct 42.50%. 2026 mirror regime analog vs original source-matched HGB rescued 16 days and broke 13 (McNemar p≈0.711), direct rescued15 and broke12 (p≈0.701), both **NON-SIGNIFICANT**. Worse performance in 2024; not a champion, no online bank action.
Audited source `GOLD_EXECUTION_2026_FULL_TRAJECTORY_CBR_20261008_SUMMARY.json`; year scores `GOLD_EXECUTION_2026_FULL_TRAJECTORY_CBR_20261008_YEAR_METRICS.csv`; paired `GOLD_EXECUTION_2026_FULL_TRAJECTORY_CBR_20261008_PAIRED.csv`; reproducible code `tools/gold_execution_2026_full_trajectory_cbr_20261008.py`.

## 3. Why 2026 sign-of-close is a weaker stand-alone target
Across fully source-eligible regular overnight price paths, fixed ±0.50% observed M15 BID-close barriers from 17TR entry, no market-closed padded bars interpreted as native:
| Year | Analysed nights | First ±0.5% crossing, rate | Initial first-hit opposite final close direction (among hits) | Nights with BOTH directional threshold crossings |
|---|---:|---:|---:|---:|
| 2023 |198|55.56%|5.45%|0|
| 2024 |197|61.93%|8.20%|4|
| 2025 |198|80.81%|9.38%|9|
| 2026 mirror Jan-Aug20 |127|95.28%|19.83%|20|
| 2026 native direct |103|94.17%|21.65%|17|
Fixed barrier frequencies are mechanically sensitive to volatility scale, so 2026 surge is NOT proven independent behavioral regime; no intrabar tick touch nor stop-loss execution claim. But initial intranight direction vs endpoint decoupling measurably increased. Core `GOLD_EXECUTION_2026_FIRSTPASSAGE_COMPETING_BARRIER_DIAGNOSTIC_20261008_METRICS.csv`; implementation `tools/gold_execution_2026_firstpassage_barrier_diagnostic_20261008.py`.

## 4. First-passage as THREE outcomes: UP_FIRST / DOWN_FIRST / NO_HIT
Genuinely different target and nonparametric probability estimate (not a binary HGB relabel): full path nearest case kernel with/without regime; proper 3-class multiclass Brier (lower=better), logloss, classwise sensitivity.
2026 mirror same-upstream N97 outcome rates NO_HIT 5.15%, UP_FIRST43.30%, DOWN_FIRST51.55%. Stale 2020–25 event prior Brier **0.68509** versus regime-conditioned CBR **0.56250**, 2026 direct N72 0.68487 vs **0.55777**. 2025 N192 stale prior Brier 0.69080 vs regime-conditioned **0.66538**; 2023 0.65681 vs0.64194; 2024 0.66492 vs0.66602 (worse). In 2026 mirror regime analogue recalls: NO_HIT **0%**, UP_FIRST **35.71%**, DOWN_FIRST **60.0%**; macro recall **31.90%**, below random-balanced baseline33.33%. Thus **probability quality improves vs stale historical prior** in inspected 2025/26, but 3-class hard decisions are **NOT robust across all events and years**; no blind validation and no tradable stop-order PnL.

**Critical post-result falsification now separately registered:** long-run stale class priors are an unfairly weak baseline amid extreme 2026 source shift. Compare with previous-year-only climatology on exact same days, 1500 calendar-month block resamples; if improvement disappears, attribute prior benefit to simple event frequency adaptation rather than path geometry. Adversarial protocol `GOLD_EXECUTION_2026_FIRSTPASSAGE_ADVERSARIAL_BASELINE_AUDIT_20261008.md`. Formal outputs `GOLD_EXECUTION_2026_THREE_WAY_FIRSTPASSAGE_CBR_20261008_METRICS.csv`, `_LASTYEAR_MONTHBLOCK.csv`, code `tools/gold_execution_2026_threeway_firstpassage_cbr_20261008.py`. The competitor rerun may still be in progress; do NOT claim that new test passed until its file exists.

## 5. Scientific direction
Stop treating a point estimate of 16h closing sign as the complete financial objective. Distinguish (A) expected absolute risk (previous study's partial measured channel), (B) signed **first-path barrier** risk with volatility-relative boundaries (requires future prereg, not yet implemented), (C) uncertainty / no-trade conditioned on bank spread and inability to trade at night, (D) BOCPD or continuous-time event dynamics using point-in-time macro publication schedule, not future release surprise. Need independent prospective 2027 observations to claim deployment; every 2026 outcome has already been inspected.

**Verdict:** whole-path geometry yields a different and modest 2025/26 sign model but is not validated; first-passage taxonomy exposed material path/endpoint mismatch and a candidate proper-probability improvement compared with stale history; **no trading champion**.
