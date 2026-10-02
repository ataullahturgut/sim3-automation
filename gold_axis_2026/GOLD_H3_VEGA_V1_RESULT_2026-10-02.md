# VEGA-H3 V1 — VOLATILITY-EXPECTATIONS GAP REVERSAL RESULT

**Status:** **NOT_PROMOTED_CONFIRM_FAIL**  
**Evidence class:** retrospective mechanism validation; architecture was motivated after historical error inspection.  
**GVZ lag:** D-1 or earlier; **reversal threshold:** 0.70

## Period metrics

| Period | AURORA Acc | VEGA Acc | AURORA BA | VEGA BA | AURORA Brier | VEGA Brier | Overrides | Rescued | Broken |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022_H2 | 57.58% | 57.58% | 58.27% | 58.27% | 0.2567 | 0.2567 | 0 | 0 | 0 |
| 2023 | 71.23% | 69.86% | 71.83% | 70.48% | 0.2118 | 0.2178 | 7 | 2 | 5 |
| 2024 | 70.83% | 70.42% | 69.97% | 70.05% | 0.2006 | 0.2053 | 13 | 6 | 7 |
| 2025 | 64.52% | 64.11% | 62.93% | 63.16% | 0.2276 | 0.2291 | 9 | 4 | 5 |
| 2026 | 60.73% | 60.21% | 61.12% | 60.52% | 0.2477 | 0.2466 | 13 | 6 | 7 |
| 2023-2024 | 71.02% | 70.15% | 71.24% | 70.57% | 0.2059 | 0.2113 | 20 | 8 | 12 |
| 2025-2026 | 62.87% | 62.41% | 62.07% | 61.85% | 0.2363 | 0.2367 | 22 | 10 | 12 |

## 2026 changed calls

| Issue | H3 end | AURORA | P(reversal) | VEGA | Actual | H3 return | Effect |
|---|---|---|---:|---|---|---:|---|
| 2026-02-03 | 2026-02-05 | DOWN | 72.3% | UP | UP | +3.64% | RESCUED |
| 2026-02-04 | 2026-02-06 | UP | 70.8% | DOWN | DOWN | -1.09% | RESCUED |
| 2026-02-10 | 2026-02-12 | UP | 71.3% | DOWN | UP | +1.14% | BROKEN |
| 2026-02-11 | 2026-02-13 | DOWN | 70.4% | UP | DOWN | -1.91% | BROKEN |
| 2026-02-12 | 2026-02-16 | UP | 73.8% | DOWN | DOWN | -1.85% | RESCUED |
| 2026-03-11 | 2026-03-13 | UP | 70.4% | DOWN | DOWN | -2.11% | RESCUED |
| 2026-03-12 | 2026-03-16 | DOWN | 72.7% | UP | DOWN | -3.53% | BROKEN |
| 2026-04-02 | 2026-04-06 | UP | 71.5% | DOWN | DOWN | -1.50% | RESCUED |
| 2026-04-06 | 2026-04-08 | UP | 80.0% | DOWN | UP | +2.11% | BROKEN |
| 2026-04-08 | 2026-04-10 | UP | 71.4% | DOWN | UP | +1.91% | BROKEN |
| 2026-04-13 | 2026-04-15 | UP | 71.5% | DOWN | UP | +1.09% | BROKEN |
| 2026-08-04 | 2026-08-06 | DOWN | 72.2% | UP | UP | +4.98% | RESCUED |
| 2026-08-28 | 2026-09-01 | DOWN | 70.5% | UP | DOWN | -4.95% | BROKEN |

## Governance

VEGA adds forward-looking options-implied volatility information but remains retrospective mechanism research. No GVZ lag, feature, model hyperparameter or reversal threshold may be retuned from 2022-2026 outcomes. Frozen AURORA prospective validation is unchanged.
