# Gold 2026 Dukascopy native BID/ASK same-provider source rescue — observed QC

**As-of:** 2026-10-08. **Result:** primary direct-vendor source acquisition genuinely initiated; **2026 same-provider model metrics NOT VERIFIED**. Do not represent this as a completed forecast backtest.

## 1. Independent source identity evidence

The frozen, earlier actually executed 2025 direct-Dukascopy-M1 vs EV Dukascopy-derived M15 quote comparison is `GOLD_EXECUTION_DUKASCOPY_2025_PRIMARY_SOURCE_OVERLAP_728_FROZEN_20261008.json` (source-run commit `2ac07b0a77cebcf761b03398b7f918c879d8f115`). It contains 728 compared BID open/close quote cells, median |difference| ≈0.011685 bps, p95 ≈0.011913 bps, accepted across four fully downloaded 2025 days. This **satisfies the pre-registered 500-cell price-source comparability threshold** but neither proves that 2026 has enough valid price bars nor that models successfully predict 2026.

An earlier direct 2026 replayer redownloaded a different, smaller 2025 sample and blocked at 360 cells with 503/timeout failures. That is not contradictory: two executions obtained different partial upstream subsets. It is scientifically wrong to discard the successful 728-cell independently frozen source receipt, or to silently lower the acceptance threshold.

## 2. Actual private 2026 source acquisition and intermediate quality

Monthly native M1 BID/ASK source recovery now targets 2026 January through October 8, with one homogeneous quote producer. Database table `gold_research_dukascopy_2026_direct_m1_m15_bidask_v2` stores raw prices only in private Neon; public GitHub summaries contain only counts and proof. Strictly **15/15 native M1 bars for accepted M15 candles**; no arbitrary market-day interpolation, no HistData/Twelve price substitution. Successful days are persisted independently to survive HTTP 503 / runner termination.

First completed read-only DB snapshot (not final month total), `GOLD_EXECUTION_2026_DIRECT_DUKASCOPY_MONTHLY_COVERAGE_STATUS_20261008.json`, measured:
- January: 576 accepted M15 bars, 6 UTC days.
- February: 576 bars, 6 days.
- March: 480 bars, 5 days.
- May: 96 bars, 1 day.
- **TOTAL at snapshot:** 1,728 accepted M15 bars / 18 UTC days.
- Of 201 considered 2026 weekday issues through October 8, only **18 DAY issue-date 09:00–17:00 source paths** and **4 regular 17:00–next09:00 OVN source paths** were sufficiently complete. These are insufficient for a meaningful same-source 2026 test. The reading is a **timestamp snapshot**, not a definitive count of future/retried acquisition results.

## 3. Immutable non-promotion and comparison policy

Pre-2026 historical Dukascopy training starts 2020, 2021 and 2022, and six previously frozen ML model identities remain unmodified. No 2026 realization enters training or parameter selection. Score exactly the same 2026 eligible days between training histories and report per-month/year BA, class recalls, Brier, paired rescues/breaks; normal weekday OVN excludes Friday→Monday 64h.

The separate full-year 2026 HistData BID candidate test **was already executed** with 184 DAY and 141 regular-OVN feature-and-label-qualified issues (2026 Jan–Sep) but cannot be labeled same-source Dukascopy score. There is also an explicit `gold_execution_2026_cross_provider_frozen_transport_20261008.py` with an independent workflow evaluating 2020–25 Dukascopy-trained models on identical HistData 2026 labels **as a domain-shift research sensitivity only**. Do not promote its results as same-provider validation.

Source ingestion workflow: `.github/workflows/gold-execution-2026-primary-monthly-and-fixed-replay.yml`. Primary replay: `tools/gold_execution_2026_reconciled_direct_source_locked_replay_20261008.py`. The main 2026 results can be reported only after a new `GOLD_EXECUTION_2026_FROZEN_HISTORY_SAME_VENDOR_CHALLENGE_20261008_SUMMARY.json` records an authoritative successful source and label gate together with matching year and monthly metrics. The older summary with 360-cell block is **not a new success**.

**No champion or claimed 2026 source-certified predictive accuracy at this stage.**
