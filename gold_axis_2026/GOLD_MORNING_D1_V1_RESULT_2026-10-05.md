# MORNING-D1 V1 — 09:00 TR MICROSTATE NOWCAST RESULT

**Selected:** M3_MICRO_PLUS_H3 / LOGIT_L2 / threshold 0.75

## Source availability

| Channel | Status | Rows | First | Last |
|---|---|---:|---|---|
| GC | OK | 10050 | 2025-01-02 05:00:00+00:00 | 2026-09-30 23:00:00+00:00 |
| SI | OK | 10050 | 2025-01-02 05:00:00+00:00 | 2026-09-30 23:00:00+00:00 |
| NQ | OK | 10032 | 2025-01-02 05:00:00+00:00 | 2026-09-30 23:00:00+00:00 |
| ZN | OK | 9979 | 2025-01-02 05:00:00+00:00 | 2026-09-30 23:00:00+00:00 |
| CL | OK | 9913 | 2025-01-02 05:00:00+00:00 | 2026-09-30 23:00:00+00:00 |

## 2025-Q3 selection

| Family | Model | Feature min coverage | Acc | BA | Brier |
|---|---|---:|---:|---:|---:|
| M1_GOLD_MICRO | LOGIT_L2 | 100.00% | 57.81% | 55.59% | 0.2495 |
| M1_GOLD_MICRO | HGB_SMALL | 100.00% | 54.69% | 53.63% | 0.2795 |
| M2_GOLD_PLUS_CROSS | LOGIT_L2 | 96.15% | 57.81% | 55.59% | 0.2597 |
| M2_GOLD_PLUS_CROSS | HGB_SMALL | 96.15% | 54.69% | 53.04% | 0.2916 |
| M3_MICRO_PLUS_H3 | LOGIT_L2 | 96.15% | 79.69% | 78.73% | 0.1552 |
| M3_MICRO_PLUS_H3 | HGB_SMALL | 96.15% | 82.81% | 82.06% | 0.1628 |

## 2025-Q4 frozen threshold

| t | Actions | Coverage | Correct | Accuracy |
|---:|---:|---:|---:|---:|
| 0.55 | 61 | 96.83% | 51 | 83.61% |
| 0.60 | 59 | 93.65% | 50 | 84.75% |
| 0.65 | 58 | 92.06% | 50 | 86.21% |
| 0.70 | 58 | 92.06% | 50 | 86.21% |
| 0.75 | 58 | 92.06% | 50 | 86.21% |

## 2026 untouched test

- full accuracy: **79.56%**; BA **79.72%**; Brier **0.1412**
- selective: **110/126 = 87.30%**, coverage **69.61%**

## CIG integration

| Policy | 2026 actions | Acc | Coverage | Aug actions | Aug acc | Aug coverage |
|---|---:|---:|---:|---:|---:|---:|
| consensus | 157 | 71.34% | 82.20% | 10 | 80.00% | 47.62% |
| resolve_only | 175 | 72.57% | 91.62% | 17 | 82.35% | 80.95% |
| veto_resolve | 159 | 77.36% | 83.25% | 17 | 82.35% | 80.95% |

## Promotion
- RESOLVE_ONLY: **PASS**
- VETO_RESOLVE: **PASS**

This is a later-information nowcast and must not be represented as a prior-close forecast. Raw hourly vendor values are not persisted in repository outputs.
