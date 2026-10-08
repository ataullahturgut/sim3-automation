# Gold execution direction — VIX–GVZ divergence preregistration (2026-10-08)

Status: Hypothesis registered ahead of training. New trial, not a baseline change. No 2025-conditioned feature or threshold search.

Question: Does previously completed Cboe VIX (market equity fear), relative to previously completed GVZ (gold-specific option fear), predict Gold direction above the XAU price path and the GVZ level alone? Divergence is a research hypothesis, not proof of causation.

Source: Cboe official daily VIX CLOSE, already pinned Cboe GVZ D-1, audited 2020–25 same-source XAU BID M15 and frozen DAY/OVN label ledger. VIX observations last and second-last must be strictly older than origin local date, max 7-day staleness; no same-day VIX.

Targets kept separate: Turkey DAY 09:00 to 17:00 and regular weekday16h overnight 17:00 to next eligible 09:00. No Friday64h target mixing.

Fixed challengers:
- BASE_LOGIT and SHAPE_GVZ_HGB are exact source-matched existing baseline identities.
- VIX_GVZ_LOGIT: full price-shape and GVZ set, plus log(previous-day VIX), log return between latest two available VIX observations, and log(VIX/GVZ); StandardScaler and L2 LogisticRegression C=0.3.
- VIX_GVZ_HGB: same feature set with max_iter=90, learning rate=.04, max_leaf_nodes=7, min_samples_leaf=35, max_depth=3, L2=10.

All models scored on identical accepted dates, fixed parameters. Training: 2022 warmup, 2023–24 prior matured-label monthly walkforward, 2025 single frozen-2024 fit and retrospective already-inspected transport. No 2025 threshold tuning.

Measurements: N, Accuracy, BA, DOWN/UP recall, Brier, log loss, confusion matrix and direct paired rescues-minus-breaks / exact McNemar against baseline. Distinguish multiple-trial exploratory evidence from statistically established edge. Bank tradability and execution spread not validated.

Cboe official source: https://www.cboe.com/tradable_products/vix/vix_historical_data
