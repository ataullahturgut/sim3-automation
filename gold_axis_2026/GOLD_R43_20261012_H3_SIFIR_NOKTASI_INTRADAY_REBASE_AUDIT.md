# R43 — The H3 ZERO POINT: from original averaged price origin to Turkish bank-decision entry clock

**Audit date: 2026-10-12.** Requested by user: find a mathematically valid zero/reference point and align original, strong 3-day H3 directions to user-executable Turkish 09:00–17:00 windows. Do NOT score daily consensus or substitute 15:00 spot for original sqld daily mean. **No retraining, no invented issued-at.**

## 1. Source-authoritative reference and mathematical identity

Native **2026 May–Sep H3 target**: StakTrakr `source:sqld`, internally `AVG(spot)` over a COMPLETE UTC calendar day, thus Turkey **D 03:00→D+1 03:00** samples; the daily source row's `12:00:00` is a **synthetic date stamp**, NOT an observation at 15:00 Turkey. Original model `feature_cutoff_date` D0 source `P_0` and target `target_end_date_h3` D3 source `P_3`: `r_H3 = log(P_3/P_0)`. The `forecast_issue_date` is the next eligible recorded daily date after D0, i.e. the H3 label includes the first D0→D1 price change, and counts D3 as the third eligible source date after D0. Original H3 model predicts **SIGN(r_H3)**, not the numerical size of that move.

**Zero-point alignment to an available Turkish-hour entry**: Choose `P_entry(t)` from an independent native timestamped market source in Istanbul at 09 or 15. Exact deterministic identity:
`log(P_3/P_entry(t)) = log(P_3/P_0) - log(P_entry(t)/P_0)`.
- Original signed H3 direction reports only first term's **SIGN**, not its unknown numeric value.
- The second term is the **observed move between the model's own origin reference and the user's possible entry**. We can measure it with no target leakage once the original D0 `sqld` mean has actually been published.
- Therefore one **cannot mathematically translate a single UP/DOWN bit to a 09/15TR UP/DOWN bit with guaranteed accuracy**. A defensible transfer needs a **prediction of H3 return magnitude with uncertainty interval** and origin-safe publish/entry timing. A large signed gap in the model's direction can consume the original remaining-price cushion.

**Concrete example from original May 2026 unchanged DPTC Q95**:
- **2026-05-07** issue, prior native UTC-average origin **2026-05-06 `P_0=$4675.01`**.
- DPTC original H3 **UP**; original `2026-05-11` H3 target-day daily average Stak **$4701.32**, so original score **UP correct**.
- However independent 15min Dukascopy candidate **May07 15TR entry $4742.985**; same-provider May11 UTC-day target average **$4699.686** ⇒ entry-to-target **DOWN**, despite same original H3 correctly reporting UP. Original H3-up return ~**+0.56%** but entry spot already about **+1.45% above original price reference**.
- This is NOT inherently data leakage or a bad original H3 label. It is an **unaccounted origin gap**, i.e. exactly the user's proposed zero-point issue.

## 2. Cohort, source, reproducible test

**2026 Mar11–Sep25: 143 verified frozen H3 issue cohorts** with **both original feature-cutoff and target Gold source `sqld`**. Exclude original mixed source `seed/LBMA`, `seed/MetalPriceAPI`, `seed/StakTrakr` from principal analysis. Same original H3 votes from `GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv` + SAGE/RuleFlow V3-TG events + DPTC-Q95 exact `feature_cutoff_date`-keyed flips `GOLD_H3_DPTC_V1_ACTIONS_2026-10-05.csv`.

Independent intraday research feed `gold_research_histdata_xau15m_candidate`, `open_price` at 09:00 or 15:00 `Europe/Istanbul`; terminal on original H3 target date `AVG(open_price)` grouped by UTC date (same averaging clock as original). We use **same HistData vendor for origin reference, entry and target** when measuring entry-to-target return. This retrospective source is not a bank executed BID/ASK and data completeness differs on holidays. Independent Dukascopy-like BID/ASK midpoint feed available through **Aug20 only**, not full September, so never claim a paired full Sep test from Dukascopy.

**Repeat source fact already independently verified May, R42**: all 21 May original H3 label directions matched independently reconstructed UTC daily averages from BOTH HistData and Dukascopy, and DPTC-Q95 scored **17/21=80.95%** on each exact same old H3 daily-average target definition.

## 3. REBASE result, Turkish 15:00, all available March–September H3 homogeneous source

A comprehensive recheck of the comparable HistData derived test gives **140/143** timestamped 15TR issue prices and target means (April adds one available matching original issue period relative to the earlier 139-row preliminary pass; use the final 140 as denominator, NOT the old preliminary 139). For the 140:
- HistData-origin-average → H3 target-average: DPTC **98/140=70.00%**, original exact Stak H3 dataset on these rows also 98/140; independent HistData signs match the original H3 label on **138/140** source returns.
- **Issue-date 15TR spot → original H3 target-date UTC daily average:** DPTC only **80/140=57.14%** (always DOWN **82/140=58.57%**). No verified entry alpha.
- **09TR**: a parallel preliminary extraction is around **57%**; precise final 09TR count needs separate validation and MUST NOT be promoted as a production clock. The historical H3 issue-date `issued_at` is not archived, and the 09TR causal eligibility of every input publisher is not certified. Governing issue deadline in May was 08NY=15TR, not a verified first signal timestamp.
- The **signed gap** (g = d \log(P_{entry}/P_0)), where (d=+1) for original UP, (d=-1) for DOWN. At **15TR**:
  - gap **<+1%** in original model direction: **57/91 = 62.64%** entry-to-target correct (always DOWN **55/91 = 60.44%**).
  - gap **≥+1%** in model direction: **23/49 = 46.94%** correct (always DOWN **27/49 = 55.10%**).
  - This is DIAGNOSTIC, NOT a prespecified validated +1% trade filter. On remaining trades, model exceeds naive DOWN by just 2/91, and posthoc 2026 threshold/regime selection could overfit.

**A simpler 2026 May–Sep after-issue magnitude heuristic FAILED**:
- Use only already matured past homogeneous `sqld` H3 reference returns (`target_end_date_h3 < issue_date`), trailing up to 40 origins, minimum 20, to calculate rolling median historical `|r_H3|`. Assume a hypothetical numerical H3 target `P0 * exp(d * rollingMedian)`, then flip the direction if this point estimate is above/below the investor's instantaneous entry.
- **HistData 15TR May–Sep N=105**: unchanged DPTC vote **59/105=56.19%**, the magnitude-guess 'rebase/flip' **58/105=55.24%**. No improvement.
- **Dukascopy 15TR May–Aug partial N=78**: old vote **43/78=55.13%**, magnitude-guess 'rebase/flip' **38/78=48.72%**. Material degradation. Therefore **DO NOT PROMOTE** that automatic median magnitude/flip model.
- The rolling median estimate is strictly historical by source date but historical DPTC architecture itself is retrospective 2026/posthoc, so none of this is untouched independent OOS.

## 4. Scientific interpretation / how a real zero-point transfer should be built

**What has been demonstrated:** The *source clock* and *zero point* are now located and verified: Stak sqld full UTC daily average **03TR→03TR**. May old H3 17/21 is robust when independently benchmarked against the **same** original target. The investor entry-time direction is a **different label**: observed offset from P0 must be deducted from an actual numeric H3 forecast. The large signed gap identifies one structural failure mode (direction already realized/overshot by entry), but a fixed cutoff or trailing median does not prove predictive advantage.

**Next legitimate modeling**: Keep unchanged directional H3 experts. On original DEV / rolling PIT-safe data learn **conditional distribution or quantiles for 3-date `log(P3/P0)`**, using expert direction/probabilities, original as-of features and normalizations; estimate `P3` credible interval. At as-of available entry clock (prefer 09/15TR when all inputs and publisher timestamps pass), subtract known actual `log(P_entry/P0)` to obtain conditional *remaining* move and decide UP/DOWN/ABSTAIN only when lower/upper credible bounds separate zero by a prespecified margin. Then lock model and compare 2025/2026 truly held-out periods without choosing best provider/hour after seeing labels. For historical 2025 `seed/LBMA` origin is London's AM fixing (12:30/13:30TR auction starts), NOT same as 2026 `sqld` 03TR→03TR mean, so do not splice as comparable same-clock origins; define a cross-source bridge or train within each source regime.

**Important timing**: A completed UTC-average is only arithmetically finalized after D+1 03TR, and usable only when published; original H3 hourly Twelve Data feature ends 16:00NY prior `feature_cutoff_date` (23TR May; 00TR winter following midnight). The model's governed 08:00 NY=15TR (May) deadline does not prove actual old signal issuance time or that all features would already be released at 09TR. This remains an explicit readiness blocker for live bank execution.

**Main line:** The user correctly demanded a source-native reference zero point. We found it, replicated old performance, quantified direction loss under actual reanchoring, discovered a large gap hazard, and rejected a non-improving naive magnitude bridge. No more reinterpreting old H3 as a newly-trained daily predictor.
