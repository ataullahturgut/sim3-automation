# GOLD SHORT-HORIZON GLOBAL XAU — Stage 3 Probability Calibration / Conviction Result

**Status:** **NO_CONVICTION_PASS**

Selected probability stream: **RAW**

## Calibration metrics

| Method | Brier | Log loss | Pred SD | Cal intercept | Cal slope | ECE |
|---|---:|---:|---:|---:|---:|---:|
| RAW | 0.246731 | 0.686634 | 0.0442 | 0.0376 | 1.2331 | 0.0266 |
| PLATT | 0.250391 | 0.694437 | 0.0550 | 0.0860 | 0.3620 | 0.0204 |
| ISOTONIC | 0.255205 | 0.781230 | 0.0992 | 0.0951 | -0.0950 | 0.0449 |

## Frozen probability bands

| Band | N | Mean p | Realized UP rate | Brier |
|---|---:|---:|---:|---:|
| <=0.40 | 8 | 0.378 | 62.5% | 0.3017 |
| 0.40-0.45 | 56 | 0.435 | 41.1% | 0.2428 |
| 0.45-0.50 | 238 | 0.480 | 47.1% | 0.2484 |
| 0.50-0.55 | 314 | 0.524 | 54.1% | 0.2478 |
| 0.55-0.60 | 123 | 0.568 | 62.6% | 0.2361 |
| >=0.60 | 16 | 0.619 | 50.0% | 0.2696 |

## Conviction gate

- p >= 0.55: n=139, realized UP=61.2%
- p <= 0.45: n=64, realized UP=43.8%
- UP-rate separation: 17.4 pp
- conviction gate pass: **False**

2025 remained unopened. No P&L or cost threshold was tested.
