# H2 — no-refit frozen H3 original votes vs future-only three-day exact-clock returns

**Final: REJECT / NO PROMOTION**. Prereg `2299d8c8` frozen BEFORE recalculating this review. Original R66 precise reference-clock ledger of **2464 historical entries**; no model was retrained. **R66/R69 previously trained direct H3 logistic and found poor 2025–26 transport; H2 does NOT duplicate this fitted learner**. This is a paired incremental truth check of the original H3 sign.

## Target / clock
Frozen R66 same-source HistData M15 quoted open: entry at 09:00, 15:00, 16:45 Turkey to original governed H3 third-date **same clock**. This is not old D0 average → D3 daily-average label. Every line has `realized_ret = ln(target_price/entry_price)` and binary label with parity verified. 09:00 **always carries prior eligible H3** (820/820), never a same-day later signal. 15:00/16:45 hypothetical same-day H3 issue is *not* first-print timestamp certified; this is not live predictive ability.

## Historical pairwise results
| TR clock | Year | N | Frozen H3 raw accuracy | H3 BA | Earlier-known gap-sign BA | N small-gap |
|---|---:|---:|---:|---:|---:|---:|
| 09:00 | 2023 | 116 | 59.48% | 58.63% | 53.70% | 63 |
| 09:00 | 2024 | 240 | 53.33% | 51.71% | 51.36% | 115 |
| 09:00 | 2025 | 247 | 51.42% | 49.37% | 50.43% | 104 |
| 09:00 | 2026 | 185 | 51.35% | 51.45% | 53.46% | 52 |
| 15:00 | 2023 | 116 | 60.34% | 59.70% | 57.87% | 63 |
| 15:00 | 2024 | 240 | 57.50% | 56.15% | 51.65% | 115 |
| 15:00 | 2025 | 247 | 48.58% | 45.51% | 49.27% | 96 |
| 15:00 | 2026 | 186 | 54.30% | 54.28% | 49.94% | 47 |
| 16:45 | 2023 | 116 | 63.79% | 63.57% | 58.67% | 67 |
| 16:45 | 2024 | 240 | 57.08% | 55.06% | 51.60% | 111 |
| 16:45 | 2025 | 247 | 49.80% | 47.41% | 50.53% | 102 |
| 16:45 | 2026 | 186 | 56.45% | 56.35% | 49.83% | 42 |

2023 and 2024 contain selected development history; 2025 and 2026 have been repeatedly examined. Higher 2023 DEV numbers do not survive 2025, for example:
- **09:00** 2025 H3 balanced accuracy 49.37%; 2026 51.45%.
- **15:00** 2025 45.51%; 2026 54.28%.
- **16:45** 2025 47.41%; 2026 56.35%.

Across **12 predeclared** opened-period paired comparisons (3 clocks × 2 years × 2 controls), minimum raw exact one-sided McNemar p **0.0519** and smallest Holm p **0.6226**. No family-wise significant gain. Frozen H3 cannot exceed both always-UP and already-known gap sign by three BA points in BOTH 2025 and 2026 at any clock. Significant post-decision incremental information was **not established**.

## Small-known-gap diagnostic (predeclared development medians)
Small subset `abs(log(entry_price/origin_mean)) < median_DEV_for_clock`, frozen at:
- 09:00: 0.006736
- 15:00: 0.003495
- 16:45: 0.004228

For example 2026 09:00 small-gap 52 calls H3 BA 61.60%, **but 2025 small-gap BA 47.31%**; do not select 2026 subset ex post. Nonoverlap greedy selection by governed source_D3 also saved with yearly per-class results in JSON to limit overlapping-horizon inflation; do not treat 3-day daily rolling labels as independent Bernoulli trials.

## Boundary
R66 same-day 15/16:45 source-vintage/issue readiness unproven. Original D0→D3 average model still valid as a *retrospective average-target estimator*, not demonstrated causally issued trade-time forecast. No claim of statistical non-existence: negative evidence for this frozen H3 vote on these clocks/vendors, at opened inspected cohorts.

## Reproduction
`tools/gold_h2_20261012_frozen_h3_truth_replay.py` recomputes all metrics, source parity and no-refit contrasts directly from original committed R66 ledger. `GOLD_H2_20261012_FROZEN_H3_FUTURE_INFORMATION_RESULT.json` holds 12 cohort class recalls and Holm correction.
