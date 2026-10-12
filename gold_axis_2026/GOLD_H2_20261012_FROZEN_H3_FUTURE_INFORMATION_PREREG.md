# H2 — frozen original H3 information vs future exact-clock XAU/USD outcome: preregistration

2026-10-12. Historical replay, not clean OOS. Check against prior R66/R69 results to **avoid duplicating their direct logistic/ridge retraining**. This new test makes **no new trained model**; its narrow purpose is an incremental, paired comparison of **frozen native H3 vote** against no-information and source-known gap direction, including small-gap contrast.

## Source and decision chronology
- Exact existing R66 frozen ledger `gold_axis_2026/GOLD_R66_20261012_H3_09_CARRY_15_1645_EXECUTION_TARGET_MODELS_ALLROWS.csv` from repository's canonical working branch; no price/vendor joins, calendar/hour scan, no alteration of original H3 target/labels.
- Three predeclared reference clock origins and targets: Europe/Istanbul 09:00, 15:00, 16:45 at issue date to exactly the **same clock on original H3 third governed date**, no overlapping returned observations treated as independent. Original H3 D0 average→D3 average is **NOT** this outcome.
- At 09:00 use previous eligible H3 issue and previous data cutoff; original R66 `prior_signal` must be true. At 15:00/16:45 same-day H3 issue time/first-print not actually historically archived, so these are **retrospective hypothetical issue-time analyses**, no live causality claim.
- `A = gap = log(entry_price/origin_mean)`, already-observed at decision (subject to source-clock caveats). Future-only label `y = (target_price>entry_price)`, R66's `realized_ret=log(target/entry)`. Enforce exact parity to source row. 2023–2024 DEV used only for historical predeclared threshold; 2025/26 repeatedly opened and only retrospective transport.

## Frozen hypotheses, controls, gates
- No logistic refit: R66 already trained same-family exact-clock logistic and failed transport; replacing its architecture or posthoc tuning is redundant.
- Candidate: unchanged `h3bit` (UP1/DOWN0). Baselines on **exact matching dates**: `ALWAYS_UP=1`; `GAP_SIGN=(gap>=0)?1:0`. Secondary `PREDECISION_SIGN=(predecision_intra>=0)?1:0` diagnostic.
- Predeclared **small-known-gap** subset: `abs(gap)` strictly below **median absolute gap in 2023–24 separately for each clock**. No rank/threshold tuning on 2025/26. Re-score frozen signals on all dates and subset, report accuracy, BA, UP/DOWN recall, N and overlap.
- Paired H3 vs ALWAYS_UP and vs GAP_SIGN: one-sided exact McNemar/binomial tail on discordant forecast correctness; adjust all **12** clock×year×control 2025/26 comparisons with Holm. Signal claim requires for **both opened years** and at least one predeclared clock H3 BA to exceed the paired always-UP BA by ≥0.03 AND paired GAP_SIGN BA by ≥0.03, and each paired Holm p<0.05. All years previously examined; even passing is merely exploratory, not virgin test.
- Three-day targets overlap; use separate weekly/nonoverlap descriptive direction and state strong serial correlation makes naïve p-values optimistic; no false independent sample claims. Friday/holiday maturity must remain based on R66 existing third *governed* day.

## Scientific result boundaries
- H2 fails if thresholds/gates fail; old H3 %65–80 cannot be advertised as 3-day post-decision skill.
- If R66 source rows fail semantic/time parity, mark BLOCKED rather than fitting around the error.
- Store evidence, reproducibility, controlled timing notes on separate research branch, no Neon writes, no manifest/champion changes.
