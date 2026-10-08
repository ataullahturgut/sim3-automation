# Gold 2026: executed Bayesian competing-event state inference and audited scientific verdict
Date 2026-10-08. This is a retrospective, already inspected 2026 source-qualified study, NOT prospective investment advice, not an implementation of continuous-time first-passage hazard with time-to-event.

## What is actually novel relative to our previous models?
Not CatBoost/HGB/logistic hyperparameter tuning. Three different mathematical representations were materially implemented and audited:
1. **16-bar multiscale normalized path geometry** queried through nearest-41 case-based historical analog memory; variant also conditions on preorigin realized volatility + publication-lagged GVZ.
2. **Path-dependent event targets** rather than final 16h close: observed BID M15 first passage of ±0.5% barriers; outputs UP_FIRST, DOWN_FIRST, NO_HIT, with censoring for large missing source chunks. No intrabar trade touch, no execution fill inferred.
3. **True Dirichlet–multinomial Bayesian online changepoint detection (BOCPD)** with run-length posterior and fixed prior alpha=(1,1,1), constant hazard 1/63 observed qualified night, max252 observations, updating only after past event outcome matures. Probability forecasts before next 17TR are posterior mixture over regime run lengths. Neither new regression nor static state labels are used. Comparators include fixed previous-calendar-year first-passage climatology, naive trailing-63 Dirichlet estimates and regime-path CBR on strictly identical dated outcomes.

Literature: Adams and MacKay 2007 arXiv 0710.3742 and online order-flow regime literature (Quantitative Finance 2024 doi:10.1080/14697688.2024.2337300); shapelets/multiscale laws (Scientific Reports 2025 doi:10.1038/s41598-025-25667-0); triple-barrier labeling (Mathematics 2024 doi:10.3390/math12050780). Literature is methodological motivation, not evidence of our gold gains.

## Bayesian model: executed same-row event probability results
Metrics from `GOLD_EXECUTION_2026_BAYESIAN_COMPETING_EVENT_BOCPD_20261008_METRICS.csv` and 1500-calendar-month-block uncertainty `GOLD_EXECUTION_2026_BAYESIAN_COMPETING_EVENT_BOCPD_20261008_MONTHBLOCK.csv`. Lower multiclass Brier is better; proper 3-event probabilities (not UP/DOWN BA).

| Cohort | N | Last-year Brier | BOCPD Brier | Trailing63 Bayes Brier | Regime-path CBR Brier |
|---|---:|---:|---:|---:|---:|
| 2023 |187|0.66010|0.65461|0.65419|**0.64194**|
| 2024 |189|0.66905|0.67102|0.66961|**0.66602**|
| 2025 |192|0.68565|**0.63228**|0.65525|0.66538|
| 2026 same-upstream mirror Jan–Aug20 |97|0.59182|0.56030|**0.55366**|0.56250|
| 2026 direct first-party native Jan–Oct07 |72|0.59353|0.56488|**0.55696**|0.55777|

BOCPD improvement relative to **fair prior-year climatology**, 1500 paired month-block descriptive intervals: 2025 **+7.78%**, 95% **[+0.90%, +14.26%]**; 2026 mirror **+5.33%**, 95% **[+0.51%,+9.71%]**; direct **+4.83%**, 95% **[-2.02%,+11.25%]**. 2023 +0.83%, 2024 -0.29%, both intervals straddle zero. This supports causal as-of sequential EVENT prevalence adjustment in specific already-inspected 2025–26 settings, but **not that BOCPD specifically beats a simpler 63-observation Bayes rate estimate**, which is numerically better on both 2026 test populations. Two 2026 populations overlap (NOT independent), source missingness and post-study repeated-hypothesis inflation not removed by descriptive CIs.

BOCPD 2026 mirror hard three-class recalls: **NO_HIT 0%**, **UP_FIRST 14.29%**, **DOWN_FIRST 82%**; 2026 direct **NO_HIT 0%**, **UP_FIRST 12.90%**, **DOWN_FIRST 72.97%**. This is a **strong DOWN-first skew**, not successful balanced outcome prediction. In 2026 median first 0.5% crossing is common, and fixed barrier class priors drift severely (2026 mirror N97: NO_HIT 5.15%, UP_FIRST 43.30%, DOWN_FIRST 51.55% vs 2023 N187 NO_HIT44.92%, UP_FIRST28.88%, DOWN_FIRST26.20%). 2026 index endpoint UP/DOWN is not equivalent to first passage.

## Correct scientific action from here
- **Retire claim of any approved 16h signed directional champion.** No bank spread returns or action policy tested; no securities recommendations justified. The modest endpoint path-memory BA~57.52/60.31 was non-significant vs HGB and degraded 2024.
- **Promote only a research hypothesis, not a production model**: a joint competing-risk *time-to-first-passage* process with volatility-relative rather than fixed 50bp barriers to factor out simple scale regime, cause-specific hazard and probability of NO_HIT conditional on risk and macro-calendar. Work at true origin 17TR and only previously published point-in-time VIX/GVZ/rates/macro; absolutely no later Fed release surprises at 17 if published afterwards.
- A bank cannot be traded overnight under the user's constraints, therefore first passage is a **17:00 hold-exposure/risk** quantity, not proof of ability to transact at barrier. Real bank live BID/ASK spread, commissions, quote latency and ability to buy/sell at 09/17 must be captured.
- Next fully prospective **later uninspected cohort** needed for model acceptance; do not retune 2026 and rebrand it untouched. Follow strict source/feature maturity and paired proper-scoring measures. All 2025 and 2026 cohorts inspected. No A/B statistically proven return.

## Immutable evidence
- Prereg `GOLD_EXECUTION_2026_BAYESIAN_EVENT_BOCPD_PREREG_20261008.md`
- Source & pair definition `GOLD_EXECUTION_2026_TRAJECTORY_ANALOG_FIRSTPASSAGE_PREREG_20261008.md`, `GOLD_EXECUTION_2026_NONPARAMETRIC_COMPETING_FIRSTPASSAGE_PREREG_20261008.md`
- Complete 3-event sampled test `GOLD_EXECUTION_2026_THREE_WAY_FIRSTPASSAGE_CBR_20261008_METRICS.csv` and `_LASTYEAR_MONTHBLOCK.csv`
- BOCPD implementation `tools/gold_execution_2026_bayesian_event_bocpd_20261008.py`; final source-safe `GOLD_EXECUTION_2026_BAYESIAN_COMPETING_EVENT_BOCPD_20261008_SUMMARY.json`, `_METRICS.csv`, `_MONTHBLOCK.csv`.
- Parent report `GOLD_EXECUTION_2026_PATH_GEOMETRY_AND_FIRSTPASSAGE_RESEARCH_AUTHORITY_20261008.md`

**Honest conclusion:** the innovative mathematical framing exposed a real volatility/first-passage regime problem and showed limited as-of event-probability adaptation; it did **not** provide a validated UP/DOWN or profitable banking strategy. Exposing that limitation is an experimental result, not a reason to cherry-pick a new HGB.
