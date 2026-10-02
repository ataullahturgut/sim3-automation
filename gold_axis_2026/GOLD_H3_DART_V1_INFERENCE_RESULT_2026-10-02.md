# DART-H3 V1 — DEPENDENCE-AWARE INFERENCE AUDIT

Circular moving-block bootstrap; paired forecast-origin differences; 10,000 replicates.

## Accuracy difference

| Period | Comparison | Block | Observed | 95% interval | P(improvement) |
|---|---|---:|---:|---:|---:|
| 2025 | DART_vs_STRUCTURAL | 5 | +0.40 pp | [-1.61, +2.42] pp | 59.4% |
| 2025 | DART_vs_STRUCTURAL | 10 | +0.40 pp | [-2.02, +2.42] pp | 58.6% |
| 2025 | DART_vs_SENTRY | 5 | -0.40 pp | [-1.21, +0.00] pp | 0.0% |
| 2025 | DART_vs_SENTRY | 10 | -0.40 pp | [-1.21, +0.00] pp | 0.0% |
| 2025 | PATH_vs_STRUCTURAL | 5 | +1.21 pp | [-3.23, +5.65] pp | 66.5% |
| 2025 | PATH_vs_STRUCTURAL | 10 | +1.21 pp | [-3.23, +5.65] pp | 66.2% |
| 2026 | DART_vs_STRUCTURAL | 5 | +2.09 pp | [-1.05, +5.76] pp | 87.0% |
| 2026 | DART_vs_STRUCTURAL | 10 | +2.09 pp | [-1.06, +5.76] pp | 84.9% |
| 2026 | DART_vs_SENTRY | 5 | +0.52 pp | [-1.57, +2.62] pp | 58.7% |
| 2026 | DART_vs_SENTRY | 10 | +0.52 pp | [-1.57, +2.62] pp | 59.2% |
| 2026 | PATH_vs_STRUCTURAL | 5 | +2.09 pp | [-1.05, +5.24] pp | 86.2% |
| 2026 | PATH_vs_STRUCTURAL | 10 | +2.09 pp | [-1.05, +5.76] pp | 84.7% |
| 2025-2026 | DART_vs_STRUCTURAL | 5 | +1.14 pp | [-0.68, +2.96] pp | 86.7% |
| 2025-2026 | DART_vs_STRUCTURAL | 10 | +1.14 pp | [-0.68, +2.96] pp | 85.6% |
| 2025-2026 | DART_vs_SENTRY | 5 | +0.00 pp | [-1.14, +1.14] pp | 42.9% |
| 2025-2026 | DART_vs_SENTRY | 10 | +0.00 pp | [-1.14, +1.14] pp | 42.8% |
| 2025-2026 | PATH_vs_STRUCTURAL | 5 | +1.59 pp | [-1.37, +4.56] pp | 84.4% |
| 2025-2026 | PATH_vs_STRUCTURAL | 10 | +1.59 pp | [-1.37, +4.56] pp | 83.9% |

## Brier difference

Negative values favor the candidate.

| Period | Comparison | Block | Observed | 95% interval | P(improvement) |
|---|---|---:|---:|---:|---:|
| 2025 | DART_vs_STRUCTURAL | 5 | +0.0009 | [-0.0031, +0.0060] | 38.3% |
| 2025 | DART_vs_STRUCTURAL | 10 | +0.0009 | [-0.0029, +0.0060] | 37.4% |
| 2025 | DART_vs_SENTRY | 5 | +0.0027 | [+0.0001, +0.0064] | 0.6% |
| 2025 | DART_vs_SENTRY | 10 | +0.0027 | [+0.0000, +0.0071] | 0.0% |
| 2025 | PATH_vs_STRUCTURAL | 5 | -0.0024 | [-0.0134, +0.0085] | 66.1% |
| 2025 | PATH_vs_STRUCTURAL | 10 | -0.0024 | [-0.0141, +0.0084] | 66.3% |
| 2026 | DART_vs_STRUCTURAL | 5 | -0.0079 | [-0.0140, -0.0024] | 99.8% |
| 2026 | DART_vs_STRUCTURAL | 10 | -0.0079 | [-0.0138, -0.0028] | 99.9% |
| 2026 | DART_vs_SENTRY | 5 | -0.0036 | [-0.0077, -0.0006] | 99.4% |
| 2026 | DART_vs_SENTRY | 10 | -0.0036 | [-0.0076, -0.0006] | 99.4% |
| 2026 | PATH_vs_STRUCTURAL | 5 | -0.0079 | [-0.0140, -0.0024] | 99.8% |
| 2026 | PATH_vs_STRUCTURAL | 10 | -0.0079 | [-0.0137, -0.0029] | 100.0% |
| 2025-2026 | DART_vs_STRUCTURAL | 5 | -0.0029 | [-0.0067, +0.0009] | 93.5% |
| 2025-2026 | DART_vs_STRUCTURAL | 10 | -0.0029 | [-0.0065, +0.0008] | 94.3% |
| 2025-2026 | DART_vs_SENTRY | 5 | -0.0001 | [-0.0026, +0.0026] | 54.7% |
| 2025-2026 | DART_vs_SENTRY | 10 | -0.0001 | [-0.0027, +0.0029] | 54.8% |
| 2025-2026 | PATH_vs_STRUCTURAL | 5 | -0.0048 | [-0.0114, +0.0019] | 92.1% |
| 2025-2026 | PATH_vs_STRUCTURAL | 10 | -0.0048 | [-0.0118, +0.0019] | 91.3% |

## Interpretation

Intervals crossing zero imply the observed point-estimate advantage is not statistically decisive under that dependence sensitivity. This audit is descriptive robustness evidence and does not alter DART states or thresholds.
