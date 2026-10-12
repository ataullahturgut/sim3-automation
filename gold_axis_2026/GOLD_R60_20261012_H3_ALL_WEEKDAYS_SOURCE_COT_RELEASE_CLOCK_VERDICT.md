# R60 — H3 ALL weekdays: 1,029 origin/issue/target and source-publication clocks, COT holiday repairs

**Date:** 2026-10-12. **Research source/clock authority: closed on currently observable date metadata; no production forecast replacement.**
**Explicit mandate:** all Mondays, Tuesdays, Wednesdays, Thursdays and Fridays, not solely Friday COT, and stop endless repeated verification. Respect frozen H3 D0→third retained observation-day D3 price-mean target.

## 1. Per-origin complete-week audit — ACTUALLY CALCULATED

Using directly fetched repository input rows:
- `GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_OPAL_PANEL.csv`: **1,029** dated H3 forecasts (June 2022–Sep 2026);
- frozen 4-metal daily price calendar: **4,233** retained dated rows;
- `GOLD_H3_DIVERGE_PROXY_V1_PANEL_2026-10-03.csv`: **1,029** macro cross-market dated sources;
- SAGE IFBC snapshot: **280** dated rows (hour bar and CME trading date);
- SAGE LLRS snapshot: **332** dated rows (hour source and bar completion);
- `GOLD_COT_GOLD_PIT_STATE_RAW_REBUILT_2026-10-06.csv`: **1,060** report records (1,034 fully populated for 14 OPAL COT features);
- R56 HELIOS replay `GOLD_R56_20261012_H3_FRIDAY_COT_DYNAMIC_HELIOS_V1_V5_931ROW_REPLAY.csv`: **931** dated rows.

**Clock assumption for this retrospective exercise:** forecast issue **15:00 Europe/Istanbul**. This is the research model's assumed issue time, **not proof that a May 2026 live order was actually placed**. D0 daily UTC-mean bar finishes at 00:00UTC (= next civil date **03:00 TRT**). The issue timestamp of 15:00 TRT must follow full D0 completion. The actual D3 target is third *retained source date* after D0, not “+72 hours”, +3 generic weekdays or COMEX business days.

| Forecast issue weekday | Complete forecast dates | Corrected new-release COT differs from intentionally lagged legacy COT | Correction required to earlier R56 `Friday+3d` assumption |
|---|---:|---:|---:|
| Monday | 165 | 157 | 4 |
| Tuesday | 208 | 203 | 0 |
| Wednesday | 220 | 17 | 0 |
| Thursday | 220 | 17 | 0 |
| Friday | 216 | 16 | 1 |
| **TOTAL** | **1,029** | **410** | **5** |

**Full-window source-day gate:**
- **1,029/1,029:** D0 exists in frozen daily-price source; D1 matches next retained priced day and D3 exactly matches third future retained priced day.
- **1,029/1,029:** all **five** metal, USD, US yield, Nasdaq and VIX source-date metadata are present and **not later than the D0 cutoff date** (5,145 date field checks).
- **280/280** IFBC hourly *bar completion* timestamps precede the assumed 15:00 TRT issue and CME trade date is not later than D0.
- **332/332** LLRS 1H bar completion timestamps precede the same assumed issue time.
- **1,029/1,029** corrected chosen COT publication timestamps precede the assumed issue time; no calendar-rule future use after applying the documented amendments.
- **931/931** the original R56 COT report picks were replicated under their original `report_date+3d Friday` rule, which is now **KNOWN NOT TO BE FULL HOLIDAY-CORRECT**.

This is genuine *calendar/metadata* parity; provider archive release firstprints, price revisions and true historical order issue timestamps are **not proven** by this test.

## 2. Important correction: published COT reports are NOT always Friday

The R56/R59 `Tuesday position date +3 calendar days` assumption mistakenly makes a holiday-shifted publication available on Friday (or even Thursday for a Monday as-of report). CFTC official **2026** calendar explicitly says Jan05, Jun22 and Jul06 are Monday release dates (15:30 New York). 2023 Jul03 and 2025 Jul01 early-July reporting-week date corrections have separately dated contemporaneous gold COT report publications July07, 2023 and July07, 2025, respectively.

| Forecast issue (15:00 TRT assumed) | Previously selected COT positioning date (R56) | Correctly eligible previous published positioning date | Why |
|---|---|---|---|
| **2023-07-07 Friday** | 2023-07-03 | **2023-06-27** | July03 report published on July07, **after** assumed issue clock |
| **2025-07-07 Monday** | 2025-07-01 | **2025-06-24** | July01 report published on July07, **after** assumed issue clock |
| **2026-01-05 Monday** | 2025-12-30 | **2025-12-23** | Official CFTC release **Jan05 at 15:30 New York**, after 15:00 TRT |
| **2026-06-22 Monday** | 2026-06-16 | **2026-06-09** | Official delayed CFTC release **Jun22 15:30 New York** |
| **2026-07-06 Monday** | 2026-06-30 | **2026-06-23** | Official delayed CFTC release **Jul06 15:30 New York** |

- CFTC official: https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm
- 2023-07-07 dated contemporary gold COT / positions as-of July03: https://goldseek.com/article/cot-gold-silver-usdx-report-july-7-2023
- 2025-07-07 dated contemporary gold COT / positions as-of July01: https://goldseek.com/article/cot-gold-silver-usdx-report-july-7-2025
- CFTC other one-off publication/2023 outage and 2025 shutdown record: https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalSpecialAnnouncements/index.htm

The 2023/2025 contemporary publication articles substantiate calendar dates but are not archived proof of exact CFTC 15:30 firstprint timestamp; this distinction is kept in the evidence status. All previous **21** CFTC documented special source-report release overrides are retained. **Five additional report-week date corrections** are layered non-destructively in R60. For 2022–2025 ordinary weeks, actual historical publication firstprints are not all in the current data; *unverified holiday weeks must be governed conservatively rather than presumed Friday certified*.

The clock-corrected new COT selections differ from frozen legacy `+7d` selections on **410/1,029**, not the earlier R55 estimate of **415/1,029**. Four of five newly corrected issue dates are Mondays and one is Friday. This is a release-timestamp/calendar repair, **not** an optimization based on gold outcome.

## 3. What remains scientifically true — and what R60 invalidates

- H3 D0/D1/D3 pricing calendar and cross-market **source-date metadata** meet the historical date-level checks above; no forced conversion into an hourly same-clock trade target.
- OPAL's old conservative +7d policy remains an intentional versioned freshness policy. The release-first research policy is separately recorded; neither requires changing frozen labels or overwriting OPAL features.
- **R56 and R59 release-first challenger are no longer FULL event-time clean** at the five issue rows. Three lie in 2026: Jan05, Jun22, Jul06. The R59 **129/191** controlled replay **must not be represented as the correctly holiday-adjusted successor score**. OPAL is rolling re-trained, so correction of five input rows may affect later model coefficients and downstream HELIOS gates; changing just five output votes is mathematically insufficient.
- May 2026 has **no direct issue-date correction** in the five above, but because OPAL refits on previous training windows even a 2025 feature repair could indirectly affect its later probabilities; no May score is claimed newly certified.
- 2026 model/target labels are retrospective in October; no sound “2026 live forecast success rate” may be inferred.
- Source-level contemporaneous firstprint and absolute original issue-time evidence for provider price, macro, CME, 1H markets remain **unavailable or unverified**. This is an explicitly identified limitation, not a reason to repeatedly replay identical unchanged archive files.

## 4. Closure decision and next scientific operating rule

**CLOSE all-weekday historical date-label reconciliation** on the 1,029-row input universe: the temporal *structure* passes, five identifiable COT holiday-release date errors are recorded, and exact-origin provider availability is explicitly `UNPROVEN`. DO NOT repeat R41–R59's frozen label validation without **new** source evidence.

For a genuine next H3 comparison, **use R60's corrected release calendar** and fail-closed release-time as-of feature joining; older historical holiday publication timestamps without proof must use a conservative delay or be individually marked unverified. Then train a newly versioned OPAL challenger and roll chronological HELIOS→SAGE/RuleFlow→DPTC once, with no posthoc threshold adjustment. Accuracy is a subsequent measured endpoint, **not** the criterion for whether dates are "correct."

**Actual artifacts:**
- `GOLD_R60_20261012_H3_ALL_WEEKDAYS_SOURCE_COT_RELEASE_CLOCK_1029.csv`: 1,029 rows × explicit forecast weekdays, D0/D1/D3, issue assumed timestamp, legacy/R56/corrected COT report and release timestamp, five macro source dates, 1H bar completion clocks, CME trade date, separate PIT-unknown status.
- `GOLD_R60_20261012_H3_ALL_WEEKDAYS_SOURCE_COT_RELEASE_CLOCK_SUMMARY.json`: numerical counts, impacted dates, daily partition and evidence limits.
- `tools/gold_r60_h3_all_weekday_asof_source_clock_audit.py`: reproducible all-origin parity rerun with assertions. **Not executed in connected GitHub-only runtime**; row ledger and all quoted metrics **were computed independently in JavaScript** directly over repository input CSVs.

**Frozen operational model remains unchanged. R59 (old 135/191; R59 controlled 129/191) retained as a historical, qualified counterfactual, not silently deleted or re-labelled.**
