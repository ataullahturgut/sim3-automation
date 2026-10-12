# R46 — May 2026 original H3 DPTC-Q95: actual chronological controller replay + per-feature source/clock/vintage labels

Date: 2026-10-12. Status: **FROZEN-H3-REPLAY PASS / PIT HISTORICAL ISSUANCE FAIL-UNPROVEN / NOT LIVE 2026**.

## Purpose
Execute the **actual DPTC-Q95 competence-state controller** for 2026 using the recorded 41-row H3 HANDOFF event timeline, frozen 2023–24 SELLR score, 2025-selected 2.3677413378977423 trigger, label-free Gold/NDX/VIX 60-row correlation/phase state and target-matured feedback, with corrected date parsing; then apply those routed reversal actions over all 21 May rows of the preserved SAGE V2+RuleFlow V3-TG H3 baseline built from the V5 direction ledger.

No hourly target relabeling, no session swap, no new H3 model training or 15TR market-price targeting; the 15TR clock appears **only** as a conservative, historically governed *evidence snapshot cutoff* for checking public archived source presence.

## 1. Execution summary
- May original issue dates **21**; V5 **12/21**, SAGE/RuleFlow **13/21**, independently replayed DPTC-Q95 **17/21 = 80.95%** versus same frozen H3 label. Frozen benchmark R42 Q95 **17/21** reproduced exactly.
- DPTC-Q95 2026 full controller replay produces **13 actions**: 11 rescued incorrect baseline decisions and 2 broken correct baseline decisions. Exactly matched original `GOLD_H3_DPTC_V1_ACTIONS_2026-10-05.csv`. **May issue-date flips** = 2026-05-01, 2026-05-19, 2026-05-22, 2026-05-28.
- Date-parser corrected replay uses **true date components** of `target_end_date_h3`; no May vote or 2026 Q95 action changes versus saved original 2026 ledger.
- The 21 source UTC-day-average target signs are frozen pinned Stak `sqld`, confirmed in R42 by two independent M15 vendor UTC-day mean signs. Replaying those signs does not demonstrate historic May issuance.

## 2. Source clock and availability contract
| Feature family | Exact 2026 May time-label | Data availability issue |
|---|---|---|
| XAU, XAG, XPT, XPD Stak `sqld` daily average | `feature_cutoff_date D`: UTC `[D 00:00,D+1 00:00)` = Turkey `[D 03:00,D+1 03:00)`; source JSON synthetic `12:00:00` is date tag only | Values not mathematically complete until **D+1 03TR**, actual source publishing later and historical vintage may be stale or revised |
| Twelve Data prior-day 1H XAU feature | 16:00 New York `feature_cutoff_date` 1H candle OPEN, May clock D 23TR → D+1 00TR | Input feature based on candle close cannot be used until at least **D+1 00TR** plus dissemination lag |
| CME daily GC and GC calls/puts volume | Exact `cme_trade_date` in per-row CSV, strictly less than cutoff D; other engineered CME features history to that trade date | Official next-business-day final volume publication; original downloaded vintage/released-at not recorded |
| Gold/silver, DXY proxy, Treasury-yield proxy, NDX, VIX daily and their cross-market transforms | Per-row `metal_source_date, usd_source_date, yield_source_date, ndx_source_date, vix_source_date`; all derived `<= D` | Raw market observation dates preserved but exact historical provider revisions and publication times not certified |
| CFTC COT state | Per-row `cot_report_date` Tuesday / conservative `cot_available_date`; historical model uses only available vintages | Date-level availability guard present; external firstprint/revision audit needed |
| Historical H3 feedback used in Q95 trust | `target_end_date_h3` of previous eligible H3 target must mature no later than current cutoff | Mixed 2025/2026 parsed datetime bug in original controller fixed for replay; publisher actual target price firstprint still missing |
| Source target evaluated | Source target date T = **third retained daily date from prior D cutoff**, not third following calendar weekday from issue | UTC-day target mean completes **T+1 03TR**; source publishing later; label never inserted into contemporaneous forecast inputs |

For 7 May 2026 issue specifically: D0 **May06**; four Stak daily metal averages cover May06 03TR→May07 03TR; hourly Twelve anchor May06 23TR→May07 00TR; CME trade date May05; cross-market five groups May05; COT report Apr28 with ledger available May05; H3 target May11 daily average covers May11 03TR→May12 03TR. No proof all firstprints and the **October-built DPTC-Q95** existed at May07.

## 3. Critical supplier vintage experiment (historically observed snapshots)
On each May issue date choose the latest matching **observed GitHub `v3` commit** with timestamp no later than **issue date 12:00UTC=15TR** (Git commits not an exhaustive `released_at` log; this is sampled forensic evidence only); load that commit's `data/spot-history-2026.json`; match the source cutoff D Gold/Silver/Platinum/Palladium price to the `54fdf1c8d39b7b6c7b874d0f30f784296e886044` freeze used to develop Q95.

- Four metals absent for 7/21 issue origins in these **sampled historic snapshots**.
- Four metals present but **at least one revised price** versus original retrospective frozen price in 12/21.
- Four metals present and **exactly identical** in only 2/21: 2026-05-11, 2026-05-12.
- This is an unprecedented additional **source-firstprint/revision risk**, separate from observational-clock alignment.
- Example 1 May issue / cutoff Apr30 old-vintage `sqld` Gold **4567.08**, later frozen complete-UTC-day `sqld` Gold **4604.34**; delta -37.26. Example 13 May issue / cutoff May12 observed `sqld` Gold **4763.05**, later frozen **4706.50**, delta +56.55. Example 18 May issue / cutoff May15 vintage **4652.34**, later frozen **4568.19**, delta +84.15.
- Old Git history saw a file with last source-day April30 on May08; files with May06 rows were confirmed after May09 05:41TR and by May10 02:11TR (firstprint exact time within the two bounds unknown). Documentation of upstream STRK-403 states prior partial-day `sqld` averages were frozen before complete-day reaggregation repairs. Not every discrepancy can be attributed uniquely without inspecting exact provider poll SQL run history.

## 4. Row by row, original H3 vote and source availability snapshot
AYNI = all four origin-day metals match later pinned freeze; FARKLI = all present but at least one revision; YOK = missing at sampled commit. Delta USD = archival Git snapshot Gold minus frozen backtest Gold. Date columns here month-day (2026).

| Issue | Cutoff D | H3 target T | Q95 vote | Real | Correct | 15TR Git snapshot four metals | Gold Δ USD |
|---|---|---|---|---|---|---|---|
| 05-01 | 04-30 | 05-05 | DOWN ↺ | DOWN | ✓ | FARKLI | -37.26 |
| 05-04 | 05-01 | 05-06 | UP | UP | ✓ | YOK | — |
| 05-05 | 05-04 | 05-07 | DOWN | UP | ✗ | YOK | — |
| 05-06 | 05-05 | 05-08 | UP | UP | ✓ | YOK | — |
| 05-07 | 05-06 | 05-11 | UP | UP | ✓ | YOK | — |
| 05-08 | 05-07 | 05-12 | DOWN | DOWN | ✓ | YOK | — |
| 05-11 | 05-08 | 05-13 | DOWN | DOWN | ✓ | AYNI | 0 |
| 05-12 | 05-11 | 05-14 | UP | DOWN | ✗ | AYNI | 0 |
| 05-13 | 05-12 | 05-15 | UP | DOWN | ✗ | FARKLI | 56.55 |
| 05-14 | 05-13 | 05-18 | DOWN | DOWN | ✓ | FARKLI | 17.21 |
| 05-15 | 05-14 | 05-19 | DOWN | DOWN | ✓ | FARKLI | 8.36 |
| 05-18 | 05-15 | 05-20 | DOWN | DOWN | ✓ | FARKLI | 84.15 |
| 05-19 | 05-18 | 05-21 | DOWN ↺ | DOWN | ✓ | FARKLI | -24.2 |
| 05-20 | 05-19 | 05-22 | DOWN | DOWN | ✓ | FARKLI | 38.35 |
| 05-21 | 05-20 | 05-25 | UP | UP | ✓ | YOK | — |
| 05-22 | 05-21 | 05-26 | DOWN ↺ | DOWN | ✓ | FARKLI | -1.64 |
| 05-25 | 05-22 | 05-27 | DOWN | DOWN | ✓ | FARKLI | 14.69 |
| 05-26 | 05-25 | 05-28 | UP | DOWN | ✗ | FARKLI | -2 |
| 05-27 | 05-26 | 05-29 | UP | UP | ✓ | FARKLI | 21.25 |
| 05-28 | 05-27 | 06-01 | UP ↺ | UP | ✓ | FARKLI | 11.73 |
| 05-29 | 05-28 | 06-02 | UP | UP | ✓ | YOK | — |

**Complete machine-readable 21-row source ledger:** `GOLD_R46_20261012_MAY_H3_Q95_SOURCE_CLOCK_VINTAGE_AND_FROZEN_REPLAY_21.csv` includes all four metal prices and windows, exact hourly bar-open/bar-close TR, five exogenous series source dates, CME trade date, COT report and ledger availability, Git commit SHA/time and completeness/revision status, phase/SELLR score, V5/SAGE/Q95 directions, original target prices and correctness.

## 5. Why a true May-2026 as-of model success number cannot honestly be given from these sources
Q95 frozen ledger was developed only in October 2026. Historical 15TR Git repo snapshots on multiple May issues have **missing or materially changed** metal inputs, and earlier H3/SELLR experts were learned or reconstructed using later source revisions. To create a causal historical replay would require complete stable point-in-time archives (or identically replicable contemporaneous raw poll records) for **all historical training and May forecast origins**, plus issuer time stamped outputs, each macro/weekly publication/revision clock, and true target-maturity publication. This May exercise does NOT refit all structural hourly daily experts from the changed historical vintages. Hence 17/21 is **correct retrospective frozen-data replay**, but there is **NO justified numeric PIT May accuracy estimate**. Do not divide a selected 2/21 matched origin set into an apparent performance statistic.

## 6. Scientific conclusion
Original H3 D0→D3 source-date horizon remains unchanged. The user's heterogeneous source windows are aligned to the preceding cutoff in the archive, and May input observation end is typically no later than issue day 03TR. But release vintage and posthoc DPTC design mean "could observe at D+1 03TR" != "could execute the published model then". Do not hide this hard firstprint caveat by switching to 15TR entry/exit labels or claiming an invented normalization gain.

R45: `GOLD_R45_20261012_H3_DPTC_Q95_SOURCE_ASOF_CLOCK_AND_ARCHIVE_VINTAGE_FORENSIC.md`; R42 native target: `GOLD_R42_20261012_ORIGINAL_H3_SOURCE_TIME_MAY_UTC_AVERAGE_RECONSTRUCTION.csv`; frozen controller code: `tools/gold_h3_dptc_v1.py`; source vendor public archive `lbruton/StakTrakr@54fdf1c8...` and dated historic commits listed in the row CSV.
