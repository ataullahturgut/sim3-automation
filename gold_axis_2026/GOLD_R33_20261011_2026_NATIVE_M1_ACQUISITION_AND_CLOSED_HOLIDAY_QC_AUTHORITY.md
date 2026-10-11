# R33 — Missing 2026 direct Dukascopy M1 acquisition and mandatory closed-session QC
**11 October 2026 UTC; quote-data source and QC only; no new model result.** Main contract: GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md. Starting branch HEAD 1afd8ab3cda6deed3d57a14de4b4bc32f38f95b5, R32 audit preserved. Additive GitHub commits only, prior price/label/model files not overwritten.

## Native M1 acquisition initiated (actual external execution)
- GitHub Actions workflow: `.github/workflows/gold-r33-2026-native-m1-gap-recovery-20261011.yml`; run https://github.com/ataullahturgut/sim3-automation/actions/runs/38165459414, started 2026-10-11 18:50 UTC, initial run status in progress at this checkpoint. Tool script `tools/gold_r33_20261011_dukascopy_missing_2026_native_m1_recovery.py`.
- **Primary** 2026 native Dukascopy BID/ASK M1, two official source hosts. Requests only exact 06:00UTC (09:00 TRT) dates missing in `gold_research_dukascopy_2026_direct_m1_m15_bidask_v2`, through CLOSED source date Friday 2026-10-09, not October 11 Sunday. Original source-only primary source ID unchanged. Candidate insert only, `ON CONFLICT DO NOTHING`; new `source_vintage=2026-10-11_RETRIEVED_HISTORICAL_NOT_PIT`. Data go only to private Neon. Actual BI5 payload SHA256 hashes and paired direct monthly Dukascopy H1 source OHLC parity included in aggregate per-day QC receipt, not raw prices publicly.
- Source status at launch: **14,208** previously stored primary M15 quotes on **148 UTC weekdays** between Jan 2 and Oct 7. **52 of 200** nominal 2026 Jan 1–Oct 7 weekday 09:00 TRT quote anchors absent. Jan 1 is a holiday and must not count as a valid market origin; raw weekday counts are NOT final tradable-date denominators. October 8/9 matured source bars are in the retrieval request, but their *H3 outcome* is not yet matured.
- Source run is asynchronous GitHub Actions infrastructure, **not** evidence of finished collection until finalized receipt and actual DB counts agree. Do not cite launched run as a 2026 source completeness PASS.

## Independent same-upstream verification for the 44 missing origin candidates
- For 2026 Jan–Sep, direct Dukascopy **monthly H1** table has **195/195 nominal weekday 06:00UTC** hourly anchors; native direct M1→M15 only **144/195**; so **51** direct missing H3 entry anchors, of which third-party same-upstream Dukascopy-node mirror holds **44**. **Seven** have no mirrored M15 origin, though the direct H1 hourly origin exists.
- Those **44/44** previously missing 06:00UTC MIRROR M15 origin hours exactly agree in **both BID/ASK hourly opens and closes** against independent direct monthly Dukascopy H1 native file, with all four M15 quarters present; direct-vs-mirror **10,832/10,832 all eight BID/ASK OHLC columns exact** on shared M15 intervals. This is strong same-upstream price corroboration, **not** original M1 tick/source-firstprint attestation or bank bid/ask execution.
- Across all fully assembled mirror hourly blocks with direct H1 reference, **3,748/3,750** open/close pairs fully exact; 2 non-origin boundary mismatches: 2026-02-01T23:00Z and 2026-03-10T22:00Z. Neither is a 09:00 TRT origin. Preserve as exceptions, never claim 100% hourly parity in every session.

## CRITICAL closed-session / calendar-padding defect (discovered by live SQL)
**A full 15/15 M1 candle count cannot prove that a market traded.** Direct 2026 source has:
- **2026-01-01 New Year's Day:** retrieved 96 M15 source bars with 15 minute-shaped M1 records per bar, but **92/96 full BID+ASK OHLC bars completely flat**; the **entire 01:45–05:30UTC preissue window flat**. Only 23:00–23:45UTC intervals show price discovery after overnight reopening. Therefore `2026-01-01 09:00 TRT` **MUST NOT** be a valid H3 decision/target origin despite physically existing vendor quote values. It was added as **raw quarantined source evidence** by first R33 workflow revision; new script revision `8f57a824501249d5b493df96c89675c228dfab0c` enforces preissue activity for future runs. The in-progress checkout was older, so all its accepted dates need final postrun QA.
- **2026-04-03 Good Friday:** **96/96** preexisting direct source M15 BID+ASK OHLC bars flat throughout calendar day, including decision window; must also be excluded from eligible decisions. This record is not a new 2026-10-11 downloaded day; it existed in the `2026-10-08` direct source. Official 2026 Good Friday holiday references: LBMA `https://www.lbma.org.uk/prices-and-data/value-dates` and CME `https://www.cmegroup.com/trading-hours.html`.
- New Year and Good Friday exact 09TR quotation availability therefore cannot be inferred from vendor bar presence. Gate source with official holiday / special trading time calendar, actual preissue nonflat activity and exact future target calendar before any new H3 model run. **Do not delete or rewrite the raw historical source in order to hide this finding; quarantine via source-quality eligibility.**

## Reproducibility
```sql
-- 2026 origin completeness, clock fixed UTC06 = 09TR:
SELECT date_trunc('month',bar_start_utc) mon,count(*) AS origin_quotes
FROM gold_research_dukascopy_2026_direct_m1_m15_bidask_v2
WHERE EXTRACT(HOUR FROM bar_start_utc AT TIME ZONE 'UTC')=6
AND EXTRACT(MINUTE FROM bar_start_utc AT TIME ZONE 'UTC')=0
GROUP BY 1 ORDER BY 1;

-- Prove apparently complete 15-minute BID+ASK observations are flat on closed days:
SELECT (bar_start_utc AT TIME ZONE 'UTC')::date AS utc_date,
count(*) AS n_bars,
count(*) FILTER (WHERE bid_open=bid_high AND bid_high=bid_low AND bid_low=bid_close
AND ask_open=ask_high AND ask_high=ask_low AND ask_low=ask_close) AS flat_bidask
FROM gold_research_dukascopy_2026_direct_m1_m15_bidask_v2
GROUP BY 1 HAVING count(*) FILTER (WHERE bid_open=bid_high AND bid_high=bid_low
AND bid_low=bid_close AND ask_open=ask_high AND ask_high=ask_low
AND ask_low=ask_close)>48 ORDER BY 1;

-- New retrieval totals, require date-level source receipt/QR parity:
SELECT source_vintage,count(*) n_m15,
count(DISTINCT (bar_start_utc AT TIME ZONE 'UTC')::date) n_utc_days
FROM gold_research_dukascopy_2026_direct_m1_m15_bidask_v2
GROUP BY 1 ORDER BY 1;
```

## Status policy
No source-merging/model scoring/selection allowed on this interim checkpoint. Distinguish native official M1 first-party *historically downloaded* from genuinely native active market trades and from true preissue source-vintage. Historical 2025/26 model evaluations were repeatedly inspected, so repeat scores on larger 2026 cohorts remain retrospective, not independent. Prospective 2027 remains required. Actual market execution is still unverified without institution-specific quotes and spreads.
