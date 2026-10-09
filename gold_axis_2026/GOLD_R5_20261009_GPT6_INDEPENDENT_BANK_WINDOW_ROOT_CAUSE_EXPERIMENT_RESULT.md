# R5 GPT-6 directly executed new research: bank-window sign-label robustness and macro-conditioned DIR4 failure
**2026-10-09 • ACTUAL NEON READ-ONLY LIVE SQL • HISTORICAL RETROSPECTIVE, NOT NEW DEPLOYED CHAMPION.**
No RD-Agent subscription, installation, LLM API costs or additional datasets were required. User asked to have GPT-6 directly lead and execute the research. Two independent falsifiable mechanisms were tested (not just a plan). Frozen original B4 and DIR4 preserved; no post-2026 fit, no parameter optimization.

## 1. R5A methodology — 15-minute matched source endpoint sensitivity
**Original preregistration BEFORE queried effects:** `GOLD_R5_20261009_TWO_BANK_WINDOWS_ENDPOINT_FRAGILITY_PREREG.md`.
Source 2023–25 target+quote single SOURCE_ID: `gold_research_evduka_xau_session_target_candidate_v1` + `gold_research_evduka_xau15m_bidask_candidate`; 2026 separate first-party native 15min panels `gold_research_dukascopy_2026_direct_m1_m15_bidask_v2`, strict `m1_matched=15`. Same Dukascopy upstream, not cross-vendor independence; 2026 already inspected, no untouched validation.
All clocks `Europe/Istanbul` with strictly start-labelled M15 BID+ASK midpoint close=end of 15-minute candle. Full original DAY09→17 is source close start08:45 vs start16:45, OVN17→next09 is source close start16:45 vs next08:45. Four anchors tested per date. Matched labels start-only15min later, end-only15min earlier, and BOTH shifted inward 15min. OVN only strict next-calendar regular weekday, no Friday weekend. Shifted targets only research robustness; a bank buy at17:15 is NOT a permitted execution recommendation.
Validate historical original midpoint return sign against canonical day_y/ovn_y. **0 sign mismatch** on all date and anchor qualified 2023–25 cohorts (original target).
The year tables below count 'fully four-anchor usable, nonzero original and all three shifted outcomes'; 2023 DAY one additional date with zero shifted-only return omitted from the strict full-shift comparison. The separately frozen DIR4/B4 side-by-side table requires original+BOTH nonzero only, hence 2023 DAY N256 vs strict multi-shift N255. This is a denominator transparency detail, not a source conflict.

### Actual clock sensitivity: percentage of labels whose UP/DOWN sign changes
| Target/year | Full 4-anchor N | ANY of three shifts flips original sign | BOTH shifts flips sign | Median original abs return, bp |
|---|---:|---:|---:|---:|
| DAY 2023 |255|44 (**17.25%**)|32 (**12.55%**)|27.63|
| DAY 2024 |259|35 (**13.51%**)|25 (**9.65%**)|34.02|
| DAY 2025 |258|32 (**12.40%**)|20 (**7.75%**)|36.74|
| **DAY 2026**|147|25 (**17.01%**)|20 (**13.61%**)|54.97|
| OVN 2023 |198|21 (**10.61%**)|17 (**8.59%**)|32.45|
| OVN 2024 |198|30 (**15.15%**)|24 (**12.12%**)|30.77|
| OVN 2025 |198|19 (**9.60%**)|16 (**8.08%**)|52.04|
| **OVN 2026**|103|7 (**6.80%**)|4 (**3.88%**)|73.44|

2026 DAY 147 all-anchors: if original magnitude <10bp, **13/14 (92.86%)** flip under at least one of three ±15minute execution windows; 10–25bp **7/21 (33.33%)**, 25–50bp **4/29 (13.79%)**, and ≥50bp **1/83 (1.20%)**. The magnitude is measured from realised future price and **CANNOT be known to gate trades at issue time**. 2026 OVN small under10bp **6/8 (75%)** flip; ≥50bp **0/64**. This is characteristic binary boundary instability of tiny net-move labels, not itself a coding error.

### EXACT same fixed historic DAY predictions rescored on both shifted endpoints
B4 = sign(last 16 completed M15 return sum), DIR4 = original frozen dominant M15 square-share >=.50 reversal else B4. Predictions are **BIT-IDENTICAL**, just use hypothetical later entry/earlier exit to rescore labels; never feed shifted prices to predictions.
| Year | N same DIR4-ready days | B4 original BA | DIR4 original BA | B4 BOTH-shift BA | DIR4 BOTH-shift BA | BOTH labels flip count |
|---|---:|---:|---:|---:|---:|---:|
| 2023 |256|48.34|50.97|45.88|46.84|32|
| 2024 |259|50.43|52.89|46.60|51.56|25|
| 2025 |258|53.94|55.58|55.60|58.61|20|
| 2026 |147|53.03|56.30|51.43|56.10|20|

**Falsified explanation:** 2026 DIR4 balance **56.30→56.10**, barely changing when both hypothetical execution boundaries shift inward. So the modest 2026 DAY skill is NOT simply created by exact candle-boundary selection; 2026 OVN source labels show even fewer shift flips. Original target label confusion is still **critical for the old 74.4% daily consensus**, but *clock fragility of correctly built 09/17 labels is not sufficient* to explain lack of higher signed accuracy.
**Research risk:** 2025 BA unexpectedly rises 55.58→58.61 under hypothetical shift, while 2023 falls50.97→46.84. A retrospectively selected clock would overfit; do not optimize entry/exit using such hindsight, especially after bank17 or if not tradable.

## 2. R5B methodology — CPI/NFP release dates vs original frozen DAY price-path model
**Separate original preregistration before the outcome-dependent event split:** `GOLD_R5_20261009_US_MACRO_INTRADAY_DAY_DIR4_ERROR_DIAGNOSTIC_PREREG.md`.
2023–25 US first-print release events from preexisting governed calendar source `GOLD_EXECUTION_PRAMV_OFFICIAL_2025_MACRO_SOURCE_GOVERNED_V2_20261008.csv`; include exact CPI or NFP timestamp only if observed announcement local timestamp between09:00 inclusive and17:00 exclusive. Dedup NFP unemployment/wage sidecars. No actual releases, surprises, forecast consensuses or future contents used; outcome labels from same source as inputs. These dates were reconstructed after years ended: does NOT prove genuine historical schedule knowledge at 08:45. Result cohorts are small (~22–24 days/yr), no train/adaptation.

### First three years, DAY DIR4:
| Year | Scheduled CPI/NFP qualifying N | DIR4 EVENT BA / ACC | DIR4 NO-EVENT BA / ACC | Event correct/N |
|---|---:|---:|---:|---:|
| 2023 |23|**43.08 / 43.48%**|51.58 / 51.93%|10/23|
| 2024 |24|**52.86 / 50.00%**|53.39 / 53.62%|12/24|
| 2025 inspected |22|**45.45 / 45.45%**|56.73 / 57.20%|10/22|
The static assumption 'on CPI/NFP releases, never trade because DAY prediction is bad' looks plausible in 2023/25 but is NOT a universal fixed signed law from this tiny population.

### Fourth-year independent clock-source extension
**Separate 2026 source/date prereg written before native event-target scoring:** `GOLD_R5_20261009_US_MACRO_DAY_2026_NATIVE_EXACT_SCHEDULE_EXTENSION_PREREG.md`. Official US BLS current historical event schedule: https://www.bls.gov/schedule/2026/home.htm ; copied 2026 Jan-Oct09 exact CPI and NFP dates in prereg and used only released before2026-10-09. Native 2026 17 fully completed pre-origin M15, source-qualified two target endpoints, n147. Previous author expected data might begin March; **ACTUAL NATIVE ALSO CONTAINS 2026-01-13**, accepted after inspecting actual source; do not assert that any month was absent on presumption. Calendar has19 recorded events Jan–Oct02; **14/19 event dates have full matching source**. Five absent/underqualified: 2026-01-09, Feb11, Feb13, Mar06 and Apr03 (not 'no event'). All date counts disclosure below.
| 2026 source-complete DATE stratum | N | Exact same DIR4 correct / N | DIR4 accuracy | DIR4 BA | DOWN recall |
|---|---:|---:|---:|---:|---:|
| CPI/NFP observed announcement date |14|**11/14**|**78.57%**|**78.89%**|80.00%|
| Other ordinary DAY dates |133|**71/133**|**53.38%**|**53.81%**|61.90%|
| All source-complete DAY |147|**82/147**|**55.78%**|**56.30%**|63.24%|

The model itself didn't switch its prediction on 2026 CPI/NFP event days relative to B4 (on event-days BOTH correct11/14); the gain comes from **event dates' realised direction correlated with original before09 price trend**. 2023/24 similarly no original DIR4-B4 interventions on release days; 2025 original DIR4 changed 1 release-day decision in positive direction. Important: model may be lucky in 2026 event dates; 14 DAYS and inspected outcomes, NO statistically established event-regime predictability or eligible risk-veto. Strong sign of a **time-varying conditional association**: 2023–25 fixed macro event exclusion would suppress 2026 highest-performing subgroup, not help.
2026 event median absolute DAY move ~82.82bp, non-event~54.66bp: *post-outcome*, context only, not preorigin trade classifier.
When old causal macro event calendar was tested for PRAMV overnight 17→next09, U.S. 08:30 release is actually inside DAY, not OVN; hence do not transplant this DAY finding to night risk without own event schedule and event timing.

## 3. Actionable scientific decisions — NO MODEL PROMOTION
1. **Data integrity finding:** for 2023–25, new same-source 09/17 original MID sign equaled governed stored y for all used dates. DID NOT detect new implementation leak in this narrow label contract. Clock fragility is nontrivial for under10bp realized moves; small-net moves' class instability alone cannot explain 2026 ~56% daytime BA nor 2026 night BA60.31.
2. **Conditional regime finding:** a release-day DAY prediction correctness pattern that appears bad in2023 and2025 reversed completely in2026. Reject any static rule to veto US release days, and reject naive 2026-only event-day model accuracy 78.6% as predictive skill. Future experiments should ask whether pre-08:45 **observable** FX/yield and preannounced event-time uncertainty interact, not whether today's outcome can be used to select easy days.
3. **Selection bias:** 2026 first-party native cohort n147 DAY /103 overnight are *source-complete selected dates* not all weekdays and same Dukascopy upstream as legacy quote publisher. 2025/26 outcomes inspected; no virgin independent holdout.
4. **What to work on rather than RD-Agent:** under-10bp and bank spread require **live before09 and before17 bank BUY/SELL executable bid/ask**, not arbitrary 15m clock optimization; for scientific directional signal require independently observed pre-origin US 2Y yields, FX, GC order-flow with PIT source, check correlation and economic mechanism, test on fixed matched date. Existing Twelve Data H1 EURUSD/USDJPY static sign overlay R4 failed yearwise; don't rerun/retune it.
5. **Next bounded test**: bank-execution quote feed readiness/permission + pre-issue PIT feature entitlement gate, then anchored risk/cost decision calibration; otherwise no plausible robust high directional accuracy claim.
6. Historical macro release schedules themselves may have been revised. A static event-date list recovered years after the fact is an ASSOCIATION diagnostic. Full prospective preissue schedule provenance still pending, not verified by retro source.

## Reproduction notes (no raw market quotes shared)
- All statistics calculated within isolated JavaScript over **read-only Neon SQL** result rows (no table writes, model fitting, or external AI provider calls). Historical source gate quote group and date `issue_date` exact with 17 previous completed M15 observations, no current-window price features.
- Clock labels: `sign(log(mid(exit)/mid(entry)))`; shifted clock labels alter *only* entry and exit anchor. `min(abs(r15))` zero not imputed; additional zero result excluded where strict multishift comparison needs sign.
- Count inequalities and bin bounds frozen at <10bp,10–25bp,25–50bp,>=50bp before seeing outcomes. Any flip includes changed sign for start-only or end-only or both. BA is `(TPR_DOWN+TPR_UP)/2`, raw accuracy is correct / N.
- Existing original frozen B4 and DIR4 formula from `GOLD_MULTIDISCIPLINARY_THREE_MECHANISM_PREREG_20261009.md`, with no model recalibration or 2026 fitting.
- No user bank execution or transaction profits were run. All y labels after preissue origin are *evaluation only*. Neither RD-Agent nor DeepSeek scored this dataset. Treat rates and covered dates as descriptive, no false significance.
