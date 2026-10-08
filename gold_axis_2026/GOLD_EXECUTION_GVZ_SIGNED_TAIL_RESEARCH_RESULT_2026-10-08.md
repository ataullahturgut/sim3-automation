# GOLD EXECUTION / SIGNED-TAIL HAZARD, GVZ AS-OF — 2026-10-08

**Status:** VALID RETROSPECTIVE HISTORICAL RESULT / UNPROMOTED EARLY WARNING, NO DIRECTIONAL-TRADE PROMOTION.  
**Target:** XAU/USD *overnight* log return, Istanbul 17:00 -> next eligible 09:00.  
**Issue-time source distinction:** D-1 completed Cboe GVZ + previous matured overnight XAU target returns. This *risk forecast* is in principle computable after the morning 09:00 data source becomes available; data-vendor latency and executable bank quotes still unverified.  
**Frozen PRAMV V1:** UNCHANGED.

### Data lineage and reproducibility

- `GOLD_EXECUTION_DUAL_HAZARD_ROWS_2026-10-08.csv`: 709 origin-day risk scores (5/20/60 preceding completed overnight returns; warm-up before 2023-03-28).
- `GOLD_GVZCLS_RAW_2021_2025.csv`: official Cboe daily GVZ, strictly *last dated observation < issue date*; no same-date close and no backward-filling of future days. 709/709 valid joins.
- `GOLD_DGS2_RAW_2022_2025.csv`: official rates, similarly D-1, 709/709 valid joins; explored as incremental challenger but not promoted.
- `tools/gold_execution_gvz_signed_tail_hazard_20261008.py`: replay code for fixed low-capacity penalized logistic event models.
- `GOLD_EXECUTION_GVZ_SIGNED_TAIL_PREDICTIONS_2026-10-08.csv`: exact 589 date-stamped forecasts, baseline probabilities, labels and GVZ source date.
- `GOLD_EXECUTION_GVZ_SIGNED_TAIL_METRICS_2026-10-08.csv`: signed-tail proper-score and AUC ablations.

### 1. New scientific target: mutually exclusive signed tail risks

**Do not conflate volatility probability with direction.** Assess two separate event classes:

1. **DOWN-TAIL:** `r_overnight <= -0.0100`, a ≥1% negative *log-return* event.
2. **UP-TAIL:** `r_overnight >= +0.0100`, a ≥1% positive *log-return* event.

These are separate binary hazards; no evidence that either event is certain to occur, and independent probabilities should not silently be interpreted as a mutually coherent three-class conditional distribution. A no-event middle class exists. Neither model is a full UP/DOWN forecast.

**Mechanistic contrast:** downside/upside tails may arise from separate risk pricing processes. The official GVZ is **total 30-day options-implied gold ETF volatility**, not an independently measured put-side downside variance risk premium or direct COMEX order flow. Do not rename this feature an actual downside VRP.

### 2. Origin-safe minimal model and timeline

- Feature #1: `log(score(t))`, score from already-matured 5, 20, 60 previous overnight targets, `sqrt(0.5*RV5²+0.3*RV20²+0.2*RV60²)`.
- Feature #2: `log(GVZ_(D-1))`, with source date strictly before forecast issue.
- Two-coefficient `L2=5` regularized logit, standardized using only the training history; intercept unpenalized.
- **2023–2024** expanding training using only matured previous outcomes and at least 120 prior eligible risk-score rows; 2023 N=76, 2024 N=259 predicted dates.
- **2025** model fit frozen on all 455 scored rows from 2023–2024 (2025 N=254). The *design* came after inspecting 2025, so 2025 is retrospective corroboration NOT an untouched out-of-sample validation.
- Same-origin baselines: (a) Laplace-smoothed matured history event rate, (b) score-only logit, (c) GVZ-only logit. Also explored rate level/change and GVZ change; no 2025-retuned family promoted.

### 3. Main result: large overnight DOWN-risk probability

| Year | Chronological evaluation | Score-only Brier | GVZ-only Brier | **Score+GVZ Brier** | Historical-rate Brier | **Score+GVZ ROC-AUC** |
|---|---:|---:|---:|---:|---:|---:|
| 2023 | 76 dates; 3 tails | 0.038473 | **0.038016** | 0.038166 | 0.038190 | 0.498 |
| 2024 | 259 dates; 14 tails | 0.051120 | 0.051230 | **0.050988** | 0.051427 | 0.650 |
| 2025 (opened archive) | 254 dates; 17 tails | 0.059657 | 0.057604 | **0.057340** | 0.062890 | **0.813** |

**2025:** score+GVZ Brier is 8.82% lower than the same-history event-rate baseline, and 3.88% lower than score-only. GVZ alone captures nearly all of the fusion improvement (0.057604 vs 0.057340), so **the incremental benefit of combining the two is small and has not been independently proved**. A low Brier is partly due to rare events; hence AUC, event calibration and alarm budget are essential.

Five-date moving-block bootstrap of *fixed predictions* (2,800 draws, seed 20261008) for 2025:
- model DOWN ROC-AUC approx **0.813**, percentile 95% CI **[0.707,0.898]**;
- historical rate Brier minus model Brier = **+0.005549**, 95% CI **[-0.001033,+0.013386]**;
- score-only Brier minus model Brier = **+0.002317**, 95% CI **[-0.002144,+0.007374]**.
Neither Brier difference excludes zero, and this is **not a model-selection-adjusted or prospective p-value**. 2024 AUC bootstrap CI ~[0.500,0.798]; 2023 N=3 extreme warnings gives no meaningful classification inference.

### 4. Magnitude dependence — predictive ability is concentrated in *severe* declines

A separate *unfitted raw-score* source-ready ROC-AUC on the larger 709-day risk-population (not the 589-row fitted-probability test) confirms a severity hierarchy:

| Actual negative overnight log-return | 2023 score AUC / events | 2024 score AUC / events | 2025 score AUC / events |
|---|---|---|---|
| <= -0.5% | 0.510 / 29 | 0.549 / 42 | 0.656 / 55 |
| <= -0.75% | 0.640 / 12 | 0.606 / 26 | 0.683 / 34 |
| <= -1.0% | 0.654 / 6 | 0.648 / 14 | 0.789 / 17 |

This is an ex-post exploratory threshold sweep (multiple selection) and does not establish monotonicity of predictive skill in a population, but suggests that volatility can rank *tail severity* better than ordinary DOWN sign. It also explains why increasing generic UP/DOWN accuracy by mixing direction experts has not reliably transported.

### 5. Decisionability falsification: high tail AUC is not automatically a usable DOWN call

Take an independently specified, purely trailing calibration rule: **alert if today's predicted DOWN-TAIL probability is above the 80th percentile of the previous 60 published DOWN-TAIL probability forecasts.** Requires 60 forecast-history warm-up; no future scores.

| Year | Alert days | Actual ≥1% declines caught | Tail-event precision |
|---|---:|---:|---:|
| 2024 | 58/259 | 6/14 | 6/58 = 10.3% |
| 2025 archive retrospective | 75/254 | 10/17 | 10/75 = 13.3% |

On the **same dates**, the original raw price volatility score with its own trailing-60 80th-percentile cutoff achieves 2024 **6/14 in 50 alarms**, and 2025 **11/17 in 54 alarms**. Thus the GVZ-fused model is **inferior as a tested alarm policy**, despite higher full-ranking ROC-AUC. In 2025, only 32 of the 75 GVZ-fused alarms have an *ordinary negative* overnight return (42.7%), approximately equal to the unconditional DOWN rate 108/254 = 42.5%. This model predicts risk of a *large* negative tail, **not** general overnight DOWN direction and not an executable sell signal. Do not promote the trailing-percentile policy based on this research.

A static cutoff of the development 80th percentile on fitted probabilities flags 182/254 2025 dates (71.7%), rendering the stated 'tail alert' insufficiently selective. Do not quietly report its 16/17 tail recall while hiding the 182 alarms.

### 6. Asymmetry control — large UP risks are much less predictable

| Year | ≥1% UP events | Score+GVZ UP Brier | UP ROC-AUC |
|---|---:|---:|---:|
| 2023 | 6/76 | 0.075819 | 0.376 |
| 2024 | 10/259 | 0.037487 | 0.554 |
| 2025 reviewed retrospective | 26/254 | 0.094873 | 0.532 |

The DOWN-hazard signal does not extend symmetrically to UP tails. However, the 2025 year had more UP tails than DOWN tails; always-UP and other class-prior strategies must be included in any direction accuracy audit.

### 7. External source and theoretical motivation

- Roh, Byun, Xu (2020), **Downside uncertainty shocks in the oil and gold markets**, *International Review of Economics & Finance* 66, 291–307, DOI `10.1016/j.iref.2019.12.003`: downside option-derived variance-risk components are distinct economic state variables; this **does not establish** the current GVZ level as such a component.
- Indriawan, Lien, Roh, Xu (2020), **Bad volatility is not always bad: evidence from the commodity markets**, *Applied Economics* 52, DOI `10.1080/00036846.2020.1735619`: decomposed variance premiums can behave asymmetrically; they report upside-component predictability as more salient for precious metals, an important caution against over-interpreting our downside empirical association.
- Salisu et al. (2023), **Gold and tail risks**, *Resources Policy*, DOI `10.1016/j.resourpol.2022.103154`: VaR/tail-risk forecasting motivations; does not validate this model.

### 8. Research decision and necessary follow-on

**Retain as an experimental morning-informational downside-tail risk score. NO DEPLOYMENT, NO PRAMV MODIFICATION.**

Strength: model uses independent options-market implied volatility with strict D-1 source gating; downside ≥1% event ranking in 2025 is promising and has a bootstrap interval above chance, while modest gains over historical event-rate occur in 2023 and 2024.

Blockers:
1. 2025 was open during exploratory hypothesis selection, not clean untouched OOS; 2023 fitted-probability evaluation has only 3 extreme events.
2. No consistently superior *risk-at-fixed-alert-budget* policy to the simpler raw prior-price risk score. Report both, don't cherry-pick AUC.
3. No general DOWN directional signal, no bank-executable P&L, and vendor-availability/quote-delay clocks require proof.
4. Raw continuous GC futures price/volume, put-vs-call option skew/variance-risk-premium, and instrument bid/ask data are distinct sources not proven available here on the exact same issue clock. **Never synthesize a skew/put-side premium from total GVZ.**
5. The raw 2022 XAU 15-minute reference exists in repository but was not materialized into this tool session (GitHub contents response empty for oversized blob); full 2022 target warm-up could substantially enlarge 2023 test, but *cannot be claimed complete yet*.
6. The 2025 macro-event calendar remains quarantined due to missing FOMC ledger entries, as governed in the prior research result.

Next experiment: gather verified 2022 17:00→09:00 origin-safe price history to eliminate 2023's second warm-up deficit, test official source-ready GC/GLD put-call asymmetry or options skew, score fixed severe-DOWN hazard against **raw-score-only** at matched alert count, and record future predictions before outcomes. If no such new independent information or genuinely untouched dates exist, *do not claim the problem solved*.

**2026 day-window target remains a separate identity; the research here is overnight only.**
