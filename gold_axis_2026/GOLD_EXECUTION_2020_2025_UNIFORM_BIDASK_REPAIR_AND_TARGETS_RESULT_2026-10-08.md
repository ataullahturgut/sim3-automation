# GOLD EXECUTION — UNIFORM XAU/USD BID/ASK DATA RECOVERY AND VERIFIED EXECUTION WINDOWS — 2026-10-08

**Status: VERIFIED 2020–2025 SIX-YEAR UNIFORM HISTORICAL QUOTE RESEARCH SOURCE + PRIVATE TARGET CANDIDATE. 2026 SAME-SOURCE EXTENSION NOT YET ACCEPTED.** Prior frozen original prices, model forecasts, and manifests retained. No paid historical download.

## A. Actual repair / alternative vendor found

A fully separated, homogeneous **XAU/USD BID/ASK 15-minute archive for 2020–2025** was recovered from the free public closed-year EV Trading Labs series derived from Dukascopy feeds. License: free with attribution to EV Trading Labs, educational research; vendor historical observations are **NOT bank-executable quotes** and not historical point-in-time data vintages.

Public source: https://evtradelabs.com/data  
Data provenance: `https://evtradelabs.com/api/simulator/data/XAUUSD/M15/{year}.json.gz`, valid for prior closed years (the current 2026 archive requires an external free-account authorization and was **not bypassed**).  
Official direct comparator: `https://datafeed.dukascopy.com/datafeed/XAUUSD/{yyyy}/{zero_based_month}/{dd}/{BID|ASK}_candles_min_1.bi5`.

All quotes and labels were saved **privately** in separate Neon tables:
- `gold_research_evduka_xau15m_bidask_candidate` — `source_id=EVTRADINGLABS_DUKASCOPY_DERIVED_XAUUSD_M15_BIDASK_2020_2025_V1`.
- `gold_research_evduka_xau_session_target_candidate_v1` — source-stable research origins, both BID/ASK window-return variants, explicit maturity gate and bid/ask sign disagreements.
- Old frozen XAUUSD/HistData/Twelve quote series are intact in separate identities; no mixed-vendor target bar series was produced.

### Exact dataset coverage and research window eligibility

| Year | Bid+ask M15 bars | Issue dates | Complete DAY (TR 09–17) | Complete OVERNIGHT (TR 17–next09) | Excluded DAY | Excluded OVN |
|---|---:|---:|---:|---:|---:|---:|
| 2020 | 23,702 | 259 | 258 | 251 | 1 | 8 |
| 2021 | 23,626 | 258 | 258 | 250 | 0 | 8 |
| 2022 | 23,647 | 258 | 258 | 248 | 0 | 10 |
| **2023** | **23,544** | **257** | **256** | **247** | **1** | **10** |
| 2024 | 23,733 | 259 | 259 | 249 | 0 | 10 |
| 2025 | 23,638 | 258 | 258 | 249 | 0 | 9 |
| **TOTAL** | **141,890** | **1,549** | **1,547** | **1,494** | **2** | **55** |

All six calendar years contain **zero bars during conservatively definitely-closed UTC weekend intervals**, and the source BID/ASK timestamps, positive prices, high/low validity, no crossed quotes and exact UTC M15 grid were verified before private storage.

**2023 gap actual result:** prior HistData 2023 had 20,600 M15 bars, native M1 gaps particularly Jan–Jul, and the HistData-only research gate allowed just **136 DAY / 145 OVN**. New uniform provider has 23,544 M15 bars; **3,413** timestamps from this source were absent in HistData 2023. The **same-source** 2023 target gate now permits **256 DAY / 247 OVN**. Therefore the prior historical coverage bottleneck was actually repaired **in an alternative same-provider 2020–2025 universe**, not by inventing quotes or padding HistData.

**Primary-feed crosscheck:** 276 exactly matching M15 timestamps between the third-party annual 2023 dataset and independently downloaded native direct Dukascopy M1 BID/ASK archives show median **0.02496 bps** abs BID-close difference and p95 **0.02556 bps**, with ASK p95 **0.02555 bps**. Thus mirrored annual data strongly agrees with Dukascopy's native 1m feed on this sampled subset. The 276-bar check is **not proof of exact tick identity for all 141,890 bars**.

**Execution-clock label calculation:** DAY 06:00 UTC source BID OPEN to 13:45 UTC source BID CLOSE, requiring every 15m interval of the daylight path; OVN 14:00 UTC BID OPEN to next expected weekday 05:45 UTC BID CLOSE, requiring valid anchors and regular-night path density. The same computation is retained for ASK returns, and BID/ASK directional disagreement is recorded rather than conflated. For 2023, **0 DAY** and **1 OVERNIGHT** BID/ASK same-vendor target sign differences. No arbitrary UP/DOWN threshold or modeled future value filled missing days. <=10 bps signals are separately flagged as research ambiguity.

## B. What is and is not certified

**PASS — one-source historical research data:** 2020–2025 uniform M15 BID/ASK quote definitions, raw file hashes, all-year calendar integrity and same-source target maturity controls; independently sampled primary-feed corroboration; 1,547 DAY and 1,494 OVERNIGHT quote-return signs in private Neon. No licensing/source switching chosen based on 2025 forecasting accuracy.

**NOT YET PASS — real-world execution truth:** price is a Dukascopy-derived broker BID/ASK, **not** the user's Turkish bank price or zero-spread MID; spot market calendar/holidays and native-M1 completeness for every EV source candle were not fully certified; historical price series were downloaded on Oct 8 2026 and do not prove the original source's public availability at each backtest origin.

**2026 remains a separate, PARTIAL price universe:** 17,616 HistData XAUUSD M15 BID candles Jan–Sep 2026 are privately source-gated with 191 eligible DAY / 185 eligible OVN candidate labels. Dukascopy direct primary M1 BID+ASK **2026-10-05** yielded 96 valid M15 candles during pilot (with 2023 3 valid direct BID/ASK days). Some October dates returned HTTP 503 and are NOT silently imputed or marked complete. EV 2026 public annual file requires account access. October 8 2026 future candles were never requested or labeled as realized before maturity.

**MODEL POLICY:** neither PRAMV V1 nor existing consensus nor LIT champions were promoted or claimed improved. Comparing forecast results across frozen and newly accepted price source demands same-source entire labels/features and same matched prediction origins. True executable bank P&L remains data-gated.

## C. Immutable proof and reproducibility

- `GOLD_EXECUTION_DUKASCOPY_XAU_BIDASK_PILOT_2026-10-08.json` — direct native April 2023 and Oct 2026 sample receipts, 384 private M15.
- `GOLD_EXECUTION_EV_DUKASCOPY_XAU_2020_2025_UNIFORM_CANDIDATE_20261008.json` — all 6 annual native public gzip hashes, price reference agreement, source geometry and 2023 independent first-party sample validation.
- `GOLD_EXECUTION_EV_DUKASCOPY_2020_2025_SESSION_TARGET_QC_20261008.json` — exact 6-year source-consistent DAY/OVN private targets and quarantine counts; target SHA256 `4f0c05ccc66105c42b3784b951caf5ef6a6efa38f1d857a74109abb0e377ae14`.
- Programs: `tools/gold_execution_evdukascopy_uniform_2020_2025_20261008.py`, `tools/gold_execution_evduka_uniform_session_gate_20261008.py`, `tools/gold_execution_dukascopy_independent_xau_pilot_20261008.py` and GitHub Actions workflows `gold-execution-evdukascopy-uniform-2020-2025.yml`, `gold-xau-uniform-source-backfill-20261008.yml`.
- Earlier `GOLD_EXECUTION_2020_2026_SOURCE_VALIDATION_AND_QUARANTINE_RESULT_2026-10-08.md` described the old **HistData-only** candidate; its 2023 gap status is not the status of the **new independent uniform source**. Both studies remain historically valid and separately named.

**Bounded outcome: the 2020–2025 intraday execution-window *historical research dataset coverage* is repaired and recorded. The 2026 current-month live and actual Turkish bank execution price layer require separate approval and source acquisition before claiming a complete end-to-end 2020–2026 tradeable signal history.**
