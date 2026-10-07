# GOLD EXECUTION RFR-NOMACRO V1 RESULT — 2026-10-07

**Status:** COMPLETE / DEVELOPMENT-SUPPORTED SELECTIVE OVERNIGHT SPECIALIST

Rule: when 16:00-16:30 and 16:30-17:00 directions are opposite and no same-day paired macro surprise has been released by 17:00, predict the overnight direction as the 16:00-16:30 direction; otherwise abstain.

| Period | N | Coverage | Rule Acc | Rule BA | UP recall | DOWN recall | Pair Acc same rows | Pair BA | Majority Acc | Rescue | Break | Net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023 | 118 | 46.27% | 57.63% | 57.75% | 56.25% | 59.26% | 54.24% | 53.04% | 54.24% | 11 | 7 | +4 |
| 2024 | 113 | 43.63% | 56.64% | 56.42% | 60.00% | 52.83% | 54.87% | 53.87% | 53.10% | 8 | 6 | +2 |
| 2025 | 111 | 43.87% | 58.56% | 58.14% | 63.33% | 52.94% | 59.46% | 58.68% | 54.05% | 2 | 3 | -1 |

DEV pooled: accuracy **57.14%**, BA **57.07%**, rescue/break/net **19/13/+6**.
DEV one-sided binomial p vs 50%: **0.0175**; exact rescue-vs-break p against pair model: **0.3771**.

Interpretation: this is a selective overnight specialist with roughly mid-40% coverage, not a full-coverage daily model. The 2025 result is retrospective transport, not prospective proof.
