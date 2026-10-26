# GOLD RISK EXOGENOUS SOURCES V4 — ACTUAL DOWNLOAD AUDIT 2026-10-26

## Scope / guardrails
Purpose: add verifiably acquired source observations to a **separate research archive** for evaluating false positives (March 30–April 3, August 11, 2026), **not** tune a 2026-specific false-alarm filter. Keep original CFTC14/CFTC21 model, ANN, Neon data and automation schedules unchanged. Fetch jobs both one-shot; push triggers removed right after launch and each workflow left as `workflow_dispatch` only.

## New official source successes (actual files, no inferred rows)

| Family | Source | Date coverage | Actual validated payload | Model gate |
|---|---|---|---|---|
| **SLV** | BlackRock iShares issuer SpreadsheetML fundDownload | 2006–2026, 2023–2026 subset **958 source date rows** | daily `NAV per Share`, `Shares Outstanding` (two 2024 dates lack shares) | no first-publication as-of; research-only |
| **US nominal yields** | FRB H.15 official CSV Treasury Constant Maturities package | 2023–2026 subset **994 weekday rows**, last 2026-10-22 | 2-year and 10-year nominal constant maturity; 42 ND/missing observations per series (holidays) | source is latest historical snapshot, not certified PIT |
| **US real yields** | US Treasury official daily par real yield curve CSV | **2023 250, 2024 250, 2025 249, 2026 204 = 953 valid 10Y records**, last 2026-10-23 | exact TIPS 5/7/10/20/30-year *Treasury par real yield curve* | not equivalent to FRED DFII10; source first publication timing unverified |
| **GLD** | SPDR direct official historical XLSX (previous downloaded 2026-10-24) | 2023–2025 **752 usable numeric days**, + 2026 until October 22 | ounces/tonnes in trust; shares and issuer history | historical publication vintage unverified; do not commit issuer XLSX to public repo |
| **CFTC** | official CFTC annual disaggregated futures ZIPs, previous 2026-10-24 | 2023–2026 | COMEX GC 088691 and SI 084691; total 398 contract-weeks | normal-week 7-day research proxy vs release; shutdown official reschedule |

**SLV parser bug resolved:** source is not a ZIP/OLE Excel file; it is XML SpreadsheetML. The issuer's original text contains six *unescaped ampersands* in hyperlink attribute values, which strict standard XML parsing rejects. The source was saved untouched with SHA-256 `f3b618e04836451a752d56bc15624379c90d9bd5670a231bf0c34222c52e0950`. To parse, only six bare ampersands are escaped to valid XML references; numeric observations are unchanged. Parsed Historical tab has **5164 worksheet rows including header**, first trade in April 2006, last 2026-10-23. Historical `NAV per share` and `Shares Outstanding` are valid; **not** daily silver ounces. 2024-03-29 and 2024-03-31 `Shares Outstanding` missing; leave NA, not zero.

**SLV model implications:** share count delta can be a creation/redemption *proxy*, not direct USD flow or bullion tonnage. NAV is a fund price metric, not gold spot. Daily shares and price first-release vintage unverified. Do not use for strict original-day predictions until source timeline is validated.

**Fed H.15 directly downloaded** from
`https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15&series=bf17364827e38702b42a58cf8eaa3f78&lastobs=&from=&to=&filetype=csv&label=include&layout=seriescolumn&type=package`
SHA256 `75dcc355bf51e2c45bd04d9b4cfc7fbc1edaa81abef1c0318de8a18ac44b9906`.

**US Treasury real curve**: official annual CSV at `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{YEAR}/all?type=daily_treasury_real_yield_curve&field_tdr_date_value={YEAR}&page&_format=csv`.
Exact official-source by-year SHA256:
- 2023 `ef28bcafaca75c45bb6b3491b4df4bd1b5e2ab7ff35ac014b6f8362df330c0ca` 
- 2024 `d3ff00a9287ebf68fdc80e72fb2d1895a73c84b3ff2a6ca8c6d64648cb470f16`
- 2025 `d3d3131c41e1f93f4661d227ce7079049d51888b395aaff863b6ad8e08838b64`
- 2026 `fdc7c08fc76db7abf7784355516aec1b98d0a7cbcac88ca465587281cb082202`.

### Not downloaded: CME GC and SI
Both official PDF URLs
`https://www.cmegroup.com/clearing/risk-management/files/GC-2020-to-present.pdf`
`https://www.cmegroup.com/clearing/risk-management/files/SI-2020-to-present.pdf`
**exist and are viewable on CME's public website**, but GitHub runner response is HTTP 403 with publisher explanation `IP address is blocked due to suspected web scraping activity ...`. We must not relabel raw files as acquired or work around the publisher's access restriction. The permitted solutions are downloading manually through a browser at these exact official URLs; requesting authorized archival access from CME; or subscribing to CME DataMine CSV. Once supplied, archive with original publisher URL and hash and check **notice date vs effective date**, front-contract code/roll; until then **exclude CME from all fits**.

Direct FRED CSV attempts remain timeout, but historical FRB nominal and Treasury TIPS alternatives now actually acquired.

### Reproducibility
- GitHub script: `gold_axis_2026/tools/retrieve_missing_official_sources_20261026.py`, `gold_axis_2026/tools/retrieve_treasury_real_curve_20261026.py`.
- GitHub manual-only workflows: `.github/workflows/gold-missing-official-oneshot-20261026.yml` and `gold-treasury-real-oneshot-20261026.yml`.
- Runs: [40277837580](https://github.com/ataullahturgut/sim3-automation/actions/runs/40277837580), [40278659820](https://github.com/ataullahturgut/sim3-automation/actions/runs/40278659820).
- Source artifacts on runs are ephemeral (30 days); programmatic derived CSVs and quality report saved separately in user-facing data package, not committed as raw copyrighted vendor records.
- Data is downloaded, not model-retrained, not inserted to Neon. Do not assert improved false alarm rate. 2026 March/August examples already consulted by research team; a new honest blind test needs an independent future period.

**Conclusion:** SLV, official nominal and TIPS real-yield sources successfully captured/quality-flagged; CME remains explicitly blocked. Existing base14 and CFTC21 risk model is preserved.
