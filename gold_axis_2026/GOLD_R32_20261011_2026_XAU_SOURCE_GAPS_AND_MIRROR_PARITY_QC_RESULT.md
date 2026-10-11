# R32 — 2026 09:00 TRT XAU source-coverage and Dukascopy mirror parity audit — 2026-10-11

## Purpose / scope
**Data quality diagnostic only — no model, predictions, threshold optimization or independent forecast claim.** Read-only SQL executed via connected Neon "Gold Control" (`winter-art-94880101`) on 2026-10-11, following remote branch HEAD `85770a49069d68ca81e4d8d8e85288c265ecf61e` and full main manifest inspection. Audited existing tables:
- `gold_research_dukascopy_2026_direct_m1_m15_bidask_v2` (`source_vintage=2026-10-08_RETRIEVED_HISTORICAL_NOT_PIT`), 14,208 complete M15 BID+ASK bars, all `m1_matched=15`, UTC 2026-01-02 00:00 through 2026-10-07 23:45.
- `gold_research_dukascopy_node_mirror_2026_xau15m_bidask_candidat` (`source_vintage=GITHUB_THIRD_PARTY_2026_08_23_M1_MIRROR_NOT_PIT_CALENDAR_PADDED`), 15,027 M15 BID+ASK bars, all `matched_calendar_m1_count=15`, UTC 2026-01-01 23:00 through 2026-08-20 23:30. **Unaccepted third-party padded mirror, NOT verified point-in-time history, not a bank quote; do not silently splice into primary.**

`09:00 TRT` = `06:00 UTC` year-round (TR UTC+3). Counts below mean an **exact 06:00 UTC 15-minute bar timestamp** on a nominal Mon–Fri origin; they are *not* yet valid H3 labels. No weekend/holiday forward fill.

## Executed results

| Month 2026 | Weekdays nominal | Direct M1→M15 origin 06:00 UTC | Mirror origin 06:00 UTC | Mirror-only origin 06:00 UTC |
|---|---:|---:|---:|---:|
| Jan | 22 | 11 | 21 | 10 |
| Feb | 20 | 6 | 20 | 14 |
| Mar | 22 | 7 | 22 | 15 |
| Apr | 22 | 22 | 21 | 0 |
| May | 21 | 21 | 21 | 0 |
| Jun | 22 | 22 | 22 | 0 |
| Jul | 23 | 18 | 23 | 5 |
| Aug | 21 | 21 | 14 (mirror ends Aug 20) | 0 |
| Sep | 22 | 15 | — | — |
| Oct 1–7 | 5 | 5 | — | — |
| **Jan 1–Oct 7** | **200** | **148** | **164 (Jan–Aug only)** | **44** |

- **52/200 = 26.0%** nominal weekday 09:00 TRT origin timestamps are absent from the *direct* 2026 source. January–March is particularly sparse: direct **24/64 = 37.5%**, missing **40/64** origin timestamps. Months are not exchange-holiday adjusted and include Jan 1 closure; precise trading-day missing count requires an official schedule. The current R30 CME/XAU matched **2026 N=99** has additional feature/target eligibility restrictions: its 99 is **not** the full 2026 day population, and nothing here measures selection-bias direction.
- **44** origin timestamps absent from direct are present in the same-vendor-derived unapproved third-party mirror (Jan 10, Feb 14, Mar 15, Jul 5). This identifies concrete vendor-specific missing-day recovery candidates without switching to an unrelated pricing vendor.
- **10,832 exact shared M15 timestamps** between the direct and mirror tables: **10,832/10,832 have exact equality in all 8 BID+ASK OHLC numeric columns** (not merely signed returns). Among exact **06:00 UTC** origin anchors, **120/120 BID opens equal**. Shared bars run 2026-01-02 00:00 UTC through 2026-08-20 23:30 UTC.
- Nonflat-price sanity diagnostic: direct-overlap mirror **0/10,832** BID flat M15 bars and mirror-only **0/4,195** flat M15 bars; mean ASK–BID close spread overlap **1.649 bps**, mirror-only **1.727 bps**. These checks detect obvious padding artifacts only, not historical firstprint or M1 fabrication.
- Unique timestamps across the two sources: **18,403** (14,208 + 15,027 − 10,832). They are NOT a promoted canonical 2026 historical series; a union would need separate holiday, full-M1, source-authenticity, availability/firstprint and 09:00+H3 label gates.

## Reproduction (SELECT-only; no mutations)

```sql
-- A. Direct 09:00 TRT exact-origin coverage by UTC calendar month
SELECT date_trunc('month',bar_start_utc) mon, COUNT(*) AS n09
FROM gold_research_dukascopy_2026_direct_m1_m15_bidask_v2
WHERE extract(hour FROM bar_start_utc AT TIME ZONE 'UTC')=6
  AND extract(minute FROM bar_start_utc AT TIME ZONE 'UTC')=0
GROUP BY 1 ORDER BY 1;

-- B. Mirror 09:00 TRT origin candidates with no exact direct-source bar
SELECT date_trunc('month',b.bar_start_utc) mon,
  COUNT(*) AS mirror_09,
  COUNT(*) FILTER (WHERE a.bar_start_utc IS NULL) AS mirror_only_09
FROM gold_research_dukascopy_node_mirror_2026_xau15m_bidask_candidat b
LEFT JOIN gold_research_dukascopy_2026_direct_m1_m15_bidask_v2 a
  ON a.bar_start_utc=b.bar_start_utc
WHERE extract(hour FROM b.bar_start_utc AT TIME ZONE 'UTC')=6
  AND extract(minute FROM b.bar_start_utc AT TIME ZONE 'UTC')=0
GROUP BY 1 ORDER BY 1;

-- C. Exact-match coverage for all 8 source quote columns
SELECT COUNT(*) n_overlap,
  COUNT(*) FILTER (WHERE
    a.bid_open=b.bid_open AND a.bid_high=b.bid_high
    AND a.bid_low=b.bid_low AND a.bid_close=b.bid_close
    AND a.ask_open=b.ask_open AND a.ask_high=b.ask_high
    AND a.ask_low=b.ask_low AND a.ask_close=b.ask_close) all_8_exact
FROM gold_research_dukascopy_2026_direct_m1_m15_bidask_v2 a
JOIN gold_research_dukascopy_node_mirror_2026_xau15m_bidask_candidat b
  ON a.bar_start_utc=b.bar_start_utc;
```

## Binding scientific conclusion

A **specific data-coverage defect** explains why 2026 H3 scores cover only a selected subset of possible origins before feature requirements. This does NOT prove 2026 model errors are caused by gaps, nor validate mirror-only OHLC values: both tables trace to Dukascopy, so parity is **not independent-vendor price confirmation**, and the mirror is explicitly `NOT_PIT_CALENDAR_PADDED`. Priority is to independently reacquire missing 2026 direct-Dukascopy M1 sessions, accept only native source timestamps and full quote/holiday checks, rebuild H3 origin/target common cohorts and reproduce R28 vs R30 2026 98/99 mismatch by date before more model complexity. **Do not fill missing labels, retrospectively choose sources for higher scores, or report 2025/26 as untouched validation. Independent prospective 2027 remains necessary.**
