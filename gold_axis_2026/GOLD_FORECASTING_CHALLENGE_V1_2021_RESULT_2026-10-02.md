# GOLD FORECASTING CHALLENGE V1 — SEALED 2021 TEST

Locked champion: **CORE3 + LOGIT_EN**.
Selection commit recorded in lock: \`875734b04557d42d93e4da74dcb1a9e9e8593870\`.

## Full coverage

| Model | N | Accuracy | Balanced acc | False calls | Brier | Log loss | UP recall | DOWN recall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| EXPANDING_PRIOR | 252 | 48.02% | 50.00% | 51.98% | 0.2512 | 0.6955 | 100.00% | 0.00% |
| COMPARATOR_CORE3_LOGIT_L2 | 252 | 49.60% | 50.26% | 50.40% | 0.2527 | 0.6988 | 66.94% | 33.59% |
| CHAMPION_CORE3_LOGIT_EN | 252 | 51.19% | 51.92% | 48.81% | 0.2522 | 0.6977 | 70.25% | 33.59% |

## Frozen confidence filters

| Validation-frozen rule | Calls | Coverage | Accuracy | Balanced acc | False calls | UP calls | DOWN calls |
|---|---:|---:|---:|---:|---:|---:|---:|
| VALIDATION_60PCT_COVERAGE_CUTOFF | 155 | 61.51% | 50.97% | 52.31% | 49.03% | 113 | 42 |
| VALIDATION_40PCT_COVERAGE_CUTOFF | 116 | 46.03% | 50.00% | 52.52% | 50.00% | 86 | 30 |

This is the single sealed-test report for Challenge V1. Any model modification belongs to a new challenge version.
