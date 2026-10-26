# GOLD RISK V8 — ACTUAL CORRECTED DATE-CLOCK REPLAY (26 October 2026)

**Executed and reproduced**, not merely an audit proposal. Branch: `gold-risk-official-download-retry-v4-20261026`.

## What actually changed

1. Fed H.10 Broad USD no longer assumes every Monday at 16:15 New York. Official Monday federal holidays are shifted to **Tuesday 16:15 America/New_York**. Explicit 2023–2026 Fed closure Mondays are frozen in `gold_axis_2026/tools/gold_risk_release_clock_v8.py`, with out-of-coverage fail-closed behavior. H.10 2026 16 January observation: NOT usable on 19 January; earliest scheduled 20 January at 16:15 NY. Exact `aware datetime` is required for TR09 checks. Date-only means legacy NY17:30.
2. The BASE14 code `gold_axis_2026/tools/gold_forecast_risk_overlay_2023_2026_v1.py` was **actually patched** to use the release clock, without changing mathematical features, training splits or quantile thresholds.
3. CFTC21 code `gold_axis_2026/tools/gold_risk_cftc_independent_overlay_v2.py` was **actually patched** with the conservative date+clock gate, preserving the existing GC/SI quality-gated `+7 days` proxy for normal weeks and 2025 delayed releases `official publication +1 day`. Tuesday POSITION dates are not public release dates.
4. SLV five-session research code `gold_axis_2026/tools/gold_risk_source_features_v6_20261026.py` was **actually patched** to exclude 2024-03-29 Good Friday and 2024-03-31 Sunday, without fabricating zero holdings/shares. Original 958 data rows remain intact for SHA/audit; eligible market-session rows 956.
5. **10/10 code regression unit tests PASS.** Independent publisher input SHA match; **994 date-asof issuer source rows replayed**. Neon read-only pairing of 945 original gold day origins indicated **18** where Monday-early H.10 source day was wrong; the original CFTC21 model's **873 actual shared feature origins** contained **17** shifted H.10 origin days.

## Exact preserved input and actual model replay

Recovered the original **24 October 2026 scientific result** archive and re-used its exact original `gold-risk-overlay-2023-2026-source-artifact.zip` (which contains `risk-overlay-source.json`) and `CFTC_GC_SI_2023_2026_QUALITY_GATED.csv`. Baseline 24 October script reproduced byte-compatible score summary. A corrected independent V8 script changed ONLY Fed H.10 release eligibility plus strict conservative CFTC as-of checks.

- Models: `RobustScaler`, `IsolationForest(n_estimators=200, random_state=1701)`, 90% yellow / 95% red **fit-set** score quantiles.
- 2025 475 fit origins (2023–24), 232 same score origins.
- 2026 707 fit origins (2023–25), 161 same score origins (through 2026-09-21).
- **873 aligned input origin rows**, exactly the same dates and target labels before/after; no 2026 post-hoc tuning; invalid 2026-02-27 source price windows quarantined.
- CLEAN reproducibility test: extracted fresh archive, ran 10 unit tests and executed corrected model in isolated folder; corrected JSON score summary compared **exactly equal** to the independently calculated V8 result.

### Retest results (old -> fixed; 2026)

| Series | Red alert origin days | Next-day loss at least 3% hit | Next-five sessions -5% loss positive origin hit | 5-day-label false red origin days |
|---|---:|---:|---:|---:|
| BASE14 | **51 -> 46** | **4/4 -> 4/4** | **9/13 -> 9/13** | **42 -> 37** |
| BASE14+CFTC7 | **29 -> 31** | **4/4 -> 4/4** | **6/13 -> 6/13** | **23 -> 25** |

### Retest results (old -> fixed; 2025)

| Series | Red alert origin days | Next-day loss >=3% hit | 5day loss >=5% hit | 5-day-label false red origin days |
|---|---:|---:|---:|---:|
| BASE14 | 31 -> 31 | 2/3 -> 2/3 | 4/5 -> 4/5 | 27 -> 27 |
| BASE14+CFTC7 | 31 -> 30 | 3/3 -> 3/3 | 5/5 -> 5/5 | 26 -> 25 |

For 2026 there are **four clusters of overlapping future five-day loss labels**, not four proven pre-onset independent crashes:
- Jan 26–30, Jun 03–05, Jun 17–18, Aug 25–27.
- BASE14 has RED **inside 4/4 label groups**; CFTC21 inside **2/4**; this **does not prove RED preceded the true first physical drop**. On Jun03–05 BASE14 RED only Jun05, after first eligible 5-day origin.

**Known false warnings remain:** 2026 March30–April03 BASE14 is RED on all five origin days, with no >=5% future loss; August11 BASE14 YELLOW, CFTC21 RED, with no comparable future 5-day drop. Calendar repair improved retrospective alarm counts, but **did not solve these warning episodes**. Do not claim falsely that they were fixed.

### Source and safety qualifications

- H10 release schedule is verified, but archived dollar-index **original first numerical vintages** are not source-captured on each historic release; same for reconstructed metal reference quotes, and other historic indicator snapshots. Date fix is **necessary but not sufficient** for genuine point-in-time trading validation.
- GLD/SLV first prints, Treasury TIPS revisions, CME GC/SI margins remain pending / quarantined. Neither the model nor thresholds were upgraded from retrospective testing.
- **No Neon mutation, no live model/application deployment, no scheduler enablement.** Existing BASE14 remains independent primary major-drawdown reference; CFTC21 an experimental comparator.

## Reproducibility

The user-facing **GOLD_RISK_V8 corrected actual test ZIP** contains the exact original source ZIP, exact original GC/SI 398-row CSV, original V2 Python script, independently corrected V8 full script, clock and tests, exact old/new score manifests, old/new daily alarm CSV, model paired comparison, alert-change audit, source-date integrity results, and the original execution logs. GitHub branch also contains patched research pipeline code and regression tests (listed above).

Reference sources: https://www.federalreserve.gov/releases/h10/default.htm ; https://www.federalreserve.gov/data/releaseschedule.htm ; https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm

**V8 STATUS: SOURCE-DATE CODE FIX PASS, MATCHED OLD/NEW MODEL REPLAY PASS, CLEAN REPRODUCTION PASS, HISTORIC NUMERIC FIRST-PRINT PENDING, LIVE DEPLOYMENT GATE CLOSED.**
