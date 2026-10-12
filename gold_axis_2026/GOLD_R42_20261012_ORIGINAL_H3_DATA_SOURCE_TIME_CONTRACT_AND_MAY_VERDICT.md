# R42 — 2026 May original H3 exact source-clock forensic FIRST, then same-semantic accuracy

**Audit 2026-10-12. BINDING CORRECTION of R41's early decision to prioritize arbitrary clock-to-clock spot prices over the original H3 data contract.** User directive: determine original quote provider and what its daily observation represents in Turkey time BEFORE any May three-day model rescore; original source may be 15TR or daily mean, so do not assume it.

## 1. Four layers that MUST remain separate

**Original Gold target and past daily price features**: `gold_axis_2026/tools/gold_short_horizon_global_xau_readiness_r2.py` `load_public_metals()` obtains `lbruton/StakTrakr/data/spot-history-{YEAR}.json` at pinned `FROZEN_STAK_REF=54fdf1c8d39b7b6c7b874d0f30f784296e886044`, reads `spot`, calls `ts.normalize()` at its timestamp, and creates `target_r3 = log(gold.shift(-3)/gold)`. **No minute/hour field is retained for the Gold target.**

**Exact 2026 May rows**: fetched `lbruton/StakTrakr/data/spot-history-2026.json` at **original H3 pin above**, checked all dates used by the 21 May forecast issue rows: ALL 21 starting `feature_cutoff_date` and original H3 target dates have **`"source":"sqld"`**. A May 01 source row literally `{"spot":4609.87,"metal":"Gold","source":"sqld","timestamp":"2026-05-01 12:00:00"}`, and source seed preserves calendar-date-only reference. Stak `12:00:00` is **not a price actually observed at 12UTC/15TR**.

**Original source producer (upstream direct code evidence, not inferred by price match)**:
- `lbruton/StakTrakr/devops/pollers/shared/spot-year-history.js` at above ref, `DAILY_AVERAGE_SQL`:
  `SELECT metal, DATE(timestamp_floor) AS day, ROUND(AVG(spot),2) AS spot FROM spot_prices WHERE timestamp_floor >= ? AND timestamp_floor < ? GROUP BY metal,day` (actual code uses CASE <1 for 4dp).
- `lbruton/StakTrakr/.agents/skills/update-spot-bundle/update-spot-bundle.py`, direct `AVG(spot)` over COMPLETE UTC days excluding in-progress UTC day, `"source":"sqld"`, synthesized `timestamp=f"{day} 12:00:00"`.
- Before STRK-403, some partial-day averages were prematurely frozen; original 2026 later pin uses updated complete UTC daily data. Individual `spot_prices` samples may not be evenly time spaced: **sample arithmetic mean ≠ exact time-weighted spot average**. It is not bid/ask tradable execution price.

**Original hourly INPUTS** (separate provider): `gold_axis_2026/tools/gold_h3_iris_v1.py` `XAU/USD` from **Twelve Data 1-hour** with `timezone=America/New_York`, admissible bars through `16:00 America/New_York` on prior feature date. In **May 2026** this is **23:00 Europe/Istanbul prior day**. The H3 `forecast_issue_date` is the NEXT weekday Stak observation date (calendar label). A separately governed deadline is **08:00 New York=15TR on issue date in May**, but does NOT imply actual historic archived `issued_at=15TR`, nor that model first becomes available at 15TR. All PIT supporting features need release check for earlier issuance.

## 2. Exact Istanbul-local time semantics for a 2026 May `sqld` GOLD observation

`2026-05-01 12:00:00` **stored tag** = merely the UTC date *May 1*. Its numeric value `4609.87` aggregates spot polls with DB `timestamp_floor` in half-open UTC window:

`[2026-05-01 00:00 UTC, 2026-05-02 00:00 UTC)`

which is **[May 01 03:00TR, May 02 03:00TR)**. The complete day's average CANNOT be known from its data before May 02 03:00TR, even though a synthetic tag says 12UTC. **May 01 15TR is inside this window, but not the value's fixing/trade clock.** A Friday may include fewer actual quotes due market close; the calendar interval is still full UTC day and only actual `spot_prices` observations are averaged.

May 1 original H3 call:

| Element | H3 historical source-date | Istanbul interval | Frozen Stak sqld mean |
|---|---|---|---:|
| **Origin** (`feature_cutoff_date`) | **2026-04-30** | Apr 30 03TR → May 01 03TR | **$4,604.34** |
| **Issue date** (`forecast_issue_date`) | **2026-05-01** | forecast date *not a particular spot quote time* | NA |
| **Target** (`target_end_date_h3`) | **2026-05-05** | May 05 03TR → May 06 03TR | **$4,553.59** |

Frozen DPTC-Q95 predicted **DOWN**; end daily mean minus origin daily mean = **−$50.75**, log return ≈ **−1.108%**; original target is correct. The original model's `H3` is a shift of **three retained available Gold DATE records from the cutoff (Apr30 -> May01 -> May04 -> May05)**, NOT the mean price across the next three days and NOT exact issue-time 15TR → 3rd subsequent day's 15TR. An issue on May01 has two **additional** available daily reference dates before May05 terminal.

## 3. Independent SAME-SEMANTICS direct replay: May 2026 21 original forecast rows

The previous R41 wrongly made independently chosen 15TR spot→17TR spot the primary comparator. **First compare apples-to-apples original UTC-day average→UTC-day average**; this is what the user requested.

Frozen May 2026 **21** `GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv` + exact `GOLD_H3_SAGE_V2_RULEFLOW_V3_TG_COMBINED_EVENTS_2026-10-04.csv` + `GOLD_H3_DPTC_V1_ACTIONS_2026-10-05.csv` Q95 directions (same original source labels). Q95 action keyed by feature cutoff date (not issue date).

Neon independent 15-minute candidate quotes: `gold_research_dukascopy_node_mirror_2026_xau15m_bidask_candidat` MID of bid/ask at M15 bar OPEN; `gold_research_histdata_xau15m_candidate` M15 spot OPEN; calculate `AVG(price)` over SQL UTC `date(bar_start_utc)` WITHOUT forcing equal 24h trading observation coverage; both independent of frozen Stak target.

| SAME fixed 21 H3 directions measured | Correct 2026 May | Truth contract |
|---|---:|---|
| **Original pinned Stak `sqld`: origin UTC daily AVG -> H3 end UTC daily AVG** | **17/21 = 80.95%** | EXACT original `target_r3` |
| **Dukascopy-like M15 midpoint UTC-day AVG -> UTC-day AVG** | **17/21 = 80.95%** | 21/21 independently reproduced UP/DOWN target labels |
| **HistData M15 spot UTC-day AVG -> UTC-day AVG** | **17/21 = 80.95%** | 21/21 independently reproduced UP/DOWN target labels |

Compared on **24 unique available** feature+target source dates, mean absolute Stak-vs-Duka 15m daily-mean level gap **$0.962** (median $0.842, maximum $3.438), while Stak-vs-HistData gap **$2.573** (median $2.259, max $7.211). Distinct sampled vendors are not expected to have identical numeric averages but **for all 21 H3 return signs they match the original reference**. Original four DPTC rescue flips are also unchanged.

EXAMPLE direct same-definition:
- original Apr30 source daily mean **$4,604.34** vs May05 **$4,553.59** ⇒ DOWN = correct.
- Dukascopy M15 daily mean Apr30 **$4,603.911**, May05 **$4,554.240** ⇒ DOWN.
- HistData M15 daily mean Apr30 **$4,600.208**, May05 **$4,551.155** ⇒ DOWN.
- May01 `sqld` daily mean itself **$4,609.87** corresponds to **May01 03TR→May02 03TR**; independent Dukascopy M15 same UTC interval **$4,608.981**; **this level proximity confirms time averaging meaning empirically**.

This is real independent repetition of historic source-semantic accuracy, NOT independent out-of-sample model design validation. Q95 was developed after 2026 errors were examined.

## 4. Distinct question: what if investor needs a SIGNAL at a KNOWN hour?

This is a NEW target, not what original `target_r3` meant. Show it separately, never replace original H3 result:

| Start price → original H3 target UTC-day mean | Dukascopy DPTC-Q95 | HistData DPTC-Q95 |
|---|---:|---:|
| Issue-day **03:00TR** spot (note possible data source release lag) → original terminal day's UTC mean | **14/21 = 66.67%** | **14/21 = 66.67%** |
| Issue-day **09:00TR** spot → original terminal day's UTC mean | **12/21 = 57.14%** | **14/21 = 66.67%** |
| Issue-day **15:00TR** spot → original terminal day's UTC mean | **12/21 = 57.14%** | **11/21 = 52.38%** |
| Issue-day **17:00TR** spot → original terminal day's UTC mean | **13/21 = 61.90%** | **14/21 = 66.67%** |

The 03:00TR observed spot quote is not necessarily a quote when the model can issue: the original past UTC-day mean is only complete at 03TR (and may become usable later depending on vendor/publisher availability), and full PIT features have not been reverified. 09TR likewise hypothetical until release trace, despite being after the hourly prior-day 23TR cutoff. The 15TR deadline is governed (not a guaranteed historic first issuance). Never cherry pick a winning hour or vendor on these 21 samples.

**`issue-day UTC-day AVG → H3 target UTC-day AVG` is not a causal 09/15TR forecast**: the issue-day mean itself includes later hours through next-day 03TR. If needed descriptive only (Duka 12/21 and Hist 11/21), DO NOT present as feasible trade at issue.

## 5. New governance conclusion

- The user was right about the **necessity to FIRST identify native original quote provenance and clock**; May 2026 H3 Gold target uses sqld arithmetic `AVG(spot)` across 00:00→24:00UTC, **03:00TR→03:00TR**; not 15TR single quote. In contrast, 2023-25 early Stak seed Gold was LBMA-AM fix, **12:30TR British summer / 13:30TR British winter auction START**, so historical source semantics differ by year and cannot be conflated.
- Previous source-semantic memo `GOLD_DAILY_REALIZATION_SOURCE_AUDIT_2026-10-06.md` correctly warned synthetic Stak noon is not a real observation and similarity to an hourly mean is not proof **by itself**. R42 goes further because it checks the **exact originating Stak upstream `sqld` averaging SQL and raw May rows**; hence for May2026 the daily mean is now **source-code established**, not just inference by resemblance. Do not amend this fact backwards to LBMA seed years or unverified non-sqld dates.
- R41 remains an arbitrary clock-based **supplementary, non-equivalent, post-issue investor evaluation**, not the definition or refutation of the original H3 **17/21** correctness. Where R41 called 15TR→17TR its primary baseline, this is replaced by the same-semantic audit as primary evidence.
- Keep separate **reference-label accuracy**, **actual issued_at**, **timestamped current entry spot vs source target mean**, **cash trading spread / slippage**, **posthoc DPTC selection**. Do not merge them into one percentage.

## Exact reproducibility and evidence

1. `lbruton/StakTrakr` commit `54fdf1c8d39b7b6c7b874d0f30f784296e886044`:
   - `data/spot-history-2026.json` May row `source:sqld`;
   - `devops/pollers/shared/spot-year-history.js` SQL `DATE(timestamp_floor)`, `AVG(spot)`;
   - `.agents/skills/update-spot-bundle/update-spot-bundle.py`, complete UTC-day query and `12:00:00` date label.
2. Original model `gold_axis_2026/tools/gold_short_horizon_global_xau_readiness_r2.py`: `shift(-3)`, `target_r3 = log(...)`, cutoff and issue columns.
3. H3 hourly feature source `gold_axis_2026/tools/gold_h3_iris_v1.py`, and `GOLD_H3_IRIS_V1_AUTHORITY_2026-10-02.md`.
4. Frozen H3 votes and DPTC actions: `GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv`, `GOLD_H3_SAGE_V2_RULEFLOW_V3_TG_COMBINED_EVENTS_2026-10-04.csv`, `GOLD_H3_DPTC_V1_ACTIONS_2026-10-05.csv`.
5. Independent retrospective Neon source panels `gold_research_dukascopy_node_mirror_2026_xau15m_bidask_candidat`, `gold_research_histdata_xau15m_candidate`, grouped by `(bar_start_utc AT TIME ZONE 'UTC')::date`; no bar/average invented.
6. 21-day machine-readable primary proof: **`GOLD_R42_20261012_ORIGINAL_H3_SOURCE_TIME_MAY_UTC_AVERAGE_RECONSTRUCTION.csv`**.
