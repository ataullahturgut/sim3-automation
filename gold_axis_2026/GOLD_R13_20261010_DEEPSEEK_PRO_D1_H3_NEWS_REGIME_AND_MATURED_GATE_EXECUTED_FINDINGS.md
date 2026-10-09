# R13 / R13B / R13C / R13D — Genuine DeepSeek V4 Pro scientific review, causal H3/D1, news/quiet and matured-competence gate
**Date 2026-10-10 TRT / source read through 2026-10-07. Verdict: REAL calculations & external review completed; _NO ROBUST UP/DOWN CHAMPION_. Original monthly model/earlier R12 unmodified.**

## 1. External referee authenticity and rejected causal mistakes
R13 first authentic DeepSeek API receipt `GOLD_R13_DEEPSEEK_V4_PRO_H3_NEWS_REGIME_20261010_RESULT.json`: returned requested `deepseek-v4-pro`, output **truncated** with finish_reason `length` at max3400 completion tokens; `status=INCOMPLETE` and failure QC. Its partial REVIEW is research notes, not complete reviewed recommendation. It made the invalid assertion `A_{t-1}` H3 target ending t+2 could be known at t and used current-day DAY outcome before 09 issue. GPT-6 flagged both explicitly.
R13B causal repair actually called DeepSeek again, receipt `GOLD_R13B_DEEPSEEK_V4_PRO_CAUSAL_REPAIR_20261010_RESULT.json` **PASS**: requested=returned `deepseek-v4-pro`, finish `stop`, 474 prompt +1152 completion tokens, returned3381 characters. Critical reviewer text `GOLD_R13B_DEEPSEEK_V4_PRO_CAUSAL_REPAIR_20261010_REVIEW.md`. Provider did not see private historical quote rows/keys, and **did not run a backtest**. Its repaired answer acknowledges maturation but then confuses 09:00 New York vs Türkiye, mislabels XAU returns as GVZ, uses an invalid claim of a 2019-published 2023–25 calendar and a median `agreement` indicator that by itself has no orientation to an UP or DOWN XAU direction. These are **rejected**, not authority to promote a model. DeepSeek's *valuable testable themes* were pre-origin maturation, conditional volatility state, calendar/no calendar decomposition and benchmark/negative controls. GPT-6 selected a lower-capacity independent falsification and actually executed it. `GOLD_R13C_CAUSAL_PREISSUE_NEWS_AND_H3_D1_HYBRID_PREREG_20261010.md` was committed BEFORE the queries; `GOLD_R13D_ONLINE_MATURED_H3_COMPETENCE_SOFT_GATE_PREREG_20261010.md` before the R13D test.

## 2. Crucial source/clock repair versus R12
True 08:45TR forecast features **04:45–08:30** 16 original M15 BID bar open-to-close increments (last bar ends08:45TR). True 16:45TR forecast features **12:45–16:30** M15 bars (last ends16:45). Old R12 05:00–08:45 path was not suitable for **08:45 early issue** because its last 08:45 M15 bar ends09:00. Source BID/ASK 09 or17 opens are ONLY FOR realized signed label, never current feature. **This R13 as-of improvement is methodological/data-timing, not higher accuracy claim.**
2020–25 audited Dukascopy-derived Neon `gold_research_evduka_xau15m_bidask_candidate` with 2026 independent Dukascopy direct `gold_research_dukascopy_2026_direct_m1_m15_bidask_v2` where `m1_matched=15`. Dates 2020-01-02→2026-10-07, raw accepted common two-clock panel 1,695 days; 4,990 qualified H3 09, H3 17 and DAY09 model rows with asof GVZ previous-day `GOLD_EXECUTION_GVZ_FREE_CANDIDATE_2020_20261007.csv`. Exact three **weekdays** ahead same 09/17 target; if missing intended target day, **exclude**, never roll forward arbitrary different date. BID/ASK endpoint signs must agree, no zero; cannot be interpreted as bank fill. Calendar holiday contract incomplete; holiday-lost observations excluded.
Price CBR exactly 8 cumulative preissue halfhour increments / sqrt(16 bar squared logreturns), 41 nearest paths, exp(-distance / median of41), with pseudo-count 5 historical UP ratio. REG adds fixed .30 standardized squared log GVZ/log preissue RV distance. Each new DAY/H3 target is separately trained; H3 training label end < following score-year Jan1; training 2020–22 (score2023),2020–23(score2024),2020–24 frozen(score2025,2026). 2025/26 previously opened, NOT virgin independent validation.

## 3. R13C — real per-year H3 09 and same-issue DAY/H3 hybrid (balanced accuracy %)
All on the exact same **qualified source dates** per annual origin. Year N for 09 H3 2023:252;2024:256;2025:255;2026:124. 09 DAY forecast itself is a distinct label and its prediction was used ONLY as a feature-free causal forecast for H3 mixing. It is NOT the realized future DAY return.
| 09TR H3 model | DEV 2023 | DEV 2024 | opened2025 | opened2026 |
| --- | ---: | ---: | ---: | ---: |
| CBR PATH | 51.59 | 50.60 | 53.36 | 45.96 |
| CBR + GVZ/RV REGIME | 51.19 | **42.62** | **55.75** | **53.75** |
| Separate D1 09→17 **predicted** CBR, retargeted H3 | 50.79 | 46.54 | 51.58 | 49.09 |
| Mean 0.5 H3+0.5 D1 forecast | 50.00 | 50.10 | 53.58 | **42.53** |
| Constant UP baseline | 50.00 | 50.00 | 50.00 | 50.00 |

2026 same124 REGIME: **72/124=58.06% raw**, BA53.75%, UP recall29.41%, DOWN78.08%; 2025 same255 REGIME **146/255=57.25% raw**, BA55.75%, UP61.49/DOWN50.00. This is an observable reversal in signed market class policy (2026 captures DOWN but misses UP), **and REGIME failed in 2024 BA42.62**. Hence DO NOT promote it as '2026 solution'. H3+DAY naive hybrid 2026 47/124=37.90% raw, BA42.53%; versus same-date raw CBR52/124 and REGIME72/124. The expected benefit of forecast horizon combination is **falsified for these frozen weights**.

R13C 17TR→next T+3 weekdays at17TR, source n2023 252;2024 256;2025 255;2026 124:
| 17TR H3 model | 2023 | 2024 | 2025 | 2026 |
| --- | ---: | ---: | ---: | ---: |
| CBR PATH | **58.95** | 45.48 | 48.16 | 52.06 |
| CBR+GVZ/RV REGIME | 51.45 | 48.65 | 48.81 | 49.77 |
No strong stability; 2026 17TR CBR PATH only63/124=50.81% raw and DOWN26.15%. Do not silently repurpose 09 H3 result for 17 H3.
Caution: This strict preissue version is not exactly identical to R12 (earlier 09/17 issuance paths): comparing their different feature bars is not a true same-forecast model upgrade.

## 4. R13C — historical macro news / no scheduled macro / high-GVZ segmentation
Source scheduled releases `GOLD_EXECUTION_PRAMV_OFFICIAL_2025_MACRO_SOURCE_GOVERNED_V2_20261008.csv`, 94 distinct event-list entries of type CPI/NFP/FOMC from 2023–25; exclude NFP companion AHE/UNEMP duplicates. If any scheduled timestamp falls **strictly after08:45TR issue and before the exact H3 end 09TR**, tag **INCLUDES SCHEDULED CPI/NFP/FOMC**. Else tag **NONE OF THESE THREE SCHEDULED**, _not no news_. Only ex-ante *release date/time*, never actual or consensus or surprise. Original historical publication-vintage for calendar not independently certified; tag is retrospective historical schedule reconstruction. 2026 official complete matching calendar **not certified**, hence 2026 news-vs-no-news stratification deliberately **NOT CLAIMED**.

| Year | CPI/NFP/FOMC in H3 window N | PATH BA | REGIME BA | No listed release N | PATH BA | REGIME BA |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2023 | 85 | 53.27 | 51.97 | 167 | 50.79 | 50.79 |
| 2024 | 89 | 51.38 | **43.54** | 167 | 50.61 | **42.48** |
| 2025 | 88 | 53.42 | **58.65** | 167 | 53.65 | 54.36 |
**No stable signed event-gating edge.** Simply swapping to separate 09 DAY H3 mixture on no-event rows and PATH on event rows did not beat PATH consistently, on 2025 same exact quiet subset PATH/BLEND both BA53.65 and same event subset PATH BA53.42.

GVZ state: last known `GVZ_{d-1}` > median of trailing last126 lagged official closes (min100) defines preissue HIGH. 2023 high GVZ N115 PATH BA55.19 vs REGIME50.77; 2024 high N167 PATH BA51.71 vs REGIME44.56; 2025 high N153 **REGIME57.31 vs PATH50.70**. Conditional expert competence flips over eras. 2025 selection high-GVZ regime head would be retrospective 'best month' illusion.

## 5. R13E — explanatory event/no event H3 large-move absolute risk and true frozen 2025 Brier
Separate actual provider BID 09→3-weekdays-later09 returns on source-qualified historical bid/ask sign eligible cohort: 2023 event86 vs no-listed-event168; 2024 event89 vs no-listed167; 2025 event88 vs no-listed165. Here a one-day N difference from strict preissue-H3 CBR cohort occurs because absolute-risk check does not require all 16 source origin feature bars; don't pair raw n blindly.
| Year | Listed CPI/NFP/FOMC somewhere in H3 | P(abs H3 return≥1%) | No listed release | P(abs H3 return≥1%) |
| --- | ---: | ---: | ---: | ---: |
| 2023 | 86 | 44/86=51.16% | 168 | 63/168=37.50% |
| 2024 | 89 | 48/89=53.93% | 167 | 80/167=47.90% |
| 2025 | 88 | 52/88=59.09% | 165 | 97/165=58.79% |

Frozen 2023+2024 Beta(1,1) 2-group prior on 2025 H3 absolute>=1%: event p=0.52542, none p=0.42730, pooled p=0.46094. 2025 Brier 2-group **0.260397** versus SAME training pooled constant **0.258474**: calendar worsens by0.001923. For >=1.5%, 2-group Brier0.271337 vs pooled0.266416; >=2% 0.231932 vs pooled0.231863. All are worse on 2025. This does NOT negate prior **15-minute CPI/NFP shock event risk** R6, which is a different target. It falsifies calendar-alone H3 tail-risk calibration for these thresholds.

## 6. R13D — true causally mature online expert competence (NOT retrospectively selected switch)
Predeclared exact formula in R13D prereg before actual test: take most recent at most63 prior origin forecasts with **realized H3 target timestamp strictly older than current issue**, exponentially weight .98^lag the score (p-y)^2, denominator15+sum weights, online expert softmax exp(-25 discounted loss). Combine PATH and REGIME probabilities; no un-matured H3 outcomes. This tests whether a low-capacity dynamic competence gate repairs 2024→2026 inversion rather than hard 2026 regime selection.

| 09TR H3 BA | 2023 | 2024 | 2025 | 2026 |
| --- | ---: | ---: | ---: | ---: |
| PATH | 51.59 | 50.60 | 53.36 | 45.96 |
| REGIME | 51.19 | 42.62 | 55.75 | 53.75 |
| STATIC equal score average | 48.81 | 47.67 | 53.40 | 48.50 |
| **ONLINE matured competence** | **48.81** | **47.67** | **52.25** | **50.44** |

2026 online 62/124=50.0% raw, BA50.44, DOWN47.95, UP52.94; vs PATH 52/124 41.94% raw BA45.96; vs better frozen REGIME72/124 58.06% raw BA53.75. Dynamic selector PATH-vs-online 2026 **22 rescues /12 newly broken = net+10** raw decisions, but fails to beat REGIME and damages 2023/24/25: 2023 18 rescues25 broken, 2024 19/26,2025 14/19; nonportable.
2026 mean online PATH weight0.406, 2023 0.495,2024 0.500,2025 0.506. Full matured previous63 evidence in 2026 every eligible origin. Gate is causal within observational score data, but 2025/26 model/architecture hypothesis chosen AFTER many prior inspections; not independent OOS.

17TR H3 online BA2023 56.78 /2024 45.77 /2025 46.12 /2026 49.61; 2026 down recall only7.69% vs PATH26.15%; **DO NOT USE**.

## 7. What was actually verified and what is NOT
- Ran actual SQL SELECT from protected Neon market price candidate, 2026 m1_matched=15 and source origin-hour bars, original repo GVZ historical candidate and governed 2023–25 US scheduled macro UTC rows. Numerical simulation in the tool execution sandbox (JavaScript orchestration and no DB writes). Not a GitHub Actions full Python-model replay, not a bank execution trial. All tests separated by clock, horizon and calendar source cohort and computed real outcomes. Preregs for R13C and R13D were created before their associated queries.
- Fixed evaluator computes raw, BA, two recalls, rescues/breaks and in R13D Brier. R13E separate risk Beta prior evaluated on opened 2025. **Event and GVZ stratification, prior 2026 anomalies, online gate all have multiple hypothesis risk; no claim of confirmatory p-value.**
- Strict random variable maturity: event schedule is known-in-principle but historic first-print calendar vintage unproved; first future macro *surprise* MUST NEVER enter origin forecast. 2020–25 vendor source archive reconstituted after the fact; availability at 08:45 historical provider firstprint and actual bank margin not certified. 2026 direct overnight stale candle issues remain separate data QC; R13 features require 16 source bars preissue but do not independently certify every raw tick quality; no false source-independent claim. **No official 2026 complete calendar passed the 2026 event/no-event test.**
- 09TR→H3 and 17TR→H3 endpoint target can require bank holding beyond 17TR for multiple days. There is no zero-spread or spread-adjusted executable PnL claim. **Overlapping H3 targets share future gold moves; the 252/256 annual forecasts are NOT independent independent trials**. Fixed T+3 *weekdays*, absence of original quote at target removes row; holiday exchanges require further official adjustment.
- External peer consultation yielded a useful negative causal audit, but DeepSeek's 'regime success' conjectures were not promoted without data. The older monthly ChHHO model remains frozen, and its original daily issued numeric values for H3 still unverified: **this R13 research does NOT claim running original monthly ChHHO optimizer, 13D HMM asof states, legacy HELIOS or RTE architectures on H3**.

## 8. Scientific conclusion
**Original research question tested honestly: more time (H3) or naive daily+H3 hybrid, news/nonnews, GVZ regime and dynamic expert competence do NOT yet deliver a robust two-sided gold direction edge through 2023–2026.** R13C strict preissue gave the relative best among those evaluated 2026 09 H3 REGIME BA53.75, 2025 55.75, but 2024 BA42.62. R13D gate improved 2026 PATH by +4.48 BA points but remains near chance and degrades earlier periods. 2025 H3 macro event-based tail Brier got **worse** versus pooled prior. Main genuine scientific advance is identifying/repairing issue-time feature-bar leakage, computing asof matured H3 forecasts, and falsifying proposed news-conditioned static combination without inventing success.
Most defensible future research ONLY if source can support it: original PIT-frozen numeric monthly ChHHO distribution and filtered (not smoothed) 13D HMM regime states as-of each H3 origin + source-verified relative GC/spot/cross-asset innovation; low-dimensional *conditional risk* then genuine 2027+ independent registry; compare matched-date same vendor and bank spread. Never retrospectively optimize over repeatedly seen 2025/26 or claim >=65% raw on an imbalanced year implies directional edge.

## Literature authority
Sobti et al., International Review of Financial Analysis (2021), https://www.sciencedirect.com/science/article/pii/S1057521921002209 : state/asymmetric macro news effects; **price discovery**, not H3 signed forecast accuracy.
Awartani et al., International Review of Financial Analysis (2024), https://www.sciencedirect.com/science/article/pii/S1057521924004186 : intraday policy-news responses.
Smales & Yang (2015), https://research-repository.uwa.edu.au/en/publications/the-importance-of-belief-dispersion-in-the-response-of-gold-futur/ : most reaction can be rapid; cannot leak post-release signs into issue.
Original project primary manifest and `GOLD_H3_H5_EXECUTION_CLOCK_HORIZON_TRANSFER_EXPLORATORY_RESULT_20261010.md` remain historical provenance; this R13 test has stricter asof features and different outcomes.
