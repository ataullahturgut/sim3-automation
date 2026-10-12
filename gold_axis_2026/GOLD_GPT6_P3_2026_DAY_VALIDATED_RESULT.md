# 2026 HAR500-EVENT XAU/USD DAY — newly completed retrospective stress

**One-line finding: NO PROMOTION.** This is the first separately recomputed **2026 DAY 09:00–16:45 TRT** run of P3's HAR500-EVENT, on **177 source-complete dates from 2026-01-02 to 2026-10-07**. **Overnight 2026 was not scored.**

## Critical data-gate correction
Prior research mistakenly treated `m1_matched != 1` as unmatched for all 17,184 2026 direct M15 bars. **In fact `m1_matched=15` for 17,184/17,184**, indicating all 15 one-minute constituent bars matched each fifteen-minute source bar. Their 2026 vintage is 2026-10-08 or 2026-10-11 **retrospective archival download**, so this is not independently certified historical on-the-day first-receipt.

2026 DAY count: 178 structurally complete 31×M15 days; 177 have positive observed RV (the excluded all-flat or zero RV day cannot be log-modeled). No bad BID/ASK crosses in source. The 2026 OVN observed gap structure is NOT the 2020–25 vendor's original 61 bars + one 75-minute closure; 133 nights had 65 contiguous bars, changing RV definition. **Do not splice identical code and call those 2026 OVN values comparable.**

## Frozen exact model and realized QLIKE (lower better)
Pre-specified in `GOLD_GPT6_P3_2026_DAY_ONLY_VALIDATION_PREREG.md`, commit `01aa6b86`, BEFORE target extractions and performance scoring. Past data: original PR #96 EV/Dukascopy 2020–25 1,547 DAY RV windows; source changed to direct Dukascopy 2026, 177 complete DAY RV targets. Ridge alpha10, rolling latest500 mature same-session rows, 3 historical RV lags / plus CPI/NFP scheduled-day flag, exact same P3 specification, no tuning. Original 2025-12-31 model scores reproduced **exactly** from the archived historical source before extension.

| 2026 DAY (177) model | Realized-volatility QLIKE | Log-RV MSE |
|---|---:|---:|
| **PERSIST5 (strong 5-window control)** | **0.366936** | 0.514359 |
| HAR500 (without event) | 0.376717 | 0.477581 |
| **HAR500-EVENT** | 0.371427 | **0.474556** |
| CLIM60 | 0.677097 | 0.634353 |

Macro event flag on 15 of 177 dates. The macro event indicator improves QLIKE vs the *same HAR500 without event* by 0.00529 QLIKE (~1.40% relative), but **does not beat PERSIST5**: 0.371427 vs 0.366936 (**1.22% larger/worse QLIKE**). On secondary log-RV MSE it beats PERSIST5, but **primary metric governs**.

Three-calendar-month moving-block resampling 10,000 draws, baseline minus event QLIKE 95% intervals:
- PERSIST5 minus HAR500-EVENT: **[-0.0274, +0.0321]**. Overlaps zero, no convincing new performance.
- HAR500 minus HAR500-EVENT: [-0.0210, +0.0358]. Overlaps zero as well.
Results by month (2026 Jan–Oct, Oct partial) stored in `GOLD_GPT6_P3_2026_DAY_RESULT.json`. January high QLIKE disproportionately penalizes event model; model beats strong baseline numerically in 7 of 10 calendar month buckets, yet not in pooled primary or statistically robust score. No after-result window/month exclusion.

## Scientific limitation
1. Different historic source/vendor/vintage between 2020–25 and 2026, despite direct M1-matched raw bars; historical first-print/receipt not recorded.
2. 2026 CPI/NFP calendar from *actual* release-date records, not verified original preannouncement snapshots. Calendar-only question is retrospective.
3. No 2026 independent unseen test: 2026 had been repeatedly inspected in earlier work; this outcome is informative **stress/transport** only.
4. QLIKE predicts 15min bar-based realized variance magnitude, NOT next-day spot UP/DOWN or numeric price forecast.
5. OVN 2026 untested: cannot quote 0.3714 as "2026 HAR500 both windows."

**Conclusion:** Early 2023/24 event-aware apparent volatility advantage not demonstrably stable through either **2025 or 2026 DAY**, and no proven forecasting edge in 2026. Do not promote or splice source to replace P3 #96.

## Repro
- Preplan: `GOLD_GPT6_P3_2026_DAY_ONLY_VALIDATION_PREREG.md`.
- SQL: `sql/gold_gpt6_p3_2026_day_m15_source.sql`.
- Source: `GOLD_GPT6_P3_2020_2025_DAY_RV_TRAINING_SOURCE.csv` (1547), `GOLD_GPT6_P3_2026_DAY_REALIZED_RV_ROWS.csv` (177).
- Per-date scores: `GOLD_GPT6_P3_2026_DAY_SCORES.csv`.
- Summary incl months, bootstrap: `GOLD_GPT6_P3_2026_DAY_RESULT.json`.
- Replay script: `tools/gold_gpt6_p3_2026_day_replay.py`. No Neon writes.
