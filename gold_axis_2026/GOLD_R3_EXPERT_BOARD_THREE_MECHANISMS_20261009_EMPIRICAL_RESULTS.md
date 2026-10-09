# R3 Expert Board: literature → three author hypotheses → DeepSeek hostile review → actual SIX matched experiments → 2026 native stress
**As of 2026-10-09. Status:** completed **retrospective, exploratory** empirical comparisons; **NO statistically verified or bank-executable signed-direction champion.** This report records a small consistent DAY jump-reversal *candidate* but not a deployed model or independent holdout success.

## 1. Three expert disciplines and their constraints
Macro/econometric literature: Xu et al. (2020) DOI10.1016/j.resourpol.2020.101830 on intraday commodity return predictability; Ma et al. (2025) DOI10.1016/j.gfj.2025.101084 on time- and liquidity-dependent gold/silver momentum/reversal; Sobti (2025) DOI10.1016/j.irfa.2025.104380 on gold jump/flow/news; Alexiou et al (2026) DOI10.1016/j.jbankfin.2026.107720 on **OPTIONS** realized signed semivariance, which **must not be misrepresented as evidence of SPOT XAU sign prediction**. Bajgrowicz, Scaillet, Treccani (2016) DOI10.1287/mnsc.2015.2234 warns apparent 15m jumps may be spurious; Xiao et al (2020) DOI10.1111/jfir.12223 shows jump news-state dependence in broad-market **equity ETFs**, not directly XAU night.
Author GPT-6 FIRST wrote prereg `GOLD_MULTIDISCIPLINARY_THREE_MECHANISM_PREREG_20261009.md` with exact 17 completed M15 origin prices, three mathematically fixed rules SSV4/RCL4/JDR4 and signed end labels. The original *TWO-round* DeepSeek technical-review job failed `DEEPSEEK_OUTPUT_INCOMPLETE_OR_TRUNCATED`; failure artifact preserved and **not passed as successful peer review**. Then **ONE** bounded flash call succeeded: `GOLD_DEEPSEEK_BOARD3_SHORT_CRITIQUE_20261009_REVIEW.md` (1,682 in +782 output =2,464 provider tokens). The reviewer criticized all three, compared duplicate risk to PRAMV/RFR and proposed-but-not-fitted TURN, and required equal-date controls. Reviewer incorrectly suggested that a precisely Istanbul-defined 17→09 target is "mislabeled overnight" because it is not NY close; this is not a valid criticism of the USER-defined execution object. External reviewer did **not** score any market data.

## 2. Existing-manifest duplication audit, no renamed champion
- Prior actual `LIT-OVN 0/1`, `PRAMV`, `RFR`, `BSC8` already investigated simple pre-origin returns/reversal, or own BID/ASK spread states. They are NOT a new information source.
- `TURN` semivariance/tail reversal was **listed as unrun research candidate**, not evidence of this exact prereg signed-semivariance rule having been completed.
- Old `CAVS` untrained GC relative venue price/volume cannot be confused with the three fixed XAU intrinsic shape tests.
- Today's negative CME3-K25 and ZN-VPT2 are independent-source price/volume studies, materially different columns.
- Thus rule formula/clock tests can be a **low-cost falsification of untested transformations**, but NOT genuinely independent information channels or breakthrough theory.

## 3. Approved 2023–25 data / exact decision time
- Historical target table: `gold_research_evduka_xau_session_target_candidate_v1`; historical BID/ASK source: `gold_research_evduka_xau15m_bidask_candidate`. Price = (bid_close+ask_close)/2; require **all 17 contiguous** 15-minute M15-start candles preceding issue. DAY starts 04:30..08:30 local, each completes by08:45; target 09→17. OVN starts12:30..16:30 local, each completes by16:45; target17→next CALENDAR weekday09, no Friday or holidays. No incomplete current M15, no FOMC release after origin, no overnight future prices as features.
- 2023/24/25 DAY n256/259/258; regular OVN n197/198/198, one 2023 night excluded for preorigin feature discontinuity. These are same-source, non-2026 rows. No zero-price or zero-variance cases in counted completed feature rows.
- Freeze baseline B4 = sign(Σ16 preorigin r15m), B1 = sign(Σlast4 r15m). DOWN=negative, UP=positive.
- S1 SSV4: sign(Σsign(r_i)*r_i²), an asymmetry-of-realized-variance momentum candidate. S2 RCL4: price terminal location within 4h high-low, if >=0.8 predict DOWN (reversion), <=0.2 predict UP, else B1. S3 JDR4: if max(r_i²)/Σr_i² >=0.50, predict *opposite* dominant r_i sign; otherwise B4. All rules frozen BEFORE seeing these experiment-specific labels, evaluated all days, no confidence threshold mining.

### Strict computational QC
An initial interactive check used the ERRONEOUS expression `r*sign(r)*r²`, which is `|r|³` and mechanically cannot represent signed semivariance. **Rejected as a software error before report**, not treated as a model result. The actual second full read-only data extraction used correct `sign(r)*r²` and asserted agreement with `sum positive r² - sum negative r²` within 1e-18. ALL S1 reported below are from the corrected execution; no false all-UP claim.

## 4. Actual six crossed mechanism × target annual balanced accuracy
| Target/year | N | B4 BA | B1 BA | SSV4 BA | RCL4 BA | JDR4 BA |
|---|---:|---:|---:|---:|---:|---:|
| DAY 2023 |256|48.34|51.61|46.90|52.11|50.97|
| DAY 2024 |259|50.43|44.32|49.19|46.88|52.89|
| DAY 2025 inspected |258|53.94|52.05|52.50|48.18|55.58|
| OVN 2023 |197|41.72|46.49|43.21|55.44|44.69|
| OVN 2024 |198|47.44|44.78|48.17|49.33|47.58|
| OVN 2025 inspected |198|55.63|54.11|55.76|47.01|56.12|

Reject SSV4 as distinct direction champion: near baseline, inconsistent. Reject RCL4 because 2023 overnight BA55.44 is not stable in 2024/25 (OVN25 47.01). JDR4 OVN likewise does not transport.

### Candidate JDR4 DAY full-date paired statistics versus B4
| Year | N | B4→JDR BA | JDR ACC | JDR DOWN recall | JDR DOWN precision | Corrected / broken | Exact McNemar p |
|---|---:|---:|---:|---:|---:|---|---:|
| 2023 DEV |256|48.34→50.97|51.17|57.58|52.41|19/12|0.281042|
| 2024 DEV |259|50.43→52.89|53.28|50.00|46.28|14/8|0.286279|
| 2025 INSPECTED |258|53.94→55.58|56.20|50.89|49.57|17/11|0.344928|
Three positive YEARLY differences are mild and per-year not significant. Across 2023–25 pooling disparate inspected cohorts: rescues50/breaks31, *nominal* exact p=0.044829; **post-selection multiple testing across 3 mechanisms×2 horizons, no adjustment or month-block CI, NOT a valid discovery significance**. Never promote from this p alone.

## 5. Extension beyond one retrospective publisher: frozen 2026 native direct M1→M15 source stress
**Source/clock separately preregistered AFTER inspected historical results, so NOT unseen holdout**: `GOLD_R3_JDR4_2026_NATIVE_STRESS_PREREG_20261009.md`. Source `gold_research_dukascopy_2026_direct_m1_m15_bidask_v2`, available Jan–Oct07 2026, source retrieval Oct08 HISTORICAL NOT PIT. Native bars all `m1_matched=15`. Derived both realized labels FROM same direct native source by 08:45-start M15 close09 and16:45-start M15 close17, and next-day08:45-start close09; full 17 preorigin M15. No price 17 anchor as pre-16:45 feature. Exclude Friday→Monday and missing outcome anchors. Native source vs historical source are different vendor retrieval methods of same general Dukascopy upstream, **NOT an independent underlying publisher**.

| Target 2026 (selected source-complete dates) | N | B4 BA | JDR4 BA | B4 ACC | JDR4 ACC | JDR4 DOWN recall | Corrected / broken | McNemar p |
|---|---:|---:|---:|---:|---:|---:|---|---:|
| DAY |147|53.03|56.30|52.38|55.78|63.24|9/4|0.266846|
| OVN regular |103|48.68|48.26|48.54|48.54|50.88|5/5|1.000000|

For 2026 DAY, quarters: 2026 Q1 N24 JDR BA60.00 vs B4 54.44; Q2 N64 60.93 vs55.06; Q3 N54 52.69 vs52.69; Q4 (Oct07 only) N5 41.67 equal. These Q1/2 months are **small, missingness-selected and previously inspected**. 2026 night N103 JDR not better than own B4 baseline, consistent original R3 no-OVN-win conclusion.

## 6. Direction hit ≠ real execution payoffs; economic fragility
Hypothetical **signed bid/ask-mid log-return** sum for DAY, assuming instant exact 09/17 execution, unlimited daily long or short, no costs, and one constant position per day. This is **NOT bank trading PnL**, not realizable with unavailable shorting and bank spreads.
- 2023 DAY B4 sum +0.02725 vs JDR4 +0.00969: **JDR worse −0.01755**.
- 2024 DAY B4 +0.03927 vs JDR4 +0.09704: JDR incremental +0.05777.
- 2025 DAY B4 +0.10928 vs JDR4 +0.21819: incremental +0.10891.
- 2026 DAY source-native B4 +0.03157 vs JDR4 +0.18837: incremental +0.15681; **43% of incremental gross signal gain comes from the largest single favorable changed DAY (0.06768)**, 63% from top two. After removing top two positives, added gross logreturn +0.05870 remains; 13 changed predictions only.
- 2026 direct features and the historical 2025 signed targets are **not** a real bank executable price panel. Any trading assessment needs actual bank buy/sell bid-ask at origin, fees, known cutoff before17 and rules about existing inventory/shorts.

## 7. Expert-board decision / scientific next gates
A successful external call produced nonbinding expert critique; independent human-style methods review noted output confusion about Istanbul-defined overnight. Six genuine retrospective matched tests done, one later separate 2026 native source stress done, and additional gross-return fragility checked. **SSV4 and RCL4: REJECT** as reliable signed forecasters. **JDR4: RETAIN FOR FALSIFICATION ONLY ON DAY, DO NOT PROMOTE**; modest cross-year advantage with weak paired evidence may be optimization luck and price-state transform, not a genuinely independent information stream. Rejection for OVN. A credible next challenge requires:
(1) audit whether 15m 'dominant' candle is true discrete jump or a volatility burst (5m native M1 aggregation if available); (2) preissue news-event labels to distinguish informational jumps vs liquidity overshoots, with publication-aware as-of; (3) month-block leave-period-out plus negative-control random flip of equal-count concentrated events; (4) original frozen PRAMV/H3 on exact dates and 09TR issue time (do NOT claim old 74.4%); (5) prospective forecast registry beginning strictly AFTER the current retrospective inspection. Not even a genuine outlier-adjusted bank payoff claim until execution broker BID/ASK exists.
