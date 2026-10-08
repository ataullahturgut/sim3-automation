# GOLD EXECUTION — 2020–2025 XAU/USD Historical Data Strengthening, Independent Labels and Final Research QC — 2026-10-08

**Audited source:** EV Trading Labs historical M15 BID+ASK archives derived from Dukascopy XAU/USD, separate proprietary-source identity `EVTRADINGLABS_DUKASCOPY_DERIVED_XAUUSD_M15_BIDASK_2020_2025_V1`.  
**Scope:** 2020-01-01 through 2025-12-31, past completed historical quotes, DAY **09:00–17:00 Türkiye**, OVERNIGHT **17:00–next expected 09:00 Türkiye**.  
**Status: HISTORICAL SINGLE-SOURCE PRICE-STRUCTURE AND LABEL-CALCULATION QC PASS; bank execution/PIT and completeness of every underlying source M1 bar NOT proven.** No model retuning or score claims in this audit.

## 1 — Exact price reconstruction and immutable storage checks

Historical source ZIP/GZIP quotes were **reloaded independently for every year**, compared by exact UTC source interval and eight separate BID/ASK OHLC columns against the private Neon persisted quotes, with **ZERO differences** on all **141,890 15-minute observations**.

| Year | BID+ASK 15m rows | stored-origin dates | quote mismatch | DAY label mismatch | overnight label mismatch |
|---|---:|---:|---:|---:|---:|
| 2020 | 23,702 | 259 | 0 | 0 | 0 |
| 2021 | 23,626 | 258 | 0 | 0 | 0 |
| 2022 | 23,647 | 258 | 0 | 0 | 0 |
| 2023 | 23,544 | 257 | 0 | 0 | 0 |
| 2024 | 23,733 | 259 | 0 | 0 | 0 |
| 2025 | 23,638 | 258 | 0 | 0 | 0 |
| **TOTAL** | **141,890** | **1,549** | **0** | **0** | **0** |

All six years had **zero** duplicate UTC M15 intervals, invalid positive prices, invalid BID or ASK high/low/open/close relationships, crossed contemporaneous BID/ASK opens or closes, offmarket Saturday/Sunday bars, UTC quarter-hour misalignment, missing source volume, zero-volume candles, and forbidden Dukascopy XAU daily maintenance interval candles. The venue closure definition adjusts the UTC gold daily pause and Sunday open/Friday close across **US summer/winter time**, per the source broker's published schedule.

Provider source catalogue and format: https://evtradelabs.com/data . Official venue-specific XAU/USD summer/winter hours: https://www.dukascopy.com/swiss/english/forex/forex-trading-accounts/link/?mob=1 .

This is *exact original-source versus private-storage integrity*, not a claim of independent second-provider price-level truth at every quarter hour.

## 2 — Independent historical label regeneration from quote anchors

A **separate, independent implementation**, not calling the original label-building function, recalculated every one of the **1,549 issue-date records** from the same 15m BID/ASK source with exact decision and target anchors:

- DAY: open at UTC **06:00** (Türkiye 09:00) to the bar starting UTC **13:45** and ending Türkiye 17:00, requiring complete 32 quarter-hour bars.
- OVERNIGHT: open UTC **14:00** (Türkiye 17:00) to the next *expected market weekday's* bar closing UTC **06:00** (Türkiye 09:00), requiring source-qualified anchors and overnight density. Nontrading dates are **NULL**, not encoded as DOWN.
- Independent tests include BID/ASK log-return values (both windows), UP/DOWN sign, BID/ASK direction disagreement, spread at each user decision origin, <=10bps magnitude flags and exact `next_expected_date`. ALL tests showed **zero** mismatch over 2020–2025.

**IMPORTANT QC harness correction:** the first version of the forensic comparator falsely counted nullable PostgreSQL target fields represented as NumPy `NaN` as differing from a missing value `None`. This is an **audit-code false alarm**, not bad stored labels. The completed corrected auditor normalizes NULL and includes the following year's bars for year-end anchor checks; the actual recorded label mismatch count is **0**. The immutable archived prices, historical source labels and model results were not overwritten.

## 3 — Independently investigate extremely large 15-minute values

Exactly **six** consecutive 15-minute **BID CLOSE-to-CLOSE absolute moves over 1.5%** were found.

| UTC timestamp of flagged bar | Event date/context | Source absolute move | Independent HistData BID same-time return check |
|---|---|---:|---|
| 2020-03-06 15:15 | COVID period | 2.047% DOWN | **SAME SIGN; difference only 0.0410 bps** |
| 2020-03-13 16:30 | COVID period | 1.556% DOWN | **SAME SIGN; difference 0.0005 bps** |
| 2020-03-16 10:45 | COVID period | 1.660% DOWN | **SAME SIGN; difference 0.0202 bps** |
| 2020-03-23 12:00 | COVID period | 1.607% UP | **SAME SIGN; difference 0.0002 bps** |
| 2021-08-08 22:45 | Asia Aug 9 2021 flash crash | 4.102% DOWN | **Second vendor lacks BOTH exact UTC anchors. Market event independently corroborated, exact quote magnitude not independently confirmed.** |
| 2023-12-03 23:15 | Asia Dec 4 2023 record gold rally | 2.632% UP | **SAME SIGN; difference 0.0006 bps** |

**Five of six** outliers are cross-confirmed by **independently sourced HistData BID prices on both exactly matching 15-minute timestamps**, with nearly identical price returns. The remaining Aug 9 2021 flash crash is independently documented by the World Gold Council as a ~4% fall over ~15 minutes, but the specific broker's historical M15 OHLC cannot be asserted identical to that published market event. Source: https://www.gold.org/goldhub/research/gold-market-commentary-august-2021 . December 4 2023 Asian-opening record episode appears in contemporaneous Reuters reporting: https://www.marketscreener.com/news/latest/Asia-shares-turn-mixed-gold-hits-record-above-2-100-45491114/ .

**Data policy:** do not erase meaningful shocks by running a simplistic 1.5% outlier filter. Preserve all source prices; tag the one non-third-party-bar-confirmed 2021 case explicitly until independent direct raw source is retrieved.

## 4 — NEW separately versioned V2 horizon/data-quality contract

The original 2020–2025 target panel is immutable; a **separate private Neon V2 table** was created: `gold_research_evduka_xau_session_quality_gate_v2`, exactly **1,549** issue dates. It records origin source/quote semantics and whether the overnight horizon is **regular 16h** or **Friday-to-Monday weekend 64h**.

**Audited outcome counts and uncertainty classes (no retroactive price/label changes):**
- Source-mature DAY: **1,547**; source-ineligible DAY: **2**.
- Source-mature OVN: **1,494**; source-ineligible OVN: **55**.
- Valid Friday-to-Monday **64-hour overnight holds**: **300** of 304 Friday issue dates. Do not silently pool them with regular 16-hour overnights; remaining valid OVN labels are **1,194** regular-weekday sessions.
- **BID/ASK source sign conflict**: 2 DAY and 5 OVERNIGHT records (these have ambiguous direction relative to quote side).
- **Small source-return magnitude** (absolute <=10bps) flagged separately: **262 DAY**, **200 OVN** in the priority-based quality classification, not invalidated and not relabeled.
- **Large quoted spread at user decision boundary** (>30bps, prespecified diagnostic): 1 OVERNIGHT-origin label (2020), separately flagged. This is **provider spread**, not user's Turkish bank spread.
- High-confidence *within limited source-structure sense* with no above flags: **1,283 DAY** and **1,288 OVN** research labels; do not call these guaranteed future forecasts or executable trading opportunities.

Source anchors, dates, actual labels, all price quotes, and the old model decisions remain unchanged.

## 5 — Data quality release decision

**APPROVED FOR RESTRICTED HISTORICAL RESEARCH:** 2020–2025 homogeneous BID and ASK quoted historical M15 data; exact persisted price-level and year/calendar identities; entire historical DAY/OVN label calculations independently verified; all source-incomplete labels NULL; selected small-move/BIDASK/conflicting-weekend/date flags exposed in an explicit V2 quality layer. No arbitrary price interpolation or cross-provider blending. Not tested for bank execution performance.

**NOT YET VERIFIED/NOT IMPLIED:** Every raw source M1 minute/tick, original historical point-in-time accessibility, bank purchase/sale spreads, date-aware special holiday session rights, universally perfect OTC spot quote-level truth on all 141,890 timestamps, or 2026 same-provider all-year coverage. Existing one-source HistData and 2025 legacy weekend anomalies remain separately quarantined. No model training occurred in this study.

**Model-readiness rule:** do not start PRAMV / ensemble / other model reruns until the user elects to start that phase; then enforce this accepted quote-source authority, 16h-versus-64h horizon split, embargo on target-period information, case-level source uncertainty flags, source-uniform features and unchanged chronological research partitions.

## 6 — Verifiable evidence (GitHub / private Neon)

- `GOLD_EXECUTION_2020_2025_PRICE_LABEL_FORENSIC_AUDIT_20261008.json` — six-year 141,890 quotes; exact public-source/private-Neon 8-value check and 1,549 independent label audit.
- `GOLD_EXECUTION_2020_2025_XAU_EXTREME_BAR_CROSS_VENDOR_QC_20261008.json` — six extreme 15-minute timestamps; five cross-confirmed, one separately flagged.
- `GOLD_EXECUTION_2020_2025_SESSION_TARGET_V2_PROVENANCE_QC_20261008.json` — 1,549 source-reliability/horizon V2 metadata rows and year-by-year counts.
- `GOLD_EXECUTION_EV_DUKASCOPY_XAU_2020_2025_UNIFORM_CANDIDATE_20261008.json` — annual source files SHA256 and data completeness.
- `GOLD_EXECUTION_EV_DUKASCOPY_2020_2025_SESSION_TARGET_QC_20261008.json` — earlier immutable source-maturity-only target proof.
- Source implementations in `gold_axis_2026/tools/gold_execution_2020_2025_price_label_forensic_20261008.py`, `gold_execution_2020_2025_extreme_cross_vendor_qc_20261008.py`, `gold_execution_2020_2025_target_scope_v2_20261008.py`.

**Verdict:** 2020–2025 historical data price fields and historical model-target labels have **no detectable errors under the completed source-format/market-clock/computation audits**. This is a strong, **bounded acceptance** for source-consistent research; not a claim of perfect independently bank-executable quote truth.
