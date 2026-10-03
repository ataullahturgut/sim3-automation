# RTE-H3 V1 — DEV FALSE-POSITIVE DIAGNOSTIC

**Scope:** 2023-2024 DEV only. 2025/2026 outcomes are not opened.

## Threshold 0.70

- candidates: **32**
- rescued / broken: **14 / 18**

### Largest standardized separations (rescued - broken)

| Feature | SMD | Rescue median | Broken median |
|---|---:|---:|---:|
| dp_rte | -1.371 | 0.0039 | 0.1745 |
| tension_velocity | -0.845 | 0.0317 | 0.9558 |
| rte_tension | +0.754 | 2.8814 | 2.4765 |
| p_rte | +0.753 | 0.8638 | 0.8154 |
| opposite_extreme_recency | -0.558 | 0.0742 | 0.1056 |
| cf_adverse_excursion_gap | -0.505 | 0.0291 | 0.1114 |
| cf_opt_total_z20_gap | +0.454 | 0.5196 | 0.3039 |
| opt_total_z20 | +0.356 | 0.8484 | 0.2775 |
| signed_opt_pressure | +0.240 | 0.3068 | 0.0385 |
| dp_inst | -0.217 | -0.0217 | 0.0753 |

### Mechanism flags

- opt_against_and_rising: rescued **42.9%**, broken **27.8%**, diff **+15.1 pp**
- cf_opt_joint: rescued **14.3%**, broken **11.1%**, diff **+3.2 pp**
- path_fracture_joint: rescued **28.6%**, broken **50.0%**, diff **-21.4 pp**

## Threshold 0.75

- candidates: **26**
- rescued / broken: **13 / 13**

### Largest standardized separations (rescued - broken)

| Feature | SMD | Rescue median | Broken median |
|---|---:|---:|---:|
| dp_rte | -1.206 | 0.0039 | 0.1754 |
| tension_velocity | -0.787 | 0.0317 | 1.1351 |
| opposite_extreme_recency | -0.633 | 0.0769 | 0.1111 |
| rte_tension | +0.534 | 2.9019 | 2.6995 |
| p_rte | +0.495 | 0.8655 | 0.8401 |
| cf_adverse_excursion_gap | -0.471 | 0.0162 | 0.1486 |
| path_consistency | +0.448 | 0.0833 | 0.0000 |
| p_inst | -0.380 | 0.5234 | 0.6740 |
| cf_deceleration_6h_gap | -0.312 | 0.0848 | 0.3609 |
| cf_gc_dlog_volume_1_gap | +0.279 | 0.0391 | 0.0487 |

### Mechanism flags

- opt_against_and_rising: rescued **46.2%**, broken **30.8%**, diff **+15.4 pp**
- cf_opt_joint: rescued **15.4%**, broken **15.4%**, diff **+0.0 pp**
- path_fracture_joint: rescued **23.1%**, broken **69.2%**, diff **-46.2 pp**

## Threshold 0.80

- candidates: **22**
- rescued / broken: **11 / 11**

### Largest standardized separations (rescued - broken)

| Feature | SMD | Rescue median | Broken median |
|---|---:|---:|---:|
| dp_rte | -1.182 | 0.0039 | 0.1930 |
| tension_velocity | -0.764 | 0.0317 | 1.1679 |
| p_rte | +0.619 | 0.8706 | 0.8601 |
| rte_tension | +0.612 | 2.9126 | 2.8563 |
| opposite_extreme_recency | -0.609 | 0.0667 | 0.1111 |
| opposite_semivar_share | -0.601 | 0.3811 | 0.4188 |
| cf_signed_d_opt_pressure_gap | -0.499 | -0.0955 | -0.0700 |
| cf_gc_dlog_volume_1_gap | +0.497 | 0.0503 | -0.3026 |
| signed_d_opt_pressure | -0.496 | -0.0332 | -0.0314 |
| path_consistency | +0.444 | 0.0833 | 0.0000 |

### Mechanism flags

- opt_against_and_rising: rescued **45.5%**, broken **27.3%**, diff **+18.2 pp**
- cf_opt_joint: rescued **9.1%**, broken **18.2%**, diff **-9.1 pp**
- path_fracture_joint: rescued **27.3%**, broken **72.7%**, diff **-45.5 pp**

## Instant probability control

| Th | Cand | Rescue | Broken | Net | Precision | Rate |
|---:|---:|---:|---:|---:|---:|---:|
| 0.55 | 47 | 15 | 32 | -17 | 31.91% | 22.49% |
| 0.60 | 35 | 13 | 22 | -9 | 37.14% | 16.75% |
| 0.65 | 21 | 9 | 12 | -3 | 42.86% | 10.05% |
| 0.70 | 8 | 3 | 5 | -2 | 37.50% | 3.83% |
| 0.75 | 4 | 1 | 3 | -2 | 25.00% | 1.91% |
| 0.80 | 4 | 1 | 3 | -2 | 25.00% | 1.91% |
