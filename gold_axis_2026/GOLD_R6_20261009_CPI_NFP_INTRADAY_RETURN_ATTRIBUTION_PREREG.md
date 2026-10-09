# R6 prereg — WHAT actually drove anomalous 2026 CPI/NFP 11/14 correct XAU DAY?
Author: GPT-6. 2026-10-09, BEFORE executing the below event-resolved subinterval return queries. **Important: the prior 11/14 success in 2026 is ALREADY inspected and this subanalysis is EXPLORATORY, not a virgin holdout.**

Question: does frozen 08:45TR /09→17 DAY DIR4 correctly anticipate gold's first market reaction to the 08:30 ET CPI/NFP release, or does its 2026 11/14 correctness arise from (A) the pre-news daytime drift, (B) a delayed partial-day/post-release continuation, or (C) chance/target aggregation with offsetting opposite moves?

Source: for 2023–25 canonical EV Dukascopy 15min bid/ask panel, frozen original source-governed event_ts_utc `GOLD_EXECUTION_PRAMV_OFFICIAL_2025_MACRO_SOURCE_GOVERNED_V2_20261008.csv` rows ONLY NFP or CPI within 09TR–17TR; event timestamp is precise UTC. For 2026 `gold_research_dukascopy_2026_direct_m1_m15_bidask_v2` require `m1_matched=15`; official BLS schedule `https://www.bls.gov/schedule/2026/home.htm` copied in prior R5 prereg. Local release 15:30TR during NY DST, 16:30TR in standard winter. Exclude event dates absent source, never treat as ordinary. Same upstream Dukascopy; not an independent market reference.
Dates source-approved if 17 contiguous completed origin M15 bars start04:30..08:30 at issue08:45, source original entry bar start08:45 closing09:00, source17 exit bar start16:45 closing17:00. On-event subinterval anchors: pre-news close = bar start release UTC minus15min (closing at release exact timestamp), first 15m-post-news close = bar START release timestamp, 17close = original. All required anchors same BID/ASK venue. Source original full day canonical sign MUST match governed day_y 2023–25; else quarantine + count. Delay timestamp known retrospective, not assume PIT official 2025 release calendar is immutable.

Exact mutually additive returns:
  `pre := ln(mid(release 0-) / mid09)` (09TR to timestamp 08:30ET);
  `reaction15 := ln(mid(release+15m) / mid(release0-))`;
  `remainder := ln(mid17 / mid(release+15m))`;
  `day := pre+reaction15+remainder`.
  `post := reaction15+remainder`.
Nonzero sign rate among each of these three intervals and full day vs frozen DIR4 and B4 sign, separately for 2023/24/25/26. Denominators must be explicit; no BA if group only one class or n<8. Define 'post drives full-day' as `sign(post)==sign(day)`; `pre drives full-day` analogous, and `post reversed pre` if `sign(pre)!=sign(post)`.
Prespecified measure of signal location: (1) accuracies vs pre-news, first15m, full post, post-remainder, full DAY, all matched dates; (2) event days when initial predicted sign gets first15 wrong yet final full correct; (3) any event with final large outcome driven by before rather than post; (4) 2026 estimated prospective utility cannot be inferred. No parameter fitting, selective gating, tuning or post-outcome use as feature.

Negative control PLACEBO: on all SOURCE-QUALIFIED no-CPI/NFP DAY dates in each year, split at matching source-local 15:30 (NY summer) /16:30 (NY winter), computed with explicit `America/New_York` DST calendar; use only current native source and sufficient full event-anchored bars. Compare sign agreement B4/DIR4 for pre, first15, post, full DAY and compare first15 magnitude bps in EVENT vs NO-EVENT at SAME CLOCK by year. Do not assert matched placebo days are other-news-free. This is a descriptive placebo, not a formal causal matching estimator.

Need BLOCK if same-source event anchors incomplete: count partial vs full date. An observed 2026 11/14 high model accuracy is NOT advertised as actionable 78% rule. Research output academic report and manifest.
