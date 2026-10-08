# GOLD EXECUTION — 2020–2026 LONG-HORIZON DATA ACQUISITION AUTHORITY

**Date:** 2026-10-08. **Status:** SOURCE/MODEL REQUIREMENT INVENTORY COMPLETE; ACQUISITION NOT YET EXECUTED.  
**Repo/branch:** `ataullahturgut/sim3-automation` / `gold-execution-channel-audit-20261006`  
**Machine-readable line-by-line inventory:** `GOLD_EXECUTION_2020_2026_SOURCE_MATRIX_2026-10-08.csv` (26 requirements).  
**Parent authority:** `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md` and `GOLD_EXECUTION_ALIGNED_HORIZON_HYBRID_RESEARCH_AUTHORITY_2026-10-07.md`.

## 0. Binding objective and time boundary

Build a **single durable, provenance-governed research raw-data base from 2020-01-01 through 2026-12-31, INCREMENTALLY**, adequate for:
1. DAY XAU/USD sign/size and realized path: bank decision around `09:00 -> 16:45/17:00 Europe/Istanbul`.
2. OVERNIGHT XAU/USD sign/size/tail risk: decision around `16:45/17:00 -> next eligible 09:00 Europe/Istanbul`.
3. WGC_NY3 and SOBTI_5_ET session-specific raw experts, plus baseline/orthogonal specialist context, as distinct session labels; these must not silently replace DAY/OVERNIGHT.
4. Executable portfolio/transaction evaluation using genuine bank or Borsa İstanbul bid/ask quotes, which **cannot be substituted** with synthetic zero-spread XAU quotes.

**2026-10-08 is the current date.** Data for `2026-10-09..2026-12-31` do NOT exist as realized history today and must be appended only after each event/bar actually occurs and is source-ready. Today's data are partial; historical training cutoffs require already completed bars/targets. Daily/weekly publication revisions are not known at an earlier origin.

A `2019` optional **WARMUP_ONLY** source slice is permitted if 2020 January origin features require 60/252 matured earlier records, but `2019` is NOT a 2020–26 test year and must not be folded into 2020 metrics. Otherwise early 2020 is explicitly history/warm-up, not scored.

**Scope lock:** This is the execution DAY/OVERNIGHT and SESSION raw-data acquisition architecture. MONTHLY H=1 VW-MIDAS/GPR remains a separate target with independent release lag and manifest. Reuse physical Au/Ag/Pt/Pd source observations only after each project's own vintage/symbol authority passes.

## 1. IMPORTANT findings from actual current GitHub authorities

Existing governed sources and intervals verified in the branch:

| Raw/source family | Already available | Acquisition verdict |
|---|---|---|
| **XAU/USD 15m spot** | 2022 15m training archive; 2023–2025 full frozen historical backfill and target audit; 2025-H2–2026-Sep additional 15m coverage (40,504 rows during 2025-07 to 2026-09 study) | **DO NOT repurchase 2022–2025**. Audit 2020–2021, reconcile overlap, patch 2026 Oct to source-ready present |
| **XAU/USD 1h** | 17,644 2022–2024 research observations and source probes in 2025–2026 | Prefer deterministic 15m -> 1h aggregation + independent vintage QC, not a duplicate purchase |
| **GC/SI/NQ/ZN/CL CME 1h** | Archived `GLBX.MDP3`, 2022-01-01..2025-01-01 exclusive, 15 continuous symbols (five roots × roll `c,n,v`), OHLCV + `ts_event` + `instrument_id`; complete raw gate | **ALREADY THERE**, including **GC.n.0 5,917 / 5,894 / 5,938 hourly bars** in 2022/23/24. Fill **2020–2021 and 2025–2026** only. Preserve original continuous rules. Original archival 2022–24 quoted total ~USD 2.3586 is a historical audit amount, NOT a quote for a new download |
| **SI / PL COMEX 1m and derived 15m** | Original Databento source 2022–2024: ~1,882,086 raw 1-minute SI+PL rows; native vs derived 1h exact OHLCV 35,497/35,497 | Reuse and extend missing 2020–2021 and 2025–2026; do not query the same purchased interval again |
| **Gold/Silver/Platinum daily** | NOVA CORE3 source was reproduced from pinned historical StakTrakr raw references for 2023–2024 sessions | Audit **full 2020–2026 span/source-vintage** before expanding; daily source values are **calendar-date labels**, not proved intraday observations; D-1 clock is binding |
| **GVZ implied volatility** | Official Cboe 2021–2025, 1,257 dated daily values | Fill 2020 + 2026; D-1 rule, no same-day close |
| **DGS2 US 2-year yield** | Official Federal Reserve H15 2022-12-20–2025-12-31, 757 rows | Fill 2020–Nov2022 + 2026; D-1 unless publication-ready proved |
| **Gold CFTC COT** | Official F/FO combined disaggregated 1,060 reports from **2006-06-13 through 2026-09-29**; 2023/2025 release-delay regimes governed | **DON'T repull 2020–2025**. Audit weekly gaps, update 2026 incremental releases; preserve exceptional delayed availability stamps |
| **Economic release ledger** | US release records only partly complete; 2025 **FOMC = 0 rows**, a known completeness failure despite eight scheduled official meetings | **BLOCK combined calendar model** until official FOMC calendar and event-time/vintage map rebuilt for 2020–2026 |
| **FX / VIX / real yield / bank spreads** | Some FX vendor probes, daily external variables in historical studies, but no universally proven 2020–26 point-in-time same-source panel | First establish source span / permissions and quote; no unsupported blanket "available" assertion |

Additional nuance: **the GC 1h raw archive is already real**. Earlier notes described paired GC 15m price/volume as data-gated; that statement applies specifically to the **same-origin 15-minute or 1-minute GC-to-spot matching**, **not** to absence of GC data at *all* granularities. There is no independently confirmed full 2020–26 **GC 1m** panel in this authority.

### 1A. Don't misinterpret the archived CME roll series

Databento's continuous `GC.n.0` (nearest expiration) `GC.v.0` (volume-rolled) and `GC.c.0` (calendar-rolled) are DISTINCT identities. The provider documents that continuous prices are **not back-adjusted**. Do not create artificial overnight returns across contract rolls. Keep `instrument_id`, actual contract mapping, raw symbol, roll flags, and explicit `roll_spanning_bar`; compute like-contract returns or mask discontinuities before deriving causal basis/lead–lag. Do not pick the roll convention by which produces the best 2025 backtest. The earlier 2022–24 `GC.c.0` is sparse compared with `GC.n.0`: not all three series should be mixed or counted as independent experts.

Databento OHLCV `ts_event` is an **interval START timestamp**, and no bar is output when no trade occurred; an absent 1m bar may be an inactive-market interval, not an ingestion defect. Audit session-open/maintenance periods separately.

## 2. Source packages directly derived from the actual model inventory

The core research does **not** demand every potentially correlated financial series up front. Source requirements are linked to named model families and a falsifiable incremental hypothesis.

| Package | Model / mechanism | Minimum variables + frequency | Priority / condition |
|---|---|---|---|
| **TARGET-PRICE** | DAY/OVN; PRAMV; LIT; PSF; V5 session targets, PATH/FPCA and RFR | XAU/USD **15m OHLC** UTC, actual first-source-ready bar, holiday/DST; optional **1m only around 09/17 and surprise releases** | **P0, indispensable** |
| **VENUE-DISCOVERY** | CAVS; continuation failure; spot-vs-COMEX lead/lag, volatility spike confirmation | `GC.n.0` **1m OHLCV** and derivations 15m; matched XAU spot; actual contract IDs; 1h already archived | **P0 research independent information**, quote & targeted pilot before full 7yr 1m |
| **TAIL-HAR-GVZ** | VEGA; downside-tail / HAR+GVZ; ordinary/large movement risk and calibration | completed 5/20/60 overnight returns from XAU + Cboe **GVZ D-1 daily** | **P0**, strong existing positive probabilistic signal, different from directional edge |
| **STRUCTURAL-CORE3** | NOVA A0/A1, session Logistic, structural IRIS; monthly raw cross-metal context (separate labels) | Gold/Silver/Platinum daily **D-1 aligned**; SI/PL intraday only if source/clock benefit | **P0 daily, P1 intraday extension** |
| **REAL-YIELD / USD** | Gold rates/FX response; US afternoon regime; RuleFlow; source-safe residuals | DGS2; DFII10 daily; intraday EUR/USD USD/JPY GBP/USD 15m if available | **P0 DGS2/DFII10, P1 intraday FX** |
| **POSITIONING** | OPAL/HELIOS COT reversal; crowding regime | Weekly COMEX CFTC Gold disaggregated, futures-only and futures+options; report + publication timestamps | **P0 but already mostly present — update only** |
| **EVENT-CLOCK** | PRAMV macro veto; Sobti news-price discovery; jump model | FOMC/BLS/BEA event schedules and actual-release time; FOMC 2025 repair; actual-vs-consensus only with verifiable prior consensus | **P0 schedule, P1 paid surprise data** |
| **CROSS-RISK** | SAGE regime, NQ/ZN/CL, VIX, USD, global risk-on/off | CME NQ/ZN/CL 1h existing 2022–24; extend; VIX daily D-1; WTI/Brent carefully distinct | **P1 for matched incremental signal test** |
| **OPTION-SKEW** | True asymmetric option downside-risk-premium research | Historical put/call volatility surfaces with strikes/tenors/known_at; `GVZ` alone **cannot reproduce** downside skew | **P2, quote/licensing first** |
| **EXECUTION-QUOTES** | Real bank actionability and cost | chosen bank bid/ask / BIST tradeable instrument, executable timestamp, spreads, hours, fees and position/inventory | **P1 required before profit/tradability claim** |

## 3. Concrete planned acquisition phases — zero redundant purchases

### Phase 0 — Inventory, contracts, no charged download

1. Inventory all existing repo/approved external storage source bundles by `dataset, symbol, schema, first/last_UTC, origin timezone, bar completeness, SHA-256, instrument_id, vintage`. Compare to the SOURCE_MATRIX. Do NOT infer data completeness from a successful three-day API probe or a result CSV.
2. Freeze a **RAW-CONSISTENT 2020–26 target contract** for DAY `09:00→17:00` and OVN `17:00→next eligible 09:00` in `Europe/Istanbul`; target end is not known before the end; 17:00 open must not be treated as executable after completed 16:45–17:00 bars.
3. Cross-check 2022–25 OHLC and original 2023–25 target labels against existing known checksums and matched-date 769/769 raw target prices. No changing existing frozen V1 model/2025 diagnostics.
4. Ask existing vendor APIs for metadata `earliest_timestamp`, `get_dataset_range`, `get_cost`, access entitlement and available byte volume. **Cost enquiry is not a purchased download**; if source is inaccessible do not fabricate fill.
5. Provide per source `READY_EXISTING / NEED_GAP_DOWNLOAD / VENDOR_PROBE_REQUIRED / CANNOT_ACCESS / FUTURE_PENDING`, and per fiscal year expected eligible dates, missing slot count and cost estimate. Current matrix entries marked unknown are NOT confirmed missing in every storage mount.

### Phase 1 — Finish XAU benchmark labels and primary low-cost risk history

**Highest priority**, because the independent XAU signal has no substitute:
- Retrieve only verified-missing `XAU/USD 15min` historical chunks for **2020-01-01..2021-12-31** (plus optional needed 2019 warm-up); preserve 2022–25 originals.
- Validate the existing 2025–2026 overlapping archives; add **2026-10-01..2026-10-08 only as far as completed and source-ready**. Future 2026 append incrementally later.
- Add 2020 official GVZ and 2026 GVZ to existing 2021–25; add missing 2020–Nov 2022 DGS2 and current 2026; obtain daily DFII10 2020..current for a limited real-rate challenger. Do not assume same-day rates/GVZ are published by the morning issue.
- Build the 2020–2026 `calendar_version`, `market_open`, `available_at` and lagged target series in separate, immutable source/label tables; explicitly mark holidays and partial target days.
- Independently recompute DAY/OVN labels and flag zero gap/horizon-ineligible dates. Store **continuous target log return, binary UP/DOWN, ≥1% both-sign risk, ≥2% absolute tail, realized intraday RV/jump path**, each target in own namespace.
- **Data acceptance gate:** >=99% of expected eligible spot 15m timestamps in each ordinary session (with documented holidays), *no missing 09/17 anchors*, zero duplicate UTC primary keys, OHLC consistency, exact-match with archived 2023–25 target returns on common dates. A threshold of 99% is a *provisional QC proposal*, not authorization to impute missing pivot bars.

### Phase 2 — COMEX causal price discovery, staged pilot before full 1m purchase

1. Existing **2022–24 GC 1h c/n/v** is a test-ready **low-frequency baseline**; confirm actual `t_ready < issue_time` and no roll-spanning return. It is insufficient to establish 16:00–17:00 half-hour event-level GC lead/lag.
2. Check availability and cost for `GLBX.MDP3`, `GC.n.0`, `ohlcv-1m` over one **matched pilot period in 2020, 2022, 2024 and 2025/2026** chosen by *calendar blocks*, not by known tail-event days (avoid selection on outcomes). Keep `ts_event`, `instrument_id`, price and volume. Native `ohlcv-1h` and aggregated 1m→1h must agree on identical instrument+UTC hours except documented roll/market close.
3. Pilot at daily 09:00 and 17:00 origins: `GC-spot lagged relative return`, `basis change`, `same-sign vs divergence`, `GC volume burst`, `GC pre-origin jump state`. Compare identical-date XAU-only model against XAU+GC. No same-day look-ahead from unclosed last bar.
4. Only if the source and a **pre-2025 development-only incremental-value gate** pass, approve or justify extending 1-minute acquisition to full 2020–2026; otherwise 1h is available for economical broader-regime study.
5. Need **explicit cost cap / billing approval** once vendor cost quotes exist, rather than applying 2022–24 historical paid prices to all seven years.

### Phase 3 — Low-cost independent state completion before more expensive events/options

- Extend **GC/SI/NQ/ZN/CL 1h** from their 2022–24 existing archives to 2020–21 and 2025–2026 to date; one `n.0` baseline roll with `c/v` reserved for source/roll robustness, not 15 separate predictive votes.
- Extend SI/PL existing `ohlcv-1m` only for gaps and if the corresponding cross-metal add-one-source matched test is justified (2022–24 is already validated); if hourly sufficient, start at 1h for missing years.
- FX `EUR/USD, USD/JPY, GBP/USD`: probe exact full-span vendor intraday eligibility; do NOT confuse daily broad USD index with instantaneous tradeable DXY or synthesize FX close at unseen timestamps.
- VIX and broad USD official daily history may be inexpensive, but keep lag contract; do not add features by sheer abundance.
- WTI `CL` is a CME contract already in the hourly source; **Brent is not the same instrument**, and licensed ICE intraday data must not be fabricated by renaming CL.

### Phase 4 — Official US event release calendar and historical consensus

- Build a 2020–2026 full official release schedule (FOMC, CPI, NFP, AHE, unemployment, PCE, JOLTS, ADP where licensed), including unexpected postponements, data revision vintages, and official press-release times.
- **Repair 2025 FOMC=0 ledger problem first**. Weekly CFTC reports have source-time delay exceptions (2023 and 2025); preserve those governing exceptions.
- At each issue time: `scheduled_not_yet_released`, `released_with_actual_and_pre-release_consensus`, `late_or_unknown`. Never `missing => no event`.
- Economic **consensus** may need paid PIT snapshots; published revised actuals alone are insufficient to reconstruct the surprise available at the historical 09:00 / 17:00 forecast.
- Calendar-only EVENT_CLOCK challenger vs actual/consensus EVENT_SHOCK challenger must remain separately flagged by data readiness.

### Phase 5 — Bank-executable price evaluation

- Specify the exact instrument(s) user can transact between ~09:00–17:00 Istanbul. Required source: local bank BID/ASK quotes with quote_time, end-user fees/limits; if BIST gold ETF/certificate, official prints and/or level-1 bid/ask, session breaks, settlement/tax/taker fees.
- Report **signal issue -> first actually obtainable actionable quote** latency; no idealized immediate trade at original signal bar; compare long-only/flat states and downside drawdown. Bank spread after ~17:00 requires direct quote proof, not spot volatility extrapolation.
- Only after this can 2020–2026 backtests be called *bank-executable*.

## 4. Database/flat file data contract — every source and target

For raw `market_observation` and daily `economic_release` schemas, preserve these fields where applicable (unknown should be null, never invented):

`source_id, vendor, dataset, raw_symbol, instrument_id, roll_rule, interval, price_unit, volume_unit, ts_event_utc, bar_start_utc, bar_end_utc, source_published_at_utc, received_at_utc, available_at_utc, source_vintage, raw_file_sha256, ingestion_sha256, retrieved_at_utc, contract_roll_flag, source_gap_flag, exchange_calendar_id`.

Every feature `feature_lineage` must carry `origin_id, feature_name, feature_value, input_source_ids, input_last_completed_at_utc, max_input_available_at_utc, logic_version, is_pit_safe`. Reject the feature if source readiness is **unknown** or if `max_input_available_at_utc > signal_issue_time_utc`.

Separate `target_ledger`: `target_id, issue_clock, target_start_utc, target_end_utc, start_price_type, end_price_type, start_price, end_price, return_log, direction, tail_up_1pct, tail_down_1pct, tail_abs_2pct, holiday_eligible, target_matured_at_utc, frozen_target_source_sha`. Never store target outcome in a production feature table.

**IMPORTANT**: a daily released event "calendar date" and its actual **announcement time** must be distinct; the original 2025 incomplete event ledger proved this is a material leakage risk. Weekly COT's *as-of report date* and *publication available_at* must remain distinct.

All source revisions are append-only; hash raw provenance and do not overwrite model-comparison source vintages. Deduplicate by (source, actual contract, UTC interval) with deterministic precedence. Never forward-fill market hours across exchange closures or use future-close values. Continuously scheduled 2026 updates have status `FUTURE_PENDING`, not `MISSING`.

## 5. Model/evaluation use contract

**No statistical guarantee from merely more history.** Structural change across COVID 2020, 2022 rates and 2025–26 high volatility can reduce performance; longer histories help if weighted/matched by regime *using only past mature data*. Train and compare to short-history baselines.

Suggested **new-research** chronology (not a rewrite of previously frozen policy labels):
- 2019 if required: independent history / indicator warm-up only.
- **2020–2022:** raw source validation + historical initial training and regime research.
- **2023–2024:** expanding-origin development and nested representation selection. Keep yearly, half-year and regime-separated metrics.
- **2025:** already-inspected archive retrospective *transport*; never pretend still sealed OOS or tune after looking then claim pristine.
- **2026 through 2026-10-08:** additional historical stress (may also have been inspected in the project); not automatically unseen just because later calendar year.
- **2026-10-09 onward:** only observations not yet occurred, with forecasts *persisted and hashed before their target begins*, qualify as prospective after complete issue/source-time recording. December 2026 targets ending in Jan 2027 cannot count as matured by Dec 31.
- Monthly/weekly labels remain in separate source/target namespaces.

For each candidate report: per-year n and source coverage; source clock/PIT PASS; day+overnight sign BA, both-class recall, accuracy and Brier; signed tail calibration and AUC/PR-AUC; distribution shift; false warnings vs risk-alarm budget; unchanged PRAMV V1 same-date comparator; gross hypothetical sign-return AND actual bid/ask long-only execution; multiple-search correction/block-bootstrap intervals, plus a strictly prospective confirmation.

**Candidate scientific gates before expanding paid data**:
1. Same exact origins and target labels with full source-ready proof for all sources.
2. First prove GC or extra source adds *out-of-origin* error diversity/rescue on 2023 and 2024 separately; not just better pooled 2025 AUC.
3. If a model's predictive gain disappears under equal alert budgets or broken-class recall, reject/flag; do not purchase an expensive multi-year options archive solely to chase a reviewed retrospective 2025 statistic.
4. No new policy changes to the frozen PRAMV V1. A challenger can coexist, but must have its own identity and fresh prospective date.

## 6. Actual acquisition order recommendation

**Approve source/cost gate in this order**:
1. XAU 15m gap coverage 2020–2021, and validated post-Sep2026 15m to current source-ready bar.
2. GVZ 2020+2026, DGS2 2020–22 and 2026, DFII10 2020-to-current, 2025 official FOMC PIT calendar repair.
3. Before any broad GC 1m purchase, first use existing 2022–24 GC 1h; request **metadata and per-year pricing** for 1m only; small calendar-block pilot.
4. GC 1m expansion only after matched clock/roll/pilot proof and cost approval; extend existing CME 1h for the missing years.
5. Fill SI/PL then FX/NQ/ZN/CL/VIX conditional on incremental source-specific model evidence.
6. Separately arrange bank executable quote data and any licensed consensus/option skew before claiming financial success.

For major source API batches, use monthly **inclusive start / exclusive end** UTC windows with receipt manifest and transactional checkpoint. Do not re-request already-saved complete chunks. Twelve Data's public support currently specifies a maximum **5,000 observations per response**, so chunk the 15m XAU and FX history by suitable time periods and reconcile overlapping vendor boundaries. Databento publishes `metadata.get_cost` for pre-purchase quotes and supports continuous `c/n/v` symbols, but historical prices are not roll-back-adjusted.

## 7. Sources & existing project authority

**Internal auditable archives:**
- `GOLD_DATABENTO_RAW_ARCHIVE_2022_2024_SUMMARY_2026-10-06.json`
- `GOLD_DATABENTO_RAW_ARCHIVE_COVERAGE_2022_2024.csv`
- `GOLD_DATABENTO_CONTINUOUS_SYMBOLOGY_2022_2024.json`
- `GOLD_SI_PL_1M_15M_VALIDATION_SUMMARY_2026-10-06.json`
- `GOLD_EXECUTION_15M_COVERAGE_PROFILE_2026-10-06.json`
- `GOLD_GVZ_DGS2_RAW_BACKFILL_SUMMARY_2026-10-06.json`
- `GOLD_COT_PIT_REAUDIT_SUMMARY_2026-10-06.json`
- `GOLD_OVN_2022_WARMUP_HAR_GVZ_RESEARCH_RESULT_2026-10-08.md`
- `GOLD_EXECUTION_GVZ_SIGNED_TAIL_RESEARCH_RESULT_2026-10-08.md`
- Main manifest model lineage section `5E.8I` and execution-aligned horizon authority.

**Vendor/official documentation (checked 2026-10-08):**
- Databento continuous contracts: https://databento.com/docs/examples/symbology/continuous
- Databento OHLCV bar timestamp, omission of zero-trade intervals: https://databento.com/docs/schemas-and-data-formats/ohlcv
- Databento historical `get_dataset_range` and `get_cost`: https://databento.com/docs/api-reference-historical
- Twelve Data historical chunks/5k row response cap: https://support.twelvedata.com/en/articles/5214728-getting-historical-data
- CFTC historical reports and 2026 releases: https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalCompressed/index.htm
- CFTC release schedule: https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm
- Federal Reserve FOMC calendar: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
- Federal Reserve/FRED real yields (DFII10): https://fred.stlouisfed.org/series/DFII10
- Cboe official historical GVZ source frozen in project's raw-source backfill summary.

**Scope of this deliverable:** COMPLETE audited model-driven requirements, source/reuse map, acquisition gates and ordering; **no paid historical vendor request or prospective future data download was executed as part of this planning task**. No model was retrained and no 2026 future event was labelled as realized.
