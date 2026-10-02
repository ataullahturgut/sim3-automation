# OPAL-H3 V1 — OPTIONS POSITIONING ASYMMETRY LAYER RESULT

**Status:** **NOT_PROMOTED_CONFIRM_FAIL**  
**Evidence class:** retrospective mechanism validation; architecture was motivated after historical error inspection.  
**CFTC availability lag:** 7 calendar days; **reversal threshold:** 0.70

## Period metrics

| Period | AURORA Acc | OPAL Acc | AURORA BA | OPAL BA | AURORA Brier | OPAL Brier | Overrides | Rescued | Broken |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022_H2 | 57.58% | 57.58% | 58.27% | 62.31% | 0.2567 | 0.2707 | 8 | 4 | 4 |
| 2023 | 71.23% | 67.12% | 71.83% | 67.41% | 0.2118 | 0.2303 | 27 | 9 | 18 |
| 2024 | 70.83% | 70.00% | 69.97% | 67.99% | 0.2006 | 0.2070 | 20 | 9 | 11 |
| 2025 | 64.52% | 64.92% | 62.93% | 61.42% | 0.2276 | 0.2330 | 23 | 12 | 11 |
| 2026 | 60.73% | 63.87% | 61.12% | 64.21% | 0.2477 | 0.2452 | 24 | 15 | 9 |
| 2023-2024 | 71.02% | 68.63% | 71.24% | 68.14% | 0.2059 | 0.2181 | 47 | 18 | 29 |
| 2025-2026 | 62.87% | 64.46% | 62.07% | 63.24% | 0.2363 | 0.2383 | 47 | 27 | 20 |

## 2026 changed calls

| Issue | H3 end | COT report | AURORA | P(reversal) | OPAL | Actual | H3 return | Effect |
|---|---|---|---|---:|---|---|---:|---|
| 2026-03-11 | 2026-03-13 | 2026-03-03 | UP | 73.5% | DOWN | DOWN | -2.11% | RESCUED |
| 2026-03-17 | 2026-03-19 | 2026-03-03 | UP | 71.0% | DOWN | DOWN | -5.84% | RESCUED |
| 2026-06-05 | 2026-06-09 | 2026-05-26 | UP | 72.5% | DOWN | DOWN | -3.85% | RESCUED |
| 2026-06-24 | 2026-06-26 | 2026-06-16 | UP | 72.2% | DOWN | DOWN | -1.93% | RESCUED |
| 2026-07-29 | 2026-07-31 | 2026-07-21 | DOWN | 71.4% | UP | UP | +0.57% | RESCUED |
| 2026-08-03 | 2026-08-05 | 2026-07-21 | DOWN | 72.5% | UP | UP | +3.09% | RESCUED |
| 2026-08-04 | 2026-08-06 | 2026-07-21 | DOWN | 80.8% | UP | UP | +4.98% | RESCUED |
| 2026-08-12 | 2026-08-14 | 2026-08-04 | DOWN | 85.1% | UP | DOWN | -0.63% | BROKEN |
| 2026-08-13 | 2026-08-17 | 2026-08-04 | UP | 76.2% | DOWN | DOWN | -0.06% | RESCUED |
| 2026-08-14 | 2026-08-18 | 2026-08-04 | DOWN | 78.3% | UP | UP | +0.03% | RESCUED |
| 2026-08-21 | 2026-08-25 | 2026-08-11 | UP | 73.6% | DOWN | UP | +3.18% | BROKEN |
| 2026-08-24 | 2026-08-26 | 2026-08-11 | UP | 76.0% | DOWN | UP | +0.92% | BROKEN |
| 2026-08-25 | 2026-08-27 | 2026-08-11 | UP | 78.4% | DOWN | DOWN | -0.91% | RESCUED |
| 2026-08-26 | 2026-08-28 | 2026-08-18 | UP | 74.4% | DOWN | DOWN | -2.12% | RESCUED |
| 2026-08-27 | 2026-08-31 | 2026-08-18 | DOWN | 74.2% | UP | DOWN | -4.03% | BROKEN |
| 2026-08-28 | 2026-09-01 | 2026-08-18 | DOWN | 88.7% | UP | DOWN | -4.95% | BROKEN |
| 2026-09-01 | 2026-09-03 | 2026-08-18 | UP | 73.1% | DOWN | UP | +0.25% | BROKEN |
| 2026-09-04 | 2026-09-08 | 2026-08-25 | UP | 70.1% | DOWN | DOWN | -1.17% | RESCUED |
| 2026-09-07 | 2026-09-09 | 2026-08-25 | DOWN | 77.0% | UP | DOWN | -1.26% | BROKEN |
| 2026-09-10 | 2026-09-14 | 2026-09-01 | UP | 77.8% | DOWN | DOWN | -2.03% | RESCUED |
| 2026-09-14 | 2026-09-16 | 2026-09-01 | UP | 77.4% | DOWN | DOWN | -0.72% | RESCUED |
| 2026-09-17 | 2026-09-21 | 2026-09-08 | DOWN | 74.3% | UP | UP | +0.88% | RESCUED |
| 2026-09-21 | 2026-09-23 | 2026-09-08 | DOWN | 80.4% | UP | DOWN | -1.40% | BROKEN |
| 2026-09-22 | 2026-09-24 | 2026-09-08 | DOWN | 81.7% | UP | DOWN | -1.86% | BROKEN |

## Governance

OPAL reconstructs delta-adjusted options-only cohort exposures from official CFTC combined minus futures-only disaggregated reports. The 7-day lag is intentionally conservative. No feature, lag, model hyperparameter or reversal threshold may be retuned from 2022-2026 outcomes. Frozen AURORA prospective validation is unchanged.
