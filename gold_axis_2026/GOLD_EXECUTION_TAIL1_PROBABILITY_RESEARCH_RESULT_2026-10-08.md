# GOLD OVERNIGHT TAIL PROBABILITY / DIRECTION SEPARATION — 2026-10-08

**Status:** COMPLETE REPLAY / PROMISING 2024–2025 PROBABILISTIC RISK SKILL / 2023 WEAK / NOT CONFIRMATORY OR DEPLOYED  
**Task:** XAU/USD magnitude risk for 17:00 Istanbul -> next eligible 09:00 Istanbul, computable after *today's* 09:00 source-ready previous-night prices.  
**Frozen directional baseline:** PRAMV V1 is untouched. Risk probability ≠ UP/DOWN prediction.  
**Input authority:** `GOLD_EXECUTION_DUAL_HAZARD_ROWS_2026-10-08.csv`, computed from preceding 5/20/60 fully matured overnight target returns.  
**New code:** `tools/gold_execution_tail_probability_calibration_20261008.py`  
**Actual chronological predictions:** `GOLD_EXECUTION_TAIL1_PROBABILITY_PREDICTIONS_2026-10-08.csv`  
**Actual summary:** `GOLD_EXECUTION_TAIL1_PROBABILITY_METRICS_2026-10-08.csv`

## 1. Research question and leakage-safe timing

Prior work found in 2025 that a fixed high-volatility alarm caught six of seven ≥2% absolute overnight movements (with 95/254 warning dates), but very small event counts make this claim fragile. The *better-powered outcome* is `TAIL1 = I(|r_{17->09}| >= 0.01)`, with 15 events / 196 scored 2023 dates, 24/259 in 2024 and 43/254 in 2025.

At date t, available source features are **only previously completed overnight returns** r_{t-1}, ..., included in `risk_score_t=sqrt(.5*RV5_t^2+.3*RV20_t^2+.2*RV60_t^2)`. This head can be evaluated after today's 09:00 historical quote is received and validated, unlike the unchanged 17:00 PRAMV, which consumes late half-hour bars. Do not treat 09:15 as an approved vendor source-ready time until latency is confirmed.

We test *risk magnitude probability* `P(|overnight log return| >= 1% | prior matured risk state)`, NOT the label sign.

## 2. Chronological probability challenger

- Input: log of the one-dimensional, already frozen three-horizon score.
- Estimator: regularized logistic link with fitted intercept, single slope and slope L2 penalty=5.
- First 120 earlier **risk-scored** dates are history-only; predictions begin in the later portion of 2023 (after the underlying 60-night risk-score warm-up). For each 2023–2024 date, train on all earlier matured risk-scored target labels (strictly prior date; no current 17:00->next09:00 target), a chronological/prequential design.
- For each 2025 date, freeze the estimator's training sample to exactly the 455 2023–2024 risk-scored rows. No 2025 outcome enters the 2025 model *parameters*.
- Baseline forecast: `p0 = (1 + prior observed TAIL1 count)/(2 + prior eligible sample size)`, i.e. smoothed historical incidence, computed from exactly the same maturation-compliant sample.
- Prediction file contains 589 evaluation rows (2023=76, 2024=259, 2025=254), forecast probability, baseline probability, number of training rows, realized target, and date. High-risk alarm `Q80` and this probability challenger are separate projects: choosing a probability threshold on 2025 is NOT allowed.

## 3. Brier/log-loss comparison (lower better)

| Evaluation | N / events | Logistic Brier | Same-history base Brier | Improvement base minus model | Logistic log-loss | Base log-loss |
|---|---:|---:|---:|---:|---:|---:|
| 2023 prequential warm-up tail | 76 / 9 | 0.109287 | **0.107361** | **-0.001926** (worse) | 0.39675 | **0.38410** |
| 2024 prequential | 259 / 24 | **0.083590** | 0.084407 | +0.000817 | **0.30548** | 0.31081 |
| 2025 retrospective locked-parameter transport | 254 / 43 | **0.139291** | 0.147317 | **+0.008026 (~5.45% relative)** | **0.45048** | 0.48845 |

2025 actual event incidence 43/254=16.93%, while the frozen regression averages forecast probability ~10.68% vs historical-rate mean 8.75%. The model better recognizes increased risk but **remains under-calibrated under the 2025 regime change**. Brier improvement ≠ profitable bank trading.

An exploratory 5-observation circular moving-block bootstrap on the *fixed* 2025 paired per-origin Brier difference, 3,300 draws, yielded ~95% percentile bounds **[+0.00253, +0.01479]** for `base Brier minus model Brier` (2024 [-0.00086,+0.00271], 2023 [-0.00493,+0.00124]). This does NOT correct for hypothesis/variant selection and the previously reviewed 2025 archive. The 2025 interval is supportive of historical within-archive differentiation, NOT a pristine prospective superiority guarantee.

**Failure flag:** The expanding fitted probability ranking has 2023 tail1 AUC ~0.391 on its **76 eligible 2023 dates**; the raw multi-horizon score on these **same 76 dates** has AUC ~0.398. The 0.632 score AUC above is measured on the different, earlier-inclusive population of **196** post-risk-warm-up dates and cannot serve as its common-row comparator. The main problem is a late-2023 regime-specific *reversed* relationship between magnitude score and >1% outcome on the probability model's selected period, not merely a chronological calibration artifact. Do NOT promote without robust regime investigation. Do NOT promote the probability challenger without early-regime repair and later unopened validation.

## 4. Cross-year rank evidence, complexity ablation

Pre-fitted **raw multi-horizon volatility risk score**, without probability calibration, separates ≥1% movements more consistently:

| Year | Raw multi-horizon ROC-AUC | 20-night RV-only ROC-AUC | Block-5 bootstrap 95% interval, multi-horizon |
|---|---:|---:|---:|
| 2023 | 0.632 | 0.649 | 0.496–0.751 |
| 2024 | 0.625 | 0.607 | 0.491–0.753 |
| 2025 reviewed retrospective | 0.658 | 0.663 | 0.553–0.752 |

Across all three years the AUC is pointwise >0.62, but 2023 and 2024 yearwise bootstrap intervals include chance, and the multi-horizon score is not proven better than 20-night RV. It is a *rank-based early-warning research signal*, not a confirmed trading signal.

An exploratory online-label-shift corrective to the 1D probability model mixes half of the logistic p with half of a 30-date recent tail incidence rate shrunk by 20 equivalent historical observations. This gives Brier 2024 **0.083173** and 2025 **0.138971**, slightly improving over their original logistic Briers. However 2023 remains inferior to the historical-rate baseline (0.109000 vs 0.107361), and a 12-variant online window/shrinkage sweep inspected already-opened 2025 outcomes. **Do not promote this online correction**; it is an explicitly data-snooped exploration and needs a fresh fixed challenger test.

A different adaptive *rank* alarm using only prior 60 risk scores' 80th percentile, as opposed to the original 2023–2024 static cutoff, yielded (with additional 60-score warm-up) 2024 **3/5** ≥2% events caught in 50 alerts vs static **1/5 in 68**; 2025 **5/7 in 54** vs static **6/7 in 95**; 2023 only 0/2 tail events in remaining 136 rows. This improves alarm-budget economy in 2024 and 2025 but not rare-event recall everywhere. It too is an exploratory risk–coverage tradeoff, NOT final selected policy.

## 5. Direction of tail events: separate falsification, not a concealed forecast

Use *original origin-known* standalone overnight M4 and PAIR forecast directions on the same future-event rows; this is **ex-post diagnostic on true tail rows**, not an actionable policy that knows tomorrow's move size.

| Year | Actual >=1% overnight events | M4 correct direction | PAIR correct direction |
|---|---:|---:|---:|
| 2023 post-warm-up | 15 | 6/15 = 40.0% | 11/15 = 73.3% |
| 2024 | 24 | 11/24 = 45.8% | 10/24 = 41.7% |
| 2025 archive retrospective | 43 | 20/43 = 46.5% | 20/43 = 46.5% |

The 2023 PAIR apparent success is NOT transported. The tested class-balanced overnight direction heads have **no replicated useful conditional direction skill on the big-move subset**. In 2025, ≥2% events are just 5 UP and 2 DOWN; an 'always UP' tail guess gets 5/7 but has no bidirectional skill. Do not turn absolute volatility warnings into buy/sell direction orders.

Additional independent information challenge: use existing matured 09:00–17:00 **daytime realized return** `LIT_DAY0_EXEC_0900.actual_ret` at its next ready timestamp as a sign proposal for 17:00→09:00. On the *overlapping DAY/overnight* records, same-sign probabilities were **82/194=42.3%** in 2023, **131/259=50.6%** in 2024, **102/217=47.0%** in 2025. Simple daytime continuation is falsified; day-to-night reversal also fails multi-year replication. DAY source completeness is lower than overnight source completeness, requiring exact-common row comparisons and a verified last completed 16:45–17:00 bar timestamp. Any 17:00 update must be calculated only after bar close and cannot assume an executable quote at the just-observed 17:00 open.



### 5A. Adaptive direction-expert challenger: independently falsified

Instead of hard voting, also tested financial online-learning/decision-theory challenger: **exp-weighting** existing M4 and PAIR direction probabilities according to *previous matured* Brier losses; last 60 dates, one global stream and a separate volatility-risk-conditioned 60-date stream. Neither uses the target overnight return at its own origin. See:

- `tools/gold_execution_tail_direction_expert_audit_20261008.py`
- `GOLD_EXECUTION_TAIL_DIRECTION_EXPERT_METRICS_2026-10-08.csv`

| Direction method | 2023 high-vol BA / N | 2024 high-vol BA / N | 2025 high-vol BA / N |
|---|---|---|---|
| Standalone M4 | 52.22% / 24 | 50.70% / 68 | **55.33% / 95** |
| Standalone PAIR | 42.22% / 24 | 50.48% / 68 | 46.89% / 95 |
| Equal M4+PAIR probabilities | 46.67% / 24 | 51.26% / 68 | 53.56% / 95 |
| Last-60 Brier Hedge | 56.67% / 24 | 49.39% / 68 | 47.11% / 95 |
| Risk-state-specific Brier Hedge | 46.67% / 24 | 47.78% / 68 | 52.56% / 95 |

The simple equal mixture changes the results but does not improve all years. The 60-day online hedge actively worsens 2024 and 2025 risk-conditioned direction. No method passes cross-year superiority; **none is promoted**. This is another demonstration that magnitude predictability and tail-direction predictability are separate targets, and adding models does not automatically add independent directional evidence.

## 6. Critical governance correction: macro calendar is NOT covered for 2025

An independent scan of `GOLD_MACRO_EVENT_LEDGER_RAW_V1_2023_2025.csv` reveals:

| Type | 2023 recorded releases | 2024 | 2025 |
|---|---:|---:|---:|
| FOMC | 8 | 8 | **0** |
| NFP / AHE / unemployment each | 12 | 12 | **11** |
| CPI | 12 | 12 | **10** |

Thus previously generated `upcoming_fomc=0` in 2025 is **NOT** proof that FOMC does not occur. The Federal Reserve's official 2025 calendar lists eight regularly scheduled FOMC meetings (https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm). Lower 2025 counts for NFP/CPI also require reconciliation, but **do not automatically prove missing publications**: BLS documents publication delays/cancellations and revised schedules during the 2025 lapse in appropriations (https://www.bls.gov/bls/2025-lapse-revised-release-dates.htm). Even non-null `upcoming_fomc` field is NOT a source-completeness certificate. The earlier `risk_vol OR calendar` combined '2025 6/7 and pooled 10/14' descriptive findings **cannot be promoted or claimed PIT-complete**, and are now **QUARANTINED**. Explicitly re-audited the algorithm and updated `GOLD_EXECUTION_DUAL_HAZARD_ROWS_2026-10-08.csv` to leave the combined/calendar outputs unknown for the entire incomplete 2025 calendar year. Volatility-only score and its 2025 6/7 retrospective finding are unaffected.

Even 2023–2024 release counts alone do not demonstrate official schedule publication as-of the morning issue or full surprise-source PIT readiness. Under no circumstances move a 17:00-released surprise into a 09:00 forecast.

## 7. Scientific decision and next requirements

**Positive research advancement:** 2025 single-input PIT-order magnitude probability Brier and log-loss improve against the chronological historical-incidence benchmark, with slightly positive 2024 prequential changes and consistently >0.62 annual *raw-risk-score* event ranking AUC. This shifts the work from chasing binary sign accuracy on <100 days to probabilistic risk ranking on ~250 days, before the bank's trade cutoff.

**Binding limits:** The 2023 calibration model performed worse than its same-history simple benchmark; 2025 was already visible during design; extreme direction remains unsolved; bank instruments have spreads, inventory constraints and liquidity. No new UP/DOWN model is promoted, no trading profit claimed, no prospective OOS validation claimed.

**Next mechanistic avenues requiring source-ready evidence:** build official PIT event calendar, daylight/DST-correct pre-09 surprise schedule; obtain COMEX gold futures / USD real yields / USD index / gold ETF flow ready before source-origin; compare signed tail-risk against single-price history at identical labels/dates; use a **proper price-quote execution test** and a prospective locked study. PRAMV V1 remains frozen. The DAY 09:00→17:00 target remains independent.

## 8. Literature

- Corsi (2009), *A Simple Approximate Long-Memory Model of Realized Volatility*, Journal of Financial Econometrics 7(2), doi:10.1093/jjfinec/nbp001.
- Sobti, Sehgal & Ilango (2021), *How do macroeconomic news surprises affect round-the-clock price discovery of gold?*, International Review of Financial Analysis 78, doi:10.1016/j.irfa.2021.101893.
- Hansen (2005), *A Test for Superior Predictive Ability*, Journal of Business & Economic Statistics 23(4), doi:10.1198/073500105000000063.
