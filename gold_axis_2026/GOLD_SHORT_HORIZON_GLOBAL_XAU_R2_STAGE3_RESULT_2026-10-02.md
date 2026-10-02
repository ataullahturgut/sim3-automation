# GOLD SHORT-HORIZON GLOBAL XAU R2 — Stage 3 Probability Calibration / Conviction Result

**Status:** **CONVICTION_PASS**

Selected probability stream: **RAW**

## Calibration metrics

| Method | Brier | Log loss | Pred SD | Cal intercept | Cal slope | ECE |
|---|---:|---:|---:|---:|---:|---:|
| RAW | 0.246637 | 0.686447 | 0.0448 | 0.0342 | 1.2343 | 0.0256 |
| PLATT | 0.250293 | 0.694202 | 0.0544 | 0.0855 | 0.3774 | 0.0223 |
| ISOTONIC | 0.252886 | 0.746264 | 0.1017 | 0.0924 | -0.0338 | 0.0460 |

## Frozen probability bands

| Band | N | Mean p | Realized UP rate | Brier |
|---|---:|---:|---:|---:|
| <=0.40 | 10 | 0.381 | 60.0% | 0.2940 |
| 0.40-0.45 | 54 | 0.436 | 37.0% | 0.2383 |
| 0.45-0.50 | 232 | 0.480 | 48.3% | 0.2492 |
| 0.50-0.55 | 311 | 0.524 | 52.7% | 0.2486 |
| 0.55-0.60 | 131 | 0.568 | 64.9% | 0.2335 |
| >=0.60 | 17 | 0.618 | 47.1% | 0.2755 |

## Conviction gate

- p >= 0.55: n=148, realized UP=62.8%
- p <= 0.45: n=64, realized UP=40.6%
- UP-rate separation: 22.2 pp
- conviction gate pass: **True**

2025 remained unopened. No P&L or cost threshold was tested.
