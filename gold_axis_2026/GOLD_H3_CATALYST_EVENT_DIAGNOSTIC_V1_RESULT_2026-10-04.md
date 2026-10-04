# CATALYST-H3 V1 — EVENT-DAY DIAGNOSTIC

**Status:** retrospective mechanism diagnostic; not a promotion test.

Events: scheduled CPI, Employment Situation/NFP, and FOMC policy-decision dates.
Event flag is based on the H3 feature_cutoff_date, so the scheduled release has occurred before the canonical end-of-day H3 decision state.

## Event vs non-event

| Year/Bucket | N | Reversal rate | V5 error | V5 missed rev | SAGE error | SAGE missed rev | Mean |H3| |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2025 EVENT | 24 | 25.00% | 37.50% | 6 | 37.50% | 6 | 1.41% |
| 2025 NON_EVENT | 224 | 37.95% | 33.04% | 62 | 32.59% | 60 | 1.56% |
| 2026 EVENT | 24 | 45.83% | 33.33% | 7 | 33.33% | 7 | 2.62% |
| 2026 NON_EVENT | 166 | 43.37% | 37.35% | 51 | 34.94% | 47 | 2.18% |
| ALL CPI | 18 | 33.33% | 33.33% | 4 | 33.33% | 4 | 1.62% |
| ALL NFP | 18 | 22.22% | 27.78% | 3 | 27.78% | 3 | 1.70% |
| ALL FOMC | 12 | 58.33% | 50.00% | 6 | 50.00% | 6 | 3.08% |
| ALL ALL_EVENT | 48 | 35.42% | 35.42% | 13 | 35.42% | 13 | 2.02% |
| ALL ALL_NON_EVENT | 390 | 40.26% | 34.87% | 113 | 33.59% | 107 | 1.82% |

## Concentration

- V5 missed reversals on event days: **13/126**
- SAGE missed reversals on event days: **13/120**

This diagnostic answers only whether scheduled macro-event days enrich reversal/error states. It does not use the surprise sign or intraday post-release response yet.
