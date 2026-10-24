# CORRECTION — paired BASE14 vs CFTC21, same origin dates and targets (2026-10-25)

**Finding:** the prior report's “2/4 five-day risk episodes” describes **CFTC21 only**; it is not directly comparable to the earlier "**4/4** next-day -3%" statistic. More seriously, the old **BASE14** was omitted from the specialist V3 contender set, so saying no alternative outperforms the new 21-input model while failing to compare to the existing old base was misleading.

**Scientific position:** DO NOT replace BASE14 by BASE21-CFTC for the primary objective of identifying major gold drawdowns. CFTC decreases alarm days while missing two high-loss five-day label episodes in 2026. It can remain an experimental additional diagnostic only; it must not veto a BASE14 alert.

## Same input panel, same fit split, same score threshold

Source artifact: `gold_risk_v2_daily_alerts.csv` from recorded 2026-10-24 experiment. Exact same CFTC-valid origin row set for both families; both score thresholds = 95th **train-only** percentile of their anomaly score. BASE14 here is **refitted on CFTC-common rows**, not bytewise the earlier original 14-feature model trained on all dates. Their counts cannot be confused.

| Period | Measure | BASE14 (no CFTC) | BASE14_PLUS_CFTC_7 |
|---|---|---:|---:|
| 2025 (232 common origins) | RED days | 31 | 31 |
| 2025 | next-day ≤-3% origin hits | 2 / 3 | **3 / 3** |
| 2025 | next5 min ≤-5% origin hits | 4 / 5 | **5 / 5** |
| 2025 | 5-day origin GROUPS with at least one simultaneous RED | 2 / 3 | **3 / 3** |
| 2026 (161 common origins) | RED days | 51 | 29 |
| 2026 | next-day ≤-3% origin hits | **4 / 4** | **4 / 4** |
| 2026 | next5 min ≤-5% origin hits | **9 / 13** | 6 / 13 |
| 2026 | 5-day origin GROUPS with at least one simultaneous RED | **4 / 4** | 2 / 4 |
| 2026 | next5 non-event RED origin days | 42 | 23 |

**WARNING:** The grouped 5-day risk label represents `min(P[t+1..t+5])/P[t]-1 <= -0.05`; an alert **inside** a group is not guaranteed to occur **before the physical selloff's first price decline**. The “4/4” grouped hit rate is therefore NOT “four crash onsets predicted before they began”. Earliest alert strictly before first 5d-positive *origin* is **3/4 BASE14**, **3/4 CFTC21**, in a rolling prior 5 observed-origin window. Those warnings too are not necessarily before the first intraday decline.

## Four 2026 5-day **overlapping label groups** (not four causally independent crash onsets)

| 2026 first-to-last positive 5d origin | BASE14 in-group RED | CFTC21 in-group RED | Caveat |
|---|---|---|---|
| Jan 26–30 | Jan 26–30 | Jan 26–30 | both hit |
| Jun 03–05 | Jun 05 | **none** | BASE14 only flagged on the group's last day; not before the first positive label |
| Jun 17–18 | Jun 17–18 | **none** | BASE14 stronger, prior week also RED for both models |
| Aug 25–27 | Aug 25 | Aug 25 | both hit |

The initial V3 record evaluated six new models without including BASE14 as an incumbent. This audit corrects that omission but **does not retune on 2026**, refit a supervised model, certify source PIT vintages, nor promote model to the app.

**Selection constraint:** A V3 model chosen solely with 2025 data cannot be retroactively relabelled as the 2026 winner. The original incumbent BASE14 must be preserved separately; the 2025-chosen 21-feature challenger **failed its 2026 transport test**. A future V4 research hypothesis must be frozen using only pre-2026 information and then tested on newer genuinely untouched origin dates; retrospective 2026 cannot become a second tuning set.

**Data caveat:** 2026 invalid source daily reference on Feb27 quarantined; 2025 shutdown CFTC report dates handled; normal weeks CFTC +7-day proxy is **not exact certified release-time**; historical four-metal first-print unverified. NONE of these are real-time trade-ready indicators.

**Deployment:** NO production update; no app change; no Neon mutation; no GitHub automatic schedules re-enabled.
