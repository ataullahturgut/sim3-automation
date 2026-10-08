# GOLD EXECUTION — PRAMV V1 Original Architecture: Official 2025 Macro Repair and 2020–2025 Price Source Refit — 2026-10-08

**Result class:** ACTUALLY EXECUTED HISTORICAL RE-FIT / PRE-RELEASE-CONSENSUS-PIT RESTRICTION.  
**Frozen original PRAMV V1 authority and 7 October results: IMMUTABLE, NOT OVERWRITTEN.**  
**No new model champion, threshold change, or production trading clearance.**

## 1. Investigated and repaired actual macro data, not fabricated

Original `GOLD_MACRO_EVENT_LEDGER_RAW_V1_2023_2025.csv` retained in full. Official restored events in `GOLD_EXECUTION_PRAMV_OFFICIAL_2025_MACRO_SOURCE_GOVERNED_V2_20261008.csv` with source receipts.

| Year | FOMC scheduled release events | NFP first-prints paired | AHE + unemployment paired each | CPI reports (paired normal monthly) |
|---|---:|---:|---:|---:|
| 2021 | 8 | 12 | 12 | 12 |
| 2022 | 8 | 12 | 12 | 12 |
| 2023 | 8 | 12 | 12 | 12 |
| 2024 | 8 | 12 | 12 | 12 |
| **2025** | **8 (restored)** | **11** | **11** | **11 calendar, 10 comparable** |

**Fed 2025 restoration:** dates **Jan 29, Mar 19, May 7, Jun 18, Jul 30, Sep 17, Oct 29, Dec 10**, release **14:00 America/New_York**, with real summer/winter UTC offset. This schedule was announced **9 August 2024** and is legitimately known in advance. The previous ledger had **zero** 2025 Fed decision timestamps, incorrectly misinforming the model's `upcoming_fomc` feature. Fed: https://www.federalreserve.gov/newsevents/pressreleases/monetary20240809a.htm ; verified earlier FOMC schedules: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm .

**BLS 2025 actual release schedule:** 11 NFP reports and 11 CPI *calendar events*, rather than naïvely expecting 12 monthly reports for both, because of the federal shutdown. September 2025 NFP was released November 20; October 2025 employment reference report was canceled; November employment was released December 16. CPI for September was released **October 24**, CPI reference October canceled, and CPI for November was released **December 18**. Importantly, the latter is a **two-month cumulative change, not the usual monthly MoM actual**, so a comparable CPI MoM surprise cannot be assigned. Its **2025-12-18** issue date is explicitly **quarantined from exact macro-data test** rather than recording zero macro releases or falsifying a surprise. See https://www.bls.gov/schedule/2025/ and https://www.bls.gov/bls/2025-lapse-revised-release-dates.htm and https://www.bls.gov/news.release/archives/cpi_12182025.htm .

**Pre-2023 genuinely discovered in private Neon:** 2021 and 2022 `MACRO_{CPI,NFP,AHE,UNEMP}_{ACTUAL_FIRST_PRINT,CONSENSUS_PIT}` each have **12 paired observations per year**, and prior FOMC event archives provide 8 regular statement timestamps per year. Event/value pairs were audited by `observation_ts`, `available_as_of`, value, and historical duplicate-vintage agreement. The exact privately licensed source values remained ephemeral in the workflow/private Neon, and **are not committed publicly**.

**2020 is not silently assumed empty:** despite audited 2020 price data, its source has **11/12 NFP/AHE/UNEMP** record pairs and a Fed score archive of **13 2020 observations including extraordinary emergency events**. Unexpected emergency decisions cannot be retrospectively converted into *known future calendar* features. Consequently 2020 was deliberately excluded from M4's macro-feature training. No 2020 model score is invented.

**Unavoidable vintage qualification:** although `available_as_of` exists for legacy series and is at the reported event release time, all historical actual/consensus first-print sources were **ingested or reconstituted in 2026**. Their consensus information, independently archived *before* publication, has **not** been verified separately for every release. This is a scientifically **restricted retrospective source-as-of reconstruction**, **not complete independently certified historical real-time PIT data**.

## 2. Original algorithm preserved and actually refitted

Using the **141,890** structurally audited Dukascopy-derived 2020–2025 15m BID/ASK archive (BID used for model targets and decision features), re-ran:

1. Original `M4_SIG_FPCA_MACRO`: 3h price path, volatility, semivolatility, drawdown, sign changes, original signed lead-lag/time-price path signatures, PCA fitted on **training history only**, published macro event and prior-surprise features, future scheduled FOMC.
2. Original `StandardScaler + L2 LogisticRegression C=1`, **UP threshold 0.50**, original rolling matured-overnight historical training.
3. Original **RFR first-impulse reversal** rule: 16:00–16:30 versus 16:30–17:00 signs must oppose.
4. Original selective PRAMV: **ABSTAIN** when a paired macro surprise was released by 17:00; else M4 and first-impulse RFR must agree; issue only their common direction. **No confidence cutoff, second voter, or post-2025 tuned threshold.**
5. Matched **PAIR_ALL comparator** actually retrained on same price source and history; score on exactly PRAMV's selected dates.

**Training chronology:** 2022 is original model price warm-up year, 2023–2024 expanding prequential scores require fully matured prior overnight target, and **2025 has frozen parameters trained through 2024**. 2023/2024 are not untouched development holdouts and 2025 had previously been inspected in this project. Normal weekday **16h** and Friday-to-Monday **64h** are partitioned independently.

The accepted authority for results should be the **2022 original warm-up** replay, not the shortened start-in-2023 debugging run or expanded sensitivity. Its script reuses original M4, RFR and pair functions with source adapters; it is a **re-estimated version of original architecture**, not an identical 2026-10-07 frozen fit.

## 3. PRIMARY RE-TEST — original 2022 warm-up on new audited BID price source

| Year | Eligible source OVN | PRAMV issued | Coverage | Accuracy | Balanced accuracy (BA) | UP recall | DOWN recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| **2023** | 247 | **83** | **33.60%** | **62.65%** | **62.28%** | 66.67% | 57.89% |
| **2024** | 249 | **79** | **31.73%** | **54.43%** | **54.17%** | 60.98% | 47.37% |
| **2025 (examined retrospective)** | 248 | **81** | **32.66%** | **59.26%** | **56.16%** | 72.92% | **39.39%** |

2025 PRAMV confusion: `TN=13, FP=20, FN=13, TP=35`. PRAMV gets **48/81** correct, while same-case retrained PAIR gets **51/81** correct (**62.96%**). PRAMV rescues **6** of PAIR mistakes, breaks **9** correct PAIR cases, net **−3**. Its exact McNemar/binomial matched-pair p-value is **0.6072**. At this sample size and retrospective model search scope, the difference is *not* a proven PRAMV superiority.

**2025 nuance:** On the exact 81 selected days, the trivial always-UP action correctly predicts **48/81 = 59.26%**, identical to PRAMV raw accuracy (but always-UP BA is 50%); this cautions against treating 59.26% raw accuracy as standalone financial edge.

**Original 7 October frozen report is NOT reproduced by this new-source fitting:** 2025 original old-source frozen **63.41% BA / N82**, new-source original-2022-warmup **56.16% BA / N81**, on a different price-feed and possibly different covered dates; do not present 7.25-point subtraction as a same-case causal loss. Source-vintage differences and re-estimation must be disclosed.

## 4. SECONDARY HISTORY SENSITIVITY — training also includes 2021

| Year | N | Coverage | Accuracy | Balanced accuracy | DOWN recall |
|---|---:|---:|---:|---:|---:|
| 2023 | 65 | 26.32% | 63.08% | **62.31%** | 55.17% |
| 2024 | 61 | 24.50% | 59.02% | **59.19%** | 48.39% |
| 2025 | 61 | 24.60% | 62.30% | **57.72%** | 39.13% |

The 2021-inclusive extended warm-up used a **different macro training span**; it generated a different abstention set and cannot be compared using BA alone without an exact same-origin sample test. Neither version has all-year 2025 BA convincingly above 60%, and DOWN detection remains modest. **Do not choose history span by whichever version happened to look better on an already-viewed 2025 test.**

For completeness, the earlier, truly restricted 2023-only-start check had N39/67/77 for 2023/24/25 and BA50.00%/57.72%/58.75%, respectively; these are *warm-up-truncated diagnostic results* and not primary model authority.

## 5. Repair ablation and source validation

- Eight 2025 advance-scheduled Fed occurrences were restored and correctly visible only in their legitimate `upcoming_fomc` windows. Against the same original fitting and price source with FOMC calendar missing, repair changed **8** 2025 upcoming-FOMC flags and **4** M4 binary direction outputs in the **primary 2022-warmup** replay (**3** M4 direction outputs in the longer 2021-warmup sensitivity replay). It did **not** redefine PRAMV's macro veto.
- 2025 Dec18 CPI macro pair is non-comparable and is strictly excluded; old FOMC postdecision score is never passed as a fictional known-at-17:00 value.
- BID and ASK quote returns are not Turkish bank executable bid/ask. Performance does not include spreads, order execution, funding, bank hours or capital curve.
- Date-level origin decisions, probabilities, gate reasons and repaired/missing FOMC ablations were preserved as GitHub Actions artifacts; only aggregate metric/manifest receipts were committed. Original results stay intact.

## 6. Final outcome, release gate and actionable research implications

**Data-layer 2025 FOMC/BLS repair: PASS (calendar).** 2021–22 macro source availability: **PASS for the required archived family counts and scheduled FOMC events**, with the historical point-in-time *consensus-vintage* qualification. 2020 remains **SOURCE-INCOMPLETE** for those macro families.

**Full original PRAMV M4/RFR/veto architecture: ACTUALLY RERUN** under audited 2020–25 quote source using faithful 2022 start; valid research metrics for 2023–25 above. **Unchanged frozen V1 as-of 7 Oct 2026 prospective validation: NOT performed**; 2025 was already examined. The current reestimated original architecture **does not provide replicated robust 2023–2025 balanced >60% edge** and is **not promoted**.

Before improving or deploying, separate (1) consensus pre-release archived-vintage certification, (2) 2020 incomplete event history and unscheduled decisions, (3) source-executable quote spread and 17:00 bank-origin tradability, (4) as-of 2026-10-08+ truly prospective original frozen parameters. No remaining discrepancy may be concealed behind a no-event=0 missing-value substitution.

## 7. Reproducibility artifacts

2025 official macro:
`GOLD_EXECUTION_PRAMV_OFFICIAL_2025_MACRO_SOURCE_QC_20261008.json`,
`GOLD_EXECUTION_PRAMV_OFFICIAL_2025_MACRO_SOURCE_GOVERNED_V2_20261008.csv`.

Earlier macro PIT availability:
`GOLD_EXECUTION_PRAMV_PRE2023_MACRO_SOURCE_AVAILABILITY_AUDIT_20261008.json`;
`GOLD_EXECUTION_PRAMV_ORIGINAL_FULLER_HISTORY_2021_2025_SOURCE_MACRO_RETEST_20261008_MACRO_PRE2023_QC.json`.

**Primary 2022 warm-up:**
`GOLD_EXECUTION_PRAMV_ORIGINAL_2022_WARMUP_SOURCE_MACRO_RETEST_20261008_SUMMARY.json`,
`GOLD_EXECUTION_PRAMV_ORIGINAL_2022_WARMUP_SOURCE_MACRO_RETEST_20261008_YEARLY_METRICS.csv`.

**Secondary 2021-expanded:**
`GOLD_EXECUTION_PRAMV_ORIGINAL_FULLER_HISTORY_2021_2025_SOURCE_MACRO_RETEST_20261008_SUMMARY.json`,
`GOLD_EXECUTION_PRAMV_ORIGINAL_FULLER_HISTORY_2021_2025_SOURCE_MACRO_RETEST_20261008_YEARLY_METRICS.csv`.

Original-architecture Python runners (2026-10-08):
`tools/gold_execution_pramv_official_macro_repair_20261008.py`,
`tools/gold_execution_pramv_pre2023_macro_inventory_20261008.py`,
`tools/gold_execution_pramv_repaired_full_retrain_20261008.py`,
`tools/gold_execution_pramv_2021_2025_history_expansion_20261008.py`.

Successful GitHub Action workflows: official macro repair (run 37811660809), 2023-only first full macro M4/RFR test (37812145420), macro 2021/22 private history evidence (37812421788), history-expanded full refit (37813136572 and strict source-publishing replay). The test dates are all **historical retrospective** even if publication was 2026-10-08.
