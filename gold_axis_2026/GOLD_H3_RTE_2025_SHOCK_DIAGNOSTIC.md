# RTE 2025 shock-transition diagnostic

**Scope:** failed 2025 confirmation reused as development. 2026 remains unopened.

- eligible origins: **211**
- V5 missed reversals: **68**

## Tension level × transition shape

| pRTE | Shape | Cand | Rescue | Broken | Net | Precision | Rate |
|---:|---|---:|---:|---:|---:|---:|---:|
| 0.65 | ALL | 71 | 33 | 38 | -5 | 46.48% | 33.65% |
| 0.65 | PLATEAU | 11 | 4 | 7 | -3 | 36.36% | 5.21% |
| 0.65 | SHOCK | 39 | 17 | 22 | -5 | 43.59% | 18.48% |
| 0.65 | BIG_SHOCK | 24 | 10 | 14 | -4 | 41.67% | 11.37% |
| 0.70 | ALL | 48 | 23 | 25 | -2 | 47.92% | 22.75% |
| 0.70 | PLATEAU | 6 | 1 | 5 | -4 | 16.67% | 2.84% |
| 0.70 | SHOCK | 32 | 15 | 17 | -2 | 46.88% | 15.17% |
| 0.70 | BIG_SHOCK | 20 | 8 | 12 | -4 | 40.00% | 9.48% |
| 0.75 | ALL | 31 | 13 | 18 | -5 | 41.94% | 14.69% |
| 0.75 | PLATEAU | 4 | 0 | 4 | -4 | 0.00% | 1.90% |
| 0.75 | SHOCK | 23 | 10 | 13 | -3 | 43.48% | 10.90% |
| 0.75 | BIG_SHOCK | 14 | 4 | 10 | -6 | 28.57% | 6.64% |
| 0.80 | ALL | 17 | 8 | 9 | -1 | 47.06% | 8.06% |
| 0.80 | PLATEAU | 1 | 0 | 1 | -1 | 0.00% | 0.47% |
| 0.80 | SHOCK | 14 | 6 | 8 | -2 | 42.86% | 6.64% |
| 0.80 | BIG_SHOCK | 9 | 2 | 7 | -5 | 22.22% | 4.27% |

## Largest 2025 reversal-vs-continuation separations

| Feature | SMD | reversal median | continuation median |
|---|---:|---:|---:|
| signed_opt_pressure | +0.390 | 0.0654 | -0.1744 |
| path_consistency | -0.375 | 0.0833 | 0.0833 |
| p_rte | +0.347 | 0.6481 | 0.5415 |
| p_inst | +0.335 | 0.5523 | 0.4520 |
| adverse_excursion | +0.219 | 0.3140 | 0.3310 |
| cf_signed_d_opt_pressure_gap | -0.167 | -0.0192 | 0.0144 |
| cf_signed_opt_pressure_gap | -0.084 | 0.0277 | 0.0188 |
| opposite_extreme_recency | +0.082 | 0.0742 | 0.0769 |
| signed_d_opt_pressure | -0.057 | 0.0033 | 0.0104 |
| dp_rte | +0.048 | 0.0668 | 0.0546 |
| deceleration_6h | -0.042 | 0.4928 | 0.3767 |
| cf_opt_total_z20_gap | +0.009 | 0.0927 | 0.2149 |
