# R65 — H3 forecast versus Turkish bank decision clocks: select 09:00, 15:00, 16:45

**12 Oct 2026 | Completed empirical clock-selection and H3 directional rebase test | Research authority, not bank execution forecast.**
**Source chain:** R60 all-weekday release/PIT calendar → R61 chronological OPAL refit → R62 dynamic HELIOS → R63 dynamic DPTC-Q95; independently timestamped spot/reference price candidates in connected Neon. The exercise fixes *execution timing before further H3 calibration*, without retrying the same source-date audit.

## 1. Primary decision: the required clocks are three, not arbitrary hourly forecasts

| clock TR (IANA Europe/Istanbul) | operating purpose | required target | action |
|---|---|---|---|
| **09:00** | primary morning entry / sell / hold decision | **DAY 09→16:45**, **H3 morning-origin → remaining H3 price distribution**, longer-horizon holding risk | PRIMARY |
| **15:00** | intraday update before / around US open-data repricing; identify H3 origin→entry drift and remaining move | **15→16:45** plus a recalculated **H3 15→its economic expiry**; not a fresh use of unavailable future macro releases | CONDITIONAL CHECKPOINT |
| **16:45** | last realistically pre-bank-spread widening decision | **OVN 16:45→next eligible09**, H3 carry-through / gap-jump risk | PRIMARY |
| 16:30 | preclose optional early decision if the user's actual bank spreads widen before 16:45 | same risk identity with 16:30-origin | FALLBACK |
| 17:00 | bank spread boundary / research mark-to-market only | avoid assuming executable buy/sell at this hour | BENCHMARK |
| 12:00 | prespecified diagnostic clock only | not promoted merely because hindsight gives a higher accuracy | CONTROL |

**No universal "best accuracy clock" was selected from 2026.** The two operational decisions 09 and 16:45 plus a contingent 15 review come from user's 09–17 bank availability and material overnight volatility. The test price source is spot XAU quote, not a bank executable ASK/BID. Do not infer that a signal available at 15 is historically available at 09.

### As-of constraints
- All hour labels are local TR with explicit IANA conversion, **not** 08:00 New York hardcoded to 15TR all year.
- US BLS standard 08:30 New York announcements map to **15:30 TRT during EDT**, **16:30 TRT during EST**, i.e. just before close in winter (CPI/NFP examples). Release content may only enter a 16:45 forecast if actually published and ingested before 16:45. Source: https://www.bls.gov/schedule/news_release/cpi.htm
- WGC shows why market session origin and bank origin are not identical, with its 2026 market session regions Asia 18:00–03:00 NY, Europe 03:00–08:00 NY, US 08:00–17:00 NY: https://www.gold.org/goldhub/research/gold-mid-year-outlook-2026
- At 09TR use **completed prior-hour/quarter-hour bars only**: bar opened 08:45 and completed 09:00 is the most recent admissible (assuming feed publication latency). At 16:45, bar opened 16:30 and completed 16:45 is last admissible; a bar stamped 16:45 cannot be used in its own 16:45 opening decision.
- COT available after a Friday NY 15:30 release cannot be used retroactively for Friday morning or 16:45TR. CFTC holiday schedules from R60 govern Monday and other special first availability.
- The original archived H3 `issued_at` and complete publisher-firstprint status are NOT proven. These times are newly defined future execution origins, **not** claims that R63 historical votes were issued then.

## 2. Why 16:45 overnight decision is necessary — ACTUAL READ-ONLY Neon SQL

Vetted upstream for time window evaluation:
- 2023–25 `gold_research_evduka_xau15m_bidask_candidate`, Dukascopy-derived same-source midpoint `(bid_open+ask_open)/2`, years split;
- 2026 `gold_research_dukascopy_2026_direct_m1_m15_bidask_v2` `m1_matched=15`; source coverage only complete observed dates, not all 2026 sessions.

Midpoint **M15 open** at exact 09:00/16:45/17:00TR; night comparator **16:45 today → next calendar-day 09:00** on dates where both quotes exist (Friday→Monday weekend excluded). No actual bank spread/PnL. These different day and overnight Ns are **not a fully paired same-date statistical superiority test**.

| Year/source | 09→16:45 Day N | Day mean absolute change | 16:45→next09 overnight N | Overnight mean absolute change | 90th percentile night abs |
|---|---:|---:|---:|---:|---:|
| 2023 historical | 257 | 0.3466% | 205 | 0.4328% | 0.9272% |
| 2024 historical | 259 | 0.4056% | 205 | 0.4542% | 1.0010% |
| 2025 historical | 258 | 0.4842% | 205 | 0.6541% | 1.3891% |
| 2026 direct observed | 179 | **0.6625%** | 133 | **1.0598%** | **2.6799%** |

On overlap-eligible dates the nightly absolute change exceeds the preceding 09→16:45 move on **54.15%, 50.24%, 62.93%, 56.39%** of observed 2023–26 days respectively. This is enough to **reject the notion of safely ignoring 16:45→09 risk**, not enough to predict its direction. Friday weekend exposure is a separate risk target; it is intentionally absent from ordinary one-night metric.

## 3. Actually rescored old H3 vs R63 at SIX bank reference clocks (not only proposed ones)

Connected Neon READ-ONLY same-vendor HistData XAU M15 `open_price`, source id `HISTDATA_XAUUSD_M1_FIXED_EST_TO_M15_CANDIDATE_2025_2026`, forecast issue 2026 May–September, original frozen H3 target dates from R63, strict common cohort with >=70 issue/target local M15 bars, >=80 UTC-date target bars, all six 09/12/15/16:30/16:45/17 prices present. **N=102 IDENTICAL matched source/issue dates for all six hours**, no opportunistic coverage-change.

Old column = frozen original Q95 H3 UP/DOWN bit; new column = R63 controlled release-corrected Q95 UP/DOWN bit. For each entry exact quote `P(t)`, target either **the original D3's UTC calendar-day mean** or the **same price source's D3 t-hour quote**. The original target is neither bank target, and **there is NO new fit on these labels yet**.

| TR origin | old H3 bit correct vs D3 daily mean | R63 H3 bit correct vs D3 daily mean | R63 H3 bit correct vs D3 SAME CLOCK |
|---|---:|---:|---:|
| 09:00 | **60/102 (58.82%)** | **58/102 (56.86%)** | **54/102 (52.94%)** |
| 12:00 | 60/102 | 60/102 | 60/102 |
| 15:00 | 58/102 | **56/102 (54.90%)** | **55/102 (53.92%)** |
| 16:30 | 56/102 | 58/102 | 61/102 |
| 16:45 | 54/102 | **56/102 (54.90%)** | **58/102 (56.86%)** |
| 17:00 | 56/102 | 58/102 | 58/102 |

When the `native H3 y` is replaced with D3 daily-mean versus entry quote at same 102 dates, target signs change on **14/102 at 09**, **20/102 at 15**, and **24/102 at 16:45**. **THIS is why 130/191=68.06% old-mean H3 DPTC score is not a bank-clock 68.06% execution accuracy.**

Do NOT treat the seeming 16:30 superiority or 12:00 results as a winner: clocks were compared on already-observed May–September and no identical fresh target-specific retrain exists. Distinguish native D3 average and same-time D3 quote in result tables, never blend the denominators. Full source/prices/labels: `GOLD_R65_20261012_H3_BANK_ANCHOR_REBASE_MAY_SEP_102_MATCHED.csv`; summary: `GOLD_R65_20261012_H3_BANK_ANCHOR_REBASE_MAY_SEP_SUMMARY.json`.

## 4. Initial numerical magnitude bridge ALSO tested — not promoted

A simple directional-conditioned expected native H3 return pilot used only DEV 2023–24 frozen/replayed HELIOS calls and homogeneous reconstructed HistData D0/D3 UTC daily-average prices with >=70 M15 bars each. **Training N=356 (2023 only 116 price-complete issues; 2024 240)**; fit the two conditional mean returns by HELIOS predicted UP vs DOWN, obtaining **+0.7232%** and **−0.2849%** conditional expected native H3 change. No 2025/26 outcome used to choose those means.

At each actual issue quote `P_entry`, source D0 price `P0`, and target D3 average, test `sign( E[log(P_D3/P0) | H3 vote] − log(P_entry/P0) )`. This is a **real numerical origin-rebase** rather than reinterpreting UP/DOWN without magnitude. For 2026 the R63 Q95 UP/DOWN bit provides the direction selector; 2025 uses new HELIOS because full H3 DPTC 2025 is not constructed here.

| Held-out-experiment period | origin | N | unchanged H3 direction correct | simple expected-move rebase correct | naive class benchmark |
|---|---|---:|---:|---:|---:|
| 2025 HELIOS test | 09:00 | 246 | 122 | 126 | always UP 143 |
| 2025 HELIOS test | 15:00 | 246 | 117 | 118 | always UP 140 |
| 2025 HELIOS test | 16:45 | 246 | 122 | 122 | always UP 145 |
| 2026 Q95 retrospective | 09:00 | 186 | **105** | **89** | always DOWN 100 |
| 2026 Q95 retrospective | 15:00 | 186 | **105** | **99** | always DOWN 98 |
| 2026 Q95 retrospective | 16:45 | 186 | **104** | **97** | always DOWN 97 |

**RESULT: FAIL for promotion.** 2025 and 2026 use distinct final directional stages; the two periods are not a pooled paired Q95 validation. Provider firstprint is not certified, DEV 2023 coverage only 116/219, and 2026 Q95 scores were fitted retrospectively in October. Despite these limits, this properly evaluated, extremely low-capacity numerical bridge **does not establish reliable transport; it often reduces correctness**. Do not implement a naive H3-magnitude flip as a bank order rule.

## 5. The correct next model to build (WITHOUT redoing old source-clock audits)

**A. Freeze source-available decision origins.**
For each bank-eligible day 09, 15 and 16:45TR, record `decision_at_utc`, `entry_ask`, `exit_bid` (if actually available), signed native H3 original D0-to-D3 price, as-of H3 prediction and **all** source/feature ingestion timestamps. If true bank ASK/BID absent, label output `spot-proxy/no-PnL`.

**B. Train separate, newly named execution targets**, keep frozen original H3 as *expert prior/state*, never copy its original label as bank-time truth:
- `DAY_0900_TO_1645`: 09 entry→16:45 exit **same date**, if both source and bank market actually executable.
- `OVN_1645_TO_NEXT0900`: 16:45 hold→next eligible09; Friday weekend hold separate `WEEKEND_HOLD`, don't presume a Monday is next civil day.
- `H3_0900_TO_D3_0900`, `H3_1500_TO_D3_1500`, `H3_1645_TO_D3_1645` for the **third designated trading-observation target day** (date calendar must be governed separately; source D3 is not automatically a +72h trade).
- Optional `H3_RESIDUAL_TO_D3_UTC_MEAN` numeric bridge for old H3 research, but do not confuse daily-average target with bank-executable exits.

**C. Calibrate residual price distribution using DEVELOPMENT 2023–24** and time-origin safe inputs. Instead of old sign plus arbitrary median magnitudes, predict conditional **quantiles** `Q10/Q50/Q90[log(P_D3/P_native_D0)]` and subtract already observed intraday gap `log(P_entry/P0)`. Proposed reliability gate: if resulting credible interval includes zero or round-trip bank spread, **ABSTAIN**, otherwise go long/flat (or short only if permitted). No posterior confidence or cutoff can be tuned on examined 2025/26 outcomes. Score direction, balanced accuracy, coverage, magnitude calibration, rescue/broken, adverse excursion and spread-adjusted return on *identical* matched rows.

**D. Origin time is an availability contract**, not just a timezone label. At 09 require prior candle complete and source publish time <=09; at 15 no use of future 15:30/16:30 macro results; at16:45 use only last completed16:30–16:45 bar, already-published CPI/NFP surprise, with price feed time <=16:45. Today's banking executable buy/sell quotes remain the ultimate gate.

## Final decision

**Clock-selection phase is READY/CLOSED: 09 and 16:45 are distinct primary decision clocks; 15 a clearly versioned interim update.** Preserve 16:30 as spread-latency fallback, 12:00 and 17:00 as controls. All H3 clock-normalization experiments and the negative magnitude bridge are documented without promotion of an accuracy number to real execution. The actual new work is now **target-specific executable-price forecasting at these locked reference clocks**, not a return to R41–R60 chronology validation.
