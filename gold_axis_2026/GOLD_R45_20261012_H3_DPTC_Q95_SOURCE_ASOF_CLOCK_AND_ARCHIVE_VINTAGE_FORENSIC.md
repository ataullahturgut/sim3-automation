# R45 — DPTC-Q95 H3 end-to-end input clock, archive-vintage and maturity forensic (2026-10-12)

**Status:** FORENSIC_VERIFIED_SOURCE_DATE_AND_VINTAGE; ISSUE_TIME_NOT_CERTIFIED; RETROSPECTIVE_ONLY. Binding correction to assumptions in R42/R43/R44. No historic predictions or labels overwritten.

## 1. Question / scope
Trace the top 2026 H3 hybrid **DPTC-Q95 = SAGE V2 + RuleFlow V3-TG baseline + dependence/SELLR trust gate**. Audit exact 2026-05-07 issue forecast (source cutoff 2026-05-06, H3 target source date 2026-05-11), date/clock and first real availability, and compare vintages of the *actual frozen* StakTrakr source; not a hypothetical intraday trade forecast.

## 2. 7 May 2026 source-clock ledger — Türkiye DST does not vary
| Dependency | Recorded source observation and lineage | Last raw observation window / publication | Status |
|---|---|---|---|
| Gold, silver, platinum, palladium | StakTrakr `sqld` `spot-history-2026.json` origin source date **2026-05-06**, values Gold 4675.01, Silver 76.50, Platinum 2026.81, Palladium 1534.30 USD/oz | Full UTC May06 window = 6May **03:00TR → 7May 03:00TR**; daily average earliest numerically complete at **7May 03:00TR**; actual GitHub file publishing much later; no contemporaneous firstprint for May07 | OBS_END_PASS; ORIGINAL_ARCHIVE_ASOF_ISSUE_FAIL |
| Twelve Data XAU/USD 1h IRIS/RIFT and downstream path inputs | `gold_h3_iris_v1.py`: previous `feature_cutoff_date=2026-05-06`, `America/New_York local_hour==16`, hourly close-derived features; no issue-day hourly bar | **16:00 NY EDT = 23:00TR May06 is the opening time of the 1h candle**, so its close available no earlier than **17:00 NY = May07 00:00TR** (+vendor lag). Twelve Data official documentation defines `datetime` as candle opening. Previous guidance that the 16NY hour was *fully* known at 23TR was wrong | OBS_END_PASS_AT_00; FIRSTPRINT_UNKNOWN |
| CME GC volume/GC call/put volume options | `gold_h3_rte_v1.py` enforces `cme_trade_date < feature_cutoff_date`; 7May row has trade date **May05** | CME's Daily Bulletin final for previous trade date ~10:00 Central next business day = **May06 18:00TR** in US CDT; preliminary may be sooner, exact artifact publication proof not preserved | FINAL_SCHEDULE_SAFE; ARCHIVED_FIRSTPRINT_UNKNOWN |
| Gold/NDX/VIX/USD/rate daily cross-market | `gold_h3_diverge_proxy_v1.py` and frozen `GOLD_H3_DIVERGE_PROXY_V1_PANEL_2026-10-03.csv`: `metal_source_date/usd_source_date/yield_source_date/ndx_source_date/vix_source_date=2026-05-05` for cutoff May06 | Source dates predate cutoff. Public market closes may be known by next session, but historical as-of API release and revision/vintage checks were not saved | SOURCE_DATE_PASS; VINTAGE_OPEN |
| Historical Global-XAU readiness rates/FX | `gold_short_horizon_global_xau_readiness_r2.py` `cut_h15=issue-2 calendar days`, `cut_h10=issue-7`, `cut_us=issue-1`, `merge_asof backward`. May07 cuts: May05 (H15), Apr30 (H10), May06 (VIX/NDX). | Calendar guard **is not proof of official released_at**; previous-day futures/equities must satisfy end-of-session/publication gate | DATE_GUARD_PRESENT; PIT_UNCERTIFIED |
| CFTC COT / OPAL | `GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv` 7May row: `cot_report_date=2026-04-28`, governed `cot_available_date=2026-05-05` | Official 28 Apr 2026 Tuesday report released **Fri May01 15:30 EDT = May01 22:30TR** (CFTC official 2026 schedule), so available before May07; ledger's May05 is conservative date-level stamp | RELEASE_PASS |
| DPTC gate | `gold_h3_dptc_v1.py`: baseline SAGE+RuleFlow vote; phase state from past 60-row Gold/NDX/VIX correlation; SELLR H3 reversal log-likelihood score trained on 2023-24; 2025 threshold; trust based on matured older H3 outcomes | Phase state for source cutoff May06 can only be computed when those origin daily features are available; posthoc construction/fitting of controller in October means **no 7May real-time Q95 issued_at existed** | 2026 BACKTEST, NOT LIVE |

Core 7May row from frozen model artifacts: `feature_cutoff_date=2026-05-06`, `forecast_issue_date=2026-05-07`, `target_end_date_h3=2026-05-11`, Q95 direction UP (underlying V5 p(UP)=0.5326192922487963, SAGE/RuleFlow UP, no Q95 intervention). Stak May06 gold origin 4675.01; May11 gold H3 target 4701.32. **Target UTC May11 average covers May11 03TR→May12 03TR**; it is not fully realized on May11 during ordinary day hours.

## 3. Primary hard forensic discovery — historical 2026 May frozen file was NOT up-to-date at the origin
The original model reads `lbruton/StakTrakr/data/spot-history-2026.json` at frozen commit `54fdf1c8d39b7b6c7b874d0f30f784296e886044` dated **2026-09-29**. The pinned file is a *later vendor vintage*, not a May07 vintage. Compare actual upstream Git commit contents:

| Provider repo SHA | Git commit clock and local | Last date in `spot-history-2026.json` | May06 four metals present? |
|---|---|---|---|
| `bc483072fd...` | 2026-05-06 11:44 CDT = **May06 19:44TR** | Apr30 | NO |
| `69b555704379...` | 2026-05-07 23:44 CDT = **May08 07:44TR** | Apr30 | NO |
| `4e154212d0fd...` | 2026-05-09 02:41 UTC = **May09 05:41TR** | Apr30 | NO |
| `046b86ba8af...` | 2026-05-09 18:11 CDT = **May10 02:11TR** | May09 | YES, May06 Gold 4675.01 and all other metals match later pinned vintage |
| `54fdf1c8d39...` | 2026-09-29 merge | Sep29 | YES |

**Conclusion**: Between two observed Git snapshots (**May09 05:41TR and May10 02:11TR**) May06 source-date spot averages became visible in the upstream repository. Exact first commit/publication clock within that gap is not proved. They were ABSENT in sampled actual May07 and May08 archived vintages. The daily source prices are independently retrospectively reproducible; this does not supply a causal real-time May07 `issued_at` on the specified ORIGINAL year-file artifact. Spot MetalpriceAPI/sqld may have been available by alternative API at May07 but neither its historical raw query availability nor a reconstructed model run is proven. Do not say 'data never existed' or 'prices are wrong', only that the **specified frozen public historical file wasn't there then**. Upstream source `spot-year-history.js` also explicitly describes historical frozen/export issues and STRK-403 repair on 2026-09-27.

## 4. Formal chronologies

- **Observation lower bound** for 7 May H3 model origin = max(May07 03TR complete source UTC avg, May07 00TR Twelve 16NY hour close, May06 CME official final, older COT/external) = **7 May 03:00TR** *if same-day publication of completed `sqld` averages and all other vintage inputs could be verified*. This is not a certification.
- **Actual given old GitHub source file path**: May07 first-print **FAIL**; even May09 05:41TR source file remained stale; source May06 is visible by May10 02:11TR. Full model cannot be claimed executable at May07 from original file path. The model DPTC-Q95 itself was assembled/frozen **2026-10-05**, not issued May07.
- **Historical 08NY=May07 15TR deadline** is a governance cutoff, never proof a historical forecast had been generated or available then.
- **H3 actual target clock** for May07 issue = `log(AVG_May11/AVG_May06)`, May06 complete May07 03TR, terminal May11 complete May12 03TR, vendor publication later. Not clock-to-clock +72h, not first-three-post-issue-days. Do not shift target to May12 merely to describe original model.

## 5. DPTC timestamp / maturation bug, replicated
Code `gold_h3_dptc_v1.py` uses `pd.to_datetime(tl.target_end_date_h3, errors="coerce")` without `format="mixed"` on a column containing dates formatted `YYYY-MM-DD` for 2025 and `YYYY-MM-DD 00:00:00` for 2026. Under the pandas parsing behavior used in source, 2026 target dates parse as `NaT`, visible as **empty `target_end_date_h3` in `GOLD_H3_DPTC_V1_ACTIONS_2026-10-05.csv`**. Thus future result-maturation feedback handling was not functioning as intended for 2026.

Independent replay in JS on all **41** frozen HANDOFF timeline records, comparing 2026 phase and trust policy with (a) NaT never-mature logic versus (b) correctly parsed target dates: BOTH yielded the SAME **13 Q95 action origins**, 11 rescues, 2 breaks (2026-06-01, 2026-07-17), and 2026 baseline 126/191 +9 net = 135/191. Hence **reported 2026 aggregate score numerically unaffected in this specific replay**, even though the code defect is real and needs an explicitly versioned fix. This is not proof the controller is generally safe on other years/paths; don't silently revise the historical output.

## 6. Accurate binding conclusion
- **User hypothesis (different as-of windows consolidated at an origin then H3 target)**: supported as an intended design and observation-time constraint; variable observation source dates indeed vary, and 7May row contains no planned model feature from after May07.
- **Availability/inference as-of 7May**: NOT established; **known direct counterexample** is missing May06 complete metal averages from the frozen-file source in May07 repository snapshot. Current quoted May scores are retrospective October synthetic forecasts, not actual realtime May-issued DPTC.
- **PIT risk**: static `date` / conservative publication lag not equivalent to archived provider `released_at`, especially Stak reprocessed historical provider vintage; 1h open-anchored candle must mature to NY17.
- **Next valid causal test**: preserve original 3-source-date H3 label; choose a predetermined first confirmed as-of timestamp and historical provider vintage on each date; only then replay the same DPTC model, with matured labels and training cutoff, and compare 2026 only prospectively after Oct05 freeze. Backtesting May with reconstructed point-in-time metal averages must be labeled **simulated PIT**, not actual preissued forecast.

## 7. Reproducible paths
- `gold_axis_2026/tools/gold_h3_dptc_v1.py`; `GOLD_H3_DPTC_V1_ACTIONS_2026-10-05.csv`; `GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V1_TIMELINE_2026-10-04.csv`; `GOLD_H3_DEPENDENCE_PHASE_SHIFT_V1_PANEL_2026-10-05.csv`; `GOLD_H3_COMPETENCE_TRANSITION_V1_SELLR_SCORES_SOURCE_2026-10-05.csv`.
- `gold_axis_2026/tools/gold_h3_iris_v1.py` `build_anchor_features`; `gold_axis_2026/tools/gold_short_horizon_global_xau_readiness_r2.py`; `gold_axis_2026/tools/gold_h3_diverge_proxy_v1.py`; `gold_axis_2026/tools/gold_h3_rte_v1.py`; `GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv`.
- Pinned original upstream price source `lbruton/StakTrakr@54fdf1c8d39b7b6c7b874d0f30f784296e886044` `data/spot-history-2026.json`; compare snapshot refs above.
- Official Twelve Data `datetime` is candle BAR OPENING: https://twelvedata.com/docs
- Official CME Daily Bulletin next-morning final: https://www.cmegroup.com/market-data/daily-bulletin.html
- CFTC weekly COT schedule: https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm
