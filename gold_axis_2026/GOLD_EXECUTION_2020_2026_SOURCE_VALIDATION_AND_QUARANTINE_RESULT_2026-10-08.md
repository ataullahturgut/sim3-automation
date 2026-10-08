# GOLD EXECUTION — 2020–2026 Source Validation and Quarantine Results — 2026-10-08

**Status:** GOVERNED SINGLE-PROVIDER BID RESEARCH CANDIDATE COMPLETED; FULL SOURCE ACCEPTANCE **FAIL / PARTIAL**, 2023 gap excluded. Original archives unchanged. No historical vendor fee.

## 1. Source and price identity

The actual HistData.com Generic ASCII M1 schema is **BID OHLC**, EST fixed UTC−05 (not New York summer daylight time). The reconstructed 15-minute candles are also **BID**. Twelve Data is an independent commodity/FX composite reference; this and historical frozen archives **must not be blended into a fictitious homogeneous series**. HistData BID is **not** bank executable BID/ASK or necessarily exchange spot MID.

- Official source: https://www.histdata.com/f-a-q/data-files-detailed-specification/
- Independent source difference authority: https://support.twelvedata.com/en/articles/11850499-understanding-price-deviations-in-commodities-and-forex-data
- Exact quote semantics frozen for **1,739 private research origin rows** with `source_quote_type = HISTDATA_GENERIC_ASCII_M1_BID_OHLC` (receipt: `GOLD_EXECUTION_XAU_QUOTE_TYPE_SOURCE_CONTRACT_2026-10-08.json`).

## 2. Actual 2020–2026 one-provider data product

The private table `gold_research_xau_execution_origin_quality_candidate_v1` contains 1,739 individual 09:00 TR research issue dates with a governed **DAY** and separate **OVERNIGHT** maturity gate. No Twelve/frozen other-source quote is used to create either label.

- DAY = Türkiye 09:00 15m OPEN → 17:00 15m CLOSE, requiring all 32 x 15-minute bars to have 15 native source minutes and correct origin/target anchors.
- OVN = Türkiye 17:00 15m OPEN → next **expected** 09:00 15m CLOSE, both anchors fully populated; weekday overnight also checks source path density. Friday-to-Monday weekend holds separately flagged, no interpolation.
- USD price is historical BID quote; sign target stored only for complete valid source anchors. Absolute 10 bps-or-smaller returns get a **diagnostic sensitivity flag**, but are never relabeled. Holiday calendars and bank spread verification still outstanding.
- Historical October 2026 source not yet validated; 2026 figures below are **January–September 2026** only. Provider downloaded Oct 8 historical vintage does not prove contemporary earlier point-in-time availability.

| Year | Private HistData 15m bars | Issue dates | Valid DAY | Excluded DAY | Valid OVN | Excluded OVN |
|---|---:|---:|---:|---:|---:|---:|
| 2020 | 23,626 | 258 | 252 | 6 | 248 | 10 |
| 2021 | 23,562 | 257 | 255 | 2 | 249 | 8 |
| 2022 | 23,643 | 258 | 255 | 3 | 248 | 10 |
| 2023 | **20,600** | 257 | **136** | **121** | **145** | **112** |
| 2024 | 23,713 | 259 | 258 | 1 | 248 | 11 |
| 2025 | 23,606 | 258 | 256 | 2 | 249 | 9 |
| 2026 Jan–Sep | 17,616 | 192 | 191 | 1 | 185 | 7 |
| **Total** | **156,366** | **1,739** | **1,603** | **136** | **1,572** | **167** |

**PASS only for restricted research panel:** 1,603 source-complete DAY and 1,572 source-complete OVN candidate BID labels. **No blanket 2020–26 market-price truth certification.**

## 3. Actual 2023 source recovery attempts

- Existing HistData XAU M1 2023 archive gives 20,600 bars vs 23,307 alternative frozen 2023 bars. Jan–Jul source has pervasive gaps.
- **Seven monthly HistData M1 retrievals** reproduced the same source; **0 new missing bars**, **0 changed overlapping close prices**. Receipt: `GOLD_EXECUTION_2023_HISTDATA_MONTHLY_REPAIR_QC_2026-10-08.json`.
- **April 2023 independent monthly tick archive test:** 2,067,972 raw BID/ASK ticks downloaded, 2,051,522 valid April-UTC ticks, reconstructed **1,268** BID/ASK 15m candles. All 1,268 timestamps already present in M1, so **0 missing 15-minute slots were recovered**. The overlapping BID closes agreed exactly (median and p95 absolute 0.0 bps). Separate tick candidate saved in private `gold_research_histdata_xau_tick_bidask15m_candidate`; not silently merged.
- Historical raw tick sample BID/ASK spread: 1.71 bps median / 2.08 bps p95 in **April 2023 only**; this is not the user's bank trading spread.
- Thus **121 invalid DAY** and **112 invalid OVN** 2023 issue dates are explicitly quarantined rather than imputed. Full 2023 remains **BLOCKED** for one-provider research.

## 4. Reconciliation and earlier vendor contamination

- Existing historical frozen **2025** price archive contains **2,354** records in a conservatively closed mainstream spot market time window. A late 2026 Twelve Data candidate contains **180** such bars. The exact source identities are kept unchanged, **but quarantined from this clean BID panel**.
- Overlapping two-vendor XAU direction labels often disagree near zero movement. The margin-bucket recheck `GOLD_EXECUTION_XAU_SOURCE_LABEL_DISAGREEMENT_ANATOMY_2026-10-08.json` shows these disagreements greatly decline on large realized moves, especially when both sources register >50 bps. The difference is source definition/sensitivity, not a license to choose whichever provider maximizes retrospective accuracy.
- Existing `GOLD_EXECUTION_2020_2026_ANNUAL_SOURCE_TRUTH_AUDIT_2026-10-08.md` contains all seven-year cross-vendor and market-calendar results.

## 5. Hard validation boundary

**Still FAIL / NOT CLAIMED:** missing 2023 same-source BID candles, 2026 October source-complete history, official venue-specific holiday-calendar and source event publication-lag guarantees, executable bank bid/ask, and full target/source-compatible PIT macro data. A mid/composite reference series may instead be modeled as a **separate reference identity**, never as a quiet historical gapfill in this BID series.

**No PRAMV, LIT, session or consensus model upgraded; no future price fabricated, no paid vendor purchase.** Research data gate enforcement and immutable original results are preserved.

Evidence scripts:
- `tools/gold_execution_histdata_one_vendor_origin_gate_20261008.py`
- `tools/gold_execution_quote_semantics_freeze_20261008.py`
- `tools/gold_execution_histdata_tick_2023_april_pilot_20261008.py`
- `tools/gold_execution_2023_histdata_monthly_repair_20261008.py`
- `tools/gold_execution_xau_label_disagreement_anatomy_20261008.py`

Signed evidence receipts: `GOLD_EXECUTION_HISTDATA_ONE_VENDOR_GOVERNED_CANDIDATE_2026-10-08.json`, `GOLD_EXECUTION_XAU_QUOTE_TYPE_SOURCE_CONTRACT_2026-10-08.json`, `GOLD_EXECUTION_2023_HISTDATA_TICK_BIDASK_REPAIR_PILOT_2026-10-08.json`.

**Decision:** Use the validated HistData BID subset **as a restricted research candidate only**. Source-truth certification for complete 2020–26 is conditional on filling/proving 2023 gaps, acquiring genuine Oct 2026 prices and real executable channel quotes. Never claim live-ready strategy performance from the candidate.
