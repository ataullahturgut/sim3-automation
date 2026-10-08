# GOLD EXECUTION — Free Historical Data Acquisition Result — 2026-10-08

**Repository:** `ataullahturgut/sim3-automation`; **branch:** `gold-execution-channel-audit-20261006`.
**Evidence class:** actual GitHub Actions downloads, source receipts, private Neon ingestion and separately reproducible QC. **Paid historical download cost: USD 0.** **Model training / source promotion: NOT EXECUTED.**
**As-of:** 2026-10-08. **2026 data after the observation date were not requested.**

## 1. Completed zero-purchase sources

| Source | Actual date coverage | Valid records | Evidence / access | Acceptance |
|---|---|---:|---|---|
| Cboe GVZ daily | 2020-01-02 .. 2026-10-07 | 1,701 | `GOLD_EXECUTION_FREE_SOURCE_STAGE1_2026-10-08.json`; candidate CSV | Official source; 1,257/1,257 frozen overlapping rows exact; candidate PASS |
| Federal Reserve H.15 DGS2 daily | 2020-01-02 .. 2026-10-06 | 1,692 | same report; official candidate CSV | 757/757 overlapping rows exact; candidate PASS |
| Federal Reserve H.15 DFII10 real 10Y | 2020-01-02 .. 2026-10-06 | 1,692 | `GOLD_EXECUTION_DFII10_FED_H15_BACKFILL_2026-10-08.json` | Official source; no additional cross-vintage comparison yet |
| HistData XAU/USD M1 aggregated to M15 | 2020-01-01 23:00Z .. 2021-12-31 21:45Z | 47,188 M15 (2020 23,626; 2021 23,562) | `GOLD_EXECUTION_HISTDATA_XAU_FREE_BACKFILL_2020_2021_20261008.json` | Private Neon table, separate source candidate; never publicly exported raw prices |
| Twelve Data XAU/USD native M15 historical gaps | 2020-01-24 02:00Z .. 2021-12-31 20:45Z, with usual market closures | 45,295 M15 (2020 22,145; 2021 23,150) | `GOLD_EXECUTION_TWELVE_XAU15M_GAP_FETCH_20261008.json` | Private Neon table; monthly QC PASS, early January 2020 unavailable from Twelve; not promoted |
| Twelve Data XAU/USD native M15 recent | 2026-09-28 00:00Z .. 2026-10-08 11:45Z bar start | 1,008 M15 | `GOLD_EXECUTION_TWELVE_RECENT_XAU15M_GAP_20261008.json` | Private Neon separate candidate. Latest bar starts 14:45 Turkey and ends 15:00 Turkey. |

The full Twelve Data run had 46,015 candidate bars (2020 22,145; 2021 23,150; 2026 October 720); 720 October bars overlapped the earlier 1,008-bar recent acquisition and were not inserted again. The 2020/21 Twelve Data historical archive and 2026 late gap thus contain 46,303 distinct candidate timestamps across their covered years when combining the 46,015 run with the 288 additional Sept 2026 bars from the recent run; source receipts determine authoritative counts. The private insert in the full-history run added **45,295** records.

**Twelve Data earliest_timestamp for XAU/USD at 15min:** `2020-01-24 02:00:00` (reported by its API). Therefore early January 2020 is **not available from this provider**, and must stay in the distinct HistData series rather than being silently copied into the Twelve Data identity.

## 2. Cross-vendor and target-anchor quality

Historical Twelve Data vs HistData on **43,918** exactly matched UTC 15-minute closes:
- Absolute relative close discrepancy median = **2.8158056 basis points**.
- Absolute relative close discrepancy p95 = **32.8489909 basis points**.
- Twelve Data price higher than HistData in **72.3735%** of matched bars.
- These are different vendor quotations; even where close, the sources are not proven interchangeable, and cross-source price paths must not be spliced by default.

HistData 2020–2021 `Europe/Istanbul` trading-window spot check (NOT exchange-calendar-adjusted):
- 2020: 257 weekdays had 09:00/16:45/17:00 pivot bars, 256 weekdays passed complete DAY 32-bar plus 3-pivot native-minute checks, and 253 had 17:00 and next weekday 08:45 overnight pivots.
- 2021: 257 / 257 / 253 under the same definitions.
- 2020 missing DAY anchors include 2020-01-01, 2020-04-10, **2020-08-12**, **2020-11-30**, 2020-12-25. Missing dates must be classified against actual exchange trading calendars; never assume holidays. 2021 missing 2021-01-01, 2021-04-02, 2021-05-31, 2021-12-24.
- 2020-06-10 had an incomplete native-minute pivot bar in the HistData candidate (source receipt `GOLD_EXECUTION_HISTDATA_2020_2021_DAY_OVN_ANCHOR_QC_20261008.json`). This needs source-specific repair, not arbitrary interpolation.

## 3. Databento cost check, zero spend

The existing authenticated Databento key returned cost quotes without any historical price download:
- GC.n.0 one week of `ohlcv-1m`: approximately **USD 0.0252** (2020 sample), **USD 0.0251** (2024), **USD 0.0246** (2026).
- GC.n.0 `ohlcv-1h`: approximately **USD 0.1170** for 2020–2021; **USD 0.1035** for 2025–2026 through 2026-10-08.
- These are estimates, **not** purchases or confirmations of remaining account credit. Existing 2022–2024 frozen GC/SI/NQ/ZN/CL archives MUST NOT be purchased again.

## 4. Next scientific acceptance gates

1. Verify year/month/15-minute **missing-slot coverage** against actual session trading calendars; explicitly flag 2020-08-12, 2020-11-30 and the 2020-06-10 incomplete HistData pivot.
2. Define source precedence separately for Twelve Data historical native M15 and HistData-derived M15, and reject unapproved provider switching at key DAY/OVN bar boundaries.
3. Establish historical point-in-time availability, UTC/TR/DST mapping, native bar completion and unambiguous DAY/OVERNIGHT targets, with no imputations across market closures.
4. Maintain as separate research candidates until clock, source, overlap and gap audits PASS; only then create immutable labeled panels. Baseline-vs-expanded-history walk-forward tests belong after this gate.
5. Future phases: macro FOMC/CPI/NFP actual-vs-consensus publication snapshots; 2020–2021 and 2025–2026 missing futures coverage; 2020–2026 daily GVZ/rates PIT publication clock; bank executable bid/ask quotes. **Do not assert these phases are already complete.**

## 5. Raw source confidentiality and replay

- Official public raw history is in separately named `GOLD_EXECUTION_*_FREE_CANDIDATE_2020_20261007.csv` files; previously frozen source files remain unchanged.
- HistData M15 private Neon table `gold_research_histdata_xau15m_candidate` is keyed by source and UTC timestamp, with immutable conflict-avoidance; current vintage evidence does not prove contemporaneous 2020 publication.
- Twelve Data M15 private Neon table `gold_research_twelve_xau15m_gap_candidate` is a separate source identity; GitHub contains receipts, timestamps, counts, hashes and quality summaries, **not the licensed raw prices**.
- GitHub Actions runs: [official free GVZ/rates](https://github.com/ataullahturgut/sim3-automation/actions/runs/37772916485), [private HistData 2020–2021](https://github.com/ataullahturgut/sim3-automation/actions/runs/37773404445), [Federal Reserve real 10Y](https://github.com/ataullahturgut/sim3-automation/actions/runs/37773690263), [Twelve recent 2026 gap](https://github.com/ataullahturgut/sim3-automation/actions/runs/37774017550), [Twelve full 2020–2021](https://github.com/ataullahturgut/sim3-automation/actions/runs/37774411626), [DAY/OVN pivot QC](https://github.com/ataullahturgut/sim3-automation/actions/runs/37774556100).

No paid historical vendor request, macro label reconstruction, investment replay, or model retraining was completed in this acquisition stage.
