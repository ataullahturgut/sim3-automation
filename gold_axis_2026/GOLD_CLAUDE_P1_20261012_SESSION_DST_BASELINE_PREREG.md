# CLAUDE P1 — Session / US-DST conditional baselines for exact-clock XAU/USD DAY and OVN returns: PREREGISTRATION

Date: 2026-10-12. Investigator: Claude (independent of GPT-6; GPT-6 P1 branch NOT read before this
result is frozen). Protocol: `GOLD_XAUUSD_TWO_INDEPENDENT_RESEARCHERS_PRIORITY_PROTOCOL_20261012.md`
(PR #93). Written and committed **before** any target return, score or model output is computed.
Only source coverage (bar counts per year) and the daily quote-blackout clock were inspected.

## Question
Does information that is known at the decision time and is *structural* — US daylight-saving regime,
weekday, and the returns of completed pre-issue trading segments (previous US session, Asian
session, previous window) — forecast the post-decision XAU/USD log return better than the
random walk (zero return) and the historical intercept? If not, the output of P1 is the set of
**correct baselines** (per year, per DST regime) that every later stage must beat.

Novelty vs prior work: R67 used H3 + prior_day / prior_overnight / pre_close_day as a *direction*
classifier conditioned on H3; R73/R73B used cross-market residuals; BSC-8 used bid/ask pressure.
None tested US-DST regime or the CME-daily-break segmentation, and none scored log-return MSE
against both RW and intercept. P1 fits no H3 and uses no other market.

## Data (read-only Neon)
- 2020–2025: `gold_research_evduka_xau15m_bidask_candidate`
  (`EVTRADINGLABS_DUKASCOPY_DERIVED_XAUUSD_M15_BIDASK_2020_2025_V1`, historical, non-PIT).
- 2026: `gold_research_dukascopy_2026_direct_m1_m15_bidask_v2` (direct Dukascopy; `m1_matched`=0 on all
  rows). **Separate source cohort**, reported separately, never pooled with 2020–25 in any test.
- Price = M15 mid close (bid_close+ask_close)/2; require 0<bid≤ask. `bar_start_utc` is the bar START;
  the close of the bar starting at T is the price at T+15 min.

## Clocks (Europe/Istanbul, UTC+3) and targets
- `P(c)` = mid close of the bar starting at c−15 min (the price at clock c).
- **DAY(d)**: decision 08:45, `y = ln P(d,16:45) / P(d,09:00)`, Mon–Fri.
- **OVN(d)**: decision 16:30, `y = ln P(d+1 calendar day,09:00) / P(d,16:45)`, Mon–Thu.
- Window eligibility identical to H3A (PR #91): DAY needs all 31 bars 09:00..16:30 starting contiguous
  (plus bar 08:45 for the origin); OVN needs 61 bars 16:45..08:45 with exactly one 75-minute daily
  quote blackout and otherwise 15-minute steps. Failing windows are excluded, not filled.
- Price-level forecast `P̂ = P_origin · exp(ŷ)`; level error in USD/oz.

## Information set and latency
Features may only use prices at clocks ≤ decision − 15 min (DAY: ≤ 08:30; OVN: ≤ 16:15), i.e. a
15-minute receipt buffer beyond bar completion. Calendar facts (weekday, America/New_York DST
offset) are known in advance.

## Pre-issue features (frozen)
- `dst` = 1 if America/New_York is on EDT on the decision date, else 0.
- Blackout = the single ≥75-minute quote gap after 16:45 (the CME daily break; 00:00 TR under EDT,
  01:00 TR under EST). `Pb` = last mid close before the blackout.
- DAY features: `f_us = ln Pb / P(d−1,16:45)` (previous US/late session),
  `f_asia = ln P(d,08:30) / Pb` (reopen + Asia + early London),
  `f_prevday = ` previous eligible DAY target (if the previous weekday DAY is ineligible: 0 and flag).
- OVN features: `g_daysofar = ln P(d,16:15) / P(d,09:00)`, `g_prevovn = ` previous eligible OVN target
  (0 and flag if missing).
- Feature rows with a missing segment price are excluded for M2/M3 *and* their baselines on the
  matched-row comparison (all comparisons row-matched).

## Models (frozen; re-estimated daily, expanding, on rows with decision date < current date)
- **RW**: ŷ = 0.
- **INT**: ŷ = mean of all prior eligible targets of the same window type from 2020-01-01.
- **M1 CAL**: shrunk cell mean, cells = dst × weekday: ŷ = m_all + n_c/(n_c+100)·(m_c − m_all).
- **M2 SEG**: ridge, alpha=10, standardized features (DAY: f_us, f_asia, f_prevday; OVN: g_daysofar,
  g_prevovn), unpenalized intercept.
- **M3 SEG×DST**: M2 features + dst + each feature×dst, same ridge.
- Minimum 250 prior training rows before the first forecast; 2020–22 are warm-up only (not scored).
- Direction: sign(ŷ) (ŷ=0 → UP). Probability p_up = Φ(ŷ/σ̂), σ̂ = expanding std of y.
  Baseline probability **PRIOR** = expanding UP fraction; class baseline **ALWAYS-UP**.
- 2025 and 2026 continue the same daily expanding re-estimation (no tuning, no refreezing choice).

## Primary outcome and gate (per target; 3 models × 2 targets)
- Primary loss: squared log-return error. Comparators: RW **and** INT.
- A model is **SUPPORTED** only if: (a) MSE < RW and MSE < INT in **each** DEV year 2023 and 2024
  separately; (b) pooled DEV 2023–24 one-sided Diebold–Mariano (Newey–West, 5 lags) p < 0.05 against
  each of RW and INT, **Holm-corrected over all 12 tests** (3 models × 2 targets × 2 comparators);
  (c) no sign reversal of the MSE improvement in opened 2025 (diagnostic, not a pass).
- Otherwise the P1 classification is **BASELINE_ONLY** (no information beyond baselines).

## Secondary (reported, not gating)
- Per year 2023, 2024, 2025, 2026(separate source): N, R²_OS vs RW and vs INT, MAE return, price-level
  MAE/RMSE (USD), accuracy, balanced accuracy, UP and DOWN recall, log-loss vs PRIOR, 3-month
  moving-block bootstrap 95% CI of MSE difference.
- Matched direction comparison against the previous best exact-clock model on identical dates:
  R67 `new_pred` and `h3bit` (`GOLD_R67_20261012_H3_AS_DAY_AND_OVN_CONDITIONER_2023_2026_ROWS.csv`):
  corrected / broken decision counts, exact McNemar.
- **Baseline atlas** (descriptive, the main P1 deliverable): per year × target × dst regime: N, mean
  return (bp), std, UP rate with Wilson 95% CI; plus mean return and UP rate of the four segments
  (prev-US, Asia, DAY, OVN). These are descriptive; no rule is selected from them.

## Honesty rules
- No threshold, window, alpha or cell definition changes after seeing results; negative result is
  committed as such. Magnitude/variance results are not presented as direction skill.
- No profitability claim (no bank quotes). 2025/26 are opened retrospective periods, not holdout.
- Neon is read-only (`SET TRANSACTION READ ONLY`); outputs are small derived CSV/JSON in this branch.
