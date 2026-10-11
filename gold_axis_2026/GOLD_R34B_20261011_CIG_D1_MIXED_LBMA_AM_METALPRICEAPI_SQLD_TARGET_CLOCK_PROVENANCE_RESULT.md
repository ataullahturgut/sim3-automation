# R34B — CIG-D1 74.40% origin-clock source forensics: MIXED source and target-window discovery

**BINDING MONTH-BY-MONTH / WEEK-BY-WEEK FOLLOW-UP:** `GOLD_R35_20261011_CIG_D1_SOURCE_CLOCK_MONTH_AND_WEEK_FORENSIC_RESULT.md` directly verifies LBMA AM 10:30 GMT ≈ 13:30TR against first-party Dukascopy M1-derived M15 (26 matched dates, MAE USD3.43 versus PM USD21.35), source-provider transitions, UTC-date sqld averaging, 21 weekly Türkiye boundary scans, and MetalpriceAPI end-of-day release timing. R35 is the preferred clock detail; this R34B remains the earlier summary.

**Date:** 2026-10-11. **AUTHORITY / NEW MATERIAL SOURCE FINDING** supplementing R34 24h-source comparison. **No model refit, no invented first-print, no net bank profit.** The user correctly demanded a historical **cross-source, Turkey-clock price match**, rather than arbitrarily re-score the originally daily forecast with unrelated market hours.

## Executive finding — there cannot be ONE historical Turkey clock for the frozen original 125

The old 2026 Jan–Jul `Gerçekleşen` values are an exact 145/145 match to **StakTrakr** `lbruton/StakTrakr` at pinned commit `ed2e549f82ba0d1cd3ca32842b82d3888d301e01`, file `data/spot-history-2026.json`. **CRITICAL NEW INSPECTION:** that data set is a **concatenation of at least FOUR materially different price provenance/observation conventions**. No single 24-hour Turkey point-to-point buy/sell window generated its prices.

Original 145 price observations / frozen consensus 125 predictions, grouped using literal immutable upstream JSON `source,provider,timestamp` metadata:

| Gold daily source provenance | Original 145 days | Exact 125 consensus days | Old CIG correct | Observed population / implication |
|---|---:|---:|---:|---|
| `source=seed,provider=LBMA` | **29** | **25** | **18/25 = 72.0%** | **2026 Jan 2–Feb 11**. Likely LBMA morning fixing, NOT a full-day average. |
| `source=seed,provider=MetalPriceAPI` | **8** | **7** | **5/7 = 71.43%** | **Feb 12–20 and Mar 9** in frozen 145. Date-level MetalPriceAPI history lacks specific executable clock. |
| `source=seed,provider=StakTrakr` | **4** | **4** | **2/4 = 50.0%** | **Feb 23–26**; poller hourly-snapshot lineage, not automatically an LBMA fix. |
| `source=sqld` | **104** | **89** | **68/89 = 76.40%** | **Mar 10–Jul 31**. App's stored source-builder uses **`DATE(timestamp_floor), AVG(spot)`**, a **daily mean of ingested price observations**, NOT a benchmark AM fixing or fixed closing print. |
| **Total** | **145** | **125** | **93/125 = 74.40%** | **Four source conventions combined in ONE direction metric**. |

**Precision:** `LBMA` is the repository author's historical **provider label**, not proof of which licensed AM/PM IBA fixing and exact final auction instant. `StakTrakr` + `MetalPriceAPI` seed source does not itself contain a verified intraday source-ready timestamp. Original Stak `timestamp='... 12:00:00'` is a **synthetic date label**, not observed UTC noon. Mixed source vintages also exist: the older Stak realization labels vs the separately frozen H3 price vintage differ on **9 of the 125** consensus labels; 74.40% drops to 70.40% against the later fixed Stak vintage (authority GOLD_DAILY_REALIZATION_SOURCE_AUDIT_2026-10-06.md).

## Independent 15-minute price forensic — LBMA **AM**, not PM, strongly indicated

Official LBMA source says Gold benchmark auctions **start at 10:30 and 15:00 London time**, and final print may be after auction start; historical benchmark tables are licensed. January–February 2026 was UK winter time; these starts translate to **13:30 TR** and **18:00 TR**, respectively, **NOT a 24-hour day**.

We checked **all 29 frozen `provider=LBMA` 2026 Jan 2–Feb 11 dates** against independent Dukascopy-upstream 15-minute BID/ASK mid-quote samples from the separate historical Neon table `gold_research_dukascopy_node_mirror_2026_xau15m_bidask_candidat`. Each comparison uses the **mean of the two near-auction M15 opening quotes**:
- 10:30 and 10:45 UTC for **AM**; 15:00 and 15:15 UTC for **PM** (both winter GMT).
- **AM**: 29 dates; mean absolute price difference **USD 3.787**; median abs **USD 3.081**; **23/29** within USD5; **27/29** within USD10.
- **PM**: same 29 dates; mean abs **USD 22.853**; median abs **USD 21.990**; **6/29** within USD5; **11/29** within USD10.
- **25 of 29** dates are closer to AM than to PM; only 4 closer to PM.
- Example **Jan 2** Stak LBMA USD **4386.85**, Dukascopy AM-near **4390.241** (USD3.39 difference), PM-near **4347.183** (USD39.67 difference). **Jan 7** Stak LBMA 4459.55, AM-near 4462.948 (USD3.40), PM-near 4436.270 (USD23.28).

**Inference:** Stak's Jan/Feb daily **looks substantially like an LBMA Gold Price AM benchmark** around London 10:30. We **do not** certify official LBMA AM exact equality without authorized benchmark-level matching and actual final auction timestamp. The third-party mirror shares the Dukascopy upstream vendor and is not an independent first-print.

**Market issue-time implication:** For the 25 old Jan/Feb LBMA-labeled **CIG signals**, this probable **~13:30TR** morning benchmark begins **BEFORE** the CIG governed `08:00 America/New_York` (winter **16:00TR**) issuance deadline. Thus the original label may already be realized before forecast issuance. Historical signals have no actual `issued_at_utc`; early production must not be invented. These 18/25 model hits are **NOT** proof of post-signal investment performance.

## Independent H1 price forensic — `sqld` is **daily-average-like**, not LBMA

StakTrakr app updater `.agents/skills/update-spot-bundle/update-spot-bundle.py` literally selects:
```sql
SELECT metal, DATE(timestamp_floor) AS day, AVG(spot) AS spot
FROM spot_prices
WHERE DATE(timestamp_floor) > ?
GROUP BY metal, day;
```
Then stamps output `<date> 12:00:00` irrespective of actual quote observation time. Thus `source=sqld` history is a per-day average over observations in that application's private DB, with the source date aggregation calendar defined by `DATE(timestamp_floor)`. Whether each date has all 24 hourly source observations requires a separate raw sqld completeness audit.

Independent Dukascopy **direct primary monthly H1** source on all **145 sqld-calendar Gold dates Mar 10–Jul 31** (including weekends) shows:
- Source Stak `sqld` value vs **UTC-date 24-hour arithmetic mean of Dukascopy hourly ASK opening quotes**: **price median absolute difference USD 1.26; MAE USD 6.85** (145 days).
- Source Stak `sqld` vs **Türkiye local-calendar 24-hour hourly mean**: **median absolute USD 4.93; MAE USD 8.55** (145 days).

This is **strong quantitative support** that the later Stak sqld dates behave like a **UTC-day rather than Türkiye-day price average**, but different quote publishers/sampling density, calendars, stale weekend records and outliers prevent exact reconstruction of the original value's timestamps.

If one deliberately imposes ONE **uniform new** source clock on the entire old 125: R34's cross-vendor comparison gave old CIG **87/125=69.60%** vs Dukascopy **UTC-day hourly mean**, and **96/125=76.80%** vs Dukascopy **Türkiye-day hourly mean**. The **price-match criterion favors UTC daily averaging** whereas the **accuracy-best criterion favors TR daily averaging**. **Do not select TR simply because 76.80% is higher:** target design chosen on already opened 2026 labels is hindsight. Either is a new retrospective proxy, not the actual old mixed source clock.

## Reproducible source receipts and constraints

1. Old frozen Gold CSV `GOLD_DAILY_H1_V2_2026_GERCEKLESEN_TAHMIN_RECOVERED_2026-10-06.csv`; old CIG predictions `GOLD_CIG_EXACT_125_ROWS_2026-10-06.csv`. Join on **exact issue_date**, no model reconstruction needed.
2. Public source snapshot: `https://github.com/lbruton/StakTrakr/blob/ed2e549f82ba0d1cd3ca32842b82d3888d301e01/data/spot-history-2026.json`. `Gold` row's `source` and `provider`, date portion of synthetic timestamp, and `spot` reproduce all 145 prices.
3. Updater: `https://github.com/lbruton/StakTrakr/blob/ed2e549f82ba0d1cd3ca32842b82d3888d301e01/.agents/skills/update-spot-bundle/update-spot-bundle.py`, plus `devops/pollers/shared/spot-poller/update-seed-data.py` showing backfill from MetalPriceAPI `/timeframe`; `poller.py` has `NOON_HOUR=17` UTC reference for a daily seed, but **DO NOT apply this automatically to every provider StakTrakr seed without row-level lineage**.
4. Independent official time references: LBMA `https://www.lbma.org.uk/prices-and-data/lbma-precious-metal-prices`; ICE/IBA `https://www.ice.com/iba/lbma-precious-metals`.
5. 15-minute SQL core:
```sql
SELECT (bar_start_utc AT TIME ZONE 'UTC')::date AS d,
AVG((bid_open+ask_open)/2.0) FILTER(WHERE EXTRACT(HOUR FROM bar_start_utc AT TIME ZONE 'UTC')=10
 AND EXTRACT(MINUTE FROM bar_start_utc AT TIME ZONE 'UTC') IN (30,45)) AS am_approx,
AVG((bid_open+ask_open)/2.0) FILTER(WHERE EXTRACT(HOUR FROM bar_start_utc AT TIME ZONE 'UTC')=15
 AND EXTRACT(MINUTE FROM bar_start_utc AT TIME ZONE 'UTC') IN (0,15)) AS pm_approx
FROM gold_research_dukascopy_node_mirror_2026_xau15m_bidask_candidat
WHERE bar_start_utc>='2026-01-02' AND bar_start_utc<'2026-02-12'
GROUP BY 1 ORDER BY 1;
```
6. For Dukascopy hourly UTC mean:
```sql
SELECT (utc AT TIME ZONE 'UTC')::date AS d, AVG(ask_open) AS h1_utc_mean
FROM gold_research_dukascopy_xau_h1_monthly_source_candidate_v1
WHERE utc>='2026-03-09' AND utc<'2026-08-02'
GROUP BY 1 HAVING COUNT(*)=24 ORDER BY 1;
```

## Binding decision

**Do not claim a single original Türkiye D1 00:00–00:00 or 03:00–03:00 tradable horizon** for CIG-D1 V1; the original labels actually join heterogeneous LBMA near-AM + MetalPriceAPI daily + StakTrakr seeded + sqld daily means. There is **no valid single time translation** for that heterogeneous target.

The original **93/125** numerical observation is reproducible, but it was evaluated against a **mixed-vendor, mixed-operator, mixed-vintage** daily series. Source-clock defect is **material and now directly evidenced by underlying publisher data and independent 15m price matches**, not just an intuition.

**Research correction**: (i) isolate first 29 LBMA seed days as plausible benchmark AM labels and do not use them as proof of signals published after the fixing; (ii) isolate sqld dates and test uniform UTC mean if that is the intended forecasting product; (iii) rebuild one pre-registered daily horizon and **one provider/vintage** across 2020–26; (iv) freeze forecast `issued_at` and causal inputs; (v) compare exactly matched fixed-origin D1/H3 results in retrospective 2023–26 and later untouched prospective 2027. **No new model performance promotion or claim of model failure based on mismatched hours.**
