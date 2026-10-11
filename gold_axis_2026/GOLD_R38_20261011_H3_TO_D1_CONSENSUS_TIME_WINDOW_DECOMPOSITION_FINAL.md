# R38 — THE ACTUAL CIG-D1 PROBLEM: H3 expert vote reused as D1; old %80's directional match is largely PRE-CUTOFF movement

**2026-10-11 — definitive direct test of the user's specific question, no model refit, no changes to exact frozen forecasts.** This takes precedence over any R37 implication that old CIG was a newly trained one-day prediction or that one can explain the 74.4% by assigning a single Turkey calendar clock. The user accurately identified that D1 was built from EXISTING THREE-BUSINESS-DAY H3 experts **by a unanimity gate**.

## 1. The actual operator in the original project (not retrospective invention)

`GOLD_D1_CIG_V1_RESULT_2026-10-05.md` says daily CIG does not refit or relabel the original H3 predictors: SAGE V2+RuleFlow V3-TG, HELIOS V5-DCE, RIFT, VEGA unanimous same H3 direction => D1 daily directional decision; else UNCERTAIN. The D1 outcome was scored as today's StakTrakr daily ref (old legacy LBMA AM at 2023-25) versus previous trading day's LBMA AM; **this is an arbitrary SAME-DAY validation overlay on H3 direction**, not an independent one-day-trained model.

Original R2 readiness `gold_axis_2026/tools/gold_short_horizon_global_xau_readiness_r2.py` defines `feature_cutoff_date` as previous daily observation date, `forecast_issue_date` as next available Gold date and H3 target price at **3 historical dated Gold indices forward from the feature cutoff date**. Model's hourly IRIS features are allowed through **16:00 New York** on the previous date (TR 23:00 US DST / TR 00:00 following calendar date US winter). The governed issue deadline is **08:00 New York** (TR15/16) on issue date. No historic actual signal timestamp is recorded.

## 2. 2025 SAME exact 218 consensus: every Türkiye hour, prior source date -> issue date

Downloaded unchanged `GOLD_OLD_CIG_2025_EXECUTION_TARGET_ROWS_2026-10-07.csv` 218 predicted directions and the matching EVTradingLabs Dukascopy-derived independently archived `gold_research_evduka_xau15m_bidask_candidate`, BID/ASK M15 source converted to midpoint OPEN at exact top of each TRT hour. Each label at hour H compares **previous feature cutoff DATE at H** versus **issue DATE at H**, weekends/holidays spanning to next eligible date. Model predictions were not altered; price series stays on same new vendor for both endpoints. This is a source-time MATCH DIAGNOSTIC, not a prospective issue-time claim.

| Fixed Turkish hour, compare prior SOURCE date at H to issue date at H | N | Frozen CIG correct |
|---|---:|---:|
| **02:00** | 218 | **174/218=79.82%** |
| 03:00 | 218 | 172/218=78.90% |
| 06:00 | 218 | 174/218=79.82% |
| 09:00 | 218 | 171/218=78.44% |
| 10:00 | 218 | 175/218=80.28% |
| **13:00** | 218 | **175/218=80.28%** |
| 14:00 | 218 | 169/218=77.52% |
| 15:00 | 218 | 164/218=75.23% |
| 16:00 | 218 | 158/218=72.48% |
| 17:00 | 218 | 147/218=67.43% |
| 18:00 | 218 | 139/218=63.76% |
| 19:00 | 218 | 133/218=61.01% |
| 20:00 | 216 | 123/216=56.94% |
| 23:00 | 207 | 113/207=54.59% |

**Aha:** No single special 02:00 hour was encoded in the old H3 forecast. The high ~80% applies to MANY previous-day-to-issue-day historical close-to-close-like windows from 02TR to 13TR; it drops across 15–23TR. The issue-date signal matches a previous-day TREND state. One should not pick 10:00 or 13:00 as a post-hoc champion simply because it reaches 80.28%.

For the **same issue-D → next eligible issue-day TR hour** instead of previous→issue, 2025 accuracy h02 **125/218=57.34%**, h09 **121/218=55.50%**, h13 **117/218=53.67%**, h16 **116/218=53.21%**, h17 **108/218=49.54%**, h23 **106/206=51.46%** (coverage varies at late hours). Thus the ~80% applies to previous/issue historical interval, not an arbitrary forward interval.

## 3. The key scientific test: split a SAME-date high-scoring window at the actual FEATURE cutoff

Use one fixed predeclared window with **exact same common dates and 212 of 218 frozen 2025 calls**:
- **A = prior source date at Türkiye 13:00** (historical market M15 midpoint),
- **B = that prior source date at New York 16:00** (historical model feature cutoff),
- **C = issue date at Türkiye 13:00**.

**2025**:

| Evaluated segment | Frozen call success | Always-UP on same rows | At scheduled 08NY issue |
|---|---:|---:|---|
| **A→C: prior 13TR -> issue 13TR** | **170/212 = 80.19%** | 120/212 = 56.60% | period ENDS BEFORE 08NY issue |
| **A→B: prior 13TR -> prior 16NY cutoff** | **182/212 = 85.85%** | 120/212 = 56.60% | **Already COMPLETED at feature cutoff** |
| **B→C: prior 16NY cutoff -> issue 13TR** | **108/212 = 50.94%** | **124/212 = 58.49%** | starts at feature cutoff, still ENDS BEFORE issue |
 
**This diagnoses the 80%**: vote direction agrees *even more* with the portion of the price movement **already observable when the final hourly model inputs close**, while no measurable edge survives in the **subsequent** B→C interval. The result does **not** allege data leakage (prior-to-cutoff features legitimately include previously observed moves). It means the D1 overlay selected a target dominated by **pre-cutoff realized momentum**.

### 2026 Jan–Jul independent historical source check (same old 125, common N=118)

Frozen CIG `GOLD_CIG_EXACT_125_ROWS_2026-10-06.csv`, original prior-date ledger `GOLD_DAILY_H1_V2_2026_GERCEKLESEN_TAHMIN_RECOVERED_2026-10-06.csv`, independent source for exact quote instants `gold_research_dukascopy_node_mirror_2026_xau15m_bidask_candidat` (Dukascopy-derived M1→M15); missing bars explicit, Jan2 prior source unavailable, Apr3 closed market excluded. On same 118 common available days:
- **A→C**: **86/118 = 72.88%**.
- **A→B, already observed before model cutoff**: **103/118 = 87.29%**.
- **B→C, after model feature cutoff**: **55/118 = 46.61%** versus always-UP **63/118 = 53.39%**.
- Original mixed price source D1 label on these 118: **88/118 = 74.58%**.

The 2026 M15 candidate is a retrospective third-party Dukascopy mirror, not a validated contemporaneous first-print. Excluded 7 of 125; 2026 period already studied, not fresh test. Nonetheless the 2026 split **replicates** the structural pre/post-feature-cutoff pattern independently of the original 2025 quote source, **without choosing a performance-optimal clock**.

## 4. The TRUE original H3 horizon and the D1 label are NOT the same

Same 218 frozen 2025 signals compared on the **original** StakTrakr Gold `seed/LBMA` price data (as originally pinned at `54fdf1c8...`), base price at prior `feature_cutoff_date`, target date plus H historical available reference indices:
- H1 from cutoff to issue: **176/218=80.73%** (old D1 overlay; price interval includes pre-final-feature time).
- H2 cutoff→2nd ref: **161/218=73.85%**.
- H3 cutoff→3rd ref: **149/218=68.35%** (original H3 expert forecast horizon; always-UP **129/218=59.17%**, but target still begins before last model feature cutoff).
- H4 **142/218=65.14%**.
- H5 **138/218=63.30%**.

This explicitly answers user's observation: **the old D1 was simply unanimous 3-day H3 state re-used to score the first dated benchmark change**, NOT a model calibrated to a unique one-day 02:00-to-02:00 future interval.

### Strictly after original governed issue, original H3 TARGET END

At the same **2025 original 218 signals**: new price START **08:00 New York issue-date (HistData/EV Duka independent quote)** and price END original H3 index `feature_cutoff_date+3 available Stak LBMA Gold dates`. Causally honest retrospective window **from issue onward** (though no actual archived issue log):
- H3 end: **120/218 = 55.05%**, always-UP **124/218 = 56.88%**.
- H2 end **117/218 = 53.67%**, always-UP 115/218.
- H4 end **111/218 = 50.92%**, always-UP 129/218.
- H5 end **113/218 = 51.83%**, always-UP 139/218.
- H1 end is the *past earlier-same-day AM benchmark*, so **103/218=47.25%** from 08NY spot is a **post-issue-to-retrospective-past endpoint**, **NOT** a causal forecast return; report only as a clock-order warning.

Consequently it would be incorrect to take the **68.35% H3 target starting at earlier LBMA AM** as proof of a truly forward-issued 3-day 68% strategy.

## 5. What the UP vote *actually* represented, and what is / is not proven

When H3 experts give UP for forecast issue-day D, they are voting the continuation/regime learned from price states available through prior date's **New York 16:00** source cutoff. Frozen D1 simply asks if all experts agree, and previously counted the **prior LBMA AM→same-day LBMA AM** direction. The vote has a pronounced **retrospective contemporaneous trend description**, not a verified prediction that tomorrow/this afternoon from issue-time will be UP.

The user was **correct** that same-day label direction strongly corresponds to specific clocked market time windows: **02, 03, 09, 10, 13 Turkey** prior-source-date→issue-date all score around 78–80%; but there is not one privileged hidden clock, and those clocked return windows **start before the last model feature cutoff**. Comparing ONLY at the original provider AM benchmark (~12:30TR BST /13:30TR GMT) was not enough to see this decomposition; this report fixes that.

**Final policy conclusion**: Preserve H3 expert architecture as a trend/regime state estimator. Remove original 2025 80.73% and 2026 74.40% from any claim of causally executable D1 or 3-day foresight. Historic signal timestamps absent, so do not claim every historic issue happened exactly at 08NY (governance deadline). To build a TRUE prediction, freeze an actual issuer timestamp after complete PIT input availability, choose one future-only end clock without optimizing over open years, evaluate exact same-source BID/ASK origin and end. Do not silently reuse H3 horizon sign as new one-day model.
