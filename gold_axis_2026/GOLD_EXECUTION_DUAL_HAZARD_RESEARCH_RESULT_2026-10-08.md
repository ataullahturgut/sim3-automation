# GOLD OVERNIGHT DUAL-HAZARD RESEARCH — 2026-10-08

**Status:** REPRODUCIBLE HISTORICAL FINDING / PROMISING TAIL WARNING, NOT UNTOUCHED OOS OR PRODUCTION  
**Target:** `17:00 -> next eligible 09:00 Europe/Istanbul`  
**Frozen directional baseline:** PRAMV V1, *unchanged*.  
**Input frozen predictions:** `GOLD_EXECUTION_PSF_OVN_PREDICTIONS_2026-10-07.csv`, M4 `ret_target`.  
**Code:** `tools/gold_execution_dual_hazard_tail_audit_20261008.py`  
**Per-origin scores / labels / audit ledger:** `GOLD_EXECUTION_DUAL_HAZARD_ROWS_2026-10-08.csv`.

## 1. Why a new target is necessary

The apparent ~60–63% sign accuracy of PRAMV V1 does not guarantee a positive bank-executable return. On frozen 2025 retrospective signals (N=82):
- correct calls 52/82 = **63.41%**;
- mean *correct-direction* signed overnight log return **+0.0040146** (about +0.401%);
- mean *incorrect-direction* signed overnight log return **-0.0067350** (about -0.674%);
- sum of idealized signed returns **+0.0067098** across all 82 signals, before spreads/delay/fees, NOT a tradable gain;
- empirical break-even correctness at those sample conditional mean move sizes ≈ **62.65%**. Slightly exceeding that threshold leaves little economic value.

This is a loss-magnitude asymmetry and economic-target mismatch, not necessarily a failure of binary direction classification. Asymmetric utility and tail risk must be modeled separately. The original frozen 2025 82-call output is not modified.

The other missing objective: 2025 has **7** overnight observations with absolute target log-return ≥2% among 254 observed 2025 targets. **PRAMV V1 acts on none of the seven**. Of those seven, five are positive and two negative. This is a tail-event blind spot, not evidence that PRAMV's direction is wrong when it acts.

## 2. Cross-disciplinary mechanism: volatility cascades + event hazards

Use an independent *risk* head on all complete target days, orthogonal in purpose to PRAMV direction:
- Corsi-style heterogeneous-memory volatility cascade is the scientific analogue (daily/weekly/monthly component logic), but this is a **fixed HAR-inspired multi-scale score, NOT an estimated canonical HAR-RV model**;
- a separate event-clock hazard state captures scheduled upcoming FOMC events and already released macro surprises; these are origin-time flags, not outcomes;
- the risk head's outputs are **HIGH-RISK / NOT HIGH-RISK**, NEVER UP/DOWN.

For each day t, compute `RV_w(t) = sqrt(mean(r^2_(t-w) ... r^2_(t-1)))` where r is prior completed `17:00 -> next eligible 09:00` XAU overnight log return, for w in {5,20,60}. **Each previous overnight is fully matured by 09:00 before today's 17:00 origin.**

`score(t) = sqrt(0.5*RV_5(t)^2 + 0.3*RV_20(t)^2 + 0.2*RV_60(t)^2)`.

These coefficients are an exploratory, low-capacity mechanism specification, not an optimized/fitted HAR regression. **No current target return may enter its own score.** A 60-target warm-up is necessary: 2023 scored N=196 of 256 (2024 259/259, 2025 254/254). Do not confuse unavailable warm-up with model abstention.

For a single fixed exploratory alert threshold, take the empirical 80th percentile (nearest lower index) of the **455 development risk-score values from 2023–2024 only**, with no use of 2025 scores or labels to set the threshold:
`score_cut = 0.007644177328023349`.

If score >= cutoff, flag HIGH-RISK. Tail events are post-origin evaluation targets, not inputs:
- `TAIL1 = abs(ret_target) >= 0.0100` (absolute **log** return ≥1%);
- `TAIL2 = abs(ret_target) >= 0.0200` (absolute **log** return ≥2%).

## 3. Primary empirical result: historical multi-scale volatility risk alerts

| Year | Risk-scored days | Risk alerts | ≥1% nights caught | ≥2% nights caught | AUC for ≥1% | AUC for ≥2% |
|---|---:|---:|---:|---:|---:|---:|
| 2023 (60-day warm-up) | 196 | 24 (12.2%) | 1/15 | 0/2 | 0.632 | 0.639 |
| 2024 | 259 | 68 (26.3%) | 7/24 | 1/5 | 0.625 | 0.554 |
| **2025 retrospective** | **254** | **95 (37.4%)** | **25/43 (58.1%)** | **6/7 (85.7%)** | **0.658** | **0.770** |

2025 ≥1% alert precision = 25/95 = **26.3%**, compared to 43/254 = **16.9%** unconditional event rate. Precision lift ≈ **1.55×**. The 95 risk alerts are **not 95 profitable direction calls**.

2025 ≥2% nominal random-selection enrichment: selecting 95 of 254 days uniformly at random would catch at least 6 of 7 events with hypergeometric p≈0.01199. This **is not a valid confirmatory p-value**, because 2025 archives were already reviewed during idea generation, there were exploratory model alternatives, and serial dependence is ignored by the hypergeometric null. A 5-target-date moving-block bootstrap of the 2025 extreme-event AUC (3,488 valid resamples, length 5, seeded 20261008) gives roughly 95% percentile interval **[0.609, 0.885]**; rare events make this imprecise.

Independent single-history benchmarks on 2025's same 254 date rows, each using its own 2023–2024 80th-percentile score:
- RV5 alone: AUC(≥2%)≈0.723; catches 5/7 using 96 alerts.
- RV20 alone: AUC≈0.751; catches 4/7 using 86 alerts.
- RV60 alone: AUC≈0.544; catches 4/7 using 122 alerts.
- Equal three-horizon average: AUC≈0.743; catches 5/7 using 102 alerts.
- Multi-horizon composite: AUC≈0.770; catches 6/7 using 95 alerts.

These comparisons are exploratory; an apparent gain of 1 detected rare event is too small to claim that particular weighting is optimal.

## 4. Event-information complement and failure analysis

An exploratory OR rule adds independent calendar warnings when `upcoming_fomc==1` or already available `macro_released==1`. The source-ready event flags must be present; missing event rows are UNKNOWN, not silent negatives. Early source-state completeness remains conditional on the project's PIT source authority.

The directly persisted origin rows also permit a source-unknown-fail-closed calendar audit:

| Year | Volatility-only alarms / ≥2% caught | Volatility OR event scored rows | Volatility OR event alarms / ≥2% caught |
|---|---|---:|---|
| 2023 | 24 / 0 of 2 | 195 | 44 / 1 of 2 |
| 2024 | 68 / 1 of 5 | 259 | 93 / 3 of 5 |
| 2025 | 95 / 6 of 7 | 253 | 110 / 6 of 7 |

Two dates whose calendar flags are unavailable cannot silently be imputed as no-event; they are excluded from the OR policy denominator unless the volatility alarm independently determines the OR outcome. Across 707 calendar-evaluable origin rows, **247** receive a combined alert (34.94%) and **10 of 14** ≥2% tail movements fall on alert dates (71.43%). Tail-event precision is **10/247 = 4.05%**, against base frequency **14/707 = 1.98%** (≈2.04× lift). A *nominal*, independent-uniform-day hypergeometric tail chance is ≈0.0055, but **must not be used as a confirmatory p-value**: the result was discovered after examining archives, alert choices were inspected retrospectively, and market dates are serially dependent. Despite positive descriptive lift in all three years, the extreme-event samples (2/5/7) are too small to promote this as a reliably transferable alarm.

Treat this as a **secondary mechanism challenge**, not as a promoted result. Its economic motivation is to distinguish two different kinds of extreme movement: volatility-clustered repricing and announcement-related jumps.

2025 seven ≥2% night moves and initial multi-scale warning:
- 2025-04-10 **+2.53%**: warned, no PRAMV;
- 2025-04-17 **+2.13%**: warned, no PRAMV;
- 2025-04-21 **+2.16%**: warned, no PRAMV;
- 2025-04-30 **−2.17%**: warned, no PRAMV;
- 2025-10-16 **+3.66%**: warned, no PRAMV;
- 2025-11-12 **+2.11%**: warned, no PRAMV;
- 2025-12-30 **−2.30%**: NOT warned, no PRAMV.

These are ex-post outcomes and should not be treated as forecast information at the historical issue time. Note only 2/7 were negative, so capturing 6/7 extreme absolute movements is **not** evidence of a strong crash-specific DOWN predictor.

## 5. Joint information coverage, economic caveat, and failed promotion gate

On 2025's 254 original PSF dates:
- PRAMV V1 directional signals: 82 (correct 52, BA 63.41%);
- volatility HIGH-RISK alerts: 95 (6/7 extreme nights detected);
- overlap of these sets: 28;
- union: **149/254 = 58.66% days with at least a directional signal or a tail warning**.

**The union is NOT directional forecast coverage**, and risk warnings must never be counted as correct UP/DOWN calls.

Retrospective *unpromoted* stress experiment: suppress original PRAMV direction trades when the independent volatility risk alarm is active. In 2025 this retains 54 signals, 39 correct (**72.22% accuracy, BA≈71.88%**) and signed gross log-return sum rises from +0.00671 to +0.03226. But this is a **2025-specific improvement**: on the available post-warm-up 2023 sample, accuracy *falls* from 40/71=56.34% to 34/62=54.84%; in 2024 from 52/86=60.47% to 34/57=59.65%. Therefore the risk gate **fails a cross-year strict promotion criterion** and cannot replace/edit frozen V1. The 2025 amount is the two-sided signed hypothetical return, not bank trade profit (shorting may be unavailable).

More sophisticated naive continuation-side use of volatility regimes still fails the cross-year direction test. The risk detector's gain is **tail-awareness**, not yet a validated broader directional alpha.

## 5B. Crucial execution-clock opportunity: earlier warning than PRAMV

**Volatility-only risk head needs no same-day 16:00–17:00 bars.** Each of RV5/RV20/RV60 uses completed prior overnight targets ending no later than *today's 09:00 Europe/Istanbul*. The mathematical risk score can therefore be evaluated **after today's 09:00 price/source readiness**, long before the bank's late-day spread expansion. For the user this is a separate **morning overnight-tail warning** (tentatively 09:15 Istanbul only after vendor-lag confirmation), even though its outcome is the *following* 17:00→next09:00 movement. This earlier issuance is NOT a 09:00→17:00 direction predictor and must NOT use today's current overnight target, which has not occurred.

The event-calendar extension must be separated by knowledge time: at a morning decision, only the schedule of upcoming releases is legal; the day's realized macro surprises released during 09:00–17:00 are **future information** and must not be imported. The combined exploratory OR alarm as currently measured uses the 17:00 event flag and therefore cannot be marketed as a 09:15 issued policy without rebuilding it with a 09:15 point-in-time event state.

Potential operational sequence:
- morning after source-ready historical prices: HIGH-RISK informational signal or normal-risk state;
- bank-action window before ~17:00: adjust exposure only after instrument/spread, sign versus absolute-risk utility and stress tests;
- late 17:00: independent unchanged PRAMV V1 direction forecast (not presumed bank-executable at zero latency).

**This is a clock-alignment research opportunity, not an already simulated executable strategy.**

## 6. Scientific assessment and next experiment

**Positive:** a different target and temporal-memory mechanism exposes serious tail risk on days the directional specialist ignores; 2025 showed a measurable 6/7 extreme-event warning in a wide-but-not-universal alert population. Robustness check and calendar jump-mechanism decomposition are worth pursuing.

**Negative/uncertain:**
1. 2023 and 2024 tail recall is poor at the same volatility cutoff; 2025's performance may be volatility-cluster regime specific.
2. Selection of the *research question* followed exposure to 2025 outcomes. The 2025 test is **not untouched OOS**, even though the numeric risk cutoff uses only 2023–2024 unlabeled scores. Do not call its nominal p-value a discovery-adjusted significance test.
3. 2% events are very rare (2 in 2023 post-warm-up, 5 in 2024, 7 in 2025). Tail AUC estimates are unstable.
4. Unknown calendar source rows are not negative event states. Scheduled future FOMC timestamps need official PIT calendar verification.
5. Bank bid/ask spreads, first obtainable **post-17:00** executable price, delayed trade decisions, no-short constraints, and actual holdings prevent interpreting idealized signed prices as performance.

**Research decision:** Keep the frozen PRAMV directional expert separate from an experimental dual-hazard warning head. For unseen confirmation, *freeze the exact 5/20/60 risk score, coefficients, cutoff, labeling, 60-day warm-up and data clocks* now, then test on a genuinely unopened future stream. In parallel, source-verify events and add a separately specified *jump-calendar hazard* with a controlled false-alert budget and paired comparisons, but do not retrofit PRAMV V1.

**Literature anchors:**
- Fulvio Corsi (2009), *A Simple Approximate Long-Memory Model of Realized Volatility*, Journal of Financial Econometrics 7(2), DOI 10.1093/jjfinec/nbp001 (multi-horizon cascade principle).
- Sobti (2025), *What triggers intraday price jumps and co-jumps in gold?*, International Review of Financial Analysis 105, DOI 10.1016/j.irfa.2025.104380 (macro/jump versus volatility regimes).
- Blaskowitz & Herwartz (2011), *On economic evaluation of directional forecasts*, International Journal of Forecasting 27(4), DOI 10.1016/j.ijforecast.2010.07.002 (signed-magnitude economic evaluation).
