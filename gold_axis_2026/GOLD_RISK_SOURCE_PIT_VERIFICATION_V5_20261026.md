# GOLD RISK — SOURCE / AS-OF VERIFICATION V5 (2026-10-26)

**Scope:** Independent read-only verification of original 2026-10-26 GitHub Actions acquisition artifacts (runs 40277837580 and 40278659820). Validate actual payloads, SHA-256, date coverage, missingness, and publisher release rules; distinguish observation date from availability. **This is not a completed historical point-in-time vintage certification and is not a model backtest.** No Neon/model/app/scheduled workflow changes.

## Direct bytes inspected

- Downloaded artifact `missing-gold-risk-official-20261026` (artifact 12630648714), containing original SLV SpreadsheetML XML and original FRB H15 CSV. Its original collection_audit.json has **SLV parse FAILED** (XML parse error); V4 report describes a later repaired read. This V5 independent read escaped exactly **six malformed bare ampersands in XML URL attributes**, without changing raw observation values.
- Downloaded artifact `gold-treasury-real-official-20261026` (artifact 12631545211), four original Treasury par-real-yield CSV files.

| Series | Observations (2023 onward) | Check | Missing | Status |
|---|---:|---|---|---|
| iShares SLV historical NAV and shares | **958** source dates, 2023-01-03 to 2026-10-23 | original bytes SHA verified; 0 duplicated dates, 0 missing NAV | 2024-03-29 and 2024-03-31 have no shares; March 31 is a Sunday | **Source integrity passed; PIT vintage/time not certified** |
| FRB H15 nominal 2Y/10Y | **994** weekday dates, 2023-01-02 to 2026-10-22 | SHA verified; 0 duplicates, exact H15 series IDs | **42 null/ND** for each (matching Fed closure holidays) | **Source integrity passed; release schedule verified; vintages not certified** |
| US Treasury 10Y par real | **953** valid daily dates (250,250,249,204), 2023-01-03 to 2026-10-23 | four SHA verified, 0 duplicates | **0** missing 10Y in rows | **Source integrity passed; publication instant/vintage not certified** |
| GLD original issuer archive | previously reported 752 valid numeric 2023–2025 rows | not in the two artifact ZIPs inspected in V5 | first-print timestamps unknown | **Earlier audit only; not independently rechecked in this V5** |
| CFTC GC/SI 2023–2026 | previously reported 398 contract-weeks | earlier V2 audit, not independently re-parsed in this V5 | exceptional 2025 CFTC delays require actual date mapping | **Publication rules verified; observations not independently rechecked in this V5** |
| CME GC/SI margin archive | — | publisher GitHub runner 403 | full history unavailable | **BLOCKED** |

Original source SHA256: SLV `f3b618e04836451a752d56bc15624379c90d9bd5670a231bf0c34222c52e0950`; H15 `75dcc355bf51e2c45bd04d9b4cfc7fbc1edaa81abef1c0318de8a18ac44b9906`; TIPS 2023 `ef28bcafaca75c45bb6b3491b4df4bd1b5e2ab7ff35ac014b6f8362df330c0ca`, 2024 `d3ff00a9287ebf68fdc80e72fb2d1895a73c84b3ff2a6ca8c6d64648cb470f16`, 2025 `d3d3131c41e1f93f4661d227ce7079049d51888b395aaff863b6ad8e08838b64`, 2026 `fdc7c08fc76db7abf7784355516aec1b98d0a7cbcac88ca465587281cb082202`.

## Publisher availability rules, documented by primary sources

1. **FRB H.15:** official H.15 posts Mon–Fri except Fed closures at **16:15 America/New_York**. Never allow observation D for decisions before D 16:15 ET. A current downloaded historical snapshot is **not evidence the same numerical value was known on day D**; vintage checks remain needed. https://www.federalreserve.gov/releases/h15/ and https://www.federalreserve.gov/data/releaseschedule.htm
2. **CFTC:** weekly position/report date usually Tuesday, public release **Friday 15:30 ET**, delayed for holidays; **do not map Tuesday to immediately tradeable**. Official 2026 calendar: https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm . 2025 government shutdown led to **13 exceptional COT release dates**; use revised **Dec 9** 2025 schedule rather than original planned releases: https://www.cftc.gov/PressRoom/PressReleases/9147-25
3. **Treasury real 10Y:** official par **real constant-maturity** curve, indicative market quotations taken about **15:30 ET**. This observation time is **not** an attested web-publication instant or historical revision vintage. Do not silently equate to FRED DFII10 (distinct instrument/series). https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics
4. **GLD:** publisher describes during-day shares and holdings updates (10:30–10:45 and 16:00–16:45 ET); latest archive does not timestamp each first original publication. Conservative temporal policy is needed for research until capture/vintage evidence. https://www.spdrgoldshares.com/usa/gld/
5. **SLV:** publisher archived NAV and Shares Outstanding are observation-date quantities; historical availability and revision vintages are not attested. Shares outstanding deltas are **creation/redemption proxy only**, neither verified cash flow nor silver tonnes. https://www.ishares.com/us/products/239855/ishares-silver-trust-fund

## Research-only illustrative as-of cutoff

For model decision **09:00 Europe/Istanbul** in 2026 (02:00 New York daylight time), H15 uses latest **previously released** observation (D 16:15 ET), while SLV and TIPS use a deliberately more delayed **next US weekday 09:00 ET availability proxy** (not publisher-certified; remains model-blocked). Missing values remain null; do not fill with zeros.

| Decision at TR09 | Latest H15 day | Latest TIPS day (provisional) | Latest SLV day (provisional) |
|---|---|---|---|
| 2026-03-30 | 2026-03-27 | 2026-03-26 | 2026-03-26 |
| 2026-03-31 | 2026-03-30 | 2026-03-27 | 2026-03-27 |
| 2026-04-01 | 2026-03-31 | 2026-03-30 | 2026-03-30 |
| 2026-04-02 | 2026-04-01 | 2026-03-31 | 2026-03-31 |
| 2026-04-03 | 2026-04-02 | 2026-04-01 | 2026-04-01 |
| 2026-08-11 | 2026-08-10 | 2026-08-07 | 2026-08-07 |

**Methodological caveat:** even this conservative proxy does not establish original first-publication vintages or protect from later corrections. Do **not** promote to production; revalidate first-print as-of histories and individual release exceptions first. Never retune 2026 alerts using hindsight. The two false-alert case windows are known; they cannot constitute an independent blind test.

**Status:** SOURCE-FILE QA: PASS (3 newly inspected families); RELEASE-RULE QA: PARTIAL; STRICT AS-OF VINTAGES: **NOT CERTIFIED**; MODEL GATE: **CLOSED**. Preserve BASE14 as gold-downside baseline and do not promote new variables until dates/vintages and OOS test pass.
