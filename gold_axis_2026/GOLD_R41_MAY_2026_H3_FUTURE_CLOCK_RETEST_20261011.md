# R41 — MAY 2026: DPTC-H3 directional success AFTER signal time, independently verified on two 15m providers

> **BINDING CORRECTION (R42, 2026-10-12):** The original May2026 H3 GOLD provider was **StakTrakr `source:sqld`**, proven from the original pinned upstream SQL source to be **`AVG(spot)` over a complete UTC calendar day** (**03:00TR day D → 03:00TR day D+1**), NOT a single instant quote at 15TR, 17TR or synthetic `12:00:00` tag. R41's independent 15TR spot→17TR spot comparison is a DISTINCT discretionary investor-clock target, not the appropriate first test of the original H3 research claim. **Correct apples-to-apples, May 21 unchanged H3 forecasts:** original Stak UTC-day AVG→UTC-day AVG **17/21=80.95%**, and two independent 15m vendors reconstructed under the **same UTC-day-average contract** also **17/21=80.95%**, with **21/21 exact H3 direction-label matches to original**. Separately, 15TR instantaneous issue quote→ORIGINAL H3 target-date full UTC daily AVG: **12/21 Dukascopy, 11/21 HistData**. Distinguish the historical daily-average-label success from an investor-issued instant-entry claim; do not erase or relabel original H3 accuracy. See `GOLD_R42_20261012_ORIGINAL_H3_DATA_SOURCE_TIME_CONTRACT_AND_MAY_VERDICT.md` and R42 21-row source-level CSV.


**Date:** 2026-10-11. **Scope:** all **21** May 2026 `forecast_issue_date` rows, original H3 DPTC-Q95 votes unchanged. We compare **historical original H3 label** to **strictly future end prices measured from time of theoretically issuing the forecast**, with no D1 consensus and no model optimization. This supersedes any implication from R40 that May's 17/21 is verified executable three-business-day foresight.

## Governing timing / H3 contract

- Features through **previous forecast-day NY 16:00** (May 2026 = **23:00 Turkish clock**); model governed issue at **forecast issue-date NY 08:00 = Turkish 15:00** (US DST in May). No actual historical `issued_at` logs, so **"available at 15:00" is a governed deadline / necessary feature-availability assumption**, not proven first live signal release.
- Original H3 label: Gold daily source quote on prior feature cutoff `feature_cutoff_date` to price on `target_end_date_h3`, which is **third observed available daily source date AFTER the feature cutoff**. It is only *two subsequent dated references after the issue day*, and original 2026 target source includes SQL daily aggregates instead of exact tradable moment.
- Two independent retrospective source candidates: Neon `gold_research_dukascopy_node_mirror_2026_xau15m_bidask_candidat` (**M15 BID/ASK open midpoint**) and `gold_research_histdata_xau15m_candidate` (**M15 spot/open**); same vendor for start and finish within each independent experiment. Both complete N=21 at compared key timepoints. Feed readings sometimes disagree (e.g. small Friday/May01 moves); none is a validated contemporaneous original bank quote and no historical live publication can be inferred.
- UK May London 10:30 = **12:30TR**; USA May 08:00 New York = **15:00TR**. Thus the original issue-day LBMA-AM-level benchmark **occurs before the governed issue time**. The evaluated legacy terminal is 2 further original available Gold days later, so its London AM time is still in the issue's future. Separate full three future-business-day horizon counts three available source dates FROM the issue, i.e. **one day farther** than original H3 target.

## Reproducible outcome: 2026 MAY H3, 21 original votes, SAME decisions

| Price comparison | DPTC-Q95 accuracy on Dukascopy candidate | DPTC-Q95 on HistData candidate | V5 Dukascopy / HistData | Tradability / attribution |
|---|---:|---:|---:|---|
| **Original historical H3 reference cutoff→target (legacy)** | **17/21 = 80.95%** | **17/21 = 80.95%** | 12/21 (original label) | Original H3 label is not vendor-specific intraday |
| May issue-date **15TR → original H3 end-date 12:30TR** | **11/21 = 52.38%** | **12/21 = 57.14%** | 10/21 ; 9/21 | Post-issue target end in future; no spread |
| **May issue-date 15TR → original H3 end-date 17TR** | **12/21 = 57.14%** | **13/21 = 61.90%** | 9/21 ; 10/21 | **Primary full forward-origin test**; no retail spread |
| May issue-date **17TR → original H3 end-date 17TR** | **13/21 = 61.90%** | **14/21 = 66.67%** | 12/21 ; 9/21 | Entry later, bank spread usually worse |
| Hypothetical May issue-date **09TR → original H3 end-date 17TR** | **13/21 = 61.90%** | **15/21 = 71.43%** | 10/21 ; 10/21 | **NOT causally certified**: original deadline 15TR; only viable if all model PIT features and live signal issuance are proved by 09TR |
| Issue date **15TR → 3 subsequent original daily eligible source dates later, 17TR** | **13/21 = 61.90%** | **11/21 = 52.38%** | 10/21 ; 8/21 | Actually THREE subsequent daily dates from issue, beyond old original H3 terminal |

Baseline on primary strict issue15→original end17: actual **UP 9/21, DOWN 12/21** on Duka; **UP10/21 DOWN11/21** HistData. Simple always-DOWN predicts **12/21** Duka, **11/21** HistData. Therefore DPTC's Duka result **12/21 does not beat DOWN baseline**, while HistData 13/21 modestly exceeds the 11/21 baseline; 21 forecasts is too small for a robust edge.

### Time structure: WHERE the three-day call corresponds to observed post-issue movement

| Current issue-date 15TR to... | Dukascopy 2026 May DPTC | HistData 2026 May DPTC |
|---|---:|---:|
| **Same issue day 17TR** | **11/21 = 52.38%** | **7/21 = 33.33%** |
| **Next original forecast-issue day 09TR** | **8/21 = 38.10%** | **9/21 = 42.86%** |
| **Next original forecast-issue day 17TR** | **10/21 = 47.62%** | **10/21 = 47.62%** |
| **Original H3 target day 17TR** | **12/21 = 57.14%** | **13/21 = 61.90%** |

This is a finite diagnostic clock panel, not a model-trained optimal hour search; never select a clock because it won 21 in-sample comparisons.

## September-vs-May model explanation

May original V5 **12/21**, SAGE+RuleFlow **13/21**, DPTC-Q95 **17/21** due to SAGE +1 and DPTC **4 flip rescues** at **issue May01 (cutoff Apr30), May19 (cutoff May18), May22 (cutoff May21), May28 (cutoff May27)**. These are real correct decisions on the original H3 target definition. Under **strict Duka issue15→end17** three flips remain correct (May19, May22, May28), but May01 turns to WRONG; relative to SAGE baseline the DPTC flips net **+2**, so strict V5 **9/21**, SAGE **10/21**, DPTC **12/21**. HistData strict V5 **10/21**, SAGE **11/21**, DPTC **13/21**, although individual "rescue" days differ due feed.

**Concrete feed-sensitive example:** May01 DPTC DOWN, old H3 source feature cutoff Apr30→end May05 DOWN -> a legacy win. Duka mid-price at actual *scheduled issue* **May01 15TR USD 4578.75**, target **May05 17TR USD 4580.704** => a tiny **UP** -> missed future direction. HistData at same fixed hours **USD 4566.715→4564.135**, slight DOWN => correct; proves date/clock and vendor matter, and forbids an overprecise % claim from one vendor.

## Exact all-21 issue rows, immutable DPTC calls, two vendor outcomes

Legend: ✅ = DPTC vote matched this exact historical label, ❌ = wrong. Columns under Duk and Hist use May issue 15TR→original H3 target-end DATE 17TR.

| Issue May date | Original H3 terminal date | DPTC H3 vote | Legacy H3 | **Duk post-issue future** | **Hist post-issue future** | Flip source |
|---|---|---|---|---|---|---|
| 05-01 | 05-05 | DOWN | ✅ | ❌ | ✅ | DPTC FLIP |
| 05-04 | 05-06 | UP | ✅ | ✅ | ✅ | — |
| 05-05 | 05-07 | DOWN | ❌ | ❌ | ❌ | — |
| 05-06 | 05-08 | UP | ✅ | ✅ | ✅ | — |
| 05-07 | 05-11 | UP | ✅ | ❌ | ❌ | — |
| 05-08 | 05-12 | DOWN | ✅ | ✅ | ✅ | — |
| 05-11 | 05-13 | DOWN | ✅ | ❌ | ❌ | — |
| 05-12 | 05-14 | UP | ❌ | ❌ | ✅ | — |
| 05-13 | 05-15 | UP | ❌ | ❌ | ❌ | — |
| 05-14 | 05-18 | DOWN | ✅ | ✅ | ✅ | — |
| 05-15 | 05-19 | DOWN | ✅ | ✅ | ✅ | — |
| 05-18 | 05-20 | DOWN | ✅ | ✅ | ✅ | — |
| 05-19 | 05-21 | DOWN | ✅ | ✅ | ✅ | DPTC FLIP |
| 05-20 | 05-22 | DOWN | ✅ | ❌ | ❌ | — |
| 05-21 | 05-25 | UP | ✅ | ✅ | ✅ | — |
| 05-22 | 05-26 | DOWN | ✅ | ✅ | ❌ | DPTC FLIP |
| 05-25 | 05-27 | DOWN | ✅ | ✅ | ✅ | — |
| 05-26 | 05-28 | UP | ❌ | ❌ | ❌ | — |
| 05-27 | 05-29 | UP | ✅ | ✅ | ✅ | SAGE FLIP |
| 05-28 | 06-01 | UP | ✅ | ✅ | ✅ | DPTC FLIP |
| 05-29 | 06-02 | UP | ✅ | ❌ | ❌ | — |

Full machine-readable intermediate ledger: `GOLD_R41_MAY_2026_H3_FUTURE_CLOCK_RETEST_ROWS_20261011.csv`; note two independent vendor price columns.

## Scientific verdict / user action sequence

1. **Yes**, DPTC May original *historical three-reference-date* score is **17/21 80.95%**, correct replay of original research.
2. **No**, the same May 21 votes **do not** demonstrate `80.95%` correct direction from **issue timestamp** through the original H3 target date. Under strictly later-origin same-provider quotes primary 15TR→H3 target17TR, performance falls to **12/21 (57.14%) or 13/21 (61.90%)**; if one insists on *three* available Gold reference dates AFTER issuance, performance **13/21 (61.90%) or 11/21 (52.38%)**.
3. Early **09TR→H3 target17TR** can be **13/21 (61.90%) or 15/21 (71.43%)**, but **not certified as a prediction** at 09TR; the actual issue record is absent, and post hoc choosing early clock plus one provider is illegitimate.
4. No conclusion that DPTC cannot predict: these 21 cases and retrospective candidate feed outputs do not decide out-of-sample future value. But historic original May 80.95% **MUST NOT** be represented as validated live three-day bank trading precision.
5. Re-test *actual* logged PIT-issued model outputs with a fixed early 09TR vs late 15TR architecture, same-market BID/ASK/fee alignment, predeclared future-only targets, across 2023–2026. **Do not retrain or optimize on May label results and then call May OOS.**

## Evidence / SQL reproducibility

Neon read-only SQL samples from **source tables** `gold_research_dukascopy_node_mirror_2026_xau15m_bidask_candidat` and `gold_research_histdata_xau15m_candidate`, range `2026-04-27 <= bar_start_utc < 2026-06-10`, grouped by `(bar_start_utc AT TIME ZONE 'Europe/Istanbul')::date`. Extract exact bar `OPEN` for NY `08:00` (May=15:00TR), Turkey `09:00` & `17:00`, London `10:30` (May=12:30TR), and NY `16:00`. No interpolated quotes. Source information is retrospective third-party research data, not tradeable settlement data. Original H3 file `GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv`; exact Q95 flips `GOLD_H3_DPTC_V1_ACTIONS_2026-10-05.csv`; exact SAGE/Ruleflow exceptions `GOLD_H3_SAGE_V2_RULEFLOW_V3_TG_COMBINED_EVENTS_2026-10-04.csv`. Price targets/derived labels are never fed into issued vote construction.
