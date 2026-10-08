# GOLD EXECUTION — 2020–2026 annual XAU/USD source truth and label concordance audit — 2026-10-08

**Status:** COMPLETED ANNUAL PROVENANCE/CALENDAR/CROSS-VENDOR DIAGNOSTIC / **NO 2020–2026 FULL SOURCE ACCEPTANCE** / original frozen panels unchanged.  
**Repository/branch:** `ataullahturgut/sim3-automation` / `gold-execution-channel-audit-20261006`.  
**Scope:** Historical spot XAU/USD 15-minute price bars and derived Turkish bank-decision DAY (09:00–17:00) / OVERNIGHT (17:00–next eligible 09:00) labels. **Separate from macro publication-clock PIT, futures, and executable bid/ask.** No paid historical data purchased.

## 1. Verified actual per-year calendar/source results

| Year | Frozen/original rows | Independent reference rows | Exact-UTC matched bar closes | Closed-market bars in original | Cross-source price diff median, bps | DAY label mismatch | OVN label mismatch | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2020 | Twelve 22,145 | HistData 23,626 | 21,432 | 0 | 3.78 | 30/236 (12.71%) | 20/235 (8.51%) | Clock test PASS; source/target agreement FAIL; Twelve starts Jan 24 |
| 2021 | Twelve 23,150 | HistData 23,562 | 22,486 | 0 | 2.04 | 33/255 (12.94%) | 43/241 (17.84%) | Clock test PASS; source/target agreement FAIL |
| 2022 | Frozen 23,551 | HistData 23,643 | 22,925 | 0 | 2.70 | 26/256 (10.16%) | 32/256 (12.50%) | Clock test PASS; source/target agreement FAIL |
| 2023 | Frozen 23,307 | HistData 20,600 | 19,918 | 0 | 1.55 | 8/141 (5.67%) | 19/193 (9.84%) | Clock test PASS; **reference coverage FAIL**, cannot extrapolate matched subset |
| 2024 | Frozen 23,618 | HistData 23,713 | 23,054 | 0 | 2.10 | 33/259 (12.74%) | 31/258 (12.02%) | Clock test PASS; source/target agreement FAIL |
| 2025 | Frozen 26,966 | HistData 23,606 | 23,282 | **2,354** | 5.91 | **27 label flips** in 2025 same-origin model audit | **27 label flips** in 2025 same-origin model audit | **Frozen calendar FAIL; source promotion blocked** |
| 2026 to Oct 8 | Twelve recent 1,008 (Sep28–Oct8) | HistData Jan–Sep 17,616 | Sep28–30 overlap 276 | **180 in recent Twelve segment** | 13.66 in Sep28–30 overlap | Not fully checked | Not fully checked | **Twelve late segment calendar FAIL; HistData candidate exists but not canonical** |

**The closed-market hard-fail screen** counts Saturday UTC and Sunday before 21:00 UTC (conservatively impossible mainstream weekday spot trading intervals); it is a necessary, NOT sufficient condition. Sunday after 21:00 and weekday/maintenance/holiday coverage require date-aware calendars and vendor source-specific checks. A source having zero hard-fail rows does **not** certify correct bid/ask, tick quality, publication vintage or bank-executable price.

For 2023 the independent HistData M1-to-M15 sample is conspicuously thinner (20,600 vs frozen 23,307). January–July monthly bar counts are 1,908, 1,650, 1,528, 1,268, 1,510, 1,444, 1,404. Only **141** matched DAY origins qualify; no inference to the full 2023 year is justified.

**2020** Twelve Data 15m API earliest timestamp is 2020-01-24 02:00 UTC; missing early January may not be filled by silently grafting another provider's spot quote. For 2020–2021 15m quote levels matched on 43,918 bars but sources are not identical. For 2022–2024, independent HistData was fetched directly in the new validation and stored separately in private Neon as 67,956 15-minute bars, without replacing the original frozen archives.

## 2. Key technical interpretations

- Divergent UP/DOWN labels across two OTC spot gold vendors **do not alone prove which vendor has bad quotes**. They prove that the assigned *model target* is source dependent, especially near zero net movement, and are a reproducibility/source-definition problem.
- **2025 original archived price series is objectively inconsistent with ordinary spot gold market closures**, with 2,354 off-market bars; 2026 late Twelve candidate also fails with 180 bars, including moving prices on Oct 3 and Oct 4.
- HistData M1 independent data for 2025 (23,606 M15 bars) and 2026 Jan–Sep (17,616 M15 bars) contain no bar in the hard-closed hours under the same check. This makes them better **calendar-clean candidates**, not already proven point-in-time, price-reference, execution-valid truth.
- 2023/2024 old archives show no hard-closed weekend bars, yet their independent source labels can disagree. Thus previous model metrics must report the source and may require source-sensitivity reruns rather than implying all previous values were fabricated.
- The year 2025 source-repair model replay showed 27 changed target labels on comparable dates (specific model windows), and 2026 clean-source LIT forecasts were near chance. These are *diagnostic*, not performance promotion.
- The frozen 2023–2025 price archives and existing PRAMV V1 evidence have **not** been overwritten. Separate original and recovery candidates are retained under distinct source identities.

## 3. Acceptance gates and concrete next steps

1. **Canonical source identity must be frozen before labels:** explicitly specify reference quote vendor, bid/mid/ask meaning, UTC 15-minute bar start/end, supported year ranges, immutable raw hashes and history vintage. Mixing HistData and Twelve across a decision bar or overnight interval is prohibited without a governed bridge.
2. **2023 coverage:** independently backfill and audit the deficient HistData Jan–Jul subset or obtain a second independent provider; explain missing market minutes/holidays and source dropouts. Retain exclusion flags, never price-impute labels across gaps.
3. **2020–2024 label reconciliation:** audit vendor disagreements by `abs(true window move)` buckets and timestamp/quote offset. Large dislocations on the same active 15-minute timestamps require particular investigation. No blanket claim of one provider's correctness based on label agreement or forecast performance.
4. **2025–2026 original source quarantine:** do not train/score against impossible-weekend price bars or silently substitute a new source; reconstruct acceptance-approved target panels with date-aware trading calendars, full maturity and same-source anchors.
5. **Model replay only after acceptance:** same origins, frozen candidate PRAMV and standalone DAY/OVN models, direction Accuracy/BA/both-class recall/Brier, no 2025/2026 adaptive selection masquerading as clean untouched holdout. Real transaction P&L remains blocked without bank bid/ask histories.

## 4. Evidence paths (actual scripts and receipts)

- `GOLD_EXECUTION_2020_2021_SOURCE_TARGET_CONCORDANCE_2026-10-08.json` (43,918 matched bars; source label disagreements by year)
- `GOLD_EXECUTION_2022_2024_INDEPENDENT_SOURCE_QC_2026-10-08.json` (independent per-year 1min input, M15 calendar, mismatch, distribution and private provenance)
- `GOLD_EXECUTION_XAU_SOURCE_CALENDAR_GATE_2026-10-08.json` (2023/24/25/26 impossible-weekend source check)
- `GOLD_EXECUTION_HISTDATA_INDEPENDENT_2025_2026_SOURCE_AUDIT_2026-10-08.json`, `GOLD_EXECUTION_HISTDATA_2026_JAN_SEP_BACKFILL_2026-10-08.json` (independent replacements)
- `GOLD_EXECUTION_2025_SOURCE_REPAIRED_LIT_RESULT_2026-10-08.md`, `GOLD_EXECUTION_CLEAN_2026_LIT_STRESS_RESULT_2026-10-08.md` (source sensitivity, no new strategy promotion)

**Bottom line:** 2020–2024 show no simple closed-weekend anomalies on the inspected source slices, but no year passes full source-independent label agreement. The 2023 independent source has missing coverage. 2025 old and the 2026 late Twelve candidate show positive evidence of off-market quotes; both are source-gated. **No historical year is currently globally certified as the unique price truth for the final execution model.**
