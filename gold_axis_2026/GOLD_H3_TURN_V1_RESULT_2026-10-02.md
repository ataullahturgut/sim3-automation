# TURN-H3 V1 — TAIL-UNBALANCED REVERSAL NAVIGATOR RESULT

**Status:** **NOT_PROMOTED_CONFIRM_FAIL**  
**Evidence class:** retrospective mechanism validation; architecture was motivated after historical error inspection.  
**Rule:** 120 active-hour semivariance; prior-250-anchor 80th-percentile tails.

## Period metrics

| Period | AURORA Acc | TURN Acc | AURORA BA | TURN BA | AURORA Brier | TURN Brier | Overrides | Rescued | Broken | Both-tail |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022_H2 | 62.50% | 63.39% | 62.05% | 63.27% | 0.2317 | 0.2345 | 9 | 5 | 4 | 9 |
| 2023 | 71.23% | 72.60% | 71.83% | 73.13% | 0.2118 | 0.2093 | 7 | 5 | 2 | 8 |
| 2024 | 70.83% | 65.42% | 69.97% | 65.41% | 0.2006 | 0.2242 | 23 | 5 | 18 | 28 |
| 2025 | 64.52% | 62.90% | 62.93% | 60.69% | 0.2276 | 0.2366 | 10 | 3 | 7 | 54 |
| 2026 | 60.73% | 59.69% | 61.12% | 60.21% | 0.2477 | 0.2513 | 6 | 2 | 4 | 27 |
| 2023-2024 | 71.02% | 68.85% | 71.24% | 69.33% | 0.2059 | 0.2171 | 30 | 10 | 20 | 36 |
| 2025-2026 | 62.87% | 61.50% | 62.07% | 60.41% | 0.2363 | 0.2430 | 16 | 5 | 11 | 81 |

## 2026 changed calls

| Issue | H3 end | AURORA | TURN | Actual | H3 return | RS+ tail | RS- tail | Effect |
|---|---|---|---|---|---:|---|---|---|
| 2026-01-27 | 2026-01-29 | DOWN | UP | UP | +7.71% | True | False | RESCUED |
| 2026-03-03 | 2026-03-05 | DOWN | UP | DOWN | -4.24% | True | False | BROKEN |
| 2026-04-09 | 2026-04-13 | DOWN | UP | DOWN | -1.09% | True | False | BROKEN |
| 2026-06-16 | 2026-06-18 | DOWN | UP | DOWN | -1.53% | True | False | BROKEN |
| 2026-07-06 | 2026-07-08 | DOWN | UP | DOWN | -2.15% | True | False | BROKEN |
| 2026-08-03 | 2026-08-05 | DOWN | UP | UP | +3.09% | True | False | RESCUED |

## Governance

TURN is a fixed literature-derived tail-region rule. No threshold, horizon, or state action was selected from 2022-2026 outcomes. Because the decision to study reversal was itself informed by historical error anatomy, only future frozen origins can provide prospective confirmation.
