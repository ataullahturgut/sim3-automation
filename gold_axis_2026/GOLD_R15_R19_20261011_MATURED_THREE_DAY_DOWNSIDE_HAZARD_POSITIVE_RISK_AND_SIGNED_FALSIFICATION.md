# R15–R19 | GENUINE NEW MEASURABLE PROGRESS IN **THREE-DAY DOWNSIDE RISK**, NOT VERIFIED UP/DOWN TRADING ALPHA
Date: 2026-10-11 TRT. Four real sequential preregistrations were committed BEFORE their Neon SELECT calls:
- R15 `GOLD_R15_H3_CAUSAL_TAIL_RISK_GVZ_RV_VS_SIGNED_SELECTOR_PREREG_20261011.md`
- R16 `GOLD_R16_H3_MATURED_LOCAL_TAIL_RISK_BASELINE_AND_DOWNSIDE_SIGN_TEST_PREREG_20261011.md`
- R17 `GOLD_R17_H3_TWO_TAIL_ASYMMETRIC_HAZARD_TO_SIGN_PREREG_20261011.md`
- R18 `GOLD_R18_DOWNSIDE_HAZARD_ABLATION_HAC_AND_SOURCE_PARITY_AUTHORITY_20261011.md`
- R19 `GOLD_R19_ONE_SIDED_H3_DOWNSIDE_HAZARD_CBR_RESCUE_PREREG_20261011.md`
**Verdict:** SOURCE-AUDITED RESEARCH BACKTEST POSITIVE AS TO BRIER DOWNSIDE-TAIL PROBABILITY VS HISTORIC STATIC/CAUSAL ROLLING BASES. Signed trade promotion remains NO. 2025/2026 are previously INSPECTED, no untouched validation.

## 1. Source and true preissue clocks
Neon PRIVATE Gold Control readonly SQL SELECT: historical 2020–25 `gold_research_evduka_xau15m_bidask_candidate`, source-qualified 2026 `gold_research_dukascopy_2026_direct_m1_m15_bidask_v2` require `m1_matched=15`. Prior GVZ daily from `GOLD_EXECUTION_GVZ_FREE_CANDIDATE_2020_20261007.csv`, require strictly earlier date and calendar staleness≤7d. Source 1696 origin dates with16 completed M15 XAU BID open-close increments at04:45..08:30TR (completed no later08:45). Additional previous6 complete09:00 BID opens for5 lagged completed daily 09→09 returns, reject any neighboring quote-source gaps>7 days. Target 09TR XAU spot BID & ASK signed quote-open return exact **third next Mon–Fri** day09TR; sign agreement, nonzero, no shift if target lacks price. Reconstructed asof uses origin gold 04:45→08:45 4h RV and previous daily-close GVZ, **no future data**. Approved common cohort **1641 source rows 2020-01-10..2026-10-02**; 2023 N254,2024 N256,2025 N255,2026 N116 (2026 event observations stop after valid H3 maturity, not whole365days). Source full target return reconstructed after expiry; never in issue features.
2023 score frozen train until Jan2023 with matured H3 label end strictly<first scoring year day (n758);2024 until Jan2024 (n1012);2025 AND2026 same frozen train until Jan2025 (n1268). Monthly metals/GPR excluded because live firstprint unverified and R14 failed; full HMM 13D states NOT claimed.

## 2. The one genuinely positive quantitative channel: major 3-day DOWNTAIL
Event `D_t=1[ln(BID_H3/BID_entry)<=-0.015]` (a gold drop exceeding ~1.5% in three weekdays), on sample where ASK direction same as BID. Model frozen L2 λ30 standardized logistic `logit P(D=1)=β0+β1 log(4h realized RV)+β2 log(previous-close GVZ)`. Compare training-only Beta(1,1) static previous years' positive frequency, **strict last63 matured-label Beta(4,4) rolling local** and ablation single predictors. All are real scored-outcome experiments, not DeepSeek invented metrics.

| Issued 08:45TR, H3 downside ≥1.5% | DEV 2023 N254 | DEV 2024 N256 | OPENED 2025 N255 | OPENED 2026 N116 |
| --- | ---: | ---: | ---: | ---: |
| Actual downside events | 21 | 35 | 29 | 36 |
| Pooled static train prior Brier | .080374 | .118040 | .101197 | .245178 |
| Matured rolling63 local Brier | .081060 | .123730 | .111445 | .229415 |
| 4h RV ONLY Brier | .079597 | .114902 | .099450 | .224238 |
| Lagged GVZ ONLY Brier | **.076962** | .116820 | **.095304** | .216386 |
| **RV+GVZ frozen Brier** | **.077488** | **.115477** | **.096095** | **.214232** |

RV+GVZ Brier vs static improves ALL four individual years by absolute .002886, .002562, .005102, and .030946, respectively. Relative 2025 ~5.0% and 2026 ~12.6% score improvement; vs causal rolling63 Brier improves all years too (.003572/.008253/.015350/.015183). **GVZ ONLY actually outperforms 2-feature RV+GVZ in 2023 and 2025**, so do NOT claim ex-ante RV incremental usefulness in all years. This result is a **probability risk forecast**, emphatically NOT a short-horizon UP/DOWN winner or bank strategy profit.

Ex-ante risk discrimination: compare top fifth vs bottom fifth by model P(down≥1.5%), AFTER scoring (no future features). On exactly same sample:
| year | quintile n | high-risk observed / n | low-risk observed / n | interpretation |
|---|---:|---:|---:|---|
| 2023 | 50 | 4/50=8% | 3/50=6% | almost no usable ranking |
| 2024 | 51 | **15/51=29.41%** | **2/51=3.92%** | meaningful historical risk separation |
| 2025 | 51 | **16/51=31.37%** | **1/51=1.96%** | meaningful observed historical risk separation |
| 2026 | 23 | **7/23=30.43%** | **6/23=26.09%** | ranking **COLLAPSED** |

Frozen RV+GVZ mean forecast risk 2025 .1724 despite true down event .1137 (overestimated), 2026 .2700 vs true .3103 (underestimated). 2026 historic static prior forecast .1339 misses regime shift and Brier .24518; RV+GVZ .21423 captures some LEVEL of elevated risk but **cannot meaningfully sort which 2026 dates are safest**. 2024/25 relative case control is useful, 2026 individual alarm cannot yet be trusted.

### R18 fixed Newey-West HAC L5 uncertainty diagnostic after discovery
Difference defined (baseline squared error)−(RV+GVZ squared error): positive = conditional model better. H3 overlapping targets require serial HAC L5, but only approximate normal CI after prior exploratory hypothesis selection, NOT independent study or robust confirmatory significance.
| year | N | mean Brier gain vs static | HAC SE L5 | naive normal 95% CI |
|---|---:|---:|---:|---|
| 2023 | 254 | .002886 | .002631 | [−.002271,+.008044] |
| 2024 | 256 | .002562 | .001400 | [−.000181,+.005306] |
| 2025 | 255 | .005102 | .005092 | [−.004878,+.015082] |
| 2026 | 116 | .030946 | .015707 | [+.000160,+.061732] |
These exploratory uncertainties plus repeated previous market inspection prohibit claiming prospectively proven predictive edge. Against GVZ-only, TWO-feature model's paired HAC CI includes0 all years; class GVZ as key driver, RV incremental *unproven*.

## 3. R15 absolute H3 >1.5% (EITHER direction) also improved 2025/26 but NOT always
| year | absolute-tail count | static Brier | RV+GVZ Brier | top fifth abs-tail | bottom fifth abs-tail |
|---|---:|---:|---:|---:|---:|
| 2023 | 60/254 | .18654 | .17996 | 12/50 | 5/50 |
| 2024 | 88/256 | .22779 | .22890 | 22/51 | 11/51 |
| 2025 | 111/255 | .26266 | **.24160** | 29/51 | 16/51 |
| 2026 | 63/116 | .30459 | **.24921** | 12/23 | 14/23 |
2026 risk forecast calibration gains not same as exante ranking; worse than baseline in2024. Per above, one-sided downside is more consistent probability target. Confirm supporting abs≥1% and≥2% tests were exploratory and not selection criteria.

## 4. R16 conservative online matured-only baseline and frozen+live hybrid
Matured rolling local formula `(4+number of D_i events with H3 end<current issue day among last63)/(8+n)` compared on every candidate. It is worse Brier than frozen RV+GVZ all 2023–26 despite allowing only available historical outcomes. Alternative frozen+half-strength matured intercept adjustment `clip log-odds shift +/-0.8` Brier for abs≥1.5%: 2023 .18363 vs RV+GVZ .17996,2024 .22864 vs .22890,2025 .23909 vs .24160,2026 .24889 vs .24921. This sometimes improves tiny amounts 2025/26 but no strong portability and 2023 fails. For DOWNside the same adjustment worsens 2025 .10061 vs frozen .09610 and2026 .21512 vs .21423. **Do not promote an adaptive gate**.

## 5. R15, R17 and R19 explicitly attempted to transfer risk skill to actual H3 UP/DOWN — and FAILED
**R15**: "only trade when H3 original PATH-CBR confidence exceeds training-only median" selected 2025 124/255, score BA51.46 vs all CBR53.14; 2026 selected52/116 score BA44.02 vs all46.82. Does not improve. 2023 selected99/254 BA49.88,2024 selected101/256 BA44.35. Confidence itself is miscalibrated for true signed accuracy.
**R17**: train separate fixed L2 RV+GVZ models for `P(H3≤−1.5%)` and `P(H3≥+1.5%)`. Sign`p_up−p_down` or fixed blended (50% CBR, 50% sigmoid(3 normalized difference)) BA:
| Model H3 signed BA |2023 N254|2024 N256|2025 N255|2026 N116|
|---|---:|---:|---:|---:|
| original price-only CBR | 51.36 | 49.62 | 53.14 | 46.82 |
| two-tail sign selector | 49.99 | 50.33 | 52.03 | 48.81 |
| frozen risk-tail + CBR 50/50 hybrid | 50.35 | 50.67 | **54.11** | 47.36 |
2026 sign selector predicts DOWN104/116 and UP12/116; 2023 predicts UP252/254 (near-always-UP). 2025 selective |risk-diff|>=.10 BA58.12/N120 but 2026 only BA48.21/N45 and zero UP recall, so not robust. These are NOT useful decisions.
**R19 one-sided hazard override**: if CBR predicts UP but frozen P(3d downside≥1.5%)>=.20, flip to DOWN or ABSTAIN. Threshold frozen before test but exploration already open. 2023/24 **zero overrides**; 2025 54 overrides (24 rescues,30 breaks, net−6 correct decisions), BA CBR53.14→override56.59 but raw60.39%→58.04% and UP recall80.75→62.11, DOWN25.53→51.06; coverage if abstain201/255=78.8%, decided BA55.31. 2026 87 overrides (55rescues,32breaks net+23 raw) causing **ALL-DOWN output**: BA exactly50% / UP recall0%, even though raw accuracy from41.38%→61.21% purely due down prevalence. 2026 abstention retains only29/116=25%, all predicted DOWN so BA50. **REJECT** despite superficial 2025/26 headline improvement. This is precisely the one-class degenerate trap user warned about.

## 6. What is now actually more precise, and hard limitations
We have a **measurable component improvement** that survives 2023–26 on year-separated risk probability score: lagged GVZ & last 4h gold volatility predict the CHANCE OF A LARGE THREE-DAY DOWNSIDE better than naive historical risk baselines on four individually scored years. However 2026 source-limited benchmark already inspected and 2026 high-v-low probability sort fails; therefore market deployable risk-alert/stop-loss and accurate signed call are NOT certified. The actual monthly 13D HMM is a MONTHLY market-state detector with 2026May/Jun transition failures, and cannot be injected as-of 08:45 with current month completed values; original monthly ChHHO model price-level skill and cross-metals were separately tested and failed transport. R19 shows why merely down-biasing 2026 is not innovation. No bank BID/ASK transaction costs, spread, real gold certificate fills. Overlapping H3 events not IID. Zero hidden data writes; all market-source SQL SELECT.
**Best scientifically defensible next stage:** Freeze R16 downside tail *probability* candidate as research comparator only, not a trader. Conduct source-certified independent true prospective 2027 with issue-time GVZ publication, full day-to-day monitored odds calibration and top-v-bottom downside rate by regime (particularly 2026-style), including a benchmark against readily known last quote/rolling past true volatility. Independently require a separate D1/H3 two-sided UP/DOWN model with genuine incremental forward signed information before combining into investment decisions.
